"""
Programación estocástica en dos etapas (Grossmann 2021, cap. 14) para §6.7 de la tesis.

Etapa 1 (aquí y ahora, d): líneas y tamaños de catálogo z_lk, frente de pelado zF_k.
Etapa 2 (esperar y ver, z(θ)): operación mensual x_lms, compra de fruta F_ms, GLP y diésel, por escenario θ_s.
Equivalente determinista (ec. 14.19):  max  −Σ_lk A_lk z_lk + Σ_s p_s · Q_s(z, x_s)
Riesgo (tesis §6.7):  max (1−λ)·E[Q] + λ·CVaR_β,  CVaR_β = ζ − (1/(1−β)) Σ_s p_s u_s,  u_s ≥ ζ − Π_s, u_s ≥ 0.
Indicadores (Birge y Louveaux; Grossmann §14.1): RP, EV, EEV, VSS = RP − EEV, WS, EVPI = WS − RP.
"""
import json, os, itertools, time
import numpy as np
from pyscipopt import Model, quicksum
import capacidad as cp
import tea_lineas as tl
import tea_burk as tb
import planificacion_milp as pm

RES = os.path.join(os.path.dirname(__file__), "results")
TAB = json.load(open(f"{RES}/milp_options.json"))
LINES = list(pm.LINES)
B1 = cp.full_balance(1.0)
SH = dict(pulp=B1["pulp_t"], peel=B1["peel_t"], core=B1["core_t"], crown=B1["crown_t"])
WPP = B1["wine_m3"] / B1["pulp_t"]; JPP = B1["peel_juice_t"] / B1["peel_t"]
FLOUR_PP = B1["flour_t"] / B1["peel_t"]; BROM_PC = B1["bromelain_kg"] / B1["core_t"]; POWD_PC = B1["powder_t"] / B1["core_t"]
SUPPLY0 = 6146.0

SUP_F = [(0.7, 0.25), (1.0, 0.50), (1.3, 0.25)]
WINE_P = [(2200.0, 0.30), (3000.0, 0.40), (4000.0, 0.30)]
FLOUR_P = [(8000.0, 0.25), (12000.0, 0.50), (16000.0, 0.25)]
SCEN = [dict(sup=a, wp=b, fp=c, p=pa * pb * pc) for (a, pa), (b, pb), (c, pc) in itertools.product(SUP_F, WINE_P, FLOUR_P)]


def mean(l, key):
    return float(np.mean([o[key] for o in TAB[l]]))


