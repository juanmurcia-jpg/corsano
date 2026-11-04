"""Genera todas las figuras (PNG, 200 dpi) a partir de results/*.json."""
import json, os, ast
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import params as p
import kinetics as kn

R = os.path.join(os.path.dirname(__file__), "results")
F = os.path.join(os.path.dirname(__file__), "figs")
os.makedirs(F, exist_ok=True)

# paleta de referencia (skill dataviz, modo claro) -------------------------------------------
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 9.5, "axes.titlesize": 10.5,
    "axes.titleweight": "bold", "legend.frameon": False, "lines.linewidth": 2.0, "font.family": "DejaVu Sans",
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(F, name), dpi=200)
    plt.close(fig)
    print("fig", name)


def J(name):
    path = os.path.join(R, name)
    return json.load(open(path)) if os.path.exists(path) else None


def ferm_label(active, op="ferm"):
    alts = sorted({a for (o, a, st, M, V, T) in active if o == op})
    if not alts:
        return "sin propagación" if op == "prop" else "—"
    out = []
    for a in alts:
        t = ast.literal_eval(a)
        if len(t) == 1:
            out.append("1 unidad" if t[0] == 1 else f"{t[0]} en paralelo")
        elif all(x == 1 for x in t):
            out.append(f"{len(t)} en serie")
        else:
            out.append("×".join(str(x) for x in t) + " serie-paralelo")
    return " + ".join(out)


def nferm(active):
    return int(sum(M for (o, a, st, M, V, T) in active if o == "ferm"))


# ============================================================================== MODELO 1
def fig_m1_kinetics():
    d = J("m1_E1E2.json")
    if not d:
        return
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
    t = np.array(d["lsoda"]["t"])
    for k, (var, lab) in enumerate((("X", "Biomasa X (g/L)"), ("S", "Azúcar S (g/L)"), ("P", "Etanol P (g/L)"))):
        ax[k].plot(t, d["lsoda"][var], color=INK, lw=2.4, label="LSODA (referencia)")
        for q, N in enumerate(("3", "5", "15")):
            tr = d["trap"][N]
            ax[k].plot(tr["t"], tr[var], "o--", ms=4.5, lw=1.2, color=C[q], label=f"Trapecios, {N} nodos")
        ax[k].set_xlabel("Tiempo (h)"); ax[k].set_ylabel(lab)
    ax[2].axhline(p.P_REF, color=INK2, lw=0.8, ls=":")
    ax[2].annotate(f"Murcia Palacios (2013): {p.P_REF} g/L a 12,5 h", (0.3, p.P_REF + 1.5), color=INK2, fontsize=8)
    ax[0].legend(fontsize=7.5, loc="upper left")
    fig.suptitle("Fig. 1  Cinética alcohólica calibrada y discretización trapezoidal (análogo a la Fig. 2 de Corsano et al., 2004)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig01_cinetica_discretizacion.png")
    # error en el punto final
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    Ns = [int(n) for n in d["trap"]]
    eP = [abs(d["trap"][str(n)]["P"][-1] - d["lsoda"]["P"][-1]) for n in Ns]
    eS = [abs(d["trap"][str(n)]["S"][-1] - d["lsoda"]["S"][-1]) for n in Ns]
    ax.loglog(Ns, eP, "o-", color=C[0], label="|ΔP| final (g/L)")
    ax.loglog(Ns, eS, "s-", color=C[1], label="|ΔS| final (g/L)")
    ax.set_xlabel("Número de nodos N"); ax.set_ylabel("Error absoluto en t = T")
    ax.set_title("Error de la discretización en el punto final"); ax.legend()
    save(fig, "fig02_error_discretizacion.png")


