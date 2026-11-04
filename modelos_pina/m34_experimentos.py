"""
Experimentos de los modelos 3 (campañas mixtas, Corsano 2007) y 4 (MC vs MP, libro 2009 cap. 5).

G1 heurística de Corsano 2007: SPC -> razón de lotes -> campañas candidatas -> NLP por campaña -> mejor
G2 desglose MC vs mejor MP, en el formato de la Tabla 4.3 del libro (+ mano de obra, que Corsano no valoró)
G3 mapa de régimen: escala de producción x salario -> ventaja MC - MP con mano de obra
G4 autonomía energética: capacidad de la isla de gasificación vs importación diésel / exportación a microrred
G5 ¿cambia la decisión si la mano de obra entra en la función objetivo? (3 vs 4.2 dotaciones)
"""
import json, os, time
import numpy as np
from multiprocessing import Pool
import params as p
import m3_m4_campanas_multiplanta as m

RES = os.path.join(os.path.dirname(__file__), "results")
NPROC = int(os.environ.get("NPROC", 2))


def _quiet():
    fd = os.open(os.devnull, os.O_WRONLY); os.dup2(fd, 1); os.dup2(fd, 2)


def solve(kw):
    tag = kw.pop("_tag", None)
    best = None
    for s in (None, 1, 2, 3, 4):
        try:
            r = m.build_and_solve(m.default_cfg(seed=s, **kw))
        except Exception:
            continue
        if r["ok"] and (best is None or r["profit"] > best["profit"]):
            best = r
    if best is None:
        return dict(ok=False, tag=tag, profit=-np.inf, profit_with_labor=-np.inf)
    best["tag"] = tag
    return best


def run(jobs):
    with Pool(NPROC, initializer=_quiet) as pl:
        return pl.map(solve, jobs)


def best_mp(extra, camps):
    jobs = [dict(extra, mode="MP", campaign=None, _tag="SPC")] + [dict(extra, mode="MP", campaign=list(c), _tag=c) for c in camps]
    rs = run(jobs)
    return rs


if __name__ == "__main__":
    t0 = time.time()
    out = {}
    # G1
    spc = solve(dict(mode="MP", campaign=None, _tag="SPC"))
    ratio = spc["prod"]["A"]["Nb"] / spc["prod"]["B"]["Nb"]
    cands = m.candidate_campaigns(ratio, max_len=6)
    chosen = [c for c, r in cands[:10]]
    for c in ("AB", "AAB", "ABB"):
        if c not in chosen:
            chosen.append(c)
    rs = run([dict(mode="MP", campaign=list(c), _tag=c) for c in chosen])
    out["G1"] = dict(spc=spc, ratio=ratio, cands=[(c, r) for c, r in cands[:20]], results=rs)
    okr = [r for r in rs if r.get("ok")]
    bestc = max(okr, key=lambda r: r["profit"])
    print("G1 ratio", round(ratio, 2), "SPC", round(spc["profit"]), "best", bestc["campaign"], round(bestc["profit"]), flush=True)
    top = [r["campaign"] for r in sorted(okr, key=lambda r: -r["profit"])[:4]]
    # G2
    mc = solve(dict(mode="MC", _tag="MC"))
    out["G2"] = dict(MC=mc, MP=bestc, SPC=spc)
    print("G2 MC", round(mc["profit"]), "MP", round(bestc["profit"]), "con MO:", round(mc["profit_with_labor"]), round(bestc["profit_with_labor"]), flush=True)
    # G3
    scales = [0.5, 1.0, 2.0, 4.0]
    g3 = []
    for sc in scales:
        rmp = best_mp(dict(scale=sc, E_cap=60 * sc, St_cap=0.25 * sc), top)
        bmp = max([r for r in rmp if r.get("ok")], key=lambda r: r["profit"])
        rmc = solve(dict(mode="MC", scale=sc, E_cap=60 * sc, St_cap=0.25 * sc, _tag=("MC", sc)))
        g3.append(dict(scale=sc, MP=bmp, MC=rmc))
        print("G3 sc", sc, "MP", bmp["campaign"], round(bmp["profit"]), "MC", round(rmc["profit"]), flush=True)
    out["G3"] = g3
    # G4: capacidad de la isla energética
    g4 = []
    for Ecap in (0.0, 20.0, 40.0, 60.0, 90.0, 120.0):
        rr = run([dict(mode="MC", E_cap=Ecap, _tag=("MC", Ecap)), dict(mode="MP", campaign=list(bestc["campaign"]), E_cap=Ecap, _tag=("MP", Ecap))])
        g4.append(dict(E_cap=Ecap, MC=rr[0], MP=rr[1]))
        print("G4", Ecap, round(rr[0]["profit"]), round(rr[1]["profit"]), flush=True)
    out["G4"] = g4
    # G5
    g5 = []
    for shifts in (3.0, 4.2):
        rr = run([dict(mode="MC", labor_in_obj=True, shifts=shifts, _tag=("MC", shifts)),
                  dict(mode="MP", campaign=list(bestc["campaign"]), labor_in_obj=True, shifts=shifts, _tag=("MP", shifts))])
        g5.append(dict(shifts=shifts, MC=rr[0], MP=rr[1]))
        print("G5", shifts, round(rr[0]["profit"]), round(rr[1]["profit"]), flush=True)
    out["G5"] = g5
    json.dump(out, open(f"{RES}/m34_all.json", "w"), default=float)
    print("M34 total", round(time.time() - t0), "s")
