"""
Diagrama de Gantt del diseño óptimo dibujado a mano, con el estilo de las figs. 33–37.

Panel A (año): curva de cosecha (oferta de fruta por mes) y ocupación mensual de cada equipo del diseño óptimo
(results/dimensionamiento.json, E1|Óptimo económico): el sombreado se intensifica con la ocupación y los equipos que
topan (≥ 95 %) se marcan con un óvalo.
Panel B (semana del mes pico, abril): turnos de 6 h efectivos de lunes a sábado para las unidades con personal
(la fracción usada de cada turno = ocupación del mes); bodega de vino y de jugo de cáscara con fermentadores desfasados
(Moresi 1989b: llenado V_F/Q, fermentación, descarga y limpieza); acetificador semicontinuo (Frings: descarga del 50 %,
carga y acetificación); secador y caldera de corona continuos con una parada semanal (disponibilidad 0,9).
Salidas: figs/fig38_gantt.svg (autocontenido) y figs/fig38_gantt.png.
"""
import json, math, os, subprocess, tempfile
import superestructura_dibujo as sd
import balance_dibujo as bd  # noqa: F401  (añade colores vapor/aire/compost a la paleta)
import dimensionamiento as dm

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
sd.W, sd.H = 2980, 2140
PAL = sd.PAL
PAL.setdefault("elec", ("#efe2ae", "#a68a33"))
INK = sd.INK
GREY = "#5e5a53"
MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
fmt = lambda v, n=0: f"{v:,.{n}f}".replace(",", " ").replace(".", ",") if n else f"{v:,.0f}".replace(",", " ")

LX, LW = 470, 2140                     # inicio y ancho del eje de tiempo


def lane_label(y, h, name, size_txt, key):
    fill, stroke = PAL[key]
    sd.hachure(70, y + h / 2 - 13, 26, 26, stroke, gap=5, sw=1.2, op=0.6, fill=fill, fill_op=0.9)
    sd.rrect(70, y + h / 2 - 13, 26, 26, stroke, 1.6, passes=1)
    sd.text(110, y + h / 2 + 2, name, 23, INK, font="Kalam", weight=700)
    if size_txt:
        sd.text(110, y + h / 2 + 26, size_txt, 17, GREY)


def block(x, y, w, h, key, intensity=1.0, txt=None, dash=None, size=17, txt_color=INK):
    fill, stroke = PAL[key]
    if w < 2:
        return
    if intensity > 0:
        sd.hachure(x, y, w, h, stroke, gap=max(4.0, 12 - 8 * intensity), sw=1.2, op=0.25 + 0.55 * intensity,
                   fill=fill, fill_op=0.25 + 0.7 * intensity)
    sd.rrect(x, y, w, h, stroke, 1.7, dash=dash, passes=1 if w < 40 else 2)
    if txt and w > 8 * len(txt) * size / 17:
        sd.text(x + w / 2, y + h / 2 + size * 0.35, txt, size, txt_color, anchor="middle")


