"""
Respuesta al informe del comité evaluador (noviembre de 2026): recálculos del bloque P0.

  tablas  H4 en VPN (TEA de cada diseño + secante del informe), intervalos [incumbente, cota dual] de H2 y H4, puente del
          capital, sensibilidad del factor de descomposición, desglose de la neutralidad (w = 0,75), impuesto por botella
          en cada régimen fiscal, prueba estequiométrica del registro.
  fiscal  óptimo reoptimizado y diseño central fijo bajo cada régimen fiscal, con su VPN.
  hoja    óptimo reoptimizado y diseño central fijo con el etanol del jugo de hoja limitado por la estequiometría.
  ws      wait-and-see del programa estocástico re-resuelto por escenario (libre con pista y diseño central fijo).
  h3      cota dual de cada punto ε del frente margen–GWP neto (corridas libres más largas).

Uso: python respuesta_comite.py tablas | fiscal | hoja | ws | h3   (salida en results/respuesta/<grupo>.json)
"""
import json, os, sys, copy
import numpy as np
import dimensionamiento as dm
import datos as DT

OUT = os.path.join(dm.RES, "respuesta")
os.makedirs(OUT, exist_ok=True)
D12 = json.load(open(os.path.join(dm.RES, "dimensionamiento.json")))
OPT = D12["E1|Óptimo económico"]
V13 = lambda g: json.load(open(os.path.join(dm.RES, "v13", f"{g}.json")))
STOICH = 92.0 / 180.0                                   # g etanol / g hexosa o pentosa (2 C2H5OH por C6; 5/3 por C5: 0,511 en ambos)


def design(r):
    return dict(r["sizes"], turno3=r["turno3"])


def save(name, res):
    json.dump(res, open(os.path.join(OUT, f"{name}.json"), "w"), indent=1, default=float)


def dual(p, gap):
    """Cota dual de un máximo a partir de la solución p y la brecha relativa de SCIP |p − d| / min(|p|, |d|)."""
    if gap is None or gap >= 1e19:
        return None
    return p * (1 + gap) if p >= 0 else p / (1 + gap)


def tea(full, label):
    import tea_dimensionado as td, tea_burk as tb
    if not full or not full.get("scen") or full["scen"][0]["products"].get("fruta_t", 0.0) < 1:
        return None
    c = td.build_case(full, label, False)
    r = tb.evaluate(c)
    return dict(NPV=r["NPV"] / 1e6, MIRR=r["MIRR"], FCI=r["FCI"] / 1e6)


def short(r):
    if not r.get("scen"):
        return dict(status=r.get("status"))
    s = r["scen"][0]; p = s["products"]
    keep = ("fruta_t", "hojas_t", "vino_m3", "botellas", "vinagre_m3", "acido_kg", "azucar_kg", "jugo_hojas_vinagre_t",
            "jugo_cascara_vinagre_t", "vino_a_vinagre_m3", "harina_t", "gwp_kg", "gwp_neto_kg")
    return dict(status=r["status"], gap=r["gap"], obj=r["obj"], bound=dual(r["obj"], r["gap"]), margin=s["margin"], FCI=r["FCI"],
                sizes=r["sizes"], turno3=r["turno3"], products={k: p.get(k, 0.0) for k in keep})


