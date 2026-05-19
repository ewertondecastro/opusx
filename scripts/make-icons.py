#!/usr/bin/env python3
"""Gera o ícone do Opus X em vários tamanhos."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os, base64, io, math

OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')
os.makedirs(OUT, exist_ok=True)

BG_TOP = (16, 18, 22)
BG_BOT = (4, 5, 7)
GOLD = (201, 169, 110)
GOLD_HI = (232, 207, 153)
GOLD_LO = (134, 110, 60)

SIZES = [180, 192, 256, 384, 512, 1024]


def make_bg(S):
    """Vertical gradient background — slightly lighter at top."""
    img = Image.new('RGB', (S, S), BG_BOT)
    px = img.load()
    for y in range(S):
        t = y / S
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        for x in range(S):
            px[x, y] = (r, g, b)
    return img


def draw_x_bar(draw, p1, p2, width, color):
    """Draw a tapered diagonal bar between two points with sharp pointed ends."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    hw = width / 2
    # slight inset so ends form a chevron point
    pts = [
        (p1[0] + nx * hw, p1[1] + ny * hw),
        (p2[0] + nx * hw, p2[1] + ny * hw),
        (p2[0] - nx * hw, p2[1] - ny * hw),
        (p1[0] - nx * hw, p1[1] - ny * hw),
    ]
    draw.polygon(pts, fill=color)


def draw_icon(size):
    S = size * 3  # supersample for crisp anti-alias
    img = make_bg(S)

    # subtle vignette
    vig = Image.new('L', (S, S), 0)
    vd = ImageDraw.Draw(vig)
    margin = int(S * 0.02)
    vd.ellipse([margin, margin, S - margin, S - margin], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(radius=S // 8))
    dark = Image.new('RGB', (S, S), (0, 0, 0))
    img = Image.composite(img, dark, vig)

    d = ImageDraw.Draw(img, 'RGBA')

    inset = int(S * 0.24)
    bar_w = int(S * 0.10)

    # subtle drop shadow behind X
    shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    off = int(S * 0.012)
    for w_mul, alpha in [(1.0, 80)]:
        bw = int(bar_w * w_mul)
        draw_x_bar(sd, (inset + off, inset + off), (S - inset + off, S - inset + off), bw, (0, 0, 0, alpha))
        draw_x_bar(sd, (S - inset + off, inset + off), (inset + off, S - inset + off), bw, (0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=S // 80))
    img.paste(shadow, (0, 0), shadow)

    d = ImageDraw.Draw(img, 'RGBA')

    # main X — solid gold with gradient feel via stacked bars
    draw_x_bar(d, (inset, inset), (S - inset, S - inset), bar_w, GOLD)
    draw_x_bar(d, (S - inset, inset), (inset, S - inset), bar_w, GOLD)

    # thin highlight along inner edge (creates dimension)
    hl_w = max(2, int(S * 0.012))
    off2 = int(S * 0.022)
    draw_x_bar(d,
               (inset + off2, inset - off2),
               (S - inset + off2, S - inset - off2),
               hl_w, GOLD_HI)
    draw_x_bar(d,
               (S - inset - off2, inset - off2),
               (inset - off2, S - inset - off2),
               hl_w, GOLD_HI)

    # downscale with high-quality filter
    out = img.resize((size, size), Image.LANCZOS)
    return out


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


for s in SIZES:
    im = draw_icon(s)
    p = os.path.join(OUT, f'icon-{s}.png')
    im.save(p, 'PNG', optimize=True)
    print('wrote', p)

# emit apple-touch base64 to embed inline (avoids extra HTTP request + caches with HTML)
b180 = base64.b64encode(png_bytes(draw_icon(180))).decode()
with open(os.path.join(OUT, 'apple-touch-180.b64'), 'w') as f:
    f.write(b180)
print('wrote apple-touch base64,', len(b180), 'chars')