def panel_year(d, y0):
    r = d["E1|Óptimo económico"]; s = r["scen"][0]; sz = r["sizes"]; U = s["util"]; rows = s["periods"]
    cap = r["caps"]
    U = dict(U)
    U["Bodega cáscara"] = [sum((x["pj"] + x.get("hjv", 0.0) * dm.T_LEAF / dm.T_PEEL) / 1.05 for x in rows if x["month"] == m)
                          / (cap["Bodega cáscara"] * dm.AC * dm.HM[m]) for m in range(12)]   # v10: + jugo de hojas
    sd.text(60, y0, "A · El año de operación", 40, INK, font="Caveat", weight=700)
    sd.text(400, y0, "ocupación mensual de cada equipo del diseño óptimo (Chocó 2022, 6 146 t/año); más trazo = más ocupado", 21, GREY)
    mw = LW / 12
    # curva de cosecha
    cy0, ch = y0 + 40, 170
    sup = s["supply_month"]; loss = s["loss_month"]; mx = max(sup)
    sd.text(110, cy0 + 70, "Oferta de fruta", 23, INK, font="Kalam", weight=700)
    sd.text(110, cy0 + 96, "t/mes (cosecha)", 17, GREY)
    sd.add(f'<g opacity="0.9">')
    pts = [(LX + (m + 0.5) * mw, cy0 + ch - 20 - (ch - 40) * v / mx) for m, v in enumerate(sup)]
    area = f"M{LX},{cy0 + ch} L{LX},{pts[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts) + f" L{LX + LW},{pts[-1][1]:.1f} L{LX + LW},{cy0 + ch} Z"
    sd.hachure(LX, cy0, LW, ch, PAL["pulpa"][1], gap=9, sw=1.1, op=0.35, fill=PAL["pulpa"][0], fill_op=0.55, angle=-35,
               shape=f'<path d="{area}"/>')
    sd.add('</g>')
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        sd.rline(x1, y1, x2, y2, PAL["pulpa"][1], 3.0, 2)
    for m, (x, y) in enumerate(pts):
        sd.rellipse(x, y, 5, 5, PAL["pulpa"][1], 2.0, n=10)
        sd.text(x, y - 14, fmt(sup[m]), 17, INK, anchor="middle")
        if loss[m] > 0.5:
            sd.text(x, cy0 + ch - 8, f"pierde {fmt(loss[m])} t", 15, "#a4513f", anchor="middle")
    sd.rline(LX, cy0 + ch, LX + LW, cy0 + ch, "#9a948a", 1.4, 1)
    # carriles
    lanes = [("Frente de lavado", sz["Frente"], "neutro", U["Frente"], "turnos"),
             ("Prensa de pulpa", sz["Prensa"], "pulpa", U["Prensa"], "turnos"),
             ("Prensa de cáscara", sz["Prensa cáscara"], "cascara", U["Prensa cáscara"], "turnos"),
             ("Extractora de hojas", sz.get("Extractora hojas", "no"), "corazon", U.get("Extractora hojas", [0] * 12), "turnos"),
             ("Clarificación", sz["Clarificación"], "agua", U["Clarificación"], "turnos"),
             ("MF de lías", sz["MF lías"], "agua", U["MF lías"], "turnos"),
             ("Bodega de vino", sz["Bodega"], "pulpa", U["Bodega"], "24 h"),
             ("Bodega de cáscara", sz["Bodega cáscara"], "cascara", U["Bodega cáscara"], "24 h"),
             ("Acetificador", sz["Acetificador"], "vinagre", U["Acetificador"], "24 h"),
             ("Secador de banda", sz["Secador"], "cascara", U["Secador"], "24 h"),
             ("Caldera de corona", sz["Caldera de corona"], "corona", U["Caldera de corona"], "24 h")]
    lanes = [l for l in lanes if l[1] != "no"]
    ly, lh, gap = cy0 + ch + 30, 62, 12
    for i, (name, size_txt, key, u, regime) in enumerate(lanes):
        y = ly + i * (lh + gap)
        lane_label(y, lh, name, f"{size_txt} · {regime}", key)
        for m in range(12):
            x = LX + m * mw + 4
            block(x, y + 6, mw - 8, lh - 12, key, min(u[m], 1.0), f"{u[m] * 100:.0f} %", size=18)
            if u[m] >= 0.95:
                sd.rellipse(x + (mw - 8) / 2, y + lh / 2, (mw - 8) / 2 + 1, lh / 2 + 1, "#b0563f", 2.2, n=22)
    yb = ly + len(lanes) * (lh + gap)
    for m in range(13):
        x = LX + m * mw
        sd.rline(x, cy0 + 10, x, yb - gap + 4, "#b9b3a8", 1.0, 1, dash="5 7")
    for m in range(12):
        sd.text(LX + (m + 0.5) * mw, yb + 22, MES[m], 22, INK, anchor="middle", font="Caveat", weight=700)
    # notas al margen derecho
    nx = LX + LW + 40
    sd.text(nx, ly + 14, "Lectura", 30, INK, font="Caveat", weight=700)
    rng = lambda u: f"{min(u) * 100:.0f}–{max(u) * 100:.0f} %"
    def top(u):
        ms = [MES[m] for m in range(12) if u[m] >= 0.95]
        return ", ".join(ms) if 0 < len(ms) <= 4 else (f"{len(ms)} de 12 meses" if ms else "ningún mes")
    notes = [("#b0563f", "óvalo: el equipo topa (≥ 95 %)"),
             (INK, f"Prensa de pulpa: tope en {top(U['Prensa'])};"),
             (INK, f"deja {fmt(sum(loss))} t/año de fruta sin procesar."),
             (INK, f"Extractora de hojas {sz.get('Extractora hojas', '—')}: {rng(U.get('Extractora hojas', [0]))}."),
             (INK, f"MF de lías {rng(U['MF lías'])}; el acetificador"),
             (INK, f"topa en {top(U['Acetificador'])}:"),
             (INK, "el modelo los dimensiona justos."),
             (INK, f"Bodega de vino {rng(U['Bodega'])}: {sz['Bodega']} es"),
             (INK, "el mínimo de Moresi (N_F ≥ 2)."),
             (INK, f"Bodega de cáscara {rng(U['Bodega cáscara'])} con el"),
             (INK, f"jugo de hojas ({fmt(dm.T_LEAF, 1)} h por lote)."),
             (INK, f"Caldera {rng(U['Caldera de corona'])}; sigue la cosecha.")]
    for i, (c, t) in enumerate(notes):
        sd.text(nx, ly + 52 + i * 29 + (12 if i >= 1 else 0) + (12 if i >= 4 else 0) + (12 if i >= 7 else 0) + (12 if i >= 9 else 0), t, 19, c)
    return yb + 40, s, r


