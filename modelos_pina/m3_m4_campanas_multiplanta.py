"""
MODELOS 3 y 4 — Planta multiproducto con campañas mixtas (Corsano et al. 2007; libro 2009, cap. 4)
                 frente a complejo multiplanta (libro 2009, cap. 5; Corsano et al. 2006c).

Productos derivados (analogía con Torula / Brandy / levadura panadera de Corsano):
   A  vino de piña (jugo de pulpa)          ruta: propagación -> fermentación -> centrífuga -> (envejecimiento)
   C  vinagre, subproducto de A (fracción sigma del lote de vino desviada al acetador)
   B  bioetanol del hub de azúcares          ruta: propagación -> fermentación -> centrífuga -> destilación
Planta madre: fraccionamiento + hub (§4.6) + isla energética de gasificación (cap. 5 de la tesis), que
"produce" electricidad y vapor (recursos producidos), con respaldo diésel (recursos suministrados) y
exportación de electricidad excedente a la microrred local (recurso exportado) — ec. 4.4 del libro.

MP  (multiproducto): A y B comparten propagador, fermentador y centrífuga; política ZW en flow-shop.
    Retardo mínimo entre el inicio de un lote i y el siguiente k:  d_ik >= s_ij + t_ij - s_kj  (etapas compartidas)
    Paso (i) modelo relajado (campañas de un solo producto):  N_A d_AA + N_B d_BB <= H
    Paso (ii)-(iv): campañas mixtas candidatas (AB, AAB, ...) -> un NLP por campaña -> mejor beneficio.
MC  (multiplanta): planta 1 (A + C) y planta 2 (B) con equipos propios; CT_l >= t_j (ec. 4.5); N_l CT_l <= H (4.7).
Las cinéticas (propagación aerobia y fermentación alcohólica) se discretizan por trapecios dentro del NLP.
Simplificación declarada: una unidad por etapa (sin duplicación) para aislar el efecto de compartir equipos.
"""
import time, itertools
import numpy as np
import casadi as ca
import params as p
from kinetics import KIN_WINE, KIN_ACET_CAL

LAB_RULE = dict(ferm=1, semi=1, dist=1)   # Corsano libro p. 77: 1 trabajador por grupo de etapas y por turno


def default_cfg(**kw):
    kB = dict(KIN_WINE); kB.update(Yps=0.46, Pmax=100.0)
    cfg = dict(N=10, b=p.B_FERM, mode="MP", campaign=None, kinA=dict(KIN_WINE), kinB=kB, kinP=dict(p.KIN_PROP),
               S_A=p.S_JUICE, S_B=p.HUB["peel"]["S"], c_A=p.C_JUICE, c_B=p.HUB["peel"]["c"],
               QA=(6000.0, p.WINE_VOL_YR), QB=(150.0, 300.0), QC=(0.0, 1500.0),        # m3, t, m3 por año
               price=dict(p.PRICE), scale=1.0,
               E_cap=60.0, c_E_prod=0.08, c_E_imp=p.C_ELEC_ZNI, q_E_exp=0.20,          # kW, USD/kWh
               St_cap=0.25, c_St_prod=12.0, c_St_imp=45.0,                              # t/h, USD/t
               labor_in_obj=False, P_wine_min=55.0, X0min=0.5, wage=p.WAGE_YR, shifts=3.0, seed=None, print_level=0)
    cfg.update(kw)
    return cfg


def spow(V, b, eps=1e-8):
    return (0.5 * (V + ca.sqrt(V * V + eps))) ** b


def labor(mode):
    if mode == "MP":
        return LAB_RULE["ferm"] + LAB_RULE["semi"] + LAB_RULE["dist"]                 # 3 por turno
    return (LAB_RULE["ferm"] + LAB_RULE["semi"]) + (LAB_RULE["ferm"] + LAB_RULE["semi"] + LAB_RULE["dist"])  # 5


