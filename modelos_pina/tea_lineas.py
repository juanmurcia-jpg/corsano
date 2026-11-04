"""
Casos TEA (metodología Burk de la plantilla del usuario) para cada línea del diseño TRL-9 y para la planta
integrada. Precios y costos en COP de 2026; supuestos [S] marcados.
"""
import copy, json, os, math
import numpy as np
import tea_burk as tb
import planta_trl9 as pt
import capacidad as cp
import params as p

RES = os.path.join(os.path.dirname(__file__), "results")
TRM = tb.COMMON["TRM"]
PR = dict(   # (mín, moda, máx) en COP por unidad                                           procedencia
    fruta_kg=(200, 400, 800),            # fruta de rechazo puesta en planta                            [S]
    corona_kg=(40, 80, 150),             # recolección de corona                                       [S]
    vino_L=(1200, 1600, 3000),           # granel; 400 USD/t de la tesis ×4 000 COP/USD                [T]/[S]
    vinagre_L=(1500, 2200, 4000),        # granel                                                     [S]
    bromelaina_kg=(120_000, 300_000, 600_000),   # cruda grado alimentario                            [S]
    polvo_kg=(20_000, 40_000, 80_000),   # polvo nutracéutico                                         [S]
    harina_kg=(6_000, 12_000, 20_000),   # harina de fibra                                            [S]
    jugo_cascara_kg=(80, 150, 250),      # precio de transferencia del jugo al etanol                  [S]
    etanol_L=(3000, 4000, 5500),         # etanol hidratado                                           [S]
    elec_kWh=(1000, 1400, 2000),         # ZNI, diésel                                                [S]
    calor_MJ=(110, 159, 220),            # GLP en caldera                                             [derivado de la plantilla]
    pectinasa_kg=(180_000, 240_000, 320_000),
    levadura_kg=(45_000, 60_000, 80_000),
)
M = lambda k: PR[k][1]


def to_equipment(eqs):
    out = []
    for e in eqs:
        out.append(dict(name=e["name"], qty=e["qty"], size=e["size"], ref_size=e["ref_size"], ref_USD=e["ref_USD"], n=e["n"]))
    return out


