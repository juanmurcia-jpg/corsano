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

# ------------------------------------------------------------------------------ v3: estocástico y anual continuo
sto = R("estocastico.json") if os.path.exists("results/estocastico.json") else None
anu = R("anual_continuo.json") if os.path.exists("results/anual_continuo.json") else None
sto_rows = []; front_rows = []; lam_star = float("nan")
if sto:
    sto_rows = [["EV: problema de valor medio (lo que promete)", n0(sto["EV"]["E"] / MM)],
                ["RP: problema estocástico (27 escenarios)", n0(sto["RP"]["E"] / MM)],
                ["EEV: decisión del EV evaluada en los escenarios", n0(sto["EEV"]["E"] / MM)],
                ["WS: esperar y ver (información perfecta)", n0(sto["WS"] / MM)],
                ["VSS = RP − EEV", n0(sto["VSS"] / MM)], ["EVPI = WS − RP", n0(sto["EVPI"] / MM)],
                ["CVaR al 90 % de la solución RP", n0(sto["frontier"][0]["CVaR"] / MM)],
                ["P(beneficio < 0) de la solución RP", pct(sum(sc["p"] for sc, v in zip(sto["scenarios"], sto["RP"]["Pi"]) if v < 0), 0)]]
    for f in sto["frontier"]:
        front_rows.append([str(f["lam"]).replace(".", ","), "+".join(sorted(f["sel"])) or "no construir", n0(f["E"] / MM), n0(f["CVaR"] / MM)])
    E0, C0 = sto["frontier"][0]["E"], sto["frontier"][0]["CVaR"]
    lam_star = E0 / (E0 - C0) if E0 > C0 else float("nan")
    ws_sel = {}
    for w in sto["WS_list"]:
        key = "+".join(sorted(w["sel"])) or "no construir"
        ws_sel[key] = ws_sel.get(key, 0) + w["p"]
    ws_rows = [[E(k), pct(v, 0)] for k, v in sorted(ws_sel.items(), key=lambda x: -x[1])]
anu_rows = []
if anu:
    for k, r in anu.items():
        mx = {u: max(v) for u, v in r["util"].items()}
        bott = ", ".join(f"{u} ({pct(v, 0)})" for u, v in sorted(mx.items(), key=lambda x: -x[1]) if v >= 0.95) or "ninguno ≥ 95 %"
        anu_rows.append([E(k), r["status"], n1(sum(r["loss_month"])), n0(r["changeovers"]), n0(r["products"]["vino_m3"]),
                         n0(r["products"]["harina_t"]), n0(r["products"].get("bromelaina_kg", 0)), bott])

# ------------------------------------------------------------------------------ v4: dimensionamiento óptimo
dim = R("dimensionamiento.json") if os.path.exists("results/dimensionamiento.json") else {}
UN = ["Frente", "Prensa", "Decantadora", "Prensa cáscara", "Pretratamiento cáscara", "Clarificación", "MF lías", "Estabilización", "Bodega", "Secador", "Bodega cáscara", "Enzima cáscara", "Acetificador", "Caldera de corona", "Almacén de mosto",
      "Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás", "Ácido cítrico", "Xantana"]
def sizes_txt(r, units=UN):
    t = "; ".join(f"{u} {r['sizes'][u]}" for u in units if u in r["sizes"] and not (r["sizes"][u] in ("no", "agua") and u in ("Decantadora", "Prensa corazón", "Aspersión", "MF lías", "Bodega cáscara", "Acetificador", "Caldera de corona", "Pretratamiento cáscara", "Enzima cáscara", "Extractora hojas", "Bodega etanol", "Destilación", "Digestor",
                                                                                                        "Motor biogás", "Ácido cítrico", "Xantana")))
    return t + ("; tercer turno" if r.get("turno3") else "")
def bott_txt(sc):
    mx = {u: max(v) for u, v in sc["util"].items()}
    return ", ".join(f"{u} ({pct(v, 0)})" for u, v in sorted(mx.items(), key=lambda x: -x[1]) if v >= 0.95) or "ninguno ≥ 95 %"
def absorbed(sc):
    return 1 - sc["loss"] / sc["supply"]
dim_e1 = [[E(k.split("|")[1]), sizes_txt(r), n0(r["FCI"]), n0(r["obj"]), pct(absorbed(r["scen"][0])), n0(r["scen"][0]["changeovers"]),
           n0(r["scen"][0]["products"]["vino_m3"]), n0(r["scen"][0]["products"]["harina_t"]), bott_txt(r["scen"][0])]
          for k, r in dim.items() if k.startswith("E1|") and r.get("scen")]
dim_e2 = [[n0(r["scen"][0]["supply"]), sizes_txt(r), n0(r["FCI"]), n0(r["obj"]),
           n0(r["FCI"] * 1e6 / r["scen"][0]["products"]["fruta_t"] / 1e3), pct(absorbed(r["scen"][0])), bott_txt(r["scen"][0])]
          for k, r in sorted(((k, r) for k, r in dim.items() if k.startswith("E2|") and r.get("scen")), key=lambda x: float(x[0].split("|")[1]))]
dim_e3 = [[E(k.split("|")[1]), sizes_txt(r), n0(r["FCI"]), n0(r["obj"]), pct(absorbed(r["scen"][0]))]
          for k, r in dim.items() if k.startswith("E3|") and r.get("scen")]
dim_e5 = [[E(k.split("|")[1]), sizes_txt(r, UN + ["Aspersión", "Prensa corazón"]), n0(r["FCI"]), n0(r["obj"]), pct(absorbed(r["scen"][0])),
           n0(r["scen"][0]["products"]["bromelaina_kg"]), bott_txt(r["scen"][0])]
          for k, r in dim.items() if k.startswith("E5|") and r.get("scen")]
dim_e4 = []
if "E4|RP" in dim and "E4|EEV" in dim and "E4|WS" in dim:
    rp, ev, eev, ws = dim["E4|RP"], dim["E4|EV"], dim["E4|EEV"], dim["E4|WS"]
    dim_e4 = [["RP: tamaños elegidos frente a los 3 escenarios de oferta", sizes_txt(rp), n0(rp["obj"])],
              ["EV: tamaños para la oferta media (lo que promete)", sizes_txt(ev), n0(ev["obj"])],
              ["EEV: tamaños del EV operados en los 3 escenarios", sizes_txt(eev), n0(eev["obj"])],
              ["WS: tamaños a medida de cada escenario", " | ".join(f"{w['sup']:g}×: " + sizes_txt(w) for w in ws["each"]), n0(ws["obj"])],
              ["VSS = RP − EEV", "", n0(rp["obj"] - eev["obj"])], ["EVPI = WS − RP", "", n0(ws["obj"] - rp["obj"])]]


def _g(k):
    return dim.get(k) if dim.get(k, {}).get("scen") else None
d_ref, d_sh, d_opt, d_nl = _g("E1|Referencia TRL-9 (planta_trl9, 6 200 t)"), _g("E1|Referencia con prensa única de 3 t/h compartida"), _g("E1|Óptimo económico"), _g("E1|Óptimo sin pérdida de fruta")
d_old, d_noso2 = _g("E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)"), _g("E1|Óptimo sin SO₂")
d_novin = _g("E1|Óptimo sin vinagre")
d_nob = _g("E1|Óptimo sin caldera de corona")
dim6 = R("dimensionamiento_v6.json") if os.path.exists("results/dimensionamiento_v6.json") else {}
v6 = lambda k: dim6.get(k, {}).get("obj") if dim6.get(k, {}).get("scen") else None
dim7 = R("dimensionamiento_v7.json") if os.path.exists("results/dimensionamiento_v7.json") else {}
v7 = lambda k: dim7.get(k, {}).get("obj") if dim7.get(k, {}).get("scen") else None
e6_rows = []
for k in sorted([k for k in dim if k.startswith("E6|") and dim[k].get("scen")], key=lambda k: (float(k.split("|")[2]), float(k.split("|")[1]))):
    r6 = dim[k]; p6 = r6["scen"][0]["products"]; wp6, vp6 = k.split("|")[1:]
    e6_rows.append([n0(float(wp6)), n0(float(vp6)), r6["sizes"].get("Acetificador", "no"), r6["sizes"].get("Bodega cáscara", "no"),
                    n0(p6["vino_m3"] - p6.get("vino_a_vinagre_m3", 0)), n0(p6.get("vino_a_vinagre_m3", 0)), n0(p6.get("jugo_cascara_vinagre_t", 0)),
                    n0(p6.get("vinagre_m3", 0)), n0(r6["obj"])])
e2r = sorted(((float(k.split("|")[1]), r) for k, r in dim.items() if k.startswith("E2|") and r.get("scen")), key=lambda x: x[0])
fx = lambda f: (f"{f:.2f}".rstrip("0").rstrip(".") + "×").replace(".", ",")
t3_at = [fx(f) for f, r in e2r if r["turno3"]]
flot_at = [fx(f) for f, r in e2r if r["sizes"]["Clarificación"].startswith("Flot")]
cent_at = [fx(f) for f, r in e2r if r["sizes"]["Clarificación"].startswith("Centr")]
dec_any = any(r["sizes"]["Decantadora"] != "no" for f, r in e2r) or any(r.get("sizes", {}).get("Decantadora", "no") != "no" for r in dim.values() if isinstance(r, dict) and r.get("sizes"))
mfmust_any = any(r["sizes"]["Clarificación"].startswith("MF") for f, r in e2r)
lees_all = all(r["sizes"]["MF lías"] != "no" for f, r in e2r)
so2_all = all(r["sizes"]["Estabilización"].startswith("SO") for f, r in e2r)
store_any = any(r["sizes"]["Almacén de mosto"] != "10 m³" for f, r in e2r)
e3_same = len({round(r["obj"]) for k, r in dim.items() if k.startswith("E3|") and r.get("scen")}) == 1
import dimensionamiento as dmod
AFv, LANGv, SHIFTv = dmod.AF, dmod.LANG, dmod.shift_cost() / MM
e3d = {k.split("|")[1]: r for k, r in dim.items() if k.startswith("E3|") and r.get("scen")}
e5d = {k.split("|")[1]: r for k, r in dim.items() if k.startswith("E5|") and r.get("scen")}
b0x, b1o, b1x = e5d.get("B referencia (prensas dedicadas TRL-9)"), e5d.get("B óptimo con la topología anterior"), e5d.get("B óptimo económico")


tdim = R("tea_dimensionado.json") if os.path.exists("results/tea_dimensionado.json") else None
# ---- v9: comparación con la v8
cmpv = R("comparativo_v8_v9.json") if os.path.exists("results/comparativo_v8_v9.json") else None
dim8 = R("dimensionamiento_v8.json") if os.path.exists("results/dimensionamiento_v8.json") else {}
v9_par = [["Jugo / cáscara", "0,50 [S]", "0,578", "Campos et al. (2020): extractora industrial, 57,8 % de jugo y 42,2 % de torta"],
          ["Materia seca de la cáscara fresca", "14 %", "17,65 %", "Campos (2020), tabla 1: humedad 82,35 %"],
          ["Materia seca que queda en la torta", "75 % [S]", "41 %", "Campos (2020): torta con 17,03 % de MS; la mayor parte de los sólidos solubles sale con el jugo"],
          ["Harina / t de cáscara", "0,117 t", "0,080 t", "consecuencia de las dos filas anteriores"],
          ["Agua evaporada / t de torta", "0,77 t", "0,81 t", "torta más húmeda: el secador de 100 kg agua/h procesa 1,24 t/h de torta (antes 1,35)"],
          ["Etanol del jugo de cáscara", "0,437 g/g [S]", "0,36 g/g (rango 0,23–0,43)", "Seguí y Fito (2018), tabla 2: fermentación directa con <i>S. bayanus</i>; 0,23 g/g con el licor prensado (tabla 3)"],
          ["Ácido acético / t de jugo de cáscara", "55,7 kg", n1(dmod.A_PJ) + " kg", "104 g/kg de azúcares × 0,36 × 60/46 × 0,94"],
          ["Estabilización del jugo de cáscara", "ninguna", "SO₂, 1 500 COP/t", "Seguí y Fito: sin tratamiento térmico aparecen bacterias acéticas entre 48 y 72 h"]]
v9_opt = [["Pretratamiento de la cáscara", "Agua (extractora) · Ca(OH)₂ al 0,1 % antes de prensar",
           "Seguí y Fito (2018): con cal el licor sube de más del 60 % a 68,4 % de la cáscara (planta piloto neumática, TRL 6)",
           "Jugo 0,65 t/t (68,4 % con 5 % de dilución) y torta 0,316 t/t; 1 kg de cal/t + mezcla (2 900 COP/t); mezclador y dosificador en el FCI"],
          ["Enzima del jugo de cáscara (antes de fermentar)", "No · precipitación con polisacárido + liofilización · UF 10 kDa + liofilización (0,25–1 t/h)",
           "Campos et al. (2020): fracción enzimática del 0,26 % de la cáscara con 17 % de MS, sin solventes (TRL 5). Seguí y Fito (2018): UF 10 kDa, 340–805 GDU/g frente a 1 400–2 800 de la bromelaína de tallo; el permeado fermenta mejor (30 frente a 23,9 g/L de etanol)",
           "0,78 kg de enzima seca/t de jugo; precio " + n0(dmod.BROM_PRICE) + " COP/kg × 1,0 (precipitación) o × 0,5 (UF); 1 % o 5 % del azúcar queda con la enzima; +10 % de etanol en el jugo tratado [S]; un operario por turno; liofilizador en el FCI"]]
tdim_rows, tdim_scale, tdim_chk = [], [], []
if tdim:
    for k, c in tdim["cases"].items():
        r = c["res"]
        tdim_rows.append([E(k), n0(c["fruit_t"]),
                          n0(r["FCI"] / MM), n0(r["revenue"] / MM), n0(r["var"] / MM), n0(r["fixed"] / MM), n0(r["NPV"] / MM), pct(r["MIRR"]),
                          n1(r["payback"]), (n0(c["breakeven"]) if not c.get("breakeven_vinegar") else "—"),
                          (n0(c["breakeven_vinegar"]) if c.get("breakeven_vinegar") else "—"), pct(c["mc"]["P_pos"], 0)])
    for r in tdim["scale"]:
        tdim_scale.append([n0(r["supply"]), sizes_txt(r), n0(r["FCI"] / MM), n0(r["NPV"] / MM),
                           (pct(r["MIRR"]) if r["MIRR"] == r["MIRR"] else "—"), n0(r.get("vinagre_m3", 0)),
                           (n0(r["breakeven_vinegar"]) if r.get("breakeven_vinegar") else "—")])
    tdim_chk = [[E(c["file"]), n0(c["NPV_py"] / MM), n0(c["NPV_xl"] / MM), f"{c['dNPV_rel']:.1e}"] for c in tdim["check"]]
    TA = tdim["cases"]
    tA0, tAo, tA1, tAn, tB0, tBo, tB1 = (TA.get(k) for k in ("A · Referencia TRL-9", "A · Óptimo con la topología anterior", "A · Óptimo con la superestructura ampliada",
                                                            "A · Óptimo sin SO₂", "B · Referencia TRL-9 con bromelaína", "B · Óptimo con la topología anterior",
                                                            "B · Óptimo con la superestructura ampliada"))
    tAv = TA.get("A · Óptimo sin vinagre")
    tAb = TA.get("A · Óptimo sin caldera de corona")
    tdp = tdim.get("prices", [])
    viable =next((r["supply"] for r in tdim["scale"] if r["NPV"] > 0), None)
old_plan = next((e for e in evp if e["lines"] == ["vino", "harina"]), None)


# ---- v9: sección y análisis comparativo (v12: lee su copia de resultados, results/dimensionamiento_v9.json)
_dim_c, _dopt_c = dim, d_opt
if os.path.exists("results/dimensionamiento_v9.json"):
    dim = R("dimensionamiento_v9.json"); d_opt = dim.get("E1|Óptimo económico", d_opt)