# ============================================================================ tablas
def gwp_terms(full):
    """Desglose del GWP lineal del MILP por término (t CO2e/año), recalculado con las variables de cada periodo."""
    S = full["scen"][0]; T = {}
    add = lambda k, v: T.__setitem__(k, T.get(k, 0.0) + v / 1000.0)
    crown_core = dm.FR["corazon"] + dm.B1["crown_t"]
    for p in S["periods"]:
        if p["dur"] <= 0:
            continue
        g = lambda k: p.get(k, 0.0) or 0.0
        add("Electricity (diesel genset)", dm.EF_KWH * (g("edem") - g("eu")))
        add("LPG heat", dm.EF_GLP_UTIL * (g("hdem") - g("hb") - g("hbu") - g("hpq")))
        add("Biomass boiler (CH4, N2O)", dm.EF_BIO_FUEL * g("hb"))
        add("Composting of unused fractions", dm.EF_COMP * (crown_core * g("fe") - g("cr") + g("comp") + g("ld")))
        add("Leaf pulp and juice returned to the field", dm.EF_FIELD_PULP * (dm.PF_H * g("hx") - g("hpb")) + dm.EF_FIELD_JUICE * g("hjr"))
        add("Leaf collection (diesel)", dm.EF_ACOPIO * g("hh"))
        add("Fruit transport", dm.EF_FRUIT_T * g("fe"))
        add("Panela", dm.EF_AZ * 1000 * g("az"))
        add("Glass bottles", dm.EF_BOT * 1000 / dm.BOTTLE_L * (dm.WINE_PM * g("bod") - g("wv")))
        add("_total", g("gwp"))
    T["Chemicals and other"] = T.pop("_total") - sum(T.values())
    T["Aeration and other fixed electricity"] = S["products"]["gwp_kg"] / 1000 - sum(T.values())     # fuera de los periodos
    return T