def stage2(m, z, zF, s, tag):
    """Restricciones y beneficio del escenario s (COP/año, antes de impuestos, sin anualidades de capital)."""
    months = range(12)
    sup = SUPPLY0 * s["sup"] * pm.SEASON / 12.0
    x = {(l, t): m.addVar(lb=0, name=f"x_{tag}_{l}_{t}") for l in LINES for t in months}
    F = {t: m.addVar(lb=0, ub=sup[t], name=f"F_{tag}_{t}") for t in months}
    LPG = {t: m.addVar(lb=0) for t in months}; DIE = {t: m.addVar(lb=0) for t in months}
    nk = {l: len(TAB[l]) for l in LINES}
    for l in LINES:
        for t in months:
            m.addCons(x[l, t] <= quicksum(TAB[l][k]["cap"] / 12.0 * z[l, k] for k in range(nk[l])))
    for t in months:
        m.addCons(F[t] <= quicksum(pm.SCALES[k] / 12.0 * zF[k] for k in zF))
        m.addCons(x["vino", t] <= SH["pulp"] * F[t]); m.addCons(x["harina", t] <= SH["peel"] * F[t])
        m.addCons(x["bromelaina", t] <= SH["core"] * F[t])
        m.addCons(x["caldera", t] + x["gasificador", t] <= SH["crown"] * F[t])
        m.addCons(x["vinagre", t] <= WPP * x["vino", t]); m.addCons(x["etanol", t] <= JPP * x["harina", t])
        m.addCons(LPG[t] >= quicksum(mean(l, "heat_per") * x[l, t] for l in LINES) - mean("caldera", "heat_out_per") * x["caldera", t])
        m.addCons(DIE[t] >= quicksum(mean(l, "elec_per") * x[l, t] for l in LINES) - mean("gasificador", "elec_out_per") * x["gasificador", t])
    pr = 0
    for t in months:
        pr += 0.95 * s["wp"] * 1000 * (WPP * x["vino", t] - x["vinagre", t]) - mean("vino", "var_per") * x["vino", t]
        pr += (0.95 * 1000 * (FLOUR_PP * s["fp"] + JPP * tl.M("jugo_cascara_kg")) - mean("harina", "var_per")) * x["harina", t]
        pr += (0.95 * (BROM_PC * tl.M("bromelaina_kg") + POWD_PC * 1000 * tl.M("polvo_kg")) - mean("bromelaina", "var_per")) * x["bromelaina", t]
        for l in ("vinagre", "etanol"):
            pr += (mean(l, "rev_per") - mean(l, "var_per")) * x[l, t]
        pr -= mean("caldera", "var_per") * x["caldera", t] + mean("gasificador", "var_per") * x["gasificador", t]
        pr -= tl.M("jugo_cascara_kg") * 1000 * 0.95 * x["etanol", t]
        pr -= tl.M("fruta_kg") * 1000 * F[t]
        pr -= pm.COMPOST_COP_kg * 1000 * (F[t] - x["vino", t] - x["harina", t] - x["bromelaina", t] - x["caldera", t] - x["gasificador", t])
        pr -= tb.COMMON["calor_COP_MJ"] * LPG[t] + tb.COMMON["elec_COP_kWh"] * DIE[t]
    return pr / 1e6, x, F                                         # MM COP


def build(scens, lam=0.0, beta=0.9, fix=None, time_limit=300):
    m = Model("SP"); m.hideOutput()
    nk = {l: len(TAB[l]) for l in LINES}
    z = {(l, k): m.addVar(vtype="B") for l in LINES for k in range(nk[l])}
    zF = {k: m.addVar(vtype="B") for k in range(len(pm.SCALES))}
    Z = lambda l: quicksum(z[l, k] for k in range(nk[l]))
    for l in LINES:
        m.addCons(Z(l) <= 1)
    m.addCons(quicksum(zF.values()) <= 1)
    for l in ("vino", "bromelaina", "harina"):
        m.addCons(Z(l) <= quicksum(zF.values()))
    m.addCons(Z("vinagre") <= Z("vino")); m.addCons(Z("etanol") <= Z("harina"))
    fs = TAB["_front_share"]
    ann = quicksum(TAB[l][k]["ann"] * ((1 - fs[k]) if l == "vino" else 1.0) * z[l, k] for l in LINES for k in range(nk[l])) \
          + quicksum(fs[k] * TAB["vino"][k]["ann"] * zF[k] for k in zF)
    ann = ann / 1e6
    if fix is not None:
        for (l, k), v in fix["z"].items():
            m.addCons(z[l, k] == v)
        for k, v in fix["zF"].items():
            m.addCons(zF[k] == v)
    Pi = {}
    for q, s in enumerate(scens):
        pr, _, _ = stage2(m, z, zF, s, f"s{q}")
        pv = m.addVar(lb=-1e5, ub=1e5, name=f"Pi_{q}")
        m.addCons(pv == pr - ann)
        Pi[q] = pv
    psum = sum(s["p"] for s in scens)
    E = quicksum(s["p"] / psum * Pi[q] for q, s in enumerate(scens))
    zeta = m.addVar(lb=-1e5, ub=1e5); u = {q: m.addVar(lb=0) for q in Pi}
    for q in Pi:
        m.addCons(u[q] >= zeta - Pi[q])
    CVaR = zeta - quicksum(s["p"] / psum * u[q] for q, s in enumerate(scens)) / (1 - beta)
    m.setObjective((1 - lam) * E + lam * CVaR, "maximize")
    m.setParam("limits/time", time_limit); m.setParam("numerics/feastol", 1e-6)
    m.optimize()
    zs = {(l, k): round(m.getVal(z[l, k])) for (l, k) in z}; zFs = {k: round(m.getVal(zF[k])) for k in zF}
    sel = {l: TAB[l][k]["scale"] for (l, k), v in zs.items() if v}
    pis = [m.getVal(Pi[q]) for q in Pi]
    pis = [x_ * 1e6 for x_ in pis]
    return dict(status=m.getStatus(), gap=m.getGap(), E=m.getVal(E) * 1e6, CVaR=m.getVal(CVaR) * 1e6, Pi=pis, sel=sel,
                front=[pm.SCALES[k] for k, v in zFs.items() if v], fix=dict(z=zs, zF=zFs),
                CVaR_post=cvar_post(pis, [s["p"] for s in scens], beta))