def cycles(lag, phases, n_tanks, H, t_off=0.0):
    """Lotes desfasados: el lote k empieza en k·lag en el tanque k mod n. Devuelve (tanque, inicio, dur, fase)."""
    out = []
    dtc = sum(d_ for _, d_ in phases)
    k0 = -int(math.ceil((dtc + abs(t_off)) / lag)) - 1
    k = k0
    while k * lag + t_off < H:
        t = k * lag + t_off
        for ph, du in phases:
            a, b = max(t, 0.0), min(t + du, H)
            if b > a:
                out.append((k % n_tanks, a, b - a, ph))
            t += du
        k += 1
    return out


def panel_week(y0, s, r):
    rows = [x for x in s["periods"] if x["month"] == 3]
    hours = sum(x["dur"] for x in rows)
    U = s["util"]; sz = r["sizes"]
    sd.text(60, y0 + 30, "B · Una semana del mes pico (abril)", 40, INK, font="Caveat", weight=700)
    sd.text(640, y0 + 30, "dos turnos de 6 h efectivas de lunes a sábado; bodega, acetificador, secador y caldera corren las 24 h", 21, GREY)
    H = 168.0
    X = lambda h: LX + h / H * LW
    top = y0 + 70
    # bandas de noche y domingo
    # ejes de días
    leaves = sz.get("Extractora hojas", "no") != "no"
    bc = sz.get("Bodega cáscara", "2×10 m³")
    nbc = int(bc.split("×")[0]) if "×" in bc else 2
    o = 1 if leaves else 0
    lanes_n = 10 + o + nbc
    lh, gap = 56, 10
    yb = top + 50 + lanes_n * (lh + gap)
    for dday in range(7):
        x0 = X(dday * 24)
        # noche 21:00–06:00 sombreada en gris claro
        for a, b in ((dday * 24, dday * 24 + 6), (dday * 24 + 21, dday * 24 + 24)):
            sd.add(f'<rect x="{X(a):.1f}" y="{top + 40}" width="{X(b) - X(a):.1f}" height="{yb - top - 40 - gap:.1f}" fill="#ebe7e0" opacity="0.55"/>')
        if dday == 6:
            sd.add(f'<rect x="{X(144):.1f}" y="{top + 40}" width="{X(168) - X(144):.1f}" height="{yb - top - 40 - gap:.1f}" fill="#e3ded5" opacity="0.6"/>')
        sd.rline(x0, top + 30, x0, yb - gap + 4, "#9a948a", 1.2, 1)
        sd.text(X(dday * 24 + 12), top + 24, DIAS[dday], 24, INK, anchor="middle", font="Caveat", weight=700)
    sd.rline(X(168), top + 30, X(168), yb - gap + 4, "#9a948a", 1.2, 1)
    ly = top + 50
    lane_y = lambda i: ly + i * (lh + gap)
    SHIFTS = [(6, 12), (13, 19)]

    def staffed(i, name, key, util, size_txt):
        y = lane_y(i)
        lane_label(y, lh, name, size_txt, key)
        for dday in range(6):
            for a, b in SHIFTS:
                t0 = dday * 24 + a; L = (b - a)
                used = L * min(util, 1.0)
                block(X(t0), y + 8, X(t0 + used) - X(t0), lh - 16, key, 0.9)
                if used < L - 0.05:
                    block(X(t0 + used), y + 8, X(t0 + L) - X(t0 + used), lh - 16, key, 0.0, dash="6 5")
        sd.text(X(144) + 12, y + lh / 2 + 7, f"{util * 100:.0f} % del turno", 18, GREY)

    staffed(0, "Frente de lavado", "neutro", U["Frente"][3], sz["Frente"])
    staffed(1, "Prensa de pulpa", "pulpa", U["Prensa"][3], sz["Prensa"])
    staffed(2, "Prensa de cáscara", "cascara", U["Prensa cáscara"][3], sz["Prensa cáscara"])
    if leaves:
        staffed(3, "Extractora de hojas", "corazon", U["Extractora hojas"][3], sz["Extractora hojas"])
    staffed(3 + o, "Clarificación", "agua", U["Clarificación"][3], sz["Clarificación"])
    staffed(4 + o, "MF de lías", "agua", U["MF lías"][3], sz["MF lías"])
    # bodega de vino (Moresi): Q medio desde el pulmón de mosto
    Qw = sum(x["bod"] for x in rows) / hours
    fill_w = dm.VF / Qw
    PH_W = [("llenado", fill_w), ("fermentación", 12.5), ("descarga", 2.5)]
    colors = {"llenado": ("pulpa", 0.35), "fermentación": ("pulpa", 1.0), "descarga": ("neutro", 0.7),
              "llenado c": ("cascara", 0.35), "fermentación c": ("cascara", 1.0),
              "acetificación": ("vinagre", 1.0), "carga": ("vinagre", 0.35), "descarga 50 %": ("neutro", 0.7)}
    sub = {"llenado": "llenado", "fermentación": "ferm. 12,5 h", "descarga": "", "llenado c": "llenado", "fermentación c": f"fermentación {fmt(dm.T_PEEL, 1)} h"}
    for j in range(2):
        y = lane_y(5 + o + j)
        lane_label(y, lh, f"Bodega vino F-10{j + 1}", "10 m³" + (f" · Q = {fmt(Qw, 2)} m³/h" if j == 0 else ""), "pulpa")
    for tk, a, du, ph in cycles(fill_w, PH_W, 2, H, t_off=-8.0):
        key, it = colors[ph]
        block(X(a), lane_y(5 + o + tk) + 8, X(a + du) - X(a), lh - 16, key, it, sub.get(ph, ""))
    Qp = sum(x["pj"] + x.get("hjv", 0.0) for x in rows) / 1.05 / hours          # v10: jugo de cáscara + jugo de hojas
    fill_p = dm.VF / Qp
    PH_P = [("llenado c", fill_p), ("fermentación c", dm.T_PEEL), ("descarga", 2.5)]
    for j in range(nbc):
        lane_label(lane_y(7 + o + j), lh, f"Jugos F-20{j + 1}", "10 m³" + (f" · Q = {fmt(Qp, 2)} m³/h" if j == 0 else ""), "cascara")
    for tk, a, du, ph in cycles(fill_p, PH_P, nbc, H, t_off=-20.0):
        key, it = colors[ph]
        block(X(a), lane_y(7 + o + tk) + 8, X(a + du) - X(a), lh - 16, key, it, sub.get(ph, "") if du > 20 else "")
    # acetificador semicontinuo
    feed = (sum(x["wv"] for x in rows) + sum(x["pj"] + x.get("hjv", 0.0) for x in rows) / 1.05) / hours
    acid_h = sum(x["acid"] for x in rows) / hours
    V_a = float(sz["Acetificador"].split()[0])
    cyc = 0.5 * V_a / feed
    PH_A = [("descarga 50 %", 0.8), ("carga", 1.5), ("acetificación", cyc - 2.3)]
    y = lane_y(7 + o + nbc)
    lane_label(y, lh, "Acetificador", f"{sz['Acetificador']} · ciclo {fmt(cyc, 1)} h", "vinagre")
    for tk, a, du, ph in cycles(cyc, PH_A, 1, H, t_off=-3.0):
        key, it = colors[ph]
        block(X(a), y + 8, X(a + du) - X(a), lh - 16, key, it, "acetificación" if ph == "acetificación" and du > 12 else "", size=15)
    sd.rline(X(0), y + lh - 4, X(168), y + lh - 4, PAL["vinagre"][1], 1.6, 1, dash="3 5")
    # secador y caldera: continuos con parada semanal (disponibilidad 0,9 → 16,8 h)
    stop = (1 - dm.AC) * 168
    for i, (name, key, u, size_txt) in enumerate((("Secador de banda", "cascara", U["Secador"][3], sz["Secador"]),
                                                  ("Caldera de corona", "corona", U["Caldera de corona"][3], sz["Caldera de corona"]))):
        y = lane_y(8 + o + nbc + i)
        lane_label(y, lh, name, size_txt, key)
        a0 = 6.0 if i == 1 else 7.0
        block(X(a0), y + 8, X(168 - stop + a0 - 6.0) - X(a0), lh - 16, key, u, f"continuo · carga {u * 100:.0f} %")
        block(X(168 - stop + a0 - 6.0), y + 8, X(168) - X(168 - stop + a0 - 6.0), lh - 16, "neutro", 0.0, "mantenimiento", dash="6 5", size=15)
        if a0 > 0:
            block(X(0), y + 8, X(a0) - X(0), lh - 16, "neutro", 0.0, "", dash="6 5")
    # horas
    for h in range(0, 169, 6):
        if h % 24:
            sd.text(X(h), yb + 4, f"{h % 24:02d}", 14, GREY, anchor="middle")
    sd.text(X(168) + 12, yb + 4, "hora", 15, GREY)
    # leyenda
    ly2 = yb + 52
    items = [("pulpa", 0.9, None, "turno operado"), ("pulpa", 0.0, "6 5", "holgura del turno"),
             ("pulpa", 0.35, None, "llenado (V_F/Q)"), ("pulpa", 1.0, None, "fermentación"),
             ("neutro", 0.7, None, "descarga y limpieza"), ("vinagre", 1.0, None, "acetificación"),
             ("vinagre", 0.35, None, "carga de vino o jugo")]
    x = LX
    for key, it, dash, lab in items:
        block(x, ly2, 54, 26, key, it, dash=dash)
        sd.text(x + 66, ly2 + 20, lab, 19, INK)
        x += 92 + 10.5 * len(lab)
    sd.add(f'<rect x="{x:.0f}" y="{ly2}" width="54" height="26" fill="#ebe7e0" opacity="0.8"/>')
    sd.text(x + 66, ly2 + 20, "noche (21–06 h)", 19, INK)
    # notas
    nx = LX + LW + 40
    sd.text(nx, ly + 14, "Lectura", 30, INK, font="Caveat", weight=700)
    notes = [f"A {fmt(Qw, 2)} m³/h el llenado de un",
             f"fermentador tarda {fmt(fill_w, 0)} h y domina",
             "el ciclo; el segundo tanque",
             "fermenta mientras el primero se llena.",
             "",
             f"Jugos de cáscara y hojas: llenado",
             f"de {fmt(fill_p, 0)} h y {fmt(dm.T_PEEL, 1)} h de fermentación.",
             "",
             f"Acetificador: ≈ {fmt(acid_h * 24, 0)} kg de ácido/d;",
             f"descarga la mitad cada {fmt(cyc, 0)} h y la",
             "aireación no para (línea punteada:",
             "grupo electrógeno de respaldo).",
             "",
             "Domingo: limpieza CIP y",
             "mantenimiento del secador."]
    for i, t in enumerate(notes):
        if t:
            sd.text(nx, ly + 52 + i * 27, t, 19, INK)
    return ly2 + 60