def run_tablas():
    res = {}
    # ---------------- H4 en VPN
    S = json.load(open(os.path.join(dm.RES, "v13", "resumen.json")))["H4"]
    a, b = (184.0, -5409.0), (3196.0, 5397.0)                                     # secante del informe (puntos del propio TEA)
    slope = (b[1] - a[1]) / (b[0] - a[0]); m0 = a[0] - a[1] / slope
    bounds = {}
    for g in ("H4a", "H4b"):
        try:
            for k, v in V13(g).items():
                if k.startswith("_") or not isinstance(v, dict) or v.get("gap") is None:
                    continue
                d = dual(v["obj"], v["gap"])
                if d is not None:
                    bounds[k] = min(bounds.get(k, 1e18), d)
                elif v.get("gap", 0) >= 1e19:
                    bounds.setdefault(k, None)
        except FileNotFoundError:
            pass
    rows = []
    for k, v in S.items():
        bt, vin = (int(x) for x in k.split("|"))
        fruit = None
        for g in ("H4q2", "H4q1", "H4q0", "H4p", "H4b", "H4a"):
            try:
                x = V13(g).get(k)
            except FileNotFoundError:
                continue
            if x and x.get("products"):
                fruit = x["products"].get("fruta_t"); wine = x["products"].get("vino_m3"); break
        rows.append(dict(bottles=bt, vinegar=vin, margin=v["margin"], NPV=v.get("NPV"), NPV_secant=a[1] + slope * (v["margin"] - a[0]),
                         bound=bounds.get(k), fruit_t=fruit, wine_m3=wine))
    res["H4"] = dict(rows=rows, slope=slope, margin_at_npv0=m0)
    # ---------------- H2: tope de energía fósil
    h2, h2p = V13("H2"), V13("H2p")
    pol = {p["frac"]: p for p in h2p["sweep"]}
    res["H2"] = [dict(frac=p["frac"], incumbent=max(p["obj"], pol.get(p["frac"], p)["obj"]), bound=dual(p["obj"], p["gap"]), gap_free=p["gap"])
                 for p in h2["sweep"]]
    o13 = h2.get("optimo_v13", {})
    res["H2_opt"] = dict(incumbent=o13.get("obj"), bound=dual(o13.get("obj", 0), o13.get("gap")), gap=o13.get("gap"))
    # ---------------- capital
    s = OPT["scen"][0]
    res["capital"] = dict(purchase=OPT["capex_purchase"] / 1e6, lang=dm.LANG, FCI_milp=OPT["FCI"], AF=dm.AF,
                          capital_charge=dm.AF * OPT["capex_purchase"] / 1e6, capex_ann=OPT["capex_ann"],
                          fixed_in_charge=OPT["capex_ann"] - dm.AF * OPT["capex_purchase"] / 1e6, contribution=s["contrib"],
                          margin=s["margin"], FCI_tea=16404.5)
    # ---------------- LCA: factor de descomposición
    A = json.load(open(os.path.join(dm.RES, "acv.json")))["Óptimo v12"]
    gw, base = A["gwp"], A["base"]
    f0 = dm.EF_COMP
    dep = gw["Compostaje de fracciones sin uso"] + gw["Pulpa y jugo de hojas devueltos al campo"]
    fixed = A["gwp_total"] - dep
    sens = []
    for f in (f0 - 100, f0, f0 + 100):
        k = f / f0
        sens.append(dict(factor=f, process=(fixed + k * dep) / 1000, base_decomp=k * (base["fruta"] + base["hojas_descomposicion"]) / 1000,
                         net_decomp=(fixed + k * dep - k * (base["fruta"] + base["hojas_descomposicion"])) / 1000,
                         base_burn=(k * base["fruta"] + base["hojas_quema"]) / 1000,
                         net_burn=(fixed + k * dep - k * base["fruta"] - base["hojas_quema"]) / 1000))
    res["lca_factor"] = dict(factor0=f0, fixed=fixed / 1000, dependent=dep / 1000, rows=sens)
    # ---------------- desglose de la neutralidad del diseño w = 0,75
    w = [e for e in V13("H3b")["mcda"] if e.get("w") == 0.75][0]["full"]
    eco = V13("H3b")["extremos"]["economico"]["full"]                         # el mismo diseño con la contabilidad v13
    te, tw = gwp_terms(eco), gwp_terms(w)
    pe, pw = eco["scen"][0]["products"], w["scen"][0]["products"]
    res["neutral"] = dict(terms_opt=te, terms_w075=tw, delta={k: tw[k] - te[k] for k in te},
                          fruit=(pe["fruta_t"], pw["fruta_t"]), leaves=(pe["hojas_t"], pw["hojas_t"]),
                          base=(dm.EF_BASE * (pe["fruta_t"] + pe["hojas_t"]) / 1000, dm.EF_BASE * (pw["fruta_t"] + pw["hojas_t"]) / 1000),
                          base_fruit_delta=dm.EF_BASE * (pw["fruta_t"] - pe["fruta_t"]) / 1000,
                          base_leaf_delta=dm.EF_BASE * (pw["hojas_t"] - pe["hojas_t"]) / 1000,
                          gwp=(pe["gwp_kg"] / 1000, pw["gwp_kg"] / 1000), net=(pe["gwp_neto_kg"] / 1000, pw["gwp_neto_kg"] / 1000),
                          margin=(eco["scen"][0]["margin"], w["scen"][0]["margin"]), sizes_w=w["sizes"],
                          products_w={k: pw.get(k) for k in ("fruta_t", "hojas_t", "vino_m3", "vino_a_vinagre_m3", "azucar_kg", "calor_glp_MJ",
                                                             "calor_corona_GJ", "pulpa_hojas_caldera_t", "pulpa_hojas_campo_t",
                                                             "jugo_hojas_vinagre_t", "jugo_cascara_vinagre_t")})
    sw = []
    for lab, terms, bse in (("Economic optimum", te, res["neutral"]["base"][0]), ("Compromise w = 0.75", tw, res["neutral"]["base"][1])):
        dep_ = terms["Composting of unused fractions"] + terms["Leaf pulp and juice returned to the field"]; G_ = sum(terms.values())
        for f in (f0 - 100, f0, f0 + 100):
            k = f / f0
            sw.append(dict(design=lab, factor=f, process=G_ - dep_ + k * dep_, baseline=k * bse, net=G_ - dep_ + k * dep_ - k * bse))
    res["neutral"]["factor_sens"] = sw
    # ---------------- impuesto por botella en cada régimen
    regs = fiscal_regimes()
    tab = []
    for lab, (e, av, iva) in regs.items():
        with_params(dict(impuesto_vino_especifico=e, impuesto_vino_ad_valorem=av, iva_vino=iva))
        for pvp in (10000.0, 16000.0, 25000.0):
            wb = dm.wine_bottle(pvp=pvp)
            tab.append(dict(regime=lab, e=e, a=av, iva=iva, pvp=pvp, tax=wb["impuesto"], vat=pvp - pvp / (1 + iva), factory=wb["fabrica"],
                            net=wb["neto"], net_L=wb["neto_L"]))
        restore_params()
    res["fiscal_bottle"] = tab
    # ---------------- prueba estequiométrica del registro
    juice_ts, prot, ash, fat = 0.062, 0.14, 0.1002, 0.035                        # Liao et al. 2022, tabla 1 (jugo de hoja, de Chen et al. 2020)
    carb = 1000 * juice_ts * (1 - prot - ash - fat)                              # g carbohidrato por kg de jugo, por diferencia
    E = DT.val("etanol_jugo_hojas")
    checks = [dict(stream="Pulp juice (Murcia Palacios 2013)", sugar=158.83, product=65.31, basis="g/L"),
              dict(stream="Leaf juice, free sugars of the registry (glucose 10.6 + xylose 16.4)", sugar=27.0, product=E * 1.02, basis="g/L"),
              dict(stream="Leaf juice, carbohydrate by difference (TS 6.2 %; protein, ash, fat removed)", sugar=carb, product=E, basis="g/kg"),
              dict(stream="Peel juice (Seguí and Fito 2018)", sugar=dm.PJ_SUGAR, product=dm.PJ_SUGAR * dm.PJ_ETOH, basis="g/kg"),
              dict(stream="Panela (registry)", sugar=1000 * DT.val("azucar_fermentable_panela"),
                   product=1000 * DT.val("azucar_fermentable_panela") * DT.val("rend_etanol_azucar_anadido"), basis="g/kg")]
    for c in checks:
        c["Y"] = c["product"] / c["sugar"]; c["frac_theor"] = c["Y"] / STOICH; c["pass"] = c["Y"] <= STOICH
    res["stoich"] = dict(checks=checks, carb_gkg=carb, Y_max=STOICH,
                         E_scen={"central (source mass balance)": E, "90 % of theoretical on carbohydrate": 0.90 * STOICH * carb,
                                 "theoretical on free sugars": STOICH * 27.0 / 1.02, "0.42 g/g on free sugars": 0.42 * 27.0 / 1.02})
    save("tablas", res)
    print(json.dumps({k: res[k] for k in ("capital", "lca_factor")}, indent=1, default=float)[:3000])
    for r in sorted(res["H4"]["rows"], key=lambda r: (r["bottles"], r["vinegar"])):
        print(r["bottles"], r["vinegar"], round(r["margin"]), r["NPV"] and round(r["NPV"]), round(r["NPV_secant"]), r["bound"] and round(r["bound"]), r["fruit_t"] and round(r["fruit_t"]))
    print("m(NPV=0) =", round(m0), "pendiente", round(slope, 3))
    for c in checks:
        print(c["stream"], round(c["Y"], 3), round(c["frac_theor"], 3), c["pass"])
    print(json.dumps(res["neutral"]["delta"], indent=1), res["neutral"]["base_fruit_delta"], res["neutral"]["base_leaf_delta"])
    for t in tab:
        print(t["regime"], t["pvp"], round(t["tax"]), round(t["vat"]), round(t["net"]))


