"""
Balance de energía de la biorrefinería de piña dibujado a mano (Sankey con el estilo de las figs. 33 y 34).

Flujos del diseño óptimo de la versión 7 (results/dimensionamiento.json) con los mismos consumos que usa el TEA
(planta_trl9.design, tea_dimensionado.build_case):
  - electricidad del grupo electrógeno diésel (zona no interconectada) y calor de proceso con GLP;
  - calor liberado por la fermentación alcohólica (≈ 96,6 kJ/mol de azúcar) y por la acetificación (493 kJ/mol de ácido),
    que retiran los chillers;
  - usos por equipo y destinos finales (calor latente del agua evaporada, calor rechazado al ambiente, gases y pérdidas).
No se contabiliza la energía química de los productos: es un balance de servicios y calores de proceso.
Salidas: figs/fig35_balance_energia.svg y .png.
"""
import json, os, subprocess, tempfile
import superestructura_dibujo as sd
import balance_dibujo as bd
import planta_trl9 as pt
import capacidad as cp
import dimensionamiento as dm
import params as p

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
sd.W, sd.H = 2840, 1760
bd.K = 0.075                                  # px por GJ/año
PAL = sd.PAL
PAL.update(dict(elec=("#efe2ae", "#a68a33"), glp=("#ecc9b8", "#b0694f"), reac=("#dcc0cf", "#94657f"),
                latente=("#cfdde7", "#62839b"), ambiente=("#d8dde3", "#7d8894"), perdidas=("#ddd3c6", "#8a7a66")))
ETA_GEN, ETA_GLP = 0.33, 0.85                 # grupo electrógeno diésel [S]; caldera de GLP (plantilla)
H_LAT = 2.26                                  # MJ/kg de agua evaporada
fmt = lambda v: f"{v:,.0f}".replace(",", " ")


def energy_v7():
    d = json.load(open(os.path.join(HERE, "results", "dimensionamiento.json")))
    r = d["E1|Óptimo económico"]; s = r["scen"][0]; pr = s["products"]
    F = pr["fruta_t"]; D = pt.design(F); L = D["lines"]; b = D["balance"]; v, h = L["vino"], L["harina"]
    kwh = lambda x: x * 3.6 / 1000             # kWh -> GJ
    juice, wine_d = b["juice_m3"], b["wine_m3"]
    e_frente = 1.3 * (F * 8 + b["peel_t"] * 12)
    e_chill_v = 1.3 * (v["elec_kWh"] - F * 8 - juice * 3.5 - wine_d * 1.0)
    e_bombas = 1.3 * (juice * 3.5 + wine_d * 1.0) + pr["mosto_m3"] * 2.0 + pr["lias_MF_m3"] * 1.0 + pr["vino_m3"] * 0.5
    e_sec = 1.3 * b["flour_t"] * 40
    V = float(r["sizes"]["Acetificador"].split()[0]) if r["sizes"]["Acetificador"] != "no" else 0.0
    e_aire = dm.AERATION_KW_M3 * V * 0.9 * 8766
    acid = pr["acido_kg"]
    e_chill_a = acid * dm.ACID_HEAT / 3.6 / 4.0
    E = dict(frente=kwh(e_frente), bombas=kwh(e_bombas), secador_el=kwh(e_sec), aire=kwh(e_aire), frio=kwh(e_chill_v + e_chill_a))
    E_tot = sum(E.values())
    q_mac = b["pulp_t"] * 1000 * 3.9 * (55 - 28) / 1000 * 0.4 / 1000                # GJ
    q_dry = (h["heat_MJ"] + pr.get("lias_secador_t", 0) * dm.LEES_DRY_EQ * h["heat_MJ"] / (b["peel_t"] * dm.CAKE)) / 1000
    Q_tot = q_mac + q_dry
    must_ferm = pr["vino_m3"] / dm.WINE_PM
    h_alc = must_ferm * p.S_JUICE / 180.16 * 96.6 / 1000 + pr["jugo_cascara_vinagre_t"] * 104 / 180.16 * 96.6 / 1000
    h_acet = acid * dm.ACID_HEAT / 1000
    water = b["water_evap_t"] + pr.get("lias_secador_t", 0) * (1 - dm.LEES_FLOUR)
    latent = water * H_LAT
    crown = b["crown_dm_t"] * 17.0 * 0.80
    return dict(F=F, E=E, E_tot=E_tot, diesel=E_tot / ETA_GEN, q_mac=q_mac, q_dry=q_dry, Q_tot=Q_tot, glp=Q_tot / ETA_GLP,
                h_alc=h_alc, h_acet=h_acet, latent=min(latent, q_dry), water=water, crown=crown, acid=acid, sizes=r["sizes"])