t8 = R("tea_dimensionado_v8.json") if os.path.exists("results/tea_dimensionado_v8.json") else None
v9_html = ""
if cmpv and d_opt and dim8:
    dec = cmpv["decomp"]; o8 = dim8["E1|Óptimo económico"]
    g9 = lambda k: dim.get(k, {}).get("obj")
    nov9, nolime, noenz = g9("E1|Óptimo sin opciones v9 (sin cal ni enzima)"), g9("E1|Óptimo sin cal"), g9("E1|Óptimo sin enzima de cáscara")
    var = {v["label"]: v for v in cmpv.get("variants", [])}
    be = cmpv.get("brom_be", {}).get("options", [])
    be_prec = min((x["breakeven"] for x in be if x["breakeven"] and x["option"].startswith("Prec")), default=None)
    e2_9 = sorted(((float(k.split("|")[1]), r) for k, r in dim.items() if k.startswith("E2|") and r.get("scen")), key=lambda x: x[0])
    enz_at = [fx(f) + " (" + r["sizes"]["Enzima cáscara"] + ")" for f, r in e2_9 if r["sizes"].get("Enzima cáscara", "no") != "no"]
    lime_at = [fx(f) for f, r in e2_9 if r["sizes"].get("Pretratamiento cáscara", "agua") != "agua"]
    p8_, p9_ = o8["scen"][0]["products"], d_opt["scen"][0]["products"]
    milp_rows = []
    for k, lab in (("E1|Referencia TRL-9 (planta_trl9, 6 200 t)", "Referencia TRL-9"), ("E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)", "Óptimo con la topología anterior"),
                   ("E1|Óptimo económico", "Óptimo con la superestructura ampliada"), ("E1|Óptimo sin vinagre", "Óptimo sin vinagre"),
                   ("E1|Óptimo sin caldera de corona", "Óptimo sin caldera de corona"), ("E1|Óptimo sin SO₂", "Óptimo sin SO₂"),
                   ("E5|B óptimo económico", "B: con bromelaína de corazón"), ("E4|RP", "Estocástico (RP)")):
        a8, a9 = dim8.get(k, {}), dim.get(k, {})
        if a8.get("obj") is not None and a9.get("obj") is not None:
            milp_rows.append([E(lab), n0(a8["obj"]), n0(a9["obj"]), n0(a9["obj"] - a8["obj"]), pct((a9["obj"] - a8["obj"]) / abs(a8["obj"]), 0),
                              E(sizes_txt(a9)) if a9.get("sizes") != a8.get("sizes") else "igual que en la v8"])
    scale_rows = [[fx(f), n0(dim8.get(k8, {}).get("obj", float("nan"))), n0(r["obj"]), E(sizes_txt(r))]
                  for (f, r), k8 in zip(e2_9, [k for k in sorted((k for k in dim if k.startswith("E2|")), key=lambda k: float(k.split("|")[1]))])]
    tea_rows = [[E(x["label"]), n0(x["NPV8"] / MM), n0(x["NPV9"] / MM), pct(x["MIRR8"]), pct(x["MIRR9"]), pct(x["P8"], 0), pct(x["P9"], 0),
                 (n0(x["BEv8"]) if x.get("BEv8") else "—"), (n0(x["BEv9"]) if x.get("BEv9") else "—")] for x in cmpv.get("tea", [])]
    prod_rows = [[E(x["label"]), n0(x["v8"]), n0(x["v9"]), (pct((x["v9"] - x["v8"]) / x["v8"], 0) if x["v8"] else "nuevo" if x["v9"] else "—")] for x in cmpv.get("prods", [])]
    var_rows = [[E(v["label"]), n0(v["obj"]), n0(v["obj"] - var["Óptimo v9"]["obj"]) if "Óptimo v9" in var else "", n0(v["FCI"]), n0(v["harina_t"]), n0(v["jugo_t"]),
                 n0(v["vino_vendido_m3"]), n0(v["enzima_kg"])] for v in cmpv.get("variants", [])]
    tor = [x for x in (cmpv.get("tornado9") or []) if "cáscara" in x["label"] or "Corona" in x["label"]]
    v9_html = f"""
<h3>Versión 9: Seguí y Fito (2018) y Campos et al. (2020)</h3>
<div class="prose">
<p><b>Qué aportan las dos fuentes.</b> Seguí y Fito (2018, <i>J. Clean. Prod.</i> 172:1224) separan de la cáscara y el corazón industriales un licor por prensado, sacan la enzima por centrífuga, microfiltración y ultrafiltración de 10 kDa, y fermentan el permeado; también miden la fermentación directa, la secuencial y la simultánea con celulasas. Campos et al. (2020, <i>Foods</i> 9:60) procesan por separado cáscara y tallo de una planta portuguesa: extractora, precipitación de la bromelaína con un polisacárido natural, jugo y torta. Las dos fuentes cambian datos que la v8 suponía y abren dos opciones nuevas.</p>
</div>
{table(['Parámetro', 'v8', 'v9', 'Fuente'], v9_par)}
{table(['Etapa nueva', 'Alternativas', 'Base técnica', 'Supuestos [S]'], v9_opt)}
<div class="prose">
<p><b>Qué hacen los datos nuevos con el mismo diseño.</b> Con los tamaños óptimos de la v8 fijos, el margen anual pasa de {n0(dec[0]['obj'])} a {n0(dec[-1]['obj'])} MM COP/año ({n0(dec[-1]['obj'] - dec[0]['obj'])}). El rendimiento de jugo y la torta de Campos restan {n0(dec[0]['obj'] - dec[1]['obj'])}: sale más jugo ({n0(dec[0]['jugo_cascara_t'])} → {n0(dec[1]['jugo_cascara_t'])} t/año), pero la torta lleva menos sólidos y la harina cae de {n0(dec[0]['harina_t'])} a {n0(dec[1]['harina_t'])} t/año. La harina vale 12 000 COP/kg y el jugo que no se acetifica, 150 COP/kg, así que el cambio es una pérdida neta. La fermentación del jugo de cáscara a 0,36 g/g resta otros {n0(dec[1]['obj'] - dec[2]['obj'])}: el acetificador sigue lleno, pero el jugo da menos ácido y hay que desviar más vino ({n0(dec[1]['vino_vendido_m3'] - dec[2]['vino_vendido_m3'])} m³/año menos de vino vendido). El SO₂ del jugo cuesta {n0(dec[2]['obj'] - dec[3]['obj'])}. (El primer valor, {n0(dec[0]['obj'])}, difiere de los {n0(o8['obj'])} reportados en la v8 porque la capacidad del secador se calcula ahora con el agua que realmente evapora la torta.)</p>
<p><b>Qué hacen las opciones nuevas.</b> {('El MILP, con las dos opciones disponibles, se queda en ' + n0(d_opt['obj']) + ' MM COP/año con ' + E(d_opt['sizes'].get('Pretratamiento cáscara', 'agua')) + ' en la cáscara y ' + ('sin separar la enzima' if d_opt['sizes'].get('Enzima cáscara', 'no') == 'no' else 'enzima por ' + E(d_opt['sizes']['Enzima cáscara'])) + '. ') }{('Sin las opciones nuevas, la reoptimización da ' + n0(nov9) + '; ') if nov9 else ''}{('sin cal, ' + n0(nolime) + '; ') if nolime else ''}{('sin enzima, ' + n0(noenz) + '. ') if noenz else ''}{('Impuestas sobre el óptimo: el prensado con cal da ' + n0(var['Prensado con cal']['obj']) + ' (' + n0(var['Prensado con cal']['obj'] - var['Óptimo v9']['obj']) + '), porque la cal saca más jugo a costa de harina, y la harina vale más; la precipitación de 0,5 t/h da ' + n0(var['Enzima por precipitación 0,5 t/h']['obj']) + ' (' + n0(var['Enzima por precipitación 0,5 t/h']['obj'] - var['Óptimo v9']['obj']) + ') con ' + n0(var['Enzima por precipitación 0,5 t/h']['enzima_kg']) + ' kg/año de bromelaína cruda, y la UF de 0,25 t/h da ' + n0(var['Enzima por UF 0,25 t/h']['obj']) + '. ') if 'Óptimo v9' in var and 'Prensado con cal' in var else ''}{('La enzima por precipitación empieza a pagar con la bromelaína cruda a ' + n0(be_prec) + ' COP/kg, ' + pct(be_prec / dmod.BROM_PRICE - 1, 0) + ' por encima del precio central; el liofilizador y el operario pesan más que lo que vale la enzima de unas 1 000 t de jugo al año. ') if be_prec else ''}{('En el barrido de escala, el MILP separa la enzima a ' + ', '.join(enz_at) + '. ') if enz_at else 'En ninguna escala del barrido conviene separar la enzima con los supuestos centrales. '}{('El prensado con cal aparece a ' + ', '.join(lime_at) + '.') if lime_at else 'El prensado con cal no aparece en ninguna escala.'}</p>
</div>
{table(['Variante del óptimo v9 (Chocó 2022)', 'Margen (MM COP/año)', 'Diferencia', 'FCI equipos (MM COP)', 'Harina (t)', 'Jugo de cáscara (t)', 'Vino vendido (m³)', 'Bromelaína (kg)'], var_rows, num_cols=(1, 2, 3, 4, 5, 6, 7)) if var_rows else ''}
<h3>Análisis comparativo entre las versiones 8 y 9</h3>
{fig('fig39_comparativo_v8_v9.png', 'Comparación v8 y v9', 'Fig. 39. Comparación entre las versiones 8 y 9: cascada del margen del óptimo (efecto de cada dato nuevo y de las opciones nuevas), productos del diseño óptimo, VPN y P(VPN > 0) de los casos comparables y tornado del óptimo v9 con las incertidumbres nuevas en ámbar.')}
{table(['Caso del MILP', 'Margen v8', 'Margen v9', 'Diferencia', 'Cambio', 'Tamaños v9'], milp_rows, num_cols=(1, 2, 3, 4))}
{table(['Producto del óptimo (por año)', 'v8', 'v9', 'Cambio'], prod_rows, num_cols=(1, 2, 3))}
{table(['Caso del TEA', 'VPN v8 (MM COP)', 'VPN v9 (MM COP)', 'MIRR v8', 'MIRR v9', 'P(VPN > 0) v8', 'P(VPN > 0) v9', 'Equilibrio del vinagre v8 (COP/L)', 'Equilibrio del vinagre v9 (COP/L)'], tea_rows, num_cols=(1, 2, 3, 4, 5, 6, 7, 8)) if tea_rows else ''}
{table(['Oferta', 'Margen v8 (MM COP/año)', 'Margen v9 (MM COP/año)', 'Tamaños v9'], scale_rows, num_cols=(1, 2)) if scale_rows else ''}
<div class="prose">V9_LECTURA</div>"""
    T9 = {x["label"]: x for x in cmpv.get("tea", [])}
    to = T9.get("Óptimo (superestructura)"); tnv = T9.get("Sin vinagre")
    es_ = cmpv.get("enz_scale", [])
    e8t, e9t = dim8.get("E2|3.556", {}).get("obj"), dim.get("E2|3.556", {}).get("obj")
    trj = next((x for x in (cmpv.get("tornado9") or []) if "cáscara" in x["label"]), None)
    trc = next((x for x in (cmpv.get("tornado9") or []) if "Corona" in x["label"]), None)
    v9_read = "<ul class='tight'>"
    v9_read += (f"<li><b>Los datos nuevos bajan el valor, no cambian el diseño.</b> A la oferta del Chocó, el margen del óptimo baja de {n0(o8['obj'])} a {n0(d_opt['obj'])} MM COP/año ({pct((d_opt['obj'] - o8['obj']) / o8['obj'], 0)}) con los mismos equipos: frente de 3 t/h, dos prensas dedicadas, centrífuga, MF de lías, SO₂, bodega de 2 × 10 m³, acetificador de 10 m³ y caldera de corona de 100 kWt. "
                 + (f"A la escala de la tesis, el margen baja de {n0(e8t)} a {n0(e9t)} ({pct((e9t - e8t) / e8t, 0)}). " if e8t and e9t else "")
                 + "El diseño de la v8 resiste los datos medidos; lo que no resiste es su rentabilidad.</li>")
    if to:
        v9_read += (f"<li><b>El TEA se vuelve frágil.</b> El VPN del óptimo pasa de {n0(to['NPV8'] / MM)} a {n0(to['NPV9'] / MM)} MM COP, la MIRR de {pct(to['MIRR8'])} a {pct(to['MIRR9'])} y P(VPN > 0) de {pct(to['P8'], 0)} a {pct(to['P9'], 0)}. "
                    + (f"Sin vinagre, el VPN queda en {n0(tnv['NPV9'] / MM)} MM COP (P = {pct(tnv['P9'], 0)}): con la harina reducida, el vinagre es el que sostiene el proyecto, y su precio encabeza el tornado. " if tnv else "")
                    + "</li>")
    v9_read += ("<li><b>La harina es la variable que más pesa y la más débil en datos.</b> Casi dos tercios de la caída vienen de que la torta de Campos lleva el 41 % de la materia seca de la cáscara y no el 75 % que suponía la v8. Con harina a 12 000 COP/kg, cada punto de materia seca en la torta vale más que el jugo que libera. Medir la materia seca de la torta con la variedad y la prensa del Chocó y validar el precio de la harina de fibra son ahora las dos primeras tareas de laboratorio y de mercado.</li>")
    if trj:
        v9_read += (f"<li><b>Fermentación del jugo de cáscara.</b> En el tornado, el rango de 0,23 a 0,43 g/g mueve el VPN entre {n0(min(trj['NPV_worst'], trj['NPV_best']) / MM)} y {n0(max(trj['NPV_worst'], trj['NPV_best']) / MM)} MM COP. Un ensayo de fermentación con el jugo real (y SO₂) cierra esta incertidumbre con poco costo."
                    + (f" La corona que llega a planta (40–100 %) pesa menos: el VPN va de {n0(min(trc['NPV_worst'], trc['NPV_best']) / MM)} a {n0(max(trc['NPV_worst'], trc['NPV_best']) / MM)} MM COP, porque si falta corona el GLP la reemplaza." if trc else "") + "</li>")
    v9_read += ("<li><b>Bromelaína: complementaria, pero solo a escala.</b> "
                + (f"Separarla del jugo de cáscara por precipitación conviene desde 2× la oferta y suma entre {n0(min(x['with_enz'] - x['without'] for x in es_))} y {n0(max(x['with_enz'] - x['without'] for x in es_))} MM COP/año (entre {n0(min(x['enz_kg'] for x in es_))} y {n0(max(x['enz_kg'] for x in es_))} kg/año de enzima cruda). " if es_ else "")
                + (f"A la oferta actual necesita un precio de {n0(be_prec)} COP/kg. " if be_prec else "")
                + "La UF con liofilización no conviene en ninguna escala: el producto tiene la mitad de la actividad y hay que liofilizar unas 60 veces más agua por tonelada de jugo. La tesis puede presentar la bromelaína como una etapa que se agrega cuando la planta crece, no como una línea aparte.</li>")
    v9_read += ("<li><b>La cal no conviene mientras la harina valga más que el jugo.</b> El prensado con Ca(OH)₂ saca 18 % más jugo, pero el acetificador ya va lleno y ese jugo extra se vende al hub a 150 COP/kg, mientras la harina que se pierde vale 12 000 COP/kg. Solo se justificaría con un destino de mayor valor para el jugo (por ejemplo, un acetificador más grande con vinagre bien pagado) o con harina mucho más barata.</li>")
    v9_read += "</ul>"
    v9_html = v9_html.replace("V9_LECTURA", v9_read)
dim, d_opt = _dim_c, _dopt_c
# ---- v10: sección nueva (registro de parámetros, hojas, cinética, localización, ACV, social, Pareto, puntos calientes, SuperPro)
import datos as DTm
RJ = lambda f: R(f) if os.path.exists(os.path.join("results", f)) else None
# v11: la sección v10 lee su copia de resultados (results/v10/) y sus figuras (figs/v10/), para no mostrar números de la v11
V10P = lambda f: ("v10/" + f) if os.path.exists(os.path.join("results", "v10", f)) else f
cmp10, acvj, socj, parj, pcj, locj, kinj = (RJ(V10P(f)) for f in ("comparativo_v9_v10.json", "acv.json", "social.json", "pareto.json",
                                                                  "puntos_calientes.json", "localizacion.json", "cinetica_jugos.json"))