# ============================================================================ parámetros
_SAVED = {}


def with_params(d):
    for k, v in d.items():
        _SAVED.setdefault(k, DT.val(k)); DT.set_val(k, v)
    dm.WINE_NET_L = dm.wine_bottle()["neto_L"]


def restore_params():
    for k, v in _SAVED.items():
        DT.set_val(k, v)
    _SAVED.clear()
    dm.WINE_NET_L = dm.wine_bottle()["neto_L"]


def fiscal_regimes():
    e0 = DT.val("impuesto_vino_especifico")
    return {"Current (Law 1816/2016; 2026 rate)": (e0, 0.20, 0.05),
            "Specific component tripled": (3 * e0, 0.20, 0.05),
            "Decree 1474/2025 rates with 5 % VAT": (750.0, 0.30, 0.05),
            "Decree 1474/2025 rates with 19 % VAT": (750.0, 0.30, 0.19),
            "2026 fiscal-rescue bill (750; 35 %; 19 % VAT)": (750.0, 0.35, 0.19)}


def run_fiscal():
    dm.HP_ON = False
    res = {}
    for lab, (e, av, iva) in fiscal_regimes().items():
        with_params(dict(impuesto_vino_especifico=e, impuesto_vino_ad_valorem=av, iva_vino=iva))
        r = dm.solve(time_limit=360, hint=design(OPT))
        f = dm.solve(fix=design(OPT), time_limit=150, gap=0.002)
        res[lab] = dict(e=e, a=av, iva=iva, net_L=dm.WINE_NET_L, reopt=short(r), reopt_tea=tea(r, "fiscal"), central=short(f),
                        central_tea=tea(f, "fiscal_c"))
        restore_params(); save("fiscal", res)
        print(lab, "reopt", round(r.get("obj", float("nan"))), r.get("scen") and round(r["scen"][0]["products"]["botellas"]),
              res[lab]["reopt_tea"], "| central", round(f.get("obj", float("nan"))), res[lab]["central_tea"], flush=True)


