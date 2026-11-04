"""
TEA de Burk recalculado con los tamaños óptimos de dimensionamiento.py.

Para cada diseño (referencia TRL-9 u óptimo) se arma un caso TEA de planta (estructura de tea_burk.py y de los
libros de asaí y coco):
  - equipos: la lista de catálogo de cada opción elegida por el MILP (con sus equipos acompañantes), más los que
    no dependen del dimensionamiento (tanques de guarda de 90 d, cuarto frío, empacadoras);
  - producción: la del programa anual del diseño (fruta realmente procesada, vino, harina, bromelaína), no la
    nominal; consumos y servicios del balance de planta_trl9 a esa fruta procesada;
  - materia prima: toda la fruta procesada a 400 COP/kg (no solo las fracciones asignadas a cada línea) y el
    compostaje de las fracciones sin uso;
  - calendario: lun–sáb con 2 turnos, o con 3 turnos si el MILP eligió el tercer turno;
  - personal compartido (75 %) e ingenieros de planta como en tea_lineas.integrated_case.
El vino es el producto principal (precio 3 000 COP/L, como en el plan del MILP); harina, jugo de cáscara,
bromelaína y polvo entran como subproductos. Salidas: VPN, MIRR, LCOP, precio de equilibrio del vino, tornado,
Monte Carlo LHS + Iman–Conover y libros Excel verificados con LibreOffice (TEA_excel/).
"""
import json, os, math, copy
import numpy as np
import tea_burk as tb
import tea_lineas as tl
import planta_trl9 as pt
import capacidad as cp
import dimensionamiento as dm
import tea_excel_run as tx

RES = os.path.join(os.path.dirname(__file__), "results")
WINE_PRICE = dm.WINE_PRICE


def E(cat, need, name):
    n, s, _ = pt.pick(cat, need)
    k = pt.CAT[cat]
    return dict(name=name, qty=n, size=s, ref_size=k["ref"][0], ref_USD=k["ref"][1], n=k["n"])


def option_equipment(u, lab):
    """Equipos de catálogo que componen la opción 'lab' del equipo 'u' (mismos que dimensionamiento.options)."""
    num = lambda: float(lab.split()[0].split("×")[0])
    if lab == "no":
        return []
    if u == "Frente":
        s = num(); return [E("lavado_seleccion", s, "Recepción, lavado y selección"), E("peladora_descorazonadora", s, "Peladora-descorazonadora")]
    if u == "Prensa":
        s = num(); return [E("prensa_banda", s, "Prensa de banda (pulpa)"), E("trituradora", s, "Trituradora de pulpa"),
                           E("macerador_camisa", s / 1.06 * 1.2, "Macerador enzimático con camisa")]
    if u in ("Prensa cáscara", "Prensa corazón"):
        s = num(); w = "cáscara" if "cáscara" in u else "corazón"
        return [E("prensa_banda", s, f"Prensa de {w}"), E("trituradora", s, f"Trituradora de {w}")]
    if u == "Decantadora":
        s = num(); return [E("decantadora", s, "Decantadora centrífuga de pulpa"), E("trituradora", s, "Trituradora de pulpa"),
                           E("macerador_camisa", s / 1.06 * 1.2, "Macerador enzimático con camisa")]
    if u == "Clarificación":
        tech, q = lab.split()[0], float(lab.split()[1])
        cat = {"MF": "MF_ceramica", "Flotación": "flotador_mosto", "Centrífuga": "centrifuga_discos"}[tech]
        name = {"MF": "Microfiltración cerámica de mosto", "Flotación": "Flotador de mosto (saturador + tanque)", "Centrífuga": "Centrífuga de discos para mosto"}[tech]
        return [E(cat, q, name)]
    if u == "MF lías":
        return [E("MF_lias", num(), "Microfiltración tangencial de lías")]
    if u == "Estabilización":
        if lab.startswith("SO"):
            return [E("dosificador_SO2", 1, "Dosificador de SO2")]
        tech, q = lab.split()[0], float(lab.split()[1])
        return [E("pasteurizador_placas", q, "Pasteurizador flash de mosto")] if tech == "HTST" else [E("UHPH", q, "Homogeneizador UHPH (300 MPa)")]
    if u == "Bodega":
        n = int(lab.split("×")[0]); q = (n - 1) * dm.VF / dm.T_PROC
        return [dict(name=f"Fermentador inox con camisa {dm.VF:.0f} m³", qty=n, size=dm.VF, ref_size=dm.VF, ref_USD=pt.fermenter_moresi(dm.VF, True), n=1.0),
                E("chiller", q * dm.HEAT_KW_PER_M3H * 1.1, "Chiller agua-glicol"), E("centrifuga_discos", q * 1.5, "Centrífuga clarificadora"),
                E("filtro_cartuchos", q * 1.5, "Filtración final"), E("propagador", 0.5, "Propagador / pie de cuba")]
    if u == "Secador":
        s = num(); return [E("secador_banda", s, "Secador de banda"), E("caldera", s * 3.2 / 3.6 * 1.1, "Generador de aire caliente / caldera"),
                           E("molino_tamiz", s / 1000 * 1.35 * dm.FLOUR_PC * 1000, "Molino y tamizadora")]
    if u == "Almacén de mosto":
        V = num()
        if V <= 50:
            return [E("tanque_pulmon", V, "Tanque pulmón de mosto")]
        e = E("tanque_guarda", V, "Almacén aséptico de mosto"); e["ref_USD"] *= 1.4; return [e]
    if u == "Aspersión":
        s = num(); j = s / 1000 / 0.12
        return [E("spray_dryer", s, "Secador por aspersión"), E("UF_bromelaina", s / 0.12 / 25, "Ultrafiltración 10 kDa"),
                E("centrifuga_discos", j, "Centrífuga de jugo de corazón"), E("tanque_precipitacion", j * 0.4, "Tanques de precipitación"),
                E("cuarto_frio", 10, "Cuarto frío de producto")]
    raise KeyError(u)


