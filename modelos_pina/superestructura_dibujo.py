"""
Ilustración de la superestructura de la biorrefinería de piña, estilo dibujo científico a mano alzada
(trazos dobles con desviación aleatoria, sombreado de lápiz de color y filtro de grano).

Lee el diseño óptimo de results/dimensionamiento.json (E1|Óptimo económico y E5 para la bromelaína) y marca en color
la alternativa elegida en cada disyunción; las descartadas quedan en gris punteado.
Salidas: figs/fig33_superestructura.svg (autocontenido, fuentes OFL incrustadas) y figs/fig33_superestructura.png.
"""
import base64, json, math, os, random
import dimensionamiento as dm_mod

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
rng = random.Random(20261105)

W, H = 2580, 2190
PX = 2120   # columna de productos
INK = "#3d3a35"
GREY = "#b9b3aa"
PAL = dict(   # (relleno pastel, trazo)
    pulpa=("#e8c3b2", "#b06f58"), cascara=("#ecdcae", "#a8843d"), corazon=("#c9d8b8", "#6e8c5c"),
    vinagre=("#dcc0cf", "#94657f"), agua=("#c3d3df", "#5e7d96"), corona=("#d9d2c8", "#8a8176"),
    neutro=("#e9e4dc", "#7a746b"))

out = []


def add(s):
    out.append(s)


# ----------------------------------------------------------------------------- primitivas a mano alzada
def j(a):
    return rng.uniform(-a, a)


def rline(x1, y1, x2, y2, color=INK, w=2.2, passes=2, bow=0.015, dash=None, op=1.0, over=3.0):
    L = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    for p in range(passes):
        a = (x1 - ux * j(over) + j(1.2), y1 - uy * j(over) + j(1.2))
        b = (x2 + ux * j(over) + j(1.2), y2 + uy * j(over) + j(1.2))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        off = bow * L * j(1.0)
        cx, cy = mx - uy * off, my + ux * off
        da = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{cx:.1f},{cy:.1f} {b[0]:.1f},{b[1]:.1f}" fill="none" stroke="{color}" '
            f'stroke-width="{w * (1 if p == 0 else 0.7):.2f}" stroke-linecap="round" opacity="{op if p == 0 else op * 0.75:.2f}"{da}/>')


def rrect(x, y, w, h, color=INK, sw=2.2, dash=None, op=1.0, passes=2):
    rline(x, y, x + w, y, color, sw, passes, dash=dash, op=op)
    rline(x + w, y, x + w, y + h, color, sw, passes, dash=dash, op=op)
    rline(x + w, y + h, x, y + h, color, sw, passes, dash=dash, op=op)
    rline(x, y + h, x, y, color, sw, passes, dash=dash, op=op)


_cid = [0]


def hachure(x, y, w, h, color, gap=8.0, angle=-38, sw=1.5, op=0.55, fill=None, fill_op=0.45, cross=False, shape=None):
    """Sombreado de lápiz: relleno suave + trazos paralelos recortados a la figura."""
    _cid[0] += 1
    cid = f"c{_cid[0]}"
    clip = shape or f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>'
    add(f'<clipPath id="{cid}">{clip}</clipPath>')
    add(f'<g clip-path="url(#{cid})" filter="url(#grain)">')
    if fill:
        add(f'<rect x="{x - 4}" y="{y - 4}" width="{w + 8}" height="{h + 8}" fill="{fill}" opacity="{fill_op}"/>')
    angles = [angle] + ([angle + 90] if cross else [])
    for ang in angles:
        t = math.radians(ang)
        dx, dy = math.cos(t), math.sin(t)
        nx, ny = -dy, dx
        cx, cy = x + w / 2, y + h / 2
        R = math.hypot(w, h) / 2 + 10
        k = -R
        while k <= R:
            px, py = cx + nx * k, cy + ny * k
            x1, y1 = px - dx * R, py - dy * R
            x2, y2 = px + dx * R, py + dy * R
            add(f'<path d="M{x1 + j(1.5):.1f},{y1 + j(1.5):.1f} L{x2 + j(1.5):.1f},{y2 + j(1.5):.1f}" stroke="{color}" '
                f'stroke-width="{sw * rng.uniform(0.7, 1.15):.2f}" opacity="{op * rng.uniform(0.6, 1.0):.2f}" stroke-linecap="round"/>')
            k += gap * rng.uniform(0.75, 1.25)
    add('</g>')


