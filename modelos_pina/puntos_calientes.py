"""
Puntos calientes del diseño óptimo (v10): etapa 3 del marco de Bertran, Tula y Gani (2022): del análisis del diseño
(etapa 2) salen los puntos calientes, y de ellos los objetivos de mejora que guían las alternativas de innovación.

Por sección de la planta se reparten: el cargo de capital anual de sus equipos (AF × compra), la electricidad y el
calor que piden sus flujos (mismos coeficientes que el MILP) y su GWP de proceso. Una sección es punto caliente si
concentra una parte del costo, la energía o el GWP mayor que su parte de los ingresos.
Salidas: results/puntos_calientes.json y figs/fig44_puntos_calientes.png.
"""
import json, os
import dimensionamiento as dm
import capacidad as cp

RES = dm.RES
SECCIONES = {
    "Frente y pulpa": ["Frente", "Prensa", "Decantadora"],
    "Mosto y bodega de vino": ["Clarificación", "MF lías", "Estabilización", "Bodega", "Almacén de mosto"],
    "Cáscara y harina": ["Prensa cáscara", "Pretratamiento cáscara", "Secador", "Enzima cáscara"],
    "Vinagre": ["Bodega cáscara", "Acetificador"],
    "Caldera de biomasa": ["Caldera de corona"],
    "Hojas (extracción, etanol, biogás)": ["Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás"],
    "Hub (cítrico, xantana)": ["Ácido cítrico", "Xantana"],
}