dim_cur, d_opt_cur, tdim_cur = dim, d_opt, tdim
dim = RJ(V10P("dimensionamiento.json")) or dim
d_opt = dim.get("E1|Óptimo económico", d_opt)
tdim = RJ(V10P("tea_dimensionado.json")) or tdim
dim9 = RJ("dimensionamiento_v9.json") or {}
v10_html = ""
if d_opt and cmp10:
    reg = DTm.registro()
    grupos = sorted({r_["grupo"] for r_ in reg.values()})
    reg_rows = [[E(g_), n0(sum(1 for r_ in reg.values() if r_["grupo"] == g_))] + [n0(sum(1 for r_ in reg.values() if r_["grupo"] == g_ and r_["etiqueta"].startswith(e_)))
                for e_ in ("T", "C", "L", "S")] for g_ in grupos]
    pv = d_opt["scen"][0]["products"]; sz10 = d_opt["sizes"]
    o9 = dim9.get("E1|Óptimo económico", {})
    dec10 = cmp10.get("decomp", [])
    e7 = [[E(k.split("|")[1]), n0(r_["obj"]), E(sizes_txt(r_)), n0(r_["scen"][0]["products"].get("hojas_t", 0)), n0(r_["scen"][0]["products"].get("vinagre_m3", 0))]
          for k, r_ in dim.items() if k.startswith("E7|") and r_.get("scen")]
    v10_opt = [["Hojas de la planta (segunda materia prima)", "Extractora de tornillo 2–60 t/h · no acopiar",
                "Chen et al. (2020): 125 t de hojas frescas por ha y año; jugo 76 % y pulpa 18 % (Liao et al. 2026)",
                n0(dmod.HOJAS_SUPPLY) + " t/año acopiables (1 039 ha × 125 t/ha × 25 % [S]); acopio " + n0(dmod.ACOPIO_VC) + " COP/t (localización estilizada)"],
               ["Jugo de hojas", "Vinagre (con la bodega de cáscara) · etanol + levadura (K. marxianus) · digestión anaerobia · devolver al campo",
                "Chen et al. (2020): 21,8 kg de etanol y 16 kg de levadura por t de jugo en 12 h; Liao et al. (2026): 17,1 m³ de biogás por t de jugo",
                "etanol " + n0(dmod.ETOH_PRICE) + " COP/L; levadura " + n0(dmod.YEAST_PRICE) + " COP/kg; motor a biogás 35 % eléctrico; excedente a " + n0(dmod.VAL_EXC) + " COP/kWh [S]"],
               ["Pulpa de hojas", "Combustible de la caldera de biomasa · devolver al campo", "Chen et al. (2020): 51,6 % de MS y 19,4 MJ/kg MS",
                n0(dmod.PULP_MJ_T) + " MJ útiles por t de pulpa húmeda"],
               ["Productos del hub", "Ácido cítrico 5–100 kg/h · goma xantana 2–25 kg/h", "Ejemplos de SuperPro (Petrides): 18 000 t/año de cítrico y 5 000 t/año de xantana",
                "inversión escalada con exponente 0,6 desde el ejemplo; precios 2 y 9 USD/kg [S]"],
               ["Mezcla del vinagre (corrección)", "El acetificador solo diluye", "Vinagre al 5 %: el jugo de cáscara (46 kg/m³) y el de hojas (27 kg/m³) necesitan vino (80 kg/m³) para llegar",
                "restricción lineal: vino + jugos ≤ ácido / 50"]]
    kin_rows = ([[E("Jugo de cáscara"), n1(kinj["cascara"]["t95_h"]), n1(kinj["cascara"]["t95_calibrado_h"]), n1(kinj["cascara"]["t_proc_h"]), "32,5 (v9, supuesto)",
                  pct(kinj["cascara"]["Y_modelo"], 0) + " → " + pct(kinj["cascara"]["Y_medido"], 0)],
                 [E("Jugo de hojas"), n1(kinj["hojas"]["t95_h"]), n1(kinj["hojas"]["t95_calibrado_h"]), "14,5 (medido)", "12 + 2,5 (Chen 2020)",
                  pct(kinj["hojas"]["Y_modelo"], 0) + " → " + pct(kinj["hojas"]["Y_medido"], 0)]] if kinj else [])
    loc_rows = [[E(k), n0(v / locj["hojas_t"])] for k, v in locj["alternativas"].items()] if locj else []
    acv_rows = []
    if acvj:
        for lab_, a_ in acvj.items():
            acv_rows.append([E(lab_), n0(a_["gwp_total"] / 1000), n0(a_["per_t_fruta"]), n0(a_["net_vs_descomposicion"] / 1000), n0(a_["net_vs_quema"] / 1000),
                             n0(a_["net_con_expansion"] / 1000), n1(a_["fossil_MJ"] / 1e6), n0(a_["water_m3"] or 0)])
    soc_rows = [[E(k), n0(v["empleos_planta"]), n0(v["empleos_acopio"]), n1(v["empleos_por_1000t_fruta"]), n0(v["pago_fruta"] / MM), n0(v["pago_acopio_hojas"] / MM),
                 n0(v["nomina_local"] / MM), n0(v["valor_territorio"] / MM)] for k, v in (socj or {}).items()]
    pc_rows = [[E(k), pct(v["frac_capital"], 0), pct(v["frac_elec_kWh"], 0), pct(v["frac_calor_MJ"], 0), pct(v["frac_gwp_kg"], 0), pct(v["frac_ingreso"], 0),
                E(", ".join({"capital": "capital", "elec_kWh": "electricidad", "calor_MJ": "calor", "gwp_kg": "GWP"}.get(x_, x_) for x_ in v["punto_caliente"]) or "—")] for k, v in (pcj or {}).items() if any(v[f"frac_{x}"] > 0.005 for x in ("capital", "elec_kWh", "calor_MJ", "gwp_kg", "ingreso"))]
    par_rows = [[n0(pt_["gwp"] / 1000), n0(pt_["margin"]), E(sizes_txt(pt_))] for pt_ in sorted((parj or {}).get("points", []), key=lambda z: z["gwp"])]
    T10 = {x["label"]: x for x in cmp10.get("tea", [])}
    tea10_rows = [[E(x["label"]), n0(x["NPV9"] / MM), n0(x["NPV10"] / MM), pct(x["MIRR9"]), pct(x["MIRR10"]), pct(x["P9"], 0), pct(x["P10"], 0)] for x in cmp10.get("tea", [])]
    prod10_rows = [[E(x["label"]), n0(x["v9"]), n0(x["v10"])] for x in cmp10.get("prods", [])]
    v10_html = f"""
<h3>Versión 10: marco de tres etapas, residuos de planta y evaluación de sostenibilidad</h3>
<div class="prose">
<p><b>De dónde sale.</b> El capítulo de Bertran, Tula y Gani (2022) ordena la síntesis, el diseño y la innovación de biorrefinerías en tres etapas y pide, para llamar sostenible a un diseño, evaluación ambiental y social y verificación con simulador. Heinzle et al. (2006) da el método de evaluación; Chen et al. (2020) y Liao et al. (2022, 2026) traen una materia prima que la tesis no consideraba: las hojas que quedan en el campo cuando se renueva el cultivo. El plan de mejora se aplicó completo; lo que depende de datos de campo del Bajo Atrato quedó con supuestos marcados [S].</p>
<p><b>Registro único de parámetros.</b> Todos los datos de la versión 10 viven en <code>datos/parametros.csv</code>, con valor, rango, distribución, unidad, etiqueta de procedencia y fuente; <code>python datos.py check</code> verifica que las constantes de los módulos anteriores coincidan con el registro (0 diferencias).</p>
</div>
{table(['Grupo', 'Parámetros', '[T]', '[C]', '[L]', '[S]'], reg_rows, num_cols=(1, 2, 3, 4, 5))}
{table(['Etapa nueva', 'Alternativas', 'Base técnica', 'Supuestos'], v10_opt)}
<div class="prose"><p><b>Cinética acoplada.</b> El tiempo de proceso de la bodega de jugo de cáscara ya no es un supuesto: sale de la cinética de Krishnan et al. (1999) para glucosa y xilosa, calibrada en tiempo con el dato medido del jugo de pulpa (65,3 g/L de etanol en 12,5 h, Murcia Palacios 2013) y en rendimiento con Seguí y Fito (2018). Para el jugo de hojas se usa el tiempo medido por Chen et al. (2020) con <i>K. marxianus</i>, porque el modelo, de una cepa de <i>S. cerevisiae</i>, fermenta la xilosa mucho más despacio.</p></div>
{table(['Jugo', 'Tiempo al 95 % del modelo (h)', 'Calibrado (h)', 'Tiempo de proceso usado (h)', 'Antes', 'Rendimiento: modelo → medido'], kin_rows) if kin_rows else ''}
{fig(('v10/' if os.path.exists('figs/v10/fig41_cinetica_jugos.png') else '') + 'fig41_cinetica_jugos.png', 'Cinética de jugos', 'Fig. 41. Cinética de Krishnan et al. (1999) para los jugos de cáscara y de hojas y sensibilidad del tiempo de fermentación al azúcar inicial y al inóculo.') if kinj else ''}
<div class="prose"><p><b>Localización estilizada.</b> Un MILP pequeño compara una planta central que recibe hojas frescas con depósitos de extracción en las zonas de cultivo que envían solo el jugo (Bertran et al. 2022, sec. 5.1; Liao et al. 2026). Las cuatro zonas, sus áreas y las distancias son marcadores de posición [S] hasta tener la ubicación de las fincas. Con ellos gana la planta central en el sitio con vía: {n0(locj['costo_t']) if locj else '—'} COP por tonelada de hojas puesta en planta, que es el costo de acopio que usa el dimensionamiento. Los depósitos no se pagan: ahorran solo el 24 % del flete (la pulpa se queda en la zona) y cada uno necesita equipo y un operario por turno.</p></div>
{table(['Configuración', 'Costo de acopio (COP/t de hojas)'], loc_rows, num_cols=(1,)) if loc_rows else ''}
{fig(('v10/' if os.path.exists('figs/v10/fig42_localizacion.png') else '') + 'fig42_localizacion.png', 'Localización', 'Fig. 42. Localización estilizada: costo de acopio por configuración y zonas supuestas.') if locj else ''}
<div class="prose">V10_RESULTADOS</div>
{table(['Sensibilidad de las hojas (E7)', 'Margen (MM COP/año)', 'Tamaños', 'Hojas acopiadas (t)', 'Vinagre (m³)'], e7, num_cols=(1, 3, 4)) if e7 else ''}
<h3>Evaluación ambiental: ciclo de vida de la cuna a la puerta</h3>
<div class="prose"><p>Unidad funcional: un año de operación (y 1 t de fruta procesada). Inventario desde el balance del dimensionamiento con los mismos coeficientes del MILP; GWP100 de IPCC AR6; electricidad del grupo diésel de la zona no interconectada; caldera de biomasa con CH₄ y N₂O de IPCC 2006; compostaje de las fracciones sin uso. Línea base sin planta: la fruta de rechazo se descompone en campo y las hojas acopiadas se queman (Liao et al. 2026) o se descomponen. La expansión del sistema (etanol por gasolina, excedente eléctrico por diésel) se reporta aparte.</p></div>
{table(['Caso', 'GWP de proceso (t CO2e/año)', 'kg CO2e por t de fruta', 'Neto frente a descomposición (t)', 'Neto frente a quema de hojas (t)', 'Neto con expansión del sistema (t)', 'Energía fósil (TJ/año)', 'Agua (m³/año)'], acv_rows, num_cols=(1, 2, 3, 4, 5, 6, 7)) if acv_rows else ''}
{fig(('v10/' if os.path.exists('figs/v10/fig40_acv.png') else '') + 'fig40_acv.png', 'ACV', 'Fig. 40. GWP de proceso por contribución, neto frente a la línea base y huella por producto del óptimo v10 (asignación económica).') if acvj else ''}
<div class="prose">V10_ACV</div>
<h3>Indicadores sociales</h3>
{table(['Caso', 'Empleos en planta', 'Empleos en acopio', 'Empleos por 1 000 t de fruta', 'Pago por fruta (MM COP/año)', 'Pago por acopio de hojas', 'Nómina local', 'Valor que queda en el territorio'], soc_rows, num_cols=(1, 2, 3, 4, 5, 6, 7)) if soc_rows else ''}
<div class="prose">V10_SOCIAL</div>
<h3>Frente de Pareto margen–GWP</h3>
{fig(('v10/' if os.path.exists('figs/v10/fig43_pareto.png') else '') + 'fig43_pareto.png', 'Pareto', 'Fig. 43. Frente de Pareto margen–GWP por ε-restricción sobre el MILP de dimensionamiento.') if parj else ''}
{table(['GWP de proceso (t CO2e/año)', 'Margen (MM COP/año)', 'Diseño'], par_rows, num_cols=(0, 1)) if par_rows else ''}
<div class="prose">V10_PARETO</div>
<h3>Etapa 3: puntos calientes y objetivos de mejora</h3>
{table(['Sección', 'Cargo de capital', 'Electricidad', 'Calor', 'GWP', 'Ingresos', 'Punto caliente en'], pc_rows) if pc_rows else ''}
{fig(('v10/' if os.path.exists('figs/v10/fig44_puntos_calientes.png') else '') + 'fig44_puntos_calientes.png', 'Puntos calientes', 'Fig. 44. Participación de cada sección en el costo de capital, la energía, el GWP y los ingresos del óptimo v10.') if pcj else ''}
<div class="prose">V10_PC</div>
<h3>Verificación con SuperPro</h3>
<div class="prose"><p>SuperPro Designer no corre en el entorno de los modelos. <code>superpro_paquete.py</code> deja en <code>superpro/</code> los procedimientos unitarios con su modo, tamaño, ciclo y especificación (<code>procedimientos.csv</code>), las corrientes anuales que el modelo de SuperPro debe reproducir (<code>corrientes.csv</code>), los indicadores a comparar con su tolerancia (<code>verificacion.csv</code>) y las instrucciones de armado (<code>LEEME.md</code>), siguiendo a Foo (2023, caps. 10 y 11). Con los resultados de SuperPro se llena la columna vacía y se corrigen los coeficientes del registro que se salgan de la tolerancia.</p></div>
<h3>Análisis comparativo entre las versiones 9 y 10</h3>
{fig(('v10/' if os.path.exists('figs/v10/fig45_comparativo_v9_v10.png') else '') + 'fig45_comparativo_v9_v10.png', 'Comparación v9 y v10', 'Fig. 45. De la v9 a la v10: cascada del margen, margen según la oferta, VPN de los casos comparables y tornado del óptimo v10.')}
{table(['Producto del óptimo (por año)', 'v9', 'v10'], prod10_rows, num_cols=(1, 2))}
{table(['Caso del TEA', 'VPN v9 (MM COP)', 'VPN v10 (MM COP)', 'MIRR v9', 'MIRR v10', 'P(VPN > 0) v9', 'P(VPN > 0) v10'], tea10_rows, num_cols=(1, 2, 3, 4, 5, 6)) if tea10_rows else ''}
<div class="prose">V10_LECTURA</div>"""
    # ---- textos de la v10 (se llenan con los resultados)
    g10 = lambda k: dim.get(k, {}).get("obj")
    nov10 = g10("E1|Óptimo sin opciones v10 (sin hojas ni hub)")
    U10 = d_opt["scen"][0]["util"]
    ue = U10.get("Extractora hojas", [0])
    pv9 = o9.get("scen", [{}])[0].get("products", {}) if o9 else {}
    tO = T10.get("Óptimo"); tNV = T10.get("Sin vinagre")
    case10 = (tdim or {}).get("cases", {}).get("A · Óptimo con la superestructura ampliada", {})
    be10 = case10.get("breakeven_vinegar")
    tor10 = cmp10.get("tornado10", [])
    tv = next((x for x in tor10 if "vinagre" in x["label"]), None)
    tac = next((x for x in tor10 if "acopio" in x["label"]), None)
    e7d = {k.split("|")[1]: r_ for k, r_ in dim.items() if k.startswith("E7|") and r_.get("scen")}
    sc10 = cmp10.get("scale", [])
    ext_sc = ", ".join(f"{fx(s_['f'])}: {s_['sizes10'].get('Extractora hojas')}" for s_ in sc10 if s_["sizes10"].get("Extractora hojas", "no") != "no")
    r_txt = (f"<p><b>Qué hace la v10 con el diseño de la v9.</b> Con los equipos de la v9 fijos, el margen pasa de {n0(dec10[0]['obj'])} a {n0(dec10[1]['obj'])} MM COP/año "
             f"al tomar el tiempo de la bodega de jugo de cáscara de la cinética calibrada ({n1(dmod.T_PEEL)} h en lugar de 32,5 h) y los costos del registro. "
             f"La restricción de mezcla del vinagre no lo cambia ({n0(dec10[2]['obj'])}): el diseño de la v9 ya la cumplía. Sin las opciones nuevas, la reoptimización se queda en {n0(nov10)}.</p>"
             if len(dec10) >= 3 and nov10 else "")
    r_txt += (f"<p><b>El óptimo v10.</b> El margen sube a {n0(d_opt['obj'])} MM COP/año ({'+' + n0(d_opt['obj'] - nov10) if nov10 else ''} sobre la reoptimización sin opciones nuevas) con "
              f"{n0(pv.get('hojas_t', 0))} t/año de hojas acopiadas, el {pct(pv.get('hojas_t', 0) / dmod.HOJAS_SUPPLY, 0)} de lo acopiable, en una extractora de {sz10.get('Extractora hojas')} "
              f"que trabaja entre el {pct(min(ue), 0)} y el {pct(max(ue), 0)} de su capacidad. Las {n0(pv.get('jugo_hojas_vinagre_t', 0))} t/año de jugo de hojas fermentan con el de cáscara "
              f"en una bodega de {sz10.get('Bodega cáscara')} y pasan a un acetificador de {sz10.get('Acetificador')} (10 m³ en la v9). Como el jugo de hojas da un vino de solo 27 kg/m³ de ácido "
              f"potencial y el vinagre debe llegar al 5 %, necesita vino de piña para la mezcla: todo el vino ({n0(pv.get('vino_a_vinagre_m3', 0))} m³/año) va al acetificador y ya no se vende vino. "
              f"El vinagre sube de {n0(pv9.get('vinagre_m3', 0))} a {n0(pv.get('vinagre_m3', 0))} m³/año. La pulpa de hojas vuelve al campo, porque la caldera de corona ya cubre todo el calor.</p>")
    r_txt += ("<p><b>Lo que limita el acopio es la mezcla, no la oferta de hojas.</b> "
              + (f"Con el 10 % o el 50 % del área renovada como fuente, el margen no cambia ({n0(e7d['fracción de acopio 0,10']['obj'])} y {n0(e7d['fracción de acopio 0,50']['obj'])}); "
                 if 'fracción de acopio 0,10' in e7d and 'fracción de acopio 0,50' in e7d else "")
              + (f"con acopio a 80 000 COP/t baja a {n0(e7d['costo de acopio 80 000 COP/t']['obj'])}. " if 'costo de acopio 80 000 COP/t' in e7d else "")
              + "(Las corridas de sensibilidad no se pulieron con tamaños vecinos y quedan unos 100 MM COP/año por debajo del óptimo pulido; se comparan entre sí.) "
              + "Cada tonelada de jugo de hojas necesita vino para llegar al 5 %, y el vino es el que limita. Etanol con levadura, digestión anaerobia y los productos del hub no se eligen, "
              + "ni en el óptimo ni en ninguna escala del barrido: el etanol paga la destilación con calor y la electricidad del grupo diésel; el biogás solo reemplaza diésel hasta la demanda de la planta, "
              + "porque en la zona no interconectada no hay a quién vender el excedente; y el cítrico y la xantana, escalados desde plantas de 18 000 y 5 000 t/año, tienen una inversión que el volumen de jugo no paga. "
              + (f"Quitar el etanol o el digestor deja el margen igual ({n0(g10('E1|Óptimo sin etanol de hojas'))} y {n0(g10('E1|Óptimo sin digestor'))}).</p>" if g10('E1|Óptimo sin digestor') else "</p>"))
    if ext_sc:
        r_txt += f"<p><b>Escala.</b> La extractora crece con la oferta ({ext_sc} la oferta actual) y el acetificador llega a 40 m³ desde 2×. El margen de la v10 supera al de la v9 en todas las escalas.</p>"
    if tO:
        r_txt += (f"<p><b>TEA.</b> El VPN del óptimo pasa de {n0(tO['NPV9'] / MM)} a {n0(tO['NPV10'] / MM)} MM COP, la MIRR de {pct(tO['MIRR9'])} a {pct(tO['MIRR10'])} y P(VPN > 0) de "
                  f"{pct(tO['P9'], 0)} a {pct(tO['P10'], 0)}, con {n0((tO['FCI10'] - tO['FCI9']) / MM)} MM COP más de FCI. "
                  + (f"El precio de equilibrio del vinagre es {n0(be10)} COP/L, un {pct(1 - be10 / dmod.VIN_PRICE, 0)} por debajo del precio central de {n0(dmod.VIN_PRICE)} COP/L. " if be10 else "")
                  + (f"En el tornado, el precio del vinagre mueve el VPN de {n0(min(tv['NPV_worst'], tv['NPV_best']) / MM)} a {n0(max(tv['NPV_worst'], tv['NPV_best']) / MM)} MM COP" if tv else "")
                  + (f"; el costo de acopio de hojas, solo de {n0(min(tac['NPV_worst'], tac['NPV_best']) / MM)} a {n0(max(tac['NPV_worst'], tac['NPV_best']) / MM)}. " if tac else ". ")
                  + f"Son {n1(pv.get('vinagre_m3', 0) / 1000)} millones de litros de vinagre al 5 % por año: antes de tomar este diseño como base, hay que contrastar ese volumen y ese precio con el mercado de vinagre a granel.</p>")
    r_txt += ("<p><b>Calidad de las soluciones.</b> El MILP de la v10 es más grande (hojas, inventario de hojas, balance eléctrico mensual) y SCIP no cierra la brecha en el tiempo dado: "
              f"el óptimo económico tiene una brecha nominal de {pct(d_opt.get('gap') or 0, 0)} frente a la cota dual. La solución se mejoró con arranque en caliente y con un pulido que prueba los tamaños vecinos "
              "de cada equipo con el diseño fijo; ningún vecino mejora el margen. La brecha refleja sobre todo una cota dual débil, pero no prueba optimalidad.</p>")
    a10 = (acvj or {}).get("Óptimo v10"); a9 = (acvj or {}).get("Diseño v9"); anv = (acvj or {}).get("Óptimo sin vinagre"); anc = (acvj or {}).get("Óptimo sin caldera")
    acv_txt = ""
    if a10 and a9:
        acv_txt = (f"<p><b>Lectura.</b> El GWP de proceso del óptimo v10 es de {n0(a10['gwp_total'] / 1000)} t CO2e/año ({n0(a10['per_t_fruta'])} kg por t de fruta), frente a "
                   f"{n0(a9['gwp_total'] / 1000)} t del diseño v9. La diferencia es casi toda electricidad diésel: el acetificador de 20 m³ y sus chillers suben la demanda de "
                   f"{n0(a9['e_dem_kWh'] / 1000)} a {n0(a10['e_dem_kWh'] / 1000)} MWh/año, y el acopio suma el transporte de las hojas. "
                   + (f"Sin vinagre el GWP baja a {n0(anv['gwp_total'] / 1000)} t; sin caldera de corona sube a {n0(anc['gwp_total'] / 1000)} t por el GLP. " if anv and anc else "")
                   + f"Frente a la línea base sin planta, en la que la fruta de rechazo y las hojas se descomponen en el campo, el óptimo v10 evita {n0(-a10['net_vs_descomposicion'] / 1000)} t CO2e/año netas "
                   f"(la v9, {n0(-a9['net_vs_descomposicion'] / 1000)}); si las hojas se quemaran en campo, el ahorro neto sería de {n0(-a10['net_vs_quema'] / 1000)} t y se evitarían {n0(a10['pm_evitado_kg'])} kg/año de material particulado. "
                   "La electricidad es el objetivo de mejora ambiental más claro: en el Bajo Atrato cada kWh sale de diésel a 0,97 kg CO2e. Los factores de emisión son genéricos (IPCC, ecoinvent como referencia) y el inventario no incluye la construcción de la planta.</p>")
    s10 = (socj or {}).get("Óptimo v10"); s9 = (socj or {}).get("Diseño v9")
    soc_txt = ""
    if s10 and s9:
        soc_txt = (f"<p><b>Lectura.</b> El óptimo v10 emplea {n0(s10['empleos_planta'])} personas en planta y unas {n0(s10['empleos_acopio'])} en el acopio de hojas. El valor que queda en el territorio "
                   f"sube de {n0(s9['valor_territorio'] / MM)} a {n0(s10['valor_territorio'] / MM)} MM COP/año ({n0(s10['valor_territorio_por_t'] / 1000)} mil COP por t de fruta): "
                   f"{n0(s10['pago_acopio_hojas'] / MM)} MM COP por el servicio de acopio de hojas y más compras locales. El pago por la fruta de rechazo ({n0(s10['pago_fruta'] / MM)} MM COP/año) "
                   f"es el {pct(s10['pago_fruta'] / s10['valor_territorio'], 0)} de ese valor: el precio que la planta paga a los productores es la palanca social más grande, y también la segunda variable del tornado. "
                   "Las fracciones de nómina y compras locales y las toneladas de hojas por empleo son supuestos [S] que hay que contrastar con la estructura productiva de la zona.</p>")
    par_txt = ""
    P_ = sorted((parj or {}).get("points", []), key=lambda z: z["gwp"])
    if len(P_) >= 2:
        hi_, lo_ = P_[-1], P_[0]
        mid = [p_ for p_ in P_[1:-1]]
        par_txt = (f"<p><b>Lectura.</b> En el extremo económico, el diseño da {n0(hi_['margin'])} MM COP/año con {n0(hi_['gwp'] / 1000)} t CO2e/año de GWP de proceso. "
                   + (" ".join(f"Con un tope de {n0(p_['eps'] / 1000)} t, el mejor diseño da {n0(p_['margin'])} MM COP/año ({'con' if p_['sizes'].get('Extractora hojas', 'no') != 'no' else 'sin'} extractora de hojas, {('acetificador de ' + p_['sizes']['Acetificador']) if p_['sizes'].get('Acetificador', 'no') != 'no' else 'sin vinagre'})." for p_ in mid[::-1] if p_.get('eps')) + " ")
                   + f"El extremo ambiental ({n0(lo_['gwp'] / 1000)} t, {n0(lo_['margin'])} MM COP/año) es casi no procesar: el GWP de proceso solo mide lo que la planta emite y no lo que evita "
                   "frente a dejar la fruta y las hojas en el campo. El frente muestra que, con electricidad diésel, cada tonelada de CO2e de proceso que se recorta cuesta margen, sobre todo al quitar el vinagre; "
                   "la versión siguiente debería optimizar el GWP neto frente a la línea base, que premia procesar. Los puntos intermedios salen de corridas con límite de tiempo y pulido local: el frente es una aproximación.</p>")
    pc_txt = ""
    if pcj:
        V_ = pcj.get("Vinagre", {}); C_ = pcj.get("Cáscara y harina", {}); Hh = pcj.get("Hojas (extracción, etanol, biogás)", {})
        pc_txt = (f"<p><b>Lectura.</b> El vinagre concentra el {pct(V_.get('frac_capital', 0), 0)} del cargo de capital, el {pct(V_.get('frac_elec_kWh', 0), 0)} de la electricidad y el "
                  f"{pct(V_.get('frac_gwp_kg', 0), 0)} del GWP, pero también el {pct(V_.get('frac_ingreso', 0), 0)} de los ingresos, así que la regla no lo marca. "
                  f"La cáscara y la harina se llevan el {pct(C_.get('frac_calor_MJ', 0), 0)} del calor con el {pct(C_.get('frac_ingreso', 0), 0)} de los ingresos; ese calor ya sale de la corona. "
                  f"Las hojas pesan el {pct(Hh.get('frac_gwp_kg', 0), 0)} del GWP (transporte del acopio y electricidad de la extractora) y no muestran ingresos propios porque su jugo se vende como vinagre. "
                  "El frente, la pulpa y la bodega de vino tampoco muestran ingresos: en el óptimo v10 todo el vino va al vinagre. La regla trata cada sección como si vendiera su propio producto; "
                  "para las secciones aguas arriba hay que leerla con el ingreso del producto final. "
                  "Objetivos de mejora para la etapa 3: (1) electricidad del vinagre (aireación y frío) con solar fotovoltaica o biogás, que bajaría el GWP y el costo; "
                  "(2) logística del acopio de hojas, con datos reales de fincas y distancias; (3) mercado y precio del vinagre, que sostienen el resultado.</p>")
    lect10 = "<ul class='tight'>"
    if len(dec10) >= 3 and nov10:
        lect10 += (f"<li><b>Las correcciones del modelo cambian poco.</b> La cinética calibrada y el registro restan {n0(dec10[0]['obj'] - dec10[1]['obj'])} MM COP/año al diseño v9; la restricción de mezcla, nada. "
                   f"La v9 reoptimizada con los datos de la v10 da {n0(nov10)}.</li>")
        lect10 += (f"<li><b>Las hojas cambian el diseño.</b> Suman {n0(d_opt['obj'] - nov10)} MM COP/año: extractora de {sz10.get('Extractora hojas')}, bodega de jugos de {sz10.get('Bodega cáscara')} "
                   f"y acetificador de {sz10.get('Acetificador')}. La planta deja de vender vino: el vino se usa para llevar el jugo de hojas al 5 %.</li>")
    if tO:
        lect10 += (f"<li><b>Más rentable, con el riesgo más concentrado.</b> VPN de {n0(tO['NPV9'] / MM)} a {n0(tO['NPV10'] / MM)} MM COP y P(VPN > 0) de {pct(tO['P9'], 0)} a {pct(tO['P10'], 0)}. "
                   + (f"Sin vinagre, el VPN es {n0(tNV['NPV10'] / MM)} MM COP (P = {pct(tNV['P10'], 0)}). " if tNV else "")
                   + (f"El vinagre aporta el {pct((pcj or {}).get('Vinagre', {}).get('frac_ingreso', 0), 0)} de los ingresos; " if pcj else "")
                   + "el estudio de mercado del vinagre a granel es ahora la tarea más importante para la tesis.</li>")
    if a10 and a9:
        lect10 += (f"<li><b>Ambiental: más emisiones de proceso, más emisiones evitadas.</b> El GWP de proceso sube de {n0(a9['gwp_total'] / 1000)} a {n0(a10['gwp_total'] / 1000)} t CO2e/año por la electricidad diésel, "
                   f"pero el ahorro neto frente a dejar fruta y hojas en el campo sube de {n0(-a9['net_vs_descomposicion'] / 1000)} a {n0(-a10['net_vs_descomposicion'] / 1000)} t.</li>")
    if s10 and s9:
        lect10 += f"<li><b>Social.</b> {n0(s10['empleos_acopio'])} empleos más en el acopio y {n0((s10['valor_territorio'] - s9['valor_territorio']) / MM)} MM COP/año más en el territorio.</li>"
    lect10 += ("<li><b>Lo que la v10 descarta con datos.</b> Etanol de hojas, digestión anaerobia, ácido cítrico y xantana no entran en ninguna escala. Volverían a la mesa con conexión a la red "
               "(venta de excedentes), calor más barato para destilar o una escala de hub regional.</li>")
    lect10 += ("<li><b>Supuestos que más pesan [S].</b> La oferta de hojas (25 % del área renovada, 125 t/ha), el costo de acopio de la localización estilizada (zonas y distancias de marcador), "
               "las fracciones locales del indicador social y el precio del vinagre. La verificación en SuperPro (paquete en <code>superpro/</code>) queda pendiente de la corrida con licencia.</li>")
    lect10 += "</ul>"
    v10_html = (v10_html.replace("V10_RESULTADOS", r_txt).replace("V10_ACV", acv_txt).replace("V10_SOCIAL", soc_txt)
                .replace("V10_PARETO", par_txt).replace("V10_PC", pc_txt).replace("V10_LECTURA", lect10))
    v10_html = v10_html  # (fin de la sección v10)
