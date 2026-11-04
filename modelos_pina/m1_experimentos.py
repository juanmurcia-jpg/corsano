"""
Experimentos del Modelo 1 (superestructura NLP de Corsano adaptada al tren de vino de piña).

E1 validación de la discretización trapezoidal frente a LSODA (análogo a la Fig. 2 de Corsano 2004)
E2 identificabilidad práctica de la cinética con un solo punto final (Murcia Palacios 2013)
E3 caso base con multiarranque (no convexidad; óptimos locales)
E4 restricción de tiempo de llenado (oxidación del mosto, tesis §4.2.4) -> costo de la protección
E5 mapa de estructuras vs exponente de costo b y escala de producción (Corsano 2006a, ej. 3)
E6 jerárquico (cadena actual de la tesis) vs simultáneo (Corsano) -> valor de la simultaneidad
E7 NLP-superestructura vs MINLP (Bonmin) con número de unidades entero (Corsano 2006a, §5)
E8 sensibilidad global de Sobol sobre el TAC óptimo
"""
import json, os, sys, time, warnings
import numpy as np
from multiprocessing import Pool
import params as p
import kinetics as kn
import m1_superestructura_vino as m1

RES = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RES, exist_ok=True)
NPROC = 4


def _quiet():
    # silencia el banner de Ipopt / avisos de CasADi en los procesos hijos
    fd = os.open(os.devnull, os.O_WRONLY); os.dup2(fd, 1); os.dup2(fd, 2)


def solve_cfg(kw):
    cfg = m1.default_cfg(**kw)
    try:
        r = m1.build_and_solve(cfg)
    except Exception as e:  # pragma: no cover
        return dict(ok=False, err=str(e), TAC=np.inf, kw={k: v for k, v in kw.items() if k != "kin"})
    r["label"] = m1.structure_label(r)
    r["kw"] = {k: v for k, v in kw.items() if k not in ("kin", "kin_prop")}
    return r


def best_of(results):
    ok = [r for r in results if r.get("ok")]
    return min(ok, key=lambda r: r["TAC"]) if ok else min(results, key=lambda r: r["TAC"])


def pool_map(jobs):
    with Pool(NPROC, initializer=_quiet) as pl:
        return pl.map(solve_cfg, jobs)


def multistart_jobs(base, seeds):
    return [dict(base, seed=s) for s in seeds] + [dict(base, seed=None)]


def slim(r):
    keep = ("ok", "status", "TAC", "capex_ann", "opex", "TL", "cpu", "iters", "nvar", "ncon", "active", "label", "kw")
    return {k: r.get(k) for k in keep}


# ------------------------------------------------------------------------------------------------
def E1_E2():
    out = {}
    k = kn.KIN_WINE
    t, y = kn.simulate_wine(k, p.X0_REF, p.S_JUICE, T=p.T_REF)
    out["lsoda"] = dict(t=t.tolist(), X=y[0].tolist(), S=y[1].tolist(), P=y[2].tolist())
    out["trap"] = {}
    for N in (3, 5, 10, 15, 30):
        tt, yy = kn.trapezoid_wine(k, p.X0_REF, p.S_JUICE, p.T_REF, N)
        out["trap"][N] = dict(t=tt.tolist(), X=yy[0].tolist(), S=yy[1].tolist(), P=yy[2].tolist())
    # E2: superficie S(12.5 h) en (mu_max, X0) y (mu_max, Pmax)
    mus = np.linspace(0.2, 0.8, 41); X0s = np.geomspace(0.05, 2.0, 41)
    grid = np.zeros((len(X0s), len(mus)))
    for i, X0 in enumerate(X0s):
        for j, mu in enumerate(mus):
            kk = dict(k, mu_max=mu)
            grid[i, j] = kn.simulate_wine(kk, X0, p.S_JUICE, T=p.T_REF, n=3)[1][1, -1]
    Pm = np.linspace(75, 130, 31); grid2 = np.zeros((len(Pm), len(mus)))
    for i, pm in enumerate(Pm):
        for j, mu in enumerate(mus):
            kk = dict(k, mu_max=mu, Pmax=pm)
            grid2[i, j] = kn.simulate_wine(kk, p.X0_REF, p.S_JUICE, T=p.T_REF, n=3)[1][1, -1]
    out["ident"] = dict(mu=mus.tolist(), X0=X0s.tolist(), S=grid.tolist(), Pmax=Pm.tolist(), S2=grid2.tolist())
    # curva de calibración mu_max(X0) que reproduce exactamente el ensayo
    curve = []
    for X0 in np.geomspace(0.05, 2.0, 15):
        curve.append((X0, kn.calibrate_mu(X0=X0)["mu_max"]))
    out["ident"]["curve"] = curve
    # consecuencia de diseño: tiempo para S=4 g/L a X0 de diseño (2 g/L, típico de pie de cuba) según el par calibrado
    cons = []
    for X0c, muc in curve:
        kk = dict(k, mu_max=muc)
        tt, yy = kn.simulate_wine(kk, 2.0, p.S_JUICE, T=40, n=4001)
        idx = np.argmax(yy[1] <= p.S_RES_MAX)
        cons.append((X0c, muc, float(tt[idx])))
    out["ident"]["design_time_at_X0_2"] = cons
    json.dump(out, open(f"{RES}/m1_E1E2.json", "w"))
    print("E1/E2 listo")


