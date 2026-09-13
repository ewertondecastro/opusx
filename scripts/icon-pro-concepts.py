#!/usr/bin/env python3
"""4 conceitos profissionais — IA + Gym + Fasting + Diet"""
from PIL import Image, ImageDraw, ImageFilter
import math, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')
os.makedirs(OUT, exist_ok=True)

S = 512 * 4   # 2048px supersampling

GOLD     = (212, 178, 120)
GOLD_HI  = (248, 224, 168)
GOLD_DIM = (140, 112, 68)
WHITE    = (255, 255, 255)
BG       = (8, 10, 12)
ELECTRIC = (100, 200, 255)   # azul IA

def new_canvas(bg=BG):
    img = Image.new('RGB', (S, S), bg)
    # subtle vignette
    vig = Image.new('L', (S, S), 0)
    vd  = ImageDraw.Draw(vig)
    m   = int(S * 0.05)
    vd.ellipse([m, m, S-m, S-m], fill=220)
    vig = vig.filter(ImageFilter.GaussianBlur(S // 5))
    dark = Image.new('RGB', (S, S), (4, 5, 6))
    return Image.composite(img, dark, vig)

def add_glow(img, cx, cy, r, color, alpha=80):
    overlay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(4, 0, -1):
        a = int(alpha * (i / 4) ** 2)
        ri = int(r * (1 + 0.5 * (4 - i) / 3))
        d.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], fill=color+(a,))
    base = img.convert('RGBA')
    return Image.alpha_composite(base, overlay).convert('RGB')