def run_hoja():
    dm.HP_ON = False
    T = json.load(open(os.path.join(OUT, "tablas.json")))["stoich"]["E_scen"]
    E0, A0 = dm.E_LJ, dm.A_LJ
    res = {}
    for lab, E in T.items():
        dm.E_LJ, dm.A_LJ = E, E * 60 / 46 * dm.ACET_YIELD
        r = dm.solve(time_limit=360, hint=design(OPT))
        f = dm.solve(fix=design(OPT), time_limit=150, gap=0.002)
        res[lab] = dict(E_LJ=E, A_LJ=dm.A_LJ, reopt=short(r), reopt_tea=tea(r, "hoja"), central=short(f), central_tea=tea(f, "hoja_c"))
        save("hoja", res)
        print(lab, round(E, 2), "reopt", round(r.get("obj", float("nan"))), r.get("scen") and round(r["scen"][0]["products"]["azucar_kg"] / 1000, 1),
              r.get("scen") and round(r["scen"][0]["products"]["vinagre_m3"]), res[lab]["reopt_tea"], flush=True)
    dm.E_LJ, dm.A_LJ = E0, A0


def run_ws():
    dm.HP_ON = False
    import estocastico as es
    res = dict(each=[])
    for a, pa in es.SUP_F:
        sc = [dict(sup=a, p=1.0)]
        f = dm.solve(scen=sc, fix=design(OPT), time_limit=200, gap=0.001)
        r = dm.solve(scen=sc, time_limit=600, hint=design(OPT))
        best = max([x for x in (f, r) if x.get("scen")], key=lambda x: x["obj"])
        res["each"].append(dict(sup=a, p=pa, central=f.get("obj"), free=r.get("obj"), free_gap=r.get("gap"), best=best["obj"],
                                bound=dual(r["obj"], r["gap"]) if r.get("scen") else None, same_design=best["sizes"] == OPT["sizes"]))
        save("ws", res)
        print("WS", a, "central", round(f.get("obj", float("nan"))), "libre", round(r.get("obj", float("nan"))), "gap", r.get("gap"), flush=True)
    res["WS"] = sum(e["p"] * e["best"] for e in res["each"])
    res["RP"] = D12["E4|RP"]["obj"]; res["EEV"] = D12["E4|EEV"]["obj"]
    res["EVPI"] = res["WS"] - res["RP"]; res["VSS"] = res["RP"] - res["EEV"]
    save("ws", res)
    print("WS", round(res["WS"], 2), "RP", round(res["RP"], 2), "EVPI", round(res["EVPI"], 3), flush=True)


def run_h3():
    dm.HP_ON = True
    h = V13("H3b")
    res = []
    for p in h["frente"]:
        r = dm.solve(gwp_max=float(p["eps"]), gwp_net=True, time_limit=600, hint=dict(p["sizes"], turno3=p["turno3"]))
        res.append(dict(eps=p["eps"], incumbent=max(p["obj"], r.get("obj", -1e18)), free=r.get("obj"), gap=r.get("gap"),
                        bound=dual(r["obj"], r["gap"]) if r.get("scen") else None))
        save("h3", res)
        print("H3 ε", round(p["eps"] / 1000), "incumbente", round(res[-1]["incumbent"]), "cota", res[-1]["bound"] and round(res[-1]["bound"]), flush=True)