def fig_m1_ident():
    d = J("m1_E1E2.json")
    if not d:
        return
    I = d["ident"]
    mu, X0, S = np.array(I["mu"]), np.array(I["X0"]), np.array(I["S"])
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
    cs = ax[0].contourf(mu, X0, np.log10(np.maximum(S, 1e-3)), levels=20, cmap=matplotlib.colors.ListedColormap(SEQ[::-1]))
    ax[0].contour(mu, X0, S, levels=[2.0], colors=[C[1]], linewidths=2.2)
    ax[0].set_yscale("log"); ax[0].set_xlabel("µmax (1/h)"); ax[0].set_ylabel("X0 del ensayo (g/L)")
    cb = fig.colorbar(cs, ax=ax[0]); cb.set_label("log10 S(12,5 h) (g/L)")
    cur = np.array(I["curve"])
    ax[0].plot(cur[:, 1], cur[:, 0], "o", color=INK, ms=3.5)
    ax[0].plot(kn.KIN_WINE["mu_max"], p.X0_REF, "*", color=C[1], ms=14, mec=INK)
    ax[0].set_title("Curva de pares (µmax, X0) que reproducen el ensayo")
    dt = np.array(I["design_time_at_X0_2"])
    ax[1].plot(dt[:, 0], dt[:, 2], "o-", color=C[0])
    ax[1].set_xscale("log"); ax[1].set_xlabel("X0 supuesto para el ensayo de referencia (g/L)")
    ax[1].set_ylabel("Tiempo para S ≤ 4 g/L con X0 = 2 g/L (h)")
    ax[1].axvline(p.X0_REF, color=INK2, ls=":", lw=1)
    ax[1].set_title("Consecuencia de diseño de la no identificabilidad")
    fig.suptitle("Fig. 3  Identificabilidad práctica: un solo punto final no determina µmax y X0 por separado",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig03_identificabilidad.png")


def gantt_m1(best, ax, ncyc=4):
    TL = best["TL"]
    act = [u for u in best["units"] if u["V"] > 1e-2]
    rows = []
    for u in act:
        lab = ("Propagador" if u["op"] == "prop" else "Fermentador") + f" {u['stage']}"
        for m in range(int(u["M"])):
            rows.append((u, m, lab + (f".{m + 1}" if u["M"] > 1 else "")))
    order = {id(u): k for k, u in enumerate(act)}
    for r_, (u, m, lab) in enumerate(rows):
        # inicio del lote en la unidad: suma de tiempos de las unidades previas de la ruta
        prev = [w for w in act if order[id(w)] < order[id(u)]]
        off = sum(w["T"] for w in prev)
        for k in range(-3, ncyc + 3):
            if k % int(u["M"]) != m:
                continue
            s = k * TL + off
            if s > ncyc * TL or s + u["T"] < 0:
                continue
            ax.barh(r_, u["T"], left=s, color=C[(k % 8)], height=0.6, edgecolor=SURF, lw=1.2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[2] for r in rows]); ax.invert_yaxis()
    ax.set_xlim(0, ncyc * TL + sum(u["T"] for u in act) * 0.2); ax.set_xlabel("Tiempo (h)")
    ax.grid(axis="y", visible=False)