def analyse(key="E1|Óptimo económico"):
    d = json.load(open(os.path.join(RES, "dimensionamiento.json")))
    r = d[key]; s = r["scen"][0]; p = s["products"]; sz = r["sizes"]
    O = dm.options(False)
    cost = lambda u: next((o["cost"] * dm.AF + o.get("fixed", 0.0) for o in O[u] if o["lab"] == sz.get(u, "no")), 0.0) if u in O else 0.0
    F = p["fruta_t"]; rows = s["periods"]
    V_acet = float(sz["Acetificador"].split()[0]) if sz.get("Acetificador", "no") != "no" else 0.0
    sec_t = sum(x["sec"] for x in rows); pulp = sum(x["P"].get("pulpa", 0) for x in rows)
    kwh = {
        "Frente y pulpa": dm.KWH["fruit"] * F,
        "Mosto y bodega de vino": dm.KWH["bod"] * sum(x["bod"] for x in rows) + 2.0 * p.get("mosto_m3", 0) + p.get("lias_MF_m3", 0),
        "Cáscara y harina": dm.KWH["peel"] * F * cp.FR["cascara"][0] + dm.KWH["flour"] * p["harina_t"],
        "Vinagre": dm.ACID_HEAT / 3.6 / 4 * p.get("acido_kg", 0) + dm.AERATION_KW_M3 * V_acet * dm.AC * 8766,
        "Caldera de biomasa": dm.KWH["crown"] * p.get("corona_caldera_t", 0) + dm.KWH_LEAF["pulp"] * p.get("pulpa_hojas_caldera_t", 0),
        "Hojas (extracción, etanol, biogás)": (dm.KWH_LEAF["ext"] * p.get("hojas_extraidas_t", 0) + dm.KWH_LEAF["etoh"] * p.get("jugo_hojas_etanol_t", 0)
                                               + dm.KWH_LEAF["ad"] * p.get("jugo_hojas_digestor_t", 0)),
        "Hub (cítrico, xantana)": 0.0,
    }
    heat = {k: 0.0 for k in SECCIONES}
    heat["Frente y pulpa"] = dm.Q_MAC * pulp
    heat["Cáscara y harina"] = dm.Q_CAKE * sec_t
    heat["Hojas (extracción, etanol, biogás)"] = dm.Q_DEST * p.get("etanol_kg", 0) + dm.Q_AD * p.get("jugo_hojas_digestor_t", 0)
    q_tot = sum(heat.values()) or 1.0
    glp_share = max(p.get("calor_glp_MJ", 0), 0) / q_tot
    rev = {"Mosto y bodega de vino": (p["vino_m3"] - p.get("vino_a_vinagre_m3", 0)) * 1000 * dm.WINE_PRICE,
           "Cáscara y harina": (p["harina_t"] + p.get("harina_lias_t", 0)) * 1000 * dm.tl.M("harina_kg"),
           "Vinagre": p.get("vinagre_m3", 0) * 1000 * dm.VIN_PRICE,
           "Hojas (extracción, etanol, biogás)": p.get("etanol_L", 0) * dm.ETOH_PRICE + p.get("levadura_kg", 0) * dm.YEAST_PRICE
                                                  + p.get("elec_excedente_kWh", 0) * dm.VAL_EXC,
           "Hub (cítrico, xantana)": p.get("citrico_kg", 0) * dm.HUB["Ácido cítrico"]["price"] + p.get("xantana_kg", 0) * dm.HUB["Xantana"]["price"]}
    e_bio = p.get("elec_bio_usada_kWh", 0); e_tot = sum(kwh.values()) or 1.0
    out = {}
    for sec, units in SECCIONES.items():
        g = dm.EF_KWH * kwh[sec] * (1 - e_bio / e_tot) + dm.EF_GLP_UTIL * heat[sec] * glp_share
        if sec == "Caldera de biomasa":
            g += dm.EF_BIO_FUEL * p.get("calor_corona_GJ", 0) * 1000
        if sec == "Hojas (extracción, etanol, biogás)":
            g += dm.EF_ACOPIO * p.get("hojas_t", 0) + dm.EF_LEAK * p.get("ch4_kg", 0)
        out[sec] = dict(capital=sum(cost(u) for u in units), elec_kWh=kwh[sec], calor_MJ=heat[sec], gwp_kg=g, ingreso=rev.get(sec, 0.0))
    tot = {k: sum(v[k] for v in out.values()) or 1.0 for k in ("capital", "elec_kWh", "calor_MJ", "gwp_kg", "ingreso")}
    for sec, v in out.items():
        v.update({f"frac_{k}": v[k] / tot[k] for k in tot})
        v["punto_caliente"] = [k for k in ("capital", "elec_kWh", "calor_MJ", "gwp_kg") if v[f"frac_{k}"] > max(v["frac_ingreso"], 0.0) + 0.10]
    json.dump(out, open(os.path.join(RES, "puntos_calientes.json"), "w"), indent=1, default=float)
    for sec, v in out.items():
        print(f"{sec}: capital {v['frac_capital']:.0%} · elec {v['frac_elec_kWh']:.0%} · calor {v['frac_calor_MJ']:.0%} · GWP {v['frac_gwp_kg']:.0%} · "
              f"ingreso {v['frac_ingreso']:.0%} → {v['punto_caliente']}")
    return out


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from figuras import C, save
    secs = [s for s in out if any(out[s][f"frac_{k}"] > 0.005 for k in ("capital", "elec_kWh", "calor_MJ", "gwp_kg", "ingreso"))]
    keys = [("frac_capital", "cargo de capital"), ("frac_elec_kWh", "electricidad"), ("frac_calor_MJ", "calor"), ("frac_gwp_kg", "GWP"), ("frac_ingreso", "ingresos")]
    fig, ax = plt.subplots(figsize=(13.5, 4.6))
    x = np.arange(len(secs)); w = 0.16
    for i, (k, lab) in enumerate(keys):
        ax.bar(x + (i - 2) * w, [out[s][k] * 100 for s in secs], w, color=C[i], label=lab)
    for xi, s in zip(x, secs):
        if out[s]["punto_caliente"]:
            ax.text(xi, max(out[s][k] for k, _ in keys) * 100 + 3, "punto caliente", ha="center", fontsize=7.5, color=C[7])
    ax.set_xticks(x); ax.set_xticklabels(secs, fontsize=8, rotation=10); ax.set_ylabel("% del total de la planta"); ax.legend(fontsize=8, ncol=5)
    ax.set_title("Una sección es punto caliente si pesa en costo, energía o GWP más de 10 puntos por encima de lo que aporta en ingresos", fontsize=9)
    fig.suptitle("Fig. 44  Puntos calientes del diseño óptimo v10 (etapa 3: de los puntos calientes a los objetivos de mejora)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig44_puntos_calientes.png")


if __name__ == "__main__":
    figure(analyse())