dim, d_opt, tdim = dim_cur, d_opt_cur, tdim_cur
# ---- v11: panela añadida, demanda de vinagre, xantana con residuo de piña y efluentes (Ebrahimi 2026; Ahamed y Li 2026; Iakovchenko 2026)
cmp11 = RJ("comparativo_v10_v11.json")
V11P = lambda f: ("v11/" + f) if os.path.exists(os.path.join("results", "v11", f)) else f   # v12: la sección v11 lee su copia
acv11, soc11, par11, pc11 = (RJ(V11P(f)) for f in ("acv.json", "social.json", "pareto.json", "puntos_calientes.json"))
dim_cur, d_opt_cur, tdim_cur = dim, d_opt, tdim
dim = RJ(V11P("dimensionamiento.json")) or dim
d_opt = dim.get("E1|Óptimo económico", d_opt)
tdim = RJ(V11P("tea_dimensionado.json")) or tdim
D10s = RJ("v10/dimensionamiento.json") or {}
T10s = RJ("v10/tea_dimensionado.json") or {}
v11_html = ""
if d_opt and cmp11:
    reg11 = [r_ for r_ in DTm.registro().values() if r_.get("nota", "").startswith("v11")]
    par_rows11 = [[E(r_["clave"]), E(r_["valor"]) + " " + E(r_["unidad"]),
                   (E(r_["minimo"]) + "–" + E(r_["maximo"])) if r_.get("minimo") and r_.get("maximo") else "—", E(r_["etiqueta"]), E(r_["fuente"])] for r_ in reg11]
    p11 = d_opt["scen"][0]["products"]; s11 = d_opt["sizes"]
    o10 = D10s.get("E1|Óptimo económico", {}); p10 = o10.get("scen", [{}])[0].get("products", {})
    g11 = lambda k: dim.get(k, {}).get("obj")
    dec11 = cmp11.get("decomp", [])
    e8_rows = [[E(e_["label"]), n0(e_["obj"]), n0(e_["vinagre_m3"]), n0(e_["vino_vendido_m3"]), n0(e_["azucar_t"]), n0(e_["hojas_t"]),
                E(e_["sizes"].get("Acetificador", "no")), E(e_["sizes"].get("Extractora hojas", "no"))] for e_ in cmp11.get("e8", [])]
    ex8 = cmp11.get("e8_extra", {})
    prod11_rows = [[E(x["label"]), n0(x["v10"]), n0(x["v11"])] for x in cmp11.get("prods", [])]
    tea11_rows = [[E(x["label"]), n0(x["NPV10"] / MM), n0(x["NPV11"] / MM), pct(x["MIRR10"]), pct(x["MIRR11"]), pct(x["P10"], 0), pct(x["P11"], 0)]
                  for x in cmp11.get("tea", [])]
    T11 = {x["label"]: x for x in cmp11.get("tea", [])}
    c11 = (tdim or {}).get("cases", {}).get("A · Óptimo con la superestructura ampliada", {})
    be11 = c11.get("breakeven_vinegar")
    tor11 = cmp11.get("tornado11", [])
    tpan = next((x for x in tor11 if "panela" in x["label"]), None); tvin = next((x for x in tor11 if "vinagre" in x["label"]), None)
    a11 = (acv11 or {}).get("Óptimo v11"); a10 = (D10s and RJ("v10/acv.json") or {}).get("Óptimo v10")
    sc11 = (soc11 or {}).get("Óptimo v11"); s10_ = (RJ("v10/social.json") or {}).get("Óptimo v10")
    v11_html = f"""
<h3>Versión 11: panela, demanda de vinagre, xantana con residuo de piña y efluentes</h3>
<div class="prose">
<p><b>De dónde sale.</b> Tres capítulos de <i>Biological Processes in the Food Industry</i> (Elsevier, 2026). Ebrahimi (cap. 12, vinagre) confirma los datos del acetificador Frings que ya usaba el modelo (94 % del rendimiento teórico, vinagre al 12 % en unas 35 h, ciclos semicontinuos de 24 a 48 h) y trae dos cosas nuevas: el azúcar añadido a los jugos antes de fermentar es práctica común en vinagres de fruta (Tanamool et al. 2020 lo hicieron con jugo de cáscara de piña y 100 a 200 g/L de sacarosa), y el efluente del vinagre se trata con electrocoagulación y humedales construidos. Iakovchenko (cap. 13, xantana) reporta 5,0 g/L de xantana con residuo líquido de piña de 60 g/L de azúcar (Rashidi et al. 2024), unas siete veces menos que el rendimiento con glucosa pura que traía el ejemplo de SuperPro. Ahamed y Li (cap. 10, ácidos orgánicos) es cualitativo y sirve de respaldo a la discusión del hub.</p>
<p><b>Qué cambia en el modelo.</b> (1) Panela añadida a los jugos de cáscara y de hojas, hasta 150 g/L, con su costo y su huella. (2) Un tope explícito a las ventas de vinagre: en la v10 la restricción de mezcla limitaba el vinagre sin decirlo; con la panela esa restricción deja de atar y hay que nombrar el límite real, que es el mercado. El tope central, {n0(dmod.VIN_DEMAND)} m³/año, es un supuesto [S] hasta tener el estudio de mercado; E8 lo barre. (3) El rendimiento de xantana con jugo de piña. (4) El tratamiento del efluente en el TEA y en el ACV.</p>
</div>
{table(['Parámetro nuevo', 'Valor', 'Rango', 'Etiqueta', 'Fuente'], par_rows11) if par_rows11 else ''}
<div class="prose">V11_RESULTADOS</div>
{table(['Demanda de vinagre (E8)', 'Margen (MM COP/año)', 'Vinagre (m³)', 'Vino vendido (m³)', 'Panela (t)', 'Hojas (t)', 'Acetificador', 'Extractora'], e8_rows, num_cols=(1, 2, 3, 4, 5)) if e8_rows else ''}
{fig('fig46_comparativo_v10_v11.png', 'Comparación v10 y v11', 'Fig. 46. De la v10 a la v11: cascada del margen con el diseño v10 fijo y reoptimización, barrido de la demanda de vinagre (E8), productos del óptimo y VPN de los casos comparables.') if os.path.exists('figs/fig46_comparativo_v10_v11.png') else ''}
{table(['Producto o insumo del óptimo (por año)', 'v10', 'v11'], prod11_rows, num_cols=(1, 2))}
{table(['Caso del TEA', 'VPN v10 (MM COP)', 'VPN v11 (MM COP)', 'MIRR v10', 'MIRR v11', 'P(VPN > 0) v10', 'P(VPN > 0) v11'], tea11_rows, num_cols=(1, 2, 3, 4, 5, 6)) if tea11_rows else ''}
<div class="prose">V11_LECTURA</div>"""
    # textos
    t_ = ""
    if len(dec11) >= 4:
        t_ += (f"<p><b>Con el diseño de la v10 fijo.</b> El margen, {n0(dec11[0]['obj'])} MM COP/año, no cambia con el rendimiento de xantana con residuo de piña "
               f"(la xantana no se elegía); baja a {n0(dec11[2]['obj'])} con el tope de {n0(dmod.VIN_DEMAND)} m³/año de vinagre "
               f"({n0(dec11[1]['vinagre_m3'])} → {n0(dec11[2]['vinagre_m3'])} m³), y a {n0(dec11[3]['obj'])} con la panela, que deja vender "
               f"{n0(dec11[3]['vino_vendido_m3'])} m³/año de vino (antes {n0(dec11[2]['vino_vendido_m3'])}) con {n0(dec11[3]['azucar_kg'] / 1000)} t/año de panela.</p>")
    nos = g11("E1|Óptimo sin azúcar añadido"); notope = g11("E1|Óptimo sin tope de demanda de vinagre")
    t_ += (f"<p><b>El óptimo v11.</b> {n0(d_opt['obj'])} MM COP/año (v10: {n0(o10.get('obj', float('nan')))}) con acetificador de {E(s11.get('Acetificador'))}, "
           f"bodega de jugos de {E(s11.get('Bodega cáscara'))} y extractora de hojas de {E(s11.get('Extractora hojas'))}. Vende {n0(p11['vino_m3'] - p11.get('vino_a_vinagre_m3', 0))} m³/año de vino "
           f"y {n0(p11.get('vinagre_m3', 0))} m³/año de vinagre hecho con {n0(p11.get('jugo_cascara_vinagre_t', 0))} t de jugo de cáscara, {n0(p11.get('jugo_hojas_vinagre_t', 0))} t de jugo de hojas "
           f"y {n0(p11.get('azucar_kg', 0) / 1000)} t de panela; acopia {n0(p11.get('hojas_t', 0))} t de hojas. "
           + (f"Sin panela, con el mismo tope, el margen es {n0(nos)}; " if nos else "")
           + (f"sin tope de demanda, {n0(notope)}. " if notope else "")
           + "El óptimo v11 supera al v10 aunque vende la mitad del vinagre: el vino vuelve a venderse a 3 000 COP/L, la panela reemplaza al vino en la mezcla a un costo mucho menor, y el acetificador y la bodega de jugos se achican. "
           "La comparación justa no es con los 4 040 de la v10, que suponían vender 5,7 millones de litros, sino con los "
           + (n0(dec11[2]['obj']) if len(dec11) >= 3 else "—") + " que daría el diseño v10 con el mismo tope de demanda.</p>")
    if e8_rows:
        e8d = {e_["label"]: e_ for e_ in cmp11.get("e8", [])}
        nt = e8d.get("sin tope", {})
        t_ += ("<p><b>La demanda de vinagre decide el diseño.</b> En el barrido E8 el vino se vende en todos los niveles; lo que crece con la demanda es el vinagre hecho con jugos y panela: "
               "el acetificador pasa de 6 a 40 m³, la extractora de 2 a 5 t/h y las hojas acopiadas de unas 700 a más de 13 000 t/año. El margen crece casi en proporción a la demanda. "
               + (f"Sin tope, el modelo llega a {n0(nt.get('vinagre_m3', 0))} m³/año, limitado por los jugos y la panela que admite cada m³ de jugo; ese caso no es un diseño, es la señal de que el vinagre a 2 200 COP/L con panela es tan rentable que solo el mercado lo frena. " if nt else "")
               + (f"Con 6 000 m³/año sin panela el margen es {n0(ex8.get('demanda 6 000 m³/año sin azúcar', {}).get('obj', float('nan')))}, "
                  f"y con la panela a 5 000 COP/kg, {n0(ex8.get('panela a 5 000 COP/kg', {}).get('obj', float('nan')))}. " if ex8 else "")
               + "Mientras no haya un estudio de mercado, la tesis debe presentar el diseño como una familia de diseños indexada por la demanda de vinagre, no como un único óptimo.</p>")
    to11 = T11.get("Óptimo")
    if to11:
        t_ += (f"<p><b>TEA.</b> VPN del óptimo {n0(to11['NPV10'] / MM)} → {n0(to11['NPV11'] / MM)} MM COP; MIRR {pct(to11['MIRR10'])} → {pct(to11['MIRR11'])}; "
               f"P(VPN > 0) {pct(to11['P10'], 0)} → {pct(to11['P11'], 0)}. El TEA v11 incluye además el tratamiento del efluente ({n0(DTm.val('costo_ptar_m3'))} COP/m³ [S]). "
               + (f"El precio de equilibrio del vinagre es {n0(be11)} COP/L. " if be11 else "")
               + (f"En el tornado, el precio del vinagre mueve el VPN entre {n0(min(tvin['NPV_worst'], tvin['NPV_best']) / MM)} y {n0(max(tvin['NPV_worst'], tvin['NPV_best']) / MM)} MM COP, " if tvin else "")
               + (f"y el de la panela solo entre {n0(min(tpan['NPV_worst'], tpan['NPV_best']) / MM)} y {n0(max(tpan['NPV_worst'], tpan['NPV_best']) / MM)}. " if tpan else "")
               + (f"En el programa estocástico (oferta 0,7, 1,0 y 1,3 veces) el EVPI es {n0(max(dim['E4|WS']['obj'] - dim['E4|RP']['obj'], 0.0))} MM COP/año: con la demanda de vinagre como límite, el mismo diseño es el mejor en los tres escenarios de oferta. " if 'E4|WS' in dim and 'E4|RP' in dim else "")
               + "</p>")
    if a11:
        ef = a11.get("efluente", {})
        t_ += (f"<p><b>ACV.</b> GWP de proceso {n0(a11['gwp_total'] / 1000)} t CO2e/año"
               + (f" (v10: {n0(a10['gwp_total'] / 1000)})" if a10 else "")
               + f"; la panela aporta {n0(a11['gwp'].get('Panela añadida', 0) / 1000)} t y el tratamiento del efluente {n0(a11['gwp'].get('Tratamiento de efluentes', 0) / 1000)} t. "
               f"El efluente ({n0(ef.get('m3', 0))} m³/año, {n0(ef.get('dqo_kg', 0) / 1000)} t de DQO [S]) sale con {n0(ef.get('dqo_vertida_kg', 0) / 1000)} t/año de DQO tras la electrocoagulación y el humedal. "
               f"Neto frente a dejar fruta y hojas en el campo: {n0(-a11['net_vs_descomposicion'] / 1000)} t CO2e/año evitadas.</p>")
    P11 = sorted((par11 or {}).get("points", []), key=lambda z: z["gwp"])
    if len(P11) >= 3:
        t_ += ("<p><b>Frente margen–GWP.</b> " + "; ".join(f"{n0(q['gwp'] / 1000)} t CO2e/año → {n0(q['margin'])} MM COP/año"
                                                         + (" (sin vinagre)" if q['sizes'].get('Acetificador', 'no') == 'no' else f" (acetificador {E(q['sizes']['Acetificador'])})")
                                                         for q in P11[1:][::-1])
               + ". El extremo de mínimo GWP sigue siendo casi no procesar; el frente confirma que el vinagre, por su electricidad diésel, es lo que más pesa en el GWP de proceso.</p>")
    if sc11:
        t_ += (f"<p><b>Social.</b> {n0(sc11['empleos_planta'])} empleos en planta y {n0(sc11['empleos_acopio'])} en el acopio; valor que queda en el territorio {n0(sc11['valor_territorio'] / MM)} MM COP/año"
               + (f" (v10: {n0(s10_['valor_territorio'] / MM)})" if s10_ else "") + ". La panela es una compra local: el registro supone que el 30 % de los insumos distintos de la fruta se compra en la región [S].</p>")
    lect11 = ("<ul class='tight'>"
              "<li><b>El límite real del vinagre es el mercado.</b> La v10 vendía 5,7 millones de litros al año porque la mezcla ataba el volumen al vino; la panela suelta esa atadura y deja ver que hace falta un dato de demanda. El estudio de mercado del vinagre a granel es la tarea más importante para la tesis.</li>"
              "<li><b>La panela devuelve el vino al mercado.</b> En todos los niveles de demanda el vinagre sale de los jugos de cáscara y de hojas con panela, y el vino se vende. La panela cuesta unos 8 COP por gramo de ácido; el vino desviado costaba su precio de venta.</li>"
              "<li><b>La xantana queda descartada con más razón.</b> Con el rendimiento medido en residuo de piña (0,083 g/g), su ingreso por tonelada de jugo es siete veces menor que el supuesto anterior.</li>"
              "<li><b>El efluente entra al balance.</b> El tratamiento con electrocoagulación y humedal suma un costo y una huella pequeños; la DQO del efluente es un supuesto [S] que hay que medir.</li>"
              "<li><b>Lo que la v11 no hizo.</b> La acetificación termotolerante (menos frío) y el vinagre de doble fuerza (menos flete por el río) quedan como alternativas de la etapa 3 para la versión siguiente.</li></ul>")
    v11_html = v11_html.replace("V11_RESULTADOS", t_).replace("V11_LECTURA", lect11)
dim, d_opt, tdim = dim_cur, d_opt_cur, tdim_cur

