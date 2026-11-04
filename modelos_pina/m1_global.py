"""
Certificación global de un subproblema del Modelo 1 con SCIP (ramificación espacial, PySCIPOpt).

Subproblema: una etapa de fermentación con M ∈ {1..12} unidades fuera de fase (entero), inóculo directo de LSA
X0 (continuo), tiempo de fermentación T, tiempo de ciclo TL <= tau, volumen V; cinética trapezoidal con N nodos.
El mismo problema discretizado se resuelve con: (a) SCIP global, (b) Bonmin B-BB y B-OA, (c) IPOPT con
enumeración de M y multiarranque. Así se mide si los solvers locales encuentran el óptimo global del
mismo modelo (la crítica de la tesis §6.10 a CONOPT).
"""
import json, os, time
import numpy as np
import casadi as ca
from pyscipopt import Model, quicksum
import params as p
from kinetics import KIN_WINE

K = KIN_WINE
N = 10
RES = os.path.join(os.path.dirname(__file__), "results")
LB = dict(V=0.3, T=2.0, TL=0.3, X0=0.05)
UB = dict(V=200.0, T=60.0, X0=3.0)


def scip_solve(tau, tlim=900):
    m = Model("m1_global")
    m.hideOutput()
    M = m.addVar("M", vtype="I", lb=1, ub=12)
    V = m.addVar("V", lb=LB["V"], ub=UB["V"]); T = m.addVar("T", lb=LB["T"], ub=UB["T"])
    TL = m.addVar("TL", lb=LB["TL"], ub=tau); nb = m.addVar("nb", lb=p.H / tau, ub=p.H / LB["TL"])
    X0 = m.addVar("X0", lb=LB["X0"], ub=UB["X0"]); h = m.addVar("h", lb=LB["T"] / (N - 1), ub=UB["T"] / (N - 1))
    X = [m.addVar(f"X{i}", lb=0, ub=25) for i in range(N)]
    S = [m.addVar(f"S{i}", lb=0, ub=p.S_JUICE) for i in range(N)]
    P = [m.addVar(f"P{i}", lb=0, ub=0.98 * K["Pmax"]) for i in range(N)]
    mu = [m.addVar(f"mu{i}", lb=0, ub=K["mu_max"]) for i in range(N)]
    cap = m.addVar("cap", lb=0); Vb = m.addVar("Vb", lb=0)
    m.addCons(h * (N - 1) == T)
    m.addCons(nb * TL == p.H)
    m.addCons(X[0] == X0); m.addCons(S[0] == p.S_JUICE); m.addCons(P[0] == 0)
    for i in range(N):
        m.addCons(mu[i] * (K["Ks"] + S[i]) == K["mu_max"] * S[i] * (1 - P[i] / K["Pmax"]))
    for i in range(N - 1):
        g0 = mu[i] * X[i]; g1 = mu[i + 1] * X[i + 1]
        m.addCons(X[i + 1] == X[i] + h / 2 * (g0 - K["kd"] * X[i] + g1 - K["kd"] * X[i + 1]))
        m.addCons(S[i + 1] == S[i] - h / 2 * (g0 + g1) / K["Yxs"])
        m.addCons(P[i + 1] == P[i] + h / 2 * K["Yps"] * (g0 + g1) / K["Yxs"])
    m.addCons(T <= M * TL)
    m.addCons(P[-1] * V >= p.PR_ETOH * TL)
    m.addCons(S[-1] <= p.S_RES_MAX)
    m.addCons(Vb == V ** p.B_FERM)
    obj = p.CCF * p.A_FERM * M * Vb + nb * (p.C_JUICE * V + p.C_ADY * X0 * V)
    z = m.addVar("z", lb=0)
    m.addCons(z >= obj / 1e5)
    m.setObjective(z, "minimize")
    m.setParam("limits/time", tlim)
    m.setParam("limits/gap", 1e-4)
    t0 = time.time()
    m.optimize()
    st = m.getStatus()
    out = dict(method="SCIP global", tau=tau, status=st, cpu=time.time() - t0, gap=m.getGap(),
               dual_bound=m.getDualbound() * 1e5)
    if m.getNSols() > 0:
        out.update(TAC=m.getObjVal() * 1e5, M=round(m.getVal(M)), V=m.getVal(V), T=m.getVal(T), TL=m.getVal(TL),
                   X0=m.getVal(X0))
    return out


