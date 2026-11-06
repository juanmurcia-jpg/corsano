"""Figuras 23-26 (versión 3): estocástico (Grossmann cap. 14), programa anual en tiempo continuo y Gantt de
cuellos de botella (Maravelias)."""
import json, os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from figuras import C, SEQ, INK, INK2, GRID, SURF, save, J
import planta_trl9 as pt
import capacidad as cp
import params as p

MM = 1e6
import fig_en
MES = fig_en.months()


def fig23_estocastico():
    d = J("estocastico.json")
    if not d:
        return
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
    sc = d["scenarios"]; ps = np.array([s["p"] for s in sc])
    for q, (k, lab) in enumerate((("RP", "Solución estocástica (RP)"), ("EEV", "Solución de valor medio (EEV)"))):
        v = np.array(d[k]["Pi"]) / MM; o = np.argsort(v)
        ax[0].step(v[o], np.cumsum(ps[o]), where="post", color=C[q], label=lab, lw=2 - q * 0.6, ls="-" if q == 0 else "--")
    ax[0].axvline(0, color=INK2, lw=0.8)
    ax[0].set_xlabel("Beneficio anual antes de impuestos (MM COP)"); ax[0].set_ylabel("Probabilidad acumulada")
    ax[0].legend(fontsize=7.5); ax[0].set_title("Distribución sobre 27 escenarios")
    labs = ["EV (promete)", "RP = EEV", "WS", "EVPI", "VSS"]
    vals = [d["EV"]["E"], d["RP"]["E"], d["WS"], d["EVPI"], d["VSS"]]
    ax[1].bar(labs, np.array(vals) / MM, color=[C[3], C[0], C[2], C[1], C[6]], width=0.6)
    for q, v in enumerate(vals):
        ax[1].text(q, v / MM + 10, f"{v/MM:,.0f}".replace(",", " "), ha="center", fontsize=8.5)
    ax[1].set_ylabel("MM COP/año"); ax[1].set_title("Indicadores de Grossmann (cap. 14)")
    ax[1].tick_params(axis="x", labelsize=7.5, rotation=20)
    fr = d["frontier"]
    ax[2].plot([f["CVaR"] / MM for f in fr], [f["E"] / MM for f in fr], "o-", color=C[0])
    groups = {}
    for f in fr:
        lab = " + ".join(sorted(f["sel"])) or "no construir"
        groups.setdefault((round(f["CVaR"] / MM), round(f["E"] / MM), lab), []).append(f["lam"])
    for (cx, ey, lab), lams in groups.items():
        rng = f"λ ≤ {max(lams):g}" if min(lams) == 0 else f"λ ≥ {min(lams):g}"
        ax[2].annotate(f"{rng}: {lab}", (cx, ey), fontsize=8, color=INK, textcoords="offset points",
                       xytext=(8, -14) if ey > 0 else (-120, 12))
    ax[2].set_xlabel("CVaR al 90 % del beneficio (MM COP/año)"); ax[2].set_ylabel("Beneficio esperado (MM COP/año)")
    ax[2].set_title("Frontera media–riesgo (§6.7)")
    fig.suptitle("Fig. 23  Programación estocástica en dos etapas para el Chocó 2022 (oferta × precio del vino × precio de la harina)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig23_estocastico.png")