# ---- v12: vino embotellado con impuesto al consumo (Ley 1816 de 2016), demanda de botellas y renta ZOMAC por año
cmp12 = RJ("comparativo_v11_v12.json")
acv12, soc12 = RJ("acv.json"), RJ("social.json")
D11s = RJ("v11/dimensionamiento.json") or {}
v12_html = ""
if d_opt and cmp12:
    WB12 = cmp12.get("wine_bottle") or dmod.wine_bottle()
    reg12 = [r_ for r_ in DTm.registro().values() if r_.get("nota", "").startswith("v12")]
    par_rows12 = [[E(r_["clave"]), E(r_["valor"]) + " " + E(r_["unidad"]),
                   (E(r_["minimo"]) + "–" + E(r_["maximo"])) if r_.get("minimo") and r_.get("maximo") else "—", E(r_["etiqueta"]), E(r_["fuente"])] for r_ in reg12]
    bot_rows = [["Precio de venta al público (con IVA del 5 %)", n0(WB12["pvp"])], ["Precio de fábrica, con impuesto al consumo", n0(WB12["fabrica"])],
                ["Impuesto al consumo: componente específico", n0(WB12["especifico"])], ["Impuesto al consumo total (específico + ad valórem)", n0(WB12["impuesto"])],
                ["Botella, tapa, etiqueta y caja", n0(WB12["empaque"])], ["Neto para la planta por botella", n0(WB12["neto"])],
                ["Neto por litro de vino (frente a 3 000 COP/L a granel en la v11)", n0(WB12["neto_L"])]]
    p12 = d_opt["scen"][0]["products"]; s12 = d_opt["sizes"]
    o11 = D11s.get("E1|Óptimo económico", {})
    dec12 = cmp12.get("decomp", [])
    e9_rows = [[E(e_["label"]), n0(e_["obj"]), n0(e_["botellas"] / 1000), n0(e_["vinagre_m3"]), n0(e_["azucar_t"]),
                E(e_["sizes"].get("Embotelladora", "no")), E(e_["sizes"].get("Acetificador", "no"))] for e_ in cmp12.get("e9", [])]
    ex9 = cmp12.get("e9_extra", {})
    prod12_rows = [[E(x["label"]), n0(x["v11"]), n0(x["v12"])] for x in cmp12.get("prods", [])]
    tea12_rows = [[E(x["label"]), n0(x["NPV11"] / MM), n0(x["NPV12"] / MM), n0((x["NPV12_prorroga"] or float("nan")) / MM), pct(x["MIRR12"]), pct(x["P12"], 0), E(x.get("size") or "—")]
                  for x in cmp12.get("tea", [])]
    T12 = {x["label"]: x for x in cmp12.get("tea", [])}
    g12 = lambda k: dim.get(k, {}).get("obj")
    v12_html = f"""
<h3>Versión 12: vino embotellado, impuesto al consumo y renta en ZOMAC</h3>
<div class="prose">
<p><b>Por qué.</b> La instancia reducida del manuscrito (sec. 6.9) encontró que, con el impuesto al consumo de vinos de la Ley 1816 de 2016, ninguna configuración de sus seis líneas era rentable. Las versiones 1 a 11 valoraban el vino a granel a 3 000 COP/L sin ese impuesto. La v12 lo incorpora con el vino embotellado, que es como se va a vender, y revisa el impuesto de renta: la planta queda en Riosucio o Carmen del Darién, municipios ZOMAC (Decreto 1650 de 2017).</p>
<p><b>Qué cambia en el modelo.</b> (1) El vino se vende en botellas de 750 mL: el impuesto al consumo combina un componente específico de 243 COP por grado alcoholimétrico (tarifa 2026) y un 20 % ad valórem sobre el precio al público antes de impuestos; el IVA es del 5 %. (2) Una línea de embotellado de 500 a 4 000 botellas por hora, el empaque por botella y un operario. (3) Un tope de demanda de vino embotellado, {n0(DTm.val('demanda_vino_botellas'))} botellas/año como supuesto central [S], barrido en E9. (4) La huella de la botella de vidrio en el ACV. (5) La renta por año: con arranque en 2030, el régimen ZOMAC de la Ley 1819 de 2016 (art. 237) ya no da tarifa reducida, así que la base usa el 35 %; el proyecto de ley 435 de 2025, que llevaría a las MiPymes al 25 % de la tarifa general hasta 2033, entra como escenario. El tamaño de la empresa sale del diseño, por sus ingresos en UVT (Decreto 957 de 2019).</p>
</div>
{table(['Parámetro nuevo', 'Valor', 'Rango', 'Etiqueta', 'Fuente'], par_rows12) if par_rows12 else ''}
{table(['Una botella de 750 mL (COP)', 'Valor'], bot_rows, num_cols=(1,))}
<div class="prose">V12_RESULTADOS</div>
{table(['Demanda de vino (E9)', 'Margen (MM COP/año)', 'Botellas (miles/año)', 'Vinagre (m³)', 'Panela (t)', 'Embotelladora', 'Acetificador'], e9_rows, num_cols=(1, 2, 3, 4)) if e9_rows else ''}
{fig('fig47_comparativo_v11_v12.png', 'Comparación v11 y v12', 'Fig. 47. De la v11 a la v12: cascada del margen con el diseño v11 fijo y reoptimización, barrido de la demanda de vino embotellado (E9), productos del óptimo y VPN de los casos comparables, con el escenario de prórroga ZOMAC.') if os.path.exists('figs/fig47_comparativo_v11_v12.png') else ''}
{table(['Producto o insumo del óptimo (por año)', 'v11', 'v12'], prod12_rows, num_cols=(1, 2))}
{table(['Caso del TEA', 'VPN v11 (MM COP)', 'VPN v12 (MM COP)', 'VPN v12 con prórroga ZOMAC', 'MIRR v12', 'P(VPN > 0) v12', 'Tamaño de empresa'], tea12_rows, num_cols=(1, 2, 3, 4, 5)) if tea12_rows else ''}
<div class="prose">V12_LECTURA</div>"""
    t_ = ""
    if len(dec12) >= 3:
        t_ += (f"<p><b>Con el diseño de la v11 fijo.</b> El margen pasa de {n0(dec12[0]['obj'])} MM COP/año con vino a granel sin impuesto a {n0(dec12[1]['obj'])} con el vino embotellado y el impuesto al consumo "
               f"({n0(dec12[1]['botellas'] / 1000)} mil botellas, embotelladora de {E(dec12[1].get('embotelladora') or '—')}), y a {n0(dec12[2]['obj'])} con el tope de "
               f"{n0(DTm.val('demanda_vino_botellas'))} botellas/año. Embotellado, el vino deja a la planta {n0(WB12['neto_L'])} COP por litro después del impuesto, del margen de distribución y del empaque, "
               f"frente a 3 000 COP/L a granel: el impuesto ({n0(WB12['impuesto'])} COP por botella) pesa menos que el valor que agrega embotellar, siempre que el mercado pague {n0(WB12['pvp'])} COP por botella.</p>")
    nt = g12("E1|Óptimo sin tope de demanda de vino")
    t_ += (f"<p><b>El óptimo v12.</b> {n0(d_opt['obj'])} MM COP/año (v11: {n0(o11.get('obj', float('nan')))}) con embotelladora de {E(s12.get('Embotelladora', 'no'))}, "
           f"acetificador de {E(s12.get('Acetificador', 'no'))}, bodega de jugos de {E(s12.get('Bodega cáscara', 'no'))} y extractora de hojas de {E(s12.get('Extractora hojas', 'no'))}. "
           f"Vende {n0(p12.get('botellas', 0) / 1000)} mil botellas de vino ({n0(p12['vino_m3'] - p12.get('vino_a_vinagre_m3', 0))} m³) y {n0(p12.get('vinagre_m3', 0))} m³ de vinagre, "
           f"con {n0(p12.get('azucar_kg', 0) / 1000)} t de panela y {n0(p12.get('hojas_t', 0))} t de hojas. "
           + (f"Sin tope de demanda de vino, el margen sube a {n0(nt)}. " if nt else "")
           + f"Con los dos mercados topados, la planta queda limitada por el mercado y no por la fruta: procesa {n0(p12['fruta_t'])} de las {n0(DTm.val('oferta_fruta_t'))} t/año de fruta de rechazo, con frente de {E(s12.get('Frente', '—'))} y una sola prensa compartida por pulpa y cáscara, y saca la mayor parte del vinagre del jugo de hojas con panela "
           f"({n0(p12.get('jugo_hojas_vinagre_t', 0))} t de jugo de hojas frente a {n0(p12.get('jugo_cascara_vinagre_t', 0))} t de jugo de cáscara). Por eso el margen ya no cambia con la oferta de fruta (E2: {n0(g12('E2|0.500') or float('nan'))} a la mitad y {n0(g12('E2|3.000') or float('nan'))} al triple) "
           f"y el valor de la información perfecta sobre la oferta es nulo (E4). La regla de llenado de la bodega (llenado directo en ≤ {n0(DTm.val('tau_llenado_max'))} h o carga desde el almacén de mosto) no cambia el diseño: el almacén de 10 m³ no guarda mosto entre meses y cada lote se carga con bomba.</p>")
    if e9_rows:
        t_ += ("<p><b>La demanda de vino embotellado.</b> El margen crece con las botellas que absorbe el mercado; "
               + (f"con PVP de 10 000 COP por botella el margen es {n0(ex9.get('PVP 10 000 COP/botella', {}).get('obj', float('nan')))}, y con 25 000 COP, {n0(ex9.get('PVP 25 000 COP/botella', {}).get('obj', float('nan')))}. " if ex9 else "")
               + (f"El mismo modelo con vino a granel sin impuesto (como en la v11) da {n0(ex9.get('vino a granel sin impuesto (v11)', {}).get('obj', float('nan')))}. " if 'vino a granel sin impuesto (v11)' in ex9 else "")
               + "Con la botella a 10 000 COP el óptimo deja de hacer vino: no compra fruta y produce solo vinagre de jugo de hojas con panela. "
               + "La pregunta de mercado ya no es solo cuánto vinagre se vende, sino cuántas botellas de vino de piña y a qué precio.</p>")
    to12 = T12.get("Óptimo")
    if to12:
        t_ += (f"<p><b>TEA y renta.</b> VPN del óptimo {n0(to12['NPV11'] / MM)} → {n0(to12['NPV12'] / MM)} MM COP; MIRR {pct(to12['MIRR11'])} → {pct(to12['MIRR12'])}; "
               f"P(VPN > 0) {pct(to12['P11'], 0)} → {pct(to12['P12'], 0)}. Por sus ingresos la empresa es {E(to12.get('size') or '—')}. Con la ley vigente la renta es del 35 % desde el arranque en 2030; "
               f"si se aprobara la prórroga del PL 435 de 2025, el VPN sería {n0((to12['NPV12_prorroga'] or float('nan')) / MM)} MM COP. La ubicación en ZOMAC no exime del impuesto al consumo, que es departamental.</p>")
    par12 = RJ("pareto.json")
    if par12 and len(par12.get("points", [])) >= 3:
        P_ = par12["points"]; p0, p1 = P_[0], P_[1]
        t_ += (f"<p><b>Margen frente a GWP.</b> El frente de Pareto (ε-restricción) va de {n0(p0['margin'])} MM COP/año con {n0(p0['gwp'] / 1000)} t CO2e/año "
               f"a {n0(P_[-1]['margin'])} con {n0(P_[-1]['gwp'] / 1000)} t (no operar). Bajar a {n0(p1['gwp'] / 1000)} t cuesta "
               f"{n0(p0['margin'] - p1['margin'])} MM COP/año, unos {n0((p0['margin'] - p1['margin']) * 1e6 / max(p0['gwp'] - p1['gwp'], 1))} COP por kg de CO2e evitado.</p>")
    a12 = (acv12 or {}).get("Óptimo v12")
    if a12:
        t_ += (f"<p><b>ACV.</b> GWP de proceso {n0(a12['gwp_total'] / 1000)} t CO2e/año; las botellas de vidrio aportan {n0(a12['gwp'].get('Botellas de vidrio', 0) / 1000)} t "
               f"(0,5 kg CO2e por botella [S]). Neto frente a dejar fruta y hojas en el campo: {n0(-a12['net_vs_descomposicion'] / 1000)} t CO2e/año evitadas.</p>")
    sc12 = (soc12 or {}).get("Óptimo v12")
    if sc12:
        t_ += f"<p><b>Social.</b> {n0(sc12['empleos_planta'])} empleos en planta y {n0(sc12['empleos_acopio'])} en el acopio; valor que queda en el territorio {n0(sc12['valor_territorio'] / MM)} MM COP/año. El impuesto al consumo no cuenta como compra local, aunque se queda en el departamento.</p>"
    lect12 = ("<ul class='tight'>"
              "<li><b>El impuesto no hunde el proyecto si el vino se embotella y se vende a buen precio.</b> La conclusión de la instancia reducida del manuscrito vale para el vino a granel con impuesto; embotellado, el valor agregado supera al impuesto mientras el precio al público se sostenga. A 10 000 COP por botella ya no conviene hacer vino.</li>"
              "<li><b>La planta la dimensiona el mercado.</b> Con 500 000 botellas y 3 000 m³ de vinagre, el óptimo procesa una quinta parte de la fruta de rechazo; la oferta de fruta deja de ser la restricción activa, y el diseño se encoge (frente de 1 t/h, sin prensa de cáscara ni caldera de corona).</li>"
              "<li><b>Ahora hay dos mercados que validar.</b> La demanda de vinagre a granel y la de vino de piña embotellado (botellas y precio) fijan el tamaño y el valor de la planta.</li>"
              "<li><b>ZOMAC no cambia la base.</b> Con arranque en 2030 la tarifa reducida ya venció; sirve como escenario (prórroga) y como argumento de política, junto con obras por impuestos.</li>"
              "<li><b>Supuestos que más pesan [S].</b> El precio al público de la botella, el margen de distribución, el costo del empaque, la demanda de botellas y la tarifa departamental del Chocó, que puede diferir de la certificada por el Ministerio de Hacienda.</li></ul>")
    v12_html = v12_html.replace("V12_RESULTADOS", t_).replace("V12_LECTURA", lect12)
super_rows = [
    ["Extracción de pulpa", "Prensa de banda (compartida con cáscara y corazón, o solo pulpa) · decantadora centrífuga", "Cap. 4: la decantadora es continua, rinde más del 80 % y entrega mosto de 150–400 NTU; consume más energía y mantenimiento", "Decantadora: +4,5 kWh/t de pulpa"],
    ["Clarificación del mosto", "MF cerámica · flotación · centrífuga de discos", "Cap. 8: la MF tangencial «no está adaptada a la clarificación de mostos» por su bajo caudal; la turbidez objetivo es 100–200 NTU. Quesada Salas (2013), jugo pulposo de piña en planta piloto: 2 850–3 570 NTU y 10,5 % de sólidos insolubles; MFT sostenida a 40–50 L/m²·h con FRV 3,7 (73 % de jugo clarificado)", "MF: 45 L/m²·h, 27 % de retenido, membranas 15 %/año · flotación: 2 900 COP/m³, 18 % de espumas · centrífuga: 2 800 COP/m³, 12 % de lodos (escalados con los sólidos de la piña)"],
    ["Recuperación de lías y espumas", "No · MF tangencial de lías (30 L/m²·h)", "Cap. 8: lías y espumas tienen 80–90 % de jugo en uva; la MF de lías es la aplicación industrial de la MF", "Recupera el 60 % del jugo de los lodos de piña [S]; el retenido de la MF de mosto no se vuelve a filtrar"],
    ["Destino de lías y retenidos", "Compostaje · línea de harina (secador)", "Quesada Salas (2013) recomienda valorizar el retenido; Vasiljevic (2020): la fibra insoluble de la piña (celulosa y hemicelulosa) es la base de la harina de fibra", "0,11 t de harina por t de lías; cada t carga el secador como 1,16 t de torta"],
    ["Vinagre", "Sin vinagre · vino desviado a vinagre · jugo de cáscara fermentado y acetificado", "Emde (2017, Ullmann's, planta Frings): acetificador sumergido de 40–60 kg/m³·d, rendimiento cercano al teórico (46 g etanol → 60 g ácido), ΔH = −493 kJ/mol, aireación 0,1–0,15 vvm, grupo electrógeno de emergencia obligatorio. Bekatorou (2020, cap. 14): vinagre de residuos de piña al 5 %", "50 kg/m³·d; 94 % del teórico; frío con COP 4 y grupo electrógeno; vinagre al 5 % a 2 200 COP/L [S]"],
    ["Estabilización", "Pasteurización flash (HTST, 75 °C) · SO₂ (≈ 50 mg/L) · UHPH (300 MPa)", "Cap. 5: UHPH industrial hasta 10 000 L/h, esteriliza e inactiva la polifenoloxidasa sin SO₂; un solo proveedor (TRL 8 en mosto de piña)", "HTST: 4 484 COP/m³ · SO₂: 1 500 COP/m³ · UHPH: 100 kWh/m³ ≈ 140 000 COP/m³"],
    ["Calor de proceso", "GLP · caldera de biomasa con corona (100–500 kWt) + GLP de respaldo", "Línea L7b del TEA (TRL 9); balance de energía de la Fig. 35: la corona podía cubrir casi todo el calor del secado", "Corona con 20 % de MS, 17 MJ/kg, caldera al 80 % (2 720 MJ útiles/t); picado 10 kWh/t; reemplaza GLP a 159 COP/MJ y evita el compostaje"],
    ["Pretratamiento de la cáscara (v9)", "Agua · Ca(OH)₂ al 0,1 %", "Seguí y Fito (2018): la cal sube el licor al 68,4 % de la cáscara", "Más jugo (0,65 t/t) y menos torta y harina; 2 900 COP/t de cáscara"],
    ["Enzima del jugo de cáscara (v9)", "No · precipitación con polisacárido · UF 10 kDa (+ liofilización)", "Campos et al. (2020); Seguí y Fito (2018): la bromelaína sale del jugo antes de fermentarlo y el jugo fermenta mejor", "0,78 kg/t de jugo; UF a mitad de precio por su baja actividad"],
    ["En todos los diseños", "Inertización con N₂ · dosificación de nutrientes (DAP 200 mg/L)", "Caps. 12, 23 y 25: nitrógeno asimilable < 140 mg/L es deficiencia; el llenado lento de los fermentadores exige proteger el mosto del oxígeno", "Generador de N₂ y dosificador en el FCI; DAP 1 600 COP/m³; N₂ 0,5 kWh/m³ de vino"],
]

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
  <p class="kicker">Tesis doctoral · Biorrefinería de piña · Bajo Atrato (Chocó) · versión 12</p>
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
    <li><a href="#estocastico">Optimización estocástica (§6.7)</a></li>
    <li><a href="#anual">Programa anual y cuellos de botella</a></li>
    <li><a href="#dimensionamiento">Dimensionamiento óptimo de equipos</a></li>
    <li><a href="#tea-dim">TEA con los tamaños óptimos</a></li>
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

<section id="estocastico">
<h2>Optimización estocástica en dos etapas (§6.7)</h2>
<div class="prose">
<p>La formulación sigue a Grossmann (<i>Advanced Optimization for PSE</i>, cap. 14). Las decisiones de diseño d se toman aquí y ahora: líneas, tamaños de catálogo y frente de pelado. Las decisiones de operación z(θ), es decir compra de fruta, flujos mensuales, GLP y diésel, se ajustan después de conocer cada escenario θ. El problema (ec. 14.12) se resuelve como su equivalente determinista (ec. 14.19) con SCIP.</p>
<p>Escenarios: 27, de la combinación de oferta de fruta (×0,7 / ×1,0 / ×1,3 sobre las 6 146 t del Chocó, con probabilidades 0,25 / 0,5 / 0,25), precio del vino a granel (2 200 / 3 000 / 4 000 COP/L; 0,3 / 0,4 / 0,3) y precio de la harina (8 000 / 12 000 / 16 000 COP/kg; 0,25 / 0,5 / 0,25). El riesgo se trata con el criterio de §6.7: max (1−λ)·E[Π] + λ·CVaR<sub>0,9</sub>(Π), con CVaR<sub>β</sub> = ζ − (1/(1−β)) Σ p<sub>s</sub> máx(0, ζ − Π<sub>s</sub>).</p>
</div>
{table(['Indicador', 'MM COP/año'], sto_rows, num_cols=(1,)) if sto else ''}
<div class="prose">
<p><b>Lectura de los indicadores.</b> El VSS es cero: la decisión de primera etapa del problema de valor medio (vino + harina a 6 200 t/año) es la misma que la del problema estocástico. Lo que cambia es la promesa: el EV anuncia {n0(sto['EV']['E']/MM) if sto else ''} MM COP/año, y con esa misma planta el beneficio esperado real es {n0(sto['RP']['E']/MM) if sto else ''} MM. Es el sesgo de los promedios: con precios y oferta asimétricos, la planta no aprovecha los escenarios buenos porque su capacidad la topa, y sí sufre los malos. El EVPI de {n0(sto['EVPI']/MM) if sto else ''} MM COP/año es alto. Medir la oferta real del Bajo Atrato y asegurar contratos de precio antes de invertir vale más que cualquier refinamiento del modelo.</p>
</div>
{table(['Decisión óptima con información perfecta', 'Probabilidad'], ws_rows) if sto else ''}
{table(['λ (peso del CVaR)', 'Diseño', 'E[Π] (MM COP/año)', 'CVaR₉₀ (MM COP/año)'], front_rows, num_cols=(2, 3)) if sto else ''}
<div class="prose"><p><b>Aversión al riesgo.</b> La decisión cambia de golpe en λ* ≈ {n1(lam_star*100).replace(',0','') if sto else ''} % (λ* = E/(E − CVaR)). Por debajo conviene construir vino + harina; por encima, con fruta comprada a 400 COP/kg, conviene no construir. No aparece ningún diseño intermedio: las escalas pequeñas no pagan su costo fijo. Para la tesis, la frontera media-riesgo de §6.7 con la oferta actual tiene dos puntos, y el resultado depende sobre todo de la tolerancia al riesgo del inversionista.</p></div>
{fig('fig23_estocastico.png', 'Programación estocástica', 'Fig. 23. Distribución del beneficio en los 27 escenarios, indicadores de Grossmann y frontera media–CVaR.')}
</section>

