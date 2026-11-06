"""
Diagrama de flujo del proceso (PFD) de la biorrefinería de piña dibujado a mano (estilo de las figs. 33–35).

Equipos como iconos con su etiqueta y tamaño del diseño óptimo (results/dimensionamiento.json, E1|Óptimo económico),
corrientes numeradas y tabla de corrientes con los caudales del balance de masa (balance_dibujo.flows_v7).
Salidas: figs/fig36_pfd.svg (autocontenido) y figs/fig36_pfd.png.
"""
import json, math, os, subprocess, tempfile
import superestructura_dibujo as sd
import balance_dibujo as bd
import dimensionamiento as dm

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
sd.W, sd.H = 2960, 1780
PAL = sd.PAL
INK, GREY = sd.INK, sd.GREY
HOT = "#b0694f"; COLD = "#5e7d96"
PAL.setdefault("elec", ("#efe2ae", "#a68a33"))
fmt = lambda v: f"{v:,.0f}".replace(",", " ")


# ----------------------------------------------------------------------------- tuberías y etiquetas
def pipe(pts, color=INK, sw=2.4, dash=None, num=None, at=0.5, head=True):
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        sd.rline(x1, y1, x2, y2, color, sw, 2, bow=0.004, dash=dash, over=1.0)
    if head:
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        L = math.hypot(x2 - x1, y2 - y1) or 1
        tx, ty = (x2 - x1) / L, (y2 - y1) / L
        for s in (1, -1):
            a = math.radians(25 * s)
            hx, hy = tx * math.cos(a) - ty * math.sin(a), tx * math.sin(a) + ty * math.cos(a)
            sd.rline(x2, y2, x2 - hx * 14, y2 - hy * 14, color, sw, 1, over=0.5)
    if num is not None:
        segs = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts[:-1], pts[1:])]
        tot = sum(s[2] for s in segs); t = at * tot
        for a, b, L in segs:
            if t <= L:
                px, py = a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L
                break
            t -= L
        tag(px, py, num, color)


def tag(x, y, n, color=INK):
    sd.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="#fdfcfa"/>')
    sd.rellipse(x, y, 16, 16, color, 1.8, n=16)
    sd.text(x, y + 7, str(n), 19, color, anchor="middle", font="Kalam", weight=700)


def label(x, y, code, name, size_txt=None, anchor="middle"):
    sd.text(x, y, code, 17, "#8a8378", anchor=anchor, font="Kalam", weight=700)
    sd.text(x, y + 26, name, 24, INK, anchor=anchor, font="Caveat", weight=700)
    if size_txt:
        sd.text(x, y + 49, size_txt, 17, "#5e5a53", anchor=anchor)


# ----------------------------------------------------------------------------- iconos de equipos
def box(x, y, w, h, key):
    fill, stroke = PAL[key]
    sd.hachure(x, y, w, h, stroke, gap=8, sw=1.3, op=0.45, fill=fill, fill_op=0.7)
    sd.rrect(x, y, w, h, stroke, 2.3)
    return stroke


def vessel(cx, top, w, h, key, cone=True, agitator=False, jacket=False, coil=False):
    fill, stroke = PAL[key]
    x0, x1 = cx - w / 2, cx + w / 2
    bot = top + h
    d = (f"M{x0},{top + 16} Q{cx},{top - 16} {x1},{top + 16} L{x1},{bot - (34 if cone else 6)} "
         + (f"L{cx + 10},{bot} L{cx - 10},{bot} L{x0},{bot - 34} Z" if cone else f"Q{cx},{bot + 12} {x0},{bot - 6} Z"))
    sd.hachure(x0, top - 10, w, h + 12, stroke, gap=8, sw=1.3, op=0.5, fill=fill, fill_op=0.75, shape=f'<path d="{d}"/>')
    for p in range(2):
        sd.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2.4 if p == 0 else 1.3}" stroke-linejoin="round" '
               f'transform="translate({sd.j(1.3):.1f},{sd.j(1.3):.1f})"/>')
    if jacket:
        sd.rline(x0 - 7, top + 30, x0 - 7, bot - 40, stroke, 1.6, 1, dash="5 4")
        sd.rline(x1 + 7, top + 30, x1 + 7, bot - 40, stroke, 1.6, 1, dash="5 4")
    if coil:
        for k in range(4):
            yy = top + 40 + k * (h - 90) / 3
            sd.rline(x0 + 8, yy, x1 - 8, yy + 8, COLD, 1.5, 1, op=0.8)
    if agitator:
        sd.rline(cx, top - 26, cx, bot - 30, INK, 2.0, 1)
        sd.rline(cx - 18, bot - 36, cx + 18, bot - 28, INK, 2.4, 1)
        sd.rrect(cx - 10, top - 40, 20, 14, INK, 1.6, passes=1)
    return x0, x1, top, bot


