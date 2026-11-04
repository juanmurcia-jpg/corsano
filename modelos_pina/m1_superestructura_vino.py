"""
MODELO 1 — Superestructura NLP sin variables binarias (Corsano et al. 2004; 2006a) para el tren de vino de piña.

Operación 1: propagación aerobia de levadura (alternativas en serie / en paralelo fuera de fase).
Operación 2: fermentación alcohólica del jugo de pulpa (alternativas 1..12 unidades fuera de fase,
             2 etapas en serie, 2x2).
Política de transferencia: espera cero (ZW). Tiempo de ciclo TL >= T_u / M_u  (ec. 5 de 2006a).
Las ODE se discretizan con el método trapezoidal (ec. 8-11 de 2004) dentro del NLP.
Costo: TAC = CCF * sum M * A * V^b + costos operativos (ec. 1 de 2006a; ec. 36 de 2006b).
Como b < 1, la solución óptima lleva a V -> 0 las alternativas no óptimas: no hacen falta binarias.

Adaptaciones a la tesis:
  * datos cinéticos de Murcia Palacios (2013) calibrados en kinetics.py
  * restricción de tiempo de llenado TL <= tau_fill  (riesgo de oxidación del mosto, tesis §4.2.4)
  * especificación de vino seco: azúcar residual de la mezcla <= 4 g/L
  * electricidad de aireación a costo de ZNI (generación diésel)
"""
import time
import numpy as np
import casadi as ca
import params as p
from kinetics import KIN_WINE, rhs_wine, rhs_prop

OP1_ALTS = [(1,), (1, 1), (2,)]                                    # propagación
OP2_ALTS = [(1,), (1, 1), (2,), (3,), (4,), (6,), (8,), (12,), (2, 2)]  # fermentación


def default_cfg(**kw):
    cfg = dict(N=15, b=p.B_FERM, A=p.A_FERM, A_prop=p.A_PROP, PR=p.PR_ETOH, tau_fill=p.TAU_FILL,
               c_juice=p.C_JUICE, c_ady=p.C_ADY, c_elec=p.C_ELEC_ZNI, kin=dict(KIN_WINE),
               kin_prop=dict(p.KIN_PROP), S_juice=p.S_JUICE, Sres=p.S_RES_MAX,
               op1=OP1_ALTS, op2=OP2_ALTS, allow_prop=True, allow_ady_direct=True,
               fix_T2=None, fix_X0=None, seed=None, Vmin=1e-4, integer_M=False, print_level=0)
    cfg.update(kw)
    return cfg


def spow(V, b, eps=1e-8):
    """V^b suave y definido para V<=0 durante las iteraciones (V+ = (V+sqrt(V^2+eps))/2)."""
    Vp = 0.5 * (V + ca.sqrt(V * V + eps))
    return Vp ** b


def _Mvar(opti, cfg, Mmax):
    M = opti.variable()
    opti.set_domain(M, "integer")
    opti.subject_to(opti.bounded(1, M, Mmax))
    opti.set_initial(M, 1)
    return M


def _unit(opti, N, ferment=True):
    u = dict(V=opti.variable(), T=opti.variable(), X=opti.variable(N), S=opti.variable(N))
    if ferment:
        u["P"] = opti.variable(N)
    return u