def rellipse(cx, cy, rx, ry, color=INK, sw=2.2, passes=2, n=28):
    for p in range(passes):
        pts = []
        a0 = rng.uniform(0, 2 * math.pi)
        for i in range(n + 3):
            a = a0 + 2 * math.pi * i / n
            pts.append((cx + (rx + j(2.0)) * math.cos(a), cy + (ry + j(2.0)) * math.sin(a)))
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(f"L{px:.1f},{py:.1f}" for px, py in pts[1:])
        add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw * (1 if p == 0 else 0.7):.2f}" stroke-linejoin="round" '
            f'opacity="{1 if p == 0 else 0.75}"/>')


def arrow(x1, y1, x2, y2, color=INK, sw=2.4, curve=0.12, dash=None, head=15, op=1.0, label=None, lab_dy=-10, lab_size=22, lab_color=None):
    L = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    cx, cy = (x1 + x2) / 2 - uy * curve * L, (y1 + y2) / 2 + ux * curve * L
    da = f' stroke-dasharray="{dash}"' if dash else ""
    for p in range(2):
        add(f'<path d="M{x1 + j(1):.1f},{y1 + j(1):.1f} Q{cx + j(3):.1f},{cy + j(3):.1f} {x2 + j(1):.1f},{y2 + j(1):.1f}" fill="none" '
            f'stroke="{color}" stroke-width="{sw * (1 if p == 0 else 0.6):.2f}" stroke-linecap="round" opacity="{op if p == 0 else op * 0.7:.2f}"{da}/>')
    tx, ty = x2 - cx, y2 - cy
    tl = math.hypot(tx, ty) or 1
    tx, ty = tx / tl, ty / tl
    for s in (1, -1):
        a = math.radians(26 * s)
        hx = tx * math.cos(a) - ty * math.sin(a)
        hy = tx * math.sin(a) + ty * math.cos(a)
        rline(x2, y2, x2 - hx * head, y2 - hy * head, color, sw, 1, bow=0.05, op=op, over=1)
    if label:
        text(cx, cy + lab_dy, label, lab_size, lab_color or color, anchor="middle")


def text(x, y, s, size=22, color=INK, anchor="start", font="Kalam", weight=400, italic=False, op=1.0):
    st = ' font-style="italic"' if italic else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{color}" '
        f'text-anchor="{anchor}" opacity="{op}"{st}>{s}</text>')


def check(x, y, color):
    rline(x, y, x + 7, y + 8, color, 2.6, 1, over=0.5)
    rline(x + 7, y + 8, x + 20, y - 9, color, 2.6, 1, over=0.5)


def disj(x, y, color=INK):
    rellipse(x, y, 17, 17, color, 2.0)
    text(x, y + 9, "∨", 27, color, anchor="middle", font="Kalam", weight=700)


# ----------------------------------------------------------------------------- tarjetas de etapa con alternativas
def card(x, y, w, title, chips, key, chosen=(), note=None, disjunction=True, faded=False, optional=False):
    """chips: lista de textos; chosen: índices elegidos. Devuelve (x, y, w, h) y centros de cada chip."""
    fill, stroke = PAL[key]
    hh, ch, pad = 50, 42, 12
    h = hh + len(chips) * (ch + 8) + pad + (34 if note else 0)
    col = GREY if faded else stroke
    rrect(x, y, w, h, col, 2.3, dash=("9 7" if optional or faded else None))
    hachure(x + 3, y + 3, w - 6, hh - 6, col if not faded else GREY, gap=9, sw=1.3, op=0.35,
            fill=(fill if not faded else "#efece7"), fill_op=0.55)
    text(x + (44 if disjunction else 14), y + 35, title, 30, INK if not faded else "#8f8a82", font="Caveat", weight=700)
    if disjunction:
        disj(x + 24, y + 26, INK if not faded else GREY)
    centers = []
    cy = y + hh + 6
    for i, s in enumerate(chips):
        cx0, cw = x + 12, w - 24
        if i in chosen and not faded:
            hachure(cx0, cy, cw, ch, stroke, gap=6.5, sw=1.6, op=0.75, fill=fill, fill_op=0.9, angle=-35)
            rrect(cx0, cy, cw, ch, stroke, 2.0)
            check(cx0 + cw - 30, cy + 22, stroke)
            col_t = INK
        else:
            rrect(cx0, cy, cw, ch, GREY, 1.6, dash="6 6", passes=1)
            col_t = "#8f8a82"
        size = min(21, (cw - (52 if i in chosen else 16)) / (0.47 * max(len(s), 1)))
        text(cx0 + 10, cy + ch / 2 + size * 0.36, s, size, col_t)
        centers.append((cx0 + cw / 2, cy + ch / 2))
        cy += ch + 8
    if note:
        text(x + 14, cy + 20, note, 18, "#6f6a62", italic=True)
    return (x, y, w, h), centers


