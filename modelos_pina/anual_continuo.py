"""
Programa ANUAL con estacionalidad en tiempo continuo (Maravelias 2021):
  - rejilla continua común (cap. 7.3, ecs. 7.35–7.36): puntos T_t con T_0 = 0, T_|T| = η, T_t ≥ T_t−1;
    aquí los cortes de mes son puntos fijos y cada mes tiene K periodos de duración variable d_mt ≥ 0;
  - procesos continuos (cap. 9.2): producción = tasa × duración, con la tasa acotada por la capacidad;
  - transiciones entre modos (cap. 9.3.2): limpieza σ al cambiar el material de la prensa compartida;
  - inventarios con capacidad χ_k (cap. 7.2/8.2) y entrada estacional de fruta = r_m · d_mt (lineal en d).
Configuraciones: A = vino + harina (plan óptimo del MILP para el Chocó 2022); B = A + bromelaína.
Resultado: campañas por mes (Gantt anual), ocupación por unidad y mes, fruta perdida -> cuellos de botella.
"""
import json, os, math
import numpy as np
from pyscipopt import Model, quicksum
import capacidad as cp
import planta_trl9 as pt
import planificacion_milp as pm
import tea_lineas as tl

RES = os.path.join(os.path.dirname(__file__), "results")
DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
HM = DAYS * 24.0
A_STAFF = cp.calendar_hours("burk") / 8766.0          # fracción del tiempo calendario con personal (2 turnos lun–sáb)
A_CONT = 0.9


def units_from_design(scale=6200.0, press_th=2.0, with_bromelain=False):
    D = pt.design(scale)
    L = D["lines"]
    get = lambda line, key: next(e for e in L[line]["equipment"] if key in e["name"])
    fe = get("vino", "Peladora"); lav = get("vino", "Recepción")
    frente = min(fe["qty"] * fe["size"], lav["qty"] * lav["size"])                  # t fruta/h
    mf = get("vino", "Microfiltración"); mf_cap = mf["qty"] * mf["size"] * 60 / 1000   # m3 jugo/h
    ferm = get("vino", "Fermentador")
    dtc = 12.5 + 2.5 + ferm["size"] / max(L["vino"]["flows"]["juice_m3"] / (365.25 * 0.9 * 24), 1e-6)
    bodega = ferm["qty"] * ferm["size"] / dtc                                           # m3/h de mosto
    sec = get("harina", "Secador de banda")
    cake_cap = sec["qty"] * sec["size"] / 1000 / (1 - 0.10 * (1 - cp.Y["peel_cake_moist"]) / (1 - cp.Y["flour_moist"]) - 0.3)
    cake_cap = sec["qty"] * sec["size"] / 1000 * 1.35                                   # t torta/h (≈ agua/0,74)
    U = dict(Frente=dict(cap=frente, a=A_STAFF), Prensa=dict(cap=press_th, a=A_STAFF), MF=dict(cap=mf_cap, a=A_STAFF),
             Bodega=dict(cap=bodega, a=A_CONT), Secador=dict(cap=cake_cap, a=A_CONT))
    if with_bromelain:
        spd = get("bromelaina", "aspersión")
        U["Aspersión"] = dict(cap=spd["qty"] * spd["size"] / 1000 / 0.12, a=A_STAFF)    # t jugo de corazón/h
    return U