def casadi_model(tau, solver, Mfix=None, seed=None, alg="B-BB"):
    opti = ca.Opti()
    rng = np.random.default_rng(seed)
    r = (lambda: 0.5 + rng.random()) if seed is not None else (lambda: 1.0)
    M = opti.variable() if Mfix is None else Mfix
    if Mfix is None:
        opti.set_domain(M, "integer"); opti.subject_to(opti.bounded(1, M, 12)); opti.set_initial(M, 1 + int(11 * rng.random()) if seed is not None else 1)
    V, T, TL, X0 = opti.variable(), opti.variable(), opti.variable(), opti.variable()
    X, S, P = opti.variable(N), opti.variable(N), opti.variable(N)
    opti.subject_to(opti.bounded(LB["V"], V, UB["V"])); opti.subject_to(opti.bounded(LB["T"], T, UB["T"]))
    opti.subject_to(opti.bounded(LB["TL"], TL, tau)); opti.subject_to(opti.bounded(LB["X0"], X0, UB["X0"]))
    opti.subject_to(X >= 0); opti.subject_to(S >= 0); opti.subject_to(P >= 0); opti.subject_to(P <= 0.98 * K["Pmax"])
    opti.subject_to(X[0] == X0); opti.subject_to(S[0] == p.S_JUICE); opti.subject_to(P[0] == 0)
    h = T / (N - 1)
    f = lambda x, s, pp: (K["mu_max"] * s / (K["Ks"] + s) * (1 - pp / K["Pmax"]))
    for i in range(N - 1):
        g0 = f(X[i], S[i], P[i]) * X[i]; g1 = f(X[i + 1], S[i + 1], P[i + 1]) * X[i + 1]
        opti.subject_to(X[i + 1] == X[i] + h / 2 * (g0 - K["kd"] * X[i] + g1 - K["kd"] * X[i + 1]))
        opti.subject_to(S[i + 1] == S[i] - h / 2 * (g0 + g1) / K["Yxs"])
        opti.subject_to(P[i + 1] == P[i] + h / 2 * K["Yps"] * (g0 + g1) / K["Yxs"])
    opti.subject_to(T <= M * TL); opti.subject_to(P[-1] * V >= p.PR_ETOH * TL); opti.subject_to(S[-1] <= p.S_RES_MAX)
    TAC = p.CCF * p.A_FERM * M * V ** p.B_FERM + p.H / TL * (p.C_JUICE * V + p.C_ADY * X0 * V)
    opti.minimize(TAC / 1e5)
    opti.set_initial(V, 10 * r()); opti.set_initial(T, 10 * r()); opti.set_initial(TL, min(tau, 8) * r() * 0.6)
    opti.set_initial(X0, 0.5 * r()); opti.set_initial(X, np.linspace(0.5, 12, N)); opti.set_initial(S, np.linspace(150, 3, N))
    opti.set_initial(P, np.linspace(0, 64, N))
    if solver == "bonmin":
        opti.solver("bonmin", {"print_time": 0, "bonmin.print_level": 0, "bonmin.algorithm": alg})
    else:
        opti.solver("ipopt", {"print_time": 0, "ipopt.print_level": 0})
    t0 = time.time()
    try:
        sol = opti.solve(); ok = True
    except RuntimeError:
        sol = opti.debug; ok = False
    return dict(ok=ok, TAC=float(sol.value(TAC)), M=(round(float(sol.value(M))) if Mfix is None else Mfix),
                V=float(sol.value(V)), T=float(sol.value(T)), TL=float(sol.value(TL)), X0=float(sol.value(X0)),
                cpu=time.time() - t0)


if __name__ == "__main__":
    fd = os.open(os.devnull, os.O_WRONLY)
    rows = []
    for tau in (12.5, 3.0):
        g = scip_solve(tau); rows.append(g); print(g, flush=True)
        for alg in ("B-BB", "B-OA"):
            for s in (None, 1, 2):
                r = casadi_model(tau, "bonmin", seed=s, alg=alg); r.update(method=f"Bonmin {alg}", tau=tau, seed=s); rows.append(r)
                print(r["method"], s, r["ok"], round(r["TAC"]), r["M"], flush=True)
        best_e = None
        for Mf in range(1, 13):
            for s in (None, 1, 2, 3):
                r = casadi_model(tau, "ipopt", Mfix=Mf, seed=s)
                if r["ok"] and (best_e is None or r["TAC"] < best_e["TAC"]):
                    best_e = r
        best_e.update(method="IPOPT + enumeración de M (48 NLP)", tau=tau); rows.append(best_e)
        print("enum", round(best_e["TAC"]), best_e["M"], flush=True)
    json.dump(rows, open(f"{RES}/m1_global.json", "w"), default=float)