def right(b):
    x, y, w, h = b
    return x + w, y + h / 2


def left(b):
    x, y, w, h = b
    return x, y + h / 2


# ----------------------------------------------------------------------------- dibujos de productos
def pineapple(cx, cy, s=1.0):
    fill, stroke = PAL["cascara"]
    rx, ry = 62 * s, 86 * s
    shape = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>'
    hachure(cx - rx, cy - ry, 2 * rx, 2 * ry, stroke, gap=16, sw=2.2, op=0.95, fill=fill, fill_op=0.95, angle=45, cross=True, shape=shape)
    rellipse(cx, cy, rx, ry, stroke, 2.6)
    gfill, gstroke = PAL["corazon"]
    for k in range(-3, 4):
        a = math.radians(-90 + k * 17)
        Lf = (95 - abs(k) * 12) * s
        bx, by = cx + k * 7 * s, cy - ry + 6
        ex, ey = bx + math.cos(a) * Lf, by + math.sin(a) * Lf
        mx, my = (bx + ex) / 2 + j(8) + k * 4, (by + ey) / 2 + j(5)
        for p in range(2):
            add(f'<path d="M{bx - 6:.1f},{by:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f} Q{mx + 8:.1f},{my + 4:.1f} {bx + 6:.1f},{by:.1f}" '
                f'fill="{gfill if p == 0 else "none"}" fill-opacity="0.7" stroke="{gstroke}" stroke-width="{2.0 if p == 0 else 1.2}" stroke-linejoin="round"/>')


def bottle(cx, cy, key="pulpa"):
    fill, stroke = PAL[key]
    d = (f"M{cx - 12},{cy - 78} L{cx + 12},{cy - 78} L{cx + 12},{cy - 40} Q{cx + 34},{cy - 22} {cx + 34},{cy + 4} L{cx + 34},{cy + 70} "
         f"L{cx - 34},{cy + 70} L{cx - 34},{cy + 4} Q{cx - 34},{cy - 22} {cx - 12},{cy - 40} Z")
    hachure(cx - 36, cy - 80, 72, 152, stroke, gap=7, sw=1.5, op=0.85, fill=fill, fill_op=0.95, shape=f'<path d="{d}"/>')
    for p in range(2):
        add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2.4 if p == 0 else 1.3}" stroke-linejoin="round" '
            f'transform="translate({j(1.5):.1f},{j(1.5):.1f})"/>')
    rrect(cx - 22, cy + 8, 44, 36, INK, 1.4, passes=1)


def jar(cx, cy, key="vinagre"):
    fill, stroke = PAL[key]
    hachure(cx - 38, cy - 50, 76, 112, stroke, gap=7, sw=1.5, op=0.85, fill=fill, fill_op=0.95, angle=-45)
    rrect(cx - 38, cy - 50, 76, 112, stroke, 2.4)
    hachure(cx - 30, cy - 70, 60, 20, PAL["neutro"][1], gap=5, sw=1.2, op=0.6, fill=PAL["neutro"][0], fill_op=0.9)
    rrect(cx - 30, cy - 70, 60, 20, PAL["neutro"][1], 2.0)
    rrect(cx - 24, cy - 14, 48, 34, INK, 1.4, passes=1)


def sack(cx, cy, key="cascara"):
    fill, stroke = PAL[key]
    d = (f"M{cx - 30},{cy - 60} Q{cx},{cy - 72} {cx + 30},{cy - 60} Q{cx + 22},{cy - 44} {cx + 26},{cy - 38} "
         f"Q{cx + 52},{cy + 10} {cx + 46},{cy + 62} Q{cx},{cy + 74} {cx - 46},{cy + 62} Q{cx - 52},{cy + 10} {cx - 26},{cy - 38} "
         f"Q{cx - 22},{cy - 44} {cx - 30},{cy - 60} Z")
    hachure(cx - 54, cy - 74, 108, 150, stroke, gap=7, sw=1.5, op=0.85, fill=fill, fill_op=0.95, angle=-50, shape=f'<path d="{d}"/>')
    for p in range(2):
        add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2.4 if p == 0 else 1.3}" stroke-linejoin="round" '
            f'transform="translate({j(1.5):.1f},{j(1.5):.1f})"/>')
    rline(cx - 26, cy - 40, cx + 26, cy - 40, INK, 2.0, 2)