def run_h3full(idx):
    """Re-resuelve un punto ε del frente H3 y guarda el diseño completo (para los puntos que mejoran el incumbente publicado)."""
    dm.HP_ON = True
    p = V13("H3b")["frente"][idx]
    r = dm.solve(gwp_max=float(p["eps"]), gwp_net=True, time_limit=900, hint=dict(p["sizes"], turno3=p["turno3"]))
    out = dict(eps=p["eps"], published=dict(margin=p["margin"], gwp_neto=p["products"]["gwp_neto_kg"] / 1000, sizes=p["sizes"]),
               new=short(r), new_tea=tea(r, "h3"))
    save(f"h3full_{idx}", out)
    print("H3full", idx, round(p["eps"] / 1000), "publicado", round(p["margin"]), "nuevo", round(r.get("obj", float("nan"))),
          r.get("scen") and round(r["scen"][0]["products"]["gwp_neto_kg"] / 1000), flush=True)


def h4_designs():
    best = {}
    for g in ("H4a", "H4b", "H4p", "H4q0", "H4q1", "H4q2"):
        try:
            h = V13(g)
        except FileNotFoundError:
            continue
        for k, v in h.items():
            if k.startswith("_") or not isinstance(v, dict) or "obj" not in v or not v.get("sizes"):
                continue
            if k not in best or v["obj"] > best[k]["obj"]:
                best[k] = v
    return best


def run_c207(part, E=None):
    """Mapa H4 re-resuelto con el etanol del jugo de hoja corregido (filas con vinagre ≥ 1 500 m³, donde se usa el jugo de hoja).
    part: índice de botellas (0–4) o 'vin11' (planta solo de vinagre a 11,1 kg/t)."""
    dm.HP_ON = False
    T = json.load(open(os.path.join(OUT, "tablas.json")))["stoich"]["E_scen"]
    E = E or T["90 % of theoretical on carbohydrate"]
    best = h4_designs(); BOT = [100000, 250000, 500000, 1000000, 2000000]
    if part == "vin11":
        keys = ["100000|3000"]; E = T["0.42 g/g on free sugars"]; tag = "c111_vin"
    elif part == "vin135":
        keys = ["100000|3000"]; E = T["theoretical on free sugars"]; tag = "c135_vin"
    else:
        b = BOT[int(part)]; keys = [f"{b}|{v}" for v in (1500, 3000, 6000, 12000)]; tag = f"c207_{part}"
    dm.E_LJ, dm.A_LJ = E, E * 60 / 46 * dm.ACET_YIELD
    base_w, base_v = dm.WINE_DEMAND_M3, dm.VIN_DEMAND
    res = {}
    for k in keys:
        b, v = (int(x) for x in k.split("|"))
        dm.WINE_DEMAND_M3, dm.VIN_DEMAND = b * dm.BOTTLE_L / 1000, v
        h = best[k]
        r = dm.solve(time_limit=360, hint=dict(h["sizes"], turno3=h["turno3"]))
        f = dm.solve(fix=dict(h["sizes"], turno3=h["turno3"]), time_limit=150, gap=0.002)
        bestr = max([x for x in (r, f) if x.get("scen")], key=lambda x: x["obj"])
        out = dict(E_LJ=E, margin_old=h["obj"], free=short(r), fixed_old_design=short(f), best=short(bestr), tea=tea(bestr, "c207"))
        if k == "500000|3000" and part != "vin11":
            import acv
            inv = acv.inventory(bestr)
            out["acv"] = {kk: (vv if not isinstance(vv, dict) else {a: float(c) for a, c in vv.items()}) for kk, vv in inv.items()
                          if isinstance(vv, (int, float, dict))}
            out["full_products"] = bestr["scen"][0]["products"]
        res[k] = out; save(tag, res)
        print("C207", k, round(E, 2), "antes", round(h["obj"]), "libre", round(r.get("obj", float("nan"))), "diseño anterior", round(f.get("obj", float("nan"))),
              "cota", res[k]["free"].get("bound") and round(res[k]["free"]["bound"]), res[k]["tea"], flush=True)
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = base_w, base_v