def rollers(x, y, w, h, key):
    st = box(x, y, w, h, key)
    for k, cx in enumerate((x + w * 0.3, x + w * 0.7)):
        sd.rellipse(cx, y + h / 2, 14, 14, INK, 1.8, n=14)
    sd.rline(x + w * 0.3 - 14, y + h / 2 - 15, x + w * 0.7 + 14, y + h / 2 - 15, INK, 1.6, 1)
    sd.rline(x + w * 0.3 - 14, y + h / 2 + 15, x + w * 0.7 + 14, y + h / 2 + 15, INK, 1.6, 1)


def zigzag(x, y, w, h, key):
    box(x, y + 20, w, h - 20, key)
    sd.rline(x + 10, y + 20, x + w / 2 - 12, y - 10, INK, 2.0, 1); sd.rline(x + w - 10, y + 20, x + w / 2 + 12, y - 10, INK, 2.0, 1)
    pts = [(x + 12 + k * (w - 24) / 6, y + h / 2 + 10 + (12 if k % 2 else -12)) for k in range(7)]
    for a, b in zip(pts[:-1], pts[1:]):
        sd.rline(a[0], a[1], b[0], b[1], INK, 1.8, 1)


def knife(x, y, w, h, key):
    box(x, y, w, h, key)
    cx, cy = x + w / 2, y + h / 2
    sd.rellipse(cx, cy, 22, 22, INK, 1.8, n=16)
    for a in range(0, 360, 60):
        r = math.radians(a)
        sd.rline(cx, cy, cx + 22 * math.cos(r), cy + 22 * math.sin(r), INK, 1.5, 1)


def centrifuge(cx, cy, key):
    fill, stroke = PAL[key]
    d = f"M{cx - 46},{cy - 34} L{cx + 46},{cy - 34} L{cx + 16},{cy + 36} L{cx - 16},{cy + 36} Z"
    sd.hachure(cx - 48, cy - 36, 96, 74, stroke, gap=7, sw=1.3, op=0.5, fill=fill, fill_op=0.75, shape=f'<path d="{d}"/>')
    for p in range(2):
        sd.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2.3 if p == 0 else 1.2}" stroke-linejoin="round" '
               f'transform="translate({sd.j(1.3):.1f},{sd.j(1.3):.1f})"/>')
    for k in range(4):
        yy = cy - 20 + k * 13
        sd.rline(cx - 36 + k * 7, yy, cx + 36 - k * 7, yy + 6, INK, 1.4, 1)
    sd.rline(cx, cy - 50, cx, cy - 34, INK, 2.0, 1)


def membrane(x, y, w, h, key):
    box(x, y, w, h, key)
    sd.rline(x + 6, y + h - 6, x + w - 6, y + 6, INK, 2.0, 1, dash="6 4")


def dryer(x, y, w, h, key):
    box(x, y, w, h, key)
    sd.rline(x + 14, y + h / 2 + 10, x + w - 14, y + h / 2 + 10, INK, 2.0, 2)
    for k in range(5):
        cx = x + 30 + k * (w - 60) / 4
        sd.rellipse(cx, y + h / 2 + 10, 7, 7, INK, 1.4, n=10)
        sd.rline(cx, y + h - 4, cx + 6, y + h / 2 + 24, HOT, 1.6, 1)
    sd.rline(x + w - 40, y, x + w - 40, y - 40, INK, 2.0, 1); sd.rline(x + w - 24, y, x + w - 24, y - 40, INK, 2.0, 1)


def furnace(x, y, w, h, key):
    box(x, y, w, h, key)
    bd.flame_small(x + w / 2, y + h / 2 + 8, key)
    sd.rline(x + w - 36, y, x + w - 36, y - 70, INK, 2.2, 1); sd.rline(x + w - 18, y, x + w - 18, y - 70, INK, 2.2, 1)