def vial(cx, cy, key="corazon"):
    fill, stroke = PAL[key]
    hachure(cx - 16, cy - 46, 32, 100, stroke, gap=6, sw=1.4, op=0.85, fill=fill, fill_op=0.95,
            shape=f'<rect x="{cx - 16}" y="{cy - 30}" width="32" height="84" rx="14"/>')
    rrect(cx - 16, cy - 30, 32, 84, stroke, 2.2)
    hachure(cx - 20, cy - 50, 40, 20, PAL["neutro"][1], gap=5, sw=1.2, op=0.6, fill=PAL["neutro"][0], fill_op=0.9)
    rrect(cx - 20, cy - 50, 40, 20, PAL["neutro"][1], 2.0)
    for k in range(2):
        hachure(cx + 22 + k * 28, cy + 58, 26, 34, stroke, gap=5, sw=1.2, op=0.5, fill=fill, fill_op=0.6,
                shape=f'<circle cx="{cx + 35 + k * 28}" cy="{cy + 75}" r="13"/>')
        rellipse(cx + 35 + k * 28, cy + 75, 13, 13, stroke, 1.8, n=16)


def product(x, y, draw, title, sub, key, faded=False):
    draw(x + 60, y + 80, key)
    text(x + 125, y + 62, title, 30, INK if not faded else "#8f8a82", font="Caveat", weight=700)
    for i, sline in enumerate(sub):
        text(x + 125, y + 92 + i * 26, sline, 20, "#5e5a53")


