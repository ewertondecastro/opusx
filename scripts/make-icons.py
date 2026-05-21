#!/usr/bin/env python3
"""Gera o ícone do Opus X — ASCEND sunrise — em todos os tamanhos."""
from PIL import Image, ImageDraw, ImageFilter
import os, base64, io

OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')
os.makedirs(OUT, exist_ok=True)

BG_TOP = (255, 150, 54)   # laranja quente
BG_BOT = (90, 30, 70)     # roxo profundo
SIZES = [180, 192, 256, 384, 512, 1024]


def draw_icon(size):
    S = size * 3  # supersample
    # fundo: gradiente vertical
    img = Image.new('RGB', (S, S), BG_BOT)
    px = img.load()
    for y in range(S):
        t = (y / S) ** 1.05
        row = tuple(int(BG_TOP[i]*(1-t) + BG_BOT[i]*t) for i in range(3))
        for x in range(S):
            px[x, y] = row

    # brilho suave no topo
    glow = Image.new('L', (S, S), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-S*0.3, -S*0.55, S*1.3, S*0.55], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(S//7))
    white = Image.new('RGB', (S, S), (255, 255, 255))
    img = Image.composite(white, img, glow.point(lambda v: int(v*0.20)))

    d = ImageDraw.Draw(img, 'RGBA')
    cx = S // 2
    th = int(S * 0.090)
    # sombra suave sob os chevrons (profundidade)
    shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    # 3 chevrons subindo — cores OPACAS (sem sobreposição translúcida = sem artefato)
    # desenha de baixo p/ cima; o de cima cobre o de baixo de forma limpa
    specs = [
        (0.660, 0.340, (223, 216, 212)),
        (0.520, 0.285, (242, 238, 236)),
        (0.380, 0.230, (255, 255, 255)),
    ]
    off = int(S * 0.012)
    for cy_f, halfw_f, _ in specs:
        cy = int(S * cy_f); hw = int(S * halfw_f); drop = int(hw * 0.64)
        vtx_y = cy - int(drop * 0.12)
        sd.line([(cx-hw+off, cy+drop+off), (cx+off, vtx_y+off), (cx+hw+off, cy+drop+off)],
                fill=(0, 0, 0, 90), width=th, joint='curve')
    shadow = shadow.filter(ImageFilter.GaussianBlur(S//120))
    img.paste(shadow, (0, 0), shadow)

    d = ImageDraw.Draw(img, 'RGBA')
    for cy_f, halfw_f, col in specs:
        cy = int(S * cy_f); hw = int(S * halfw_f); drop = int(hw * 0.64)
        vtx_y = cy - int(drop * 0.12)
        d.line([(cx-hw, cy+drop), (cx, vtx_y), (cx+hw, cy+drop)],
               fill=col, width=th, joint='curve')
        for ex, ey in [(cx-hw, cy+drop), (cx+hw, cy+drop)]:
            d.ellipse([ex-th//2, ey-th//2, ex+th//2, ey+th//2], fill=col)

    return img.resize((size, size), Image.LANCZOS)


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


for s in SIZES:
    im = draw_icon(s)
    p = os.path.join(OUT, f'icon-{s}.png')
    im.save(p, 'PNG', optimize=True)
    print('wrote', p)

b180 = base64.b64encode(png_bytes(draw_icon(180))).decode()
with open(os.path.join(OUT, 'apple-touch-180.b64'), 'w') as f:
    f.write(b180)
print('wrote apple-touch base64,', len(b180), 'chars')
