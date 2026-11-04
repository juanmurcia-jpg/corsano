"""Genera informe.html (versión 2) a partir de los resultados JSON; conserva las secciones de la versión 1."""
import json, os, re, html
import numpy as np
import planta_trl9 as pt
import capacidad as cp
import params as p

R = lambda f: json.load(open(os.path.join("results", f)))
E = html.escape
MM = 1e6


def n0(x):
    return f"{x:,.0f}".replace(",", " ")


def n1(x):
    return f"{x:,.1f}".replace(",", " ").replace(".", ",")


def pct(x, d=1):
    return (f"{x*100:.{d}f} %").replace(".", ",")


def table(head, rows, num_cols=()):
    h = "".join(f"<th>{E(c)}</th>" for c in head)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f'<td class="num">{c}</td>' if q in num_cols else f"<td>{c}</td>" for q, c in enumerate(r)) + "</tr>"
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'


def fig(name, alt, cap, maxw=None):
    st = f' style="max-width:{maxw}px"' if maxw else ""
    return f'<figure{st}><img src="figs/{name}" alt="{E(alt)}"><figcaption>{cap}</figcaption></figure>'


mr = R("moresi_R_P1.json"); m2 = R("moresi_P2_P3.json"); capj = R("capacidad.json"); tea = R("tea_lineas.json")
plans = R("milp_planes.json"); sweep = R("milp_barrido.json"); evp = R("milp_tea_planes.json"); stn = R("stn_semana.json")
xchk = R("tea_excel_check.json")
b1 = cp.full_balance(1.0)

# ------------------------------------------------------------------------------ bloques de datos
R1 = mr["R1"]
cal_c = R1["calibrated"][0]["tF"]; cal_o = R1["calibrated"][1]["tF"]
nom_c = R1["nominal"][0]["tF"]; nom_o = R1["nominal"][1]["tF"]
r2rows = []
names = [("NF", "Fermentadores N_F"), ("QRT", "Carga de refrigeración Q_RT (kW)"), ("CI", "Inversión C_I (MLit)"), ("dep_fab", "Depreciación fabricados"),
         ("dep_mach", "Depreciación maquinaria"), ("maint", "Mantenimiento"), ("elec", "Electricidad"), ("inoc", "Inóculo"), ("man", "Mano de obra"),
         ("Co", "Costo operativo C_o (MLit)"), ("Cv", "Costo específico C_v (Lit/L)")]
for key, lab in names:
    row = [lab]
    for r in mr["R2"]:
        ref = r["ref"][key]; mdl = r["model"]["Cv_lit_L"] if key == "Cv" else r["model"][key]
        row.append(f"{n1(ref)} / {n1(mdl)}")
    r2rows.append(row)
p1rows = []
for r in mr["P1"]:
    if abs(r["X0"] - R1["X0_eff"]) > 1e-6:
        continue
    pol = "cerrado (isotérmico)" if r["mode"] == "closed" else f"abierto {r['T0']}–{r['Ts']} °C"
    p1rows.append([pol, f"{r['T0']} °C", "no termina" if r["t85"] != r["t85"] else n1(r["t85"]),
                   "no termina" if r["t975"] != r["t975"] else n1(r["t975"])])
P3 = m2["P3"]
p2best = []
for case in sorted({r["case"] for r in m2["P2"]}):
    for reg, lab in (("continuo_7500h", "continua (7 500 h)"), ("estacional_28d", "estacional (28 d, como Moresi)")):
        sel = [r for r in m2["P2"] if r["case"] == case and r["regime"] == reg]
        b = min(sel, key=lambda r: r["Cv"])
        p2best.append([E(case.replace("_", " ")), lab, n0(b["VF"]), str(b["NF"]), n1(b["fill_h"]), n0(b["CI"] / 1000), n1(b["Cv"] * 1000)])
C2 = capj["C2"]; C3 = capj["C3"]; C4 = capj["C4"]; Cd = capj["C1_design"]
c3rows = [[E(k), n0(v["fruit_t"]), n0(v["wine_hL"]), pct(v["wine_hL"] / (p.WINE_VOL_YR * 10)), n0(v["flour_t"]), n0(v["bromelain_kg"])] for k, v in C3.items()]
# diseño TRL-9 (base de la tesis)
t0 = list(tea.keys())[0]
des = tea[t0]["design"]
trl_rows = [[E(k), str(v[0]), E(v[1])] for k, v in pt.TECH.items()]
eqrows = []
lname = dict(vino="L1 Vino", vinagre="L3 Vinagre", bromelaina="L4 Bromelaína + polvo", harina="L5 Harina de cáscara", etanol="L6 Etanol", energia="L7a Gasificación (TRL 8)")
for lk, v in des["lines"].items():
    for e in v["equipment"]:
        eqrows.append([lname.get(lk, lk), E(e["name"]), str(e["qty"]), f"{n1(e['size'])} {E(e['unit'])}", n1(e["need"]), str(e["TRL"])])