def build_case(r, label, with_bromelain):
    """Caso TEA de planta a partir de una solución de dimensionamiento.py (primer escenario)."""
    sc = r["scen"][0]; pr = sc["products"]
    F = pr["fruta_t"]
    D = pt.design(F)
    L = D["lines"]; b = D["balance"]
    v, h, br = L["vino"], L["harina"], L["bromelaina"]
    eqs = []
    for u, lab in r["sizes"].items():
        eqs += option_equipment(u, lab)
    wine_m3 = pr["vino_m3"]
    eqs += [E("tanque_guarda", wine_m3 * 90 / 365 * 1.1, "Tanques de guarda (90 d)"), E("cuarto_frio", 10, "Cuarto frío (levaduras, enzimas)"),
            E("empacadora", 1, "Empacadora de harina"), E("generador_N2", 1, "Generador de N2 (inertización de tanques)"),
            E("dosificador_nutrientes", 1, "Dosificador de nutrientes (DAP)")]
    if with_bromelain:
        eqs.append(E("empacadora", 1, "Empacadora de bromelaína y polvo"))
    for e in eqs:
        e.setdefault("TRL", 9)
    brom_frac = (pr["bromelaina_kg"] / br["flows"]["bromelain_kg"]) if with_bromelain and br["flows"]["bromelain_kg"] > 0 else 0.0
    clar, stab = r["sizes"]["Clarificación"], r["sizes"]["Estabilización"]
    rows = sc["periods"]
    must = pr.get("mosto_m3", sum(x["mf"] for x in rows))                 # mosto que entra a clarificación
    stab_m3 = sum(x.get("stab", 0.0) for x in rows)
    dec_t = sum(x["Pd"].get("pulpa", 0.0) for x in rows)
    mem = 0.0
    if clar.startswith("MF"):
        mem += 0.15 * dm.buy("MF_ceramica", float(clar.split()[1]))
    if r["sizes"].get("MF lías", "no") != "no":
        mem += 0.15 * dm.buy("MF_lias", float(r["sizes"]["MF lías"].split()[0]))
    raw = [dict(name="Fruta de rechazo puesta en planta", qty_year=F * 1000, price=tl.M("fruta_kg"), main=True),
           dict(name="Pectinasa", qty_year=v["consumables"]["pectinasa_kg"], price=tl.M("pectinasa_kg")),
           dict(name="Levadura seca activa", qty_year=v["consumables"]["levadura_kg"], price=tl.M("levadura_kg")),
           dict(name="Reposición de membranas MF (COP)", qty_year=1, price=mem),
           dict(name="Nutrientes (DAP, 200 mg/L)", qty_year=must, price=dm.DAP_VC),
           dict(name="Metabisulfito (SO2, ≈ 50 mg/L)", qty_year=(stab_m3 if stab.startswith("SO") else 0.0), price=dm.SO2_VC),
           dict(name="Coadyuvantes de flotación", qty_year=(must if clar.startswith("Flot") else 0.0), price=dm.FLOT_VC - 1.0 * dm.E_COP),
           dict(name="Empaques de harina (COP)", qty_year=pr["harina_t"] * 1000 / 25, price=2_500)]
    lines = [v, h] + ([br] if with_bromelain else [])
    scale = [1.0, 1.0] + ([brom_frac] if with_bromelain else [])
    kwh_extra = (dec_t * 4.5 + must * {"MF": 0.0, "Flotación": 1.0, "Centrífuga": 2.0}[clar.split()[0]] + pr.get("lias_MF_m3", 0.0) * 1.0
                 + (stab_m3 * 100.0 if stab.startswith("UHPH") else 0.0) + wine_m3 * 0.5)
    heat_past = 0.0 if stab.startswith("HTST") else v["flows"]["juice_m3"] * dm.HTST_VC / dm.H_COP   # MJ de pasteurización que no se gastan
    util = [dict(name="Electricidad", qty_year=sum(l["elec_kWh"] * 1.3 * f for l, f in zip(lines, scale)) + kwh_extra, price_key="elec_COP_kWh"),
            dict(name="Calor de proceso (MJ)", qty_year=sum(l["heat_MJ"] * f for l, f in zip(lines, scale)) - heat_past, price_key="calor_COP_MJ"),
            dict(name="Agua de planta (t)", qty_year=sum(l["water_t"] * f for l, f in zip(lines, scale)), price_key="agua_COP_t")]
    unused = b["crown_t"] + (b["core_t"] * (1 - brom_frac) if with_bromelain else b["core_t"]) + pr.get("cascara_compost_t", 0.0)
    waste = [dict(name="Aguas residuales (t)", qty_year=util[2]["qty_year"], price=tb.COMMON["ARD_COP_t"]),
             dict(name="Compostaje de fracciones sin uso (t)", qty_year=unused, price=dm.COMPOST * 1000),
             dict(name="Lías y espumas a compostaje (m³)", qty_year=pr.get("lias_compost_m3", 0.0), price=dm.LEES_DISP)]
    byp = [dict(name="harina", qty_year=pr["harina_t"] * 1000, price=tl.M("harina_kg")),
           dict(name="jugo", qty_year=(pr["harina_t"] / dm.FLOUR_PC / dm.CAKE) * cp.Y["peel_juice_frac"] * 1000, price=tl.M("jugo_cascara_kg"))]
    if with_bromelain:
        raw += [dict(name="Reposición de membranas UF (COP)", qty_year=1, price=0.2 * pt.pick("UF_bromelaina", float(r["sizes"]["Aspersión"].split()[0]) / 0.12 / 25)[2] * tl.TRM),
                dict(name="Empaques y reactivos de bromelaína (COP)", qty_year=pr["bromelaina_kg"], price=8_000)]
        byp += [dict(name="bromelaina", qty_year=pr["bromelaina_kg"], price=tl.M("bromelaina_kg")),
                dict(name="polvo", qty_year=br["flows"]["powder_t"] * brom_frac * 1000, price=tl.M("polvo_kg"))]
    pos = math.ceil((4 + 2 + (2 if with_bromelain else 0)) * 0.75)
    cal = dict(tb.calendar(3), shifts=3) if r.get("turno3") else 3
    return dict(name=label, product=dict(name="Vino de piña a granel", unit="L", qty_year=wine_m3 * 1000, price=WINE_PRICE),
                raw=raw, utilities=util, waste=waste, equipment=eqs, positions=pos, calendar=cal, byproducts=byp,
                engineer=2 if with_bromelain else 1)