<section id="anual">
<h2>Programa anual con estacionalidad en tiempo continuo</h2>
<div class="prose">
<p>El modelo combina varias piezas de Maravelias (<i>Chemical Production Scheduling</i>):</p>
<ul class="tight">
<li><b>Rejilla continua común</b> (cap. 7.3, ec. 7.35–7.36): T<sub>0</sub> = 0, T<sub>|T|</sub> = η y T<sub>t</sub> ≥ T<sub>t−1</sub>. Los cortes de mes son puntos fijos y cada mes tiene K periodos de duración libre.</li>
<li><b>Procesos continuos</b> (cap. 9.2): lo producido es tasa × duración, con la tasa acotada por la capacidad.</li>
<li><b>Transiciones</b> (cap. 9.3.2): limpieza de 1 h al cambiar el material de la prensa compartida.</li>
<li><b>Inventarios</b> con capacidad χ<sub>k</sub> (cap. 8.2): fruta, 3 días de oferta pico; pulpa 1,5 t; cáscara 3 t; torta 12 t; pulmón de mosto 50 m³.</li>
</ul>
<p>La entrada de fruta es la tasa estacional del mes por la duración del periodo, así que es lineal en d y el modelo sigue siendo un MILP. Las unidades con personal operan el 36 % del tiempo calendario (2 turnos de lunes a sábado); la bodega y el secador, el 90 %. El programa es periódico: el inventario final del año es igual al inicial. Se comparó K = 2 y K = 4 periodos por mes para comprobar que la solución no depende de la rejilla.</p>
</div>
{table(['Configuración', 'Estado', 'Fruta perdida (t/año)', 'Cambios de material', 'Vino (m³)', 'Harina (t)', 'Bromelaína (kg)', 'Cuellos de botella (máx. mensual)'], anu_rows, num_cols=(2, 3, 4, 5, 6)) if anu else ''}
{fig('fig24_gantt_anual.png', 'Gantt anual', 'Fig. 24. Gantt anual: campañas de la prensa compartida por material, con marcas de cambio, y carga de cada unidad por periodo.') if anu else ''}
{fig('fig25_ocupacion_anual.png', 'Ocupación anual', 'Fig. 25. Ocupación por unidad y mes en cada configuración (en negrita, ≥ 95 %) y fruta no procesada por falta de capacidad.') if anu else ''}
{fig('fig26_gantt_bodega.png', 'Gantt de bodega', 'Fig. 26. Gantt de la bodega con fermentadores desfasados a la escala del Chocó y a la de la tesis.')}
<div class="prose">
<p><b>Cuellos de botella identificados.</b> El programa anual, el semanal (Fig. 21) y el de bodega (Fig. 26) se complementan:</p>
<ul class="tight">
<li><b>Prensa compartida.</b> Con vino + harina y una prensa de 2 t/h, la prensa está al 100 % en diez de los doce meses: los ciclos de cambio y limpieza, unos 2,8 por día, le quitan tiempo aun con poca oferta. La fruta se pierde en abril–junio y septiembre–noviembre, unas 520 t al año (8 % de la oferta).</li>
<li><b>Con bromelaína.</b> Al agregarla, la prensa reparte su tiempo entre tres materiales y la pérdida sube a unas 1 580 t (26 %). La prensa es el cuello principal de cualquier ampliación del portafolio.</li>
<li><b>Prensa de 3 t/h.</b> La pérdida baja a unas 220 t (3,6 %) y el cuello pasa al frente de pelado, que queda al 100 %. La bodega llega al 83–91 % en los picos.</li>
<li><b>Unidades con holgura.</b> La microfiltración (≤ 63 %) y el secador (≤ 35 %) nunca son limitantes.</li>
</ul>
<p>La secuencia de ampliación queda: primero una prensa de 3 t/h o una prensa dedicada al corazón, después una segunda peladora, y luego fermentadores. En la bodega, a caudal bajo, cada fermentador tarda más en llenarse (34,5 h a la escala del Chocó) que en fermentar (12,5 h). Esa exposición al aire es el problema de oxidación de §4.2.4.</p>
<p>La semana pico del STN (Fig. 21) mostraba la prensa de 2 t/h al 64 %. Ahí la oferta semanal estaba topada por el frente del plan del MILP (119 t/semana), y el acoplamiento con el almacenamiento era exacto. En el modelo anual la oferta del pico llega a unas 640 t/mes y el acoplamiento lineal es conservador. Los dos resultados acotan la ocupación real de la prensa entre esos valores.</p>
</div>
</section>