def build_and_solve(cfg):
    N = cfg["N"]; sc = cfg["scale"]
    opti = ca.Opti()
    rng = np.random.default_rng(cfg["seed"])
    rnd = (lambda: 0.7 + 0.6 * rng.random()) if cfg["seed"] is not None else (lambda: 1.0)
    kp = cfg["kinP"]
    prod = {}
    for i, kin, Sfeed in (("A", cfg["kinA"], cfg["S_A"]), ("B", cfg["kinB"], cfg["S_B"])):
        d = dict(B=opti.variable(), Bp=opti.variable(), Tp=opti.variable(), T=opti.variable(), th=opti.variable(),
                 Xp=opti.variable(N), Sp=opti.variable(N), X=opti.variable(N), S=opti.variable(N), P=opti.variable(N),
                 Nb=opti.variable(), Fp=opti.variable(), Fw=opti.variable())
        opti.subject_to(opti.bounded(0.05 * sc, d["B"], 300 * sc)); opti.subject_to(opti.bounded(1e-3, d["Bp"], 0.10 * d["B"]))   # inóculo <= 10 % del lote
        opti.subject_to(opti.bounded(0.5, d["Tp"], 60)); opti.subject_to(opti.bounded(1.0, d["T"], 120))
        opti.subject_to(opti.bounded(0.1, d["th"], 12)); opti.subject_to(opti.bounded(1, d["Nb"], 20000))
        for v in ("Xp", "Sp", "X", "S", "P"):
            opti.subject_to(d[v] >= 0)
        opti.subject_to(d["P"] <= 0.97 * kin["Pmax"])
        # propagación: jugo diluido a S0 = 20 g/L, siembra 0.5 g/L de LSA
        opti.subject_to(d["Fp"] >= 0); opti.subject_to(d["Fw"] >= 0)
        opti.subject_to(d["Bp"] == d["Fp"] + d["Fw"])
        opti.subject_to(d["Sp"][0] * d["Bp"] == Sfeed * d["Fp"]); opti.subject_to(d["Sp"][0] <= p.S0_PROP_MAX)
        opti.subject_to(d["Xp"][0] == 0.5)
        h = d["Tp"] / (N - 1)
        for n in range(N - 1):
            f = lambda X, S: (kp["mu_max"] * S / (kp["Ks"] + S) * X - kp["kd"] * X, -kp["mu_max"] * S / (kp["Ks"] + S) * X / kp["Yxs"])
            a, b_ = f(d["Xp"][n], d["Sp"][n]), f(d["Xp"][n + 1], d["Sp"][n + 1])
            opti.subject_to(d["Xp"][n + 1] == d["Xp"][n] + h / 2 * (a[0] + b_[0]))
            opti.subject_to(d["Sp"][n + 1] == d["Sp"][n] + h / 2 * (a[1] + b_[1]))
        # fermentación: pie de cuba + mosto sin diluir
        opti.subject_to(d["X"][0] * d["B"] == d["Xp"][-1] * d["Bp"])
        opti.subject_to(d["S"][0] * d["B"] == d["Sp"][-1] * d["Bp"] + Sfeed * (d["B"] - d["Bp"]))
        opti.subject_to(d["P"][0] == 0)
        opti.subject_to(d["X"][0] >= cfg["X0min"])
        h = d["T"] / (N - 1)
        def g(X, S, P, k=kin):
            mu = k["mu_max"] * S / (k["Ks"] + S) * (1 - P / k["Pmax"])
            return mu * X - k["kd"] * X, -mu * X / k["Yxs"], k["Yps"] * mu * X / k["Yxs"]
        for n in range(N - 1):
            a, b_ = g(d["X"][n], d["S"][n], d["P"][n]), g(d["X"][n + 1], d["S"][n + 1], d["P"][n + 1])
            for v, q in zip(("X", "S", "P"), range(3)):
                opti.subject_to(d[v][n + 1] == d[v][n] + h / 2 * (a[q] + b_[q]))
        d["Sfeed"] = Sfeed
        prod[i] = d
    A, B = prod["A"], prod["B"]
    opti.subject_to(A["S"][-1] <= p.S_RES_MAX)                     # vino seco
    opti.subject_to(A["P"][-1] >= cfg["P_wine_min"])               # vino >= 7.0 % v/v (tesis §4.2.3: 7-8 % v/v)
    sigma = opti.variable(); opti.subject_to(opti.bounded(0, sigma, 0.5))
    td = opti.variable(); opti.subject_to(opti.bounded(0.5, td, 24))
    eta_l = 0.985

    QA = A["Nb"] * A["B"] * (1 - sigma); QC = A["Nb"] * A["B"] * sigma
    EtB = B["Nb"] * B["B"] * B["P"][-1] * eta_l / 1000.0           # t/año
    opti.subject_to(opti.bounded(cfg["QA"][0] * sc, QA, cfg["QA"][1] * sc))
    opti.subject_to(opti.bounded(cfg["QC"][0] * sc, QC, cfg["QC"][1] * sc))
    opti.subject_to(opti.bounded(cfg["QB"][0] * sc, EtB, cfg["QB"][1] * sc))

    # ------------------------------------------------------------- tiempos de etapa (ruta flow-shop)
    tau = {"A": [A["Tp"], A["T"], A["th"]], "B": [B["Tp"], B["T"], B["th"], td]}
    shared = [0, 1, 2]                                              # prop, ferm, centrífuga
    def start(i, j):
        return sum(tau[i][:j]) if j > 0 else 0

    cap = 0
    a_ = p.A_FERM
    if cfg["mode"] == "MP":
        Vp, Vf, Qc = opti.variable(), opti.variable(), opti.variable()
        for i in "AB":
            opti.subject_to(Vp >= prod[i]["Bp"]); opti.subject_to(Vf >= prod[i]["B"])
            opti.subject_to(Qc >= prod[i]["B"] / prod[i]["th"])
        cap += p.A_PROP * spow(Vp, cfg["b"]) + a_ * spow(Vf, cfg["b"]) + 30_000.0 * spow(Qc, 0.6)
        units = dict(Vp=Vp, Vf=Vf, Qc=Qc)
        # retardos ZW
        dly = {}
        for i in "AB":
            for k in "AB":
                dvar = opti.variable(); opti.subject_to(dvar >= 0)
                stages = shared + ([3] if (i == "B" and k == "B") else [])
                for j in stages:
                    opti.subject_to(dvar >= start(i, j) + tau[i][j] - start(k, j))
                dly[(i, k)] = dvar
        camp = cfg["campaign"]
        if camp is None:                                            # modelo relajado (SPC)
            opti.subject_to(A["Nb"] * dly[("A", "A")] + B["Nb"] * dly[("B", "B")] <= p.H)
            Tcamp = None; Ncamp = None
        else:
            Ncamp = opti.variable(); opti.subject_to(Ncamp >= 1)
            nA, nB = camp.count("A"), camp.count("B")
            opti.subject_to(A["Nb"] == nA * Ncamp); opti.subject_to(B["Nb"] == nB * Ncamp)
            Lc = len(camp)
            Tcamp = sum(dly[(camp[q], camp[(q + 1) % Lc])] for q in range(Lc))
            opti.subject_to(Ncamp * Tcamp <= p.H)
            # etapa dedicada (destilación de B): entre dos lotes B sucesivos de la secuencia cíclica
            # el tiempo entre inicios debe cubrir t_dist (en ZW la destilación arranca con el mismo desfase)
            posB = [q for q in range(Lc) if camp[q] == "B"]
            for qi, q0 in enumerate(posB):
                q1 = posB[(qi + 1) % len(posB)]
                steps = (q1 - q0) % Lc or Lc
                gap = sum(dly[(camp[(q0 + r) % Lc], camp[(q0 + r + 1) % Lc])] for r in range(steps))
                opti.subject_to(gap >= td)
    else:                                                           # MC
        units = {}
        for i in "AB":
            d = prod[i]
            Vp, Vf, Qc, CT = opti.variable(), opti.variable(), opti.variable(), opti.variable()
            opti.subject_to(Vp >= d["Bp"]); opti.subject_to(Vf >= d["B"]); opti.subject_to(Qc >= d["B"] / d["th"])
            for t_ in tau[i]:
                opti.subject_to(CT >= t_)
            opti.subject_to(d["Nb"] * CT <= p.H)
            cap += p.A_PROP * spow(Vp, cfg["b"]) + a_ * spow(Vf, cfg["b"]) + 30_000.0 * spow(Qc, 0.6)
            units[i] = dict(Vp=Vp, Vf=Vf, Qc=Qc, CT=CT)
        dly = {}; Tcamp = None; Ncamp = None
    # equipos dedicados (iguales en ambos escenarios en estructura)
    kA = KIN_ACET_CAL["acetador"]
    n_acet = opti.variable(); opti.subject_to(n_acet >= A["Nb"] * 24.0 / p.H); opti.subject_to(n_acet >= 1)
    cap += n_acet * a_ * spow(A["B"] * sigma + 1e-3, cfg["b"]) * 1.4          # acetador sumergido (aireado)
    Vage = QA * 90.0 / 365.0                                                    # 90 días de envejecimiento
    cap += 12 * 0.5 * a_ * spow(Vage / 12.0, cfg["b"])                           # 12 tanques inox. (más simples)
    Drate = B["B"] * B["P"][-1] * eta_l / td                                    # kg/h en destilación
    cap += 250_000.0 * spow(Drate / 40.0, 0.6) + 0.6 * a_ * spow(B["B"], cfg["b"])

    # ------------------------------------------------------------- recursos de la planta madre (ec. 4.4)
    kWh = sum(prod[i]["Nb"] * (p.KW_AIR * prod[i]["Bp"] * prod[i]["Tp"] + 1.5 * prod[i]["B"]) for i in "AB") \
          + QC * 24.0 * 0.6 / 1.0                                              # aireación del acetador ~0.6 kW/m3
    Eload = kWh / p.H                                                           # kW medio
    steam = B["Nb"] * B["B"] * B["P"][-1] / 1000.0 * (150.0 / B["P"][-1]) / 1000.0 * 1000.0  # t/año (≈150/P t/t)
    Stload = steam / p.H
    E_prod, E_imp, E_exp = opti.variable(), opti.variable(), opti.variable()
    S_prod, S_imp = opti.variable(), opti.variable()
    for v in (E_prod, E_imp, E_exp, S_prod, S_imp):
        opti.subject_to(v >= 0)
    opti.subject_to(E_prod <= cfg["E_cap"]); opti.subject_to(E_prod + E_imp == Eload + E_exp)
    opti.subject_to(S_prod <= cfg["St_cap"]); opti.subject_to(S_prod + S_imp == Stload)
    energy_cost = p.H * (cfg["c_E_prod"] * E_prod + cfg["c_E_imp"] * E_imp + cfg["c_St_prod"] * S_prod + cfg["c_St_imp"] * S_imp)
    energy_rev = p.H * cfg["q_E_exp"] * E_exp

    raw = sum(prod[i]["Nb"] * (cfg["c_" + i] * (prod[i]["B"] - prod[i]["Bp"] + prod[i]["Fp"]) + p.C_WATER * prod[i]["Fw"]
                               + p.C_ADY * 0.5 * prod[i]["Bp"]) for i in "AB")
    opex = raw + energy_cost
    pr = cfg["price"]
    revenue = pr["wine"] * 1000 * QA + pr["vinegar"] * 1000 * QC + pr["ethanol"] * 1000 * EtB + energy_rev
    lab_cost = labor(cfg["mode"]) * cfg["shifts"] * cfg["wage"]
    TAC = p.CCF * cap + opex + (lab_cost if cfg["labor_in_obj"] else 0)
    profit = revenue - TAC
    opti.minimize(-profit / 1e6)

    # ------------------------------------------------------------- inicialización
    for i, d in prod.items():
        opti.set_initial(d["B"], (12 if i == "A" else 6) * sc * rnd()); opti.set_initial(d["Bp"], 0.06 * (12 if i == "A" else 6) * sc * rnd())
        opti.set_initial(d["Tp"], 8 * rnd()); opti.set_initial(d["T"], 14 * rnd()); opti.set_initial(d["th"], 1.0)
        opti.set_initial(d["Nb"], 500); opti.set_initial(d["Fp"], 0.1 * sc); opti.set_initial(d["Fw"], 0.5 * sc)
        opti.set_initial(d["Xp"], np.linspace(0.5, 9, N)); opti.set_initial(d["Sp"], np.linspace(20, 0.5, N))
        opti.set_initial(d["X"], np.linspace(1.5, 12, N)); opti.set_initial(d["S"], np.linspace(d["Sfeed"] * 0.95, 2, N))
        opti.set_initial(d["P"], np.linspace(0, 0.41 * d["Sfeed"], N))
    opti.set_initial(td, 4); opti.set_initial(sigma, 0.1); opti.set_initial(n_acet, 1.5)
    opti.solver("ipopt", {"ipopt.print_level": cfg["print_level"], "print_time": 0, "ipopt.max_iter": 4000,
                          "ipopt.tol": 1e-7, "ipopt.mu_strategy": "adaptive"})
    t0 = time.time()
    try:
        sol = opti.solve(); ok = True
    except RuntimeError:
        sol = opti.debug; ok = False
    v = lambda e: float(sol.value(e))
    res = dict(ok=ok, status=opti.stats().get("return_status"), cpu=time.time() - t0, mode=cfg["mode"],
               campaign="".join(cfg["campaign"]) if cfg["campaign"] else ("SPC-relajado" if cfg["mode"] == "MP" else "MC"),
               profit=v(profit), revenue=v(revenue), TAC=v(TAC), capex=v(cap), capex_ann=v(p.CCF * cap), opex=v(opex),
               energy_cost=v(energy_cost), energy_rev=v(energy_rev), raw=v(raw), labor_cost=lab_cost,
               workers=labor(cfg["mode"]) * cfg["shifts"], QA=v(QA), QC=v(QC), EtB=v(EtB), sigma=v(sigma), td=v(td),
               Eload=v(Eload), E_imp=v(E_imp), E_exp=v(E_exp), Stload=v(Stload), S_imp=v(S_imp), n_acet=v(n_acet),
               prod={i: dict(B=v(d["B"]), Bp=v(d["Bp"]), Tp=v(d["Tp"]), T=v(d["T"]), th=v(d["th"]), Nb=v(d["Nb"]),
                             X0=v(d["X"][0]), Pend=v(d["P"][-1]), Send=v(d["S"][-1])) for i, d in prod.items()},
               units={k: (v(x) if not isinstance(x, dict) else {kk: v(xx) for kk, xx in x.items()}) for k, x in units.items()},
               delays={f"{i}{k}": v(x) for (i, k), x in dly.items()},
               Tcamp=(v(Tcamp) if Tcamp is not None else None), Ncamp=(v(Ncamp) if Ncamp is not None else None))
    res["profit_with_labor"] = res["profit"] - (0 if cfg["labor_in_obj"] else lab_cost)
    return res