def E3():
    rs = pool_map(multistart_jobs({}, range(24)))
    best = best_of(rs)
    json.dump(dict(all=[slim(r) for r in rs], best=best), open(f"{RES}/m1_E3.json", "w"))
    print("E3 best", round(best["TAC"]), best["label"])


def E4():
    taus = [12.5, 9, 7, 5, 4, 3, 2, 1.5, 1.0]
    jobs = []
    for tau in taus:
        jobs += multistart_jobs(dict(tau_fill=tau), range(8))
    rs = pool_map(jobs)
    out = []
    for tau in taus:
        b = best_of([r for r in rs if r["kw"]["tau_fill"] == tau])
        out.append(dict(tau=tau, **slim(b)))
        print("tau", tau, round(b["TAC"]), b["label"])
    json.dump(out, open(f"{RES}/m1_E4.json", "w"))


def E5():
    bs = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    scales = [0.5, 1.0, 2.0, 4.0]
    jobs = []
    for b in bs:
        for sc in scales:
            jobs += multistart_jobs(dict(b=b, PR=p.PR_ETOH * sc), range(5))
    rs = pool_map(jobs)
    out = []
    for b in bs:
        for sc in scales:
            sel = [r for r in rs if abs(r["kw"]["b"] - b) < 1e-9 and abs(r["kw"]["PR"] - p.PR_ETOH * sc) < 1e-6]
            bb = best_of(sel)
            out.append(dict(b=b, scale=sc, **slim(bb)))
            print("b", b, "sc", sc, round(bb["TAC"]), bb["label"])
    json.dump(out, open(f"{RES}/m1_E5.json", "w"))


def E6():
    """Jerárquico: la cinética fija T2=12.5 h y X0=0.2 g/L (LSA directa, sin propagación) y luego se dimensiona.
    Intermedio: se permite propagación pero T2 queda fijo en 12.5 h.
    Simultáneo: Corsano (todo libre)."""
    cases = {
        "jerarquico": dict(allow_prop=False, fix_T2=12.5, fix_X0=0.2, op2=[(1,), (2,), (3,), (4,), (6,), (8,), (12,)]),
        "intermedio": dict(fix_T2=12.5, op2=[(1,), (2,), (3,), (4,), (6,), (8,), (12,)]),
        "simultaneo": dict(),
    }
    out = {}
    for tau in (12.5, 3.0, 1.0):
        out[tau] = {}
        for name, kw in cases.items():
            if "op2" in kw:   # sólo alternativas capaces de cumplir T2=12.5 h con TL<=tau
                kw = dict(kw, op2=[a for a in kw["op2"] if a[0] * tau >= 12.5 - 1e-9])
                if not kw["op2"]:
                    out[tau][name] = dict(ok=False, TAC=None, label="infactible (requiere > 12 unidades)", active=[])
                    print("E6", tau, name, "INFACTIBLE"); continue
            rs = pool_map(multistart_jobs(dict(kw, tau_fill=tau), range(8)))
            b = best_of(rs)
            out[tau][name] = slim(b)
            if not b.get("ok"):
                out[tau][name] = dict(ok=False, TAC=None, label="infactible", active=[])
                print("E6", tau, name, "INFACTIBLE"); continue
            if not np.isfinite(b.get("TAC", np.inf)) or not b.get("ok"):
                out[tau][name] = dict(ok=False, TAC=None, label="infactible", active=[])
                print("E6", tau, name, "INFACTIBLE")
                continue
            print("E6", tau, name, round(b["TAC"]), b["label"])
    json.dump(out, open(f"{RES}/m1_E6.json", "w"))