<section id="dimensionamiento">
<h2>Dimensionamiento óptimo de equipos para balancear los flujos</h2>
<div class="prose">
<p><b>Por qué hace falta.</b> El diseño TRL-9 (<code>planta_trl9.py</code>) dimensiona cada equipo por separado, con el flujo medio anual y el tamaño de catálogo más barato que lo cubre. Así cada equipo queda bien en promedio, pero los flujos no quedan balanceados: con la cosecha estacional, unos equipos topan la producción en los meses pico mientras otros pasan el año a medio uso (Fig. 25). El apartado que se propone para la tesis dimensiona todos los equipos <i>a la vez</i> y con el programa anual dentro del mismo modelo (diseño y operación simultáneos). Así el tamaño de cada equipo se elige mirando lo que pasa aguas arriba y aguas abajo en cada mes.</p>
<p><b>Formulación</b> (<code>dimensionamiento.py</code>, MILP en SCIP):</p>
<ul class="tight">
<li><b>Elección de tamaño como disyunción</b> (Grossmann 2021, cap. 10): para cada equipo u, ∨<sub>s</sub>[y<sub>us</sub>; cap<sub>u</sub> = cap<sub>us</sub>; costo<sub>u</sub> = C<sub>us</sub>] con Σ<sub>s</sub> y<sub>us</sub> = 1. Los tamaños salen del catálogo de <code>planta_trl9.CAT</code>; cada opción incluye los equipos que la acompañan (por ejemplo, la prensa con su trituradora y su macerador, la bodega con su chiller y su centrífuga, el secador con su caldera y su molino). La clarificación, la recuperación de lías y la estabilización del mosto son etapas propias con alternativas tecnológicas (ver la superestructura ampliada).</li>
<li><b>Producto tamaño × horas.</b> La capacidad de un periodo es cap<sub>us</sub>·y<sub>us</sub>·h<sub>t</sub>, con h<sub>t</sub> continua. Se linealiza de forma exacta con variables g<sub>ust</sub> ≤ H·y<sub>us</sub>, Σ<sub>s</sub> g<sub>ust</sub> ≤ h<sub>t</sub> (0-1 por continua acotada, Grossmann cap. 7.3). Lo mismo para la prensa en tiempo compartido y para el acoplamiento con los pulmones perecederos, donde la capacidad del frente multiplica el tiempo de campaña.</li>
<li><b>Bodega de Moresi lineal en N<sub>F</sub>.</b> De N<sub>F</sub> = Q·Δt<sub>c</sub>/V<sub>F</sub> con Δt<sub>c</sub> = V<sub>F</sub>/Q + t<sub>proc</sub> (Moresi 1989b, con la corrección del tiempo de llenado) sale Q ≤ (N<sub>F</sub> − 1)·V<sub>F</sub>/t<sub>proc</sub>: mientras un fermentador se llena, los demás fermentan. Es lineal en el número de fermentadores.</li>
<li><b>Operación anual</b>: la misma rejilla continua anclada a los meses, la prensa compartida con limpiezas, los inventarios periódicos y la oferta estacional del programa anual (Maravelias caps. 7.3, 8.2, 9.3.2 y 10), con K = 2 periodos por mes.</li>
<li><b>Palancas de flujo además del tamaño.</b> Una prensa dedicada a la cáscara (evita los cambios de material), una decantadora dedicada a la pulpa, un almacén aséptico de mosto de 10 a 800 m³ (puede guardar el mosto de los meses pico para fermentarlo en los valles), un tercer turno en el frente ({n0(SHIFTv)} MM COP/año de nómina adicional con prestaciones y supervisión, la alternativa operativa a comprar equipo) y el compostaje de la cáscara que no se alcance a secar.</li>
<li><b>Objetivo</b>: maximizar el margen anual, es decir la contribución (ingresos − costos variables del TEA de cada línea − fruta a 400 COP/kg − cambios) menos el cargo de capital de los equipos. El cargo es {pct(AFv, 1)} del costo de compra por año: factor Lang equivalente de Burk {n1(LANGv)} × (CRF del 10 % a 10 años + 5 % de mantenimiento + 3 % de impuestos locales). La nómina base y los costos fijos que no dependen del tamaño no entran, porque no cambian la elección. Por eso los márgenes de esta sección no son el VPN del TEA.</li>
</ul>
</div>
<h3>Superestructura ampliada con <i>White Wine Technology</i></h3>
<div class="prose"><p>La versión anterior fijaba la topología de la tesis: prensa de banda, microfiltración del mosto y pasteurización flash. Con <i>White Wine Technology</i> (Morata, ed., 2022) se agregaron alternativas en cada etapa del mosto. El MILP elige la tecnología y el tamaño a la vez; las pérdidas y los costos variables dependen de la opción elegida y se modelan por opción (flujo por alternativa, con la misma linealización exacta).</p></div>
{table(['Etapa', 'Alternativas', 'Base técnica (Morata 2022)', 'Costos y pérdidas [S]'], super_rows)}
{fig('fig33_superestructura.png', 'Superestructura ilustrada', 'Fig. 33. Superestructura de la biorrefinería: etapas, alternativas de cada disyunción y destinos de cada fracción. En color, el diseño óptimo de la versión 10 (con la fila nueva de hojas de la planta); en gris punteado, las alternativas descartadas; en verde punteado, la bromelaína del corazón de la configuración B.')}
<div class="prose"><p>Dos efectos de calidad del libro no entran en el objetivo: la turbidez objetivo del mosto (100–200 NTU) y el riesgo de fermentación lenta con mostos clarificados en exceso, por falta de fitoesteroles. Los dos van en contra de la microfiltración del mosto, de modo que, si el MILP la descarta por costo, la calidad refuerza esa decisión. Los costos de la decantadora, el flotador, la UHPH y la microfiltración de lías son supuestos de orden de magnitud: el libro da capacidades, no precios.</p></div>
{table(['Diseño', 'Tamaños', 'FCI equipos (MM COP)', 'Margen (MM COP/año)', 'Fruta procesada', 'Cambios/año', 'Vino (m³)', 'Harina (t)', 'Cuellos (≥ 95 %)'], dim_e1, num_cols=(2, 3, 4, 5, 6, 7)) if dim_e1 else ''}
{fig('fig27_dimensionamiento.png', 'Dimensionamiento óptimo', 'Fig. 27. Ocupación mensual de cada equipo en el diseño TRL-9, en el óptimo con la topología anterior y en el óptimo con la superestructura ampliada, e inversión por equipo.') if d_opt else ''}
<div class="prose">
<p><b>Qué cambia el óptimo con la oferta del Chocó 2022.</b> {('Frente al diseño TRL-9, el óptimo ' + ('agranda' if float(d_opt['sizes']['Frente'].split()[0]) > float(d_ref['sizes']['Frente'].split()[0]) else 'reduce') + ' el frente de ' + d_ref['sizes']['Frente'] + ' a ' + d_opt['sizes']['Frente'] + ' y el secador de ' + d_ref['sizes']['Secador'] + ' a ' + d_opt['sizes']['Secador'] + ', que en la referencia pasaba el año al ' + pct(min(d_ref['scen'][0]['util']['Secador']), 0) + '–' + pct(max(d_ref['scen'][0]['util']['Secador']), 0) + '. ' + ('Conserva las dos prensas dedicadas de 1 t/h' if d_opt['sizes'].get('Prensa cáscara', 'no') != 'no' else 'Usa una sola prensa de ' + d_opt['sizes']['Prensa'] + ' compartida por pulpa y cáscara') + ' y la bodega de ' + d_opt['sizes']['Bodega'].replace('×', ' × ') + '. En el mosto cambia la topología: la microfiltración de 20 m² se reemplaza por ' + d_opt['sizes']['Clarificación'].lower().replace('centrífuga', 'una centrífuga de discos de').replace('flotación', 'flotación de') + (', se agrega microfiltración de lías de ' + d_opt['sizes']['MF lías'] if d_opt['sizes'].get('MF lías', 'no') != 'no' else '') + ' y la pasteurización flash se reemplaza por ' + ('sulfitado' if d_opt['sizes']['Estabilización'].startswith('SO') else d_opt['sizes']['Estabilización']) + '. La fruta procesada ' + ('sube' if absorbed(d_opt['scen'][0]) > absorbed(d_ref['scen'][0]) else 'baja') + ' de ' + pct(absorbed(d_ref['scen'][0])) + ' a ' + pct(absorbed(d_opt['scen'][0])) + ' de la oferta' + (' (con el vino y el vinagre topados por la demanda, la planta no compra más fruta de la que puede vender)' if absorbed(d_opt['scen'][0]) < absorbed(d_ref['scen'][0]) else '') + ', la inversión en equipos ' + ('baja en ' if d_ref['FCI'] > d_opt['FCI'] else 'sube en ') + n0(abs(d_ref['FCI'] - d_opt['FCI'])) + ' MM COP (con el vinagre' + (' y la caldera' if d_opt['sizes'].get('Caldera de corona', 'no') != 'no' else '') + ') y el margen anual mejora en ' + n0(d_opt['obj'] - d_ref['obj']) + ' MM COP. En los meses pico quedan al límite: ' + bott_txt(d_opt['scen'][0]) + '.') if d_ref and d_opt else ''}</p>
<p><b>Qué aporta la superestructura ampliada.</b> {('Con la topología anterior (prensa, microfiltración del mosto y pasteurización), el mejor diseño da ' + n0(d_old['obj']) + ' MM COP/año con ' + n0(d_old['FCI']) + ' MM COP de equipos. Sin contar el vinagre, la superestructura ampliada sube el margen a ' + n0(d_novin['obj']) + ' (+' + n0(d_novin['obj'] - d_old['obj']) + ') con ' + n0(abs(d_old['FCI'] - d_novin['FCI'])) + (' MM COP menos de inversión' if d_old['FCI'] > d_novin['FCI'] else ' MM COP más de inversión') + '. La ganancia viene de ' + ('tres decisiones: (1) una clarificación por centrífuga o flotación pierde mucho menos jugo que la microfiltración del mosto, que con los datos de Quesada Salas deja el 27 % como retenido; (2) la microfiltración de lías recupera el ' + pct(dmod.LEES_REC, 0) + ' del jugo de los lodos de clarificación, ' + n0(d_novin['scen'][0]['products']['lias_MF_m3'] * dmod.LEES_REC) + ' m³/año de mosto; (3) el sulfitado reemplaza a la pasteurización.' if d_novin['scen'][0]['products']['lias_MF_m3'] > 0 else 'dos decisiones: (1) una clarificación por centrífuga o flotación pierde mucho menos jugo que la microfiltración del mosto, que con los datos de Quesada Salas deja el 27 % como retenido; (2) el sulfitado reemplaza a la pasteurización.') + ' Con el vinagre, el margen llega a ' + n0(d_opt['obj']) + ' MM COP/año (siguiente subsección). ') if d_old and d_opt and d_novin else ''}{('Si el mercado exige vino sin SO₂, el modelo vuelve a ' + d_noso2['sizes']['Estabilización'] + ' y el margen baja en ' + n0(d_opt['obj'] - d_noso2['obj']) + ' MM COP/año; la UHPH no se elige porque su energía de compresión a 300 MPa, unos 100 kWh/m³ con la electricidad diésel de la zona, cuesta unos 140 000 COP por m³ de mosto. ') if d_noso2 and d_opt else ''}{'La decantadora no se elige en ningún caso: con la oferta del Chocó una prensa de banda de 1 t/h dedicada a la pulpa es más barata y no tiene cambios de material.' if not dec_any else ''}</p>
<p><b>Prensas dedicadas o una compartida.</b> {('Reemplazar las dos prensas de 1 t/h por una sola de 3 t/h compartida cuesta más (FCI ' + n0(d_sh['FCI']) + ' frente a ' + n0(d_ref['FCI']) + ' MM COP) y rinde menos (' + n0(d_sh['obj']) + ' frente a ' + n0(d_ref['obj']) + ' MM COP/año): exige ' + n0(d_sh['scen'][0]['changeovers']) + ' cambios de material al año con su limpieza, y la fruta procesada no sube porque el cuello sigue en el frente. El cuello de la prensa compartida del programa anual se resuelve separando los materiales, no comprando una prensa más grande.') if d_sh and d_ref else ''} {('Si se exige procesar el 100 % de la fruta, el modelo cambia a una prensa compartida de ' + d_nl['sizes']['Prensa'] + ' y pierde ' + n0(d_opt['obj'] - d_nl['obj']) + ' MM COP/año frente al óptimo económico, que deja sin procesar el ' + pct(1 - absorbed(d_opt['scen'][0])) + ' de la fruta en los días pico.') if d_nl and d_opt else ''}</p>
</div>
{fig('fig29_flujos_almacen.png', 'Flujos e inventario', 'Fig. 29. Flujos mensuales del diseño óptimo (oferta, fruta procesada, mosto clarificado y fermentado) e inventario del pulmón de mosto, que el modelo deja en 10 m³.') if d_opt else ''}
{fig('fig30_gantt_optimo.png', 'Gantt del diseño óptimo', 'Fig. 30. Gantt anual del diseño óptimo: ocupación de cada equipo por periodo de la rejilla continua.') if d_opt else ''}
<h3>Versión 7: datos de piña y rutas de vinagre</h3>
<div class="prose">
<p><b>Calibración con Quesada Salas (2013).</b> La tesis de la Universidad de Costa Rica midió en planta piloto la microfiltración tangencial de jugo pulposo de piña con maceración enzimática previa. El jugo pulposo tiene 2 850–3 570 NTU y 10,5 % de sólidos insolubles, mucho más que un mosto de uva (400–3 000 NTU y 0,7–4 %). En ensayos de seis horas la membrana sostuvo 40–50 L/m²·h con un factor de reducción volumétrico de 3,7, es decir, el 73 % del jugo sale clarificado y el 27 % queda como retenido. La versión anterior suponía 60 L/m²·h y 2 % de retenido. Con los datos medidos, {('el diseño TRL-9 baja de ' + n0(v6('E1|Referencia TRL-9 (planta_trl9, 6 200 t)')) + ' a ' + n0(v7('E1|Referencia TRL-9 (planta_trl9, 6 200 t)')) + ' MM COP/año de margen y el mejor diseño con la topología anterior de ' + n0(v6('E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)')) + ' a ' + n0(v7('E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)')) + '. El óptimo sin vinagre baja de ' + n0(v6('E1|Óptimo económico')) + ' a ' + n0(v7('E1|Óptimo sin vinagre')) + ', porque los lodos de centrífuga también se escalaron con los sólidos de la piña (valores de la versión 7; los de la versión 9 están en la tabla de E1).') if dim6 and dim7 else ''} Los lodos y el retenido ya no van solo a compostaje: pueden ir al secador de la línea de harina, como recomienda la misma tesis. Quesada Salas también recomienda centrifugar antes de microfiltrar: es la secuencia que elige el MILP, con la microfiltración solo para las lías.</p>
<p><b>Rutas de vinagre (Emde 2017, Ullmann's; Bekatorou 2020).</b> El acetificador sumergido de Frings produce 40–60 kg de ácido acético por m³ y día, con un rendimiento cercano al teórico (46 g de etanol dan 60 g de ácido). La reacción libera 493 kJ/mol, que en el Chocó hay que retirar con frío, y la aireación no puede parar: cortes de 10–45 s bajan la productividad hasta 80 %, de modo que el grupo electrógeno de emergencia es obligatorio en una zona no interconectada. Bekatorou (cap. 14) describe vinagre al 5 % hecho con residuos de piña. Aquí se modelan dos rutas: (1) desviar vino terminado al acetificador y (2) fermentar el jugo de la prensa de cáscara (104 g/kg de azúcar), que hoy se vende al hub a 150 COP/kg, y acetificarlo; el jugo prensado no necesita la sacarificación enzimática de Roda et al., que es más del 90 % del costo.</p>
<p>{('Con vino a 3 000 COP/L y vinagre a ' + n0(dmod.VIN_PRICE) + ' COP/L, el óptimo agrega un acetificador de ' + d_opt['sizes']['Acetificador'] + ' y una bodega de jugo de cáscara de ' + d_opt['sizes']['Bodega cáscara'] + '. Desvía ' + n0(d_opt['scen'][0]['products']['vino_a_vinagre_m3']) + ' m³/año de vino y ' + n0(d_opt['scen'][0]['products']['jugo_cascara_vinagre_t']) + ' t/año de jugo de cáscara, y produce ' + n0(d_opt['scen'][0]['products']['vinagre_m3']) + ' m³/año de vinagre al 5 %. El margen sube de ' + n0(d_novin['obj']) + ' a ' + n0(d_opt['obj']) + ' MM COP/año con ' + n0(d_opt['FCI'] - d_novin['FCI']) + ' MM COP más de equipos. ' + ('La razón es simple: un m³ de vino da unos 1,6 m³ de vinagre, que a ' + n0(dmod.VIN_PRICE) + ' COP/L vale más que el vino a 3 000 COP/L y no necesita 90 días de guarda.' if d_opt['scen'][0]['products']['vino_a_vinagre_m3'] > 1 else 'No desvía vino: embotellado vale más que como vinagre, y el vinagre sale de los jugos de cáscara y de hojas (' + n0(d_opt['scen'][0]['products'].get('jugo_hojas_vinagre_t', 0)) + ' t/año) con panela.')) if d_opt and d_novin and d_opt['sizes'].get('Acetificador', 'no') != 'no' else ''}</p>
<p><b>El resultado depende del precio del vinagre, que es un supuesto.</b> El barrido siguiente resuelve el MILP con cuatro precios del vino y dos del vinagre. El volumen de vinagre del óptimo, unos 3 millones de litros al año, habría que contrastarlo con el mercado colombiano de vinagre de frutas a granel antes de tomarlo como base de diseño.</p>
</div>
{table(['Vino: neto por litro (COP/L)', 'Vinagre (COP/L)', 'Acetificador', 'Bodega de cáscara', 'Vino vendido (m³)', 'Vino a vinagre (m³)', 'Jugo de cáscara a vinagre (t)', 'Vinagre (m³)', 'Margen (MM COP/año)'], e6_rows, num_cols=(0, 1, 4, 5, 6, 7, 8)) if e6_rows else ''}
{fig('fig32_vinagre_precios.png', 'Vinagre y precios', 'Fig. 32. Destino del vino según los precios del vino y del vinagre, acetificador elegido y VPN del diseño óptimo de cada par de precios.') if e6_rows else ''}
{fig('fig34_balance_masa.png', 'Balance de masa ilustrado', 'Fig. 34. Balance de masa del diseño óptimo (t/año): el ancho de cada corriente es proporcional a su masa. El agua de dilución del vinagre cierra el balance; la corona quemada sale por la caldera. Abajo, las hojas de la planta (v10): jugo a la bodega de jugos y pulpa devuelta al campo.') if d_opt else ''}
{fig('fig35_balance_energia.png', 'Balance de energía ilustrado', 'Fig. 35. Balance de energía del diseño óptimo (GJ/año): electricidad de grupo electrógeno diésel, calor de proceso con caldera de corona y GLP, y calores de reacción retirados por los chillers.') if d_opt else ''}
{fig('fig36_pfd.png', 'Diagrama de flujo del proceso', 'Fig. 36. Diagrama de flujo del proceso del diseño óptimo: equipos con su código y tamaño, corrientes numeradas y tabla de corrientes (t/año y condiciones de operación); en la v10, la extractora de hojas EX-101 alimenta la bodega de jugos F-201. Calor en terracota discontinua; los chillers atienden los equipos marcados con ❄.') if d_opt else ''}
{fig('fig37_layout.png', 'Layout conceptual de la planta', 'Fig. 37. Layout conceptual de la planta (vista en planta, escala aproximada, lote de 70 × 45 m): doce zonas por función, huellas de equipos del diseño óptimo (tanques con H = 1,5·D) y recorridos de fruta, torta, corona, vino, vinagre, harina, residuos y aguas residuales. Distribución conceptual; la ingeniería de detalle debe verificar retiros, viento dominante y normativa sanitaria.') if d_opt else ''}
{fig('fig38_gantt.png', 'Gantt del diseño óptimo dibujado a mano', 'Fig. 38. Gantt del diseño óptimo. A: oferta de fruta y ocupación mensual de cada equipo (óvalo: ≥ 95 %). B: semana de abril con dos turnos de 6 h efectivos de lunes a sábado, extractora de hojas, fermentadores de vino y de jugos (cáscara y hojas) desfasados según Moresi (llenado V_F/Q, fermentación, descarga), acetificador semicontinuo (descarga del 50 % cada ≈ 18 h) y secador y caldera de corona continuos con parada dominical.') if d_opt else ''}
<div class="prose"><p><b>Bromelaína (Vasiljevic 2020).</b> El capítulo confirma la ruta de membranas para bromelaína cruda y propone ultrafiltración en dos etapas con membranas cerámicas (75 kDa y 10 kDa, a pH 7 y hasta 40 °C), que en Nor et al. (2016) recuperó el 96,8 % de la enzima y subió la pureza 2,5 veces. También reporta que la corona tiene la mayor actividad proteolítica de los residuos (Ketnawa et al. 2012). No se agregaron al MILP porque faltan dos datos: el precio de la bromelaína según su pureza y la actividad por kilogramo de corona de la variedad del Chocó. Con esos dos datos, la segunda etapa de UF y la corona como fuente de bromelaína (compitiendo con la caldera) entran como opciones de la superestructura.</p></div>
<h3>Versión 8: caldera de corona</h3>
<div class="prose"><p>{(('El balance de energía mostró que la corona, que el óptimo de la versión 7 mandaba a compost, podía cubrir casi todo el calor del secado. Se agregó a la superestructura una caldera de biomasa con corona (100–500 kWt, con picadora y secador de corona) que reemplaza GLP. El óptimo elige ' + ('una caldera de ' + d_opt['sizes'].get('Caldera de corona', 'no') + ', quema ' + n0(d_opt['scen'][0]['products'].get('corona_caldera_t', 0)) + ' t/año de corona y entrega ' + n0(d_opt['scen'][0]['products'].get('calor_corona_GJ', 0)) + ' GJ/año de calor' if d_opt['sizes'].get('Caldera de corona', 'no') != 'no' else 'no instalarla') + ('. Frente al mismo modelo sin caldera, el margen sube de ' + n0(d_nob['obj']) + ' a ' + n0(d_opt['obj']) + ' MM COP/año con ' + n0(d_opt['FCI'] - d_nob['FCI']) + ' MM COP más de equipos. ' if d_opt['sizes'].get('Caldera de corona', 'no') != 'no' else ': con la planta topada por la demanda, el secador es pequeño y su calor no paga la caldera (la de 100 kWt sí entraba en las versiones 8 a 11). ')) if d_opt and d_nob else '')}{('El MILP terminó por tiempo con una brecha de ' + pct(d_opt['gap'] or 0, 1) + ': con la caldera, la relajación lineal se debilita y SCIP no alcanza a cerrar la cota. Para que parta de una solución buena, cada corrida se inicia con la solución de la versión anterior, que es factible; la solución reportada es al menos tan buena como esa. Después, cada caso se pulió evaluando con tamaños fijos los diseños vecinos (cada tamaño de caldera y los de los casos hermanos; <code>pulido_v8.py</code> y, en la versión 9, <code>pulido_v9.py</code>), lo que corrigió soluciones inconsistentes, como un caso libre peor que uno restringido. La optimalidad no está demostrada: las brechas que se reportan se miden contra la cota de la corrida libre.') if d_opt and (d_opt.get('gap') or 0) > 0.01 else ''}</p></div>
{v9_html}
{v10_html}
{v11_html}
{v12_html}
<h3>Regla de dimensionamiento según la oferta</h3>
<div class="prose"><p>Se resolvió el mismo modelo desde la mitad de la oferta actual hasta la base de la tesis (21 856 t/año), con libertad total de tamaños, almacén y turnos:</p></div>
{table(['Oferta (t/año)', 'Tamaños óptimos', 'FCI (MM COP)', 'Margen (MM COP/año)', 'FCI por t/año (miles COP)', 'Fruta procesada', 'Cuellos (≥ 95 %)'], dim_e2, num_cols=(0, 2, 3, 4, 5)) if dim_e2 else ''}
{fig('fig28_escala_dimensionamiento.png', 'Dimensionamiento por escala', 'Fig. 28. Tamaño óptimo de cada equipo y ocupación del mes pico según la oferta; economía de escala; valor del almacén aséptico y del tercer turno a 2× la oferta actual.') if dim_e2 else ''}
<div class="prose">
<p><b>Lectura.</b></p>
<ul class="tight">
<li><b>Los equipos del frente se dimensionan por el mes pico.</b> Frente, prensas y clarificación trabajan con personal y siguen a la fruta, que es perecedera (3 días de patio). La bodega y el secador operan 24/7 y quedan con el mínimo de unidades que cubre el pico: 2 fermentadores de 10 m³ hasta 2× la oferta actual y 3 desde 2,5×. El secador crece en escalones con la cáscara.</li>
<li><b>Prensas dedicadas desde unas 4 600 t/año (0,75× la oferta).</b> Por debajo de esa oferta conviene una sola prensa compartida (dos prensas cuestan más que los cambios). Por encima, siempre se separan pulpa y cáscara.</li>
<li><b>El tercer turno pierde peso.</b> {('Con la superestructura ampliada solo se elige a ' + (', '.join(t3_at[:-1]) + ' y ' + t3_at[-1] if len(t3_at) > 1 else t3_at[0]) + ' la oferta actual, donde cuesta casi lo mismo que el frente y las prensas del tamaño siguiente; en las demás escalas conviene comprar el equipo.') if t3_at else 'Con la superestructura ampliada no se elige en ninguna escala.'}</li>
<li><b>Tecnología del mosto por escala.</b> {('La microfiltración del mosto no se elige en ninguna escala. ' if not mfmust_any else '') + ('La flotación gana a ' + ', '.join(flot_at) + ' y la centrífuga a ' + ', '.join(cent_at) + ' la oferta: cuestan casi lo mismo y la elección depende de cómo encaja cada tamaño de catálogo. ' if flot_at and cent_at else '') + ('La microfiltración de lías y el sulfitado se eligen en todas las escalas. ' if lees_all and so2_all else '') + ('La decantadora no se elige en ninguna. ' if not dec_any else '') + ('El acetificador se elige en todas las escalas, de ' + min((r['sizes']['Acetificador'] for f, r in e2r), key=lambda x: float(x.split()[0])) + ' a ' + max((r['sizes']['Acetificador'] for f, r in e2r), key=lambda x: float(x.split()[0])) + ', con el precio supuesto del vinagre.' if e2r and all(r['sizes'].get('Acetificador', 'no') != 'no' for f, r in e2r) else '')}</li>
<li><b>El almacén aséptico de mosto no se elige en ninguna escala.</b> Nivelaría la bodega guardando el exceso de mosto de los meses pico, unos 50–100 m³ a la escala actual. Un tanque aséptico de ese volumen cuesta más que el fermentador adicional que hace lo mismo, y el cuello estacional está aguas arriba, donde la fruta no se puede almacenar. {('A 2× la oferta, prohibir el almacén, el tercer turno o ambos no cambia el óptimo (tabla siguiente).' if e3_same else 'A 2× la oferta, prohibir el almacén no cambia nada (tabla siguiente).')} Nivelar la estacionalidad exigiría almacenar pulpa congelada o fruta en cámara, que no es TRL-9 para fruta de rechazo a esta escala.</li>
<li><b>Economía de escala.</b> El FCI por tonelada procesada al año baja de unos {n0(dim_e2 and min(float(r[4].replace(' ', '')) for r in dim_e2[:1]))} a unos {n0(dim_e2 and float(dim_e2[-1][4].replace(' ', '')))} miles de COP entre los extremos del barrido.</li>
</ul>
</div>
{table(['Palancas a 2× la oferta', 'Tamaños', 'FCI (MM COP)', 'Margen (MM COP/año)', 'Fruta procesada'], dim_e3, num_cols=(2, 3, 4)) if dim_e3 else ''}
<h3>Dimensionamiento estocástico (Grossmann cap. 14)</h3>
<div class="prose"><p>Los tamaños son de primera etapa y la operación anual de segunda etapa, en tres escenarios de oferta (0,7×, 1,0× y 1,3× la oferta actual, con probabilidades 0,25, 0,50 y 0,25, como en el programa estocástico de §6.7).</p></div>
{table(['Problema', 'Tamaños', 'Margen esperado (MM COP/año)'], dim_e4, num_cols=(2,)) if dim_e4 else ''}
<div class="prose"><p>{(('El problema estocástico elige los mismos equipos que el de valor medio. ' if dim['E4|RP']['sizes'] == dim['E4|EV']['sizes'] and dim['E4|RP']['turno3'] == dim['E4|EV']['turno3'] else 'Frente a los tres escenarios, el problema estocástico cambia ' + '; '.join(u + ' ' + dim['E4|RP']['sizes'][u] + ' en lugar de ' + dim['E4|EV']['sizes'][u] for u in dim['E4|RP']['sizes'] if dim['E4|RP']['sizes'][u] != dim['E4|EV']['sizes'].get(u)) + '. ') + ('Con los tamaños del valor medio (EEV) se pierde el ' + pct(1 - sum(x['supply'] * x['p'] - x['loss'] * x['p'] for x in dim['E4|EEV']['scen']) / sum(x['supply'] * x['p'] for x in dim['E4|EEV']['scen'])) + ' de la fruta esperada, porque en el escenario alto el frente y las prensas saturan. ' if abs(dim['E4|WS']['obj'] - dim['E4|RP']['obj']) > 0.005 * abs(dim['E4|RP']['obj']) else 'Con el vino y el vinagre topados por la demanda, la oferta de fruta no es la restricción activa: el diseño procesa la misma fruta en los tres escenarios y la que queda sin procesar no se pierde por falta de capacidad, sino porque no hay mercado para más vino ni vinagre. ') + 'El VSS es de ' + n0(max(dim['E4|RP']['obj'] - dim['E4|EEV']['obj'], 0)) + ' MM COP/año y el EVPI de ' + n0(max(dim['E4|WS']['obj'] - dim['E4|RP']['obj'], 0)) + ' MM COP/año. ' + (('El problema estocástico terminó por tiempo con una brecha de ' + pct(dim['E4|RP']['gap'], 1) + ' (unos ' + n0(dim['E4|RP']['gap'] * dim['E4|RP']['obj']) + ' MM COP/año), mayor que el VSS, así que con este presupuesto de cómputo el VSS no se distingue de cero. ') if dim['E4|RP']['gap'] * dim['E4|RP']['obj'] > abs(dim['E4|RP']['obj'] - dim['E4|EEV']['obj']) else '') + ('El valor medio promete ' + n0(dim['E4|EV']['obj']) + ' MM COP/año y su diseño rinde en realidad ' + n0(dim['E4|EEV']['obj']) + ': el mismo sesgo del valor medio de §6.7.' if dim['E4|EEV']['obj'] < dim['E4|EV']['obj'] - 0.005 * abs(dim['E4|EV']['obj']) else 'El diseño del valor medio rinde lo mismo en los tres escenarios (' + n0(dim['E4|EEV']['obj']) + ' MM COP/año): sin la oferta como restricción, desaparece el sesgo del valor medio de §6.7.')) if dim_e4 else ''}</p></div>
<h3>Configuración con bromelaína</h3>
{table(['Diseño', 'Tamaños', 'FCI (MM COP)', 'Margen (MM COP/año)', 'Fruta procesada', 'Bromelaína (kg)', 'Cuellos (≥ 95 %)'], dim_e5, num_cols=(2, 3, 4, 5)) if dim_e5 else ''}
<div class="prose"><p>{('Con la bromelaína disponible, el óptimo no la produce: elige un diseño sin secador por aspersión y da ' + n0(b1x['obj']) + ' MM COP/año, prácticamente lo mismo que la configuración A (' + n0(d_opt['obj']) + '). Con el vino y el vinagre topados por la demanda, la planta procesa poca fruta y el corazón no alcanza para pagar el módulo de bromelaína. El diseño TRL-9 con tres prensas dedicadas queda en ' + n0(b0x['obj']) + ' MM COP/año.') if b1x and b0x and b1x['sizes'].get('Aspersión', 'no') == 'no' else ''}{('Con bromelaína y la superestructura ampliada, el óptimo usa un frente de ' + b1x['sizes']['Frente'] + ', una prensa de ' + b1x['sizes']['Prensa'] + ' compartida entre pulpa y corazón (' + n0(b1x['scen'][0]['changeovers']) + ' cambios al año), una prensa dedicada de cáscara de ' + b1x['sizes']['Prensa cáscara'] + ' y un secador por aspersión de ' + b1x['sizes']['Aspersión'] + (', con tercer turno' if b1x['turno3'] else ', sin tercer turno') + '. Procesa ' + pct(absorbed(b1x['scen'][0])) + ' de la fruta y ' + n0(b1x['scen'][0]['products']['bromelaina_kg']) + ' kg de bromelaína. El margen es ' + n0(b1x['obj']) + ' MM COP/año: ' + n0(b1x['obj'] - d_opt['obj']) + ' más que el óptimo sin bromelaína y ' + n0(b1x['obj'] - b1o['obj']) + ' más que el óptimo con la topología anterior (' + n0(b1o['obj']) + '), ' + ('que necesitaba una sola prensa para los tres materiales y tercer turno' if (b1o['sizes'].get('Prensa cáscara') == 'no' or b1o.get('turno3')) else 'que conserva la clarificación por MF y la pasteurización') + '. El diseño TRL-9 con tres prensas dedicadas queda en ' + n0(b0x['obj']) + ' MM COP/año y pierde el ' + pct(1 - absorbed(b0x['scen'][0])) + ' de la fruta.') if b1x and b1o and b0x and d_opt and b1x['sizes'].get('Aspersión', 'no') != 'no' else ''}</p></div>
<div class="prose">
<p><b>Cómo incluirlo en la tesis.</b> Se propone un apartado nuevo en el capítulo de diseño, después del diseño TRL-9 (§4.x «Dimensionamiento óptimo de equipos y balance de flujos»), con cuatro partes:</p>
<ol class="tight">
<li>la formulación disyuntiva y su linealización (tres ecuaciones y la tabla de opciones de catálogo con sus costos), con la superestructura de tecnologías del mosto de <i>White Wine Technology</i>;</li>
<li>la comparación con el diseño TRL-9 (tabla de E1 y Fig. 27);</li>
<li>la regla de dimensionamiento por escala (tabla de E2 y Fig. 28), que responde qué cambia si la oferta crece;</li>
<li>el dimensionamiento estocástico, que enlaza con §6.7.</li>
</ol>
<p>El TEA de Burk debe recalcularse con los tamaños óptimos; los libros de <code>TEA_excel/</code> aceptan la nueva lista de equipos sin cambiar su estructura.</p>
</div>
</section>


<section id="tea-dim">
<h2>TEA de Burk con los tamaños óptimos</h2>
<div class="prose">
<p>El margen del dimensionamiento es un criterio de decisión, no un indicador financiero: no incluye nómina, impuestos, depreciación ni capital de trabajo. Para confirmar la elección se recalculó el TEA completo de Burk (<code>tea_dimensionado.py</code>) con los equipos elegidos por el MILP y la operación anual de cada diseño:</p>
<ul class="tight">
<li><b>Equipos:</b> la lista de catálogo de cada opción elegida, con sus equipos acompañantes, más los que no dependen del dimensionamiento: tanques de guarda de 90 días para el vino del año, cuarto frío y empacadoras. El CapEx sigue la plantilla (instalación 1,3; no listados 10 %; flete 5 %; OSBL 0,23; obra civil 0,15; EPC 0,30; contingencia 0,20).</li>
<li><b>Producción:</b> la del programa anual de cada diseño (fruta realmente procesada, vino, harina, bromelaína), no la nominal. Consumos y servicios salen del balance de masa a esa fruta.</li>
<li><b>Materia prima:</b> toda la fruta procesada a 400 COP/kg, más el compostaje de corona, corazón sin uso y cáscara no secada a 30 COP/kg.</li>
<li><b>Personal:</b> calendario de lunes a sábado con 2 turnos, o con 3 si el MILP eligió el tercer turno. Personal compartido al 75 % y uno o dos ingenieros de planta, como en el TEA integrado.</li>
<li><b>Precios:</b> {('vino embotellado a precio de fábrica (' + n0(dmod.wine_bottle()['fabrica']) + ' COP por botella de 750 mL, con el impuesto al consumo como costo y el empaque como materia prima; versión 12)' if dmod.BOTTLED else 'vino a 3 000 COP/L (el precio de nicho del plan del MILP)')}; harina, jugo de cáscara, bromelaína y polvo como subproductos. Tornado y Monte Carlo (LHS con Iman–Conover, ρ = 0,45 entre precio y materia prima, 1 000 corridas) con las distribuciones de la plantilla.</li>
</ul>
</div>
{table(['Caso', 'Fruta (t/año)', 'FCI', 'Ingresos', 'Costos variables', 'Costos fijos', 'VPN', 'MIRR', 'Recuperación (años)', ('Precio de equilibrio del vino (COP/botella, fábrica)' if dmod.BOTTLED else 'Precio de equilibrio del vino (COP/L)'), 'Precio de equilibrio del vinagre (COP/L)', 'P(VPN > 0)'], tdim_rows, num_cols=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)) if tdim else ''}
<div class="prose"><p class="small">Valores monetarios en MM COP de 2026 salvo indicación. Los tamaños de cada caso están en las tablas del dimensionamiento. En los casos con vinagre, el vino pasa a ser un producto menor y su precio de equilibrio deja de ser informativo; ahí se reporta el del vinagre. En esos casos el tornado y el Monte Carlo también varían el precio del vinagre (±30 %, independiente del vino); los libros Excel conservan los cinco parámetros de la plantilla.</p></div>
{fig('fig31_tea_dimensionado.png', 'TEA con tamaños óptimos', 'Fig. 31. TEA de Burk con los tamaños de referencia y óptimos: inversión, VPN y MIRR; Monte Carlo; tornado del mejor caso; VPN y precio de equilibrio del vino del diseño óptimo según la oferta.') if tdim else ''}
<div class="prose">
<p><b>Lectura.</b></p>
<ul class="tight">
<li><b>El TEA completo confirma el orden del MILP.</b> {('Con vino + harina, el VPN pasa de ' + n0(tA0['res']['NPV'] / MM) + ' MM COP en el diseño TRL-9 a ' + n0(tAo['res']['NPV'] / MM) + ' con los tamaños óptimos de la topología anterior y a ' + n0(tA1['res']['NPV'] / MM) + ' con la superestructura ampliada (MIRR ' + pct(tA0['res']['MIRR']) + ' → ' + pct(tAo['res']['MIRR']) + ' → ' + pct(tA1['res']['MIRR']) + '). El FCI ' + ('baja' if tA1['res']['FCI'] < tA0['res']['FCI'] else 'sube') + ' de ' + n0(tA0['res']['FCI'] / MM) + ' a ' + n0(tA1['res']['FCI'] / MM) + ' MM COP y la probabilidad de VPN positivo sube de ' + pct(tA0['mc']['P_pos'], 0) + ' a ' + pct(tA1['mc']['P_pos'], 0) + '. Sin SO₂ (pasteurización flash), el VPN queda en ' + n0(tAn['res']['NPV'] / MM) + ' MM COP.' + ((' Sin las rutas de vinagre, el óptimo da VPN de ' + n0(tAv['res']['NPV'] / MM) + ' MM COP (MIRR ' + pct(tAv['res']['MIRR']) + ', P(VPN > 0) = ' + pct(tAv['mc']['P_pos'], 0) + '): el vinagre aporta ' + n0((tA1['res']['NPV'] - tAv['res']['NPV']) / MM) + ' MM COP de VPN con el precio supuesto de ' + n0(dmod.VIN_PRICE) + ' COP/L.') if tAv else '') + ((' Sin la caldera de corona, el VPN es ' + n0(tAb['res']['NPV'] / MM) + ' MM COP: la caldera aporta ' + n0((tA1['res']['NPV'] - tAb['res']['NPV']) / MM) + ' MM COP.') if tAb and abs(tA1['res']['NPV'] - tAb['res']['NPV']) > 0.5 * MM else (' El óptimo no lleva caldera de corona.' if tAb else ''))) if tA0 and tAo and tA1 and tAn else ''}</li>
<li><b>Con bromelaína.</b> {('El diseño TRL-9 con tres prensas dedicadas da VPN de ' + n0(tB0['res']['NPV'] / MM) + ' MM COP. El óptimo con la topología anterior sube a ' + n0(tBo['res']['NPV'] / MM) + (' con tercer turno' if tBo.get('turno3') else '') + ', y el de la superestructura ampliada a ' + n0(tB1['res']['NPV'] / MM) + (' con tercer turno' if tB1.get('turno3') else ' sin tercer turno') + ' (MIRR ' + pct(tB1['res']['MIRR']) + ', recuperación en ' + n1(tB1['res']['payback']) + ' años, P(VPN > 0) = ' + pct(tB1['mc']['P_pos'], 0) + '). La bromelaína suma ' + n0((tB1['res']['NPV'] - tA1['res']['NPV']) / MM) + ' MM COP de VPN sobre el óptimo de vino + harina, con ' + n0((tB1['res']['FCI'] - tA1['res']['FCI']) / MM) + ' MM COP más de inversión' + (': es el mejor caso, pero su ventaja es pequeña frente a la incertidumbre del precio del vino.' if tB1['res']['NPV'] > tA1['res']['NPV'] + 0.5 * MM else ': con la demanda topada, el óptimo B no separa bromelaína y coincide con el de vino + harina.')) if tB0 and tBo and tB1 and tA1 else ''}</li>
<li><b>{('El precio del vinagre manda.' if tB1 and tB1['tornado'][0]['label'] == 'Precio del vinagre' else 'El precio del vino sigue mandando.')}</b> {('En el tornado del mejor caso, el VPN solo se vuelve negativo con ' + ' o '.join({'Precio del producto': 'el vino un 30 % más barato', 'Precio del vinagre': 'el vinagre un 30 % más barato', 'Costo de la materia prima principal': 'la fruta un 50 % más cara', 'CapEx (±30 %)': 'un CapEx un 30 % mayor', 'Tasa de descuento': 'una tasa de descuento del 18 %', 'Factor de producción': 'la producción al 80 %', 'Rendimiento del jugo de cáscara (0,23–0,43 g/g)': 'el jugo de cáscara fermentando a 0,23 g/g', 'Corona que llega a planta (40–100 %)': 'solo el 40 % de la corona en planta'}[t['label']] + ' (' + n0(t['NPV_worst'] / MM) + ' MM COP)' for t in tB1['tornado'] if t['NPV_worst'] < 0) + '. ' + (('Con las rutas de vinagre, el precio de equilibrio del vinagre es ' + n0(tB1['breakeven_vinegar']) + ' COP/L con bromelaína y ' + n0(tA1['breakeven_vinegar']) + ' COP/L sin ella, frente al supuesto de ' + n0(dmod.VIN_PRICE) + ' COP/L: un ' + pct(1 - tA1['breakeven_vinegar'] / dmod.VIN_PRICE, 0) + ' de margen de error en el precio que más pesa.' + (' Sin vinagre, el precio de equilibrio del vino es ' + n0(tAv['breakeven']) + ' COP por botella a precio de fábrica, frente a ' + n0(dmod.wine_bottle()['fabrica']) + ' COP supuestos.' if dmod.BOTTLED else ' Sin vinagre, el precio de equilibrio del vino es ' + n0(tAv['breakeven']) + ' COP/L, por encima de los 1 600 COP/L de los TEA por línea.')) if tA1.get('breakeven_vinegar') and tB1.get('breakeven_vinegar') and tAv else ('El precio de equilibrio es ' + n0(tB1['breakeven']) + ' COP/L con bromelaína y ' + n0(tA1['breakeven']) + ' COP/L sin ella; los dos están por encima del precio base de los TEA por línea (1 600 COP/L).'))) if tA1 and tB1 else ''}</li>
<li><b>Escala mínima.</b> {('Con el vino y el vinagre topados por la demanda, el VPN no depende de la oferta de fruta: ' + n0(min(x['NPV'] for x in tdim['scale']) / MM) + '–' + n0(max(x['NPV'] for x in tdim['scale']) / MM) + ' MM COP en todo el barrido (' + n0(tdim['scale'][0]['supply']) + ' a ' + n0(tdim['scale'][-1]['supply']) + ' t/año). La escala la fija el mercado, no la fruta.') if tdim and tdim.get('scale') and min(x['NPV'] for x in tdim['scale']) > 0 else ''}{('Con los tamaños óptimos de cada oferta, el VPN es negativo a ' + n0(tdim['scale'][0]['supply']) + ' t/año y positivo desde ' + n0(viable) + ' t/año de fruta; el umbral está entre esos dos puntos del barrido, por debajo de la oferta actual del Chocó. A la base de la tesis (21 856 t/año), el VPN llega a ' + n0(tdim['scale'][-1]['NPV'] / MM) + ' MM COP' + ((' y el precio de equilibrio del vinagre baja a ' + n0(tdim['scale'][-1]['breakeven_vinegar']) + ' COP/L') if tdim['scale'][-1].get('breakeven_vinegar') else '') + '.') if tdim and viable and min(x['NPV'] for x in tdim['scale']) <= 0 else ''}</li>
</ul>
<p><b>Diferencias con el TEA del plan de la versión 2.</b> {('El plan vino + harina del MILP (Chocó 2022) tenía VPN de ' + n0(old_plan['NPV'] / MM) + ' MM COP con FCI de ' + n0(old_plan['FCI'] / MM) + '. El caso de referencia de esta sección da ' + n0(tA0['res']['NPV'] / MM) + ' MM COP porque corrige tres cosas: (1) la producción sale del programa anual (el diseño TRL-9 procesa ' + n0(tA0['fruit_t']) + ' t, no 6 146); (2) el plan anterior heredaba del diseño el desvío del 16 % del vino a vinagre aunque la línea de vinagre no estaba en el plan, de modo que ese vino no se vendía; ahora se vende todo; (3) antes la fruta se cobraba solo por las fracciones asignadas a cada línea (pulpa y cáscara, el 75 %), y ahora se cobra toda la fruta más el compostaje de lo que no se usa. Las correcciones (2) y (3) van en sentidos opuestos. Además, desde la versión 6 todos los casos incluyen nutrientes (DAP), inertización con N₂, el retenido de la clarificación y el compostaje de lías; por eso el diseño TRL-9 pasa de 763 MM COP en la versión 5 a ' + n0(tA0['res']['NPV'] / MM) + ' aquí.') if old_plan and tA0 else ''}</p>
</div>
<h3>TEA del diseño óptimo por escala</h3>
{table(['Oferta (t/año)', 'Tamaños', 'FCI (MM COP)', 'VPN (MM COP)', 'MIRR', 'Vinagre (m³/año)', 'Precio de equilibrio del vinagre (COP/L)'], tdim_scale, num_cols=(0, 2, 3, 4, 5, 6)) if tdim else ''}
<h3>Libros Excel</h3>
<div class="prose"><p>Los {len(tdim['cases']) if tdim else ''} casos de Chocó 2022 se exportaron a <code>TEA_excel/</code> con la estructura de los libros de asaí y coco (Inicio, Tablero, Modelo del proceso, Costos de Equipos, CapEx, OpEx &amp; Ingresos, Flujo de Caja, Tornado, Break-Even, Monte Carlo), con fórmulas vivas, y se recalcularon en LibreOffice. En la exportación se corrigió un detalle: un residuo distinto de las aguas residuales (aquí, el compostaje) tomaba la tarifa de aguas residuales. Los once libros anteriores no tenían otros residuos, así que no cambian.</p></div>
{table(['Libro', 'VPN Python (MM COP)', 'VPN Excel (MM COP)', 'Diferencia relativa'], tdim_chk, num_cols=(1, 2, 3)) if tdim else ''}
</section>