def node(d, cx, cy, r, col=GOLD, bright=WHITE):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    d.ellipse([cx-r//3, cy-r//3, cx+r//3, cy+r//3], fill=bright)

def thick_line(d, p1, p2, w, col):
    """Linha com caps arredondados."""
    d.line([p1, p2], fill=col, width=w)
    r = w // 2
    for p in (p1, p2):
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=col)


# ══════════════════════════════════════════════════════════════
# CONCEITO A — CIRCUIT BRAIN
# Silhueta de cérebro feita de nós neurais + traços de circuito
# ══════════════════════════════════════════════════════════════
def concept_circuit_brain(S):
    img = new_canvas()

    # glow central difuso
    img = add_glow(img, S//2, S//2, int(S*0.30), GOLD_DIM, 50)
    d = ImageDraw.Draw(img, 'RGBA')

    cx = S // 2
    cy = int(S * 0.48)
    R  = int(S * 0.28)
    th = int(S * 0.016)
    nr = int(S * 0.024)

    # Define os nós que formam o contorno de um cérebro
    # (semi-elipse superior com "sulcos" nas laterais)
    brain_pts = []
    # Metade superior — arco oval
    for a in range(-165, 5, 15):
        rad = math.radians(a)
        rx = R * (1 + 0.15 * abs(math.cos(rad * 2)))
        ry = R * 0.82
        brain_pts.append((cx + int(rx * math.cos(rad)),
                           cy + int(ry * math.sin(rad) * 0.85)))

    # Parte inferior: junção (base do cérebro)
    brain_pts += [
        (cx + int(R * 0.55), cy + int(R * 0.40)),
        (cx + int(R * 0.15), cy + int(R * 0.52)),
        (cx - int(R * 0.15), cy + int(R * 0.52)),
        (cx - int(R * 0.55), cy + int(R * 0.40)),
    ]

    # Nós internos (sinapses)
    inner = [
        (cx,              cy - int(R * 0.30)),
        (cx + int(R*0.40), cy - int(R * 0.10)),
        (cx - int(R*0.40), cy - int(R * 0.10)),
        (cx + int(R*0.22), cy + int(R * 0.18)),
        (cx - int(R*0.22), cy + int(R * 0.18)),
        (cx,              cy - int(R * 0.60)),
        (cx + int(R*0.55), cy - int(R * 0.48)),
        (cx - int(R*0.55), cy - int(R * 0.48)),
    ]

    all_pts = brain_pts + inner

    # Traços de conexão (circuito horizontal/vertical)
    wire_col = GOLD_DIM + (100,)
    for i, (ax, ay) in enumerate(all_pts):
        for j, (bx, by) in enumerate(all_pts):
            if j <= i: continue
            dist = math.hypot(bx - ax, by - ay)
            if dist < R * 0.60:
                # linha em L (estilo circuito)
                mid_x = ax if abs(bx - ax) < abs(by - ay) else bx
                mid_y = by if abs(bx - ax) < abs(by - ay) else ay
                d.line([(ax, ay), (mid_x, mid_y), (bx, by)], fill=wire_col, width=th)

    # Contorno do cérebro (traços entre nós adjacentes)
    for i in range(len(brain_pts)):
        a = brain_pts[i]
        b = brain_pts[(i+1) % len(brain_pts)]
        d.line([a, b], fill=GOLD+(200,), width=th+int(S*0.003))

    # Divisor central (sulco)
    d.line([(cx, cy - int(R*0.75)), (cx, cy + int(R*0.38))],
           fill=GOLD_DIM+(140,), width=th)

    # Nós
    for pt in brain_pts:
        node(d, pt[0], pt[1], nr, GOLD, GOLD_HI)
    for pt in inner:
        node(d, pt[0], pt[1], int(nr*0.75), GOLD_DIM, GOLD)

    # Pulso (linha de ECG) na base
    pulse_y = cy + int(R * 0.72)
    pw      = int(R * 0.65)
    pts = [
        (cx - pw,         pulse_y),
        (cx - int(pw*0.5), pulse_y),
        (cx - int(pw*0.3), pulse_y - int(R*0.22)),
        (cx - int(pw*0.1), pulse_y + int(R*0.28)),
        (cx + int(pw*0.1), pulse_y - int(R*0.40)),
        (cx + int(pw*0.3), pulse_y),
        (cx + pw,         pulse_y),
    ]
    d.line(pts, fill=GOLD_HI+(230,), width=int(th*1.2))

    return img.resize((512, 512), Image.LANCZOS)


# ══════════════════════════════════════════════════════════════
# CONCEITO B — ATLAS (silhueta atlética + rede neural)
# Figura humana em "X" formada por nós conectados
# ══════════════════════════════════════════════════════════════
def concept_atlas(S):
    img = new_canvas()
    img = add_glow(img, S//2, int(S*0.42), int(S*0.28), GOLD_DIM, 60)
    d   = ImageDraw.Draw(img, 'RGBA')

    cx   = S // 2
    top  = int(S * 0.10)
    bot  = int(S * 0.88)
    h    = bot - top
    th   = int(S * 0.018)
    nr   = int(S * 0.028)

    # Pontos chave da figura (pose "mãos acima da cabeça" = vitória)
    head  = (cx, top + int(h * 0.08))
    neck  = (cx, top + int(h * 0.16))
    lsho  = (cx - int(h*0.22), top + int(h * 0.22))
    rsho  = (cx + int(h*0.22), top + int(h * 0.22))
    lhand = (cx - int(h*0.36), top + int(h * 0.08))  # mãos levantadas
    rhand = (cx + int(h*0.36), top + int(h * 0.08))
    core  = (cx, top + int(h * 0.38))
    lhip  = (cx - int(h*0.14), top + int(h * 0.50))
    rhip  = (cx + int(h*0.14), top + int(h * 0.50))
    lknee = (cx - int(h*0.17), top + int(h * 0.68))
    rknee = (cx + int(h*0.17), top + int(h * 0.68))
    lfeet = (cx - int(h*0.19), top + int(h * 0.88))
    rfeet = (cx + int(h*0.19), top + int(h * 0.88))

    # Conexões do "esqueleto neural"
    connections = [
        (lhand, lsho), (rhand, rsho),
        (lsho, neck), (rsho, neck),
        (neck, head),
        (lsho, core), (rsho, core),
        (core, lhip), (core, rhip),
        (lhip, lknee), (rhip, rknee),
        (lknee, lfeet), (rknee, rfeet),
        # cross-connections (rede neural)
        (lsho, rsho), (lhip, rhip),
        (lsho, rhip), (rsho, lhip),
        (lknee, rknee),
    ]

    wire_col = GOLD_DIM + (90,)
    for a, b in connections:
        d.line([a, b], fill=GOLD+(200,), width=th)

    # Linhas de circuito extra (horizontais) nas articulações principais
    for pt in [neck, core]:
        ext = int(h * 0.12)
        d.line([(pt[0]-ext, pt[1]), (pt[0]+ext, pt[1])],
               fill=wire_col, width=th-2)
        for side in [-ext, ext]:
            br = int(S * 0.010)
            ex = pt[0] + side
            d.rectangle([ex-br, pt[1]-br, ex+br, pt[1]+br], fill=wire_col)

    # Nós (articulações)
    major = [head, lhand, rhand, lfeet, rfeet]
    minor = [neck, lsho, rsho, core, lhip, rhip, lknee, rknee]
    for pt in major:
        node(d, pt[0], pt[1], int(nr*1.3), GOLD_HI, WHITE)
    for pt in minor:
        node(d, pt[0], pt[1], nr, GOLD, GOLD_HI)

    # Auréola no nó da cabeça (glow)
    img = add_glow(img, head[0], head[1], int(nr*3), GOLD_HI, 70)
    d   = ImageDraw.Draw(img, 'RGBA')
    node(d, head[0], head[1], int(nr*1.5), GOLD_HI, WHITE)

    return img.resize((512, 512), Image.LANCZOS)


# ══════════════════════════════════════════════════════════════
# CONCEITO C — VOLT X (energia + IA)
# "X" premium com raio integrado, nós de circuito, fundo escuro
# ══════════════════════════════════════════════════════════════
def concept_volt_x(S):
    img = new_canvas()

    cx = cy = S // 2
    arm   = int(S * 0.305)
    thick = int(S * 0.100)
    nr    = int(S * 0.038)

    dx = dy = arm * 0.707

    # Sombra do X
    sd = Image.new('RGBA', (S, S), (0,0,0,0))
    sdraw = ImageDraw.Draw(sd)
    off = int(S*0.018)
    for pts in [
        [(cx-dx+off, cy-dy+off), (cx+dx+off, cy+dy+off)],
        [(cx+dx+off, cy-dy+off), (cx-dx+off, cy+dy+off)],
    ]:
        sdraw.line(pts, fill=(0,0,0,120), width=thick+int(S*0.012))
    sd = sd.filter(ImageFilter.GaussianBlur(S//50))
    img.paste(Image.new('RGB',(S,S),(0,0,0)), (0,0), sd.split()[3])

    # Glow dourado no centro
    img = add_glow(img, cx, cy, int(arm*0.55), GOLD, 90)
    d   = ImageDraw.Draw(img, 'RGBA')

    # Os dois braços do X
    for p1, p2 in [
        ((cx-dx, cy-dy), (cx+dx, cy+dy)),
        ((cx+dx, cy-dy), (cx-dx, cy+dy)),
    ]:
        thick_line(d, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), thick, GOLD)

    # Raio (bolt) no centro — pequeno, integrado ao X
    bh = int(thick * 1.9)
    bw = int(thick * 0.72)
    bolt = [
        (cx + bw,        cy - bh),
        (cx - bw//3,     cy - int(bh*0.05)),
        (cx + bw//2,     cy),
        (cx - bw,        cy + bh),
        (cx + bw//3,     cy + int(bh*0.05)),
        (cx - bw//2,     cy),
    ]
    # Sombra do bolt
    shadow_bolt = [(x+int(S*0.006), y+int(S*0.006)) for x,y in bolt]
    d.polygon(shadow_bolt, fill=(0,0,0,140))
    d.polygon(bolt, fill=WHITE+(240,))

    # Nós nas pontas do X + linhas de circuito
    tips = [
        (int(cx-dx), int(cy-dy)),
        (int(cx+dx), int(cy+dy)),
        (int(cx+dx), int(cy-dy)),
        (int(cx-dx), int(cy+dy)),
    ]
    wire = GOLD_DIM + (100,)
    for tx, ty in tips:
        # calcular direção "para fora"
        dirx = 1 if tx > cx else -1
        diry = 1 if ty > cy else -1
        ext  = int(S * 0.062)
        # horizontal + vertical wire
        d.line([(tx, ty), (tx + dirx*ext, ty)], fill=wire, width=int(S*0.009))
        d.line([(tx, ty), (tx, ty + diry*ext)], fill=wire, width=int(S*0.009))
        br = int(S * 0.013)
        for ex, ey in [(tx + dirx*ext, ty), (tx, ty + diry*ext)]:
            d.rectangle([ex-br, ey-br, ex+br, ey+br], fill=wire)
        node(d, tx, ty, nr, GOLD_HI, WHITE)

    return img.resize((512, 512), Image.LANCZOS)


# ══════════════════════════════════════════════════════════════
# CONCEITO D — MONOLITH BADGE
# Anel + "OX" em monograma premium, tipografia geométrica
# ══════════════════════════════════════════════════════════════
def concept_monolith(S):
    img = new_canvas()
    img = add_glow(img, S//2, S//2, int(S*0.32), GOLD_DIM, 70)
    d   = ImageDraw.Draw(img, 'RGBA')

    cx = cy = S // 2
    R_out = int(S * 0.40)
    R_in  = int(S * 0.34)
    ring_w = R_out - R_in

    # Anel externo
    d.ellipse([cx-R_out, cy-R_out, cx+R_out, cy+R_out], fill=GOLD)
    d.ellipse([cx-R_in,  cy-R_in,  cx+R_in,  cy+R_in],  fill=BG)

    # Marcadores no anel (como relógio de luxo) — 12 traços
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        r1 = R_in + int(ring_w * 0.15)
        r2 = R_in + int(ring_w * 0.75) if i % 3 == 0 else R_in + int(ring_w * 0.5)
        w  = int(ring_w * 0.18) if i % 3 == 0 else int(ring_w * 0.10)
        x1 = cx + int(r1 * math.cos(angle))
        y1 = cy + int(r1 * math.sin(angle))
        x2 = cx + int(r2 * math.cos(angle))
        y2 = cy + int(r2 * math.sin(angle))
        d.line([(x1, y1), (x2, y2)], fill=BG, width=w)

    # "X" central — versão clean, thick
    arm   = int(S * 0.195)
    thick = int(S * 0.075)
    dx = dy = arm * 0.707
    for p1, p2 in [
        ((cx-dx, cy-dy), (cx+dx, cy+dy)),
        ((cx+dx, cy-dy), (cx-dx, cy+dy)),
    ]:
        thick_line(d, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), thick, GOLD)
    # Pequeno círculo central
    cr = int(S * 0.040)
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=BG)
    d.ellipse([cx-cr//2, cy-cr//2, cx+cr//2, cy+cr//2], fill=GOLD)

    # OPUS X em lowercase no topo do anel (arco)
    # Simula com pequenos retângulos (sem fonte)
    label_y = cy - int(R_in * 0.72)
    def draw_letter_O(d, lx, ly, w, h, thick, col):
        d.ellipse([lx, ly, lx+w, ly+h], fill=col)
        d.ellipse([lx+thick, ly+thick, lx+w-thick, ly+h-thick], fill=BG)
    def draw_letter_P(d, lx, ly, w, h, thick, col):
        d.rectangle([lx, ly, lx+thick, ly+h], fill=col)
        d.ellipse([lx, ly, lx+w, ly+int(h*0.55)], fill=col)
        d.ellipse([lx+thick, ly+thick, lx+w-thick, ly+int(h*0.55)-thick], fill=BG)
    def draw_letter_U(d, lx, ly, w, h, thick, col):
        d.rectangle([lx, ly, lx+thick, ly+h-w//2], fill=col)
        d.rectangle([lx+w-thick, ly, lx+w, ly+h-w//2], fill=col)
        d.ellipse([lx, ly+h-w, lx+w, ly+h], fill=col)
        d.ellipse([lx+thick, ly+h-w+thick, lx+w-thick, ly+h-thick], fill=BG)
    def draw_letter_S(d, lx, ly, w, h, thick, col):
        d.ellipse([lx, ly, lx+w, ly+int(h*0.52)], fill=col)
        d.ellipse([lx+thick, ly+thick, lx+w-thick, ly+int(h*0.52)-thick], fill=BG)
        d.rectangle([lx, ly+int(h*0.26), lx+w//2, ly+int(h*0.52)], fill=col)
        d.ellipse([lx, ly+int(h*0.48), lx+w, ly+h], fill=col)
        d.ellipse([lx+thick, ly+int(h*0.48)+thick, lx+w-thick, ly+h-thick], fill=BG)
        d.rectangle([lx+w//2, ly+int(h*0.48), lx+w, ly+int(h*0.74)], fill=col)

    # "OPUS X" texto usando Bebas-like geometry — simplificado
    lw, lh, lt = int(S*0.054), int(S*0.072), int(S*0.013)
    gap = int(S * 0.010)
    total = lw*5 + gap*5
    sx = cx - total//2

    # Simplified: draw "OPUS" as bold rects (pixelated but clean) + X
    letters_x = [sx + i*(lw+gap) for i in range(5)]
    # O
    d.ellipse([letters_x[0], label_y, letters_x[0]+lw, label_y+lh], fill=GOLD)
    d.ellipse([letters_x[0]+lt, label_y+lt, letters_x[0]+lw-lt, label_y+lh-lt], fill=BG)
    # P
    d.rectangle([letters_x[1], label_y, letters_x[1]+lt, label_y+lh], fill=GOLD)
    d.ellipse([letters_x[1], label_y, letters_x[1]+lw, label_y+lh//2+lt], fill=GOLD)
    d.ellipse([letters_x[1]+lt, label_y+lt, letters_x[1]+lw-lt, label_y+lh//2], fill=BG)
    # U
    d.rectangle([letters_x[2], label_y, letters_x[2]+lt, label_y+lh-lw//2], fill=GOLD)
    d.rectangle([letters_x[2]+lw-lt, label_y, letters_x[2]+lw, label_y+lh-lw//2], fill=GOLD)
    d.ellipse([letters_x[2], label_y+lh-lw, letters_x[2]+lw, label_y+lh], fill=GOLD)
    d.ellipse([letters_x[2]+lt, label_y+lh-lw+lt, letters_x[2]+lw-lt, label_y+lh-lt], fill=BG)
    # S
    d.ellipse([letters_x[3], label_y, letters_x[3]+lw, label_y+lh//2+lt], fill=GOLD)
    d.ellipse([letters_x[3]+lt, label_y+lt, letters_x[3]+lw-lt, label_y+lh//2-lt], fill=BG)
    d.rectangle([letters_x[3], label_y+lh//2-lt, letters_x[3]+lw//2+lt, label_y+lh//2+lt+2], fill=GOLD)
    d.ellipse([letters_x[3], label_y+lh//2-lt, letters_x[3]+lw, label_y+lh], fill=GOLD)
    d.ellipse([letters_x[3]+lt, label_y+lh//2+lt, letters_x[3]+lw-lt, label_y+lh-lt], fill=BG)
    d.rectangle([letters_x[3]+lw//2, label_y+lh//2-lt, letters_x[3]+lw, label_y+lh//2+lt*2], fill=BG)
    # X (bold)
    xth = int(lt * 1.1)
    xdx = lw * 0.5 * 0.707
    xdy = lh * 0.5 * 0.707
    xcx = letters_x[4] + lw//2
    xcy = label_y + lh//2
    for p1, p2 in [
        ((xcx-xdx, xcy-xdy), (xcx+xdx, xcy+xdy)),
        ((xcx+xdx, xcy-xdy), (xcx-xdx, xcy+xdy)),
    ]:
        thick_line(d, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), xth, GOLD)

    return img.resize((512, 512), Image.LANCZOS)


# ── RENDER ALL ──
for name, fn in [
    ('A-circuit-brain', concept_circuit_brain),
    ('B-atlas',         concept_atlas),
    ('C-volt-x',        concept_volt_x),
    ('D-monolith',      concept_monolith),
]:
    out = fn(S)
    p   = os.path.join(OUT, f'pro-{name}.png')
    out.save(p, 'PNG', optimize=True)
    print('wrote', p)
