"""
Balance de masa de la biorrefinería de piña dibujado a mano (diagrama de Sankey con el estilo de la fig. 33).

El ancho de cada corriente es proporcional a su masa (t/año). Los flujos salen del diseño óptimo de la versión 7
(results/dimensionamiento.json, E1|Óptimo económico); los volúmenes se pasan a masa con las densidades del modelo
(jugo y mosto 1,06 t/m³, vino 0,99, vinagre 1,01). El agua de dilución del vinagre se obtiene por cierre del balance.
Salidas: figs/fig34_balance_masa.svg (autocontenido) y figs/fig34_balance_masa.png.
"""
import json, math, os, subprocess, tempfile
import superestructura_dibujo as sd
import capacidad as cp
import dimensionamiento as dm

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
sd.W, sd.H = 2840, 1720
K = 0.042                                  # px por t/año
RHO_J, RHO_W, RHO_V = cp.RHO_JUICE, 0.99, 1.01
PAL = sd.PAL
PAL.update(dict(vapor=("#d6e1e8", "#7f97a8"), aire=("#e3e8ee", "#8a9aab"), compost=("#d9cbb6", "#8a6f52")))
fmt = lambda v: f"{v:,.0f}".replace(",", " ")


def flows_v7():
    d = json.load(open(os.path.join(HERE, "results", "dimensionamiento.json")))
    r = d["E1|Óptimo económico"]; s = r["scen"][0]; p = s["products"]
    F = p["fruta_t"]
    fr = dict(pulpa=0.45 * F, cascara=0.30 * F, corazon=0.10 * F, corona=0.15 * F)
    juice = p["mosto_m3"] * RHO_J                      # jugo de pulpa a clarificación
    bagazo = fr["pulpa"] - juice
    lodos = juice * dm.CENT_LOSS
    clar = juice - lodos
    mfl = p["lias_MF_m3"] * RHO_J
    rec = mfl * dm.LEES_REC
    ret = mfl - rec
    l_sec = p["lias_secador_t"]
    l_comp = lodos - mfl - l_sec
    must = clar + rec
    wine = p["vino_m3"] * RHO_W
    co2_l = must - wine
    w_vin = p["vino_a_vinagre_m3"] * RHO_W
    w_sold = wine - w_vin
    pj = p["jugo_cascara_vinagre_t"]
    sold_pj = fr["cascara"] * cp.Y["peel_juice_frac"] - pj
    torta = fr["cascara"] * (1 - cp.Y["peel_juice_frac"])
    co2_pj = pj * 0.46 * 0.95 * 104 / 1000 * 44 / 46        # CO2 de la fermentación del jugo de cáscara
    pwine = pj - co2_pj
    acid = p["acido_kg"] / 1000
    o2 = acid * 32 / 60
    vin = p["vinagre_m3"] * RHO_V
    water = vin - (w_vin + pwine + o2)
    flour = p["harina_t"] + p.get("harina_lias_t", 0)
    vapor = torta + l_sec - flour
    return dict(F=F, loss=s["loss"], fr=fr, juice=juice, bagazo=bagazo, lodos=lodos, clar=clar, rec=rec, ret=ret, l_sec=l_sec,
                l_comp=l_comp, must=must, wine=wine, co2_l=co2_l, w_vin=w_vin, w_sold=w_sold, pj=pj, sold_pj=sold_pj, torta=torta,
                co2_pj=co2_pj, pwine=pwine, o2=o2, water=water, vin=vin, flour=flour, vapor=vapor, sizes=r["sizes"])


