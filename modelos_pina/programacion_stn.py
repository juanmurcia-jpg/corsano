"""
Programación semanal de la planta con la red estado-tarea (STN) en tiempo discreto de Maravelias (2021),
cap. 7.2.2, ecs. (7.4)-(7.6):
  (7.4)  Σ_{i∈I_j} Σ_{n'∈NU_in} X_ijn' ≤ 1                      una tarea a la vez por unidad
  (7.5)  β^MIN_j X_ijn ≤ B_ijn ≤ β^MAX_j X_ijn                    tamaño de lote
  (7.6)  I_k,n+1 = I_kn + Σ_{i∈I+_k} ρ_ik B_i,n−τ_i − Σ_{i∈I−_k} ρ_ik B_in + ξ_kn − S_kn ≤ χ_k   inventario
Se añade el cambio de material en la prensa compartida (limpieza de 1 h entre pulpa y cáscara; cap. 3 del libro)
y ventanas de operación por turnos (lun–sáb, 2 turnos de 8 h) para las tareas con personal.

Plan: el óptimo del MILP para la oferta del Chocó 2022 (vino + harina de cáscara, escala 6 200 t/año).
Semana del mes pico (oferta estacional máxima). Opción compartida: UNA prensa para pulpa y cáscara (ahorro de
capital frente al diseño con dos prensas) -> ¿cabe en la semana?
"""
import json, os
import numpy as np
from pyscipopt import Model, quicksum
import capacidad as cp
import planificacion_milp as pm

RES = os.path.join(os.path.dirname(__file__), "results")
HZ = 144                 # h (lun 0:00 – dom 0:00)


def shift_open(n):
    day = n // 24; h = n % 24
    return day < 6 and 6 <= h < 22