def cases_from_design(D, heat_source="glp"):
    L = D["lines"]; b = D["balance"]
    heat_price_key = "calor_COP_MJ"
    cs = {}
    lv = L.get("vino") or L.get("vino_premium")
    def base(name, line, product, price, qty, raw, extra_util=(), byp=(), unit=""):
        util = [dict(name="Electricidad", qty_year=line["elec_kWh"] * 1.3, price_key="elec_COP_kWh"),
                dict(name="Calor de proceso (MJ)", qty_year=line["heat_MJ"], price_key=heat_price_key),
                dict(name="Agua de planta (t)", qty_year=line["water_t"], price_key="agua_COP_t")] + list(extra_util)
        return dict(name=name, product=dict(name=product, unit=unit, qty_year=qty, price=price), raw=raw, utilities=util,
                    waste=[dict(name="Aguas residuales (t)", qty_year=line["water_t"], price=tb.COMMON["ARD_COP_t"])],
                    equipment=to_equipment(line["equipment"]), positions=line["positions"], calendar=line["calendar"],
                    byproducts=list(byp))
    # L1 vino rápido
    v = L["vino"]
    cs["L1 Vino de piña (rápido, 30 °C)"] = base(
        "L1 Vino de piña", v, "Vino a granel", M("vino_L"), v["flows"]["wine_sold_m3"] * 1000,
        [dict(name="Pulpa (fruta asignada por masa)", qty_year=b["pulp_t"] * 1000, price=M("fruta_kg"), main=True),
         dict(name="Pectinasa", qty_year=v["consumables"]["pectinasa_kg"], price=M("pectinasa_kg")),
         dict(name="Levadura seca activa", qty_year=v["consumables"]["levadura_kg"], price=M("levadura_kg")),
         dict(name="Reposición de membranas (COP)", qty_year=1, price=v["consumables"]["membranas_USD"] * TRM)],
        unit="L")
    # L2 vino premium (Moresi 15–22 °C, 5 d)
    Dp = pt.design(b["fruit_t"], premium=True)
    vp = Dp["lines"]["vino_premium"]
    cs["L2 Vino premium (15–22 °C, 5 d)"] = base(
        "L2 Vino premium", vp, "Vino premium a granel", M("vino_L"), vp["flows"]["wine_sold_m3"] * 1000,
        [dict(name="Pulpa (fruta asignada por masa)", qty_year=b["pulp_t"] * 1000, price=M("fruta_kg"), main=True),
         dict(name="Pectinasa", qty_year=vp["consumables"]["pectinasa_kg"], price=M("pectinasa_kg")),
         dict(name="Levadura seca activa", qty_year=vp["consumables"]["levadura_kg"], price=M("levadura_kg")),
         dict(name="Reposición de membranas (COP)", qty_year=1, price=vp["consumables"]["membranas_USD"] * TRM)],
        unit="L")
    # L3 vinagre (vino a precio de mercado como materia prima)
    vg = L["vinagre"]
    cs["L3 Vinagre (acetador sumergido)"] = base(
        "L3 Vinagre", vg, "Vinagre 5 % a granel", M("vinagre_L"), vg["flows"]["vinegar_m3"] * 1000,
        [dict(name="Vino base (precio de transferencia)", qty_year=vg["flows"]["wine_in_m3"] * 1000, price=M("vino_L"), main=True)],
        unit="L")
    # L4 bromelaína + polvo
    br = L["bromelaina"]
    cs["L4 Bromelaína + polvo nutracéutico"] = base(
        "L4 Bromelaína", br, "Bromelaína cruda", M("bromelaina_kg"), br["flows"]["bromelain_kg"],
        [dict(name="Corazón (fruta asignada por masa)", qty_year=br["flows"]["core_t"] * 1000, price=M("fruta_kg"), main=True),
         dict(name="Reposición de membranas (COP)", qty_year=1, price=br["consumables"]["membranas_USD"] * TRM),
         dict(name="Empaques y reactivos (COP)", qty_year=br["flows"]["bromelain_kg"], price=8_000)],
        byp=[dict(name="polvo", qty_year=br["flows"]["powder_t"] * 1000, price=M("polvo_kg"))], unit="kg")
    # L5 harina de cáscara (+ jugo vendido al etanol)
    hr = L["harina"]
    cs["L5 Harina de fibra de cáscara"] = base(
        "L5 Harina de cáscara", hr, "Harina de fibra", M("harina_kg"), hr["flows"]["flour_t"] * 1000,
        [dict(name="Cáscara (fruta asignada por masa)", qty_year=hr["flows"]["peel_t"] * 1000, price=M("fruta_kg"), main=True),
         dict(name="Empaques (COP)", qty_year=hr["flows"]["flour_t"] * 1000 / 25, price=2_500)],
        byp=[dict(name="jugo", qty_year=hr["flows"]["peel_juice_t"] * 1000, price=M("jugo_cascara_kg"))], unit="kg")
    # L6 etanol
    et = L["etanol"]
    cs["L6 Etanol hidratado (jugo de cáscara)"] = base(
        "L6 Etanol", et, "Etanol hidratado 95 %", M("etanol_L"), et["flows"]["ethanol_L"],
        [dict(name="Jugo de cáscara (transferencia)", qty_year=et["flows"]["peel_juice_t"] * 1000, price=M("jugo_cascara_kg"), main=True),
         dict(name="Levadura", qty_year=et["consumables"]["levadura_kg"], price=M("levadura_kg"))], unit="L")
    # L7 energía: (a) gasificación TRL 8 ; (b) caldera de biomasa TRL 9 (calor para el secado)
    en = L["energia"]
    cs["L7a Isla de gasificación (TRL 8)"] = base(
        "L7a Gasificación", en, "Electricidad autogenerada", M("elec_kWh"), en["flows"]["E_el_MWh"] * 1000,
        [dict(name="Corona (recolección)", qty_year=en["flows"]["crown_t"] * 1000, price=M("corona_kg"), main=True)],
        byp=[dict(name="calor", qty_year=en["flows"]["Q_th_GJ"] * 1000 * 0.5, price=M("calor_MJ"))], unit="kWh")
    heat_boiler_MJ = b["crown_dm_t"] * 1000 * 17.0 * 0.80
    boiler_line = dict(equipment=[pt.eq("ast", "astilladora_secador_biomasa", b["crown_t"] / D["H_front"], "Picadora de corona",
                                        "Gasificación downdraft + motor (≤ 100 kWe)"),
                                  pt.eq("cal", "caldera", heat_boiler_MJ / D["H_front"] / 3.6, "Caldera de biomasa (agua caliente/vapor)",
                                        "Harina de fibra de cáscara (prensa + secador de banda + molino)")],
                       elec_kWh=b["crown_t"] * 10, heat_MJ=0.0, water_t=0.0, positions=1, calendar=3)
    for e in boiler_line["equipment"]:
        e["TRL"] = 9
    cs["L7b Caldera de biomasa (TRL 9)"] = base(
        "L7b Caldera", boiler_line, "Calor útil", M("calor_MJ"), min(heat_boiler_MJ, b["Q_dry_GJ"] * 1000 + 1e-9),
        [dict(name="Corona (recolección)", qty_year=b["crown_t"] * 1000, price=M("corona_kg"), main=True)], unit="MJ")
    return cs


