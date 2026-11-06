"""Figuras 27-30 (versión 4): dimensionamiento óptimo de equipos acoplado al programa anual (dimensionamiento.py)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figuras import C, INK, INK2, GRID, SURF, save, J

import fig_en
MES = fig_en.months()
CUM = np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
ORDER = ["Frente", "Prensa", "Decantadora", "Prensa cáscara", "Prensa corazón", "Clarificación", "MF lías", "Estabilización", "Bodega", "Secador", "Aspersión", "Enzima cáscara", "Bodega cáscara", "Acetificador", "Caldera de corona", "Extractora hojas"]


def _key(d, start):
    return next((k for k in d if k.startswith(start)), None)


SHORT = {"Referencia TRL-9 (planta_trl9, 6 200 t)": "Referencia TRL-9", "Óptimo con la topología anterior (prensa, MF de mosto, HTST)": "Óptimo · topología anterior",
         "Óptimo económico": "Óptimo · superestructura ampliada"}
PAL = list(C) + ["#8c564b", "#17becf", "#7f7f7f", "#bcbd22"]


def fig27_dimensionamiento(d):
    keys = [k for k in (_key(d, "E1|Referencia TRL-9"), _key(d, "E1|Óptimo con la topología anterior"), _key(d, "E1|Óptimo económico")) if k]
    if not keys:
        return
    fig, ax = plt.subplots(1, len(keys) + 1, figsize=(4.4 * (len(keys) + 1), 4.2), gridspec_kw=dict(width_ratios=[1] * len(keys) + [1.05]))
    for q, k in enumerate(keys):
        r = d[k]; s = r["scen"][0]
        us = [u for u in ORDER if u in s["util"]]
        M = np.array([s["util"][u] for u in us])
        im = ax[q].imshow(M, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
        for i in range(M.shape[0]):
            for j in range(12):
                ax[q].text(j, i, f"{M[i, j]*100:.0f}", ha="center", va="center", fontsize=6.3,
                           color="white" if M[i, j] > 0.7 else INK, fontweight="bold" if M[i, j] >= 0.95 else None)
        ax[q].set_yticks(range(len(us)))
        ax[q].set_yticklabels([f"{u}\n{r['sizes'].get(u, '')}" for u in us], fontsize=7)
        ax[q].set_xticks(range(12)); ax[q].set_xticklabels(MES, fontsize=7); ax[q].grid(False)
        ax[q].set_title(f"{SHORT.get(k.split('|')[1], k.split('|')[1])}\nmargen {r['obj']:,.0f} MM/año · pérdida {s['loss']/s['supply']*100:.1f} %".replace(",", " "), fontsize=8.5)
    fig.colorbar(im, ax=ax[len(keys) - 1], fraction=0.04).set_label("Ocupación (%)")
    # CapEx (compra) por equipo
    import dimensionamiento as dm
    O = dm.options(False)
    axb = ax[-1]
    units = [u for u in O]
    x = np.arange(len(keys)); bottom = np.zeros(len(keys))
    for i, u in enumerate(units):
        vals = []
        for k in keys:
            lab = d[k]["sizes"][u]
            vals.append(next(o["cost"] for o in O[u] if o["lab"] == lab) * dm.LANG / 1e6)
        axb.bar(x, vals, 0.6, bottom=bottom, color=PAL[i % len(PAL)], label=u, edgecolor=SURF, lw=0.5)
        bottom += np.array(vals)
    for xi, b in zip(x, bottom):
        axb.text(xi, b + 100, f"{b:,.0f}".replace(",", " "), ha="center", fontsize=8)
    axb.set_xticks(x); axb.set_xticklabels([SHORT.get(k.split("|")[1], k.split("|")[1]).replace(" · ", "\n") for k in keys], fontsize=7.5)
    axb.set_ylabel("FCI de los equipos dimensionados (MM COP)"); axb.legend(fontsize=6.5, ncol=1, loc="center left", bbox_to_anchor=(1.01, 0.5))
    axb.set_ylim(0, max(bottom) * 1.12)
    axb.set_title("Inversión por equipo (factor Lang de Burk)", fontsize=9)
    fig.suptitle("Fig. 27  Dimensionamiento óptimo frente al diseño TRL-9: ocupación mensual de cada equipo (≥ 95 % en negrita) e inversión",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig27_dimensionamiento.png")


def fig28_escala(d):
    ks = sorted([k for k in d if k.startswith("E2|") and d[k].get("scen")], key=lambda k: float(k.split("|")[1]))
    if not ks:
        return
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.6), gridspec_kw=dict(width_ratios=[1.45, 1, 1]))
    sup = [d[k]["scen"][0]["supply"] for k in ks]
    units = [u for u in ORDER if u in d[ks[0]]["sizes"]] + ["Almacén de mosto"]
    M = np.zeros((len(units), len(ks)))
    for j, k in enumerate(ks):
        ut = d[k]["scen"][0]["util"]
        for i, u in enumerate(units):
            M[i, j] = max(ut[u]) if u in ut else np.nan
    im = ax[0].imshow(np.nan_to_num(M, nan=0), aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
    for j, k in enumerate(ks):
        for i, u in enumerate(units):
            lab = d[k]["sizes"][u]
            short = (lab.replace(" kg agua/h", "").replace(" t/h", "").replace(" m³/h", "").replace(" m³", "").replace(" m²", "").replace(" kWt", "")
                     .replace("Centrífuga ", "C ").replace("Flotación ", "F ").replace("Precipitación ", "P ").replace("MF ", "MF ").replace(".", ","))
            ax[0].text(j, i, short, ha="center", va="center",
                       fontsize=6.4, color="white" if (M[i, j] == M[i, j] and M[i, j] > 0.7) else INK)
    ax[0].set_yticks(range(len(units))); ax[0].set_yticklabels([u + {"Frente": " (t/h)", "Prensa": " (t/h)", "Prensa cáscara": " (t/h)", "Decantadora": " (t/h)", "MF lías": " (m²)",
                                                                       "Secador": " (kg agua/h)", "Almacén de mosto": " (m³)", "Clarificación": " (C/F/MF, m³/h o m²)",
                                                                       "Enzima cáscara": " (P = precipitación, t/h)", "Acetificador": " (m³)", "Caldera de corona": " (kWt)", "Bodega cáscara": " (n × m³)", "Extractora hojas": " (t/h)"}.get(u, "") for u in units], fontsize=7.5)
    ax[0].set_xticks(range(len(ks))); ax[0].set_xticklabels([f"{x/1000:.1f}k" + ("\nT3" if d[k]["turno3"] else "") for x, k in zip(sup, ks)], fontsize=7)
    ax[0].set_xlabel("Oferta de fruta (t/año); T3 = tercer turno"); ax[0].grid(False)
    ax[0].set_title("Tamaño óptimo (texto) y ocupación del mes pico (color)", fontsize=9)
    fig.colorbar(im, ax=ax[0], fraction=0.035).set_label("Ocupación pico")
    obj = [d[k]["obj"] for k in ks]; fci = [d[k]["FCI"] for k in ks]
    proc = [d[k]["scen"][0]["products"]["fruta_t"] for k in ks]
    ax[1].plot(sup, obj, "-o", color=C[0], label="Margen anual (MM COP)")
    ax[1].plot(sup, fci, "-s", color=C[1], label="FCI de equipos (MM COP)")
    ax[1].set_xlabel("Oferta (t/año)"); ax[1].set_ylabel("MM COP"); ax[1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    a2 = ax[1].twinx(); a2.plot(sup, [f / p_ * 1e6 / 1e3 for f, p_ in zip(fci, proc)], ":^", color=C[3], label="FCI específico"); a2.grid(False)
    a2.set_ylabel("FCI por t de fruta procesada al año (miles COP)", color=C[3])
    ax[1].axvline(6146, color=GRID, ls="--"); ax[1].text(6300, ax[1].get_ylim()[1] * 0.92, "Chocó 2022", fontsize=7, color=INK2)
    ax[1].set_title("Economía de escala del diseño óptimo", fontsize=9)
    e3 = [(k.split("|")[1], d[k]["obj"], d[k]["scen"][0]["loss"] / d[k]["scen"][0]["supply"]) for k in d if k.startswith("E3|") and d[k].get("scen")]
    if e3:
        labs = [a for a, _, _ in e3]; vals = [b for _, b, _ in e3]
        ax[2].barh(range(len(vals)), vals, color=[C[0]] + [C[2]] * (len(vals) - 1))
        for i, (v, l) in enumerate(zip(vals, [c for _, _, c in e3])):
            ax[2].text(v * 0.02, i, f"{v:,.0f} · pérdida {l*100:.1f} %".replace(",", " "), va="center", fontsize=7.5, color="white")
        ax[2].set_yticks(range(len(vals))); ax[2].set_yticklabels(labs, fontsize=7.5); ax[2].invert_yaxis()
        ax[2].set_xlabel("Margen anual (MM COP/año)")
        ax[2].set_title("Palancas a 2× la oferta", fontsize=9)
    fig.suptitle("Fig. 28  Regla de dimensionamiento: tamaños óptimos según la oferta, economía de escala y valor del almacén aséptico y del tercer turno",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig28_escala_dimensionamiento.png")


def fig29_30_flujos(d):
    k = _key(d, "E1|Óptimo económico") or _key(d, "E1|Óptimo sin pérdida")
    if not k:
        return
    r = d[k]; s = r["scen"][0]; rows = s["periods"]
    caps = r["caps"]
    # ---------------- Fig. 29: flujos mensuales e inventario del almacén aséptico
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.2))
    sup = np.array(s["supply_month"]); fe = np.array([sum(x["fe"] for x in rows if x["month"] == m) for m in range(12)])
    bod = np.array([sum(x["bod"] for x in rows if x["month"] == m) for m in range(12)])
    mf = np.array([sum(x["mf"] for x in rows if x["month"] == m) for m in range(12)])
    xm = np.arange(12)
    ax[0].bar(xm - 0.2, sup, 0.4, color=C[6], label="Oferta de fruta (t/mes)")
    ax[0].bar(xm + 0.2, fe, 0.4, color=C[0], label="Fruta procesada (t/mes)")
    a2 = ax[0].twinx()
    a2.plot(xm, mf, "-o", color=C[1], label="Mosto a clarificación (m³/mes)"); a2.plot(xm, bod, "-s", color=C[3], label="Mosto fermentado (bodega, m³/mes)")
    a2.set_ylabel("m³/mes"); a2.grid(False)
    ax[0].set_xticks(xm); ax[0].set_xticklabels(MES); ax[0].set_ylabel("t/mes")
    h1, l1 = ax[0].get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels(); ax[0].legend(h1 + h2, l1 + l2, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax[0].set_title("Sin almacenar fruta, la clarificación y la bodega siguen a la cosecha", fontsize=9)
    t = np.array([x["start"] + x["dur"] for x in rows]) / 24; Iv = np.array([x["I_mosto"] for x in rows])
    ax[1].fill_between(np.r_[0, t], np.r_[Iv[-1], Iv], step="pre", color=C[1], alpha=0.35)
    ax[1].step(np.r_[0, t], np.r_[Iv[-1], Iv], where="pre", color=C[1])
    ax[1].axhline(caps["Almacén de mosto"], color=C[3], ls="--", lw=1); ax[1].text(5, caps["Almacén de mosto"] * 0.96, f"capacidad {r['sizes']['Almacén de mosto']}", fontsize=7.5, va="top", color=C[3])
    ax[1].set_xticks(CUM[:-1] + 15); ax[1].set_xticklabels(MES); ax[1].set_xlim(0, 365); ax[1].set_ylabel("Mosto en almacén aséptico (m³)")
    ax[1].set_title("El pulmón de mosto solo amortigua días: el modelo no compra un almacén mayor", fontsize=9)
    fig.suptitle(f"Fig. 29  Flujos balanceados del diseño óptimo ({k.split('|')[1]})", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig29_flujos_almacen.png")
    # ---------------- Fig. 30: Gantt anual del diseño óptimo
    lanes = ["Frente"] + (["Prensa · pulpa"] if caps.get("Prensa", 0) > 0 else []) + (["Decantadora (pulpa)"] if caps.get("Decantadora", 0) > 0 else []) + (["Prensa cáscara (dedicada)"] if caps.get("Prensa cáscara", 0) > 0 else ["Prensa · cáscara"]) + ["Clarificación"] + (["MF de lías"] if caps.get("MF lías", 0) > 0 else []) + ["Bodega", "Secador"]
    fig, ax = plt.subplots(figsize=(13, 4.4))
    a_st = (1.5 if r["turno3"] else 1.0) * (s["util"] and 1.0)
    import dimensionamiento as dm
    a_st = dm.A3 if r["turno3"] else dm.A2
    for x in rows:
        s0, du = x["start"] / 24, x["dur"] / 24
        if du <= 1e-6:
            continue
        for lane, val, u, a in (("Frente", x["fe"], "Frente", a_st), ("Clarificación", x["mf"], "Clarificación", a_st), ("MF de lías", x.get("ml", 0), "MF lías", a_st), ("Decantadora (pulpa)", x["Pd"].get("pulpa", 0), "Decantadora", a_st), ("Bodega", x["bod"], "Bodega", dm.AC),
                                ("Secador", x["sec"], "Secador", dm.AC), ("Prensa cáscara (dedicada)", x["Pd"].get("cascara", 0), "Prensa cáscara", a_st)):
            if lane not in lanes:
                continue
            f = min(val / (caps[u] * a * x["dur"]), 1.0)
            ax.barh(lanes.index(lane), du, left=s0, color=plt.cm.Blues(0.2 + 0.75 * f), height=0.7, edgecolor=SURF, lw=0.3)
        for mode, lane, cc in (("pulpa", "Prensa · pulpa", C[0]), ("cascara", "Prensa · cáscara", C[1])):
            if lane not in lanes:
                continue
            f = min(x["tau"].get(mode, 0) / (a_st * x["dur"]), 1.0)
            if f > 1e-3:
                ax.barh(lanes.index(lane), du, left=s0, color=cc, alpha=0.25 + 0.75 * f, height=0.7, edgecolor=SURF, lw=0.3)
    for m in range(12):
        n = sum(x["W"] for x in rows if x["month"] == m)
        if n >= 0.5:
            ax.text(CUM[m] + 15, 1 - 0.55, f"{n:.0f} cambios", ha="center", fontsize=6.5, color=INK2)
    for c_ in CUM:
        ax.axvline(c_, color=GRID, lw=0.8)
    ax.set_xticks(CUM[:-1] + 15); ax.set_xticklabels(MES); ax.set_xlim(0, 365)
    ax.set_yticks(range(len(lanes))); ax.set_yticklabels([f"{l}" for l in lanes]); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    sm = plt.cm.ScalarMappable(cmap="Blues", norm=matplotlib.colors.Normalize(0, 1)); fig.colorbar(sm, ax=ax, pad=0.01).set_label("Ocupación")
    sz = {u: v for u, v in r["sizes"].items() if v != "no"}
    it = [f"{u} {sz[u]}" for u in sz] + (["turno 3"] if r["turno3"] else [])
    ax.set_title("Tamaños: " + " · ".join(it[:5]) + "\n" + " · ".join(it[5:]), fontsize=8)
    fig.suptitle("Fig. 30  Gantt anual del diseño óptimo: ninguna unidad topa la producción salvo la que el margen justifica",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig30_gantt_optimo.png")


if __name__ == "__main__":
    d = J("dimensionamiento.json")
    if d:
        fig27_dimensionamiento(d); fig28_escala(d); fig29_30_flujos(d)


def fig31_tea():
    t = J("tea_dimensionado.json")
    if not t:
        return
    cs = t["cases"]
    keys = [k for k in ("A · Referencia TRL-9", "A · Óptimo con la topología anterior", "A · Óptimo sin vinagre", "A · Óptimo con la superestructura ampliada", "B · Óptimo con la topología anterior", "B · Óptimo con la superestructura ampliada") if k in cs]
    fig, ax = plt.subplots(2, 2, figsize=(13.5, 8.4))
    # (a) FCI y VPN
    a = ax[0, 0]; x = np.arange(len(keys)); w = 0.38
    fci = [cs[k]["res"]["FCI"] / 1e6 for k in keys]; npv = [cs[k]["res"]["NPV"] / 1e6 for k in keys]
    a.bar(x - w / 2, fci, w, color=C[1], label="FCI (MM COP)"); a.bar(x + w / 2, npv, w, color=C[0], label="VPN al 10 % (MM COP)")
    for xi, f, n, k in zip(x, fci, npv, keys):
        a.text(xi - w / 2, f + 200, f"{f:,.0f}".replace(",", " "), ha="center", fontsize=7)
        a.text(xi + w / 2, max(n, 0) + 200, f"{n:,.0f}\nMIRR {cs[k]['res']['MIRR']*100:.1f} %".replace(",", " ").replace(".", ","), ha="center", fontsize=7)
    SH = {"A · Referencia TRL-9": "A: referencia\nTRL-9", "A · Óptimo con la topología anterior": "A: óptimo\ntopología v5", "A · Óptimo con la superestructura ampliada": "A: óptimo\ncon vinagre", "A · Óptimo sin vinagre": "A: óptimo\nsin vinagre", "B · Óptimo con la topología anterior": "B: óptimo\ntopología v5", "B · Óptimo con la superestructura ampliada": "B: óptimo\nampliada"}
    a.set_xticks(x); a.set_xticklabels([SH.get(k, k) for k in keys], fontsize=7.5); a.legend(fontsize=7.5, loc="upper left")
    a.set_ylim(0, max(fci) * 1.18); a.set_title("Inversión y valor: tamaños de referencia frente a óptimos", fontsize=9)
    # (b) Monte Carlo
    b = ax[0, 1]
    for q, k in enumerate(keys):
        v = np.sort(np.array(cs[k]["mc"]["NPV"]) / 1e6)
        b.plot(v, np.linspace(0, 1, len(v)), color=C[q], lw=1.8, ls="-" if "ampliada" in k else "--",
               label=f"{k} · P(VPN>0) = {cs[k]['mc']['P_pos']:.2f}".replace(".", ","))
    b.axvline(0, color=INK2, lw=0.8); b.set_xlabel("VPN (MM COP)"); b.set_ylabel("Probabilidad acumulada"); b.legend(fontsize=6.8, loc="upper left")
    b.set_title("Monte Carlo LHS + Iman–Conover (1 000 corridas)", fontsize=9)
    # (c) tornado del mejor caso
    k = max(keys, key=lambda k: cs[k]["res"]["NPV"]); tor = cs[k]["tornado"]; base = cs[k]["res"]["NPV"] / 1e6
    c_ = ax[1, 0]
    for i, rr in enumerate(tor):
        lo, hi = rr["NPV_worst"] / 1e6, rr["NPV_best"] / 1e6
        c_.barh(i, hi - base, left=base, color=C[0]); c_.barh(i, lo - base, left=base, color=C[1])
    c_.axvline(base, color=INK, lw=1); c_.set_yticks(range(len(tor))); c_.set_yticklabels([rr["label"].replace("Precio del producto", "Precio del vino") for rr in tor], fontsize=8); c_.invert_yaxis()
    c_.set_xlabel("VPN (MM COP)"); c_.set_title(f"Tornado: {k} (azul = mejor, naranja = peor)", fontsize=9)
    # (d) escala
    sc = t["scale"]; d_ = ax[1, 1]
    s_ = [r["supply"] for r in sc]
    d_.plot(s_, [r["NPV"] / 1e6 for r in sc], "-o", color=C[0], label="VPN del óptimo (vino 3 000 COP/L)")
    d_.axhline(0, color=INK2, lw=0.8); d_.axvline(6146, color=GRID, ls="--"); d_.set_xlabel("Oferta de fruta (t/año)"); d_.set_ylabel("VPN (MM COP)")
    d2 = d_.twinx(); d2.plot(s_, [r["breakeven"] for r in sc], "-s", color=C[3], label="Precio de equilibrio del vino"); d2.grid(False)
    d2.axhline(1600, color=C[3], ls=":", lw=1); d2.text(s_[-1], 1640, "precio base del TEA (1 600)", ha="right", fontsize=7, color=C[3])
    d2.set_ylabel("Precio de equilibrio del vino (COP/L)", color=C[3])
    h1, l1 = d_.get_legend_handles_labels(); h2, l2 = d2.get_legend_handles_labels(); d_.legend(h1 + h2, l1 + l2, fontsize=7, loc="upper left")
    d_.set_title("TEA del diseño óptimo según la oferta", fontsize=9)
    fig.suptitle("Fig. 31  TEA de Burk recalculado con los tamaños óptimos (Chocó 2022 y regla por escala)", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig31_tea_dimensionado.png")


def fig32_vinagre():
    d = J("dimensionamiento.json"); t = J("tea_dimensionado.json")
    if not d:
        return
    ks = sorted([k for k in d if k.startswith("E6|") and d[k].get("scen")], key=lambda k: (float(k.split("|")[2]), float(k.split("|")[1])))
    if not ks:
        return
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.6), gridspec_kw=dict(width_ratios=[1.5, 1]))
    x = np.arange(len(ks)); labs = []
    sold, wv, pjv = [], [], []
    for k in ks:
        p_ = d[k]["scen"][0]["products"]; wp, vp = k.split("|")[1:]
        labs.append(f"vino {int(wp):,}\nvinagre {int(vp):,}".replace(",", " "))
        sold.append(p_["vino_m3"] - p_.get("vino_a_vinagre_m3", 0)); wv.append(p_.get("vino_a_vinagre_m3", 0) * 1.6)
        pjv.append(p_.get("jugo_cascara_vinagre_t", 0) * 55.7 / 50)
    a = ax[0]
    a.bar(x - 0.2, sold, 0.4, color=C[0], label="Vino vendido (m³/año)")
    a.bar(x + 0.2, wv, 0.4, color=C[3], label="Vinagre de vino (m³/año)")
    a.bar(x + 0.2, pjv, 0.4, bottom=wv, color=C[2], label="Vinagre de jugo de cáscara (m³/año)")
    for xi, k in zip(x, ks):
        a.text(xi, max(sold[list(x).index(xi)], wv[list(x).index(xi)] + pjv[list(x).index(xi)]) + 60, d[k]["sizes"].get("Acetificador", "no").replace("no", "sin acetif."), ha="center", fontsize=6.8, color=INK2)
    a.set_xticks(x); a.set_xticklabels(labs, fontsize=7); a.set_ylabel("m³/año"); a.legend(fontsize=7, loc="upper left")
    a.set_title("Qué hace el óptimo con el vino según los precios (vino: neto COP/L); arriba, el acetificador elegido", fontsize=9)
    b = ax[1]
    if t and t.get("prices"):
        P = t["prices"]
        for q, vp in enumerate(sorted({r["vinegar_price"] for r in P})):
            rr = sorted([r for r in P if r["vinegar_price"] == vp], key=lambda r: r["wine_price"])
            b.plot([r["wine_price"] for r in rr], [r["NPV"] / 1e6 for r in rr], "-o", color=C[q], label=f"Vinagre a {int(vp):,} COP/L".replace(",", " "))
        b.axhline(0, color=INK2, lw=0.8); b.set_xlabel("Vino: neto por litro tras impuesto, margen y empaque (COP/L)"); b.set_ylabel("VPN del diseño óptimo (MM COP)"); b.legend(fontsize=7.5)
        b.set_title("TEA de Burk del óptimo de cada par de precios", fontsize=9)
    fig.suptitle("Fig. 32  El vinagre como cobertura del precio del vino (Emde 2017; Bekatorou 2020)", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig32_vinagre_precios.png")


if __name__ == "__main__":
    fig31_tea()
    fig32_vinagre()