def hammer(x, y, w, h, key):
    box(x, y, w, h, key)
    cx, cy = x + w / 2, y + h / 2
    sd.rellipse(cx, cy, 20, 20, INK, 1.8, n=14)
    for a in (20, 140, 260):
        r = math.radians(a)
        sd.rline(cx, cy, cx + 26 * math.cos(r), cy + 26 * math.sin(r), INK, 2.2, 1)


def turbine_vessel(cx, top, w, h, key):
    x0, x1, top, bot = vessel(cx, top, w, h, key, cone=False, coil=True)
    sd.rline(cx, bot + 4, cx, bot - 24, INK, 2.0, 1)
    for a in range(0, 360, 45):
        r = math.radians(a)
        sd.rline(cx, bot - 24, cx + 16 * math.cos(r), bot - 24 + 7 * math.sin(r), INK, 1.6, 1)
    return x0, x1, top, bot


def util_icon(x, y, glyph, key, title, sub):
    st = box(x, y, 92, 70, key)
    if glyph == "G":
        sd.rellipse(x + 46, y + 35, 22, 22, INK, 2.0, n=16)
        sd.text(x + 46, y + 44, "G", 26, INK, anchor="middle", font="Kalam", weight=700)
    elif glyph == "snow":
        for a in (0, 60, 120):
            r = math.radians(a)
            sd.rline(x + 46 - 22 * math.cos(r), y + 35 - 22 * math.sin(r), x + 46 + 22 * math.cos(r), y + 35 + 22 * math.sin(r), COLD, 2.2, 1)
    else:
        sd.text(x + 46, y + 46, glyph, 30, INK, anchor="middle", font="Kalam", weight=700)
    sd.text(x + 106, y + 30, title, 24, INK, font="Caveat", weight=700)
    sd.text(x + 106, y + 54, sub, 17, "#5e5a53")


