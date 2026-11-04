"""
MODELO 2 — Línea de etanol del hub de azúcares con reciclo de vinaza y restricción ambiental
(adaptación de Corsano et al. 2006b, ChERD 84:932, y del modelo de red de 2004).

Analogía estructural Corsano (caña) -> tesis (piña):
    melaza            -> jugo de cáscara (peel)            [hub, §4.4]
    jugo de filtros   -> hidrolizado de hojas/corona (hydro) [hub, §4.5]  (con inhibidores: furfural/HMF)
    —                 -> permeado UF del tallo+corazón (perm) [hub, §4.3]
    vinaza reciclada  -> vinaza de la destilación del etanol del hub (vin)
Etapas: propagación aerobia (serie) -> fermentación alcohólica (serie/paralelo) -> centrífuga (semicontinua)
        -> destilación por lotes (Fenske / Underwood aprox. / Gilliland-Eduljee, ec. 24-31 de 2006b).
Penalización por vinaza no reciclada: ec. 37 (volumen) o ec. 38 (volumen y DBO ~ S_W).
La mezcla de sustratos genera términos bilineales x_k·V·S: es el mismo tipo de no convexidad que el
balance de propiedad del hub de la tesis (§4.6).
"""
import time
import numpy as np
import casadi as ca
import params as p
from kinetics import KIN_WINE

FEEDS = ("peel", "hydro", "perm")
SRC = FEEDS + ("vin",)


def default_cfg(**kw):
    kin_f = dict(KIN_WINE); kin_f.update(Yps=0.46, Pmax=100.0)   # fermentación de azúcares mixtos [L]/[S]
    cfg = dict(N=10, b=p.B_FERM, PR=p.PR_ETOH_HUB, penalty="eq38", phi_max=0.40, alpha=p.ALPHA_INHIB_HYDRO,
               Sw_fix=None, Sw_max=None, VRes_max=None, allow_vin_prop=True, kin_f=kin_f, kin_p=dict(p.KIN_PROP),
               hub=dict(p.HUB), Ncol=20, eta_l_min=0.80, seed=None, X0min=p.X0_MIN_FERM, print_level=0,
               op1=[(1,), (1, 1)], op2=[(1,), (1, 1), (2,), (3,)])
    cfg.update(kw)
    return cfg


def spow(V, b, eps=1e-8):
    return (0.5 * (V + ca.sqrt(V * V + eps))) ** b


def yxs_blend(x):
    c = p.YXS_BLEND
    y = sum(c[k] * x[k] for k in SRC)
    y += c["peel_hydro"] * x["peel"] * x["hydro"] + c["peel_perm"] * x["peel"] * x["perm"]
    y += c["hydro_perm"] * x["hydro"] * x["perm"] + c["perm_vin"] * x["perm"] * x["vin"]
    return y