def integrated_case(cs, keys, name="Planta integrada TRL-9"):
    """Suma de líneas en un solo TEA (sin doble conteo de transferencias internas)."""
    I = dict(name=name, product=dict(name="Ingresos agregados (COP)", unit="COP", qty_year=0.0, price=1.0), raw=[], utilities=[],
             waste=[], equipment=[], positions=0, calendar=3, byproducts=[])
    internal = {"Jugo de cáscara (transferencia)", "Vino base (precio de transferencia)"}
    for k in keys:
        c = cs[k]
        I["byproducts"].append(dict(name=c["name"], qty_year=c["product"]["qty_year"], price=c["product"]["price"]))
        for bp in c.get("byproducts", []):
            if bp["name"] == "jugo" and any("Etanol" in kk for kk in keys):
                continue                                   # el jugo se consume internamente
            if bp["name"] == "calor":
                continue
            I["byproducts"].append(dict(bp))
        I["raw"] += [dict(r) for r in c["raw"] if r["name"] not in internal]
        for u in c["utilities"]:
            uu = dict(u)
            if u["name"].startswith("Calor") and any("Caldera" in kk for kk in keys):
                uu["qty_year"] = 0.0                       # calor cubierto por la caldera de biomasa
            I["utilities"].append(uu)
        I["waste"] += c["waste"]; I["equipment"] += c["equipment"]
        I["positions"] += c["positions"]
    if any("Vinagre" in k for k in keys) and any(k.startswith("L1") for k in keys):
        for bp in I["byproducts"]:                          # el vino desviado a vinagre no se vende como vino
            if bp["name"] == "L1 Vino de piña":
                bp["qty_year"] -= cs["L3 Vinagre (acetador sumergido)"]["raw"][0]["qty_year"]
    I["byproducts"] = [bp for bp in I["byproducts"] if not bp["name"].startswith("L7b")]
    if len(keys) >= 2:
        I["positions"] = math.ceil(I["positions"] * 0.75)     # personal compartido entre líneas [S]
    I["engineer"] = 2 if len(keys) >= 3 else 1
    return I