def build():
    d = json.load(open(os.path.join(HERE, "results", "dimensionamiento.json")))
    sd.text(60, 72, "Diagrama de Gantt del diseño óptimo", 58, INK, font="Caveat", weight=700)
    sd.text(62, 112, "Versión 11 · arriba, el año completo (rejilla continua de 24 periodos agregada por mes); abajo, una semana típica de abril con lotes "
                     "desfasados (Moresi 1989b).", 21, GREY)
    y, s, r = panel_year(d, 190)
    sd.rline(60, y + 6, sd.W - 60, y + 6, "#c9c3b8", 1.4, 1, dash="10 10")
    end = panel_week(y + 40, s, r)
    return end


if __name__ == "__main__":
    end = build()
    sd.H = int(end + 30)
    svg = sd.svg_doc()
    p_svg = os.path.join(FIGS, "fig38_gantt.svg")
    open(p_svg, "w", encoding="utf-8").write(svg)
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {sd.W}, height: {sd.H} }}, deviceScaleFactor: 1.25 }});
  await p.goto('file://{p_svg}');
  await p.waitForTimeout(800);
  await p.screenshot({{ path: '{os.path.join(FIGS, "fig38_gantt.png")}' }});
  await b.close();
}})();"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
    subprocess.run(["node", fh.name], check=True)
    os.unlink(fh.name)
    print("fig fig38_gantt.svg/.png", sd.W, sd.H)