# TEA por línea
tea_rows = []
for tag, d in tea.items():
    for k, v in d["tea"].items():
        r = v["res"]; pr = v["case"]["product"]["price"]
        tea_rows.append([E(tag), E(k), n0(r["FCI"] / MM), n0(r["NPV"] / MM), (pct(r["MIRR"]) if r["MIRR"] == r["MIRR"] else "—"),
                         ("—" if k.startswith("Planta") else n0(r["LCOP"])), ("—" if k.startswith("Planta") else n0(pr)),
                         ("—" if v["breakeven"] != v["breakeven"] else n0(v["breakeven"])), pct(v["mc"]["P_pos"], 0)])
# planes MILP
plan_rows = []
for so in plans:
    if so["obj"] <= 0 and "Chocó" not in so["label"]:
        continue
    L = so["lines"]
    act = ", ".join(l for l, v in L.items() if v["size_scale"]) or "ninguna"
    wine = L["vino"]["processed"] * b1["wine_m3"] / b1["pulp_t"] - L["vinagre"]["processed"]
    flour = L["harina"]["processed"] * b1["flour_t"] / b1["peel_t"]
    brom = L["bromelaina"]["processed"] * b1["bromelain_kg"] / b1["core_t"]
    vin = L["vinagre"]["processed"] * b1["vinegar_m3"] / (b1["wine_m3"] * 0.16) if L["vinagre"]["processed"] else 0
    plan_rows.append([E(so["label"]), act, n0(so["fruit_bought"]), n0(L["vino"]["processed"]), n0(L["harina"]["processed"]),
                      n0(L["bromelaina"]["processed"]), n0(wine), n0(vin), n0(flour), n0(brom), n0(so["obj"] / MM)])
ev_rows = [[E(e["label"]), ", ".join(e["lines"]), n0(e["scale"]), n0(e["FCI"] / MM), n0(e["NPV"] / MM), pct(e["MIRR"]),
            ("—" if e["payback"] != e["payback"] else n1(e["payback"])), str(e["workers"]), pct(e["P_pos"], 0)] for e in evp]
minv = []
for mode in ("fruta", "residuos"):
    for wp in (1600.0, 2200.0, 3000.0, 4000.0):
        ok = sorted([r["supply"] for r in sweep if r["mode"] == mode and r["wp"] == wp and r["obj"] > 1e6])
        if mode == "residuos" and wp != 1600.0:
            continue
        minv.append([("Fruta de rechazo comprada" if mode == "fruta" else "Residuos de procesador (cualquier precio de vino)"),
                     (n0(wp) if mode == "fruta" else "—"), (n0(ok[0]) if ok else "> 22 000")])
stn_rows = []
for lab, r in stn.items():
    u = r["util"]
    stn_rows.append([E(lab), r["status"], n0(r["nbin"]), n1(r["fruit_week"]), n1(r["fruit_left"]),
                     ", ".join(f"{k} {pct(v, 0)}" for k, v in sorted(u.items()))])
x_rows = [[E(c["file"]), n0(c["NPV_py"] / MM), n0(c["NPV_xl"] / MM), f"{c['dNPV_rel']:.1e}"] for c in xchk]

# ------------------------------------------------------------------------------ v1 (secciones previas)
v1 = open("informe_v1.html").read()
style = v1[v1.index("<style>"): v1.index("</style>") + 8]
v1_main = v1[v1.index('<section id="hallazgos">'): v1.index("</main>")]
v1_main = v1_main.replace('id="hallazgos"', 'id="v1-hallazgos"').replace("<h2>Hallazgos principales</h2>", "<h2>Modelos Corsano (versión 1): hallazgos</h2>")