def fig24_25_anual():
    d = J("anual_continuo.json")
    if not d:
        return
    Kmax = max(int(k.split("K=")[1]) for k in d)
    key = next((k for k in d if k.startswith("B: vino + harina + bromelaína") and f"K={Kmax}" in k), list(d)[0])
    r = d[key]
    rows = r["periods"]
    units = list(r["units"])
    lanes = ["Frente", "Prensa · pulpa", "Prensa · cáscara"] + (["Prensa · corazón"] if "Aspersión" in units else []) + ["MF", "Bodega", "Secador"] + (["Aspersión"] if "Aspersión" in units else [])
    col = {"Prensa · pulpa": C[0], "Prensa · cáscara": C[1], "Prensa · corazón": C[4]}
    fig, ax = plt.subplots(figsize=(13, 4.6))
    U = r["units"]
    for rr in rows:
        s0, du = rr["start"] / 24, rr["dur"] / 24
        if du <= 1e-6:
            continue
        def frac(val, u):
            cap = U[u]["cap"] * U[u]["a"] * rr["dur"]
            return val / cap if cap > 0 else 0
        for lane, val, u in (("Frente", rr["fe"], "Frente"), ("MF", rr["mf"], "MF"), ("Bodega", rr["bod"], "Bodega"),
                             ("Secador", rr["sec"], "Secador"), ("Aspersión", rr.get("asp", 0), "Aspersión")):
            if lane not in lanes:
                continue
            f = min(frac(val, u), 1.0)
            ax.barh(lanes.index(lane), du, left=s0, color=plt.cm.Blues(0.2 + 0.75 * f), height=0.7, edgecolor=SURF, lw=0.3)
        for mode, lane in (("pulpa", "Prensa · pulpa"), ("cascara", "Prensa · cáscara"), ("corazon", "Prensa · corazón")):
            if mode in rr.get("tau", {}) and rr["dur"] > 0:
                f = min(rr["tau"][mode] / (U["Prensa"]["a"] * rr["dur"]), 1.0)
                if f > 1e-3:
                    ax.barh(lanes.index(lane), du, left=s0, color=col[lane], alpha=0.25 + 0.75 * f, height=0.7, edgecolor=SURF, lw=0.3)
    # ciclos (cambios de material) por mes
    for mo in range(12):
        n = sum(rr["W"] for rr in rows if rr["month"] == mo)
        cm = np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        ax.text(cm[mo] + 15, lanes.index("Prensa · pulpa") - 0.55, f"{n:.0f} cambios", ha="center", fontsize=6.5, color=INK2)
    if "Prensa · corazón" in lanes and "corazon" not in rows[0].get("tau", {}):
        lanes_present = True
    cum = np.cumsum([0] + [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    ax.set_xticks(cum[:-1] + 15); ax.set_xticklabels(MES); ax.set_xlim(0, 365)
    for c_ in cum:
        ax.axvline(c_, color=GRID, lw=0.8)
    ax.set_yticks(range(len(lanes))); ax.set_yticklabels(lanes); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    ax.set_title(f"Prensa compartida: tiempo por material (intensidad = fracción del periodo) · demás unidades: ocupación (azul) · "
                 f"{r['changeovers']:.0f} cambios de material/año", fontsize=9)
    sm = plt.cm.ScalarMappable(cmap="Blues", norm=matplotlib.colors.Normalize(0, 1)); fig.colorbar(sm, ax=ax, pad=0.01).set_label("Ocupación")
    fig.suptitle(f"Fig. 24  Gantt anual en tiempo continuo (Maravelias cap. 7.3 y 9): {key.split(' | ')[0]}",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig24_gantt_anual.png")
    # Fig 25: mapa de ocupación de todas las configuraciones
    cfgs = [k for k in d if f"K={max(int(x.split('K=')[1]) for x in d)}" in k] or list(d)
    fig, ax = plt.subplots(1, len(cfgs) + 1, figsize=(4.3 * (len(cfgs) + 1), 3.9),
                           gridspec_kw=dict(width_ratios=[1] * len(cfgs) + [0.9]))
    for q, k in enumerate(cfgs):
        rr = d[k]; us = list(rr["util"]); M = np.array([rr["util"][u] for u in us])
        im = ax[q].imshow(M, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
        for i in range(M.shape[0]):
            for j in range(12):
                ax[q].text(j, i, f"{M[i, j]*100:.0f}", ha="center", va="center", fontsize=6.3,
                           color="white" if M[i, j] > 0.7 else INK, fontweight="bold" if M[i, j] >= 0.95 else None)
        ax[q].set_yticks(range(len(us))); ax[q].set_yticklabels(us, fontsize=8); ax[q].set_xticks(range(12)); ax[q].set_xticklabels(MES, fontsize=7)
        ax[q].grid(False); ax[q].set_title(k.split(" | ")[0].replace(", prensa compartida", "\nprensa"), fontsize=8.5)
    fig.colorbar(im, ax=ax[len(cfgs) - 1], fraction=0.04).set_label("Ocupación (%)")
    axl = ax[-1]
    for q, k in enumerate(cfgs):
        axl.bar(np.arange(12) + (q - 1) * 0.27, d[k]["loss_month"], 0.27, color=C[q], label=k.split(":")[0])
    axl.set_xticks(range(12)); axl.set_xticklabels(MES, fontsize=7); axl.set_ylabel("Fruta no procesada (t/mes)")
    axl.legend(fontsize=7, title="Configuración"); axl.set_title("Pérdida por capacidad", fontsize=9)
    fig.suptitle("Fig. 25  Cuellos de botella a lo largo del año: ocupación por unidad y mes (≥ 95 % en negrita) y fruta perdida",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig25_ocupacion_anual.png")


def fig26_bodega():
    fig, ax = plt.subplots(2, 1, figsize=(12.5, 5.6))
    for q, (scale, lab) in enumerate(((6200.0, "Chocó 2022 (6 200 t/año)"), (cp.fruit_for_wine(p.WINE_VOL_YR)[0], "Base de la tesis (21 856 t/año)"))):
        D = pt.design(scale); L = D["lines"]["vino"]
        f = next(e for e in L["equipment"] if "Fermentador" in e["name"])
        Q = L["flows"]["juice_m3"] / D["H_cont"]
        fill = max(1.5, f["size"] / Q); ferm = 12.5; empty, clean = 1.5, 1.0
        dtc = fill + ferm + empty + clean
        lag = f["size"] / Q
        H = 96
        for k in range(-int(dtc / lag) - 2, int(H / lag) + 2):
            j = k % f["qty"]; s = k * lag
            for ph, dur, cc in (("Llenado", fill, C[3]), ("Fermentación", ferm, C[0]), ("Vaciado", empty, C[2]), ("Limpieza", clean, C[6])):
                if s + dur > 0 and s < H:
                    ax[q].barh(j, dur, left=s, color=cc, height=0.6, edgecolor=SURF, lw=0.5)
                s += dur
        occ = Q * dtc / (f["qty"] * f["size"])
        ax[q].set_xlim(0, H); ax[q].set_yticks(range(f["qty"])); ax[q].set_yticklabels([f"F{j+1}" for j in range(f["qty"])])
        ax[q].invert_yaxis(); ax[q].grid(axis="y", visible=False); ax[q].set_xlabel("Horas")
        ax[q].set_title(f"{lab}: {f['qty']} × {f['size']:.0f} m³, mosto {Q:.2f} m³/h, llenado {fill:.1f} h, "
                        f"ciclo {dtc:.1f} h, ocupación {occ*100:.0f} %", fontsize=9)
    ax[0].legend(handles=[Patch(color=C[3], label="Llenado (exposición al aire)"), Patch(color=C[0], label="Fermentación 12,5 h"),
                          Patch(color=C[2], label="Vaciado"), Patch(color=C[6], label="Limpieza")], fontsize=7.5, ncol=4, loc="upper right")
    fig.suptitle("Fig. 26  Gantt de la bodega (procedimiento de Moresi con llenado V_F/Q_M): el llenado domina el ciclo a caudal bajo",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig26_gantt_bodega.png")


if __name__ == "__main__":
    for f in (fig23_estocastico, fig24_25_anual, fig26_bodega):
        try:
            f()
        except Exception:
            import traceback; traceback.print_exc()
