"""Figuras de la respuesta al comité: reemplazan las Figuras 5.18 y 5.19 de la tesis (antes fig48 y fig49 del informe).

  python respuesta_figuras.py            -> figs/fig52_h1_h4_vpn.png, figs/fig53_h2_h3_cotas.png (español)
  FIG_LANG=en python respuesta_figuras.py -> figs/en/... (inglés)

Fig. 52  H1 a 20,7 kg/t (margen y VPN, simultáneo frente a secuencial) y mapa H4 en VPN del TEA a 20,7 kg/t, con la línea
         VPN = 0 y la clasificación de los puntos que deciden la frontera (robusto / no establecido).
Fig. 53  H2 (a 21,8 kg/t, con bomba de calor): margen hallado y cota dual por tope fósil. H3 (a 21,8 kg/t): frente con cotas
         duales, el punto ε = −645 t corregido y el dominado retirado; y, a 20,7 kg/t, el óptimo y el diseño de emisión neta nula.
Datos: results/respuesta/{cifras,tablas,h1_207,h3,h3full_0,h3full_1,neutral207,gwp207}.json y results/v13/H3b.json.
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
import figuras  # estilo común (rcParams)
from figuras import C, INK, INK2

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results", "respuesta")
EN = os.environ.get("FIG_LANG", "").lower() == "en"
OUT = os.path.join(HERE, "figs", "en") if EN else os.path.join(HERE, "figs")
os.makedirs(OUT, exist_ok=True)


def J(n, d=R):
    return json.load(open(os.path.join(d, n)))


def L(es, en):
    return en if EN else es


def num(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s if EN else s.replace(",", " ").replace(".", ",")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=200)
    plt.close(fig)
    print("fig", os.path.join(OUT, name))


NEG, MID, POS = C[7], "#f2f1ee", C[0]
CMAP = LinearSegmentedColormap.from_list("div", [NEG, "#f3b9b4", MID, "#b5cff0", POS])


def fig52():
    c = J("cifras.json")
    h1 = J("h1_207.json")
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.0), gridspec_kw=dict(width_ratios=[0.8, 1.35]))
    # --- H1 ---
    cen = c["central"]
    groups = [L("Simultáneo\n(óptimo)", "Simultaneous\n(optimum)"), L("Secuencial\npor fracciones", "Sequential\nby fractions")]
    mg = [cen["margin"], h1["eval"]["margin"]]
    npv = [cen["tea"]["NPV"], h1["tea"]["NPV"]]
    x = np.arange(2); w = 0.36
    b1 = ax[0].bar(x - w / 2 - 0.01, mg, w, color=C[0], label=L("Margen anual del MILP (MM COP/año)", "Annual MILP margin (MM COP/year)"))
    b2 = ax[0].bar(x + w / 2 + 0.01, npv, w, color=C[1], label=L("VPN al 10 % (MM COP)", "NPV at 10 % (MM COP)"))
    for bars in (b1, b2):
        for r_ in bars:
            h = r_.get_height()
            ax[0].annotate(num(h), (r_.get_x() + r_.get_width() / 2, h), ha="center", va="bottom", fontsize=8.5,
                           xytext=(0, 2), textcoords="offset points")
    ax[0].axhline(0, color=INK2, lw=0.8)
    ax[0].set_xticks(x); ax[0].set_xticklabels(groups, fontsize=9)
    ax[0].set_ylim(0, 1.25 * max(npv + mg))
    ax[0].set_ylabel("MM COP")
    ax[0].set_title(L("H1: la misma superestructura, diseño simultáneo o por fracciones",
                      "H1: the same superstructure, designed simultaneously or by fractions"), fontsize=9.5)
    ax[0].legend(fontsize=8, loc="upper right")
    ax[0].text(0.01, -0.2, L("Con flujos promedio los valores son los mismos. Jugo de hoja: 20,7 kg/t.",
                             "Average flows give the same values. Leaf juice: 20.7 kg/t."),
               transform=ax[0].transAxes, fontsize=7.5, color=INK2)
    # --- H4: VPN ---
    H = c["H4"]
    B = sorted({p["bottles"] for p in H.values()}); V = sorted({p["vinegar"] for p in H.values()})
    Z = np.full((len(V), len(B)), np.nan)
    for p in H.values():
        if p.get("NPV") is not None:
            Z[V.index(p["vinegar"]), B.index(p["bottles"])] = p["NPV"]
    norm = TwoSlopeNorm(vmin=-11000, vcenter=0, vmax=25000)
    im = ax[1].imshow(np.clip(Z, -11000, 25000), origin="lower", cmap=CMAP, norm=norm, aspect="auto")
    for i, v in enumerate(V):
        for j, b in enumerate(B):
            z = Z[i, j]
            if np.isfinite(z):
                r_, g_, b_, _ = CMAP(norm(np.clip(z, -11000, 25000)))
                dark = 0.2126 * r_ + 0.7152 * g_ + 0.0722 * b_ < 0.5
                ax[1].text(j, i, num(z), ha="center", va="center", fontsize=8, color="white" if dark else INK)
            else:
                ax[1].add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#e4e3df", edgecolor="white", hatch="///", lw=0))
                ax[1].text(j, i, L("no se\nconstruye", "not\nbuilt"), ha="center", va="center", fontsize=7, color=INK2)
    Zc = np.ma.masked_invalid(Z)
    ax[1].contour(Zc, levels=[0.0], colors=INK, linewidths=2.0)
    flip = c["flip"]
    for k, f in flip.items():
        b, v = (int(s) for s in k.split("|"))
        robust = f["deviation_to_flip"] > c["secant"]["dev_max"]
        ax[1].add_patch(Rectangle((B.index(b) - 0.47, V.index(v) - 0.47), 0.94, 0.94, fill=False, edgecolor=INK,
                                  lw=1.8, ls="-" if robust else (0, (3, 2))))
    ax[1].set_xticks(range(len(B)))
    ax[1].set_xticklabels([L("100 000\n(sin vino)", "100,000\n(no wine)") if b == 100000 else num(b) for b in B], fontsize=8)
    ax[1].set_yticks(range(len(V))); ax[1].set_yticklabels([num(v) for v in V], fontsize=8)
    ax[1].set_xlabel(L("Demanda de vino embotellado (botellas/año)", "Bottled-wine demand (bottles/year)"))
    ax[1].set_ylabel(L("Demanda de vinagre al 5 % (m³/año)", "Demand for 5 % vinegar (m³/year)"))
    ax[1].grid(False)
    cb = fig.colorbar(im, ax=ax[1], fraction=0.04, pad=0.02)
    cb.set_label(L("VPN del diseño reoptimizado (MM COP)", "NPV of the re-optimized design (MM COP)"))
    ax[1].set_title(L("H4: VPN del TEA por par de mercados (línea gruesa: VPN = 0)",
                      "H4: TEA NPV for each pair of market sizes (thick line: NPV = 0)"), fontsize=9.5)
    handles = [Patch(facecolor="none", edgecolor=INK, lw=1.8, label=L("No viable, robusto (cota dual)", "Not viable, robust (dual bound)")),
               Patch(facecolor="none", edgecolor=INK, lw=1.8, ls=(0, (3, 2)),
                     label=L("No viable como se halló; no establecido", "Not viable as found; not established"))]
    handles.append(Line2D([], [], color=INK, lw=2, label=L("VPN = 0 (interpolado)", "NPV = 0 (interpolated)")))
    ax[1].legend(handles=handles, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=3, frameon=False)
    fig.suptitle(L("Valor del diseño simultáneo (H1) y frontera de demanda mínima viable en VPN (H4), jugo de hoja a 20,7 kg/t",
                   "Value of simultaneous design (H1) and NPV frontier of minimum viable demand (H4), leaf juice at 20.7 kg/t"),
                 fontsize=10.5, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig52_h1_h4_vpn.png")


def fig53():
    t = J("tablas.json")
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.0))
    # --- H2 (a 21,8 kg/t, con bomba de calor) ---
    o = t["H2_opt"]
    pts = [dict(frac=1.0, m=o["incumbent"], b=o["bound"])] + [dict(frac=s["frac"], m=s["incumbent"], b=s["bound"]) for s in t["H2"]]
    xs = [100 * p["frac"] for p in pts]; ms = [p["m"] for p in pts]
    for p in pts:
        if p["b"] is not None:
            ax[0].plot([100 * p["frac"]] * 2, [p["m"], p["b"]], color=C[0], lw=1.2, alpha=0.55)
            ax[0].plot([100 * p["frac"]], [p["b"]], marker="_", ms=12, mew=2, color=C[0], alpha=0.75)
        else:
            ax[0].annotate(L("sin cota\nfinita", "no finite\nbound"), (100 * p["frac"], p["m"]), textcoords="offset points",
                           xytext=(0, 10), ha="center", fontsize=7.5, color=INK2)
    ax[0].plot(xs, ms, "o-", color=C[0], ms=7, lw=2, label=L("Margen hallado", "Margin found"))
    ax[0].annotate(L("bomba de calor\n25 kWt", "heat pump\n25 kWt"), (80, pts[1]["m"]), textcoords="offset points", xytext=(10, 10),
                   fontsize=7.5, color=INK2)
    ax[0].axhline(0, color=INK2, lw=0.8)
    ax[0].invert_xaxis()
    ax[0].set_xlabel(L("Tope de energía fósil (% del óptimo sin tope)", "Fossil-energy cap (% of the uncapped optimum)"))
    ax[0].set_ylabel(L("Margen anual (MM COP/año)", "Annual margin (MM COP/year)"))
    ax[0].set_title(L("H2: costo de la autonomía energética (a 21,8 kg/t)", "H2: cost of energy autonomy (at 21.8 kg/t)"), fontsize=9.5)
    ax[0].legend(handles=[Line2D([], [], color=C[0], marker="o", lw=2, label=L("Margen hallado", "Margin found")),
                          Line2D([], [], color=C[0], marker="_", ms=12, mew=2, lw=1.2, alpha=0.6,
                                 label=L("Cota dual de la corrida libre", "Dual bound of the free run"))], fontsize=8, loc="lower left")
    # --- H3 ---
    h3 = J("h3.json"); f0 = J("h3full_0.json"); f1 = J("h3full_1.json")
    b3 = J("H3b.json", os.path.join(HERE, "results", "v13"))
    w = {round(e["w"], 2): e for e in b3["mcda"]}
    eco = b3["extremos"]["economico"]
    amb = b3["extremos"]["ambiental"]
    g = lambda e: (e["products"]["gwp_neto_kg"] if "products" in e else e["gwp_neto"]) / 1000
    front = [  # (GWP neto t, margen, cota dual o None), a 21,8 kg/t
        (g(eco), t["H2_opt"]["incumbent"], t["H2_opt"]["bound"]),
        (g(w[0.75]), w[0.75]["margin"], None),
        (f0["published"]["gwp_neto"], f0["new"]["margin"], f0["new"]["bound"]),
        (g(w[0.5]), w[0.5]["margin"], None),
        (f1["new"]["products"]["gwp_neto_kg"] / 1000, f1["new"]["margin"], f1["new"]["bound"]),
        (h3[2]["eps"] / 1000, h3[2]["incumbent"], h3[2]["bound"]),
        (h3[3]["eps"] / 1000, h3[3]["incumbent"], None),
        (h3[4]["eps"] / 1000, h3[4]["incumbent"], None),
        (g(amb), amb["margin"], None),
    ]
    front.sort()
    for gx, m, b in front:
        if b is not None:
            ax[1].plot([gx, gx], [m, b], color=C[0], lw=1.2, alpha=0.55)
            ax[1].plot([gx], [b], marker="_", ms=12, mew=2, color=C[0], alpha=0.75)
    ax[1].plot([p[0] for p in front], [p[1] for p in front], "o-", color=C[0], ms=6, lw=2,
               label=L("Frente hallado (a 21,8 kg/t)", "Front found (at 21.8 kg/t)"))
    ax[1].plot([f1["published"]["gwp_neto"]],
               [f1["published"]["margin"]], "X", ms=9, mfc="none", mec=INK2, mew=1.4,
               label=L("Punto publicado antes, dominado (retirado)", "Point published earlier, dominated (withdrawn)"))
    ax[1].annotate(L("ε = −645 t\ncorregido", "ε = −645 t\ncorrected"), (f1["new"]["products"]["gwp_neto_kg"] / 1000, f1["new"]["margin"]), textcoords="offset points",
                   xytext=(-75, 28), fontsize=7.5, color=INK2,
                   arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    ax[1].annotate("w = 0,75" if not EN else "w = 0.75", (g(w[0.75]), w[0.75]["margin"]), textcoords="offset points",
                   xytext=(-70, 28), fontsize=7.5, color=INK2,
                   arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    n = J("neutral207.json"); g7 = J("gwp207.json")
    opt207 = (g7["optimum"]["short"]["products"]["gwp_neto_kg"] / 1000, g7["optimum"]["short"]["margin"])
    nz = (n["short"]["products"]["gwp_neto_kg"] / 1000, n["short"]["margin"])
    ax[1].plot([opt207[0], nz[0]], [opt207[1], nz[1]], "D", ms=10, mfc="none", mec=C[1], mew=2,
               label=L("A 20,7 kg/t: óptimo y diseño de emisión neta nula", "At 20.7 kg/t: optimum and net-zero design"))
    ax[1].annotate(L("neto nulo\n(−83 MM COP/año)", "net zero\n(−83 MM COP/year)"), nz, textcoords="offset points", xytext=(8, -30),
                   fontsize=7.5, color=INK2)
    ax[1].axvline(0, color=INK2, lw=0.8, ls=":")
    ax[1].axhline(0, color=INK2, lw=0.8)
    ax[1].set_xlabel(L("Huella neta frente a la línea base sin planta (t CO₂e/año; GWP lineal del MILP)",
                       "Net GWP against the no-plant baseline (t CO₂e/year; linear GWP of the MILP)"))
    ax[1].set_ylabel(L("Margen anual (MM COP/año)", "Annual margin (MM COP/year)"))
    ax[1].set_title(L("H3: frente margen–huella neta con cotas duales", "H3: margin–net GWP front with dual bounds"), fontsize=9.5)
    ax[1].legend(fontsize=7.5, loc="lower right")
    fig.suptitle(L("Autonomía energética (H2) y frente margen–huella neta (H3) con las cotas duales de cada corrida",
                   "Energy autonomy (H2) and margin–net GWP front (H3) with the dual bound of each run"),
                 fontsize=10.5, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig53_h2_h3_cotas.png")


if __name__ == "__main__":
    fig52()
    fig53()