ch = Cd
html_out = f"""<title>Modelos Corsano para la piña</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600;7..72,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
{style}
<main>
<header class="top">
  <p class="kicker">Tesis doctoral · Biorrefinería de piña · Bajo Atrato (Chocó) · versión 2</p>
  <h1>Moresi, capacidad, diseño TRL-9 y TEA por línea de producción</h1>
  <p class="lede">Esta versión pone en el centro las referencias de Moresi (1989a, b), dimensiona la materia prima y la planta con tecnologías TRL-9, monta un TEA por línea con la metodología Burk de sus TEA de asaí y coco, y decide qué procesar con la producción actual mediante un MILP de síntesis (Grossmann) y un programa semanal con red estado-tarea (Maravelias). Los modelos Corsano de la versión 1 siguen al final.</p>
  <div class="meta"><span>Moresi replicado contra su Tabla 3</span><span>EVA 2022 (UPRA)</span><span>11 libros TEA verificados con LibreOffice</span><span>SCIP 10</span></div>
  <ul class="toc">
    <li><a href="#v2-hallazgos">Hallazgos de la versión 2</a></li>
    <li><a href="#moresi">Moresi: réplica y aplicación a la piña</a></li>
    <li><a href="#capacidad">Materia prima y análisis de capacidad</a></li>
    <li><a href="#trl9">Diseño industrial TRL-9</a></li>
    <li><a href="#tea">TEA por línea (metodología Burk)</a></li>
    <li><a href="#milp">Qué procesar con la producción actual (MILP)</a></li>
    <li><a href="#stn">Programación semanal (STN)</a></li>
    <li><a href="#excel">Libros Excel y verificación</a></li>
    <li><a href="#tesis2">Cambios que sugiere a la tesis</a></li>
    <li><a href="#v1-hallazgos">Modelos Corsano (versión 1)</a></li>
  </ul>
</header>

<section id="v2-hallazgos">
<h2>Hallazgos de la versión 2</h2>
<div class="findings">
  <div class="finding"><div class="n">{n0(C2['central']['fruit_t'])} t/año</div><div class="t">Fruta entera que exige la base de la tesis (78 300 hL/año de vino), con un rango de {n0(C2['pulpa alta 55 %']['fruit_t'])} a {n0(C2['pulpa baja 25 % (75 % residuo)']['fruit_t'])} t según la fracción de pulpa. Es {n1(C2['central']['fruit_t']/6146)} veces la producción del Chocó en 2022 (6 146 t, EVA).</div><div class="s">Capacidad · Fig. 18</div></div>
  <div class="finding"><div class="n">+{n1((P3['ratio_from_yield']-1)*100)} de +{n1((P3['ratio']-1)*100)} %</div><div class="t">La ventaja de etanol de la línea premium que reporta §4.2.5 casi entera sale de comparar dos modelos con coeficientes de rendimiento distintos (Moresi frente a Murcia Palacios). La conversión más completa aporta solo +{n1((P3['ratio_from_conversion']-1)*100)} %.</div><div class="s">Moresi · Fig. 17</div></div>
  <div class="finding"><div class="n">v_M &lt; 0 sobre ~28 °C</div><div class="t">La regresión de Moresi (Tabla 1) solo vale en el rango del vino blanco. A 30 °C, la condición del ensayo de Murcia Palacios, predice que la fermentación no avanza.</div><div class="s">Moresi · Fig. 17</div></div>
  <div class="finding"><div class="n">33 % vs 111 %</div><div class="t">Calor del secado de cáscara que cubre la gasificación (TRL 8) frente a una caldera de biomasa de corona (TRL 9). El diseño TRL-9 cambia la isla eléctrica por calor.</div><div class="s">Capacidad · Fig. 18</div></div>
  <div class="finding"><div class="n">Harina de cáscara</div><div class="t">Con la producción actual y residuos de un procesador, la única línea robusta es la harina de fibra: VPN {n0(next(e['NPV'] for e in evp if 'residuos' in e['label'] and 'Chocó' in e['label'])/MM)} MM COP, P(VPN&gt;0) = {pct(next(e['P_pos'] for e in evp if 'residuos' in e['label'] and 'Chocó' in e['label']),0)}.</div><div class="s">MILP + TEA · Figs. 19–20</div></div>
  <div class="finding"><div class="n">1 prensa compartida</div><div class="t">El STN semanal muestra que una prensa de 2 t/h sirve a pulpa y cáscara con limpieza entre materiales. Los cuellos de botella son el pelado, la microfiltración y el secador.</div><div class="s">STN · Fig. 21</div></div>
</div>
<div class="note"><strong>Supuestos.</strong> Los precios de venta, el costo de la fruta (400 COP/kg), los costos de referencia de equipos y los rendimientos de bromelaína y harina son supuestos <span class="tag">[S]</span>, marcados en el código y en los libros Excel (celdas amarillas). Como en sus TEA de asaí y coco, deben reemplazarse por cotizaciones y datos de planta. Las conclusiones de escala y de selección de líneas se mantienen en los barridos. Las cifras absolutas son ilustrativas.</div>
</section>

<section id="moresi">
<h2>Moresi: réplica y aplicación a la piña</h2>
<div class="prose">
<p>Se implementó el modelo completo de Moresi: la estequiometría y la cinética de la ec. 9 con los parámetros de la Tabla 1 (1989a), y los balances dinámicos con carga de refrigeración, arrastre de etanol por CO₂ y el procedimiento de diseño de 11 pasos (1989b). Hubo un único cambio de formulación: el consumo de sustrato y la producción de etanol siguen solo al crecimiento. En la forma original, cuando la muerte celular domina (r_X &lt; 0), el modelo "devolvería" azúcar y etanol.</p>
<h3>Réplica cinética</h3>
<p>Con el inóculo nominal de 0,2 g/L, el tiempo para consumir el 85 % del azúcar sale {n1(nom_c)} h en el sistema cerrado (15 °C) y {n1(nom_o)} h en el abierto (15–22 °C), contra 81 y 79 h publicados. Se calibró un solo parámetro, el inóculo viable efectivo, con el caso cerrado: X₀ = {R1['X0_eff']:.3f} g/L. El caso abierto queda como predicción independiente y da {n1(cal_o)} h, 11 % por encima de lo publicado. El signo del efecto de la temperatura queda invertido: en la Tabla 1, K_S, K_SI y K_E bajan al subir la temperatura, y a 22 °C la inhibición por sustrato frena más al principio. Esto no puede resolverse desde los capítulos, porque los parámetros vienen de las referencias 4 y 7 de Moresi.</p>
<h3>Réplica de costos</h3>
<p>Con los tiempos de fermentación publicados se recuperaron las correlaciones f.o.b. de la Tabla 3. Se reprodujeron los factores de módulo de Guthrie (2,00 / 2,13 / 1,78) y el factor de recuperación de capital al 15 % (10 años para equipos fabricados y 5 para maquinaria). Cada casilla muestra publicado / reproducido:</p>
</div>
{table(['Partida', '30 000 hL (cerrado)', '60 000 hL (abierto)', '120 000 hL (abierto)'], r2rows, num_cols=(1, 2, 3))}
<div class="prose"><p>El número de fermentadores, la depreciación de equipos fabricados, el mantenimiento, el inóculo y la mano de obra coinciden. La única diferencia está en la refrigeración de los sistemas abiertos (+15 a +31 % en la depreciación de maquinaria). Viene de cómo se superponen los picos de enfriamiento de 4 h de fermentadores desfasados; Moresi no detalla ese cálculo.</p></div>
{fig('fig16_moresi_replica.png', 'Réplica cinética y de costos de Moresi', 'Fig. 16. Perfiles de azúcar, etanol y temperatura con la cinética calibrada, y diferencia porcentual de cada partida de costo frente a la Tabla 3.')}
<div class="prose"><h3>Aplicación al jugo de piña</h3></div>
{table(['Política', 'T₀', 't para 85 % (h)', 't para 97,5 % (h)'], p1rows, num_cols=(2, 3))}
<div class="prose">
<p>Con 158,8 g/L, la cinética de Moresi da 64–75 h entre 15 y 22 °C. Por encima de 25 °C el tiempo crece muy rápido, y v_M se vuelve negativo cerca de 28–29 °C. La regresión es de vino blanco (15–25 °C) y no sirve para extrapolar al ensayo de Murcia Palacios a 30 °C (12,5 h). Por eso la tesis compara su línea rápida (dato de Murcia, 30 °C) con su línea premium (cinética de Moresi, 15–22 °C) usando dos modelos que no se pueden poner en la misma escala.</p>
<p><b>Ventaja de la línea premium.</b> La tesis atribuye a la conversión casi completa (99,2 %) un 15,4 % más de etanol por tonelada de azúcar. La descomposición muestra otra cosa: el cociente de etanol es {n1(P3['ratio'])} (+{n1((P3['ratio']-1)*100)} %). Ese cociente se separa en el cociente de rendimientos estequiométricos, Y_E de Moresi a 15 °C = {P3['YE_moresi_15C_gg']:.3f} g/g frente a 0,416 g/g de Murcia (+{n1((P3['ratio_from_yield']-1)*100)} %), y en la conversión ({pct(P3['conv_prem'])} frente a {pct(P3['conv_fast'])}, +{n1((P3['ratio_from_conversion']-1)*100)} %). La línea rápida ya convierte el 98,7 % del azúcar. La ventaja reportada es un efecto del cambio de modelo, no de la línea premium.</p>
<p><b>Diseño de la bodega con el procedimiento de Moresi.</b> En caudal continuo bajo, el llenado de un tanque tarda V_F/Q_M y no las 1,5 h que supone Moresi, así que se corrigió Δt_c. El resultado más fuerte es la diferencia de régimen. La bodega de Moresi opera 28 días de vendimia; la piña puede operar todo el año, y eso divide la inversión de fermentación por un factor de 7,7 a 9,2. En operación continua, el óptimo sin restricción de llenado es un sistema cerrado de 30 m³. Pero tarda unas 29 h en llenarse, justo el riesgo de oxidación que la tesis discute en §4.2.4.</p>
</div>
{table(['Caso', 'Régimen', 'V_F óptimo (m³)', 'N_F', 'Llenado (h)', 'Inversión (miles USD)', 'Costo (USD/m³ de vino)'], p2best, num_cols=(2, 3, 4, 5, 6))}
{fig('fig17_moresi_pina.png', 'Moresi aplicado a la piña', 'Fig. 17. Tiempos de fermentación de piña según la temperatura, con v_M de la Tabla 1 en línea discontinua; descomposición de la ventaja premium; costo de fermentación frente a V_F en régimen continuo y estacional.')}
</section>

<section id="capacidad">
<h2>Materia prima y análisis de capacidad</h2>
<div class="prose">
<p>El balance se arma con las fracciones de la fruta entera: pulpa 45 % (25–55 %), cáscara 30 %, corazón 10 % y corona 15 % <span class="tag">[L]</span>. Se usa el 87 % de rendimiento de jugo y los 158,8 g/L de la tesis. La oferta actual sale del documento regional de la UPRA (EVA 2022): 1 039 ha sembradas, 888 ha cosechadas, 6 146 t y 6,92 t/ha. Eso es un 58 % más que las 3 883 t de 2008 que usa la tesis.</p>
</div>
{table(['Escenario de oferta', 'Fruta (t/año)', 'Vino posible (hL/año)', '% de la base de la tesis', 'Harina (t/año)', 'Bromelaína (kg/año)'], c3rows, num_cols=(1, 2, 3, 4, 5))}
<div class="prose">
<p>A la inversa, la base de diseño de la tesis requiere {n0(C2['central']['fruit_t'])} t/año de fruta y {n0(ch['pulp_t'])} t de pulpa. Para el resto de la planta implica {n0(ch['peel_t'])} t de cáscara, {n0(ch['core_t'])} t de corazón y {n0(ch['crown_t'])} t de corona. Los equipos que fijan la capacidad son:</p>
<ul class="tight">
<li><b>Calendario.</b> Con el escenario 3 de la plantilla (lun–sáb, 2 turnos de 6 h efectivas = {n0(C4['H_b'])} h/año), el frente procesa {n1(C4['fruit_flow_burk_th'])} t/h de fruta, contra {n1(C4['fruit_flow_continuo_th'])} t/h si operara 7 500 h. La UHPH de 10 000 L/h que cita la tesis quedaría al {pct(C4['UHPH_util_burk'], 0)}, y un pasteurizador de 3 000 L/h cubre el caudal.</li>
<li><b>Envejecimiento.</b> 90 días a la producción de diseño exigen {n0(C4['aging_m3'])} m³ de tanques, el equipo más voluminoso de la planta.</li>
<li><b>Vinagre.</b> La acetificación estática (30 d, Roda 2017a) necesita {n0(C4['vinegar_static_m3'])} m³ de trabajo; un acetador sumergido a 50 kg/m³·d necesita {n1(C4['vinegar_acetator_m3'])} m³. Con la regla de Frings para planta piloto (200 L → 20 000 L/año; Bekatorou 2020, p. 93) serían {n1(C4['frings_rule_m3'])} m³.</li>
<li><b>Energía.</b> El secado de la torta de cáscara evapora {n0(ch['water_evap_t'])} t/año de agua y pide {n0(ch['Q_dry_GJ'])} GJ. La gasificación de la corona da {n0(ch['Q_th_GJ'])} GJ de calor recuperable ({pct(ch['heat_cover'], 0)}) y {n1(ch['P_el_kW_7500'])} kWe. Una caldera de biomasa con la misma corona entrega unos {n0(ch['crown_dm_t']*17*0.8)} GJ. El cuello de botella energético es de calor, no de electricidad.</li>
</ul>
</div>
{fig('fig18_capacidad.png', 'Análisis de capacidad', 'Fig. 18. Oferta documentada frente a la fruta que exige la base de la tesis (escala logarítmica); capacidad de vino según la fruta disponible; balance de calor del secado.')}
</section>

<section id="trl9">
<h2>Diseño industrial TRL-9</h2>
<div class="prose"><p>El diseño usa solo tecnologías con planta comercial operando (TRL 9). Cada equipo se dimensiona con el balance y el calendario, y se elige el tamaño de catálogo que cubre la necesidad al menor costo. La UHPH (TRL 8) se cambia por pasteurización flash. La gasificación (TRL 8) queda como alternativa de la caldera de biomasa. La deslignificación e hidrólisis de hojas y corona (TRL 6) y el ácido cítrico o la xantana a partir del hub (TRL 7) quedan fuera del diseño TRL-9.</p></div>
{table(['Tecnología', 'TRL', 'Base'], trl_rows, num_cols=(1,))}
<div class="prose"><p>Lista de equipos a la escala de la tesis ({n0(C2['central']['fruit_t'])} t/año de fruta). Las cantidades y tamaños salen de <code>planta_trl9.py</code>, y los libros Excel traen la misma lista con costos:</p></div>
{table(['Línea', 'Equipo', 'Unidades', 'Tamaño', 'Necesidad', 'TRL'], eqrows, num_cols=(2, 4, 5))}
</section>

<section id="tea">
<h2>TEA por línea (metodología Burk)</h2>
<div class="prose">
<p>Cada línea se evaluó con la misma cadena de sus TEA de asaí (v5.19) y coco (v12):</p>
<ul class="tight">
<li><b>Capital.</b> Costos de equipos por ley de potencia, actualizados con el IPP (182,84) y la TRM, con Fi = 1,3, 10 % de no listados y 5 % de flete. CapEx según Sinnott &amp; Towler: OSBL 0,23 y obra civil 0,15 sobre el ISBL; EPC 0,30 y contingencia 0,20 sobre costos directos.</li>
<li><b>Operación.</b> Nómina colombiana completa (salud 8,5 %, pensión 12 %, cesantías, intereses, prima, vacaciones, CCF, ARL y auxilio de transporte), supervisión 0,6 × mano de obra, mantenimiento 5 %, impuestos y seguros 3 %, y capital de trabajo de 1 mes.</li>
<li><b>Flujo de caja.</b> 10 años, inversión 30/70, primer año al 50 %, depreciación lineal (ET art. 137), renta 35 % con rezago de un año, arrastre de pérdidas sin tope y 95 % del producto vendido.</li>
<li><b>Riesgo.</b> Monte Carlo con hipercubo latino, Beta-PERT λ = 4 y correlación de Iman–Conover (ρ precio–materia prima = 0,45).</li>
</ul>
<p>La fruta se reparte entre las fracciones por masa.</p>
</div>
{table(['Escala', 'Línea', 'FCI (MM COP)', 'VPN (MM COP)', 'MIRR', 'Costo nivelado', 'Precio supuesto', 'Precio de equilibrio', 'P(VPN>0)'], tea_rows, num_cols=(2, 3, 4, 5, 6, 7, 8))}
{fig('fig19_tea_lineas.png', 'TEA por línea', 'Fig. 19. VPN por línea en tres escalas de oferta, y costo nivelado y precio de equilibrio relativos al precio supuesto, a la escala de la tesis.')}
<div class="prose">
<p>A la escala de la tesis, la harina de cáscara (MIRR 20 %), la bromelaína y el vinagre son rentables. El vino a granel a 400 USD/t (1 600 COP/L) no lo es: su precio de equilibrio está cerca de 2 300 COP/L (≈0,57 USD/L). El etanol pierde por escala (≈200 000 L/año) y la gasificación por costo de capital y mano de obra 24/7. El factor Lang equivalente de la plantilla (FCI/compra ≈ 3,1) es menor que el 4,74 de Burk para plantas de fluidos. Es razonable para plantas de alimentos pequeñas, pero conviene declararlo en la tesis.</p>
</div>
{fig('fig22_montecarlo.png', 'Monte Carlo', 'Fig. 22. Distribución del VPN de las líneas rentables y de la planta integrada a la escala de la tesis.', maxw=820)}
</section>

<section id="milp">
<h2>Qué procesar con la producción actual (MILP)</h2>
<div class="prose">
<p>Formulación (Grossmann, <i>Advanced Optimization for PSE</i>):</p>
<ul class="tight">
<li><b>Cargos fijos y tamaños:</b> se modelan con variables 0-1 (cap. 6). Cada línea elige un único tamaño de catálogo, una disyunción cuya envolvente convexa es exacta con variables SOS1 (cap. 7.2 y 10). Así las economías de escala entran sin no linealidades.</li>
<li><b>Lógica entre líneas:</b> se traduce de proposiciones a desigualdades (cap. 7.1). El vinagre requiere vino, el etanol requiere el prensado de cáscara, y el vino, la bromelaína y la harina requieren el frente de pelado.</li>
<li><b>Restricciones mensuales:</b> 12 meses con oferta estacional y fruta perecedera sin inventario entre meses, balances de fracciones, y sustitución de GLP por la caldera y de diésel por el gasificador.</li>
<li><b>Coeficientes:</b> salen del TEA en cada escala. El plan elegido se evalúa después con el TEA completo, con impuestos (enfoque polilítico, Kallrath 2021).</li>
</ul>
<p>Se compararon dos regímenes de abastecimiento: fruta de rechazo comprada entera a 400 COP/kg, o residuos de un procesador existente a 80 COP/kg (el supuesto de §3.3 de la tesis).</p>
</div>
{table(['Escenario', 'Líneas', 'Fruta (t)', 'Pulpa → vino (t)', 'Cáscara → harina (t)', 'Corazón → bromelaína (t)', 'Vino vendido (m³)', 'Vinagre (m³)', 'Harina (t)', 'Bromelaína (kg)', 'Beneficio antes de imp. (MM COP/año)'], plan_rows, num_cols=tuple(range(2, 11)))}
{table(['Régimen', 'Precio del vino (COP/L)', 'Oferta mínima viable (t fruta/año)'], minv, num_cols=(1, 2))}
<div class="prose"><p>Evaluación rigurosa de los planes con el TEA completo y Monte Carlo:</p></div>
{table(['Plan', 'Líneas', 'Escala (t/año)', 'FCI (MM COP)', 'VPN (MM COP)', 'MIRR', 'Recuperación (años)', 'Personas', 'P(VPN>0)'], ev_rows, num_cols=(2, 3, 4, 5, 6, 7, 8))}
{fig('fig20_milp.png', 'MILP de planificación', 'Fig. 20. Beneficio anual del plan óptimo según la oferta de fruta y el precio del vino. Letras: V vino, A vinagre, B bromelaína, H harina, E etanol, C caldera, G gasificador. Derecha: plan mensual del Chocó 2022.')}
<div class="prose">
<p><b>Respuesta para la producción actual (Chocó 2022, 6 146 t).</b> Con fruta comprada a 400 COP/kg y vino a granel a 1 600 COP/L no conviene procesar nada. Con vino a 3 000 COP/L, el óptimo procesa 5 733 t de fruta (93 % de la oferta; los picos de abril, mayo, octubre y noviembre exceden la capacidad elegida). De esa fruta salen unas 2 580 t de pulpa para unos 2 054 m³ de vino y 1 720 t de cáscara para unas 200 t de harina. El corazón y la corona se compostan, porque a esa escala la bromelaína y la caldera no pagan su capital. Si la cáscara viene de un procesador existente, la harina sola es la opción más robusta (P(VPN&gt;0) = 0,94).</p>
<p>La escala mínima viable depende sobre todo del precio del vino y del costo de la materia prima. La base de la tesis solo cierra con vino a 400 USD/t si se procesan unas 22 000 t/año, y esa cantidad no existe hoy en el Chocó.</p>
</div>
</section>

<section id="stn">
<h2>Programación semanal (STN)</h2>
<div class="prose"><p>Se usó el modelo de tiempo discreto de Maravelias (<i>Chemical Production Scheduling</i>, cap. 7.2.2):</p>
<ul class="tight">
<li>ec. 7.4: una tarea a la vez por unidad;</li>
<li>ec. 7.5: tamaño de lote acotado;</li>
<li>ec. 7.6: balance de inventario con capacidad de almacenamiento χ_k.</li>
</ul>
<p>Se agregaron la limpieza al cambiar de material en una unidad compartida (cap. 3) y ventanas de turno. El caso es la semana pico del plan del Chocó: 119 t de fruta con entregas diarias. El almacenamiento es limitado para los perecederos (pulpa 1,5 t, cáscara 3 t, torta 12 t) y hay un tanque pulmón de mosto de 50 m³.</p></div>
{table(['Configuración', 'Estado SCIP', 'Binarias', 'Fruta semana (t)', 'Fruta sin procesar (t)', 'Ocupación por unidad'], stn_rows, num_cols=(2, 3, 4))}
{fig('fig21_stn.png', 'Gantt semanal STN', 'Fig. 21. Programa óptimo con una prensa compartida de 2 t/h e inventarios intermedios. Franjas grises: fuera de turno; solo fermentadores y secador operan de noche.')}
<div class="prose"><p>La prensa compartida evita comprar una segunda prensa. Como el pelado, la microfiltración y el secador quedan al 100 % en la semana pico, cualquier aumento de oferta requiere ampliar esas tres unidades antes que los fermentadores, que se ocupan entre 10 y 30 %.</p></div>
</section>

<section id="excel">
<h2>Libros Excel y verificación</h2>
<div class="prose"><p>Cada caso se exportó a un libro con las hojas de su plantilla: Inicio, Tablero, Modelo del proceso, Costos de Equipos, CapEx, OpEx &amp; Ingresos, Flujo de Caja, Tornado, Break-Even y Monte Carlo. Las celdas amarillas son editables y las cadenas de costos, nómina y flujo de caja tienen fórmulas vivas. Se recalcularon con LibreOffice y se compararon con Python:</p></div>
{table(['Libro', 'VPN Python (MM COP)', 'VPN Excel (MM COP)', 'Diferencia relativa'], x_rows, num_cols=(1, 2, 3))}
</section>

<section id="tesis2">
<h2>Cambios que sugiere a la tesis (versión 2)</h2>
<ol class="edits prose">
<li><b>§4.2.5, tiempo de parada.</b> Los 78–81 h de la Tabla 3 de Moresi no son un "punto de parada de costo mínimo". Son el tiempo para consumir el 85 % del azúcar, el criterio fijo de su paso 2.</li>
<li><b>§4.2.5, intercambiadores.</b> En Moresi, los 4 y 10 intercambiadores sirven a 26 y 69 fermentadores abiertos. La bodega de 5 fermentadores es cerrada, con camisa y sin intercambiador. Hay que corregir "cuatro a diez intercambiadores para cinco a sesenta y nueve fermentadores".</li>
<li><b>§4.2.5, ventaja premium.</b> Reemplazar "+15,4 % de etanol por conversión casi completa" por la descomposición de la Fig. 17: +15,1 % por cambio de modelo y +1,3 % por conversión.</li>
<li><b>§4.2.3 y §4.2.5, validez térmica.</b> Declarar que la cinética de Moresi solo vale entre 15 y 25 °C y no describe la línea rápida a 30 °C.</li>
<li><b>§3.3 y §3.5, base de diseño.</b> Actualizar la oferta con la EVA 2022 (6 146 t) y declarar que la base de 78 300 hL/año exige unas 21 900 t/año de fruta, 3,6 veces la producción del departamento. O se redimensiona la planta, o se justifica el abastecimiento con fruta de fuera del Chocó.</li>
<li><b>Cap. 5, energía.</b> Para un diseño TRL-9, la caldera de biomasa de corona cubre el calor de secado y la gasificación no. Conviene presentar la gasificación como alternativa TRL 8.</li>
<li><b>Cap. 8, TEA.</b> Adoptar la estructura de los TEA de asaí y coco (libros en <code>TEA_excel/</code>) y reportar el precio de equilibrio del vino (≈2 300 COP/L a la escala de la tesis) junto al precio "ilustrativo" de 400 USD/t.</li>
<li><b>Cap. 6 y 9, selección de líneas.</b> Incorporar el MILP con tamaños discretos y el STN semanal como evidencia de qué procesar con la oferta actual y de dónde están los cuellos de botella.</li>
</ol>
</section>

{v1_main}
</main>
"""
open("informe.html", "w").write(html_out)
print("ok", len(html_out))
