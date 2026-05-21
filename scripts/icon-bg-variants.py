#!/usr/bin/env python3
"""ASCEND em 4 fundos motivacionais diferentes — 512px para escolha."""
from PIL import Image, ImageDraw, ImageFilter
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')

# (top, bottom) gradientes de fundo
BACKGROUNDS = {
    'sunrise':  ((255, 150, 54),  (90, 30, 70)),    # laranja quente -> roxo profundo
    'energy':   ((242, 78, 54),   (120, 18, 28)),   # vermelho-coral -> vinho
    'goldluxe': ((201, 169, 110), (40, 30, 18)),    # dourado -> marrom escuro
    'amber':    ((255, 176, 32),  (140, 60, 10)),   # âmbar vibrante -> bronze
}
CHEVRON = (255, 255, 255)        # branco — salta em qualquer fundo colorido
CHEV_SOFT = (255, 255, 255, 235)


def bg_gradient(S, top, bot):
    img = Image.new('RGB', (S, S), bot)
    px = img.load()
    for y in range(S):
        t = (y / S) ** 1.05
        px_row = tuple(int(top[i]*(1-t) + bot[i]*t) for i in range(3))
        for x in range(S):
            px[x, y] = px_row
    return img


def draw_ascend(S, top, bot):
    img = bg_gradient(S, top, bot)
    # leve brilho no topo (luz)
    glow = Image.new('L', (S, S), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-S*0.3, -S*0.55, S*1.3, S*0.55], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(S//7))
    white = Image.new('RGB', (S, S), (255, 255, 255))
    img = Image.composite(white, img, glow.point(lambda v: int(v*0.22)))

    d = ImageDraw.Draw(img, 'RGBA')
    cx = S // 2
    th = int(S * 0.092)
    specs = [(0.70, 0.40, 200), (0.55, 0.33, 230), (0.40, 0.26, 255)]
    for cy_f, halfw_f, alpha in specs:
        cy = int(S * cy_f)
        hw = int(S * halfw_f)
        drop = int(hw * 0.62)
        vtx_y = cy - int(drop*0.15)
        col = (255, 255, 255, alpha)
        d.line([(cx-hw, cy+drop), (cx, vtx_y)], fill=col, width=th, joint='curve')
        d.line([(cx, vtx_y), (cx+hw, cy+drop)], fill=col, width=th, joint='curve')
        d.ellipse([cx-th//2, vtx_y-th//2, cx+th//2, vtx_y+th//2], fill=col)
    return img


for name, (top, bot) in BACKGROUNDS.items():
    SS = 512 * 3
    out = draw_ascend(SS, top, bot).resize((512, 512), Image.LANCZOS)
    p = os.path.join(OUT, f'ascend-{name}.png')
    out.save(p, 'PNG', optimize=True)
    print('wrote', p)