def build_and_solve(cfg):
    N = cfg["N"]
    kin, kp = cfg["kin"], cfg["kin_prop"]
    opti = ca.Opti()
    TL = opti.variable()
    rng = np.random.default_rng(cfg["seed"])
    units1, units2 = [], []
    cost_cap, juice, water, ady, kwh = 0, 0, 0, 0, 0

    def trap(u, ferment):
        h = u["T"] / (N - 1)
        for i in range(N - 1):
            if ferment:
                f0 = rhs_wine(u["X"][i], u["S"][i], u["P"][i], kin)
                f1 = rhs_wine(u["X"][i + 1], u["S"][i + 1], u["P"][i + 1], kin)
                for s_, k_ in zip(("X", "S", "P"), range(3)):
                    opti.subject_to(u[s_][i + 1] == u[s_][i] + h / 2 * (f0[k_] + f1[k_]))
            else:
                f0 = rhs_prop(u["X"][i], u["S"][i], kp)
                f1 = rhs_prop(u["X"][i + 1], u["S"][i + 1], kp)
                for s_, k_ in zip(("X", "S"), range(2)):
                    opti.subject_to(u[s_][i + 1] == u[s_][i] + h / 2 * (f0[k_] + f1[k_]))

    def bounds(u, M, ferment):
        opti.subject_to(opti.bounded(cfg["Vmin"], u["V"], 400))
        opti.subject_to(opti.bounded(0.05, u["T"], 240))
        opti.subject_to(u["T"] <= M * TL)                       # ZW, fuera de fase
        opti.subject_to(u["X"] >= 0); opti.subject_to(u["S"] >= 0)
        opti.subject_to(u["X"] <= 60); opti.subject_to(u["S"] <= 200)
        if ferment:
            opti.subject_to(u["P"] >= 0); opti.subject_to(u["P"] <= 0.98 * kin["Pmax"])

    # ---------------------------------------------------------------- operación 1: propagación
    Bpool, XB, SB = 0, 0, 0
    if cfg["allow_prop"]:
        for alt in cfg["op1"]:
            prev = None
            for j, M in enumerate(alt):
                u = _unit(opti, N, ferment=False); u["alt"] = alt; u["j"] = j
                u["M"] = _Mvar(opti, cfg, 3) if cfg["integer_M"] else M
                Fj, Fw = opti.variable(), opti.variable()
                opti.subject_to(Fj >= 0); opti.subject_to(Fw >= 0)
                u["Fj"], u["Fw"] = Fj, Fw
                if prev is None:
                    a0 = opti.variable(); opti.subject_to(a0 >= 0); u["ady"] = a0
                    opti.subject_to(u["V"] == Fj + Fw)
                    opti.subject_to(u["X"][0] * u["V"] == a0)
                    opti.subject_to(u["S"][0] * u["V"] == cfg["S_juice"] * Fj)
                    ady += a0
                else:
                    opti.subject_to(u["V"] == prev["V"] + Fj + Fw)
                    opti.subject_to(u["X"][0] * u["V"] == prev["X"][-1] * prev["V"])
                    opti.subject_to(u["S"][0] * u["V"] == prev["S"][-1] * prev["V"] + cfg["S_juice"] * Fj)
                opti.subject_to(u["S"][0] <= p.S0_PROP_MAX)
                trap(u, False); bounds(u, u["M"], False)
                cost_cap += u["M"] * cfg["A_prop"] * spow(u["V"], cfg["b"])
                juice += Fj; water += Fw
                kwh += p.KW_AIR * u["V"] * u["T"]
                units1.append(u); prev = u
            Bpool += prev["V"]; XB += prev["X"][-1] * prev["V"]; SB += prev["S"][-1] * prev["V"]
        Xp, Sp = opti.variable(), opti.variable()
        opti.subject_to(Xp * Bpool == XB); opti.subject_to(Sp * Bpool == SB)   # pool (bilineal)
        opti.subject_to(opti.bounded(0, Xp, 60)); opti.subject_to(opti.bounded(0, Sp, 200))

    # ---------------------------------------------------------------- operación 2: fermentación
    Bin_sum, prodE, sugar_out, vol_out = 0, 0, 0, 0
    for alt in cfg["op2"]:
        prev = None
        for j, M in enumerate(alt):
            u = _unit(opti, N, ferment=True); u["alt"] = alt; u["j"] = j
            u["M"] = _Mvar(opti, cfg, 12) if cfg["integer_M"] else M
            Fj = opti.variable(); opti.subject_to(Fj >= 0); u["Fj"] = Fj
            if prev is None:
                Bin = opti.variable(); opti.subject_to(Bin >= 0); u["Bin"] = Bin
                a2 = opti.variable(); opti.subject_to(a2 >= 0); u["ady"] = a2
                if not cfg["allow_ady_direct"]:
                    opti.subject_to(a2 == 0)
                if not cfg["allow_prop"]:
                    opti.subject_to(Bin == 0)
                    Xin, Sin = 0, 0
                else:
                    Xin, Sin = Xp, Sp
                opti.subject_to(u["V"] == Bin + Fj)
                opti.subject_to(u["X"][0] * u["V"] == Xin * Bin + a2)
                opti.subject_to(u["S"][0] * u["V"] == Sin * Bin + cfg["S_juice"] * Fj)
                opti.subject_to(u["P"][0] == 0)
                Bin_sum += Bin; ady += a2
            else:
                opti.subject_to(u["V"] == prev["V"] + Fj)
                opti.subject_to(u["X"][0] * u["V"] == prev["X"][-1] * prev["V"])
                opti.subject_to(u["S"][0] * u["V"] == prev["S"][-1] * prev["V"] + cfg["S_juice"] * Fj)
                opti.subject_to(u["P"][0] * u["V"] == prev["P"][-1] * prev["V"])
            trap(u, True); bounds(u, u["M"], True)
            if cfg["fix_T2"] is not None:
                opti.subject_to(u["T"] == cfg["fix_T2"])
            if cfg["fix_X0"] is not None and prev is None:
                opti.subject_to(u["X"][0] == cfg["fix_X0"])
            cost_cap += u["M"] * cfg["A"] * spow(u["V"], cfg["b"])
            juice += Fj
            units2.append(u); prev = u
        prodE += prev["P"][-1] * prev["V"]
        sugar_out += prev["S"][-1] * prev["V"]; vol_out += prev["V"]
    if cfg["allow_prop"]:
        opti.subject_to(Bin_sum == Bpool)

    opti.subject_to(prodE >= cfg["PR"] * TL)                     # producción (ec. 3-4 de 2006a)
    opti.subject_to(sugar_out <= cfg["Sres"] * vol_out)          # vino seco (mezcla)
    opti.subject_to(opti.bounded(0.2, TL, cfg["tau_fill"]))     # llenado <= tau (oxidación)

    nb = p.H / TL                                                # lotes/año
    opcost = nb * (cfg["c_juice"] * juice + p.C_WATER * water + cfg["c_ady"] * ady + cfg["c_elec"] * kwh)
    TAC = p.CCF * cost_cap + opcost
    opti.minimize(TAC / 1e5)

    # ---------------------------------------------------------------- inicialización "todas activas"
    TL0 = min(cfg["tau_fill"], 6.0) * (0.7 + 0.6 * rng.random() if cfg["seed"] is not None else 1.0)
    opti.set_initial(TL, TL0)
    for u in units1:
        T0 = (u["M"] if not cfg["integer_M"] else 1) * TL0 * 0.8
        opti.set_initial(u["V"], 0.5 * (1 + rng.random() if cfg["seed"] is not None else 1))
        opti.set_initial(u["T"], T0)
        opti.set_initial(u["X"], np.linspace(0.5, 8, N)); opti.set_initial(u["S"], np.linspace(18, 1, N))
        opti.set_initial(u["Fj"], 0.06); opti.set_initial(u["Fw"], 0.4)
    for u in units2:
        T0 = (u["M"] if not cfg["integer_M"] else 1) * TL0 * 0.8
        V0 = cfg["PR"] * TL0 / 60 / len(cfg["op2"]) * (0.5 + rng.random() if cfg["seed"] is not None else 1)
        opti.set_initial(u["V"], V0); opti.set_initial(u["T"], T0); opti.set_initial(u["Fj"], 0.9 * V0)
        opti.set_initial(u["X"], np.linspace(1, 12, N)); opti.set_initial(u["S"], np.linspace(150, 3, N))
        opti.set_initial(u["P"], np.linspace(0, 62, N))
    if cfg["allow_prop"]:
        opti.set_initial(Xp, 8); opti.set_initial(Sp, 1)

    opts = {"ipopt.print_level": cfg["print_level"], "print_time": 0, "ipopt.max_iter": 3000,
            "ipopt.tol": 1e-7, "ipopt.mu_strategy": "adaptive"}
    if cfg["integer_M"]:
        opti.solver("bonmin", {"print_time": 0, "bonmin.print_level": 0, "bonmin.algorithm": cfg.get("bonmin_alg", "B-BB"),
                               "bonmin.time_limit": 600})
    else:
        opti.solver("ipopt", opts)
    t0 = time.time()
    try:
        sol = opti.solve(); ok = True
    except RuntimeError:
        sol = opti.debug; ok = False
    cpu = time.time() - t0
    stats = opti.stats()
    val = lambda e: float(sol.value(e))
    res = dict(ok=ok, status=stats.get("return_status"), cpu=cpu, iters=stats.get("iter_count"),
               TAC=val(TAC), capex_ann=val(p.CCF * cost_cap), opex=val(opcost), TL=val(TL),
               nvar=opti.nx, ncon=opti.ng, units=[])
    for op, U in (("prop", units1), ("ferm", units2)):
        for u in U:
            d = dict(op=op, alt=str(u["alt"]), stage=u["j"] + 1, M=(val(u["M"]) if cfg["integer_M"] else u["M"]), V=val(u["V"]), T=val(u["T"]),
                     X=np.array(sol.value(u["X"])).tolist(), S=np.array(sol.value(u["S"])).tolist())
            if "P" in u:
                d["P"] = np.array(sol.value(u["P"])).tolist()
            d["Fj"] = val(u["Fj"])
            if "ady" in u:
                d["ady"] = val(u["ady"])
            res["units"].append(d)
    res["active"] = [(d["op"], d["alt"], d["stage"], d["M"], round(d["V"], 3), round(d["T"], 2))
                     for d in res["units"] if d["V"] > 1e-2]
    return res


def structure_label(res):
    ops = {}
    for (op, alt, st, M, V, T) in res["active"]:
        ops.setdefault(op, set()).add(alt)
    s1 = "+".join(sorted(ops.get("prop", []))) or "sin propagación"
    s2 = "+".join(sorted(ops.get("ferm", [])))
    return f"Prop {s1} | Ferm {s2}"


if __name__ == "__main__":
    r = build_and_solve(default_cfg(print_level=0))
    print(r["ok"], r["status"], f"TAC={r['TAC']:.0f}", f"TL={r['TL']:.2f}", f"cpu={r['cpu']:.2f}s", r["nvar"], r["ncon"])
    for a in r["active"]:
        print(a)
    print(structure_label(r))