def E7():
    rows = []
    # NLP superestructura (multiarranque) restringida a una etapa por operación para comparar como en Corsano 2006a §5
    for tau in (12.5, 3.0):
        t0 = time.time()
        rs = pool_map(multistart_jobs(dict(tau_fill=tau, op1=[(1,), (2,)], op2=[(1,), (2,), (3,), (4,), (6,), (8,), (12,)]), range(8)))
        b = best_of(rs)
        rows.append(dict(metodo="NLP superestructura (sin binarias)", tau=tau, **slim(b), cpu_total=sum(r["cpu"] for r in rs)))
        for alg in ("B-BB", "B-OA"):
            r = solve_cfg(dict(tau_fill=tau, op1=[(1,)], op2=[(1,)], integer_M=True, bonmin_alg=alg))
            r["Ms"] = [u["M"] for u in r["units"]]
            rows.append(dict(metodo=f"MINLP Bonmin {alg} (M entero)", tau=tau, **slim(r), cpu_total=r["cpu"], Ms=r["Ms"]))
            print("E7", tau, alg, r["ok"], round(r["TAC"]), r["Ms"])
    json.dump(rows, open(f"{RES}/m1_E7.json", "w"))


def _sobol_job(x):
    names, vals = x
    kin = dict(kn.KIN_WINE)
    kw = {}
    for n_, v in zip(names, vals):
        if n_ in ("mu_max", "Pmax", "Yps"):
            kin[n_] = v
        elif n_ == "A_rel":
            kw["A"] = p.A_FERM * v; kw["A_prop"] = p.A_PROP * v
        else:
            kw[n_] = v
    kw["kin"] = kin
    best = None
    for s in (None, 1):
        r = solve_cfg(dict(kw, seed=s))
        if r.get("ok") and (best is None or r["TAC"] < best["TAC"]):
            best = r
    if best is None:
        return dict(TAC=np.nan, TL=np.nan, ncap=np.nan)
    nunits = sum(M for (op, alt, st, M, V, T) in best["active"] if op == "ferm")
    return dict(TAC=best["TAC"], TL=best["TL"], nferm=nunits, capfrac=best["capex_ann"] / best["TAC"])


def E8(N=64):
    from SALib.sample import saltelli
    from SALib.analyze import sobol
    mu0 = kn.KIN_WINE["mu_max"]
    problem = dict(num_vars=8,
                   names=["mu_max", "Pmax", "Yps", "c_juice", "c_ady", "A_rel", "b", "c_elec"],
                   bounds=[[0.75 * mu0, 1.25 * mu0], [80, 110], [0.38, 0.45], [20, 60], [8, 25], [0.7, 1.3],
                           [0.5, 0.7], [0.15, 0.6]])
    X = saltelli.sample(problem, N, calc_second_order=False)
    with Pool(NPROC, initializer=_quiet) as pl:
        Y = pl.map(_sobol_job, [(problem["names"], x) for x in X])
    tac = np.array([y["TAC"] for y in Y])
    nan = np.isnan(tac)
    if nan.any():
        tac[nan] = np.nanmean(tac)
    Si = sobol.analyze(problem, tac, calc_second_order=False)
    out = dict(problem=problem, X=X.tolist(), Y=Y, S1=Si["S1"].tolist(), ST=Si["ST"].tolist(),
               S1_conf=Si["S1_conf"].tolist(), ST_conf=Si["ST_conf"].tolist(), n_fail=int(nan.sum()))
    json.dump(out, open(f"{RES}/m1_E8.json", "w"), default=float)
    print("E8 S1", np.round(Si["S1"], 3), "ST", np.round(Si["ST"], 3), "fallos", nan.sum())


if __name__ == "__main__":
    todo = sys.argv[1:] or ["E1", "E3", "E4", "E5", "E6", "E7", "E8"]
    for e in todo:
        t0 = time.time()
        {"E1": E1_E2, "E3": E3, "E4": E4, "E5": E5, "E6": E6, "E7": E7, "E8": E8}[e]()
        print(e, f"{time.time() - t0:.0f}s", flush=True)
