"""
Experimentos del Modelo 2 (línea de etanol del hub, reciclo de vinaza, penalización ambiental; Corsano 2006b).

F1 caso base con las dos penalizaciones de Corsano (ec. 37 y 38) y sin penalización
F2 concentración del hub (factor f): ¿cuándo se vuelve óptimo reciclar vinaza? (vínculo con C_H de §4.6)
F3 barrido de S_W (azúcar residual de la vinaza) — análogo a la Fig. 3 de Corsano 2006b
F4 frontera de Pareto TAC vs vinaza descargada (ε-restricción, vínculo con §6.6 de la tesis)
F5 asignación del hub: participación del hidrolizado vs inhibición (alpha) y costo del hidrolizado
F6 límite de reciclo phi_max (acumulación de sales/inhibidores)
"""
import json, os, sys, time, copy
import numpy as np
from multiprocessing import Pool
import params as p
import m2_hub_etanol_reciclo as m2

RES = os.path.join(os.path.dirname(__file__), "results")
NPROC = int(os.environ.get("NPROC", 2))


def _quiet():
    fd = os.open(os.devnull, os.O_WRONLY); os.dup2(fd, 1); os.dup2(fd, 2)


def hub_scaled(f, evap_cost_per_m3_water=0.35 * p.C_STEAM):
    """Concentra todas las corrientes del hub por un factor f (evaporación múltiple efecto, 0.35 t vapor/t agua)."""
    h = copy.deepcopy(p.HUB)
    for k in h:
        h[k]["S"] *= f
        h[k]["c"] = h[k]["c"] * f + (f - 1) * evap_cost_per_m3_water      # mismo USD/kg azúcar + evaporación
        h[k]["Fmax"] /= f
    return h


def solve(kw):
    tag = kw.pop("_tag", None)
    best = None
    for s in (None, 1, 2, 3):
        try:
            r = m2.build_and_solve(m2.default_cfg(seed=s, **kw))
        except Exception as e:
            continue
        if r["ok"] and (best is None or r["TAC"] < best["TAC"]):
            best = r
    if best is None:
        return dict(ok=False, tag=tag)
    best.pop("units_full", None)
    best["tag"] = tag
    return best


def run(jobs):
    with Pool(NPROC, initializer=_quiet) as pl:
        return pl.map(solve, jobs)


def slim(r):
    keys = ("ok", "tag", "TAC", "capex_ann", "opex", "penalty", "CT", "Sw", "Pw", "eta_l", "eta_h", "R", "Nmin",
            "steam_t_yr", "VRes_yr", "Vvin_yr", "recycle_frac", "use_yr", "water_yr", "active", "label", "cpu")
    return {k: r.get(k) for k in keys}


if __name__ == "__main__":
    out = {}
    t0 = time.time()
    # F1
    jobs = [dict(penalty=pen, _tag=pen) for pen in ("none", "eq37", "eq38")]
    rs = run(jobs)
    out["F1"] = [slim(r) for r in rs]
    base = [r for r in rs if r["tag"] == "eq38"][0]
    out["F1_units"] = base["units"]
    print("F1", [(r["tag"], round(r["TAC"]), r["label"], round(r["recycle_frac"], 2)) for r in rs], flush=True)
    # F2
    fs = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    rs = run([dict(hub=hub_scaled(f), _tag=f) for f in fs])
    out["F2"] = [slim(r) for r in rs]
    print("F2", [(r["tag"], round(r.get("TAC", 0)), round(r.get("recycle_frac", 0), 2), round(r.get("water_yr", 0))) for r in rs], flush=True)
    # F3: S_W fijo, con alimentación diluida (f=1) y concentrada (f=3)
    Sws = [0.5, 2, 5, 10, 15, 20, 30, 40]
    jobs = [dict(Sw_fix=s, hub=hub_scaled(f), _tag=(f, s)) for f in (1.0, 3.0) for s in Sws]
    rs = run(jobs)
    out["F3"] = [slim(r) for r in rs]
    print("F3 ok", sum(r["ok"] for r in rs), flush=True)
    # F4: Pareto
    jobs = []
    for f in (1.0, 3.0):
        r0 = [r for r in out["F2"] if r["tag"] == f][0]
        V0 = r0["VRes_yr"]
        for frac in (1.0, 0.8, 0.6, 0.4, 0.25, 0.1, 0.03):
            jobs.append(dict(hub=hub_scaled(f), VRes_max=frac * V0 + 1e-3, penalty="none", _tag=(f, frac, V0)))
    rs = run(jobs)
    out["F4"] = [slim(r) for r in rs]
    print("F4 ok", sum(r["ok"] for r in rs), flush=True)
    # F5: asignación del hub (participación de hidrolizado)
    alphas = [0.0, 0.15, 0.3, 0.45, 0.6]
    costs = [1.0, 2.0, 3.0, 4.5, 6.0, 9.0]
    jobs = []
    for a in alphas:
        for c in costs:
            h = copy.deepcopy(p.HUB); h["hydro"]["c"] = c
            jobs.append(dict(alpha=a, hub=h, _tag=(a, c)))
    rs = run(jobs)
    out["F5"] = [slim(r) for r in rs]
    print("F5 ok", sum(r["ok"] for r in rs), flush=True)
    # F6
    phis = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6]
    rs = run([dict(phi_max=ph, hub=hub_scaled(3.0), _tag=ph) for ph in phis])
    out["F6"] = [slim(r) for r in rs]
    print("F6", [(r["tag"], round(r.get("TAC", 0)), round(r.get("recycle_frac", 0), 2)) for r in rs], flush=True)
    json.dump(out, open(f"{RES}/m2_all.json", "w"), default=float)
    print("M2 total", round(time.time() - t0), "s")