def build(fruit_week_t, press_cap_th=3.0, shared_press=True, n_ferm=3, VF=10.0, t_ferm=15, dryer_cap_t_h=1.6,
          time_limit=240):
    b1 = cp.full_balance(1.0)
    fr = dict(pulp=b1["pulp_t"], peel=b1["peel_t"], core=b1["core_t"], crown=b1["crown_t"])
    juice_yield = cp.JUICE_YIELD_PULP / cp.RHO_JUICE          # m3 jugo / t pulpa
    peel_cake = 1 - cp.Y["peel_juice_frac"]
    flour_per_cake = (b1["flour_t"] / b1["peel_t"]) / peel_cake
    # tareas: (unidades, duración h, ent: {estado: ρ}, sal: {estado: ρ}, requiere turno, capacidad por unidad)
    T = {
        "Fraccionar": dict(units=["Frente"], tau=1, cons={"fruta": 1.0}, prod={"pulpa": fr["pulp"], "cascara": fr["peel"],
                         "corazon": fr["core"], "corona": fr["crown"]}, shift=True, cap=2.4),
        "Prensar pulpa": dict(units=["Prensa"] if shared_press else ["PrensaP"], tau=1, cons={"pulpa": 1.0},
                              prod={"jugo": juice_yield}, shift=True, cap=press_cap_th),
        "Prensar cáscara": dict(units=["Prensa"] if shared_press else ["PrensaC"], tau=1, cons={"cascara": 1.0},
                                prod={"torta": peel_cake}, shift=True, cap=press_cap_th),
        "Clarificar (MF)": dict(units=["MF"], tau=1, cons={"jugo": 1.0}, prod={"mosto": 1.0}, shift=True, cap=3.0),
        "Fermentar": dict(units=[f"F{q + 1}" for q in range(n_ferm)], tau=t_ferm, cons={"mosto": 1.0}, prod={"vino": 1.0},
                          shift=False, cap=VF),
        "Secar torta": dict(units=["Secador"], tau=1, cons={"torta": 1.0}, prod={"harina": flour_per_cake}, shift=False,
                            cap=dryer_cap_t_h),
    }
    chi = dict(fruta=1e9, pulpa=1.5, cascara=3.0, corazon=1e9, corona=1e9, jugo=4.0, mosto=50.0, torta=12.0, vino=1e9, harina=1e9)
    # entregas diarias de fruta (lun–sáb, a las 6:00)
    xi = {n: (fruit_week_t / 6.0 if (n % 24 == 6 and n // 24 < 6) else 0.0) for n in range(HZ)}
    m = Model("STN"); m.hideOutput()
    X, B = {}, {}
    for i, d in T.items():
        for j in d["units"]:
            for n in range(HZ):
                if d["shift"] and not all(shift_open(n + q) for q in range(d["tau"])):
                    continue
                if n + d["tau"] > HZ:
                    continue
                X[i, j, n] = m.addVar(vtype="B", name=f"X_{i}_{j}_{n}")
                B[i, j, n] = m.addVar(lb=0, ub=d["cap"], name=f"B_{i}_{j}_{n}")
                m.addCons(B[i, j, n] <= d["cap"] * X[i, j, n])                                   # (7.5)
                if i == "Fermentar":
                    m.addCons(B[i, j, n] >= 0.8 * d["cap"] * X[i, j, n])                      # llenado mínimo 80 %
    units = sorted({j for d in T.values() for j in d["units"]})
    for j in units:                                                                           # (7.4)
        for n in range(HZ):
            terms = [X[i, j, n2] for i, d in T.items() if j in d["units"] for n2 in range(max(0, n - d["tau"] + 1), n + 1)
                     if (i, j, n2) in X]
            if terms:
                m.addCons(quicksum(terms) <= 1)
    if shared_press:                                                                          # limpieza al cambiar de material
        for n in range(HZ - 1):
            for a, b in (("Prensar pulpa", "Prensar cáscara"), ("Prensar cáscara", "Prensar pulpa")):
                if ("" or (a, "Prensa", n)) in X and (b, "Prensa", n + 1) in X:
                    m.addCons(X[a, "Prensa", n] + X[b, "Prensa", n + 1] <= 1)
    states = list(chi)
    I = {(k, n): m.addVar(lb=0, ub=chi[k], name=f"I_{k}_{n}") for k in states for n in range(HZ + 1)}
    for k in states:
        m.addCons(I[k, 0] == 0)
    for n in range(HZ):                                                                        # (7.6)
        for k in states:
            prod = quicksum(d["prod"][k] * B[i, j, n - d["tau"] + 1] for i, d in T.items() if k in d["prod"]
                            for j in d["units"] if (i, j, n - d["tau"] + 1) in B)
            cons = quicksum(d["cons"][k] * B[i, j, n] for i, d in T.items() if k in d["cons"] for j in d["units"] if (i, j, n) in B)
            supply = xi[n] if k == "fruta" else 0.0
            m.addCons(I[k, n + 1] == I[k, n] + prod - cons + supply)
    # objetivo: procesar toda la fruta y maximizar vino + harina, penalizar inventario final de perecederos
    fruit_left = I["fruta", HZ]
    obj = (10.0 * quicksum(B["Fermentar", j, n] for j in T["Fermentar"]["units"] for n in range(HZ) if ("Fermentar", j, n) in B)
           + 20.0 * quicksum(B["Secar torta", "Secador", n] for n in range(HZ) if ("Secar torta", "Secador", n) in B)
           - 1000.0 * fruit_left - 5.0 * quicksum(I[k, HZ] for k in ("pulpa", "cascara", "jugo", "torta")))
    m.setObjective(obj, "maximize")
    m.setParam("limits/time", time_limit)
    m.optimize()
    sched = []
    for (i, j, n), v in X.items():
        if m.getVal(v) > 0.5:
            sched.append(dict(task=i, unit=j, start=n, dur=T[i]["tau"], size=m.getVal(B[i, j, n])))
    inv = {k: [m.getVal(I[k, n]) for n in range(HZ + 1)] for k in states}
    util = {}
    for j in units:
        busy = sum(s["dur"] for s in sched if s["unit"] == j)
        avail = sum(1 for n in range(HZ) if shift_open(n)) if any(T[i]["shift"] for i in T if j in T[i]["units"]) else HZ
        util[j] = busy / avail
    return dict(status=m.getStatus(), gap=m.getGap(), obj=m.getObjVal(), schedule=sched, inventory=inv, util=util,
                fruit_week=fruit_week_t, fruit_left=m.getVal(fruit_left), nbin=len(X), shared=shared_press,
                press_cap=press_cap_th)


if __name__ == "__main__":
    sup = 6146.0 * pm.SEASON / 12.0
    peak_week = min(float(sup.max()), 6200 / 12.0) / (30.4 / 7)
    out = {}
    for lab, kw in (("Prensa compartida 3 t/h", dict(shared_press=True, press_cap_th=3.0)),
                    ("Prensa compartida 2 t/h", dict(shared_press=True, press_cap_th=2.0)),
                    ("Dos prensas 2 t/h", dict(shared_press=False, press_cap_th=2.0))):
        r = build(peak_week, **kw)
        out[lab] = r
        print(lab, r["status"], "gap", round(r["gap"], 4), "fruta semana", round(peak_week, 1), "sin procesar", round(r["fruit_left"], 2),
              "binarias", r["nbin"], {k: round(v, 2) for k, v in r["util"].items()}, flush=True)
    json.dump(out, open(f"{RES}/stn_semana.json", "w"), default=float)