# ----------------------------------------------------------------------------- motor de Sankey a mano alzada
class Sankey:
    def __init__(self):
        self.nodes, self.flows = {}, []

    def node(self, key, x, y, label, color="neutro", sub=None, side="right", bar=True):
        self.nodes[key] = dict(x=x, y=y, label=label, color=color, sub=sub, side=side, bar=bar, out=0.0, inn=0.0, tot_out=0.0, tot_in=0.0)

    def flow(self, a, b, v, color, label=None, lab_pos=0.5, lab_dy=0):
        self.flows.append(dict(a=a, b=b, v=v, color=color, label=label, lab_pos=lab_pos, lab_dy=lab_dy))
        self.nodes[a]["tot_out"] += v; self.nodes[b]["tot_in"] += v

    def draw(self):
        for f in self.flows:
            A, B = self.nodes[f["a"]], self.nodes[f["b"]]
            w = max(f["v"] * K, 2.5)
            y1 = A["y"] + A["out"] * K; A["out"] += f["v"]
            y2 = B["y"] + B["inn"] * K; B["inn"] += f["v"]
            x1, x2 = A["x"] + 14, B["x"]
            band(x1, y1, x2, y2, w, f["color"])
            if f["label"]:
                t = f["lab_pos"]
                lx = x1 + (x2 - x1) * t
                ly = y1 + (y2 - y1) * (3 * t * t - 2 * t ** 3) + w / 2 + 7 + f["lab_dy"]
                sd.text(lx, ly, f["label"], 19 if w > 14 else 17, PAL[f["color"]][1] if w <= 14 else sd.INK, anchor="middle")
        for k, n in self.nodes.items():
            h = max(n["tot_out"], n["tot_in"]) * K
            fill, stroke = PAL[n["color"]]
            if n["bar"]:
                sd.hachure(n["x"], n["y"], 14, max(h, 4), stroke, gap=5, sw=1.4, op=0.8, fill=fill, fill_op=0.95)
                sd.rrect(n["x"], n["y"], 14, max(h, 4), stroke, 2.0)
            if n["side"] == "right":
                lx, anchor = n["x"] + 26, "start"
            elif n["side"] == "left":
                lx, anchor = n["x"] - 12, "end"
            else:
                lx, anchor = n["x"] + 7, "middle"
            ly = n["y"] - 14 if n["side"] == "top" else n["y"] + h / 2 + 6
            sd.text(lx, ly - (10 if n["sub"] and n["side"] != "top" else 0), n["label"], 27, sd.INK, anchor=anchor, font="Caveat", weight=700)
            if n["sub"]:
                sd.text(lx, ly + (16 if n["side"] != "top" else -30), n["sub"], 18, "#5e5a53", anchor=anchor)


def band(x1, y1, x2, y2, w, key):
    fill, stroke = PAL[key]
    mx = (x1 + x2) / 2
    d = (f"M{x1:.1f},{y1:.1f} C{mx:.1f},{y1:.1f} {mx:.1f},{y2:.1f} {x2:.1f},{y2:.1f} L{x2:.1f},{y2 + w:.1f} "
         f"C{mx:.1f},{y2 + w:.1f} {mx:.1f},{y1 + w:.1f} {x1:.1f},{y1 + w:.1f} Z")
    xmin, ymin = min(x1, x2), min(y1, y2)
    sd.hachure(xmin, ymin - 2, abs(x2 - x1), abs(y2 - y1) + w + 4, stroke, gap=9 if w > 20 else 6, sw=1.4, op=0.5,
               fill=fill, fill_op=0.75, angle=-32, shape=f'<path d="{d}"/>')
    for yy in (0, w):
        for pss in range(2):
            j = sd.j
            sd.add(f'<path d="M{x1 + j(1):.1f},{y1 + yy + j(1.2):.1f} C{mx + j(4):.1f},{y1 + yy + j(2):.1f} {mx + j(4):.1f},{y2 + yy + j(2):.1f} '
                   f'{x2 + j(1):.1f},{y2 + yy + j(1.2):.1f}" fill="none" stroke="{stroke}" stroke-width="{1.7 if pss == 0 else 1.0}" '
                   f'opacity="{0.9 if pss == 0 else 0.6}" stroke-linecap="round"/>')


