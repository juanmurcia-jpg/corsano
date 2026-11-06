"""
Análisis de ciclo de vida de la cuna a la puerta (v10). Heinzle et al. (2006, cap. 4.3); Liao et al. (2022, 2026);
Bertran, Tula y Gani (2022, etapa 2: análisis económico y ambiental para detectar puntos calientes).

Unidad funcional: la operación de un año de la planta (y, normalizado, 1 t de fruta procesada). Límites: desde la
fruta y las hojas en finca hasta los productos a granel en la puerta de la planta. Bienes de capital, empaques y
distribución quedan fuera.

Inventario: sale de la solución del dimensionamiento (products de dimensionamiento.json) con los mismos coeficientes
que usa el MILP para su GWP lineal (dimensionamiento.KWH, EF_*), más el agua del TEA. Categorías:
  - GWP100 (kg CO2e, IPCC AR6), por contribución: electricidad diésel, GLP, caldera de biomasa (CH4 y N2O),
    compostaje, fugas de biogás, acopio de hojas, transporte de fruta e insumos químicos;
  - energía fósil (MJ): diésel del grupo electrógeno y del acopio, y GLP;
  - agua (m³) y material particulado (kg, solo la quema evitada).
Línea base sin planta: la fruta de rechazo se descompone en campo (factores de compostaje [S]) y las hojas que se
acopian se queman (Liao et al. 2026) o se descomponen en campo. Expansión del sistema (aparte): el etanol reemplaza
gasolina y el excedente eléctrico reemplaza diésel de la red local.
Asignación económica a los productos (VPN del TEA no interviene): por valor anual de ventas.
Salidas: results/acv.json y figs/fig40_acv.png.
"""
import json, os
import datos as D
import dimensionamiento as dm
import capacidad as cp

RES = dm.RES
CASES = [("Referencia TRL-9", "E1|Referencia TRL-9 (planta_trl9, 6 200 t)"), ("Diseño v11", "E1|Diseño v11 con parámetros v12"),
         ("Óptimo sin opciones v10", "E1|Óptimo sin opciones v10 (sin hojas ni hub)"), ("Óptimo sin caldera", "E1|Óptimo sin caldera de corona"),
         ("Óptimo sin vinagre", "E1|Óptimo sin vinagre"), ("Óptimo sin azúcar", "E1|Óptimo sin azúcar añadido"), ("Óptimo v12", "E1|Óptimo económico")]
GASOLINA_EF = 2.8 * 0.65          # kg CO2e evitados por L de etanol hidratado (0,65 L de gasolina equivalente) [S]