def solve(U, supply=6146.0, K=4, sigma=1.0, with_bromelain=False, time_limit=90):
    b1 = cp.full_balance(1.0)
    fr = dict(pulpa=b1["pulp_t"], cascara=b1["peel_t"], corazon=b1["core_t"])
    juice = cp.JUICE_YIELD_PULP / cp.RHO_JUICE
    cake = 1 - cp.Y["peel_juice_frac"]; core_juice = cp.Y["core_juice_frac"]
    flour_per_cake = (b1["flour_t"] / b1["peel_t"]) / cake
    wine_per_must = 1 - cp.WINE_LOSS
    modes = ["pulpa", "cascara"] + (["corazon"] if with_bromelain else [])
    rate_in = supply * pm.SEASON / 12.0 / HM                     # t/h de fruta que llega en cada mes
    chi = dict(fruta=3 * 24 * max(rate_in), pulpa=1.5, cascara=3.0, corazon=2.0, jugo=4.0, mosto=50.0, torta=12.0, jcor=3.0)
    m = Model("anual"); m.hideOutput()
    MT = [(mo, t) for mo in range(12) for t in range(K)]
    d = {mt: m.addVar(lb=0, ub=HM[mt[0]]) for mt in MT}
    for mo in range(12):
        m.addCons(quicksum(d[mo, t] for t in range(K)) == HM[mo])          # (7.35)-(7.36) con cortes de mes fijos
    # prensa compartida en tiempo compartido: τ_i horas por material y n cambios (entero) en cada periodo
    tau = {(i, mt): m.addVar(lb=0) for i in modes for mt in MT}
    ncy = {mt: m.addVar(vtype="I", lb=0, ub=4 * HM[mt[0]]) for mt in MT}
    P = {(i, mt): m.addVar(lb=0) for i in modes for mt in MT}             # t procesadas en la prensa
    fe = {mt: m.addVar(lb=0) for mt in MT}; mfv = {mt: m.addVar(lb=0) for mt in MT}
    bod = {mt: m.addVar(lb=0) for mt in MT}; sec = {mt: m.addVar(lb=0) for mt in MT}
    asp = {mt: m.addVar(lb=0) for mt in MT} if with_bromelain else None
    loss = {mt: m.addVar(lb=0) for mt in MT}
    st = list(chi)
    I = {(k, q): m.addVar(lb=0, ub=chi[k]) for k in st for q in range(len(MT) + 1)}
    for k in st:
        m.addCons(I[k, 0] == I[k, len(MT)])                              # programa periódico anual
    for q, mt in enumerate(MT):
        mo, t = mt
        nm = len(modes)
        m.addCons(quicksum(tau[i, mt] for i in modes) + sigma * ncy[mt] <= U["Prensa"]["a"] * d[mt])   # tiempo + limpiezas
        for i in modes:
            m.addCons(P[i, mt] <= U["Prensa"]["cap"] * tau[i, mt])
            # acoplamiento con el almacenamiento perecedero: mientras se prensa i, las otras fracciones se acumulan.
            # Con ncy/nm ciclos por periodo, cada campaña de i dura τ_i/(ncy/nm); lo acumulado de j no puede pasar de χ_j:
            #   fr_j · F_max · τ_i · nm / ncy ≤ χ_j   ⇔   fr_j · F_max · nm · τ_i ≤ χ_j · ncy   (lineal, conservador)
            for j in modes:
                if j != i:
                    m.addCons(fr[j] * U["Frente"]["cap"] * nm * tau[i, mt] <= chi[j] * ncy[mt])
        for v, u in ((fe, "Frente"), (mfv, "MF"), (bod, "Bodega"), (sec, "Secador")):
            m.addCons(v[mt] <= U[u]["cap"] * U[u]["a"] * d[mt])
        if with_bromelain:
            m.addCons(asp[mt] <= U["Aspersión"]["cap"] * U["Aspersión"]["a"] * d[mt])
        # inventarios (ec. 7.6 en rejilla continua): I_{q+1} = I_q + producción − consumo + entradas − pérdidas
        bal = {
            "fruta": rate_in[mo] * d[mt] - fe[mt] - loss[mt],
            "pulpa": fr["pulpa"] * fe[mt] - P["pulpa", mt],
            "cascara": fr["cascara"] * fe[mt] - P["cascara", mt],
            "corazon": fr["corazon"] * fe[mt] - (P["corazon", mt] if with_bromelain else 0) - (0 if with_bromelain else fr["corazon"] * fe[mt]),
            "jugo": juice * P["pulpa", mt] - mfv[mt],
            "mosto": mfv[mt] - bod[mt],
            "torta": cake * P["cascara", mt] - sec[mt],
            "jcor": (core_juice * P["corazon", mt] - asp[mt]) if with_bromelain else 0,
        }
        for k in st:
            m.addCons(I[k, q + 1] == I[k, q] + bal[k])
    # valor (márgenes por unidad procesada, del TEA): vino, harina, bromelaína; pérdida de fruta
    v_wine = 0.95 * 3000.0 * 1000 * wine_per_must - pm.mean("vino", "var_per") / (juice * 1.0) if hasattr(pm, "mean") else 0
    marg_wine = 0.95 * 3000.0 * 1000 * wine_per_must                    # COP por m3 de mosto fermentado
    marg_flour = 0.95 * tl.M("harina_kg") * 1000 * flour_per_cake          # COP por t de torta secada
    marg_brom = 0.95 * tl.M("bromelaina_kg") * (b1["bromelain_kg"] / b1["core_t"]) / core_juice
    obj = quicksum(marg_wine * bod[mt] + marg_flour * sec[mt] + (marg_brom * asp[mt] if with_bromelain else 0)
                   - 400.0 * 1000 * loss[mt] - 2e4 * ncy[mt] for mt in MT)
    m.setObjective(obj / 1e6, "maximize")
    m.setParam("limits/time", time_limit); m.setParam("limits/gap", 0.01)
    m.optimize()
    v = m.getVal
    sol = dict(status=m.getStatus(), gap=m.getGap(), K=K, sigma=sigma, with_bromelain=with_bromelain, units=U, supply=supply)
    rows = []
    T0 = 0.0
    for q, mt in enumerate(MT):
        mo, t = mt
        rows.append(dict(month=mo, k=t, start=T0, dur=v(d[mt]), tau={i: v(tau[i, mt]) for i in modes}, W=v(ncy[mt]),
                         P={i: v(P[i, mt]) for i in modes}, fe=v(fe[mt]), mf=v(mfv[mt]), bod=v(bod[mt]), sec=v(sec[mt]),
                         asp=(v(asp[mt]) if with_bromelain else 0.0), loss=v(loss[mt])))
        T0 += v(d[mt])
    sol["periods"] = rows
    util = {u: [] for u in U}
    for mo in range(12):
        rr = [r for r in rows if r["month"] == mo]
        avail = lambda u: U[u]["cap"] * U[u]["a"] * HM[mo]
        util["Frente"].append(sum(r["fe"] for r in rr) / avail("Frente"))
        util["Prensa"].append((sum(sum(r["tau"].values()) for r in rr) + sigma * sum(r["W"] for r in rr)) / (U["Prensa"]["a"] * HM[mo]))
        util["MF"].append(sum(r["mf"] for r in rr) / avail("MF"))
        util["Bodega"].append(sum(r["bod"] for r in rr) / avail("Bodega"))
        util["Secador"].append(sum(r["sec"] for r in rr) / avail("Secador"))
        if with_bromelain:
            util["Aspersión"].append(sum(r["asp"] for r in rr) / avail("Aspersión"))
    sol["util"] = util
    sol["loss_month"] = [sum(r["loss"] for r in rows if r["month"] == mo) for mo in range(12)]
    sol["supply_month"] = (supply * pm.SEASON / 12.0).tolist()
    sol["changeovers"] = sum(r["W"] for r in rows)
    sol["products"] = dict(vino_m3=sum(r["bod"] for r in rows) * wine_per_must, harina_t=sum(r["sec"] for r in rows) * flour_per_cake,
                           bromelaina_kg=sum(r["asp"] for r in rows) * marg_brom / (0.95 * tl.M("bromelaina_kg")) if with_bromelain else 0.0)
    return sol


if __name__ == "__main__":
    out = {}
    for lab, kw in (("A: vino + harina, prensa compartida 2 t/h", dict(with_bromelain=False)),
                    ("B: vino + harina + bromelaína, prensa compartida 2 t/h", dict(with_bromelain=True)),
                    ("B con prensa de 3 t/h", dict(with_bromelain=True, press=3.0))):
        U = units_from_design(press_th=kw.pop("press", 2.0), with_bromelain=kw["with_bromelain"])
        for K in (2, 4):
            r = solve(U, K=K, **kw)
            out[f"{lab} | K={K}"] = r
            print(lab, "K", K, r["status"], "gap", round(r["gap"], 4), "pérdida t", round(sum(r["loss_month"]), 1),
                  "cambios", round(r["changeovers"]), {k: round(v, 1) for k, v in r["products"].items()},
                  "ocupación máx", {u: round(max(v), 2) for u, v in r["util"].items()}, flush=True)
            json.dump(out, open(f"{RES}/anual_continuo.json", "w"), default=float)
    json.dump(out, open(f"{RES}/anual_continuo.json", "w"), default=float)