# ----------------------------------------------------------------------------- composición
def build(d):
    opt = d["E1|Óptimo económico"]; s = opt["sizes"]; pr = opt["scen"][0]["products"]
    b = d.get("E5|B óptimo económico", {}).get("sizes", {})
    wine_sold = pr["vino_m3"] - pr.get("vino_a_vinagre_m3", 0)
    fmt = lambda v: f"{v:,.0f}".replace(",", " ")

    text(60, 72, "Superestructura de la biorrefinería de piña", 58, INK, font="Caveat", weight=700)
    text(62, 112, "Cada ∨ es una disyunción (Grossmann cap. 10): el MILP elige una alternativa y su tamaño. En color, el diseño óptimo de la versión 12 "
                  "(Chocó 2022); en gris, las alternativas descartadas. Nuevo en la v12: vino embotellado con impuesto al consumo y tope de demanda de vino.", 21, "#5e5a53")

    # fruta y frente
    pineapple(170, 790, 1.0)
    text(170, 935, "Fruta de rechazo", 32, INK, anchor="middle", font="Caveat", weight=700)
    text(170, 963, f"{fmt(opt['scen'][0]['supply'])} t/año (EVA 2022)", 20, "#5e5a53", anchor="middle")
    text(170, 989, "estacional: dos cosechas", 19, "#6f6a62", anchor="middle", italic=True)
    bF, _ = card(300, 660, 220, "Frente", [f"{s['Frente']}", "1 · 2 · 5 · 8 t/h"], "neutro", chosen=(0,),
                 note="lavado · pelado")
    arrow(245, 790, 298, 760, INK, 2.4, 0.0, head=14)

    # reparto en fracciones
    hx, hy = 585, 760
    arrow(right(bF)[0], right(bF)[1], hx, hy, INK, 2.4, 0.0, head=0)
    rellipse(hx, hy, 9, 9, INK, 2.4, n=12)
    rows = dict(pulpa=330, cascara=880, corazon=1235, corona=1500)

    # ---- fila de pulpa: vino
    bE, cE = card(650, 200, 250, "Extracción", [f"Prensa de banda {s['Prensa']}", "Decantadora centrífuga"], "pulpa",
                  chosen=(0,) if s["Prensa"] != "no" else (1,))
    arrow(hx + 6, hy - 6, left(bE)[0] - 4, left(bE)[1], PAL["pulpa"][1], 2.6, -0.15, label="pulpa 45 %", lab_dy=-14, lab_color=PAL["pulpa"][1])
    clar_opts = ["Centrífuga", "Flotación", "MF del mosto (27 % retenido)"]
    ci = 0 if s["Clarificación"].startswith("Centr") else 1 if s["Clarificación"].startswith("Flot") else 2
    clar_opts[ci] = clar_opts[ci].split(" (")[0] + " " + " ".join(s["Clarificación"].split()[1:])
    bC, cC = card(945, 200, 290, "Clarificación", clar_opts, "agua", chosen=(ci,), note="turbidez objetivo 100–200 NTU")
    arrow(right(bE)[0] + 2, right(bE)[1], left(bC)[0] - 4, left(bC)[1], PAL["pulpa"][1], 2.6, 0.05)
    est_opts = ["SO₂ (≈ 50 mg/L)", "Pasteurización HTST", "UHPH 300 MPa"]
    ei = 0 if s["Estabilización"].startswith("SO") else 1 if s["Estabilización"].startswith("HTST") else 2
    bS, cS = card(1280, 200, 245, "Estabilización", est_opts, "agua", chosen=(ei,))
    arrow(right(bC)[0] + 2, right(bC)[1] - 20, left(bS)[0] - 4, left(bS)[1] - 20, PAL["agua"][1], 2.6, 0.05)
    bP, cP = card(1570, 200, 205, "Pulmón", [f"{s['Almacén de mosto']}", "aséptico 25–800 m³"], "agua", chosen=(0,))
    arrow(right(bS)[0] + 2, right(bS)[1], left(bP)[0] - 4, left(bP)[1], PAL["agua"][1], 2.6, 0.05)
    bB, cB = card(1820, 200, 235, "Bodega", [f"{s['Bodega']}", "+ N₂ y DAP"], "pulpa", chosen=(0, 1), disjunction=False,
                  note="Q ≤ (N_F − 1)·V_F / t")
    arrow(right(bP)[0] + 2, right(bP)[1], left(bB)[0] - 4, left(bB)[1], PAL["pulpa"][1], 2.6, 0.05)
    product(PX, 170, bottle, "Vino embotellado" if dm_mod.BOTTLED else "Vino a granel",
            [f"≈ {fmt(pr.get('botellas', 0) / 1000)} mil botellas/año" if dm_mod.BOTTLED else f"≈ {fmt(wine_sold)} m³/año", "guarda de 90 días"], "pulpa")
    arrow(right(bB)[0] + 2, right(bB)[1] - 30, PX + 22, 260, PAL["pulpa"][1], 2.6, -0.1)

    # lías
    bL, cL = card(945, 520, 290, "Lodos y lías (12 %)", [f"MF de lías {s['MF lías']}", "al secador → harina", "compostaje"],
                  "agua", chosen=(0, 1), note="la MF recupera el 60 % del jugo")
    arrow(bC[0] + 145, bC[1] + bC[3] + 2, bL[0] + 145, bL[1] - 4, PAL["agua"][1], 2.2, 0.0, dash="7 6")
    arrow(right(bL)[0] + 2, cL[0][1], bS[0] + 110, bS[1] + bS[3] + 4, PAL["agua"][1], 2.2, 0.18, label="jugo recuperado", lab_size=18, lab_dy=26)

    # ---- fila de cáscara: harina y vinagre
    lime = s.get("Pretratamiento cáscara", "agua") != "agua"
    jf, kf = (0.684, 0.316) if lime else (0.578, 0.422)
    bT, cT = card(650, 575, 250, "Pretratamiento", ["agua (jugo 58 %)", "Ca(OH)₂ 0,1 % (jugo 68 %)"], "cascara",
                  chosen=(1,) if lime else (0,), note="Campos 2020 · Seguí 2018")
    bK, cK = card(650, 800, 250, "Prensa de cáscara", [f"dedicada {s['Prensa cáscara']}", "compartida con la pulpa"], "cascara",
                  chosen=(0,) if s["Prensa cáscara"] != "no" else (1,))
    arrow(bT[0] + 125, bT[1] + bT[3] + 2, bK[0] + 125, bK[1] - 4, PAL["cascara"][1], 2.2, 0.0)
    arrow(hx + 6, hy + 4, left(bK)[0] - 4, left(bK)[1], PAL["cascara"][1], 2.6, 0.12, )
    text(470, 905, "cáscara 30 %", 22, PAL["cascara"][1], anchor="middle")
    bD, cD = card(1280, 800, 245, "Secador de banda", [f"{s['Secador']}", "50 · 200 · 300 · 500 · 800"], "cascara", chosen=(0,),
                  note="+ molino y tamiz")
    arrow(right(bK)[0] + 2, cK[0][1], left(bD)[0] - 4, left(bD)[1] - 10, PAL["cascara"][1], 2.6, -0.05, label=f"torta ({kf * 100:.0f} %, 17 % MS)", lab_size=19)
    arrow(cL[1][0] + 120, cL[1][1] + 22, bD[0] + 60, bD[1] - 4, PAL["cascara"][1], 2.0, 0.1, dash="7 6")
    product(PX, 770, sack, "Harina de fibra", [f"≈ {fmt(pr['harina_t'] + pr.get('harina_lias_t', 0))} t/año", "cáscara + lías"], "cascara")
    arrow(right(bD)[0] + 2, right(bD)[1], PX + 10, 850, PAL["cascara"][1], 2.6, 0.06)

    hub_on = (pr.get("citrico_kg", 0) + pr.get("xantana_kg", 0)) > 0
    bJ, cJ = card(945, 1010, 290, "Jugo de cáscara", [f"fermentar {s['Bodega cáscara']}" + (" + panela" if pr.get("azucar_kg", 0) > 1 else ""), "venta al hub (150 COP/kg)", "ácido cítrico · xantana"], "vinagre",
                  chosen=tuple(i for i, on in enumerate((s["Bodega cáscara"] != "no", pr.get("jugo_cascara_t", 0) > pr.get("jugo_cascara_vinagre_t", 0) + 1, hub_on)) if on) or (1,))
    arrow(bK[0] + 125, bK[1] + bK[3] + 2, left(bJ)[0] - 4, left(bJ)[1], PAL["vinagre"][1], 2.4, 0.15, label=f"jugo ({jf * 100:.0f} %)", lab_size=19, lab_dy=28)
    enz = s.get("Enzima cáscara", "no")
    eo = ["precipitación con polisacárido", "UF 10 kDa + liofilización", "sin separar"]
    ei_ = 2 if enz == "no" else (0 if enz.startswith("Prec") else 1)
    if enz != "no":
        eo[ei_] = eo[ei_].split(" con")[0].split(" +")[0] + " " + " ".join(enz.split()[1:])
    bZ, cZ = card(1262, 1010, 300, "Enzima del jugo", eo, "corazon", chosen=(ei_,), note="sin proteasas el jugo fermenta mejor")
    bA, cA = card(1600, 1010, 290, "Acetificador Frings", [f"{s['Acetificador']} · 50 kg/m³·d", "2 · 4 · 6 · 20 m³ · no"], "vinagre",
                  chosen=(0,) if s["Acetificador"] != "no" else (1,), note="frío · grupo electrógeno")
    arrow(right(bJ)[0] + 2, cJ[0][1], left(bZ)[0] - 4, cZ[0][1], PAL["vinagre"][1], 2.6, 0.0)
    arrow(right(bZ)[0] + 2, cZ[0][1], left(bA)[0] - 4, cA[0][1], PAL["vinagre"][1], 2.6, 0.0)
    arrow(bB[0] + 60, bB[1] + bB[3] + 4, bA[0] + 190, bA[1] - 4, PAL["vinagre"][1], 2.6, 0.12, dash="10 6")
    text(bB[0] + 80, bB[1] + bB[3] + 250, "vino desviado", 21, PAL["vinagre"][1])
    text(bB[0] + 80, bB[1] + bB[3] + 276, f"≈ {fmt(pr.get('vino_a_vinagre_m3', 0))} m³/año", 21, PAL["vinagre"][1])
    product(PX, 990, jar, "Vinagre al 5 %", [f"≈ {fmt(pr.get('vinagre_m3', 0))} m³/año", "Emde 2017 · Bekatorou 2020"], "vinagre")
    arrow(right(bA)[0] + 2, right(bA)[1], PX + 16, 1075, PAL["vinagre"][1], 2.6, 0.05)

    # ---- fila de corazón: bromelaína (configuración B)
    bR, cR = card(650, 1225, 250, "Prensa de corazón", ["compartida con pulpa", "dedicada", "compostaje"], "corazon",
                  chosen=(0,) if b.get("Prensa corazón", "no") == "no" and b else (), optional=True)
    arrow(hx + 2, hy + 8, left(bR)[0] - 4, left(bR)[1], PAL["corazon"][1], 2.4, 0.2, dash="9 7", label="corazón 10 %", lab_dy=40,
          lab_color=PAL["corazon"][1])
    bU, cU = card(985, 1275, 290, "Bromelaína", [f"aspersión {b.get('Aspersión', '25 kg agua/h')}", "UF 10 kDa (o 75 + 10 kDa)"], "corazon",
                  chosen=(0, 1), disjunction=False, optional=True, note="Vasiljevic 2020")
    arrow(right(bR)[0] + 2, cR[0][1], left(bU)[0] - 4, left(bU)[1], PAL["corazon"][1], 2.4, -0.04, dash="9 7")
    product(PX, 1220, vial, "Bromelaína cruda", [f"≈ {fmt(pr.get('enzima_cascara_kg', 0))} kg/año del jugo de cáscara" if enz != "no" else "del jugo de cáscara: desde 2× la oferta",
                                                  "del corazón: solo en la config. B"], "corazon")
    arrow(right(bU)[0] + 2, right(bU)[1], PX + 38, 1300, PAL["corazon"][1], 2.4, 0.05, dash="9 7")
    if enz != "no":
        arrow(bZ[0] + 150, bZ[1] + bZ[3] + 2, PX + 20, 1270, PAL["corazon"][1], 2.6, -0.12)

    # ---- corona
    boiler = s.get("Caldera de corona", "no")
    bO, _ = card(650, 1452, 330, "Corona", [f"caldera de biomasa {boiler if boiler != 'no' else '100–500 kWt'}", "compostaje"], "corona",
                 chosen=(0,) if boiler != "no" else (1,),
                 note=(f"→ {fmt(pr.get('calor_corona_GJ', 0))} GJ/año de calor al secador" if boiler != "no" else "calor para el secador"))
    arrow(hx - 2, hy + 10, left(bO)[0] - 4, left(bO)[1], PAL["corona"][1], 2.2, 0.28, label="corona 15 %", lab_dy=120, lab_color=PAL["corona"][1])

    # ---- hojas de la planta (v10: Chen et al. 2020; Liao et al. 2022 y 2026)
    ext = s.get("Extractora hojas", "no")
    text(170, 1770, "Hojas de la planta", 30, INK, anchor="middle", font="Caveat", weight=700)
    text(170, 1798, "renovación del cultivo", 19, "#5e5a53", anchor="middle")
    text(170, 1822, f"{fmt(dm_mod.HOJAS_SUPPLY)} t/año acopiables", 19, "#6f6a62", anchor="middle", italic=True)
    for k_ in range(5):
        rline(120 + k_ * 22, 1745, 140 + k_ * 16, 1690 - (k_ % 2) * 18, PAL["corazon"][1], 2.4, 2)
    bH, cH = card(650, 1700, 300, "Hojas", [f"extractora {ext}" if ext != "no" else "extractora 2–60 t/h", "dejar en el campo"], "corazon",
                  chosen=(0,) if ext != "no" else (1,), note=(f"≈ {fmt(pr.get('hojas_t', 0))} t/año acopiadas" if ext != "no" else "Chen 2020 · Liao 2022, 2026"))
    arrow(300, 1790, left(bH)[0] - 4, left(bH)[1], PAL["corazon"][1], 2.4, 0.0)
    flows = (pr.get("jugo_hojas_vinagre_t", 0), pr.get("jugo_hojas_etanol_t", 0), pr.get("jugo_hojas_digestor_t", 0), pr.get("jugo_hojas_campo_t", 0))
    bLJ, cLJ = card(1010, 1700, 330, "Jugo de hojas (76 %)", ["vinagre (mezclado con vino)", "etanol + levadura (K. marxianus)", "digestor → electricidad", "devolver al campo"],
                    "vinagre", chosen=tuple(i for i, f_ in enumerate(flows) if f_ > 1) if ext != "no" else ())
    arrow(right(bH)[0] + 2, cH[0][1], left(bLJ)[0] - 4, cLJ[0][1], PAL["vinagre"][1], 2.4, 0.0)
    pflows = (pr.get("pulpa_hojas_caldera_t", 0), pr.get("pulpa_hojas_campo_t", 0))
    bPH, cPH = card(1400, 1700, 300, "Pulpa de hojas (18 %)", ["combustible de la caldera", "devolver al campo"], "corona",
                    chosen=tuple(i for i, f_ in enumerate(pflows) if f_ > 1) if ext != "no" else ())
    ylow = bLJ[1] + bLJ[3] + 26          # la pulpa pasa por debajo de la tarjeta del jugo
    rline(bH[0] + 150, bH[1] + bH[3] + 2, bH[0] + 150, ylow, PAL["corona"][1], 2.0, 2, dash="7 6")
    rline(bH[0] + 150, ylow, bPH[0] + 60, ylow, PAL["corona"][1], 2.0, 2, dash="7 6")
    arrow(bPH[0] + 60, ylow, bPH[0] + 60, bPH[1] + bPH[3] + 4, PAL["corona"][1], 2.0, 0.0, dash="7 6")
    text(bH[0] + 170, ylow - 8, "pulpa", 18, PAL["corona"][1])
    if flows[0] > 1:
        arrow(right(bLJ)[0] + 2, cLJ[0][1], bA[0] + 40, bA[1] + bA[3] + 4, PAL["vinagre"][1], 2.4, 0.15, label="al acetificador", lab_size=18, lab_dy=-8)
    if pflows[0] > 1:
        arrow(bPH[0] + 40, bPH[1] - 4, bO[0] + 300, bO[1] + bO[3] + 4, PAL["corona"][1], 2.2, 0.2)
    if pr.get("etanol_L", 0) > 1 or pr.get("elec_bio_kWh", 0) > 1:
        product(PX, 1700, vial, "Etanol y energía", [f"≈ {fmt(pr.get('etanol_L', 0))} L/año de etanol", f"≈ {fmt(pr.get('elec_bio_kWh', 0) / 1000)} MWh/año de biogás"], "corazon")

    # ---- leyenda y palancas
    lx, ly = 1180, 2000
    rrect(lx, ly, 1340, 160, PAL["neutro"][1], 1.8, dash="8 7", passes=1)
    text(lx + 20, ly + 38, "Cómo leer", 30, INK, font="Caveat", weight=700)
    hachure(lx + 20, ly + 56, 120, 34, PAL["pulpa"][1], gap=6.5, sw=1.4, op=0.6, fill=PAL["pulpa"][0], fill_op=0.75)
    rrect(lx + 20, ly + 56, 120, 34, PAL["pulpa"][1], 1.8)
    check(lx + 108, ly + 74, PAL["pulpa"][1])
    text(lx + 152, ly + 80, "alternativa elegida", 20, INK)
    rrect(lx + 340, ly + 56, 120, 34, GREY, 1.6, dash="6 6", passes=1)
    text(lx + 472, ly + 80, "descartada", 20, "#8f8a82")
    disj(lx + 620, ly + 73, INK)
    text(lx + 646, ly + 80, "disyunción: se elige una", 20, INK)
    rline(lx + 900, ly + 73, lx + 960, ly + 73, PAL["corazon"][1], 2.4, 2, dash="9 7")
    text(lx + 970, ly + 80, "opcional (config. B)", 20, INK)
    text(lx + 20, ly + 122, "Palancas operativas en el mismo MILP: tercer turno en el frente · almacén aséptico de mosto · compostaje de fracciones.", 19, "#5e5a53")
    text(lx + 20, ly + 146, "Operación anual en tiempo continuo (Maravelias), costos del TEA de Burk y tamaños de catálogo.", 19, "#5e5a53")