def waves(cx, cy, key="ambiente"):
    fill, stroke = PAL[key]
    for k in range(3):
        x0 = cx - 34 + k * 26
        d = f"M{x0},{cy + 46} C{x0 - 16},{cy + 20} {x0 + 16},{cy + 4} {x0},{cy - 20} C{x0 - 16},{cy - 40} {x0 + 14},{cy - 54} {x0 + 2},{cy - 70}"
        for pss in range(2):
            sd.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{3.2 if pss == 0 else 1.6}" stroke-linecap="round" '
                   f'opacity="{0.9 if pss == 0 else 0.6}" transform="translate({sd.j(1.5):.1f},{sd.j(1.5):.1f})"/>')
    sd.hachure(cx - 52, cy + 46, 104, 18, stroke, gap=5, sw=1.2, op=0.6, fill=fill, fill_op=0.9)
    sd.rrect(cx - 52, cy + 46, 104, 18, stroke, 2.0)


def flame(cx, cy, key="perdidas"):
    fill, stroke = PAL[key]
    d = (f"M{cx},{cy + 52} C{cx - 46},{cy + 44} {cx - 46},{cy - 4} {cx - 14},{cy - 36} C{cx - 12},{cy - 14} {cx},{cy - 10} {cx + 2},{cy - 22} "
         f"C{cx + 4},{cy - 50} {cx + 18},{cy - 62} {cx + 22},{cy - 74} C{cx + 50},{cy - 30} {cx + 48},{cy + 40} {cx},{cy + 52} Z")
    sd.hachure(cx - 50, cy - 76, 100, 130, stroke, gap=6, sw=1.4, op=0.7, fill=fill, fill_op=0.9, angle=60, shape=f'<path d="{d}"/>')
    for pss in range(2):
        sd.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2.4 if pss == 0 else 1.3}" stroke-linejoin="round" '
               f'transform="translate({sd.j(1.5):.1f},{sd.j(1.5):.1f})"/>')


