"""
Layout conceptual de la planta (vista en planta) dibujado a mano, con el estilo de las figs. 33–36.

Zonas por función y recorrido de los materiales (de oeste a este: recepción, proceso húmedo, bodega, vinagre; al sur:
biomasa y caldera, secado y harina, servicios, despacho; borde sur: compostaje, oficinas, báscula y PTAR).
Huellas de equipos aproximadas a partir de los tamaños del diseño óptimo (results/dimensionamiento.json); los tanques
se dibujan con el diámetro que da su volumen con H = 1,5·D. Es una distribución conceptual, no de ingeniería de detalle.
Salidas: figs/fig37_layout.svg (autocontenido) y figs/fig37_layout.png.
"""
import json, math, os, subprocess, tempfile
import superestructura_dibujo as sd
import balance_dibujo as bd
import planta_trl9 as pt
import dimensionamiento as dm

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
sd.W, sd.H = 3030, 1500
PAL = sd.PAL
PAL.setdefault("elec", ("#efe2ae", "#a68a33"))
PAL.setdefault("glp", ("#ecc9b8", "#b0694f"))
INK = sd.INK
S, OX, OY = 28.0, 150.0, 190.0          # px por metro y origen del plano
X = lambda m: OX + m * S
Y = lambda m: OY + m * S
fmt = lambda v: f"{v:,.0f}".replace(",", " ")
ZONES = []


def diam(V):
    return (4 * V / (1.5 * math.pi)) ** (1 / 3)


def zone(x, y, w, h, key, name, sub=None, lab_at="tl", op=0.45):
    fill, stroke = PAL[key]
    sd.hachure(X(x), Y(y), w * S, h * S, stroke, gap=11, sw=1.2, op=0.22, fill=fill, fill_op=op, angle=-30)
    sd.rrect(X(x), Y(y), w * S, h * S, stroke, 2.6)
    lx, ly = (X(x) + 12, Y(y) + 30) if lab_at == "tl" else (X(x) + 12, Y(y + h) - (34 if sub else 14))
    sd.text(lx, ly, name, 27, INK, font="Caveat", weight=700)
    if sub:
        sd.text(lx, ly + 22, sub, 16.5, "#5e5a53")
    ZONES.append((name, w * h, key))


def eq(x, y, w, h, key, txt=None, size=15):
    fill, stroke = PAL[key]
    sd.hachure(X(x), Y(y), w * S, h * S, stroke, gap=5, sw=1.3, op=0.7, fill=fill, fill_op=0.95)
    sd.rrect(X(x), Y(y), w * S, h * S, stroke, 2.0)
    if txt:
        sd.text(X(x + w / 2), Y(y + h / 2) + size * 0.35, txt, size, INK, anchor="middle")


def tank(cx, cy, V, key, txt=None, size=14):
    fill, stroke = PAL[key]
    D = diam(V); r = D / 2 * S
    sd.hachure(X(cx) - r, Y(cy) - r, 2 * r, 2 * r, stroke, gap=5, sw=1.3, op=0.7, fill=fill, fill_op=0.95,
               shape=f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{r:.1f}"/>')
    sd.rellipse(X(cx), Y(cy), r, r, stroke, 2.0, n=20)
    if txt:
        sd.text(X(cx), Y(cy) + r + 16, txt, size, INK, anchor="middle")
    return D


def flow(pts_m, key, label=None, at=0.5, dash=None, sw=3.2, lab_dy=-10):
    color = PAL[key][1] if key in PAL else key
    pts = [(X(a), Y(b)) for a, b in pts_m]
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        sd.rline(x1, y1, x2, y2, color, sw, 2, bow=0.006, dash=dash, over=1.0, op=0.85)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    L = math.hypot(x2 - x1, y2 - y1) or 1
    tx, ty = (x2 - x1) / L, (y2 - y1) / L
    for s in (1, -1):
        a = math.radians(26 * s)
        hx, hy = tx * math.cos(a) - ty * math.sin(a), tx * math.sin(a) + ty * math.cos(a)
        sd.rline(x2, y2, x2 - hx * 18, y2 - hy * 18, color, sw, 1, over=0.5)
    if label:
        segs = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts[:-1], pts[1:])]
        t = at * sum(s_[2] for s_ in segs)
        for a, b, Ls in segs:
            if t <= Ls:
                px, py = a[0] + (b[0] - a[0]) * t / Ls, a[1] + (b[1] - a[1]) * t / Ls
                break
            t -= Ls
        sd.add(f'<rect x="{px - 6 * len(label) * 0.9:.0f}" y="{py + lab_dy - 18:.0f}" width="{12 * len(label) * 0.9:.0f}" height="24" fill="#fdfcfa" opacity="0.85"/>')
        sd.text(px, py + lab_dy, label, 18, color, anchor="middle")


