"""
v14: tabla del valor de cada acople entre escalas y figuras 50 (marco multiescala) y 51 (resultados).

  python multiescala_v14_post.py        -> results/v14/acoples.json, figs/fig50_multiescala.png, figs/fig51_multiescala_resultados.png
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import dimensionamiento as dm
from figuras import C, INK, INK2, GRID, save

OUT = os.path.join(dm.RES, "v14")
L = lambda g: json.load(open(os.path.join(OUT, f"{g}.json"))) if os.path.exists(os.path.join(OUT, f"{g}.json")) else {}
L13 = lambda g: json.load(open(os.path.join(dm.RES, "v13", f"{g}.json")))
fmt = lambda v, n=0: f"{v:,.{n}f}".replace(",", " ").replace(".", ",")


def box(ax, x, y, w, h, title, sub, body, col):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", fc=col + "22", ec=col, lw=1.6))
    ax.text(x + 0.012, y + h - 0.022, title, fontsize=10.5, fontweight="bold", va="top", color=INK)
    ax.text(x + w - 0.012, y + h - 0.024, sub, fontsize=8, va="top", ha="right", color=INK2, style="italic")
    ax.text(x + 0.012, y + h - 0.068, body, fontsize=8.2, va="top", color=INK, linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, col):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, mutation_scale=14))


def tag(ax, x, y, s):
    ax.text(x, y, s, fontsize=8, fontweight="bold", color="white", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.25", fc=C[1], ec="none"))


def fig50():
    fig, ax = plt.subplots(figsize=(14, 8.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.89); ax.axis("off")
    W, Hh = 0.40, 0.145
    xs = 0.30
    B = {   # escala: (x, y, título, subtítulo, cuerpo, color)
        "micro": (xs, 0.03, "Microorganismo: cinética", "minutos–horas · L",
                  "Monod con inhibición por etanol (Murcia Palacios 2013)\nKrishnan et al. (1999) para jugos de cáscara y de hojas\nidentificabilidad: un punto final, µmax y X0 no se separan", C[2]),
        "equipo": (xs, 0.25, "Equipo y tren de fermentación", "horas–días · m³",
                   "superestructura NLP del modelo 1 (Corsano et al. 2004, 2006a)\nregla de Moresi (1989b) y regla de llenado τ\nprogramación semanal STN (Maravelias 2021)", C[0]),
        "planta": (xs, 0.47, "Planta: síntesis, tamaños y operación anual", "semanas–año · t/año",
                   "GDP de 23 pasos y 152 opciones → MILP exacto (Grossmann 2021)\nrejilla continua de 24 periodos con la estacionalidad de la oferta\nbalances de energía, calidad y mercado; huella y autonomía", C[6]),
        "territorio": (0.03, 0.73, "Territorio", "km · cosecha anual",
                       "oferta EVA 2022 y su perfil mensual\nacopio de hojas: sitio y depósitos (MILP)\nretorno de pulpa de hojas al campo", C[5]),
        "economia": (0.57, 0.73, "Economía y política", "10 años · país",
                     "TEA de Burk, Monte Carlo y Sobol\nimpuesto al consumo, ZOMAC, demandas de vino y vinagre\nACV de la cuna a la puerta contra la línea base", C[3]),
    }
    for k, (x, y, t, s, b, c) in B.items():
        box(ax, x, y, W, Hh, t, s, b, c)
    up, dn = C[1], INK2
    # micro ↔ equipo
    arrow(ax, xs + 0.10, 0.03 + Hh, xs + 0.10, 0.25, up); arrow(ax, xs + 0.30, 0.25, xs + 0.30, 0.03 + Hh, dn)
    ax.text(xs - 0.012, 0.205, "↑ t_proc, rendimiento Y_P/S\n   y su banda (no identificable)", fontsize=8.2, ha="right", va="center", color=up)
    ax.text(xs + W + 0.012, 0.205, "↓ inóculo X0, azúcar S0,\n   temperatura y τ de llenado", fontsize=8.2, ha="left", va="center", color=dn)
    tag(ax, xs + 0.10, 0.205, "U")
    # equipo ↔ planta
    arrow(ax, xs + 0.10, 0.25 + Hh, xs + 0.10, 0.47, up); arrow(ax, xs + 0.30, 0.47, xs + 0.30, 0.25 + Hh, dn)
    ax.text(xs - 0.012, 0.43, "↑ capacidad Q ≤ (N−1)·V/t_proc,\n   costo por fermentador", fontsize=8.2, ha="right", va="center", color=up)
    ax.text(xs + W + 0.012, 0.43, "↓ flujo de mosto Q, tamaños N y V,\n   carga de la semana pico", fontsize=8.2, ha="left", va="center", color=dn)
    tag(ax, xs + 0.24, 0.43, "D1 · D2")
    # planta ↔ territorio y economía
    arrow(ax, 0.20, 0.73, xs + 0.06, 0.47 + Hh, dn); arrow(ax, xs + 0.12, 0.47 + Hh, 0.24, 0.73, up)
    ax.text(0.03, 0.665, "↓ oferta mensual de fruta y hojas,\n   costo de acopio (COP/t)\n↑ hojas y fruta que pide la planta", fontsize=8.2, ha="left", va="center", color=INK)
    tag(ax, 0.235, 0.66, "T · H1")
    arrow(ax, 0.80, 0.73, xs + W - 0.06, 0.47 + Hh, dn); arrow(ax, xs + W - 0.12, 0.47 + Hh, 0.76, 0.73, up)
    ax.text(0.97, 0.665, "↓ precios, impuestos y topes de demanda\n↑ margen, inversión, huella y empleo", fontsize=8.2, ha="right", va="center", color=INK)
    tag(ax, 0.765, 0.66, "H4")
    ax.text(0.03, 0.155, "Cada flecha es una variable de acople.\nHasta v13 la mayoría se fijaba en un solo\nsentido (la cinética daba un tiempo; la\nplanta no devolvía su flujo al tren).\n\nEtiquetas: interfaz medida en v13–v14\n(tabla del valor de cada acople, §5.11).",
            fontsize=8.4, color=INK2, va="top", linespacing=1.4)
    ax.text(0.97, 0.13, "naranja: de la escala menor a la mayor\n(del detalle al sistema); gris: de la mayor\na la menor (del sistema al detalle)", fontsize=8.4, color=INK2, ha="right", va="top", linespacing=1.4)
    fig.suptitle("Fig. 50  Marco multiescala del diseño: cinco escalas, sus modelos y las variables que pasan entre ellas",
                 fontsize=11, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig50_multiescala.png")


def stn_res():
    D = L("D1")
    for f in ("D1b_abril", "D1b_festivo"):
        d = L(f)
        for k in ("abril_2sem", "festivo_largo"):
            if k in d:
                D[k] = d[k]
    return D


def tabla():
    """Valor de cada acople: pérdida de margen al cortar el enlace, medida con el modelo más detallado de las dos escalas."""
    U, T, D2, D1 = L("U"), L("T"), L("D2"), stn_res()
    H1 = json.load(open(os.path.join(dm.RES, "v13", "resumen.json")))["H1"]
    m0 = U["central"]["opt"]["margin"]
    rows = []
    rows.append(dict(acople="Fracciones dentro de la planta (pulpa → cáscara → hojas)", prueba="H1 (v13)",
                     regret=1 - H1["secuencial"]["margin"] / H1["optimo"]["margin"], base="margen",
                     nota="diseño secuencial por fracciones frente al simultáneo"))
    esc = H1["escala"]
    rows.append(dict(acople="Planta ↔ estacionalidad de la cosecha", prueba="H1 (v13)", regret=0.0,
                     regret_rango=[1 - v["promedio_evaluado"] / v["estacional"] for v in esc.values()], base="margen",
                     nota="0 a la escala actual (la demanda limita, no la capacidad); 4–12 % a 2–3,6 veces la oferta"))
    rows.append(dict(acople="Cinética ↔ tren de fermentación (modelo 1)", prueba="D2", regret=D2["12.5"]["ahorro"],
                     regret_rango=[D2["12.5"]["ahorro"], D2["3.0"]["ahorro"]], base="costo anual del tren",
                     nota=f"al flujo del óptimo ({D2['vino_m3']:.0f} m³/año); con la base original: "
                          f"{D2['base_tesis']['12.5']:.1%} y {D2['base_tesis']['3.0']:.1%}"))
    mU = [U[k]["central_fijo"]["margin"] for k in ("rapido", "lento", "lento_hojas_krishnan")]
    rows.append(dict(acople="Cinética → planta (banda no identificable)", prueba="U", regret=0.0,
                     efecto=[min(mU) / m0 - 1, max(mU) / m0 - 1], base="margen",
                     nota=f"mismo diseño en toda la banda (f = {U['band']['f_min']:.2f}–{U['band']['f_max']:.2f}); el margen se mueve solo por "
                          "auxiliares dimensionados con la capacidad nominal"))
    ok = {k: v for k, v in D1.items() if isinstance(v, dict) and "dumps" in v}
    rows.append(dict(acople="Planta → semana (STN horaria)", prueba="D1", regret=0.0, base="pérdidas en la semana",
                     semanas={k: dict(perdidas=sum(v["dumps"].values()), falta_acido=v["short_acid"], falta_botellas=v["short_bott"], gap=v["gap"])
                              for k, v in ok.items()},
                     nota="la semana pico y la cinética lenta caben sin pérdidas"))
    cfg = {k: v for k, v in T.items() if isinstance(v, dict) and "opt" in v and "evaluado_costo_real" in v}
    rows.append(dict(acople="Planta ↔ territorio (acopio de hojas)", prueba="T", regret=max(1 - v["evaluado_costo_real"]["margin"] / m0 for v in cfg.values()),
                     efecto=[min(v["opt"]["margin"] for v in cfg.values()) / m0 - 1, 0.0], base="margen",
                     nota="el diseño y las 3 746 t de hojas no cambian con el costo de acopio; el sitio y los depósitos valen hasta 6,3 %"))
    out = dict(rows=rows, margen_central=m0)
    json.dump(out, open(os.path.join(OUT, "acoples.json"), "w"), indent=1, default=float)
    for r in rows:
        print(f"{r['acople']:<60} {r['prueba']:<9} regret {r['regret']:.1%}  {r.get('regret_rango', '')} {r.get('efecto', '')}")
    return out


def gantt(ax, S, title):
    lanes = ["Frente", "Prensa", "Flotación", "Extractora", "Embotelladora", "F1", "F2", "J1", "J2", "Acetificador"]
    col = {"Fraccionar": C[0], "Prensar pulpa": C[3], "Prensar cáscara": C[1], "Flotar": C[4], "Extraer hojas": C[5], "Embotellar": C[6]}
    HZ = 168 * S.get("weeks", 1)
    for i, u in enumerate(lanes):
        for s in S["schedule"]:
            if s["unit"] != u or s["size"] < 1e-6 and not s["task"].startswith("Fermentar"):
                continue
            c = col.get(s["task"], C[2] if s["task"].startswith("Fermentar") else SEQ_L)
            st, du = s["start"], s["dur"]
            segs = [(st, min(du, HZ - st))] + ([(0, st + du - HZ)] if st + du > HZ else [])
            for a, d in segs:
                ax.broken_barh([(a, d)], (i - 0.38, 0.76), color=c, lw=0)
    cap = max(S["acet"]) or 1.0
    ia = lanes.index("Acetificador")
    for n, a in enumerate(S["acet"]):
        h = 0.76 * a / cap
        ax.broken_barh([(n, 1)], (ia + 0.38 - h, h), color=INK2, lw=0)
    ax.set_yticks(range(len(lanes))); ax.set_yticklabels(lanes, fontsize=8); ax.invert_yaxis()
    for d in range(0, HZ + 1, 24):
        ax.axvline(d, color=GRID, lw=0.8, zorder=0)
    ax.set_xlim(0, HZ); ax.set_xticks([12 + 24 * d for d in range(HZ // 24)])
    import fig_en
    ax.set_xticklabels((fig_en.days() * 2)[:HZ // 24], fontsize=8)
    ax.grid(False); ax.set_title(title, fontsize=9.5)
    from matplotlib.patches import Patch
    hs = [Patch(color=c, label=k) for k, c in list(col.items()) + [("Llenar fermentador", SEQ_L), ("Fermentar (lote)", C[2]),
                                                                  ("Acetificar (altura = kg ácido/h)", INK2)]]
    ax.legend(handles=hs, fontsize=7, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.1))


SEQ_L = "#9ec5f4"


def fig51():
    U, T, D2 = L("U"), L("T"), L("D2"); D1 = stn_res(); A = L("acoples")
    fig = plt.figure(figsize=(15.5, 9.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15], hspace=0.55, wspace=0.32)
    # A: banda cinética
    ax = fig.add_subplot(gs[0, 0]); b = U["band"]["rows"]
    x = [r["x"] for r in b]
    for k, c, lab in (("pulpa", C[0], "jugo de pulpa"), ("cascara", C[1], "jugo de cáscara"), ("hojas", C[5], "jugo de hojas")):
        ax.plot(x, [r["B"][k] for r in b], "-o", ms=3, color=c, label=f"{lab} (planta a 0,5 g/L)")
    ax.plot(x, [r["A"]["cascara"] for r in b], "--", color=C[1], label="cáscara si la planta inocula como el ensayo")
    ax.set_xscale("log"); ax.set_xlabel("inóculo supuesto del ensayo (g/L)"); ax.set_ylabel("fermentación en la planta (h)")
    ax.set_title("A · Banda de tiempos compatible con un solo punto", fontsize=9.5); ax.legend(fontsize=7)
    # B: U en el MILP
    ax = fig.add_subplot(gs[0, 1])
    labs = ["rápido\nf = %.2f" % U["rapido"]["f"], "central", "lento\nf = %.2f" % U["lento"]["f"], "lento y hojas\na 27,1 h"]
    keys = ["rapido", None, "lento", "lento_hojas_krishnan"]
    mar = [U[k]["central_fijo"]["margin"] if k else U["central"]["opt"]["margin"] for k in keys]
    npv = [U[k]["central_fijo_tea"]["NPV"] if k else U["central"]["tea"]["NPV"] for k in keys]
    xx = np.arange(4)
    ax.bar(xx - 0.2, mar, 0.4, color=C[0], label="margen (MM COP/año)"); ax.bar(xx + 0.2, npv, 0.4, color=C[3], label="VPN (MM COP)")
    for i in range(4):
        ax.text(xx[i] - 0.2, mar[i] + 80, fmt(mar[i]), ha="center", fontsize=7.5); ax.text(xx[i] + 0.2, npv[i] + 80, fmt(npv[i]), ha="center", fontsize=7.5)
    ax.set_xticks(xx); ax.set_xticklabels(labs, fontsize=8); ax.set_ylim(0, max(npv) * 1.32)
    ax.set_title("B · Reoptimizar en los extremos devuelve el mismo diseño", fontsize=9.5); ax.legend(fontsize=7.5, loc="upper left", ncol=2)
    # C: valor de cada acople
    ax = fig.add_subplot(gs[0, 2])
    rows = A["rows"]; names = ["Fracciones (H1)", "Estacionalidad (H1)", "Cinética ↔ tren (M1)", "Cinética → planta (U)",
                               "Planta → semana (D1)", "Planta ↔ territorio (T)"]
    yy = np.arange(len(rows))
    for i, r in enumerate(rows):
        ax.barh(i, r["regret"] * 100, color=C[1] if r["regret"] > 0.005 else GRID, height=0.55)
        rg = r.get("regret_rango")
        if rg:
            ax.plot([min(rg) * 100, max(rg) * 100], [i, i], color=INK, lw=2.5, solid_capstyle="butt")
        ef = r.get("efecto")
        if ef:
            ax.plot([ef[0] * 100, ef[1] * 100], [i + 0.3, i + 0.3], color=C[0], lw=2)
    ax.set_yticks(yy); ax.set_yticklabels(names, fontsize=8); ax.invert_yaxis(); ax.axvline(0, color=INK2, lw=0.8); ax.set_xlim(-8, 46)
    ax.set_xlabel("% (barra: pérdida al cortar el acople; negro: rango;\nazul: efecto en el margen sin cambio de diseño)", fontsize=8)
    ax.set_title("C · Valor de cada acople entre escalas", fontsize=9.5)
    # D: Gantt de la semana pico
    ax = fig.add_subplot(gs[1, :])
    Sb = D1["base"]
    gantt(ax, Sb, f"D · Semana del mes de más fruta (mayo) con los tamaños del óptimo: STN cíclica de 168 h; sin pérdidas; "
                  f"frente al {Sb['util']['Frente']:.0%} del turno; acetificador continuo")
    fig.suptitle("Fig. 51  Pruebas multiescala del óptimo: cinética → planta, planta → semana y valor de cada acople",
                 fontsize=11, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig51_multiescala_resultados.png")


if __name__ == "__main__":
    import sys
    todo = sys.argv[1:] or ["50", "tabla", "51"]
    if "50" in todo:
        fig50()
    if "tabla" in todo:
        tabla()
    if "51" in todo:
        fig51()