# ----------------------------------------------------------------------------- composición
def build():
    d = json.load(open(os.path.join(HERE, "results", "dimensionamiento.json")))
    r = d["E1|Óptimo económico"]; s = r["sizes"]; f = bd.flows_v7()
    pr = r["scen"][0]["products"]
    sd.text(60, 72, "Diagrama de flujo del proceso", 58, INK, font="Caveat", weight=700)
    sd.text(62, 112, "Diseño óptimo de la versión 11 · Chocó 2022. Equipos con su tamaño de catálogo; corrientes numeradas con sus caudales en la tabla "
                     "(t/año). Línea continua: proceso; terracota discontinua: calor; azul discontinua: frío.", 21, "#5e5a53")
    # --- frente
    pipe([(40, 330), (108, 330)], INK, num=1, at=0.45)
    sd.text(40, 300, "fruta", 20, "#5e5a53")
    box(110, 285, 150, 90, "neutro")
    for k in range(3):
        sd.rline(124, 330 + k * 12, 246, 336 + k * 12, COLD, 1.4, 1, op=0.8)
    label(185, 410, "L-101", "Recepción y lavado", f"{s['Frente']}")
    pipe([(262, 330), (318, 330)], INK)
    knife(320, 285, 140, 90, "neutro")
    label(390, 215, "P-101", "Pelado y descorazonado")
    # --- línea de pulpa y vino
    pipe([(462, 315), (538, 315)], PAL["pulpa"][1], num=2, at=0.5)
    zigzag(540, 270, 120, 110, "pulpa"); label(600, 410, "T-101", "Trituradora")
    pipe([(662, 330), (690, 330)], PAL["pulpa"][1])
    vessel(735, 250, 80, 150, "pulpa", cone=False, agitator=True, jacket=True)
    label(735, 150, "M-101", "Macerador 55 °C", "pectinasa, 1 h")
    pipe([(778, 330), (838, 330)], PAL["pulpa"][1])
    rollers(840, 290, 150, 80, "pulpa"); label(915, 215, "PR-101", "Prensa de banda", s["Prensa"])
    pipe([(915, 372), (915, 470)], "#8a6f52", num=7, at=0.55); sd.text(915, 495, "bagazo a compost", 17, "#8a6f52", anchor="middle")
    pipe([(992, 330), (1062, 330)], PAL["pulpa"][1], num=6, at=0.45)
    centrifuge(1115, 330, "agua"); label(1085, 200, "C-101", "Centrífuga", s["Clarificación"].replace("Centrífuga ", ""))
    sd.rrect(1180, 196, 40, 46, PAL["agua"][1], 1.8); sd.text(1200, 226, "SO₂", 15, INK, anchor="middle", font="Kalam", weight=700)
    pipe([(1200, 244), (1200, 316)], PAL["agua"][1], sw=1.8)
    pipe([(1162, 330), (1238, 330)], PAL["agua"][1], num=8, at=0.65)
    vessel(1275, 270, 70, 120, "agua", cone=False); label(1275, 445, "TK-101", "Pulmón", s["Almacén de mosto"])
    pipe([(1312, 330), (1366, 330)], PAL["agua"][1])
    vessel(1405, 235, 70, 175, "pulpa", cone=True, coil=True); vessel(1495, 235, 70, 175, "pulpa", cone=True, coil=True)
    label(1450, 445, "F-101/102", "Fermentadores", s["Bodega"] + " · N₂ · DAP")
    sd.text(1450, 222, "❄", 26, COLD, anchor="middle")
    pipe([(1532, 330), (1586, 330)], PAL["pulpa"][1], num=11, at=0.5)
    vessel(1620, 260, 56, 130, "pulpa", cone=False); vessel(1690, 260, 56, 130, "pulpa", cone=False)
    label(1655, 445, "TK-102/103", "Guarda 90 días")
    pipe([(1720, 330), (1790, 330)], PAL["pulpa"][1], num=13, at=0.45)
    sd.bottle(1840, 320, "pulpa"); sd.text(1840, 430, "Vino a granel", 24, INK, anchor="middle", font="Caveat", weight=700)
    # lodos y MF de lías
    pipe([(1115, 368), (1115, 540)], PAL["agua"][1], num=9, at=0.55)
    membrane(1060, 542, 110, 64, "agua"); sd.text(1185, 572, "MF-101", 17, "#8a8378", font="Kalam", weight=700)
    sd.text(1185, 596, f"MF de lías {s['MF lías']}", 20, INK, font="Caveat", weight=700)
    pipe([(1170, 560), (1262, 560), (1262, 396)], PAL["agua"][1], num=10, at=0.3)
    pipe([(1100, 608), (1100, 712)], "#8a6f52", num=None)
    sd.text(1092, 668, "retenido al secador", 16, "#8a6f52", anchor="end")
    # vino al acetificador
    pipe([(1655, 392), (1655, 520), (1560, 520), (1560, 940)], PAL["vinagre"][1], num=12, at=0.55)
    # --- línea de cáscara y harina
    pipe([(375, 377), (375, 760), (538, 760)], PAL["cascara"][1], num=3, at=0.6)
    rollers(540, 720, 140, 80, "cascara"); label(610, 648, "PR-102", "Prensa de cáscara", s["Prensa cáscara"])
    pipe([(682, 750), (818, 750)], PAL["cascara"][1], num=14, at=0.4)
    dryer(820, 714, 360, 90, "cascara"); label(1000, 840, "D-101", "Secador de banda", s["Secador"])
    sd.text(1166, 664, "vapor", 18, "#7f97a8", anchor="middle")
    pipe([(1182, 760), (1258, 760)], PAL["cascara"][1])
    hammer(1260, 722, 100, 76, "cascara"); label(1310, 840, "ML-101", "Molino y tamiz")
    pipe([(1362, 760), (1790, 760)], PAL["cascara"][1], num=16, at=0.15)
    sd.sack(1840, 755, "cascara"); sd.text(1840, 865, "Harina de fibra", 24, INK, anchor="middle", font="Caveat", weight=700)
    # --- jugo de cáscara y vinagre
    pipe([(610, 802), (610, 1030), (943, 1030)], PAL["vinagre"][1], num=15, at=0.5)
    vessel(985, 950, 80, 160, "vinagre", cone=True, coil=True)
    label(985, 1150, "F-201", "Fermentación de jugo", s["Bodega cáscara"])
    pipe([(1027, 1030), (1393, 1030)], PAL["vinagre"][1])
    turbine_vessel(1450, 940, 110, 190, "vinagre"); sd.text(1450, 925, "❄", 26, COLD, anchor="middle")
    label(1450, 1170, "A-101", "Acetificador Frings", f"{s['Acetificador']} · aire 0,1 vvm")
    pipe([(1350, 1110), (1393, 1110)], "#8a9aab", sw=1.8); sd.text(1300, 1116, "aire", 18, "#8a9aab", anchor="middle")
    pipe([(1507, 1030), (1598, 1030)], PAL["vinagre"][1])
    membrane(1600, 996, 100, 64, "vinagre"); sd.text(1650, 1090, "MF + tanques", 18, "#5e5a53", anchor="middle")
    pipe([(1702, 1030), (1790, 1030)], PAL["vinagre"][1], num=17, at=0.45)
    sd.jar(1840, 1030, "vinagre"); sd.text(1840, 1125, "Vinagre al 5 %", 24, INK, anchor="middle", font="Caveat", weight=700)
    pipe([(1220, 1060), (1393, 1060)], "#7d8894", sw=1.8, dash="8 6"); sd.text(1225, 1050, "agua de dilución", 16, "#7d8894")
    # --- corazón y corona, caldera
    pipe([(405, 377), (405, 1250)], PAL["corazon"][1], num=4, at=0.82, head=True)
    sd.text(396, 1276, "corazón a compost", 18, PAL["corazon"][1], anchor="end")
    sd.text(396, 1298, "(bromelaína en la config. B)", 16, "#6f6a62", anchor="end", italic=True)
    pipe([(440, 377), (440, 1330), (538, 1330)], PAL["corona"][1], num=5, at=0.8)
    zigzag(540, 1280, 130, 100, "corona"); label(605, 1410, "CH-101", "Picadora y secador")
    boiler = s.get("Caldera de corona", "no")
    pipe([(672, 1330), (758, 1330)], PAL["corona"][1], num=18, at=0.5)
    furnace(760, 1270, 150, 120, "corona"); label(835, 1420, "B-101", "Caldera de corona", boiler if boiler != "no" else "—")
    sd.text(866, 1215, "gases", 17, "#8a8176", anchor="end")
    pipe([(820, 1270), (820, 806)], HOT, sw=2.2, dash="9 6", num=19, at=0.25)
    sd.text(828, 1000, "aire caliente", 17, HOT)
    pipe([(760, 1300), (700, 1300), (700, 380), (727, 380)], HOT, sw=2.0, dash="9 6", head=True)
    sd.text(692, 1240, "agua caliente al macerador", 16, HOT, anchor="end")
    # --- hojas de la planta (v10)
    if s.get("Extractora hojas", "no") != "no":
        pipe([(1000, 1330), (1078, 1330)], PAL["corazon"][1], num=20, at=0.4)
        sd.text(1000, 1300, "hojas", 20, "#5e5a53")
        rollers(1080, 1292, 150, 76, "corazon"); label(1155, 1410, "EX-101", "Extractora de hojas", s["Extractora hojas"])
        pipe([(1130, 1292), (1130, 1080), (1027, 1080)], PAL["vinagre"][1], num=21, at=0.35)
        pipe([(1232, 1330), (1330, 1330)], PAL["corazon"][1], num=22, at=0.5)
        sd.text(1340, 1338, "pulpa al campo", 18, PAL["corazon"][1])
    if f.get("az", 0) > 0.1:   # v11: panela a la bodega de jugos
        pipe([(1150, 975), (1029, 975)], PAL["cascara"][1], num=23, at=0.4)
        sd.text(1160, 981, "panela", 18, PAL["cascara"][1])
    # --- servicios
    sd.text(60, 1530, "Servicios", 32, INK, font="Caveat", weight=700)
    util_icon(60, 1550, "G", "elec", "Grupo electrógeno diésel", "zona no interconectada; obligatorio para la aireación")
    util_icon(640, 1550, "snow", "agua", "Chillers agua-glicol", "F-101/102, F-201 y A-101 (❄)")
    util_icon(1120, 1550, "N₂", "neutro", "Generador de N₂ y DAP", "inertización y nutrientes")
    # --- tabla de corrientes
    tx, ty, tw = 1990, 160, 920
    rows = [
        (1, "Fruta de rechazo", f["F"], "6 146 t/año de oferta (EVA 2022)"),
        (2, "Pulpa", f["fr"]["pulpa"], "45 % de la fruta"),
        (3, "Cáscara", f["fr"]["cascara"], "30 %"),
        (4, "Corazón", f["fr"]["corazon"], "10 %"),
        (5, "Corona", f["fr"]["corona"], "15 %; 20 % de materia seca"),
        (6, "Jugo de pulpa", f["juice"], "55 °C tras macerar; 87 % del prensado"),
        (7, "Bagazo de pulpa", f["bagazo"], "a compost"),
        (8, "Mosto clarificado", f["clar"], "SO₂ ≈ 50 mg/L"),
        (9, "Lodos de centrífuga", f["lodos"], "12 % del jugo"),
        (10, "Jugo recuperado", f["rec"], "permeado de la MF de lías (60 %)"),
        (11, "Vino", f["wine"], "fermentación a 30 °C, 12,5 h"),
        (12, "Vino a vinagre", f["w_vin"], "sin guarda"),
        (13, "Vino a granel", f["w_sold"], "tras 90 días de guarda"),
        (14, "Torta de cáscara", f["torta"], "83 % de humedad"),
        (15, "Jugo de cáscara", f["pj"], "104 g/kg de azúcar"),
        (16, "Harina de fibra", f["flour"], "10 % de humedad; cáscara + lías"),
        (17, "Vinagre al 5 %", f["vin"], "50 kg/m³·d en el acetificador"),
        (18, "Corona a la caldera", f.get("crown_b", 0), "picada y secada"),
        (19, "Calor de la caldera", pr.get("calor_corona_GJ", 0), "GJ/año al secador y al macerador"),
    ]
    if s.get("Extractora hojas", "no") != "no":
        rows += [(20, "Hojas acopiadas", f.get("hojas", 0), "acopio en finca"),
                 (21, "Jugo de hojas", f.get("lj", 0), f"{dm.JF_H:.2f} t/t; a F-201 con el jugo de cáscara"),
                 (22, "Pulpa y pérdidas de hojas", f.get("l_campo", 0) + f.get("l_cald", 0), "devueltas al campo")]
    if f.get("az", 0) > 0.1:   # v11: panela añadida a la bodega de jugos
        rows.append((len(rows) + 1, "Panela añadida", f["az"], "a F-201; hasta 150 g/L de jugo"))
    rh = 52 if len(rows) <= 22 else 48
    th = 60 + rh * len(rows)
    sd.rrect(tx, ty, tw, th, PAL["neutro"][1], 2.0)
    sd.hachure(tx + 3, ty + 3, tw - 6, 54, PAL["neutro"][1], gap=8, sw=1.2, op=0.35, fill=PAL["neutro"][0], fill_op=0.8)
    cols = [(tx + 20, "N°"), (tx + 80, "Corriente"), (tx + 420, "t/año"), (tx + 540, "Condiciones")]
    for x, h in cols:
        sd.text(x, ty + 40, h, 26, INK, font="Caveat", weight=700, anchor="end" if h == "t/año" and False else "start")
    for i, (n, name, val, cond) in enumerate(rows):
        y = ty + 60 + i * rh
        sd.rline(tx + 8, y, tx + tw - 8, y, "#d6d0c6", 1.0, 1, over=0.5)
        tag(tx + 38, y + rh / 2, n, INK)
        sd.text(tx + 80, y + rh / 2 + 8, name, 21, INK)
        sd.text(tx + 500, y + rh / 2 + 8, fmt(val), 21, INK, anchor="end")
        sd.text(tx + 540, y + rh / 2 + 7, cond, 17.5, "#5e5a53")
    sd.text(tx, ty + th + 34, "Corriente 19 en GJ/año. Caudales del balance de masa (fig. 34); tamaños del MILP de dimensionamiento.", 17, "#6f6a62", italic=True)
    return r


if __name__ == "__main__":
    build()
    svg = sd.svg_doc()
    p_svg = os.path.join(FIGS, "fig36_pfd.svg")
    open(p_svg, "w", encoding="utf-8").write(svg)
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {sd.W}, height: {sd.H} }}, deviceScaleFactor: 1.25 }});
  await p.goto('file://{p_svg}');
  await p.waitForTimeout(800);
  await p.screenshot({{ path: '{os.path.join(FIGS, "fig36_pfd.png")}' }});
  await b.close();
}})();"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
    subprocess.run(["node", fh.name], check=True)
    os.unlink(fh.name)
    print("fig fig36_pfd.svg/.png")