def inventory(r, case=None):
    s = r["scen"][0]; p = s["products"]; sz = r["sizes"]
    F = p["fruta_t"]
    V_acet = float(sz["Acetificador"].split()[0]) if sz.get("Acetificador", "no") != "no" else 0.0
    aer = dm.AERATION_KW_M3 * V_acet * dm.AC * 8766
    e_dem = p.get("elec_demanda_kWh", 0.0) + aer
    e_net = e_dem - p.get("elec_bio_usada_kWh", 0.0)
    q_glp = max(p.get("calor_glp_MJ", 0.0), 0.0)
    q_bio = p.get("calor_corona_GJ", 0.0) * 1000
    comp_t = ((cp.FR["corazon"][0] + cp.FR["corona"][0]) * F - p.get("corona_caldera_t", 0.0) + p.get("cascara_compost_t", 0.0)
              + p.get("lias_compost_m3", 0.0))
    rows = s["periods"]
    so2_m3 = sum(x.get("stab", 0.0) for x in rows) if sz.get("Estabilización", "").startswith("SO") else 0.0
    lime_t = p.get("cascara_cal_t", 0.0)
    pulp_t = F * cp.FR["pulpa"][0]
    yeast_base = p["vino_m3"] / dm.WINE_PM + p.get("jugo_cascara_vinagre_t", 0.0) + p.get("jugo_hojas_vinagre_t", 0.0) + p.get("jugo_hojas_etanol_t", 0.0)
    g = {
        "Electricidad (grupo diésel)": dm.EF_KWH * e_net,
        "Calor con GLP": dm.EF_GLP_UTIL * q_glp,
        "Caldera de biomasa (CH4, N2O)": dm.EF_BIO_FUEL * q_bio,
        "Compostaje de fracciones sin uso": dm.EF_COMP * comp_t,
        "Fugas de biogás": dm.EF_LEAK * p.get("ch4_kg", 0.0),
        "Acopio de hojas (diésel)": dm.EF_ACOPIO * p.get("hojas_t", 0.0),
        "Transporte de fruta": dm.EF_FRUIT_T * F,
        "Insumos químicos": (dm.EF_CHEM["dap"] * p.get("mosto_m3", 0.0) + dm.EF_CHEM["so2"] * so2_m3 + dm.EF_CHEM["yeast"] * yeast_base
                             + dm.EF_CHEM["lime"] * lime_t + dm.EF_CHEM["pect"] * pulp_t),
        "Panela añadida": dm.EF_AZ * p.get("azucar_kg", 0.0),                                  # v11
        "Botellas de vidrio": dm.EF_BOT * p.get("botellas", 0.0),                                # v12
    }
    fossil = (e_net * 3.6 / D.val("eta_grupo_diesel") + q_glp / D.val("eta_caldera_glp")
              + D.val("diesel_acopio_hojas") * p.get("hojas_t", 0.0)
              + dm.EF_FRUIT_T * F / D.val("ef_diesel") * D.val("pci_diesel"))
    water = next((u["qty_year"] for u in (case or {}).get("utilities", []) if u["name"].startswith("Agua")), None)
    # v11: efluente tratado con electrocoagulación y humedal construido (Ebrahimi 2026, sec. 12.5.4): electricidad de la
    # electrocoagulación y CH4 de la DQO que degrada el humedal (IPCC); la DQO que queda se reporta aparte
    eff = (water or 0.0) * D.val("frac_efluente")
    dqo = eff * D.val("dqo_efluente_kg_m3")
    dqo_ec = dqo * D.val("remocion_dqo_ec"); dqo_hum = (dqo - dqo_ec) * D.val("remocion_dqo_humedal")
    g["Tratamiento de efluentes"] = (dm.EF_KWH * D.val("kwh_ec_kg_dqo") * dqo_ec
                                     + D.val("bo_ch4_dqo") * D.val("mcf_humedal") * dqo_hum * D.val("gwp_ch4"))
    fossil += D.val("kwh_ec_kg_dqo") * dqo_ec * 3.6 / D.val("eta_grupo_diesel")
    effluent = dict(m3=eff, dqo_kg=dqo, dqo_vertida_kg=dqo - dqo_ec - dqo_hum)
    # línea base: fruta que se descompone en campo y hojas acopiadas que se queman o se descomponen
    ms_h = D.val("ms_hojas"); burn = D.val("quema_frac_ms")
    base_fruit = dm.EF_COMP * F
    leaves = p.get("hojas_t", 0.0)
    base_leaf_burn = leaves * ms_h * burn * (D.val("quema_ch4") * D.val("gwp_ch4") + D.val("quema_n2o") * D.val("gwp_n2o"))   # kg/t MS × t MS
    base_leaf_decomp = dm.EF_COMP * leaves
    pm_avoided = leaves * ms_h * burn * D.val("quema_pm")
    credits = {"Etanol en lugar de gasolina": GASOLINA_EF * p.get("etanol_L", 0.0),
               "Excedente eléctrico en lugar de diésel": dm.EF_KWH * p.get("elec_excedente_kWh", 0.0)}
    total = sum(g.values())
    return dict(F=F, gwp=g, gwp_total=total, gwp_milp=p.get("gwp_kg"), fossil_MJ=fossil, water_m3=water,
                base=dict(fruta=base_fruit, hojas_quema=base_leaf_burn, hojas_descomposicion=base_leaf_decomp), pm_evitado_kg=pm_avoided,
                credits=credits, net_vs_quema=total - base_fruit - base_leaf_burn, net_vs_descomposicion=total - base_fruit - base_leaf_decomp,
                net_con_expansion=total - base_fruit - base_leaf_decomp - sum(credits.values()), per_t_fruta=total / F,
                e_dem_kWh=e_dem, e_bio_kWh=p.get("elec_bio_usada_kWh", 0.0), q_glp_MJ=q_glp, efluente=effluent)


def allocation(inv, case):
    """Asignación económica del GWP neto de proceso a los productos (por valor de ventas)."""
    vals = {"vino (L)": (case["product"]["qty_year"], case["product"]["price"])}
    for bp in case["byproducts"]:
        if bp["qty_year"] > 0:
            vals[bp["name"]] = (bp["qty_year"], bp["price"])
    rev = {k: q * pr for k, (q, pr) in vals.items()}
    tot = sum(rev.values())
    return {k: dict(cantidad=vals[k][0], kgCO2e_por_unidad=inv["gwp_total"] * rev[k] / tot / vals[k][0] if vals[k][0] else None,
                    fraccion=rev[k] / tot) for k in rev}