def build():
    e = energy_v7(); E = e["E"]
    S = bd.Sankey()
    sd.text(60, 72, "Balance de energía de la biorrefinería de piña", 58, sd.INK, font="Caveat", weight=700)
    sd.text(62, 112, f"Diseño óptimo de la versión 7 · Chocó 2022 · {fmt(e['F'])} t/año de fruta. El ancho de cada corriente es "
                     "proporcional a la energía (GJ/año); zona no interconectada: la electricidad sale de un grupo electrógeno diésel.", 21, "#5e5a53")
    # nodos: fuentes
    S.node("diesel", 340, 210, "Diésel", "elec", f"{fmt(e['diesel'])} GJ/año", side="left")
    S.node("glp", 340, 640, "GLP", "glp", f"{fmt(e['glp'])} GJ/año", side="left")
    S.node("ralc", 340, 1080, "Fermentación alcohólica", "reac", "calor de reacción", side="left")
    S.node("racet", 340, 1180, "Acetificación", "reac", "493 kJ/mol de ácido", side="left")
    # conversión
    S.node("elec", 700, 200, "Electricidad", "elec", f"{fmt(e['E_tot'] / 3.6)} MWh/año", side="top")
    S.node("calor", 700, 650, "Calor de proceso", "glp", "caldera de GLP", side="top")
    # usos
    S.node("u_frente", 1150, 170, "Frente y prensas", "elec", "lavado, pelado, trituración", side="right")
    S.node("u_bombas", 1150, 300, "Bombas y separación", "elec", "centrífuga, MF de lías, N₂", side="right")
    S.node("u_aire", 1150, 420, "Aireación", "elec", f"acetificador {e['sizes']['Acetificador']}", side="right")
    S.node("u_secel", 1150, 560, "Ventiladores y molino", "elec", "secador de harina", side="right")
    S.node("u_mac", 1150, 650, "Maceración a 55 °C", "glp", "pectinasa, 1 h", side="right")
    S.node("u_dry", 1150, 760, "Secado", "glp", f"{fmt(e['water'])} t de agua evaporada", side="right")
    S.node("u_frio", 1150, 1060, "Frío (chillers)", "reac", "bodegas y acetificador", side="right")
    # destinos
    PX = 2060
    S.node("d_lat", PX, 700, "Calor latente del agua evaporada", "latente", None, side="right")
    S.node("d_amb", PX, 1010, "Calor rechazado al ambiente", "ambiente", None, side="right")
    S.node("d_gas", PX, 420, "Gases del secador y pérdidas", "perdidas", None, side="right")
    S.node("d_conv", PX, 170, "Pérdidas de conversión", "perdidas", None, side="right")
    # flujos
    S.flow("diesel", "elec", e["E_tot"], "elec", fmt(e["E_tot"]), 0.5)
    S.flow("diesel", "d_conv", e["diesel"] - e["E_tot"], "perdidas", f"grupo electrógeno (η {int(ETA_GEN * 100)} %) {fmt(e['diesel'] - e['E_tot'])}", 0.22, -4)
    S.flow("glp", "calor", e["Q_tot"], "glp", fmt(e["Q_tot"]), 0.5)
    S.flow("glp", "d_conv", e["glp"] - e["Q_tot"], "perdidas", f"caldera {fmt(e['glp'] - e['Q_tot'])}", 0.12)
    S.flow("elec", "u_frente", E["frente"], "elec", fmt(E["frente"]), 0.5)
    S.flow("elec", "u_bombas", E["bombas"], "elec", fmt(E["bombas"]), 0.5)
    S.flow("elec", "u_aire", E["aire"], "elec", fmt(E["aire"]), 0.5)
    S.flow("elec", "u_secel", E["secador_el"], "elec", fmt(E["secador_el"]), 0.5)
    S.flow("elec", "u_frio", E["frio"], "elec", None)
    S.flow("calor", "u_mac", e["q_mac"], "glp", fmt(e["q_mac"]), 0.5)
    S.flow("calor", "u_dry", e["q_dry"], "glp", fmt(e["q_dry"]), 0.5)
    S.flow("ralc", "u_frio", e["h_alc"], "reac", fmt(e["h_alc"]), 0.5)
    S.flow("racet", "u_frio", e["h_acet"], "reac", fmt(e["h_acet"]), 0.5)
    S.flow("u_frente", "d_amb", E["frente"], "ambiente", None)
    S.flow("u_bombas", "d_amb", E["bombas"], "ambiente", None)
    S.flow("u_aire", "d_amb", E["aire"], "ambiente", None)
    S.flow("u_secel", "d_gas", E["secador_el"], "perdidas", None)
    S.flow("u_mac", "d_gas", e["q_mac"], "perdidas", None)
    S.flow("u_dry", "d_gas", e["q_dry"] - e["latent"], "perdidas", f"gases {fmt(e['q_dry'] - e['latent'])}", 0.5)
    S.flow("u_dry", "d_lat", e["latent"], "latente", f"{fmt(e['latent'])}", 0.5)
    S.flow("u_frio", "d_amb", E["frio"] + e["h_alc"] + e["h_acet"], "ambiente", f"condensadores {fmt(E['frio'] + e['h_alc'] + e['h_acet'])}", 0.5)
    S.draw()
    tot = {k: S.nodes[k]["tot_in"] for k in ("d_lat", "d_amb", "d_gas", "d_conv")}
    flame(PX + 500, 210, "perdidas"); flame(PX + 500, 470, "perdidas"); bd.cloud(PX + 500, 760, "latente"); waves(PX + 500, 1080)
    for k, y in (("d_conv", 170), ("d_gas", 420), ("d_lat", 700), ("d_amb", 1010)):
        hpx = tot[k] * bd.K
        sd.text(PX + 26, y + hpx / 2 + 34, f"{fmt(tot[k])} GJ/año", 18, "#5e5a53")
    ins = e["diesel"] + e["glp"] + e["h_alc"] + e["h_acet"]
    outs = sum(tot.values())
    # cierre y lecturas
    bx, by = 60, 1440
    sd.rrect(bx, by, 1300, 290, PAL["neutro"][1], 1.8, dash="8 7", passes=1)
    sd.text(bx + 20, by + 40, "Cierre y lectura (GJ/año)", 30, sd.INK, font="Caveat", weight=700)
    sd.text(bx + 20, by + 78, f"Entradas: diésel {fmt(e['diesel'])} + GLP {fmt(e['glp'])} + calores de reacción {fmt(e['h_alc'] + e['h_acet'])} = {fmt(ins)}", 21, sd.INK)
    sd.text(bx + 20, by + 110, f"Salidas: conversión {fmt(tot['d_conv'])} + gases {fmt(tot['d_gas'])} + latente {fmt(tot['d_lat'])} + ambiente {fmt(tot['d_amb'])} = {fmt(outs)}", 21, sd.INK)
    share_v = (E["aire"] + kwh_chill_a(e)) / e["E_tot"]
    sd.text(bx + 20, by + 150, f"• El secado es el {100 * e['q_dry'] / e['Q_tot']:.0f} % del calor; el agua evaporada se lleva {100 * e['latent'] / e['q_dry']:.0f} % de él como calor latente.", 19, "#5e5a53")
    sd.text(bx + 20, by + 180, f"• El vinagre (aireación + frío del acetificador) usa el {100 * share_v:.0f} % de la electricidad: 493 kJ/mol de ácido hay que retirarlos con chillers.", 19, "#5e5a53")
    sd.text(bx + 20, by + 210, f"• Con diésel al {int(ETA_GEN * 100)} %, generar la electricidad pierde {fmt(e['diesel'] - e['E_tot'])} GJ/año, tanto como todo el calor de secado.", 19, "#5e5a53")
    sd.text(bx + 20, by + 240, f"• Ácido producido: {fmt(e['acid'] / 1000)} t/año; agua evaporada: {fmt(e['water'])} t/año.", 19, "#5e5a53")
    # recuadro de la corona
    cx, cy = 1420, 1440
    sd.rrect(cx, cy, 1360, 290, PAL["corazon"][1], 2.0, dash="10 7")
    sd.hachure(cx + 3, cy + 3, 1354, 48, PAL["corazon"][1], gap=9, sw=1.3, op=0.35, fill=PAL["corazon"][0], fill_op=0.55)
    sd.text(cx + 20, cy + 38, "Oportunidad: la corona como combustible", 30, sd.INK, font="Caveat", weight=700)
    sd.text(cx + 20, cy + 84, f"La corona ({fmt(e['F'] * 0.15)} t/año, 20 % de materia seca, 17 MJ/kg) en una caldera de biomasa al 80 % daría "
                              f"≈ {fmt(e['crown'])} GJ/año de calor,", 19, "#5e5a53")
    sd.text(cx + 20, cy + 112, f"el {100 * e['crown'] / e['Q_tot']:.0f} % del calor de proceso que hoy se compra como GLP ({fmt(e['glp'])} GJ/año de combustible). "
                               "En el óptimo de la versión 7 la corona va a compost:", 19, "#5e5a53")
    sd.text(cx + 20, cy + 140, "la caldera de biomasa (TRL 9, línea L7b del TEA) no estaba en la superestructura del dimensionamiento.", 19, "#5e5a53")
    sd.text(cx + 20, cy + 180, "Supuestos: grupo electrógeno al 33 % [S]; caldera de GLP al 85 % (plantilla); 96,6 kJ/mol de azúcar fermentado;", 18, "#6f6a62", italic=True)
    sd.text(cx + 20, cy + 206, "2,26 MJ/kg de calor latente; consumos por equipo de planta_trl9 y del TEA (incluye 30 % de no listados).", 18, "#6f6a62", italic=True)
    sd.text(cx + 20, cy + 232, "No se cuenta la energía química de los productos: es un balance de servicios y calores de proceso.", 18, "#6f6a62", italic=True)
    rel_x = 340 + 7
    sd.text(1130, 1040, f"compresores {fmt(E['frio'])} →", 18, PAL["elec"][1], anchor="end")
    sd.text(rel_x, 1300, "fuentes internas: las retiran los chillers", 18, PAL["reac"][1], anchor="middle", italic=True)
    return e


def kwh_chill_a(e):
    return e["acid"] * dm.ACID_HEAT / 3.6 / 4.0 * 3.6 / 1000


if __name__ == "__main__":
    e = build()
    svg = sd.svg_doc()
    p_svg = os.path.join(FIGS, "fig35_balance_energia.svg")
    open(p_svg, "w", encoding="utf-8").write(svg)
    js = f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: {sd.W}, height: {sd.H} }}, deviceScaleFactor: 1.25 }});
  await p.goto('file://{p_svg}');
  await p.waitForTimeout(800);
  await p.screenshot({{ path: '{os.path.join(FIGS, "fig35_balance_energia.png")}' }});
  await b.close();
}})();"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
    subprocess.run(["node", fh.name], check=True)
    os.unlink(fh.name)
    print("fig fig35_balance_energia", {k: round(v) for k, v in e.items() if isinstance(v, float)}, {k: round(v) for k, v in e["E"].items()})