# ----------------------------------------------------------------------------- dibujos de destinos
def cloud(cx, cy, key="vapor"):
    fill, stroke = PAL[key]
    for dx, dy, r in ((-34, 6, 26), (-6, -12, 32), (28, 2, 26), (6, 16, 24)):
        sd.hachure(cx + dx - r, cy + dy - r, 2 * r, 2 * r, stroke, gap=6, sw=1.2, op=0.45, fill=fill, fill_op=0.85,
                   shape=f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{r}"/>')
        sd.rellipse(cx + dx, cy + dy, r, r, stroke, 2.0, n=18)


def mound(cx, cy, key="compost"):
    fill, stroke = PAL[key]
    d = f"M{cx - 62},{cy + 30} Q{cx - 40},{cy - 40} {cx},{cy - 44} Q{cx + 40},{cy - 40} {cx + 62},{cy + 30} Z"
    sd.hachure(cx - 64, cy - 46, 128, 78, stroke, gap=6, sw=1.4, op=0.7, fill=fill, fill_op=0.9, angle=40, cross=True, shape=f'<path d="{d}"/>')
    for p in range(2):
        sd.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2.4 if p == 0 else 1.3}" stroke-linejoin="round" '
               f'transform="translate({sd.j(1.5):.1f},{sd.j(1.5):.1f})"/>')
    g = PAL["corazon"][1]
    sd.add(f'<path d="M{cx},{cy - 44} Q{cx + 4},{cy - 70} {cx + 22},{cy - 78} Q{cx + 14},{cy - 58} {cx},{cy - 44}" fill="{PAL["corazon"][0]}" stroke="{g}" stroke-width="2"/>')