def build_and_solve(cfg):
    N, hub = cfg["N"], cfg["hub"]
    kf, kp = cfg["kin_f"], cfg["kin_p"]
    rng = np.random.default_rng(cfg["seed"])
    opti = ca.Opti()
    CT = opti.variable()
    Sw = opti.variable()           # azúcar residual en la vinaza (g/L) — variable de optimización (2006b)
    Pw = opti.variable()           # etanol residual en la vinaza
    eta_l, eta_h = opti.variable(), opti.variable()
    t_cen, t_dist = opti.variable(), opti.variable()
    cap, feed_cost, water, ady, kwh = 0, 0, 0, 0, 0
    use = {k: 0 for k in SRC}
    units = []

    def new_unit(M, ferment):
        u = dict(M=M, V=opti.variable(), T=opti.variable(), X=opti.variable(N), S=opti.variable(N),
                 F={k: opti.variable() for k in SRC}, W=opti.variable(), ferment=ferment)
        u["P"] = opti.variable(N)
        u["x"] = {k: opti.variable() for k in SRC}     # fracción del azúcar inicial aportada por cada fuente
        for k in SRC:
            opti.subject_to(u["F"][k] >= 0); opti.subject_to(opti.bounded(0, u["x"][k], 1))
        opti.subject_to(u["W"] >= 0)
        opti.subject_to(sum(u["x"][k] for k in SRC) == 1)
        opti.subject_to(opti.bounded(1e-4, u["V"], 300)); opti.subject_to(opti.bounded(0.05, u["T"], 120))
        opti.subject_to(u["T"] <= M * CT)
        opti.subject_to(u["X"] >= 0); opti.subject_to(u["S"] >= 0); opti.subject_to(u["S"] <= 200)
        opti.subject_to(u["X"] <= 80); opti.subject_to(u["P"] >= 0); opti.subject_to(u["P"] <= 0.97 * kf["Pmax"])
        opti.subject_to(u["F"]["vin"] <= cfg["phi_max"] * u["V"])       # límite de reciclo (sales/inertes)
        return u

    def kinetics(u):
        h = u["T"] / (N - 1)
        if u["ferment"]:
            mu_max = kf["mu_max"] * (1 - cfg["alpha"] * u["x"]["hydro"])
            def f(X, S, P):
                mu = mu_max * S / (kf["Ks"] + S) * (1 - P / kf["Pmax"])
                return mu * X - kf["kd"] * X, -mu * X / kf["Yxs"], kf["Yps"] * mu * X / kf["Yxs"]
        else:
            Y = yxs_blend(u["x"])
            mu_max = kp["mu_max"] * (1 - cfg["alpha"] * u["x"]["hydro"])
            def f(X, S, P):
                mu = mu_max * S / (kp["Ks"] + S)
                return mu * X - kp["kd"] * X, -mu * X / Y, 0 * X
        for i in range(N - 1):
            a = f(u["X"][i], u["S"][i], u["P"][i]); b = f(u["X"][i + 1], u["S"][i + 1], u["P"][i + 1])
            opti.subject_to(u["X"][i + 1] == u["X"][i] + h / 2 * (a[0] + b[0]))
            opti.subject_to(u["S"][i + 1] == u["S"][i] + h / 2 * (a[1] + b[1]))
            opti.subject_to(u["P"][i + 1] == u["P"][i] + h / 2 * (a[2] + b[2]))

    def feed_balances(u, Vin, Xin, Sin, Pin, xin, ady_var=None):
        Ftot = sum(u["F"][k] for k in SRC) + u["W"]
        opti.subject_to(u["V"] == Vin + Ftot)
        opti.subject_to(u["X"][0] * u["V"] == Xin * Vin + (ady_var if ady_var is not None else 0))
        sug = {k: u["F"][k] * hub[k]["S"] for k in FEEDS}
        sug["vin"] = u["F"]["vin"] * Sw
        opti.subject_to(u["S"][0] * u["V"] == Sin * Vin + sum(sug.values()))
        opti.subject_to(u["P"][0] * u["V"] == Pin * Vin + u["F"]["vin"] * Pw)
        for k in SRC:   # ec. 21-23 de 2004: contribución de cada fuente al azúcar inicial (bilineal)
            opti.subject_to(u["x"][k] * u["S"][0] * u["V"] == sug[k] + xin[k] * Sin * Vin)

    # ----------------------------------------------------------------------- propagación
    pool = dict(V=0, XV=0, SV=0, PV=0, xSV={k: 0 for k in SRC})
    for alt in cfg["op1"]:
        prev = None
        for j, M in enumerate(alt):
            u = new_unit(M, False); u["op"] = "prop"; u["alt"] = alt; u["j"] = j
            opti.subject_to(u["S"][0] <= p.S0_PROP_MAX)
            if not cfg["allow_vin_prop"]:
                opti.subject_to(u["F"]["vin"] == 0)
            if prev is None:
                a0 = opti.variable(); opti.subject_to(a0 >= 0); ady += a0; u["ady"] = a0
                opti.subject_to(a0 <= 0.5 * u["V"])          # siembra del propagador <= 0.5 g/L de LSA
                feed_balances(u, 0, 0, 0, 0, {k: 0 for k in SRC}, ady_var=a0)
            else:
                feed_balances(u, prev["V"], prev["X"][-1], prev["S"][-1], prev["P"][-1], prev["x"])
            kinetics(u)
            cap += M * p.A_PROP * spow(u["V"], cfg["b"])
            kwh += p.KW_AIR * u["V"] * u["T"]
            units.append(u); prev = u
        pool["V"] += prev["V"]; pool["XV"] += prev["X"][-1] * prev["V"]; pool["SV"] += prev["S"][-1] * prev["V"]
        pool["PV"] += prev["P"][-1] * prev["V"]
        for k in SRC:
            pool["xSV"][k] += prev["x"][k] * prev["S"][-1] * prev["V"]
    Xp, Sp, Pp = opti.variable(), opti.variable(), opti.variable()
    xp = {k: opti.variable() for k in SRC}
    opti.subject_to(Xp * pool["V"] == pool["XV"]); opti.subject_to(Sp * pool["V"] == pool["SV"])
    opti.subject_to(Pp * pool["V"] == pool["PV"])
    for k in SRC:
        opti.subject_to(xp[k] * Sp * pool["V"] == pool["xSV"][k]); opti.subject_to(opti.bounded(0, xp[k], 1))
    opti.subject_to(opti.bounded(0, Xp, 80)); opti.subject_to(opti.bounded(0, Sp, 200)); opti.subject_to(opti.bounded(0, Pp, 100))

    # ----------------------------------------------------------------------- fermentación
    Bin_sum, Bout, EtOH, Sout, Xout = 0, 0, 0, 0, 0
    for alt in cfg["op2"]:
        prev = None
        for j, M in enumerate(alt):
            u = new_unit(M, True); u["op"] = "ferm"; u["alt"] = alt; u["j"] = j
            if prev is None:
                Bin = opti.variable(); opti.subject_to(Bin >= 0); Bin_sum += Bin; u["Bin"] = Bin
                feed_balances(u, Bin, Xp, Sp, Pp, xp)

            else:
                feed_balances(u, prev["V"], prev["X"][-1], prev["S"][-1], prev["P"][-1], prev["x"])
            opti.subject_to(u["X"][0] >= cfg["X0min"])   # pitching mínimo en cada fermentador
            kinetics(u)
            cap += M * p.A_FERM * spow(u["V"], cfg["b"])
            units.append(u); prev = u
        Bout += prev["V"]; EtOH += prev["P"][-1] * prev["V"]; Sout += prev["S"][-1] * prev["V"]
        Xout += prev["X"][-1] * prev["V"]
    opti.subject_to(Bin_sum == pool["V"])
    for u in units:
        for k in SRC:
            use[k] += u["F"][k]
        water += u["W"]

    # ----------------------------------------------------------------------- centrífuga (semicontinua)
    opti.subject_to(opti.bounded(0.1, t_cen, 12))
    Qcen = Bout / t_cen                                        # m3/h
    cap += 30_000.0 * spow(Qcen, 0.6)                          # [S] centrífuga de discos
    kwh += 1.5 * Bout                                          # kWh/m3 [L]

    # ----------------------------------------------------------------------- destilación por lotes (2006b)
    opti.subject_to(opti.bounded(cfg['eta_l_min'], eta_l, 0.995)); opti.subject_to(opti.bounded(0.001, eta_h, 0.2))
    opti.subject_to(opti.bounded(0.5, t_dist, 24))
    fl = EtOH                                    # kg etanol en la alimentación (g/L*m3 = kg)
    fh = 1000.0 * Bout - fl / 0.789 * 0.789      # kg agua aprox. (1 m3 ≈ 1000 kg)
    dl, dh = eta_l * fl, eta_h * fh
    alpha = p.ALPHA_LH
    Nmin = ca.log(ca.log(1 - eta_l) / ca.log(1 - eta_h)) / np.log(alpha)
    eta = (dl + dh) / (fl + fh)
    rl = ca.log(1 - eta_l) / ca.log(1 - eta); rh = ca.log(1 - eta_h) / ca.log(1 - eta)
    Rmin = ca.fmax((rl - alpha * rh) / (alpha - 1), 0.1)
    Nc = cfg["Ncol"]
    opti.subject_to(Nmin <= 0.8 * Nc)
    Xg = (Nc - Nmin) / (Nc + 1)
    Z = (1 - Xg) ** 2.95                         # ec. 26 de Corsano 2006b: R = (Rmin + Z)/(1 - Z)
    R = (Rmin + Z) / (1 - Z)
    vap = (dl + dh) * (R + 1)                    # kg vapor por lote
    Aevap = vap * p.DH_VAP / (t_dist * 4710.15 * 50.0)
    Acond = vap * p.DH_VAP / (t_dist * 2826.1 * 49.3)
    Acol = vap / (t_dist * 3600 * 0.6 * 2.5)     # m2  (rho_G=0.6, v_G=2.5 m/s)
    cap += 4_000.0 * spow(Aevap, 0.6) + 3_000.0 * spow(Acond, 0.6) + 60_000.0 * spow(Acol * Nc * 0.6, 0.6) \
           + 0.6 * p.A_FERM * spow(Bout, cfg["b"])    # columna, intercambiadores, calderín
    steam_t = vap * p.DH_VAP / 2100.0 / 1000.0   # t vapor por lote (calor latente vapor 2100 kJ/kg)

    # ----------------------------------------------------------------------- vinaza y reciclo
    Vvin = Bout - (dl / 789.0 + dh / 1000.0)
    opti.subject_to(Sw * Vvin == Sout)                         # azúcar no volátil
    opti.subject_to(Pw * Vvin == (1 - eta_l) * EtOH)
    opti.subject_to(opti.bounded(0, Sw, 200)); opti.subject_to(opti.bounded(0, Pw, 60))
    VRes = Vvin - use["vin"]
    opti.subject_to(VRes >= 0)
    if cfg["Sw_fix"] is not None:
        opti.subject_to(Sw == cfg["Sw_fix"])
    if cfg["Sw_max"] is not None:
        opti.subject_to(Sw <= cfg["Sw_max"])
    nb = p.H / CT
    if cfg["VRes_max"] is not None:
        opti.subject_to(VRes * nb <= cfg["VRes_max"])

    # ----------------------------------------------------------------------- programación ZW y producción
    opti.subject_to(CT >= t_cen + t_dist)                      # ec. 33-34
    opti.subject_to(opti.bounded(0.5, CT, 48))
    opti.subject_to(dl >= cfg["PR"] * CT)                      # ec. 35
    for k in FEEDS:
        opti.subject_to(use[k] <= hub[k]["Fmax"] * CT)         # disponibilidad del hub

    if cfg["penalty"] == "eq37":
        pen = nb * p.ZF * VRes
    elif cfg["penalty"] == "eq38":
        pen = nb * (p.ZE_ZT + (Sw + p.NF_VIN + 2.09 / 1.07 * Pw) / p.OS * p.ZBO) * VRes   # etanol residual como DBO equivalente
    else:
        pen = 0
    feed_cost = sum(hub[k]["c"] * use[k] for k in FEEDS)
    opex = nb * (feed_cost + p.C_WATER * water + p.C_ADY * ady + p.C_ELEC_ZNI * kwh + p.C_STEAM * steam_t)
    TAC = p.CCF * cap + opex + pen
    opti.minimize(TAC / 1e5)

    # ----------------------------------------------------------------------- inicialización
    r = (lambda: 0.6 + 0.8 * rng.random()) if cfg["seed"] is not None else (lambda: 1.0)
    opti.set_initial(CT, 10 * r()); opti.set_initial(Sw, 15); opti.set_initial(Pw, 2)
    opti.set_initial(eta_l, 0.95); opti.set_initial(eta_h, 0.02); opti.set_initial(t_cen, 1); opti.set_initial(t_dist, 6)
    for u in units:
        V0 = (1.0 if u["op"] == "prop" else 10.0) * r()
        opti.set_initial(u["V"], V0); opti.set_initial(u["T"], 8 * r())
        for k in FEEDS:
            opti.set_initial(u["F"][k], 0.25 * V0 * r())
        opti.set_initial(u["F"]["vin"], 0.1 * V0); opti.set_initial(u["W"], 0.1 * V0)
        for k in SRC:
            opti.set_initial(u["x"][k], 0.25)
        if u["op"] == "prop":
            opti.set_initial(u["X"], np.linspace(0.5, 8, N)); opti.set_initial(u["S"], np.linspace(18, 1, N))
            opti.set_initial(u["P"], 0)
        else:
            opti.set_initial(u["X"], np.linspace(2, 10, N)); opti.set_initial(u["S"], np.linspace(85, 5, N))
            opti.set_initial(u["P"], np.linspace(1, 36, N))
    opti.set_initial(Xp, 8); opti.set_initial(Sp, 1)
    for k in SRC:
        opti.set_initial(xp[k], 0.25)

    opti.solver("ipopt", {"ipopt.print_level": cfg["print_level"], "print_time": 0, "ipopt.max_iter": 4000,
                          "ipopt.tol": 1e-7, "ipopt.mu_strategy": "adaptive"})
    t0 = time.time()
    try:
        sol = opti.solve(); ok = True
    except RuntimeError:
        sol = opti.debug; ok = False
    v = lambda e: float(sol.value(e))
    res = dict(ok=ok, status=opti.stats().get("return_status"), cpu=time.time() - t0, TAC=v(TAC),
               capex_ann=v(p.CCF * cap), opex=v(opex), penalty=v(pen), CT=v(CT), Sw=v(Sw), Pw=v(Pw),
               eta_l=v(eta_l), eta_h=v(eta_h), R=v(R), Nmin=v(Nmin), steam_t_yr=v(steam_t * nb),
               VRes_yr=v(VRes * nb), Vvin_yr=v(Vvin * nb), recycle_frac=v(use["vin"] / Vvin),
               use_yr={k: v(use[k] * nb) for k in SRC}, water_yr=v(water * nb),
               nvar=opti.nx, ncon=opti.ng, units=[])
    for u in units:
        res["units"].append(dict(op=u["op"], alt=str(u["alt"]), stage=u["j"] + 1, M=u["M"], V=v(u["V"]), T=v(u["T"]),
                                 F={k: v(u["F"][k]) for k in SRC}, W=v(u["W"]), x={k: v(u["x"][k]) for k in SRC},
                                 X=np.array(sol.value(u["X"])).tolist(), S=np.array(sol.value(u["S"])).tolist(),
                                 P=np.array(sol.value(u["P"])).tolist()))
    res["active"] = [(d["op"], d["alt"], d["stage"], d["M"], round(d["V"], 3), round(d["T"], 2))
                     for d in res["units"] if d["V"] > 1e-2]
    ops = {}
    for (op, alt, st, M, V, T) in res["active"]:
        ops.setdefault(op, set()).add(alt)
    res["label"] = f"Prop {'+'.join(sorted(ops.get('prop', []))) or '-'} | Ferm {'+'.join(sorted(ops.get('ferm', [])))}"
    return res


if __name__ == "__main__":
    for s in (None, 1, 2):
        r = build_and_solve(default_cfg(seed=s))
        print(r["ok"], r["status"], round(r["TAC"]), r["label"], f"CT={r['CT']:.2f} Sw={r['Sw']:.1f} rec={r['recycle_frac']:.2f}",
              {k: round(x) for k, x in r["use_yr"].items()}, f"{r['cpu']:.1f}s")
