"""Figuras 16-28 (versión 2: Moresi, capacidad, TRL-9, TEA Burk, MILP Grossmann, STN Maravelias)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from figuras import C, SEQ, INK, INK2, GRID, SURF, save, J
import params as p
import fig_en
import moresi as mo
import planificacion_milp as pm

plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})
MM = 1e6


def fig16_moresi_replica():
    d = J("moresi_R_P1.json")
    if not d:
        return
    R1 = d["R1"]
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.7))
    for q, (b, lab) in enumerate(((R1["calibrated"][0], "cerrado 15 °C"), (R1["calibrated"][1], "abierto 15–22 °C"))):
        ax[0].plot(b["t"], b["S"], color=C[q], label=f"Azúcar, {lab}")
        ax[0].plot(b["t"], b["E"], "--", color=C[q], label=f"Etanol, {lab}")
    ax[0].axhline(0.15 * 220, color=INK2, lw=0.8, ls=":")
    ax[0].annotate("85 % de consumo (criterio de Moresi, paso 2)", (5, 0.15 * 220 + 4), fontsize=7.5, color=INK2)
    ax[0].set_xlim(0, 130); ax[0].set_xlabel("Tiempo (h)"); ax[0].set_ylabel("g/L"); ax[0].legend(fontsize=7)
    ax[0].set_title("Mosto de uva, X₀ viable calibrado")
    b = R1["calibrated"][1]
    ax[1].plot(b["t"], b["T"], color=C[1]); ax[1].set_xlim(0, 100)
    ax[1].set_xlabel("Tiempo (h)"); ax[1].set_ylabel("T (°C)"); ax[1].set_title("Política abierta: 15 → 22 °C, enfriamiento 4 h")
    rows = d["R2"]
    items = [("dep_fab", "Depreciación\nfabricados"), ("dep_mach", "Depreciación\nmaquinaria"), ("maint", "Mantenimiento"),
             ("elec", "Electricidad"), ("inoc", "Inóculo"), ("man", "Mano de obra"), ("CI", "Inversión C_I")]
    x = np.arange(len(items)); w = 0.13
    for q, r in enumerate(rows):
        ref, mdl = r["ref"], r["model"]
        err = [(mdl[k] - ref[k]) / ref[k] * 100 for k, _ in items]
        ax[2].bar(x + (q - 1) * w * 1.2, err, w, color=C[q], label=f"{r['Qp']:,} hL".replace(",", " "))
    ax[2].axhline(0, color=INK2, lw=0.8)
    ax[2].set_xticks(x); ax[2].set_xticklabels([lab for _, lab in items], fontsize=7.2)
    ax[2].set_ylabel("Diferencia vs Tabla 3 (%)"); ax[2].legend(fontsize=7.5, title="Bodega")
    ax[2].set_title("Réplica del modelo de costos (pasos 4–10)")
    fig.suptitle(f"Fig. 16  Réplica de Moresi (1989a, b): cinética con un parámetro calibrado (X₀ = {R1['X0_eff']:.3f} g/L) y costos de su Tabla 3",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig16_moresi_replica.png")


def fig17_moresi_pina():
    d = J("moresi_R_P1.json"); d2 = J("moresi_P2_P3.json")
    if not d or not d2:
        return
    P1 = [r for r in d["P1"] if r["mode"] == "closed" and abs(r["X0"] - d["R1"]["X0_eff"]) < 1e-6]
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.7))
    T = [r["T0"] for r in P1]
    ax[0].plot(T, [r["t85"] for r in P1], "o-", color=C[0], label="85 % (criterio de Moresi)")
    ax[0].plot(T, [r["t975"] for r in P1], "s-", color=C[1], label="97,5 % (vino seco, ≤ 4 g/L)")
    ax[0].scatter([30], [12.5], marker="*", s=180, color=C[3], zorder=5, edgecolor=INK, label="Murcia Palacios (2013), 30 °C")
    TT = np.linspace(10, 32, 200); vm = [mo.params_T(t)[0] for t in TT]
    ax2 = ax[0].twinx(); ax2.plot(TT, vm, color=INK2, lw=1, ls="--"); ax2.set_ylabel("v_M de la Tabla 1 (1/h)", color=INK2)
    ax2.axhline(0, color=INK2, lw=0.6); ax2.grid(False)
    ax[0].set_xlabel("Temperatura de fermentación (°C)"); ax[0].set_ylabel("Tiempo de fermentación (h)")
    ax[0].set_ylim(0, 250); ax[0].legend(fontsize=7, loc="upper left"); ax[0].set_title("Piña (158,8 g/L), cinética de Moresi", fontsize=9.5)
    P3 = d2["P3"]
    labs = ["Ventaja total\nde etanol", "Por rendimiento\nestequiométrico", "Por conversión\nmás completa"]
    vals = [(P3["ratio"] - 1) * 100, (P3["ratio_from_yield"] - 1) * 100, (P3["ratio_from_conversion"] - 1) * 100]
    ax[1].bar(labs, vals, color=[C[0], C[1], C[2]], width=0.6)
    for q, v in enumerate(vals):
        ax[1].text(q, v + 0.4, f"+{v:.1f} %", ha="center", fontsize=9)
    ax[1].axhline(15.4, color=INK2, ls=":", lw=1); ax[1].annotate("tesis §4.2.5: +15,4 %", (1.3, 15.9), fontsize=8, color=INK2)
    ax[1].set_ylabel("Etanol/t azúcar: premium vs rápida (%)")
    ax[1].set_title("Origen de la ventaja premium", fontsize=9.5)
    rows = d2["P2"]
    for q, case in enumerate(sorted({r["case"] for r in rows})):
        for reg, ls in (("continuo_7500h", "-"), ("estacional_28d", "--")):
            rr = sorted([r for r in rows if r["case"] == case and r["regime"] == reg], key=lambda r: r["VF"])
            ax[2].plot([r["VF"] for r in rr], [r["Cv"] * 1000 for r in rr], ls, color=C[q], label=case if reg.startswith("cont") else None)
    ax[2].set_xlabel("Volumen de cada fermentador V_F (m³)"); ax[2].set_ylabel("Costo de fermentación (USD/m³ de vino)")
    ax[2].legend(fontsize=6.6, title="— continuo   - - estacional 28 d", title_fontsize=7)
    ax[2].set_title("Bodega de 78 300 hL/año (Moresi)", fontsize=9.5)
    fig.suptitle("Fig. 17  Moresi aplicado a la piña: validez térmica de la cinética, ventaja premium y diseño de la bodega",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig17_moresi_pina.png")


def fig18_capacidad():
    d = J("capacidad.json")
    if not d:
        return
    fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.9))
    req = d["C2"]
    labs = ["Rechazo\nQuibdó", "Chocó\n2008", "Chocó\n2022 (EVA)", "Base tesis\n(pulpa 55 %)", "Base tesis\n(pulpa 45 %)", "Base tesis\n(pulpa 25 %)"]
    vals = [144, 3883, 6146, req["pulpa alta 55 %"]["fruit_t"], req["central"]["fruit_t"], req["pulpa baja 25 % (75 % residuo)"]["fruit_t"]]
    cols = [C[2], C[2], C[2], C[1], C[1], C[1]]
    ax[0].bar(range(6), vals, color=cols, width=0.65); ax[0].set_yscale("log")
    for q, v in enumerate(vals):
        ax[0].text(q, v * 1.15, f"{v:,.0f}".replace(",", " "), ha="center", fontsize=7.5)
    ax[0].set_xticks(range(6)); ax[0].set_xticklabels(labs, fontsize=7.2); ax[0].set_ylabel("Fruta entera (t/año, escala log)")
    ax[0].legend(handles=[Patch(color=C[2], label="Oferta documentada"), Patch(color=C[1], label="Requerida por la tesis")], fontsize=7.5)
    ax[0].set_title("Oferta frente a requerimiento")
    cv = d["curve"]
    ax[1].fill_between(cv["fruit_t"], cv["wine_hL_lo"], cv["wine_hL_hi"], color=SEQ[1], alpha=0.8, label="pulpa 25–55 %")
    ax[1].plot(cv["fruit_t"], cv["wine_hL"], color=C[0], label="pulpa 45 %")
    ax[1].axhline(p.WINE_VOL_YR * 10, color=C[1], ls="--", lw=1.2); ax[1].annotate("78 300 hL/año (tesis)", (130, p.WINE_VOL_YR * 10 * 1.15), fontsize=7.5, color=C[1])
    for x_, lab in ((3883, "Chocó 2008"), (6146, "Chocó 2022")):
        ax[1].axvline(x_, color=INK2, ls=":", lw=1); ax[1].annotate(lab, (x_ * 1.05, 300), fontsize=7, color=INK2, rotation=90)
    ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlabel("Fruta disponible (t/año)"); ax[1].set_ylabel("Vino posible (hL/año)")
    ax[1].legend(fontsize=7.5, loc="lower right"); ax[1].set_title("Capacidad que soporta la oferta")
    b = d["C1_design"]
    labs2 = ["Calor de secado\n(harina)", "Calor del gasificador\n(TRL 8)", "Calor de caldera\nde corona (TRL 9)"]
    vals2 = [b["Q_dry_GJ"], b["Q_th_GJ"], b["crown_dm_t"] * 17.0 * 0.80]
    ax[2].bar(labs2, vals2, color=[C[1], C[0], C[2]], width=0.6)
    for q, v in enumerate(vals2):
        ax[2].text(q, v * 1.02, f"{v:,.0f} GJ".replace(",", " "), ha="center", fontsize=8)
    ax[2].set_ylabel("GJ/año"); ax[2].set_title("Cuello de botella energético (base de la tesis)")
    fig.suptitle("Fig. 18  Análisis de capacidad: la base de diseño exige 3,6 veces la producción del Chocó 2022 y más calor del que da el gasificador",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig18_capacidad.png")


def fig19_tea_lineas():
    d = J("tea_lineas.json")
    if not d:
        return
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    tags = list(d.keys())
    lines = [k for k in d[tags[0]]["tea"].keys() if not k.startswith("Planta")]
    y = np.arange(len(lines)); w = 0.27
    for q, t in enumerate(tags):
        v = [d[t]["tea"][k]["res"]["NPV"] / MM for k in lines]
        ax[0].barh(y + (q - 1) * w, v, w, color=C[q], label=t)
    ax[0].axvline(0, color=INK2, lw=0.8); ax[0].set_yticks(y); ax[0].set_yticklabels([k.split(" (")[0] for k in lines], fontsize=8)
    ax[0].invert_yaxis(); ax[0].set_xlabel("VPN a 10 años, 10 % real (MM COP)"); ax[0].legend(fontsize=7.5, loc="lower right")
    ax[0].set_title("VPN por línea y escala (TEA según Burk)")
    t0 = tags[0]
    rel = []
    for k in lines:
        r = d[t0]["tea"][k]
        price = r["case"]["product"]["price"]
        rel.append((k.split(" (")[0], r["res"]["LCOP"] / price, r["breakeven"] / price if r["breakeven"] == r["breakeven"] else np.nan))
    ax[1].barh(np.arange(len(rel)), [r[1] for r in rel], color=C[0], height=0.35, label="Costo nivelado / precio")
    ax[1].barh(np.arange(len(rel)) + 0.38, [r[2] for r in rel], color=C[1], height=0.35, label="Precio de equilibrio (VPN = 0) / precio")
    ax[1].axvline(1, color=INK2, ls="--", lw=1)
    ax[1].set_yticks(np.arange(len(rel)) + 0.19); ax[1].set_yticklabels([r[0] for r in rel], fontsize=8); ax[1].invert_yaxis()
    ax[1].set_xscale("log"); ax[1].set_xlabel("Relación con el precio de venta supuesto (escala log; < 1 es rentable)")
    ax[1].legend(fontsize=7.5); ax[1].set_title(f"Costo frente a precio — {t0}")
    fig.suptitle("Fig. 19  TEA por línea de producción (estructura de los TEA de asaí y coco; COP de 2026)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig19_tea_lineas.png")


def fig20_milp():
    sw = J("milp_barrido.json"); pl = J("milp_planes.json")
    if not sw:
        return
    fig, ax = plt.subplots(1, 3, figsize=(13, 4.0))
    for q, mode in enumerate(("fruta", "residuos")):
        wps = sorted({r["wp"] for r in sw if r["mode"] == mode}); sups = sorted({r["supply"] for r in sw})
        M = np.array([[next(r["obj"] for r in sw if r["mode"] == mode and r["wp"] == wp and r["supply"] == s) / MM for s in sups] for wp in wps])
        vmax = np.nanmax(np.abs(M))
        im = ax[q].imshow(M, aspect="auto", origin="lower", cmap="RdBu", vmin=-vmax, vmax=vmax)
        for i, wp in enumerate(wps):
            for j, s in enumerate(sups):
                r = next(r for r in sw if r["mode"] == mode and r["wp"] == wp and r["supply"] == s)
                code = "".join({"vino": "V", "vinagre": "A", "bromelaina": "B", "harina": "H", "etanol": "E", "caldera": "C", "gasificador": "G"}[l] for l in r["lines"])
                ax[q].text(j, i, code or "–", ha="center", va="center", fontsize=6.5, color=INK)
        ax[q].set_xticks(range(len(sups))); ax[q].set_xticklabels([f"{s/1000:.1f}".rstrip("0").rstrip(".") for s in sups], fontsize=7.5)
        ax[q].set_yticks(range(len(wps))); ax[q].set_yticklabels([f"{w:,.0f}".replace(",", " ") for w in wps])
        ax[q].set_xlabel("Oferta de fruta (miles de t/año)"); ax[q].set_ylabel("Precio del vino (COP/L)")
        ax[q].grid(False); ax[q].axvline(sups.index(6146) if 6146 in sups else 6, color=INK, lw=1, ls=":")
        fig.colorbar(im, ax=ax[q]).set_label("MM COP/año antes de impuestos", fontsize=8)
        ax[q].set_title("Fruta de rechazo comprada (400 COP/kg)" if mode == "fruta" else "Residuos de procesador (80 COP/kg)")
    so = next((s for s in (pl or []) if s["label"].startswith("Chocó 2022 completo") and "3 000" in s["label"]), None)
    if so:
        mth = np.arange(12)
        ax[2].bar(mth, so["supply_monthly"], color=SEQ[1], label="Oferta estacional", width=0.8)
        ax[2].bar(mth, so["fruit_monthly"], color=C[0], width=0.5, label="Fruta procesada")
        ax[2].set_xticks(mth); ax[2].set_xticklabels(fig_en.month_initials())
        ax[2].set_ylabel("t/mes"); ax[2].legend(fontsize=7.5); ax[2].set_title("Plan mensual óptimo, Chocó 2022 (V + H)")
    fig.suptitle("Fig. 20  MILP de síntesis y planificación (Grossmann): qué líneas construir según oferta, precio y régimen de abastecimiento",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig20_milp.png")


def fig21_stn():
    d = J("stn_semana.json")
    if not d:
        return
    r = d["Prensa compartida 2 t/h"]
    units = sorted({s["unit"] for s in r["schedule"]}, key=lambda u: ["Frente", "Prensa", "MF", "F1", "F2", "F3", "Secador"].index(u) if u in ["Frente", "Prensa", "MF", "F1", "F2", "F3", "Secador"] else 99)
    tasks = sorted({s["task"] for s in r["schedule"]})
    col = {t: C[q % 8] for q, t in enumerate(tasks)}
    fig, ax = plt.subplots(2, 1, figsize=(12, 5.4), gridspec_kw=dict(height_ratios=[1.3, 1]))
    for s in r["schedule"]:
        ax[0].barh(units.index(s["unit"]), s["dur"], left=s["start"], color=col[s["task"]], height=0.6, edgecolor=SURF, lw=0.5)
    for dd in range(7):
        ax[0].axvspan(dd * 24 + 22, dd * 24 + 30, color=GRID, alpha=0.5, lw=0)
    ax[0].set_yticks(range(len(units))); ax[0].set_yticklabels(units); ax[0].invert_yaxis(); ax[0].set_xlim(0, 144)
    ax[0].set_xticks(range(0, 145, 24)); ax[0].set_xticklabels(fig_en.days())
    ax[0].legend(handles=[Patch(color=col[t], label=t) for t in tasks], fontsize=7.2, ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    ax[0].grid(axis="y", visible=False)
    ax[0].set_title(f"Semana pico ({r['fruit_week']:.0f} t de fruta): una prensa compartida de 2 t/h basta (ocupación {r['util']['Prensa']*100:.0f} %)")
    inv = r["inventory"]; t = np.arange(len(inv["mosto"]))
    for q, k in enumerate(("mosto", "torta", "pulpa", "cascara")):
        ax[1].plot(t, inv[k], color=C[q], label=k)
    ax[1].set_xlim(0, 144); ax[1].set_xticks(range(0, 145, 24)); ax[1].set_xticklabels(fig_en.days())
    ax[1].set_ylabel("Inventario (t o m³)"); ax[1].legend(fontsize=7.5, ncol=4); ax[1].set_title("Inventarios intermedios (ec. 7.6, con límites χ_k)")
    fig.suptitle("Fig. 21  Programación semanal con la red estado-tarea en tiempo discreto (Maravelias, ecs. 7.4–7.6)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig21_stn.png")


def fig22_mc():
    d = J("tea_lineas.json")
    if not d:
        return
    t = list(d.keys())[0]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    keys = ["L5 Harina de fibra de cáscara", "L4 Bromelaína + polvo nutracéutico", "L3 Vinagre (acetador sumergido)", "Planta integrada TRL-9"]
    for q, k in enumerate(keys):
        v = np.array(d[t]["tea"][k]["mc"]["NPV"]) / MM
        ax.hist(v, bins=40, color=C[q], alpha=0.55, label=f"{k.split(' (')[0]} — P(VPN>0) = {np.mean(v > 0):.2f}")
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("VPN (MM COP)"); ax.set_ylabel("Iteraciones"); ax.legend(fontsize=7.5)
    ax.set_title(f"Fig. 22  Monte Carlo (hipercubo latino, Beta-PERT, Iman–Conover) — {t}", loc="left")
    save(fig, "fig22_montecarlo.png")


if __name__ == "__main__":
    for f in (fig16_moresi_replica, fig17_moresi_pina, fig18_capacidad, fig19_tea_lineas, fig20_milp, fig21_stn, fig22_mc):
        try:
            f()
        except Exception:
            import traceback; traceback.print_exc()