def run(case, mc_n=1000):
    r = tb.evaluate(case)
    be = tb.breakeven_price(case)
    _, tor = tb.tornado(case, tl.tornado_specs(case))
    mc = tb.monte_carlo(case, tl.mc_dists(case), tl.MC_R, n=mc_n)
    return dict(res={k: v for k, v in r.items() if k != "capex"}, capex={k: v for k, v in r["capex"].items() if k != "rows"},
                equipment=r["capex"]["rows"], breakeven=be, tornado=tor,
                mc=dict(P_pos=mc["P_pos"], P5=mc["P5"], P50=mc["P50"], P95=mc["P95"], CVaR5=mc["CVaR5"], NPV=mc["NPV"].tolist()),
                case=case)


if __name__ == "__main__":
    dim = json.load(open(f"{RES}/dimensionamiento.json"))
    sel = [("A · Referencia TRL-9", "E1|Referencia TRL-9 (planta_trl9, 6 200 t)", False),
           ("A · Óptimo con la topología anterior", "E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)", False),
           ("A · Óptimo con la superestructura ampliada", "E1|Óptimo económico", False),
           ("A · Óptimo sin SO₂", "E1|Óptimo sin SO₂", False),
           ("B · Referencia TRL-9 con bromelaína", "E5|B referencia (prensas dedicadas TRL-9)", True),
           ("B · Óptimo con la topología anterior", "E5|B óptimo con la topología anterior", True),
           ("B · Óptimo con la superestructura ampliada", "E5|B óptimo económico", True)]
    out = dict(cases={}, scale=[], check=[])
    made = []
    for lab, key, wb in sel:
        c = build_case(dim[key], lab, wb)
        res = run(c)
        res["sizes"] = dim[key]["sizes"]; res["turno3"] = dim[key]["turno3"]; res["fruit_t"] = dim[key]["scen"][0]["products"]["fruta_t"]
        res["dim_margin"] = dim[key]["obj"]
        out["cases"][lab] = res
        r = res["res"]
        print(lab, f"FCI {r['FCI']/1e6:,.0f} | VPN {r['NPV']/1e6:,.0f} | MIRR {r['MIRR']*100:.1f} % | LCOP {r['LCOP']:,.0f} COP/L | "
                   f"PE vino {res['breakeven']:,.0f} | P(VPN>0) {res['mc']['P_pos']:.2f} | nómina {r['labor']/1e6:,.0f}", flush=True)
        made.append(tx.make(c, dict(dim[key]["scen"][0]["products"]), "Dimensionado_Choco2022",
                            note=f"Tamaños de dimensionamiento.py: {dim[key]['sizes']}" + ("; tercer turno" if dim[key]["turno3"] else "")))
    # regla por escala: TEA del óptimo de cada oferta (sin Monte Carlo)
    for k in sorted([k for k in dim if k.startswith("E2|")], key=lambda k: float(k.split("|")[1])):
        rr = dim[k]
        c = build_case(rr, f"Óptimo a {rr['scen'][0]['supply']:,.0f} t/año", False)
        r = tb.evaluate(c)
        out["scale"].append(dict(supply=rr["scen"][0]["supply"], fruit_t=rr["scen"][0]["products"]["fruta_t"], sizes=rr["sizes"], turno3=rr["turno3"],
                                 FCI=r["FCI"], NPV=r["NPV"], MIRR=r["MIRR"], LCOP=r["LCOP"], breakeven=tb.breakeven_price(c), labor=r["labor"]))
        print("escala", round(rr["scen"][0]["supply"]), f"FCI {r['FCI']/1e6:,.0f} VPN {r['NPV']/1e6:,.0f} PE {out['scale'][-1]['breakeven']:,.0f}", flush=True)
    out["check"] = tx.recalc_check(made)
    for c in out["check"]:
        print(c["file"], "VPN py", round(c["NPV_py"] / 1e6, 1), "xl", None if c["NPV_xl"] is None else round(c["NPV_xl"] / 1e6, 1), "dRel", c["dNPV_rel"])
    json.dump(out, open(f"{RES}/tea_dimensionado.json", "w"), default=float)
