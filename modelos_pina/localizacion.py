"""
Localización estilizada (v10): ¿una planta central que recibe hojas frescas o depósitos de extracción en las zonas
de cultivo que envían solo el jugo? Bertran, Tula y Gani (2022, sec. 5.1: síntesis con localización y transporte,
ePSIN) y Liao et al. (2026: depósitos ubicados con SIG y NSGA-II).

TODO EL ESCENARIO ES SUPUESTO [S]: no hay aún datos de ubicación de fincas en el Bajo Atrato. Las cuatro zonas,
sus participaciones en el área sembrada y las distancias por río y por vía son marcadores de posición que se
reemplazan cuando lleguen los datos de campo; la estructura del modelo se mantiene.

MILP (SCIP): elegir un sitio de planta s (binaria y_s), qué zonas tienen depósito de extracción (binaria z_j) y por qué
modo se transporta cada flujo. Minimiza el costo anual: corte y cargue + transporte (hojas frescas o jugo) + depósitos
(inversión anualizada con el factor AF del dimensionamiento + un operario por turno). Resultado: costo de acopio por
tonelada de hojas puesta en planta (equivalente) y distancia media de la fruta, que pasan al registro de parámetros.
"""
import json, os
from pyscipopt import Model, quicksum
import datos as D
import dimensionamiento as dm
import tea_burk as tb

RES = dm.RES
ZONAS = {   # zona: (fracción del área, km por río al sitio A, km por vía al sitio B)   [S]
    "Zona 1 (ribera norte)": (0.40, 15, 40),
    "Zona 2 (ribera centro)": (0.30, 35, 20),
    "Zona 3 (afluentes)": (0.20, 55, 30),
    "Zona 4 (interior)": (0.10, 80, 60),
}
SITIOS = {"A: muelle sobre el río": "rio", "B: cabecera con vía": "via"}
FLETE = {"rio": 900.0, "via": 600.0}           # COP/t·km por lancha y por camión [S]
CORTE = 15_000.0                               # COP/t de hojas: corte, cargue y descargue [S]