def fonts_css():
    css = []
    for fam, wt, fn in (("Kalam", 400, "Kalam-400.woff2"), ("Kalam", 700, "Kalam-700.woff2"), ("Caveat", 700, "Caveat-700.woff2")):
        b64 = base64.b64encode(open(os.path.join(FIGS, "fonts", fn), "rb").read()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "".join(css)


def svg_doc():
    defs = f'''<defs><style>{fonts_css()}</style>
<filter id="pencil" x="-2%" y="-2%" width="104%" height="104%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="1" seed="9" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 1.3" result="ga"/>
  <feComposite in="d" in2="ga" operator="in"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="5" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 1.25" result="ga"/>
  <feComposite in="SourceGraphic" in2="ga" operator="in"/>
</filter></defs>'''
    body = "\n".join(out)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}'
            f'<rect width="{W}" height="{H}" fill="#fdfcfa"/><g filter="url(#pencil)">{body}</g></svg>')


if __name__ == "__main__":
    d = json.load(open(os.path.join(HERE, "results", "dimensionamiento.json")))
    build(d)
    svg = svg_doc()
    p_svg = os.path.join(FIGS, "fig33_superestructura.svg")
    open(p_svg, "w", encoding="utf-8").write(svg)
    import subprocess, tempfile
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {W}, height: {H} }}, deviceScaleFactor: 1.25 }});
  await p.goto('file://{p_svg}');
  await p.waitForTimeout(800);
  await p.screenshot({{ path: '{os.path.join(FIGS, "fig33_superestructura.png")}' }});
  await b.close();
}})();"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(js)
    subprocess.run(["node", f.name], check=True)
    os.unlink(f.name)
    print("fig fig33_superestructura.svg/.png", len(svg) // 1024, "KB")