def fig_m1_base():
    d = J("m1_E3.json")
    if not d:
        return
    best = d["best"]
    fig = plt.figure(figsize=(11, 6.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05])
    ax0 = fig.add_subplot(gs[0, :])
    gantt_m1(best, ax0)
    ax0.set_title(f"Diagrama de Gantt del óptimo (ZW, TL = {best['TL']:.2f} h; colores = lotes sucesivos)")
    act = [u for u in best["units"] if u["V"] > 1e-2]
    t0 = 0
    axs = [fig.add_subplot(gs[1, k]) for k in range(3)]
    for q, u in enumerate(act):
        tt = np.linspace(0, u["T"], len(u["X"])) + t0
        nm = ("Prop." if u["op"] == "prop" else "Ferm.") + f" {u['stage']} ({u['V']:.2f} m³)"
        axs[0].plot(tt, u["X"], "o-", ms=3, color=C[q], label=nm)
        axs[1].plot(tt, u["S"], "o-", ms=3, color=C[q])
        if "P" in u:
            axs[2].plot(tt, u["P"], "o-", ms=3, color=C[q])
        t0 += u["T"]
    for a, lab in zip(axs, ("X (g/L)", "S (g/L)", "P etanol (g/L)")):
        a.set_xlabel("Tiempo acumulado del lote (h)"); a.set_ylabel(lab)
    axs[0].legend(fontsize=7.5)
    fig.suptitle(f"Fig. 4  Modelo 1, óptimo base: propagación {ferm_label(best['active'], 'prop')} → fermentación "
                 f"{ferm_label(best['active'])}; TAC = {best['TAC'] / 1e3:,.1f} k USD/año",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig04_m1_optimo_base.png")
    # multiarranque
    allr = [r for r in d["all"] if r["ok"]]
    fl = lambda r: ferm_label(r["active"])
    noprop = lambda r: ferm_label(r["active"], "prop") == "sin propagación"
    labs = sorted({fl(r) for r in allr})
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    vals = sorted(allr, key=lambda r: r["TAC"])
    for k, r in enumerate(vals):
        ax.bar(k, r["TAC"] / 1e3, color=C[labs.index(fl(r)) % 8], width=0.75,
               hatch="///" if noprop(r) else None, edgecolor=SURF if not noprop(r) else INK2, lw=0.6)
    ax.set_ylim(min(r["TAC"] for r in vals) / 1e3 * 0.97, max(r["TAC"] for r in vals) / 1e3 * 1.01)
    ax.set_xlabel("Arranques ordenados por TAC"); ax.set_ylabel("TAC óptimo local (k USD/año)")
    hand = [Patch(color=C[labs.index(l) % 8], label="Ferm. " + l) for l in labs]
    hand.append(Patch(facecolor=SURF, edgecolor=INK2, hatch="///", label="sin propagación (inóculo directo)"))
    ax.legend(handles=hand, fontsize=7.2, loc="upper left", ncol=2)
    nst = len({r["label"] for r in allr})
    ax.set_title(f"Fig. 5  Multiarranque: {nst} estructuras localmente óptimas en {len(d['all'])} arranques", loc="left")
    save(fig, "fig05_m1_multiarranque.png")


def fig_m1_tau():
    d = J("m1_E4.json")
    if not d:
        return
    tau = [r["tau"] for r in d]
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.6))
    cap = np.array([r["capex_ann"] for r in d]) / 1e3; op = np.array([r["opex"] for r in d]) / 1e3
    x = np.arange(len(tau))
    ax[0].bar(x, cap, color=C[0], width=0.7, label="Capital anualizado", edgecolor=SURF)
    ax[0].bar(x, op, bottom=cap, color=C[1], width=0.7, label="Operación", edgecolor=SURF)
    for k, r in enumerate(d):
        ax[0].text(k, (cap[k] + op[k]) + 4, f"{(r['TAC'] / d[0]['TAC'] - 1) * 100:+.1f}%", ha="center", fontsize=7.5, color=INK2)
    ax[0].set_xticks(x); ax[0].set_xticklabels([f"{t:g}" for t in tau])
    ax[0].set_xlabel("Tiempo máximo de llenado τ (h)"); ax[0].set_ylabel("TAC (k USD/año)")
    ax[0].set_ylim(0, max(cap + op) * 1.25); ax[0].legend(loc="upper left", ncol=2, fontsize=8)
    ax[0].set_title("Costo de proteger el mosto contra la oxidación")
    nf = [nferm(r["active"]) for r in d]
    ax[1].step(tau, nf, where="post", color=C[2])
    ax[1].plot(tau, nf, "o", color=C[2], ms=6)
    last = None
    for t_, n_, r in zip(tau, nf, d):
        lab = ferm_label(r["active"])
        if lab != last:
            ax[1].annotate(lab, (t_, n_), textcoords="offset points", xytext=(-4, 7), fontsize=7.5, color=INK2, ha="right")
        last = lab
    ax[1].invert_xaxis(); ax[1].set_xlabel("τ (h)"); ax[1].set_ylabel("Fermentadores instalados")
    ax[1].set_title("Estructura óptima (emerge sin binarias)")
    fig.suptitle("Fig. 6  Restricción de tiempo de llenado (tesis §4.2.4) dentro de la superestructura NLP",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig06_m1_llenado_oxidacion.png")


def fig_m1_bmap():
    d = J("m1_E5b.json") or J("m1_E5.json")
    if not d:
        return
    bs = sorted({r["b"] for r in d}); scs = sorted({r["scale"] for r in d})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.0))
    labs = sorted({ferm_label(r["active"]) for r in d if r.get("ok")})
    M = np.full((len(scs), len(bs)), np.nan)
    for r in d:
        if r.get("ok"):
            M[scs.index(r["scale"]), bs.index(r["b"])] = labs.index(ferm_label(r["active"]))
    cmap = matplotlib.colors.ListedColormap(C[:max(len(labs), 1)])
    ax[0].imshow(M, cmap=cmap, aspect="auto", origin="lower", vmin=-0.5, vmax=len(labs) - 0.5)
    for r in d:
        if r.get("ok"):
            i, j = scs.index(r["scale"]), bs.index(r["b"])
            ax[0].text(j, i, str(nferm(r["active"])), ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    ax[0].set_xticks(range(len(bs))); ax[0].set_xticklabels([f"{b:g}" for b in bs])
    ax[0].set_yticks(range(len(scs))); ax[0].set_yticklabels([f"{s:g}×" for s in scs])
    ax[0].set_xlabel("Exponente de costo b"); ax[0].set_ylabel("Escala de producción (× 78 300 hL/año)")
    ax[0].grid(False)
    ax[0].legend(handles=[Patch(color=C[k], label=l) for k, l in enumerate(labs)], fontsize=7, loc="upper left",
                 bbox_to_anchor=(0, -0.18), ncol=2)
    ax[0].set_title("Estructura de fermentación óptima (número = fermentadores)")
    for q, sc in enumerate(scs):
        rr = sorted([r for r in d if r["scale"] == sc and r.get("ok")], key=lambda r: r["b"])
        ax[1].plot([r["b"] for r in rr], [r["TAC"] / 1e3 / sc for r in rr], "o-", color=C[q], label=f"{sc:g}×")
    ax[1].set_xlabel("Exponente de costo b"); ax[1].set_ylabel("TAC / escala (k USD/año)")
    ax[1].legend(title="Escala"); ax[1].set_title("Economía de escala")
    fig.suptitle("Fig. 7  Mapa de estructuras vs exponente de costo y escala, tras pulido por estructura (cf. ej. 3 de Corsano 2006a)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig07_m1_mapa_b_escala.png")


def fig_m1_hier():
    d = J("m1_E6.json")
    if not d:
        return
    taus = list(d.keys())
    names = [("jerarquico", "Jerárquico (cadena actual de la tesis)"), ("intermedio", "Intermedio (T₂ fijo, inóculo libre)"),
             ("simultaneo", "Simultáneo (Corsano)")]
    fig, ax = plt.subplots(figsize=(8.8, 3.8))
    w = 0.26
    for q, (k, lab) in enumerate(names):
        vals = [d[t][k]["TAC"] / 1e3 if d[t][k].get("ok") else np.nan for t in taus]
        ax.bar(np.arange(len(taus)) + (q - 1) * w, vals, width=w - 0.02, color=C[q], label=lab)
    for i, t in enumerate(taus):
        h, s = d[t]["jerarquico"]["TAC"], d[t]["simultaneo"]["TAC"]
        ax.text(i + w, s / 1e3 + 8, f"−{(1 - s / h) * 100:.1f}%", ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(len(taus))); ax.set_xticklabels([f"τ = {float(t):g} h" for t in taus])
    ax.set_ylabel("TAC (k USD/año)"); ax.legend(fontsize=8)
    ax.set_title("Fig. 8  Valor de la optimización simultánea frente a la jerárquica (§6.10 de la tesis)")
    save(fig, "fig08_m1_jerarquico_vs_simultaneo.png")


def fig_m1_sobol():
    d = J("m1_E8.json")
    if not d:
        return
    names = {"mu_max": "µmax", "Pmax": "Pmax", "Yps": "Y_P/S", "c_juice": "Costo jugo", "c_ady": "Costo LSA",
             "A_rel": "Coef. costo A", "b": "Exponente b", "c_elec": "Electricidad ZNI"}
    nm = [names[n] for n in d["problem"]["names"]]
    S1, ST = np.array(d["S1"]), np.array(d["ST"]); e1, eT = np.array(d["S1_conf"]), np.array(d["ST_conf"])
    o = np.argsort(ST)
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    y = np.arange(len(nm))
    ax[0].barh(y - 0.18, S1[o], 0.34, xerr=e1[o], color=C[0], label="S1 (primer orden)", ecolor=INK2)
    ax[0].barh(y + 0.18, ST[o], 0.34, xerr=eT[o], color=C[1], label="ST (total)", ecolor=INK2)
    ax[0].set_yticks(y); ax[0].set_yticklabels([nm[i] for i in o]); ax[0].legend(loc="lower right")
    ax[0].set_xlabel("Índice de Sobol"); ax[0].set_title("Sensibilidad global del TAC óptimo")
    X = np.array(d["X"]); Y = np.array([r["TAC"] for r in d["Y"]])
    k = int(np.argmax(ST))
    nf = np.array([r.get("nferm", np.nan) for r in d["Y"]])
    sc = ax[1].scatter(X[:, k], Y / 1e3, c=nf, s=9, cmap=matplotlib.colors.ListedColormap(SEQ[1:]), alpha=0.85)
    cb = fig.colorbar(sc, ax=ax[1]); cb.set_label("Fermentadores en el óptimo")
    ax[1].set_xlabel(nm[k]); ax[1].set_ylabel("TAC (k USD/año)"); ax[1].set_title(f"TAC vs el factor dominante ({nm[k]})")
    fig.suptitle(f"Fig. 9  Análisis de Sobol (Saltelli, {len(Y)} reoptimizaciones; {d['n_fail']} sin convergencia)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig09_m1_sobol.png")


# ============================================================================== MODELO 2
def fig_m2():
    d = J("m2_all.json")
    if not d:
        return
    F2 = sorted([r for r in d["F2"] if r.get("ok")], key=lambda r: r["tag"])
    f = [r["tag"] for r in F2]
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.5))
    ax[0].plot(f, [r["recycle_frac"] * 100 for r in F2], "o-", color=C[0])
    ax[0].set_xlabel("Factor de concentración del hub f"); ax[0].set_ylabel("Vinaza reciclada (%)")
    ax[0].set_title("Reciclo óptimo de vinaza")
    ax[1].plot(f, [r["VRes_yr"] for r in F2], "o-", color=C[1], label="Vinaza descargada")
    ax[1].plot(f, [r["water_yr"] for r in F2], "s-", color=C[2], label="Agua fresca de dilución")
    ax[1].set_xlabel("f"); ax[1].set_ylabel("m³/año"); ax[1].legend(); ax[1].set_title("Balance hídrico")
    cap = np.array([r["capex_ann"] for r in F2]) / 1e3; op = np.array([r["opex"] for r in F2]) / 1e3
    pen = np.array([r["penalty"] for r in F2]) / 1e3
    ax[2].bar(range(len(f)), cap, color=C[0], label="Capital", edgecolor=SURF)
    ax[2].bar(range(len(f)), op, bottom=cap, color=C[1], label="Operación", edgecolor=SURF)
    ax[2].bar(range(len(f)), pen, bottom=cap + op, color=C[7], label="Penalización vinaza (ec. 38)", edgecolor=SURF)
    ax[2].set_xticks(range(len(f))); ax[2].set_xticklabels([f"{x:g}" for x in f]); ax[2].set_xlabel("f")
    ax[2].set_ylabel("TAC (k USD/año)"); ax[2].legend(fontsize=7.5); ax[2].set_title("Composición del TAC")
    fig.suptitle("Fig. 10  Modelo 2: el reciclo de Corsano (2006b) sólo es óptimo si el hub entrega azúcar concentrado",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig10_m2_concentracion_hub.png")

    # F3: TAC vs Sw
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.6))
    for q, fv in enumerate((1.0, 3.0)):
        rr = sorted([r for r in d["F3"] if r.get("ok") and r["tag"][0] == fv], key=lambda r: r["tag"][1])
        ax[0].plot([r["tag"][1] for r in rr], [r["TAC"] / 1e3 for r in rr], "o-", color=C[q], label=f"f = {fv:g}")
        ax[1].plot([r["tag"][1] for r in rr], [r["recycle_frac"] * 100 for r in rr], "o-", color=C[q], label=f"f = {fv:g}")
    ax[0].set_xlabel("Azúcar residual en la vinaza S_W (g/L)"); ax[0].set_ylabel("TAC (k USD/año)"); ax[0].legend()
    ax[0].set_title("TAC vs S_W (análogo a la Fig. 3 de Corsano 2006b)")
    ax[1].set_xlabel("S_W (g/L)"); ax[1].set_ylabel("Vinaza reciclada (%)"); ax[1].legend(); ax[1].set_title("Reciclo asociado")
    fig.suptitle("Fig. 11  Compromiso tiempo de fermentación – recuperación de azúcar por reciclo",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig11_m2_Sw.png")

    # F4 Pareto
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for q, fv in enumerate((1.0, 3.0)):
        rr = sorted([r for r in d["F4"] if r.get("ok") and r["tag"][0] == fv], key=lambda r: r["VRes_yr"])
        ax.plot([r["VRes_yr"] for r in rr], [r["TAC"] / 1e3 for r in rr], "o-", color=C[q], label=f"f = {fv:g}")
    ax.set_xlabel("Vinaza descargada (m³/año)"); ax.set_ylabel("TAC sin penalización (k USD/año)")
    ax.legend(); ax.set_title("Fig. 12  Frontera de Pareto costo – descarga (ε-restricción)")
    save(fig, "fig12_m2_pareto.png")

    # F5 asignación del hub bajo escasez
    rr = [r for r in d["F5"] if r.get("ok")]
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    r0 = sorted([r for r in rr if r["tag"][0] == 0.0], key=lambda r: r["tag"][1])
    prs = [r["tag"][1] for r in r0]
    bottom = np.zeros(len(r0))
    names = dict(peel="Jugo de cáscara (110 g/L)", perm="Permeado UF (80 g/L)", hydro="Hidrolizado (60 g/L)")
    for q, k in enumerate(("peel", "perm", "hydro")):
        v = np.array([r["use_yr"][k] * p.HUB[k]["S"] / 1000 for r in r0])
        ax[0].bar(range(len(prs)), v, bottom=bottom, color=C[q], label=names[k], edgecolor=SURF, width=0.7)
        bottom += v
    ax[0].set_xticks(range(len(prs))); ax[0].set_xticklabels([f"{x:g}" for x in prs])
    ax[0].set_xlabel("Producción de etanol exigida (kg/h)"); ax[0].set_ylabel("Azúcar fermentado (t/año)")
    ax[0].legend(fontsize=8); ax[0].set_title("Orden de mérito del hub (α = 0)")
    for q, a_ in enumerate(sorted({r["tag"][0] for r in rr})):
        s_ = sorted([r for r in rr if r["tag"][0] == a_], key=lambda r: r["tag"][1])
        x = np.array([r["tag"][1] for r in s_]); y = np.array([r["TAC"] for r in s_])
        mc = np.diff(y) / (np.diff(x) * p.H)
        ax[1].step(x[1:], mc, where="pre", color=C[q], label=f"α = {a_:g}")
        ax[1].plot((x[1:] + x[:-1]) / 2, mc, "o", color=C[q], ms=5)
    ax[1].axhline(p.PRICE["ethanol"], color=INK2, ls=":", lw=1)
    ax[1].annotate(f"precio supuesto {p.PRICE['ethanol']} USD/kg", (45, p.PRICE["ethanol"] + 0.03), fontsize=8, color=INK2)
    ax[1].set_xlabel("Producción de etanol exigida (kg/h)"); ax[1].set_ylabel("Costo marginal (USD/kg etanol)")
    ax[1].set_ylim(0.8, 1.7); ax[1].legend(fontsize=8); ax[1].set_title("Costo marginal del etanol del hub")
    fig.suptitle("Fig. 13  Asignación del hub bajo escasez: el orden lo fija la concentración, no el costo por kg de azúcar",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig13_m2_asignacion_hub.png")


# ============================================================================== MODELOS 3-4
def gantt_campaign(r, ax, title, ncyc=2):
    P = r["prod"]
    tau = {"A": [P["A"]["Tp"], P["A"]["T"], P["A"]["th"]], "B": [P["B"]["Tp"], P["B"]["T"], P["B"]["th"], r["td"]]}
    stages = ["Propagador", "Fermentador", "Centrífuga", "Destilación"]
    if r["campaign"] in ("SPC-relajado", "MC"):
        seq = ["A"] * 3 + ["B"] * 3
    else:
        seq = list(r["campaign"]) * ncyc
    def dly(i, k):
        si = np.concatenate([[0], np.cumsum(tau[i])]); sk = np.concatenate([[0], np.cumsum(tau[k])])
        js = [0, 1, 2] + ([3] if i == k == "B" else [])
        return max(si[j] + tau[i][j] - sk[j] for j in js)
    t = 0
    for q, i in enumerate(seq):
        s = t
        for j, tj in enumerate(tau[i]):
            ax.barh(j, tj, left=s, color=C[0] if i == "A" else C[1], height=0.6, edgecolor=SURF, lw=1.2)
            ax.text(s + tj / 2, j, i, ha="center", va="center", color="white", fontsize=7)
            s += tj
        if q < len(seq) - 1:
            t += dly(i, seq[q + 1])
    ax.set_yticks(range(4)); ax.set_yticklabels(stages); ax.invert_yaxis(); ax.set_xlabel("Tiempo (h)")
    ax.grid(axis="y", visible=False); ax.set_title(title)


def fig_m34():
    d = J("m34_all.json")
    if not d:
        return
    G1 = d["G1"]
    rs = [r for r in G1["results"] if r.get("ok")]
    rs.sort(key=lambda r: -r["profit"])
    fig = plt.figure(figsize=(11, 6.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.4])
    ax = fig.add_subplot(gs[:, 0])
    labs = [r["campaign"] for r in rs] + ["SPC"]
    vals = [r["profit"] / 1e6 for r in rs] + [G1["spc"]["profit"] / 1e6]
    cols = [C[0]] * len(rs) + [C[1]]
    ax.barh(range(len(labs)), vals, color=cols, height=0.7)
    ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs, fontsize=8); ax.invert_yaxis()
    ax.set_xlim(min(vals) * 0.995, max(vals) * 1.002); ax.set_xlabel("Beneficio neto anual (M USD)")
    ax.set_title(f"Campañas candidatas (razón N_A/N_B del SPC = {G1['ratio']:.2f})")
    gantt_campaign(G1["spc"], fig.add_subplot(gs[0, 1]), "Campañas de un solo producto (SPC)")
    gantt_campaign(rs[0], fig.add_subplot(gs[1, 1]), f"Mejor campaña mixta: {rs[0]['campaign']}")
    fig.suptitle("Fig. 14  Modelo 3: heurística de campañas mixtas de Corsano et al. (2007) — A vino, B bioetanol",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig14_m3_campanas.png")

    # G2 desglose
    G2 = d["G2"]
    mc, mp = G2["MC"], G2["MP"]
    cats = [("Capital anualizado", lambda r: r["capex_ann"]), ("Materias primas", lambda r: r["raw"]),
            ("Energía (gasificador + respaldo)", lambda r: r["energy_cost"]), ("Mano de obra", lambda r: r["labor_cost"])]
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
    for q, (lab, fn) in enumerate(cats):
        bottom_mc = sum(f(mc) for _, f in cats[:q]); bottom_mp = sum(f(mp) for _, f in cats[:q])
        ax[0].bar([0, 1], [fn(mc) / 1e3, fn(mp) / 1e3], bottom=[bottom_mc / 1e3, bottom_mp / 1e3], color=C[q], label=lab,
                  width=0.55, edgecolor=SURF)
    ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(["Complejo multiplanta (MC)", f"Multiproducto (MP, {mp['campaign']})"])
    ax[0].set_ylabel("Costo anual (k USD)"); ax[0].legend(fontsize=7.5, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.42))
    for q_, r_ in enumerate((mc, mp)):
        tot = sum(f(r_) for _, f in cats)
        ax[0].text(q_, tot / 1e3 + 15, f"{tot / 1e3:,.0f} k\nexporta {r_['E_exp']:.0f} kW a la microrred", ha="center", fontsize=7.5, color=INK2)
    ax[0].set_ylim(0, 1500)
    ax[0].set_title(f"Trabajadores: MC {mc['workers']:.0f} vs MP {mp['workers']:.0f} (regla del libro, p. 77)")
    G3 = d["G3"]
    scs = [g["scale"] for g in G3]
    for q, wage in enumerate((0, 3750, 7500, 15000)):
        diff = [((g["MP"]["profit"] - 3 * 3 * wage) - (g["MC"]["profit"] - 5 * 3 * wage)) / 1e3 for g in G3]
        ax[1].plot(scs, diff, "o-", color=C[q], label=f"{wage:,} USD/año".replace(",", "."))
    ax[1].axhline(0, color=INK2, lw=0.8)
    ax[1].set_xscale("log", base=2); ax[1].set_xticks(scs); ax[1].set_xticklabels([f"{s:g}×" for s in scs])
    ax[1].set_xlabel("Escala de producción"); ax[1].set_ylabel("Beneficio MP − MC (k USD/año)")
    ax[1].legend(title="Salario por operario", fontsize=7.5, loc="upper left", bbox_to_anchor=(1.01, 1.0)); ax[1].set_title("Ventaja de compartir equipos")
    fig.suptitle("Fig. 15  Modelo 4: complejo multiplanta vs planta multiproducto (libro de Corsano et al., 2009, cap. 5)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig15_m4_MC_vs_MP.png")


if __name__ == "__main__":
    for f in (fig_m1_kinetics, fig_m1_ident, fig_m1_base, fig_m1_tau, fig_m1_bmap, fig_m1_hier, fig_m1_sobol, fig_m2, fig_m34):
        try:
            f()
        except Exception as e:
            import traceback; traceback.print_exc()