def set_leaf(E):
    dm.E_LJ, dm.A_LJ = E, E * 60 / 46 * dm.ACET_YIELD


def run_fiscal207():
    """Regímenes fiscales con el valor central corregido del etanol del jugo de hoja (20,7 kg/t)."""
    dm.HP_ON = False
    set_leaf(json.load(open(os.path.join(OUT, "tablas.json")))["stoich"]["E_scen"]["90 % of theoretical on carbohydrate"])
    c = json.load(open(os.path.join(OUT, "c207_2.json")))["500000|3000"]["best"]
    cen = dict(c["sizes"], turno3=c["turno3"])
    vin = json.load(open(os.path.join(OUT, "c207_0.json")))["100000|3000"]["best"]
    res = {}
    for lab, (e, av, iva) in fiscal_regimes().items():
        with_params(dict(impuesto_vino_especifico=e, impuesto_vino_ad_valorem=av, iva_vino=iva))
        r = dm.solve(time_limit=360, hint=cen)
        f = dm.solve(fix=cen, time_limit=150, gap=0.002)
        v = dm.solve(fix=dict(vin["sizes"], turno3=vin["turno3"]), time_limit=150, gap=0.002)
        cands = [x for x in (r, f, v) if x.get("scen")]
        best = max(cands, key=lambda x: x["obj"])
        res[lab] = dict(e=e, a=av, iva=iva, best=short(best), best_tea=tea(best, "f207"), free_bound=dual(r["obj"], r["gap"]) if r.get("scen") else None,
                        central=short(f), central_tea=tea(f, "f207c"))
        restore_params(); save("fiscal207", res)
        print("F207", lab, "mejor", round(best["obj"]), round(best["scen"][0]["products"]["botellas"]), "cota", res[lab]["free_bound"] and round(res[lab]["free_bound"]),
              res[lab]["best_tea"], "| central", round(f.get("obj", float("nan"))), round(f["scen"][0]["products"]["fruta_t"]), res[lab]["central_tea"], flush=True)


def run_gwp207():
    """GWP neto (contabilidad v13) del óptimo y del compromiso w = 0,75 con el etanol de hoja corregido, diseños fijos."""
    dm.HP_ON = True
    set_leaf(json.load(open(os.path.join(OUT, "tablas.json")))["stoich"]["E_scen"]["90 % of theoretical on carbohydrate"])
    c = json.load(open(os.path.join(OUT, "c207_2.json")))["500000|3000"]["best"]
    w = [e for e in V13("H3b")["mcda"] if e.get("w") == 0.75][0]
    res = {}
    for lab, d in (("optimum", dict(c["sizes"], turno3=c["turno3"], **{"Bomba de calor": "no"})), ("w075", dict(w["sizes"], turno3=w["turno3"]))):
        r = dm.solve(fix=d, time_limit=150, gap=0.002)
        res[lab] = dict(short=short(r), terms=gwp_terms(r), tea=tea(r, "g207"))
        save("gwp207", res)
        print("G207", lab, round(r["obj"]), round(r["scen"][0]["products"]["gwp_kg"] / 1000, 1), round(r["scen"][0]["products"]["gwp_neto_kg"] / 1000, 1), res[lab]["tea"], flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "h3full":
        run_h3full(int(sys.argv[2]))
    elif sys.argv[1] in ("fiscal207", "gwp207"):
        dict(fiscal207=run_fiscal207, gwp207=run_gwp207)[sys.argv[1]]()
    elif sys.argv[1] == "c207":
        run_c207(sys.argv[2])
    else:
        dict(tablas=run_tablas, fiscal=run_fiscal, hoja=run_hoja, ws=run_ws, h3=run_h3)[sys.argv[1]]()
