"""
Post-proceso riguroso del Modelo 1:
E5b "pulido" del mapa de estructuras: para cada celda (b, escala) se resuelve el NLP restringido a cada
    estructura candidata (problema más pequeño y mejor condicionado) y se toma el mínimo. Elimina óptimos
    locales del NLP completo — equivale a la enumeración que Corsano 2006a §5 hace con MINLP.
E6  rerun (con el filtro de alternativas factibles para T2 fijo).
V1  verificación a posteriori: se re-simula con LSODA la operación óptima del NLP (N=15 trapecios).
"""
import json, os, time, ast
import numpy as np
from multiprocessing import Pool
import params as p
import kinetics as kn
import m1_experimentos as ex

RES = ex.RES


def E5b():
    d = json.load(open(f"{RES}/m1_E5.json"))
    cands = {ast.literal_eval(a) for r in d for (o, a, st, M, V, T) in r["active"] if o == "ferm"}
    cands |= {(1,), (1, 1), (2,), (2, 2), (3,), (1, 1, 1)}
    cands = sorted(cands)
    jobs = []
    for r in d:
        for c in cands:
            for s in (None, 1):
                jobs.append(dict(b=r["b"], PR=p.PR_ETOH * r["scale"], op2=[c], seed=s))
    rs = ex.pool_map(jobs)
    out = []
    for r in d:
        sel = [x for x in rs if x.get("ok") and abs(x["kw"]["b"] - r["b"]) < 1e-9 and abs(x["kw"]["PR"] - p.PR_ETOH * r["scale"]) < 1e-6]
        best = min(sel + ([r] if r.get("ok") else []), key=lambda x: x["TAC"])
        row = dict(b=r["b"], scale=r["scale"], **ex.slim(best))
        row["TAC_full_nlp"] = r["TAC"]; row["label_full_nlp"] = r["label"]
        row["by_structure"] = {str(x["kw"]["op2"][0]): x["TAC"] for x in sel}
        out.append(row)
        print("E5b", r["b"], r["scale"], round(best["TAC"]), best["label"], "| NLP completo", round(r["TAC"]), flush=True)
    json.dump(out, open(f"{RES}/m1_E5b.json", "w"), default=float)


def V1():
    d = json.load(open(f"{RES}/m1_E3.json"))["best"]
    rows = []
    for u in d["units"]:
        if u["V"] < 1e-2 or u["op"] != "ferm":
            continue
        t, y = kn.simulate_wine(kn.KIN_WINE, u["X"][0], u["S"][0], P0=u["P"][0], T=u["T"])
        rows.append(dict(unit=f"{u['alt']}-{u['stage']}", V=u["V"], T=u["T"], P_nlp=u["P"][-1], P_sim=float(y[2, -1]),
                         S_nlp=u["S"][-1], S_sim=float(y[1, -1]), X_nlp=u["X"][-1], X_sim=float(y[0, -1])))
        print("V1", rows[-1])
    json.dump(rows, open(f"{RES}/m1_V1.json", "w"))


if __name__ == "__main__":
    import sys
    for e in sys.argv[1:] or ["V1", "E6", "E5b"]:
        t0 = time.time()
        {"V1": V1, "E6": ex.E6, "E5b": E5b}[e]()
        print(e, round(time.time() - t0), "s", flush=True)