TORNADO_KEYS = dict(price="Precio del producto", raw_scale="Costo de la materia prima principal", f_prod="Factor de producción",
                    tasa="Tasa de descuento", capex_scale="CapEx (±30 %)")


def tornado_specs(case):
    pr = case["product"]["price"]
    return [("Precio del producto", "price", 0.7 * pr, pr, 1.3 * pr),
            ("Costo de la materia prima principal", "raw_scale", 1.5, 1.0, 0.5),
            ("Factor de producción", "f_prod", 0.8 / 0.9, 1.0, 0.98 / 0.9),
            ("Tasa de descuento", "tasa", 0.18, 0.10, 0.06),
            ("CapEx (±30 %)", "capex_scale", 1.3, 1.0, 0.7)]


def mc_dists(case):
    pr = case["product"]["price"]
    return [("price", 0.7 * pr, pr, 1.3 * pr), ("raw_scale", 0.5, 1.0, 1.8), ("f_prod", 0.8 / 0.9, 1.0, 0.98 / 0.9),
            ("tasa", 0.06, 0.10, 0.18), ("capex_scale", 0.8, 1.0, 1.5)]


MC_R = [[1, 0.45, 0, 0, 0], [0.45, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]   # plantilla: ρ(precio, MP)=0,45


def run_all(fruit_t, tag, mc_n=1000):
    D = pt.design(fruit_t)
    cs = cases_from_design(D)
    keys_int = ["L1 Vino de piña (rápido, 30 °C)", "L3 Vinagre (acetador sumergido)", "L4 Bromelaína + polvo nutracéutico",
                "L5 Harina de fibra de cáscara", "L6 Etanol hidratado (jugo de cáscara)", "L7b Caldera de biomasa (TRL 9)"]
    cs["Planta integrada TRL-9"] = integrated_case(cs, keys_int)
    out = {}
    for k, c in cs.items():
        r = tb.evaluate(c)
        be = tb.breakeven_price(c) if not k.startswith("Planta") else np.nan
        base, tor = tb.tornado(c, tornado_specs(c))
        mc = tb.monte_carlo(c, mc_dists(c), MC_R, n=mc_n)
        out[k] = dict(res={kk: vv for kk, vv in r.items() if kk not in ("capex",)}, capex={kk: vv for kk, vv in r["capex"].items() if kk != "rows"},
                      equipment=r["capex"]["rows"], breakeven=be, tornado=tor,
                      mc=dict(P_pos=mc["P_pos"], P5=mc["P5"], P50=mc["P50"], P95=mc["P95"], CVaR5=mc["CVaR5"],
                              NPV=mc["NPV"].tolist()), case=c)
        print(tag, k, f"FCI {r['FCI']/1e6:,.0f} MM | VPN {r['NPV']/1e6:,.0f} MM | MIRR {r['MIRR']*100 if r['MIRR']==r['MIRR'] else float('nan'):.1f} % | "
                      f"CN {r['LCOP']:,.0f} vs P {c['product']['price']:,.0f} | PE {be:,.0f} | P(VPN>0) {mc['P_pos']:.2f}", flush=True)
    return D, out


if __name__ == "__main__":
    allres = {}
    for tag, fruit in (("Base tesis (78 300 hL)", cp.fruit_for_wine(p.WINE_VOL_YR)[0]),
                       ("Chocó 2022 (6 146 t)", 6146.0),
                       ("Pérdida poscosecha Chocó (1 537 t)", 6146.0 * 0.25)):
        D, out = run_all(fruit, tag, mc_n=600)
        allres[tag] = dict(fruit_t=fruit, design=dict(TRL=D["TRL"], lines={k: dict(flows=v["flows"],
                           equipment=[{kk: vv for kk, vv in e.items()} for e in v["equipment"]]) for k, v in D["lines"].items()}),
                           tea=out)
    json.dump(allres, open(f"{RES}/tea_lineas.json", "w"), default=float)
