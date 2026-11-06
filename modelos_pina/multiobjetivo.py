"""
Frente de Pareto margen–GWP por ε-restricción (v10). Bertran, Tula y Gani (2022, sec. 3.4: objetivo económico o
ambiental); Liao et al. (2026: optimización multiobjetivo).

El MILP de dimensionamiento.py lleva el GWP de proceso como expresión lineal (kg CO2e/año, mismos coeficientes que
acv.py). Pasos:
  1. extremo económico: el óptimo de E1 (máximo margen) y su GWP;
  2. extremo ambiental: mínimo GWP (con un desempate mínimo por margen);
  3. puntos intermedios: máximo margen con GWP ≤ ε para ε entre los dos extremos.
Cada punto arranca en caliente con el diseño del punto anterior y se pule con tamaños vecinos (pulido_v10.fixed).
Salidas: results/pareto.json y figs/fig43_pareto.png.
"""
import json, os
import numpy as np
import dimensionamiento as dm

RES = dm.RES


def design(r):
    return dict(r["sizes"], turno3=r["turno3"])


def best_of(cands, **kw):
    best = None
    for fx in cands:
        try:
            r = dm.solve(fix=fx, time_limit=60, gap=0.002, **kw)
        except Exception:
            continue
        if r.get("scen") and (best is None or r["obj"] > best["obj"]):
            best = r
    return best


def point(r, eps=None):
    s = r["scen"][0]
    return dict(eps=eps, margin=s["margin"], gwp=s["products"]["gwp_kg"], sizes=r["sizes"], turno3=r["turno3"], gap=r.get("gap"), status=r["status"])


def frente(pts):
    """Puntos no dominados (mayor margen con menor o igual GWP). Las corridas con límite de tiempo pueden dejar puntos dominados."""
    return [p for p in pts if not any(q is not p and q["gwp"] <= p["gwp"] + 1e-6 and q["margin"] > p["margin"] + 1e-6 for q in pts)]


def run(n=6):
    d = json.load(open(os.path.join(RES, "dimensionamiento.json")))
    eco = d["E1|Óptimo económico"]
    g_eco = eco["scen"][0]["products"]["gwp_kg"]
    pts = [point(eco)]
    print("extremo económico", round(pts[0]["margin"]), round(g_eco / 1000), flush=True)
    seeds = [design(d[k]) for k in ("E1|Óptimo sin opciones v10 (sin hojas ni hub)", "E1|Óptimo sin vinagre", "E1|Diseño v9 con parámetros v10") if k in d]
    low = dm.solve(objective="gwp", time_limit=240, hint=seeds[0] if seeds else None)
    g_min = low["scen"][0]["products"]["gwp_kg"]
    print("extremo ambiental", round(low["scen"][0]["margin"]), round(g_min / 1000), flush=True)
    prev = design(eco)
    for eps in np.linspace(g_eco, g_min, n + 1)[1:-1]:
        r = dm.solve(gwp_max=float(eps), time_limit=180, hint=prev)
        cand = [design(r)] if r.get("scen") else []
        cand += [dict(prev, **{u: "no"}) for u in ("Extractora hojas", "Bodega etanol", "Destilación", "Acetificador", "Bodega cáscara")]
        alt = best_of(cand, gwp_max=float(eps))
        if alt and (not r.get("scen") or alt["obj"] > r["obj"]):
            r = alt
        if r.get("scen"):
            pts.append(point(r, float(eps))); prev = design(r)
            print("ε", round(eps / 1000), "→ margen", round(pts[-1]["margin"]), "GWP", round(pts[-1]["gwp"] / 1000), r["sizes"].get("Extractora hojas"),
                  r["sizes"].get("Acetificador"), flush=True)
    pts.append(point(low))
    out = dict(points=frente(pts), all_points=pts, g_eco=g_eco, g_min=g_min)
    json.dump(out, open(os.path.join(RES, "pareto.json"), "w"), indent=1, default=float)
    return out


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK2, save
    P = sorted(out["points"], key=lambda p: p["gwp"])
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.plot([p["gwp"] / 1000 for p in P], [p["margin"] for p in P], "-o", color=C[0])
    for p in P:
        s = p["sizes"]
        tag = ("hojas " + s.get("Extractora hojas", "no") if s.get("Extractora hojas", "no") != "no" else "sin hojas") + \
              (" · acet. " + s.get("Acetificador") if s.get("Acetificador", "no") != "no" else " · sin vinagre")
        ax.annotate(tag, (p["gwp"] / 1000, p["margin"]), xytext=(6, -12), textcoords="offset points", fontsize=7.5, color=INK2)
    ax.set_xlabel("GWP de proceso (t CO2e/año)"); ax.set_ylabel("Margen anual del MILP (MM COP/año)")
    ax.set_title("Cada punto es un diseño óptimo con un tope de GWP (ε-restricción)", fontsize=9)
    fig.suptitle("Fig. 43  Frente de Pareto margen–GWP del dimensionamiento v10", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig43_pareto.png")


if __name__ == "__main__":
    import sys
    if "figura" in sys.argv[1:]:          # rehacer el filtro y la figura con results/pareto.json
        o = json.load(open(os.path.join(RES, "pareto.json")))
        o["all_points"] = o.get("all_points", o["points"]); o["points"] = frente(o["all_points"])
        json.dump(o, open(os.path.join(RES, "pareto.json"), "w"), indent=1, default=float)
        figure(o)
    else:
        figure(run())