def dim_line(x1, y1, x2, y2, txt, off=0, vertical=False):
    if vertical:
        sd.rline(X(x1) - off, Y(y1), X(x2) - off, Y(y2), "#6f6a62", 1.4, 1)
        for yy in (y1, y2):
            sd.rline(X(x1) - off - 8, Y(yy), X(x1) - off + 8, Y(yy), "#6f6a62", 1.4, 1)
        sd.text(X(x1) - off - 14, Y((y1 + y2) / 2), txt, 20, "#6f6a62", anchor="end")
    else:
        sd.rline(X(x1), Y(y1) - off, X(x2), Y(y2) - off, "#6f6a62", 1.4, 1)
        for xx in (x1, x2):
            sd.rline(X(xx), Y(y1) - off - 8, X(xx), Y(y1) - off + 8, "#6f6a62", 1.4, 1)
        sd.text(X((x1 + x2) / 2), Y(y1) - off - 10, txt, 20, "#6f6a62", anchor="middle")


def build():
    d = json.load(open(os.path.join(HERE, "results", "dimensionamiento.json")))
    r = d["E1|Óptimo económico"]; s = r["sizes"]; pr = r["scen"][0]["products"]
    f = bd.flows_v7()
    sd.text(60, 72, "Layout conceptual de la planta", 58, INK, font="Caveat", weight=700)
    sd.text(62, 112, "Vista en planta, a escala aproximada. Zonas por función y recorrido de los materiales de oeste a este; huellas de equipos del diseño "
                     "óptimo de la versión 8 (Chocó 2022). Distribución conceptual: no es ingeniería de detalle.", 21, "#5e5a53")
    # lote y vías
    sd.rrect(X(0), Y(0), 70 * S, 45 * S, INK, 2.8)
    for y0 in (14, 30):
        sd.hachure(X(0), Y(y0), 70 * S, 4 * S, "#9a948a", gap=14, sw=1.0, op=0.18, fill="#e7e3dc", fill_op=0.7, angle=0)
        sd.rline(X(1), Y(y0 + 2), X(69), Y(y0 + 2), "#9a948a", 1.6, 1, dash="16 12")
    sd.text(X(35), Y(16) + 7, "vía interna (camiones)", 18, "#7a746b", anchor="middle")
    sd.text(X(35), Y(32) + 7, "vía interna", 18, "#7a746b", anchor="middle")
    # portones
    for y0 in (14, 30):
        sd.rline(X(0), Y(y0) + 6, X(0), Y(y0 + 4) - 6, "#fdfcfa", 8, 1, over=0)
        sd.text(X(0.6), Y(y0 + 3.6), "portón", 16, "#7a746b")
    # ---------------- zonas norte
    zone(0, 0, 12, 14, "cascara", "Recepción de fruta", "patio cubierto · 3 días de pico")
    for i in range(3):
        for k in range(4):
            sd.rrect(X(1 + k * 2.6), Y(4 + i * 3), 2.0 * S, 2.0 * S, PAL["cascara"][1], 1.4, passes=1)
    sd.text(X(6), Y(13.4), "canastillas de fruta", 15, "#5e5a53", anchor="middle")
    zone(12, 0, 22, 14, "neutro", "Nave de proceso húmedo", "piso sanitario, drenajes")
    eq(13, 3, 8, 2, "neutro", f"lavado y selección {s['Frente']}")
    eq(21.6, 2.6, 2.6, 1.8, "neutro", "peladora"); eq(21.6, 4.8, 2.6, 1.8, "neutro", "peladora")
    eq(25, 3.2, 1.6, 1.4, "pulpa", "trit.")
    tank(28.2, 4.0, 1.0, "pulpa", "macerador")
    eq(29.6, 3.2, 4.0, 1.6, "pulpa", f"prensa {s['Prensa']}")
    eq(21.6, 9.0, 3.2, 1.6, "cascara", f"prensa cáscara")
    eq(29.6, 7.0, 2.2, 1.6, "agua", "centrífuga")
    eq(29.6, 9.6, 3.2, 1.6, "agua", f"MF lías {s['MF lías']}")
    eq(32.3, 7.0, 1.2, 1.2, "agua", "SO₂", 13)
    eq(13, 9.5, 3, 3, "agua", "cuarto frío")
    zone(34, 0, 20, 14, "pulpa", "Bodega de vino", "piso con pendiente y canaletas")
    tank(36.4, 4.6, 10, "agua", "pulmón 10 m³")
    D = tank(40.4, 4.6, 10, "pulpa", "F-101"); tank(43.6, 4.6, 10, "pulpa", "F-102")
    gV = max(f["w_sold"] / 0.99, 1) * 90 / 365 * 1.1
    ng, sg, _ = pt.pick("tanque_guarda", gV)
    for k in range(ng):
        tank(37.5 + k * 5.6, 10.6, sg, "pulpa", f"guarda {sg} m³" if k == 0 else None)
    zone(54, 0, 16, 14, "vinagre", "Vinagre", "acetificación y tanques")
    tank(56.4, 4.4, 10, "vinagre", "F-201"); tank(59.4, 4.4, 10, "vinagre", "F-202")
    tank(63.4, 4.4, float(s["Acetificador"].split()[0]), "vinagre", f"acetificador {s['Acetificador']}")
    eq(66.0, 2.6, 1.4, 1.4, "vinagre", "espuma", 12); eq(66.0, 4.6, 2.6, 1.2, "vinagre", "MF vinagre", 12)
    vV = f["vin"] / 1.01 * 30 / 365 * 1.1
    nv, sv, _ = pt.pick("tanque_guarda", vV)
    for k in range(nv):
        tank(57.0 + k * 5.6, 10.6, sv, "vinagre", f"vinagre {sv} m³" if k == 0 else None)
    # ---------------- zonas centrales
    boiler = s.get("Caldera de corona", "no")
    zone(0, 18, 12, 12, "corona", "Biomasa y caldera", "corona picada y secada")
    for k in range(2):
        sd.rellipse(X(2.2 + k * 2.6), Y(22.5), 1.1 * S, 1.6 * S, PAL["corona"][1], 1.6, n=16)
    sd.text(X(3.5), Y(25.2), "pilas de corona", 15, "#5e5a53", anchor="middle")
    eq(1.2, 26.3, 4.0, 2.0, "corona", "picadora")
    eq(7.4, 21.0, 3.6, 2.8, "corona", f"caldera {boiler}" if boiler != "no" else "caldera", 13)
    sd.rellipse(X(10.2), Y(25.4), 0.5 * S, 0.5 * S, INK, 1.8, n=12); sd.text(X(10.2), Y(26.6), "chimenea", 14, "#5e5a53", anchor="middle")
    zone(12, 18, 22, 12, "cascara", "Secado y harina", "polvo controlado")
    eq(13.2, 21.2, 13.0, 2.6, "cascara", f"secador de banda {s['Secador']}")
    eq(27.2, 21.4, 2.2, 1.8, "cascara", "molino", 13); eq(30.2, 21.4, 2.4, 2.0, "cascara", "empaque", 13)
    for i in range(2):
        for k in range(6):
            sd.rrect(X(14 + k * 2.4), Y(25.2 + i * 2.2), 1.6 * S, 1.6 * S, PAL["cascara"][1], 1.3, passes=1)
    sd.text(X(28.5), Y(27.2), "bodega de harina (estibas)", 15, "#5e5a53", anchor="middle")
    zone(34, 18, 12, 12, "elec", "Servicios", "energía, frío y agua")
    eq(35, 20.8, 4.4, 2.2, "elec", "grupo electrógeno", 13)
    eq(40.4, 20.8, 2.2, 1.6, "agua", "chiller", 12); eq(43.0, 20.8, 2.2, 1.6, "agua", "chiller", 12)
    eq(40.4, 23.0, 1.6, 1.2, "neutro", "N₂", 12)
    tank(37.0, 26.4, 30, "agua", "agua")
    eq(41.0, 26.2, 4.2, 1.6, "glp", "GLP", 13)
    zone(46, 18, 24, 12, "neutro", "Producto terminado y despacho", "vino y vinagre a granel, harina en sacos")
    for k in range(4):
        eq(48 + k * 3.0, 22.0, 2.0, 2.0, "pulpa" if k < 2 else "vinagre", "IBC", 12)
    for k in range(5):
        sd.rrect(X(61 + (k % 3) * 2.4), Y(21.6 + (k // 3) * 2.4), 1.6 * S, 1.6 * S, PAL["cascara"][1], 1.3, passes=1)
    for k in range(3):
        sd.rline(X(49 + k * 7), Y(30), X(53 + k * 7), Y(30), "#fdfcfa", 7, 1, over=0)
        sd.text(X(51 + k * 7), Y(29.3), "muelle", 14, "#7a746b", anchor="middle")
    # ---------------- zonas sur
    zone(0, 34, 14, 11, "compost", "Compostaje", "a sotavento · bagazo, corazón, lías")
    for k in range(3):
        sd.rrect(X(1.5), Y(38.4 + k * 2.0), 11 * S, 1.2 * S, PAL["compost"][1], 1.5, passes=1)
        sd.hachure(X(1.5), Y(38.4 + k * 2.0), 11 * S, 1.2 * S, PAL["compost"][1], gap=5, sw=1.1, op=0.6, fill=PAL["compost"][0], fill_op=0.9, angle=40)
    zone(14, 34, 22, 11, "neutro", "Oficinas, laboratorio y vestidores")
    for k, t in enumerate(("oficinas", "laboratorio", "vestidores y baños", "comedor")):
        sd.rrect(X(15 + k * 5.2), Y(37.5), 4.8 * S, 6 * S, "#7a746b", 1.5, passes=1)
        sd.text(X(17.4 + k * 5.2), Y(40.8), t, 15, "#5e5a53", anchor="middle")
    zone(36, 34, 16, 11, "neutro", "Báscula y parqueadero")
    eq(37.5, 37.4, 13, 3.0, "neutro", "báscula camionera 60 t")
    for k in range(6):
        sd.rrect(X(37.5 + k * 2.1), Y(41.3), 1.8 * S, 3.0 * S, "#9a948a", 1.2, passes=1)
    zone(52, 34, 18, 11, "agua", "PTAR", "homogenización y lodos activados")
    tank(56, 40, 60, "agua", "homogenización"); tank(62.5, 40, 90, "agua", "aireación"); tank(67.6, 40.2, 15, "agua", "lodos")
    # ---------------- recorridos
    flow([(-3, 16), (4, 16), (4, 14.2)], "cascara", "fruta", at=0.35)
    flow([(11.6, 4), (13, 4)], "cascara")
    flow([(33.8, 4), (35, 4)], "pulpa", None)
    flow([(45.5, 6.5), (47.5, 6.5), (47.5, 8.6)], "pulpa", None)
    flow([(50.5, 7.8), (55.0, 7.8)], "vinagre", "vino a vinagre", at=0.5)
    flow([(23.3, 10.7), (23.3, 17.7), (23.3, 20.9)], "cascara", "torta", at=0.62)
    flow([(19, 12.6), (19, 16.0), (6, 16.0), (6, 18.2)], "corona", "corona", at=0.55)
    flow([(25.5, 10.8), (25.5, 16.3), (57.2, 16.3), (57.2, 8.3)], "vinagre", "jugo de cáscara", at=0.72)
    flow([(11.0, 22.4), (13.1, 22.4)], "#b0694f", "aire caliente", at=0.5, dash="9 6", lab_dy=-14)
    flow([(44.5, 13.2), (44.5, 17.0), (50.0, 17.0), (50.0, 21.8)], "pulpa", "vino", at=0.35)
    flow([(64.0, 13.2), (64.0, 17.4), (56.0, 17.4), (56.0, 21.8)], "vinagre", "vinagre", at=0.3)
    flow([(32.5, 24.6), (34.0, 24.6), (34.0, 32.2), (60.5, 32.2), (60.5, 29.6)], "cascara", "harina", at=0.18, lab_dy=-12)
    flow([(55.0, 30.2), (55.0, 32.0), (71.5, 32.0)], INK, "despacho", at=0.75)
    flow([(17.0, 13.0), (17.0, 14.6), (0.6, 14.6), (0.6, 33.0), (6.0, 33.0), (6.0, 35.6)], "compost", "residuos", at=0.79, dash="10 7", sw=2.6)
    flow([(30.0, 13.4), (30.0, 15.0), (68.6, 15.0), (68.6, 33.4), (66.0, 33.4), (66.0, 35.6)], "agua", "aguas residuales", at=0.55, dash="10 7", sw=2.4)
    # cotas
    dim_line(0, 0, 70, 0, "70 m", off=36)
    dim_line(0, 0, 0, 45, "45 m", off=40, vertical=True)
    return s


def panel():
    px, py = 2200, 190
    # norte y escala
    cx, cy = px + 70, py + 70
    sd.rellipse(cx, cy, 46, 46, INK, 2.0, n=20)
    sd.add(f'<path d="M{cx},{cy - 40} L{cx + 12},{cy + 10} L{cx},{cy} L{cx - 12},{cy + 10} Z" fill="{PAL["neutro"][0]}" stroke="{INK}" stroke-width="2"/>')
    sd.text(cx, cy - 54, "N", 26, INK, anchor="middle", font="Caveat", weight=700)
    bx, by = px + 170, py + 80
    for k in range(4):
        x0 = bx + k * 5 * S
        if k % 2 == 0:
            sd.hachure(x0, by, 5 * S, 14, INK, gap=4, sw=1.0, op=0.6, fill="#d9d4cc", fill_op=0.9)
        sd.rrect(x0, by, 5 * S, 14, INK, 1.4, passes=1)
        sd.text(x0, by + 38, str(k * 5), 16, INK, anchor="middle")
    sd.text(bx + 20 * S, by + 38, "20 m", 16, INK, anchor="middle")
    # cuadro de zonas
    ty = py + 170
    sd.text(px, ty, "Zonas", 32, INK, font="Caveat", weight=700)
    tot = 0.0
    for i, (name, a, key) in enumerate(ZONES):
        y = ty + 22 + i * 40
        fill, stroke = PAL[key]
        sd.hachure(px, y, 30, 26, stroke, gap=5, sw=1.2, op=0.6, fill=fill, fill_op=0.9)
        sd.rrect(px, y, 30, 26, stroke, 1.6, passes=1)
        sd.text(px + 44, y + 20, name, 20, INK)
        sd.text(px + 800, y + 20, f"{fmt(a)} m²", 20, INK, anchor="end")
        tot += a
    y = ty + 22 + len(ZONES) * 40
    sd.rline(px, y, px + 800, y, "#9a948a", 1.2, 1)
    sd.text(px + 44, y + 28, "Zonas (sin vías)", 20, INK, font="Kalam", weight=700)
    sd.text(px + 800, y + 28, f"{fmt(tot)} m²", 20, INK, anchor="end", weight=700)
    sd.text(px + 44, y + 58, "Lote", 20, INK, font="Kalam", weight=700)
    sd.text(px + 800, y + 58, f"{fmt(70 * 45)} m² (70 × 45 m)", 20, INK, anchor="end", weight=700)
    # notas
    ny = y + 110
    sd.text(px, ny, "Criterios de distribución", 30, INK, font="Caveat", weight=700)
    notes = ["El material avanza de oeste a este sin cruces: recepción → proceso",
             "húmedo → bodega → vinagre; los secos van por el sur.",
             "La caldera queda junto al secador, que usa el 95 % del calor.",
             "Bodega y acetificador junto a servicios: frío y grupo electrógeno",
             "(la aireación no puede parar).",
             "GLP y caldera separados de la nave; compostaje y PTAR al sur,",
             "a sotavento (verificar el viento dominante del sitio).",
             "Huellas de equipos aproximadas [S]; tanques con H = 1,5·D."]
    for i, t in enumerate(notes):
        sd.text(px, ny + 34 + i * 27, t, 18, "#5e5a53")


if __name__ == "__main__":
    build(); panel()
    svg = sd.svg_doc()
    p_svg = os.path.join(FIGS, "fig37_layout.svg")
    open(p_svg, "w", encoding="utf-8").write(svg)
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {sd.W}, height: {sd.H} }}, deviceScaleFactor: 1.25 }});
  await p.goto('file://{p_svg}');
  await p.waitForTimeout(800);
  await p.screenshot({{ path: '{os.path.join(FIGS, "fig37_layout.png")}' }});
  await b.close();
}})();"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
    subprocess.run(["node", fh.name], check=True)
    os.unlink(fh.name)
    print("fig fig37_layout.svg/.png", [(z[0], round(z[1])) for z in ZONES])
