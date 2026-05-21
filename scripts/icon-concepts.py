#!/usr/bin/env python3
"""Gera 3 conceitos de ícone do Opus X em 512px para escolha."""
from PIL import Image, ImageDraw, ImageFilter
import os, math

OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')
os.makedirs(OUT, exist_ok=True)

GOLD     = (201, 169, 110)
GOLD_HI  = (236, 212, 158)
GOLD_LO  = (150, 122, 70)
BG_TOP   = (28, 30, 35)
BG_BOT   = (6, 7, 9)


def bg(S):
    img = Image.new('RGB', (S, S), BG_BOT)
    px = img.load()
    for y in range(S):
        t = y / S
        r = int(BG_TOP[0]*(1-t) + BG_BOT[0]*t)
        g = int(BG_TOP[1]*(1-t) + BG_BOT[1]*t)
        b = int(BG_TOP[2]*(1-t) + BG_BOT[2]*t)
        for x in range(S):
            px[x, y] = (r, g, b)
    # vignette
    vig = Image.new('L', (S, S), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-S*0.1, -S*0.1, S*1.1, S*1.1], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(S//6))
    dark = Image.new('RGB', (S, S), (0, 0, 0))
    return Image.composite(img, dark, vig)


def lerp(a, b, t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))


def grad_fill(draw, poly, c_top, c_bot, ys):
    """Aproxima gradiente vertical pintando o polígono em faixas (simplificado: cor sólida média)."""
    draw.polygon(poly, fill=lerp(c_top, c_bot, 0.5))


def concept_ascend(S):
    """3 chevrons subindo — progresso / superar nível."""
    img = bg(S)
    d = ImageDraw.Draw(img, 'RGBA')
    cx = S // 2
    th = int(S * 0.085)          # espessura do traço
    # 3 chevrons: de baixo (grande/escuro) pra cima (pequeno/claro)
    specs = [
        (0.70, 0.40, GOLD_LO),
        (0.55, 0.33, GOLD),
        (0.40, 0.26, GOLD_HI),
    ]
    for cy_f, halfw_f, color in specs:
        cy = int(S * cy_f)
        hw = int(S * halfw_f)
        drop = int(hw * 0.62)
        # chevron "^": dois braços
        pts_outer = [(cx - hw, cy + drop), (cx, cy - drop*0 + 0), (cx + hw, cy + drop)]
        # desenha como linha grossa com pontas
        d.line([(cx - hw, cy + drop), (cx, cy - int(drop*0.15))], fill=color, width=th, joint='curve')
        d.line([(cx, cy - int(drop*0.15)), (cx + hw, cy + drop)], fill=color, width=th, joint='curve')
        # ponta arredondada no vértice
        d.ellipse([cx-th//2, cy-int(drop*0.15)-th//2, cx+th//2, cy-int(drop*0.15)+th//2], fill=color)
    return img


def concept_emblem(S):
    """Anel (O) com X inscrito — monograma OX, emblema premium."""
    img = bg(S)
    d = ImageDraw.Draw(img, 'RGBA')
    cx = cy = S // 2
    R = int(S * 0.34)
    ring_w = int(S * 0.055)
    # anel
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=GOLD, width=ring_w)
    # X inscrito
    x_th = int(S * 0.072)
    inset = int(R * 0.52)
    for p1, p2, col in [
        ((cx-inset, cy-inset), (cx+inset, cy+inset), GOLD_HI),
        ((cx+inset, cy-inset), (cx-inset, cy+inset), GOLD),
    ]:
        d.line([p1, p2], fill=col, width=x_th)
        for p in (p1, p2):
            d.ellipse([p[0]-x_th//2, p[1]-x_th//2, p[0]+x_th//2, p[1]+x_th//2], fill=col)
    return img


def concept_bars(S):
    """Barras ascendentes com pico — força / progresso medido."""
    img = bg(S)
    d = ImageDraw.Draw(img, 'RGBA')
    n = 4
    gap = int(S * 0.045)
    total_w = int(S * 0.52)
    bar_w = (total_w - gap*(n-1)) // n
    x0 = (S - total_w) // 2
    base_y = int(S * 0.74)
    heights = [0.16, 0.26, 0.37, 0.50]
    cols = [GOLD_LO, GOLD_LO, GOLD, GOLD_HI]
    for i in range(n):
        x = x0 + i*(bar_w+gap)
        h = int(S * heights[i])
        d.rounded_rectangle([x, base_y-h, x+bar_w, base_y], radius=bar_w//3, fill=cols[i])
    # seta/pico no topo da última barra
    lx = x0 + (n-1)*(bar_w+gap) + bar_w//2
    ly = base_y - int(S*heights[-1])
    aw = int(bar_w*0.95)
    d.polygon([(lx, ly-int(S*0.13)), (lx-aw, ly+int(S*0.02)), (lx+aw, ly+int(S*0.02))], fill=GOLD_HI)
    return img


for name, fn in [('ascend', concept_ascend), ('emblem', concept_emblem), ('bars', concept_bars)]:
    SS = 512 * 3
    big = fn(SS).filter(ImageFilter.GaussianBlur(0.4))
    out = big.resize((512, 512), Image.LANCZOS)
    p = os.path.join(OUT, f'concept-{name}.png')
    out.save(p, 'PNG', optimize=True)
    print('wrote', p)