def candidate_campaigns(ratio, max_len=6):
    """Paso (ii) de Corsano 2007: secuencias cíclicas no equivalentes con nA/nB cercano a la razón del relajado."""
    out = set()
    for L in range(2, max_len + 1):
        for seq in itertools.product("AB", repeat=L):
            if "A" not in seq or "B" not in seq:
                continue
            # forma canónica bajo rotación
            rots = ["".join(seq[q:] + seq[:q]) for q in range(L)]
            canon = min(rots)
            # descarta secuencias que son repetición de una más corta (ABAB = AB repetida)
            if any(L % d == 0 and canon == canon[:d] * (L // d) for d in range(1, L)):
                continue
            out.add(canon)
    cands = []
    for s in sorted(out, key=len):
        r = s.count("A") / s.count("B")
        cands.append((s, r))
    cands.sort(key=lambda x: (abs(np.log(x[1] / max(ratio, 1e-3))), len(x[0])))
    return cands


if __name__ == "__main__":
    for mode, camp in (("MP", None), ("MP", list("AB")), ("MC", None)):
        r = build_and_solve(default_cfg(mode=mode, campaign=camp))
        print(mode, r["campaign"], r["ok"], round(r["profit"]), round(r["capex"]), r["prod"]["A"]["Nb"], r["prod"]["B"]["Nb"],
              {k: (round(x, 2) if not isinstance(x, dict) else {kk: round(xx, 2) for kk, xx in x.items()}) for k, x in r["units"].items()},
              f"{r['cpu']:.1f}s")