<section id="tesis2">
<h2>Cambios que sugiere a la tesis (versión 2)</h2>
<ol class="edits prose">
<li><b>§4.2.5, tiempo de parada.</b> Los 78–81 h de la Tabla 3 de Moresi no son un "punto de parada de costo mínimo". Son el tiempo para consumir el 85 % del azúcar, el criterio fijo de su paso 2.</li>
<li><b>§4.2.5, intercambiadores.</b> En Moresi, los 4 y 10 intercambiadores sirven a 26 y 69 fermentadores abiertos. La bodega de 5 fermentadores es cerrada, con camisa y sin intercambiador. Hay que corregir "cuatro a diez intercambiadores para cinco a sesenta y nueve fermentadores".</li>
<li><b>§4.2.5, ventaja premium.</b> Reemplazar "+15,4 % de etanol por conversión casi completa" por la descomposición de la Fig. 17: +15,1 % por cambio de modelo y +1,3 % por conversión.</li>
<li><b>§4.2.3 y §4.2.5, validez térmica.</b> Declarar que la cinética de Moresi solo vale entre 15 y 25 °C y no describe la línea rápida a 30 °C.</li>
<li><b>§3.3 y §3.5, base de diseño.</b> Actualizar la oferta con la EVA 2022 (6 146 t) y declarar que la base de 78 300 hL/año exige unas 21 900 t/año de fruta, 3,6 veces la producción del departamento. O se redimensiona la planta, o se justifica el abastecimiento con fruta de fuera del Chocó.</li>
<li><b>Cap. 5, energía.</b> Para un diseño TRL-9, la caldera de biomasa de corona cubre el calor de secado y la gasificación no. Conviene presentar la gasificación como alternativa TRL 8. {('En el dimensionamiento de la versión 10, la caldera de corona (' + d_opt['sizes'].get('Caldera de corona', 'no') + ') entrega ' + n0(d_opt['scen'][0]['products'].get('calor_corona_GJ', 0)) + ' GJ/año y desplaza casi todo el GLP.') if d_opt and d_opt['sizes'].get('Caldera de corona', 'no') != 'no' else ''}</li>
<li><b>Cap. 8, TEA.</b> Adoptar la estructura de los TEA de asaí y coco (libros en <code>TEA_excel/</code>) y reportar el precio de equilibrio del vino (≈2 300 COP/L a la escala de la tesis) junto al precio "ilustrativo" de 400 USD/t.</li>
<li><b>Cap. 8, TEA con tamaños óptimos.</b> Evaluar la planta con los equipos del dimensionamiento y la producción del programa anual, no con la nominal. {(('Con la oferta actual, el mejor caso es vino + harina + bromelaína con la superestructura ampliada (VPN ≈ ' + n0(tB1['res']['NPV'] / MM) + ' MM COP, MIRR ' + pct(tB1['res']['MIRR']) + ', P(VPN > 0) = ' + pct(tB1['mc']['P_pos'], 0) + '), seguido muy de cerca por vino + harina (' + n0(tA1['res']['NPV'] / MM) + ' MM COP).') if tB1['res']['NPV'] > tA1['res']['NPV'] + 0.5 * MM else ('Con la oferta actual y el vino embotellado, el mejor caso es el óptimo con vinagre y la superestructura ampliada (VPN ≈ ' + n0(tA1['res']['NPV'] / MM) + ' MM COP, MIRR ' + pct(tA1['res']['MIRR']) + ', P(VPN > 0) = ' + pct(tA1['mc']['P_pos'], 0) + '); la bromelaína no agrega valor con la demanda topada.')) if tdim and tB1 and tA1 else ''} Cobrar toda la fruta procesada, no solo las fracciones asignadas a cada línea.</li>
<li><b>§4.2.1 y §4.2.3, microfiltración del jugo de piña.</b> Usar los valores medidos por Quesada Salas (2013), la misma fuente del rendimiento de prensado de la tesis: 40–50 L/m²·h sostenidos y 73 % de jugo clarificado (FRV 3,7), no 60 L/m²·h sin retenido. Con esos valores, la microfiltración del mosto completo no es competitiva frente a centrífuga + microfiltración de lías, y el retenido debe ir a la línea de harina.</li>
<li><b>§4.3, vinagre.</b> Rediseñar la línea con el acetificador de Frings (Emde 2017: 40–60 kg/m³·d, frío, grupo electrógeno de emergencia) y evaluar el jugo de la prensa de cáscara como materia prima del vinagre (Bekatorou 2020). {('Con vinagre a ' + n0(dmod.VIN_PRICE) + ' COP/L, el vinagre es la salida más rentable del vino; el precio del vinagre de frutas a granel y el tamaño de su mercado son ahora los datos que más pesan en la decisión.') if d_opt and d_opt['sizes'].get('Acetificador', 'no') != 'no' else ''}</li>
<li><b>§4.2.3–4.2.4, tratamiento del mosto.</b> Reemplazar la microfiltración del mosto por flotación o centrífuga de discos, con microfiltración de lías para recuperar el jugo, y declarar la turbidez objetivo (100–200 NTU, Morata 2022, cap. 8). Justificar la estabilización (SO₂, pasteurización o UHPH) y agregar la dosificación de nitrógeno asimilable y la inertización con N₂ (caps. 12, 23 y 25).</li>
<li><b>§6.7, incertidumbre.</b> Reportar RP, EEV, VSS y EVPI junto al CVaR. Con la oferta actual, el VSS es {n0(max(dim['E4|RP']['obj'] - dim['E4|EEV']['obj'], 0)) if 'E4|RP' in dim else '0'} y el EVPI de unos {n0(max(dim['E4|WS']['obj'] - dim['E4|RP']['obj'], 0)) if 'E4|WS' in dim else '—'} MM COP/año. Lo que justifica medir antes de invertir es el sesgo del valor medio (+43 %) y la conmutación en λ* ≈ 0,2, más que la diferencia entre decisiones.</li>
<li><b>§4.x, dimensionamiento.</b> Agregar el dimensionamiento simultáneo con el programa anual y la superestructura de tecnologías del mosto. {('Con la oferta actual, el frente de ' + d_opt['sizes']['Frente'] + ', ' + ('las dos prensas dedicadas de 1 t/h' if d_opt['sizes'].get('Prensa cáscara', 'no') != 'no' else 'una prensa de ' + d_opt['sizes']['Prensa'] + ' compartida por pulpa y cáscara') + ', ' + d_opt['sizes']['Clarificación'].lower() + (', microfiltración de lías de ' + d_opt['sizes']['MF lías'] if d_opt['sizes'].get('MF lías', 'no') != 'no' else '') + ' y un secador de ' + d_opt['sizes']['Secador'] + ' procesan el ' + pct(absorbed(d_opt['scen'][0])) + ' de la fruta. ' + ('El almacén aséptico de mosto queda en el mínimo (' + d_opt['sizes'].get('Almacén de mosto', '—') + ') y sirve para cargar los fermentadores, no para guardar mosto entre meses; la decantadora no se justifica.' if d_opt['sizes'].get('Almacén de mosto', '').startswith('10 ') else 'La decantadora no se justifica.')) if d_opt else ''}</li>
<li><b>§4.4 y Cap. 8, cáscara (versión 9).</b> Usar los rendimientos medidos de Campos et al. (2020) (57,8 % de jugo; torta con 17 % de materia seca, que retiene el 41 % de los sólidos) y de Seguí y Fito (2018) (0,36 g de etanol/g de azúcar en el jugo de cáscara), y estabilizar el jugo de cáscara antes de fermentarlo. Con esos datos la harina cae un tercio y el VPN del óptimo baja {(n0(cmpv['tea'][2]['NPV8'] / MM) + ' → ' + n0(cmpv['tea'][2]['NPV9'] / MM) + ' MM COP') if cmpv and len(cmpv.get('tea', [])) > 2 else ''}; la materia seca de la torta y el precio de la harina pasan a ser los datos más urgentes. Presentar la bromelaína del jugo de cáscara (precipitación sin solventes) como una etapa que se agrega desde unas 12 000 t/año, no como una línea aparte, y descartar el prensado con cal mientras la harina valga más que el jugo.</li>
<li><b>Capítulo de metodología (versión 10).</b> Organizar el método en las tres etapas de Bertran, Tula y Gani (2022): síntesis con la superestructura y el MILP (incluidas las hojas de la planta como segunda materia prima), diseño y verificación (balances, cinética calibrada, SuperPro, TEA de Burk), e innovación desde los puntos calientes. Agregar la evaluación de sostenibilidad de Heinzle et al. (2006): ACV de la cuna a la puerta con línea base sin planta, indicadores sociales y frente de Pareto margen–GWP. Declarar el registro de parámetros con su etiqueta de procedencia como parte del método.{(' Con los supuestos centrales, el óptimo v10 acopia ' + n0(d_opt['scen'][0]['products'].get('hojas_t', 0)) + ' t/año de hojas, produce ' + n0(d_opt['scen'][0]['products'].get('vinagre_m3', 0)) + ' m³/año de vinagre y da ' + n0(d_opt['obj']) + ' MM COP/año de margen; el mercado del vinagre es la condición que hay que validar.') if d_opt else ''}</li>
<li><b>§4.3 y Cap. 8, vinagre (versión 11).</b> Tratar la demanda de vinagre como un dato de entrada con escenarios, no como una consecuencia del diseño, y presentar el diseño como una familia indexada por esa demanda. Incluir la panela añadida a los jugos antes de fermentar (Ebrahimi 2026; Tanamool et al. 2020), que permite vender el vino y hacer el vinagre con los jugos de cáscara y de hojas, y el tratamiento del efluente del vinagre (electrocoagulación y humedal construido) en el TEA y el ACV. Usar para la xantana el rendimiento medido con residuo de piña (Iakovchenko 2026), no el de glucosa pura.</li>
<li><b>Cap. 8, impuestos y producto (versión 12).</b> Evaluar el vino embotellado con el impuesto al consumo departamental (Ley 1816 de 2016: componente específico por grado y 20 % ad valórem) y el IVA del 5 %, con su línea de embotellado, su empaque y un tope de demanda de botellas. Declarar el régimen de renta: la planta queda en municipios ZOMAC (Decreto 1650 de 2017), pero con arranque en 2030 la Ley 1819 de 2016 ya no da tarifa reducida; la prórroga del PL 435 de 2025 es un escenario, no la base.{(' Con los supuestos centrales, el óptimo v12 da ' + n0(d_opt['obj']) + ' MM COP/año.') if d_opt else ''}</li>
<li><b>Cap. 6 y 9, selección de líneas.</b> Incorporar el MILP con tamaños discretos y el STN semanal como evidencia de qué procesar con la oferta actual y de dónde están los cuellos de botella.</li>
</ol>
</section>

{v1_main}
</main>
"""
open("informe.html", "w").write(html_out)
print("ok", len(html_out))