def build():
    f = flows_v7()
    S = Sankey()
    sd.text(60, 72, "Balance de masa de la biorrefinería de piña", 58, sd.INK, font="Caveat", weight=700)
    sd.text(62, 112, f"Diseño óptimo de la versión 7 · Chocó 2022 · {fmt(f['F'])} t/año de fruta procesada. El ancho de cada corriente es "
                     "proporcional a su masa (t/año); los líquidos se pasan a masa con sus densidades.", 21, "#5e5a53")
    # nodos
    S.node("fruta", 250, 700, "Fruta", "cascara", f"{fmt(f['F'])} t/año", side="left")
    S.node("frente", 470, 700, "Frente", "neutro", "lavado · pelado", side="top")
    S.node("pulpa", 720, 250, "Pulpa", "pulpa", "45 %", side="top")
    S.node("cascara", 720, 650, "Cáscara", "cascara", "30 %", side="top")
    S.node("corazon", 720, 1150, "Corazón", "corazon", "10 %", side="top")
    S.node("corona", 720, 1360, "Corona", "corona", "15 %", side="top")
    S.node("clar", 1010, 225, "Centrífuga", "agua", "clarificación", side="top")
    S.node("lodos", 1220, 470, "Lodos", "agua", "12 %", side="top")
    S.node("bodega", 1420, 215, "Bodega", "pulpa", "fermentación", side="top")
    S.node("vino", 1700, 200, "Vino", "pulpa", None, side="top")
    S.node("secador", 1220, 660, "Secador", "cascara", "de banda", side="top")
    S.node("fermc", 1220, 930, "Fermentación", "vinagre", "jugo de cáscara", side="top")
    S.node("aire", 1700, 860, "Aire (O₂)", "aire", None, side="left")
    S.node("agua", 1700, 1000, "Agua de dilución", "agua", "cierre del balance", side="left")
    S.node("acet", 1960, 700, "Acetificador", "vinagre", None, side="top")
    PX = 2240
    S.node("p_vino", PX, 170, "Vino a granel", "pulpa", None, side="right", bar=True)
    S.node("p_harina", PX, 480, "Harina de fibra", "cascara", None, side="right")
    S.node("p_vinagre", PX, 720, "Vinagre al 5 %", "vinagre", None, side="right")
    S.node("p_emis", PX, 1040, "Vapor y CO₂", "vapor", None, side="right")
    S.node("p_comp", PX, 1300, "Compost y caldera", "compost", None, side="right")
    # flujos (en el orden de apilamiento de cada nodo)
    S.flow("fruta", "frente", f["F"], "cascara", None)
    S.flow("frente", "pulpa", f["fr"]["pulpa"], "pulpa", fmt(f["fr"]["pulpa"]), 0.55)
    S.flow("frente", "cascara", f["fr"]["cascara"], "cascara", fmt(f["fr"]["cascara"]), 0.55)
    S.flow("frente", "corazon", f["fr"]["corazon"], "corazon", fmt(f["fr"]["corazon"]), 0.6)
    S.flow("frente", "corona", f["fr"]["corona"], "corona", fmt(f["fr"]["corona"]), 0.6)
    S.flow("pulpa", "clar", f["juice"], "pulpa", f"jugo {fmt(f['juice'])}", 0.5)
    S.flow("pulpa", "p_comp", f["bagazo"], "compost", f"bagazo de pulpa {fmt(f['bagazo'])}", 0.12, 4)
    S.flow("clar", "bodega", f["clar"], "agua", f"mosto {fmt(f['clar'])}", 0.5)
    S.flow("clar", "lodos", f["lodos"], "agua", fmt(f["lodos"]), 0.5)
    S.flow("lodos", "bodega", f["rec"], "agua", f"MF de lías {fmt(f['rec'])}", 0.55, -4)
    S.flow("lodos", "secador", f["l_sec"], "agua", fmt(f["l_sec"]), 0.5)
    S.flow("lodos", "p_comp", f["ret"] + max(f["l_comp"], 0), "compost", f"retenido {fmt(f['ret'] + max(f['l_comp'], 0))}", 0.18)
    S.flow("bodega", "vino", f["wine"], "pulpa", f"vino {fmt(f['wine'])}", 0.5)
    S.flow("bodega", "p_emis", f["co2_l"], "vapor", f"CO₂ y lías {fmt(f['co2_l'])}", 0.12)
    S.flow("vino", "p_vino", f["w_sold"], "pulpa", fmt(f["w_sold"]), 0.5)
    S.flow("vino", "acet", f["w_vin"], "vinagre", f"vino a vinagre {fmt(f['w_vin'])}", 0.45)
    S.flow("cascara", "secador", f["torta"], "cascara", f"torta {fmt(f['torta'])}", 0.5)
    S.flow("cascara", "fermc", f["pj"], "vinagre", f"jugo de cáscara {fmt(f['pj'])}", 0.5)
    S.flow("secador", "p_harina", f["flour"], "cascara", fmt(f["flour"]), 0.5)
    S.flow("secador", "p_emis", f["vapor"], "vapor", f"agua evaporada {fmt(f['vapor'])}", 0.35)
    S.flow("fermc", "acet", f["pwine"], "vinagre", f"vino de cáscara {fmt(f['pwine'])}", 0.28)
    S.flow("fermc", "p_emis", f["co2_pj"], "vapor", f"CO₂ {fmt(f['co2_pj'])}", 0.5)
    S.flow("aire", "acet", f["o2"], "aire", f"O₂ {fmt(f['o2'])}", 0.5, -4)
    S.flow("agua", "acet", f["water"], "agua", fmt(f["water"]), 0.5)
    S.flow("acet", "p_vinagre", f["vin"], "vinagre", fmt(f["vin"]), 0.5)
    S.flow("corazon", "p_comp", f["fr"]["corazon"], "corazon", "corazón (B: bromelaína)", 0.25)
    S.flow("corona", "p_comp", f["fr"]["corona"], "corona", "corona", 0.25)
    S.draw()
    # dibujos y valores de los destinos
    tot = {k: S.nodes[k]["tot_in"] for k in ("p_vino", "p_harina", "p_vinagre", "p_emis", "p_comp")}
    sd.bottle(PX + 500, 205, "pulpa"); sd.sack(PX + 500, 505, "cascara"); sd.jar(PX + 500, 800, "vinagre")
    cloud(PX + 500, 1070); mound(PX + 500, 1360)
    for k, y, extra in (("p_vino", 170, f"≈ {fmt(f['w_sold'] / RHO_W)} m³"), ("p_harina", 480, "cáscara + lías"),
                        ("p_vinagre", 720, f"≈ {fmt(f['vin'] / RHO_V)} m³"), ("p_emis", 1040, "secado y fermentaciones"),
                        ("p_comp", 1300, "bagazo, corazón, corona, retenido")):
        h = tot[k] * K
        sd.text(PX + 26, y + h / 2 + 34, f"{fmt(tot[k])} t/año · {extra}", 18, "#5e5a53")
    sd.text(240, 900, f"no procesada {fmt(f['loss'])} t", 18, "#8f8a82", anchor="end", italic=True)
    # cierre del balance
    ins = f["F"] + f["o2"] + f["water"]
    outs = sum(tot.values())
    bx, by = 60, 1480
    sd.rrect(bx, by, 1180, 175, PAL["neutro"][1], 1.8, dash="8 7", passes=1)
    sd.text(bx + 20, by + 40, "Cierre del balance (t/año)", 30, sd.INK, font="Caveat", weight=700)
    sd.text(bx + 20, by + 78, f"Entradas: fruta {fmt(f['F'])} + O₂ {fmt(f['o2'])} + agua de dilución {fmt(f['water'])} = {fmt(ins)}", 21, sd.INK)
    sd.text(bx + 20, by + 110, f"Salidas: vino {fmt(tot['p_vino'])} + vinagre {fmt(tot['p_vinagre'])} + harina {fmt(tot['p_harina'])} + "
                               f"vapor y CO₂ {fmt(tot['p_emis'])} + compost {fmt(tot['p_comp'])} = {fmt(outs)}", 21, sd.INK)
    sd.text(bx + 20, by + 144, f"Productos vendibles: {100 * (tot['p_vino'] + tot['p_vinagre'] + tot['p_harina']) / ins:.0f} % de la masa que entra; "
                               f"la fruta deja {100 * (tot['p_comp']) / f['F']:.0f} % como residuo sólido.", 19, "#5e5a53")
    lx, ly = 1300, 1480
    sd.rrect(lx, ly, 1460, 175, PAL["neutro"][1], 1.8, dash="8 7", passes=1)
    sd.text(lx + 20, ly + 40, "Supuestos", 30, sd.INK, font="Caveat", weight=700)
    for i, t in enumerate(["Prensa de pulpa: 87 % de jugo (Quesada Salas 2013); centrífuga: 12 % de lodos; la MF de lías recupera el 60 % del jugo.",
                           "Bodega: CO₂ y lías por diferencia entre mosto y vino; jugo de cáscara con 104 g/kg de azúcar.",
                           "Acetificación: 46 g de etanol + 32 g de O₂ → 60 g de ácido; vinagre al 5 %; el agua de dilución cierra el balance.",
                           "Corona y corazón van a compost o caldera en la configuración A; con bromelaína, el corazón va a la línea B."]):
        sd.text(lx + 20, ly + 74 + i * 26, t, 17.5, "#5e5a53")
    return f


if __name__ == "__main__":
    f = build()
    svg = sd.svg_doc()
    p_svg = os.path.join(FIGS, "fig34_balance_masa.svg")
    open(p_svg, "w", encoding="utf-8").write(svg)
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {sd.W}, height: {sd.H} }}, deviceScaleFactor: 1.25 }});
  await p.goto('file://{p_svg}');
  await p.waitForTimeout(800);
  await p.screenshot({{ path: '{os.path.join(FIGS, "fig34_balance_masa.png")}' }});
  await b.close();
}})();"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
    subprocess.run(["node", fh.name], check=True)
    os.unlink(fh.name)
    print("fig fig34_balance_masa.svg/.png", {k: round(v) for k, v in f.items() if isinstance(v, float)})
