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


if __name__ == "__main__":
    import sys
    todo = sys.argv[1:] or ["50", "tabla", "51"]
    if "50" in todo:
        fig50()