def run():
    import tea_dimensionado as td
    d = json.load(open(os.path.join(RES, "dimensionamiento.json")))
    out = {}
    for lab, key in CASES:
        r = d.get(key)
        if not r or not r.get("scen"):
            continue
        case = td.build_case(r, lab, False)
        inv = inventory(r, case)
        inv["asignacion"] = allocation(inv, case)
        out[lab] = inv
        print(f"{lab}: GWP {inv['gwp_total'] / 1000:,.0f} t CO2e/año (MILP {inv['gwp_milp'] / 1000 if inv['gwp_milp'] else float('nan'):,.0f}); "
              f"{inv['per_t_fruta']:,.0f} kg/t fruta; neto frente a descomposición {inv['net_vs_descomposicion'] / 1000:,.0f} t; "
              f"fósil {inv['fossil_MJ'] / 1e6:,.1f} TJ", flush=True)
    json.dump(out, open(os.path.join(RES, "acv.json"), "w"), indent=1, default=float)
    return out


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from figuras import C, INK, INK2, save
    labs = list(out)
    cats = list(next(iter(out.values()))["gwp"])
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 4.8), gridspec_kw=dict(width_ratios=[1.35, 1]))
    x = np.arange(len(labs)); bottom = np.zeros(len(labs))
    pal = C + ["#8c564b", "#7f7f7f"]
    for i, c in enumerate(cats):
        vals = np.array([out[l]["gwp"][c] / 1000 for l in labs])
        ax[0].bar(x, vals, 0.6, bottom=bottom, color=pal[i % len(pal)], label=c); bottom += vals
    ax[0].plot(x, [(out[l]["gwp_total"] - out[l]["base"]["fruta"] - out[l]["base"]["hojas_descomposicion"]) / 1000 for l in labs], "kD", ms=6,
               label="neto frente a la línea base (descomposición en campo)")
    for xi, l in zip(x, labs):
        ax[0].text(xi, bottom[xi] + 25, f"{out[l]['gwp_total'] / 1000:,.0f}".replace(",", " "), ha="center", fontsize=8)
    ax[0].axhline(0, color=INK2, lw=0.8)
    ax[0].set_xticks(x); ax[0].set_xticklabels(labs, rotation=15, ha="right", fontsize=8)
    ax[0].set_ylabel("t CO2e/año"); ax[0].legend(fontsize=7, loc="upper left", ncol=2)
    ax[0].set_title("GWP de proceso por contribución y neto frente a la línea base", fontsize=9)
    best = out.get("Óptimo v12") or out[labs[-1]]
    al = {k: v for k, v in best["asignacion"].items() if v["kgCO2e_por_unidad"]}
    names = {"vino (L)": "vino (kg CO2e/L)", "vinagre": "vinagre (kg CO2e/L)", "harina": "harina (kg CO2e/kg)", "etanol": "etanol (kg CO2e/L)",
             "levadura": "levadura (kg CO2e/kg)", "jugo": "jugo de cáscara (kg CO2e/kg)", "electricidad_excedente": "excedente eléctrico (kg CO2e/kWh)"}
    ks = list(al)
    ax[1].barh(range(len(ks)), [al[k]["kgCO2e_por_unidad"] for k in ks], color=C[0])
    for i, k in enumerate(ks):
        ax[1].text(al[k]["kgCO2e_por_unidad"] * 1.02, i, f"{al[k]['kgCO2e_por_unidad']:.2f} · {al[k]['fraccion'] * 100:.0f} % del valor", va="center", fontsize=8)
    ax[1].set_yticks(range(len(ks))); ax[1].set_yticklabels([names.get(k, k) for k in ks], fontsize=8); ax[1].invert_yaxis()
    ax[1].set_xlim(0, max(al[k]["kgCO2e_por_unidad"] for k in ks) * 1.6)
    ax[1].set_title("Huella por producto del óptimo v12 (asignación económica)", fontsize=9)
    fig.suptitle("Fig. 40  Análisis de ciclo de vida de la cuna a la puerta (GWP100, IPCC AR6): contribuciones, línea base y huella por producto",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig40_acv.png")


if __name__ == "__main__":
    figure(run())