def cvar_post(pis, ps, beta=0.9):
    """CVaR_β del beneficio (cola inferior 1−β) calculado a posteriori sobre la distribución discreta."""
    o = np.argsort(pis); pis = np.asarray(pis)[o]; ps = np.asarray(ps)[o] / np.sum(ps)
    tail, acc, val = 1 - beta, 0.0, 0.0
    for v_, p_ in zip(pis, ps):
        take = min(p_, tail - acc)
        if take <= 0:
            break
        val += take * v_; acc += take
    return val / tail


if __name__ == "__main__":
    t0 = time.time(); out = {}
    RP = build(SCEN); out["RP"] = RP
    print("RP", RP["status"], f"E={RP['E']/1e6:,.0f} MM", RP["sel"], RP["front"], flush=True)
    EVs = [dict(sup=sum(s["sup"] * s["p"] for s in SCEN), wp=sum(s["wp"] * s["p"] for s in SCEN), fp=sum(s["fp"] * s["p"] for s in SCEN), p=1.0)]
    EV = build(EVs); out["EV"] = EV
    EEV = build(SCEN, fix=EV["fix"]); out["EEV"] = EEV
    print("EV", f"{EV['E']/1e6:,.0f}", EV["sel"], "EEV", f"{EEV['E']/1e6:,.0f}", flush=True)
    WS = 0.0; ws_list = []
    for s in SCEN:
        r = build([dict(s, p=1.0)]); WS += s["p"] * r["E"]; ws_list.append(dict(s, obj=r["E"], sel=r["sel"]))
    out["WS"] = WS; out["WS_list"] = ws_list
    out["VSS"] = RP["E"] - EEV["E"]; out["EVPI"] = WS - RP["E"]
    print(f"WS={WS/1e6:,.0f}  VSS={out['VSS']/1e6:,.0f}  EVPI={out['EVPI']/1e6:,.0f} MM COP/año", flush=True)
    # frontera media–CVaR
    front = []
    for lam in (0.0, 0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 1.0):
        r = build(SCEN, lam=lam)
        front.append(dict(lam=lam, E=r["E"], CVaR=r["CVaR_post"], sel=r["sel"], Pi=r["Pi"]))
        print("λ", lam, f"E={r['E']/1e6:,.0f}", f"CVaR90={r['CVaR_post']/1e6:,.0f}", r["sel"], flush=True)
    out["frontier"] = front
    out["scenarios"] = SCEN
    for k in ("RP", "EV", "EEV"):
        out[k]["fix"] = dict(z={f"{a}|{b}": v for (a, b), v in out[k]["fix"]["z"].items()}, zF=out[k]["fix"]["zF"])
    json.dump(out, open(f"{RES}/estocastico.json", "w"), default=float)
    print("t", round(time.time() - t0), "s")