def solve(hojas_t=None, verbose=True):
    hojas_t = hojas_t or dm.HOJAS_SUPPLY
    JF = D.val("jugo_hojas_frac")
    dep_purchase = dm.buy("extrusora_hojas", 5) + dm.buy("tanque_pulmon", 20)       # depósito: extrusora de 5 t/h + tanque de jugo [S]
    op1 = tb.payroll(1, tb.calendar(3), engineer=0)["total"] * (1 + tb.COMMON["supervision"])
    dep_ann = dm.AF * dep_purchase + op1
    m = Model("localizacion"); m.hideOutput()
    ys = {s: m.addVar(vtype="B") for s in SITIOS}
    zj = {j: m.addVar(vtype="B") for j in ZONAS}
    xf = {(j, s): m.addVar(lb=0) for j in ZONAS for s in SITIOS}       # t de hojas frescas de la zona j al sitio s
    xj = {(j, s): m.addVar(lb=0) for j in ZONAS for s in SITIOS}       # t de hojas extraídas en el depósito de j (sale jugo)
    m.addCons(quicksum(ys.values()) == 1)
    for j, (f, d_a, d_b) in ZONAS.items():
        Hj = hojas_t * f
        m.addCons(quicksum(xf[j, s] + xj[j, s] for s in SITIOS) == Hj)
        for s in SITIOS:
            m.addCons(xf[j, s] + xj[j, s] <= Hj * ys[s])
            m.addCons(xj[j, s] <= Hj * zj[j])
    dist = lambda j, s: ZONAS[j][1] if SITIOS[s] == "rio" else ZONAS[j][2]
    cost = (quicksum(CORTE * (xf[j, s] + xj[j, s]) + FLETE[SITIOS[s]] * dist(j, s) * (xf[j, s] + JF * xj[j, s])
                     for j in ZONAS for s in SITIOS) + dep_ann * quicksum(zj.values()))
    m.setObjective(cost, "minimize"); m.optimize()
    site = max(SITIOS, key=lambda s: m.getVal(ys[s]))
    deps = [j for j in ZONAS if m.getVal(zj[j]) > 0.5]
    total = m.getObjVal()
    # alternativas fijas para comparar: central en cada sitio sin depósitos y con depósito en cada zona
    def fixed(site_, deps_):
        c = 0.0
        for j, (f, d_a, d_b) in ZONAS.items():
            Hj = hojas_t * f; dd = d_a if SITIOS[site_] == "rio" else d_b
            c += CORTE * Hj + FLETE[SITIOS[site_]] * dd * Hj * (JF if j in deps_ else 1.0)
        return c + dep_ann * len(deps_)
    alts = {f"Central en {s.split(':')[0]}, sin depósitos": fixed(s, []) for s in SITIOS}
    alts.update({f"{s.split(':')[0]} con depósitos en las 4 zonas": fixed(s, list(ZONAS)) for s in SITIOS})
    fruit_km = sum(f * (d_a if SITIOS[site] == "rio" else d_b) for f, d_a, d_b in ZONAS.values())
    out = dict(hojas_t=hojas_t, sitio=site, depositos=deps, costo_total=total, costo_t=total / hojas_t, alternativas=alts,
               dist_fruta_km=fruit_km, deposito_anual=dep_ann, supuestos=dict(zonas=ZONAS, fletes=FLETE, corte=CORTE))
    if verbose:
        print(f"sitio {site}; depósitos {deps}; costo {total / 1e6:,.0f} MM COP/año = {total / hojas_t:,.0f} COP/t; fruta a {fruit_km:.0f} km")
        for k, v in alts.items():
            print(f"   {k}: {v / hojas_t:,.0f} COP/t")
    return out


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK2, save
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 4.2), gridspec_kw=dict(width_ratios=[1.1, 1]))
    alts = dict(out["alternativas"]); alts["Óptimo del MILP"] = out["costo_total"]
    labs = list(alts); vals = [alts[k] / out["hojas_t"] for k in labs]
    ax[0].barh(range(len(vals)), vals, color=[C[2] if k == "Óptimo del MILP" else C[0] for k in labs])
    for i, v in enumerate(vals):
        ax[0].text(v * 1.01, i, f"{v:,.0f}".replace(",", " "), va="center", fontsize=8)
    ax[0].set_yticks(range(len(vals))); ax[0].set_yticklabels(labs, fontsize=8); ax[0].invert_yaxis()
    ax[0].set_xlabel("COP por t de hojas puesta en planta"); ax[0].set_xlim(0, max(vals) * 1.18)
    ax[0].set_title("Costo de acopio por configuración (escenario supuesto)", fontsize=9)
    # esquema de zonas: posición ilustrativa por distancias al sitio A (río) y B (vía)
    for i, (j, (f, d_a, d_b)) in enumerate(out["supuestos"]["zonas"].items()):
        ax[1].scatter(d_a, d_b, s=2200 * f, color=C[3], alpha=0.55, edgecolor=INK2)
        ax[1].text(d_a, d_b + 5, j.split(" (")[0] + ("\n(depósito)" if j in out["depositos"] else ""), ha="center", fontsize=8)
    ax[1].set_xlabel("km por río al sitio A"); ax[1].set_ylabel("km por vía al sitio B")
    ax[1].set_title(f"Zonas de cultivo (tamaño = área) · planta en {out['sitio'].split(':')[0]}", fontsize=9)
    ax[1].set_xlim(0, 95); ax[1].set_ylim(0, 75)
    fig.suptitle("Fig. 42  Localización estilizada: planta central frente a depósitos de extracción en las zonas (todo el escenario es supuesto)",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig42_localizacion.png")


if __name__ == "__main__":
    out = solve()
    out["sensibilidad"] = {f"{f:.2f}": solve(dm.HOJAS_SUPPLY * f / D.val("frac_acopio_hojas"), verbose=False)["costo_t"] for f in (0.10, 0.25, 0.50)}
    json.dump(out, open(os.path.join(RES, "localizacion.json"), "w"), indent=1, default=float)
    figure(out)
