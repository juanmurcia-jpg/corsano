"""
Dimensionamiento óptimo de equipos acoplado al programa anual con estacionalidad (diseño + operación simultáneos).

Idea: el tamaño de cada equipo no se fija por el flujo medio de diseño (planta_trl9.py) sino que lo elige un MILP
que, al mismo tiempo, programa la operación de todo el año en tiempo continuo (el modelo de anual_continuo.py).
Así los flujos quedan balanceados: ningún equipo sobra mientras otro topa la producción.

Formulación (referencias):
  - Grossmann (2021), cap. 10: elección de un tamaño de catálogo por equipo como disyunción
        ∨_s [ y_us ;  cap_u = cap_us ;  costo_u = C_us ]  ,  Σ_s y_us = 1
    con su envolvente convexa; el producto «tamaño × horas disponibles» se linealiza de forma exacta
    (variable 0-1 × continua acotada, Glover 1975; Grossmann cap. 7.3).
  - Grossmann (2021), cap. 14: versión estocástica en dos etapas: tamaños en la primera etapa (aquí y ahora),
    operación anual en la segunda etapa por escenario de oferta.
  - Maravelias (2021), cap. 7.3, 8.2, 9.3.2 y 10: rejilla continua anclada a los meses, procesos continuos con
    tasa ≤ capacidad, prensa en tiempo compartido con limpiezas σ, inventarios con capacidad y programa periódico.
  - Moresi (1989b): N_F = Q·Δt_c/V_F con Δt_c = V_F/Q + t_proc  ⇒  Q ≤ (N_F − 1)·V_F/t_proc (lineal en N_F):
    mientras un fermentador se llena, los demás fermentan.
  - Burk (estructura de los TEA de asaí y coco): costo de compra -> FCI con el factor equivalente de Lang del
    motor tea_burk.py; cargo anual = FCI·(CRF + mantenimiento + impuestos locales).

Decisiones de diseño (todas discretas, del catálogo de planta_trl9.CAT):
  frente (lavado + peladoras), prensa principal (pulpa y, si se comparte, cáscara/corazón), prensa dedicada de
  cáscara (0 = no hay), MF + pasteurizador, bodega (N_F fermentadores de 10 m³ + chiller + centrífuga),
  secador de banda + caldera + molino, almacenamiento aséptico de mosto (nivela meses pico y valle),
  tercer turno en el frente (alternativa operativa a comprar equipo), y en la configuración B, módulo de bromelaína
  (aspersión + UF + centrífuga) y prensa dedicada de corazón.
"""
import json, os, math, sys, copy, time
import numpy as np
from pyscipopt import Model, quicksum
import capacidad as cp
import planta_trl9 as pt
import planificacion_milp as pm
import tea_burk as tb
import tea_lineas as tl
import params as p
import moresi as mo

RES = os.path.join(os.path.dirname(__file__), "results")
DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
HM = DAYS * 24.0
A2 = cp.calendar_hours("burk") / 8766.0          # lun–sáb, 2 turnos de 6 h efectivas
A3 = 1.5 * A2                                     # con tercer turno
AC = 0.9                                          # procesos continuos (bodega, secador)
C = tb.COMMON
CRF = C["tasa"] * (1 + C["tasa"]) ** C["anios"] / ((1 + C["tasa"]) ** C["anios"] - 1)
VF, T_PROC = 10.0, 12.5 + 2.5                     # fermentador de 10 m³; fermentación + descarga/limpieza (h)
SUPPLY = 6146.0                                    # EVA 2022, Chocó
WINE_PRICE = 3000.0                                # COP/L (plan del MILP y moda del programa estocástico)
FRUIT_PRICE = 400.0                                # COP/kg puesto en planta (TEA)
COMPOST = pm.COMPOST_COP_kg
CH_COST = 2e4                                      # COP por cambio de material en la prensa (aguas, CIP corto)
SIGMA = 1.0                                        # h de limpieza por cambio


# ----------------------------------------------------------------------------- costos de las opciones
def _lang():
    D = pt.design(6200)
    x = tb.capex(tl.to_equipment(D["lines"]["vino"]["equipment"] + D["lines"]["harina"]["equipment"]))
    return x["FCI"] / x["purchase"]


LANG = _lang()
AF = LANG * (CRF + C["mantenimiento"] + C["impuestos_locales"])     # COP/año por COP de compra


def buy(cat, need):
    """Costo de compra (COP base) de la combinación de catálogo más barata que cubre 'need'."""
    if need <= 0:
        return 0.0
    n, s, _ = pt.pick(cat, need)
    k = pt.CAT[cat]
    return tb.equipment_cost(dict(qty=n, size=s, ref_size=k["ref"][0], ref_USD=k["ref"][1], n=k["n"]))[0]


def ferm_cost(n):
    return tb.equipment_cost(dict(qty=n, size=VF, ref_size=VF, ref_USD=pt.fermenter_moresi(VF, True), n=1.0))[0]


B1 = cp.full_balance(1.0)
FR = dict(pulpa=B1["pulp_t"], cascara=B1["peel_t"], corazon=B1["core_t"])
JUICE = cp.JUICE_YIELD_PULP / cp.RHO_JUICE                 # m³ jugo / t pulpa
CAKE = 1 - cp.Y["peel_juice_frac"]                         # t torta / t cáscara
CORE_J = cp.Y["core_juice_frac"]
FLOUR_PC = (B1["flour_t"] / B1["peel_t"]) / CAKE           # t harina / t torta
WINE_PM = 1 - cp.WINE_LOSS                                 # m³ vino / m³ mosto
HEAT_KW_PER_M3H = 1000 * p.S_JUICE / 180.16 * 96.6 / 3600 * 2.0


def options(with_bromelain=False):
    """Opciones discretas por equipo: lista de dict(lab, cap, cost[COP compra]). cap en la unidad de flujo del equipo."""
    O = {}
    O["Frente"] = [dict(lab=f"{s:g} t/h", cap=s, cost=buy("lavado_seleccion", s) + buy("peladora_descorazonadora", s))
                   for s in (1, 2, 3, 5, 8)]
    O["Prensa"] = [dict(lab=f"{s:g} t/h", cap=s, cost=buy("prensa_banda", s) + buy("trituradora", s) + buy("macerador_camisa", s / 1.06 * 1.2))
                   for s in (1, 2, 3, 5, 8)]
    O["Prensa cáscara"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{s:g} t/h", cap=s, cost=buy("prensa_banda", s) + buy("trituradora", s)) for s in (1, 2, 3)]
    O["MF"] = [dict(lab=f"{A:g} m²", cap=A * 60 / 1000, cost=buy("MF_ceramica", A) + buy("pasteurizador_placas", A * 60))
               for A in (10, 20, 30, 40, 60, 80, 120)]
    O["Bodega"] = [dict(lab=f"{n}×10 m³", cap=(n - 1) * VF / T_PROC,
                        cost=ferm_cost(n) + buy("chiller", (n - 1) * VF / T_PROC * HEAT_KW_PER_M3H * 1.1)
                        + buy("centrifuga_discos", (n - 1) * VF / T_PROC * 1.5) + buy("filtro_cartuchos", (n - 1) * VF / T_PROC * 1.5)
                        + buy("propagador", 0.5))
                   for n in range(2, 13)]
    O["Secador"] = [dict(lab=f"{s:g} kg agua/h", cap=s / 1000 * 1.35,
                         cost=buy("secador_banda", s) + buy("caldera", s * 3.2 / 3.6 * 1.1) + buy("molino_tamiz", s / 1000 * 1.35 * FLOUR_PC * 1000))
                    for s in (50, 100, 200, 300, 500, 800)]
    O["Almacén de mosto"] = [dict(lab=f"{V:g} m³", cap=V, cost=(buy("tanque_pulmon", V) if V <= 50 else 1.4 * buy("tanque_guarda", V)))
                             for V in (10, 25, 50, 100, 200, 400, 800)]
    if with_bromelain:
        O["Aspersión"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
            dict(lab=f"{s:g} kg agua/h", cap=s / 1000 / 0.12,
                 cost=buy("spray_dryer", s) + buy("UF_bromelaina", s / 0.12 / 25) + buy("centrifuga_discos", s / 1000 / 0.12)
                 + buy("tanque_precipitacion", s / 1000 / 0.12 * 0.4) + buy("cuarto_frio", 10))
            for s in (5, 10, 25, 50)]
        O["Prensa corazón"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
            dict(lab=f"{s:g} t/h", cap=s, cost=buy("prensa_banda", s) + buy("trituradora", s)) for s in (1, 2)]
    return O


REFERENCE = {   # diseño TRL-9 a 6 200 t/año (planta_trl9.design): lavado 2 t/h, prensa de pulpa 1 t/h + prensa de cáscara 1 t/h,
    "Frente": "2 t/h", "Prensa": "1 t/h", "Prensa cáscara": "1 t/h", "MF": "20 m²", "Bodega": "2×10 m³",   # MF 20 m², 2 × 10 m³,
    "Secador": "300 kg agua/h", "Almacén de mosto": "10 m³", "turno3": 0,                                    # secador 300, pulmón 10 m³
}
REFERENCE_B = dict(REFERENCE, **{"Aspersión": "10 kg agua/h", "Prensa corazón": "1 t/h"})


def margins(wine_price=WINE_PRICE, flour_price=None):
    """Márgenes de contribución por unidad de flujo (COP), del TEA de cada línea a 6 200 t/año."""
    D = pt.design(6200)
    cs = tl.cases_from_design(D)
    def var_noraw(key):
        c = cs[key]; r = tb.evaluate(c)
        return r["var"] - sum(rr["qty_year"] * rr["price"] for rr in c["raw"] if rr.get("main"))
    v_w = var_noraw("L1 Vino de piña (rápido, 30 °C)") / (D["lines"]["vino"]["flows"]["juice_m3"])          # COP/m³ mosto
    v_h = var_noraw("L5 Harina de fibra de cáscara") / (D["lines"]["harina"]["flows"]["peel_t"] * CAKE)       # COP/t torta
    v_b = var_noraw("L4 Bromelaína + polvo nutracéutico") / (D["lines"]["bromelaina"]["flows"]["core_t"] * CORE_J)   # COP/t jugo de corazón
    fp = flour_price or tl.M("harina_kg")
    brom_rev = (B1["bromelain_kg"] * tl.M("bromelaina_kg") + B1["powder_t"] * 1000 * 40000.0) / (B1["core_t"] * CORE_J)
    return dict(
        wine=C["vendido"] * wine_price * 1000 * WINE_PM - v_w,
        flour=C["vendido"] * fp * 1000 * FLOUR_PC - v_h,
        brom=C["vendido"] * brom_rev - v_b,
        peel_juice=cp.Y["peel_juice_frac"] * 150.0 * 1000,          # crédito del jugo de cáscara al hub, por t de cáscara prensada
        guard=AF * buy("tanque_guarda", 160) / 160 * 90 / 365 * 1.1,  # tanques de guarda (90 d), COP/año por m³ de vino/año
    )


def shift_cost(with_bromelain=False):
    pos = 4 + 2 + (2 if with_bromelain else 0)
    c2 = tb.calendar(3); c3 = dict(c2, shifts=3)
    return (tb.payroll(pos, c3, engineer=0)["total"] - tb.payroll(pos, c2, engineer=0)["total"]) * (1 + C["supervision"])


# ----------------------------------------------------------------------------- modelo
def build(scen, K=2, with_bromelain=False, fix=None, loss_max=None, allow_shift=True, mg=None, store_max=None):
    """scen: lista de dict(sup=factor de oferta, p=probabilidad). Devuelve (modelo, variables)."""
    O = options(with_bromelain)
    mg = mg or margins()
    modes = ["pulpa", "cascara"] + (["corazon"] if with_bromelain else [])
    ded = {"cascara": "Prensa cáscara", "corazon": "Prensa corazón"}
    nm = len(modes)
    m = Model("dimensionamiento"); m.hideOutput()
    # ---------------- primera etapa: tamaños
    y = {(u, k): m.addVar(vtype="B", name=f"y_{u}_{k}") for u in O for k in range(len(O[u]))}
    for u in O:
        m.addCons(quicksum(y[u, k] for k in range(len(O[u]))) == 1)
    y3 = m.addVar(vtype="B", name="turno3", ub=1 if allow_shift else 0)
    fix = fix or {}
    for u, lab in fix.items():
        if u == "turno3":
            m.addCons(y3 == lab); continue
        if u not in O:
            continue
        k = [o["lab"] for o in O[u]].index(lab)
        m.addCons(y[u, k] == 1)
    if store_max is not None:
        m.addCons(quicksum(O["Almacén de mosto"][k]["cap"] * y["Almacén de mosto", k] for k in range(len(O["Almacén de mosto"]))) <= store_max)
    yded = {j: quicksum(y[ded[j], k] for k in range(1, len(O[ded[j]]))) for j in modes if j in ded and ded[j] in O}
    capex_ann = quicksum(AF * O[u][k]["cost"] * y[u, k] for u in O for k in range(len(O[u]))) + shift_cost(with_bromelain) * y3
    Hx = float(HM.max())
    MT = [(mo_, t) for mo_ in range(12) for t in range(K)]
    chi_fix = dict(fruta=None, pulpa=1.5, cascara=3.0, corazon=2.0, jugo=4.0, torta=12.0, jcor=3.0)
    second = 0.0
    V = dict(y=y, y3=y3, O=O, modes=modes, MT=MT, scen=[])
    for sc in scen:
        supply = SUPPLY * sc["sup"]
        rate_in = supply * pm.SEASON / 12.0 / HM
        chi = dict(chi_fix, fruta=3 * 24 * max(rate_in))
        d = {mt: m.addVar(lb=0, ub=HM[mt[0]]) for mt in MT}
        w = {mt: m.addVar(lb=0, ub=HM[mt[0]]) for mt in MT}                    # w = y3·d
        Hs = {}
        for mo_ in range(12):
            m.addCons(quicksum(d[mo_, t] for t in range(K)) == HM[mo_])
        for mt in MT:
            m.addCons(w[mt] <= d[mt]); m.addCons(w[mt] <= HM[mt[0]] * y3)
            Hs[mt] = A2 * d[mt] + (A3 - A2) * w[mt]                            # horas con personal
        # horas por tamaño elegido (0-1 × continua): g[u,k,mt] ≤ cap_h·y ; Σ_k g ≤ horas disponibles
        def cap_expr(u, mt, staffed):
            g = {k: m.addVar(lb=0) for k in range(len(O[u]))}
            for k in g:
                m.addCons(g[k] <= Hx * y[u, k])
            m.addCons(quicksum(g.values()) <= (Hs[mt] if staffed else AC * d[mt]))
            return quicksum(O[u][k]["cap"] * g[k] for k in g)
        tau = {(i, k, mt): m.addVar(lb=0) for i in modes for k in range(len(O["Prensa"])) for mt in MT}
        ncy = {mt: m.addVar(vtype="I", lb=0, ub=4 * HM[mt[0]]) for mt in MT}
        P = {(i, mt): m.addVar(lb=0) for i in modes for mt in MT}
        Pd = {(j, mt): m.addVar(lb=0) for j in yded for mt in MT}
        fe = {mt: m.addVar(lb=0) for mt in MT}; mfv = {mt: m.addVar(lb=0) for mt in MT}
        bod = {mt: m.addVar(lb=0) for mt in MT}; sec = {mt: m.addVar(lb=0) for mt in MT}
        asp = {mt: m.addVar(lb=0) for mt in MT}
        loss = {mt: m.addVar(lb=0) for mt in MT}
        comp = {mt: m.addVar(lb=0) for mt in MT}                                # cáscara sin prensar a compostaje
        compk = {mt: m.addVar(lb=0) for mt in MT}                               # corazón sin procesar a compostaje
        st = list(chi) + ["mosto"]
        nq = len(MT)
        I = {(k_, q): m.addVar(lb=0, ub=(chi[k_] if k_ in chi else None)) for k_ in st for q in range(nq + 1)}
        for q in range(nq + 1):
            m.addCons(I["mosto", q] <= quicksum(O["Almacén de mosto"][k]["cap"] * y["Almacén de mosto", k] for k in range(len(O["Almacén de mosto"]))))
        for k_ in st:
            m.addCons(I[k_, 0] == I[k_, nq])
        nF = len(O["Frente"])
        for q, mt in enumerate(MT):
            mo_ = mt[0]
            m.addCons(quicksum(tau[i, k, mt] for i in modes for k in range(len(O["Prensa"]))) + SIGMA * ncy[mt] <= Hs[mt])
            for i in modes:
                for k in range(len(O["Prensa"])):
                    m.addCons(tau[i, k, mt] <= Hx * y["Prensa", k])
                m.addCons(P[i, mt] <= quicksum(O["Prensa"][k]["cap"] * tau[i, k, mt] for k in range(len(O["Prensa"]))))
                if i in yded:   # si la fracción tiene prensa dedicada, no pasa por la principal
                    m.addCons(quicksum(tau[i, k, mt] for k in range(len(O["Prensa"]))) <= Hx * (1 - yded[i]))
            # acoplamiento con los pulmones perecederos (anual_continuo.py), con F_max = capacidad del frente elegida:
            #   fr_j · F_max · n_m · τ_i ≤ χ_j · n_ciclos ; F_max·τ_i = Σ_f cap_f · v_fi, v_fi = y_f·τ_i (exacto)
            for i in modes:
                ti = quicksum(tau[i, k, mt] for k in range(len(O["Prensa"])))
                v = {f: m.addVar(lb=0) for f in range(nF)}
                for f in range(nF):
                    m.addCons(v[f] <= Hx * y["Frente", f]); m.addCons(v[f] <= ti)
                    m.addCons(v[f] >= ti - Hx * (1 - y["Frente", f]))
                for j in modes:
                    if j == i:
                        continue
                    Mbig = FR[j] * nm * max(o["cap"] for o in O["Frente"]) * Hx
                    m.addCons(FR[j] * nm * quicksum(O["Frente"][f]["cap"] * v[f] for f in range(nF))
                              <= chi[j] * ncy[mt] + (Mbig * yded[j] if j in yded else 0))
            m.addCons(fe[mt] <= cap_expr("Frente", mt, True))
            m.addCons(mfv[mt] <= cap_expr("MF", mt, True))
            m.addCons(bod[mt] <= cap_expr("Bodega", mt, False))
            m.addCons(sec[mt] <= cap_expr("Secador", mt, False))
            for j in yded:
                m.addCons(Pd[j, mt] <= cap_expr(ded[j], mt, True))
            if with_bromelain:
                m.addCons(asp[mt] <= cap_expr("Aspersión", mt, True))
            else:
                m.addCons(asp[mt] == 0)
            Pc = P["cascara", mt] + (Pd["cascara", mt] if "cascara" in yded else 0)
            Pk = (P["corazon", mt] + (Pd["corazon", mt] if "corazon" in yded else 0)) if with_bromelain else 0
            bal = {
                "fruta": rate_in[mo_] * d[mt] - fe[mt] - loss[mt],
                "pulpa": FR["pulpa"] * fe[mt] - P["pulpa", mt],
                "cascara": FR["cascara"] * fe[mt] - Pc - comp[mt],
                "corazon": (FR["corazon"] * fe[mt] - Pk - compk[mt]) if with_bromelain else 0,
                "jugo": JUICE * P["pulpa", mt] - mfv[mt],
                "mosto": mfv[mt] - bod[mt],
                "torta": CAKE * Pc - sec[mt],
                "jcor": (CORE_J * Pk - asp[mt]) if with_bromelain else 0,
            }
            for k_ in st:
                m.addCons(I[k_, q + 1] == I[k_, q] + bal[k_])
        if loss_max is not None:
            m.addCons(quicksum(loss.values()) <= loss_max * supply)
        unused = FR["corazon"] * (0 if with_bromelain else 1) + B1["crown_t"]
        Pcas = lambda mt: P["cascara", mt] + (Pd["cascara", mt] if "cascara" in yded else 0)
        contrib = quicksum(mg["wine"] * bod[mt] + mg["flour"] * sec[mt] + mg["brom"] * asp[mt] + mg["peel_juice"] * Pcas(mt)
                           - (FRUIT_PRICE * 1000 + COMPOST * 1000 * unused) * fe[mt] - COMPOST * 1000 * (comp[mt] + compk[mt]) - CH_COST * ncy[mt]
                           - mg["guard"] * WINE_PM * bod[mt] for mt in MT)
        second = second + sc["p"] * contrib
        V["scen"].append(dict(sc=sc, supply=supply, d=d, w=w, tau=tau, ncy=ncy, P=P, Pd=Pd, fe=fe, mfv=mfv, bod=bod, sec=sec,
                              asp=asp, loss=loss, comp=comp, I=I, contrib=contrib, Hs=Hs))
    m.setObjective((second - capex_ann) / 1e6, "maximize")
    V["capex_ann"] = capex_ann
    return m, V


def extract(m, V, with_bromelain):
    v = m.getVal
    O = V["O"]
    sizes = {u: O[u][max(range(len(O[u])), key=lambda k: v(V["y"][u, k]))] for u in O}
    out = dict(status=m.getStatus(), gap=m.getGap(), obj=m.getObjVal(), sizes={u: s["lab"] for u, s in sizes.items()},
               caps={u: s["cap"] for u, s in sizes.items()}, turno3=int(round(v(V["y3"]))),
               capex_purchase=sum(s["cost"] for s in sizes.values()), capex_ann=v(V["capex_ann"]) / 1e6,
               FCI=LANG * sum(s["cost"] for s in sizes.values()) / 1e6, scen=[])
    a_st = A3 if out["turno3"] else A2
    for S in V["scen"]:
        rows, T0 = [], 0.0
        for mt in V["MT"]:
            dur = v(S["d"][mt])
            # tiempo efectivo de prensa por material = lo procesado / capacidad (τ del modelo es una cota superior)
            tau = {i: v(S["P"][i, mt]) / sizes["Prensa"]["cap"] for i in V["modes"]}
            rows.append(dict(month=mt[0], k=mt[1], start=T0, dur=dur, tau=tau, W=v(S["ncy"][mt]),
                             P={i: v(S["P"][i, mt]) for i in V["modes"]}, Pd={j: v(S["Pd"][j, mt]) for j, _ in [(a, b) for (a, b) in S["Pd"] if b == mt]},
                             fe=v(S["fe"][mt]), mf=v(S["mfv"][mt]), bod=v(S["bod"][mt]), sec=v(S["sec"][mt]), asp=v(S["asp"][mt]),
                             loss=v(S["loss"][mt]), comp=v(S["comp"][mt]), I_mosto=v(S["I"]["mosto", V["MT"].index(mt) + 1])))
            T0 += dur
        util = {}
        cap = out["caps"]
        for u, key, staffed in (("Frente", "fe", True), ("MF", "mf", True), ("Bodega", "bod", False), ("Secador", "sec", False),
                                ("Aspersión", "asp", True)):
            if u not in cap or cap[u] <= 0:
                continue
            util[u] = [sum(r[key] for r in rows if r["month"] == mo_) / (cap[u] * (a_st if staffed else AC) * HM[mo_]) for mo_ in range(12)]
        util["Prensa"] = [(sum(sum(r["tau"].values()) for r in rows if r["month"] == mo_) + SIGMA * sum(r["W"] for r in rows if r["month"] == mo_))
                          / (a_st * HM[mo_]) for mo_ in range(12)]
        for j, u in (("cascara", "Prensa cáscara"), ("corazon", "Prensa corazón")):
            if u in cap and cap[u] > 0:
                util[u] = [sum(r["Pd"].get(j, 0) for r in rows if r["month"] == mo_) / (cap[u] * a_st * HM[mo_]) for mo_ in range(12)]
        prod = dict(fruta_t=sum(r["fe"] for r in rows), cascara_compost_t=sum(r["comp"] for r in rows), vino_m3=sum(r["bod"] for r in rows) * WINE_PM,
                    harina_t=sum(r["sec"] for r in rows) * FLOUR_PC,
                    bromelaina_kg=sum(r["asp"] for r in rows) * B1["bromelain_kg"] / (B1["core_t"] * CORE_J))
        out["scen"].append(dict(sup=S["sc"]["sup"], p=S["sc"]["p"], supply=S["supply"], contrib=v(S["contrib"]) / 1e6, periods=rows,
                                util=util, loss=sum(r["loss"] for r in rows), loss_month=[sum(r["loss"] for r in rows if r["month"] == mo_) for mo_ in range(12)],
                                supply_month=(S["supply"] * pm.SEASON / 12.0).tolist(), changeovers=sum(r["W"] for r in rows), products=prod,
                                margin=v(S["contrib"]) / 1e6 - out["capex_ann"]))
    return out


def solve(scen=None, K=2, with_bromelain=False, time_limit=240, gap=0.005, **kw):
    scen = scen or [dict(sup=1.0, p=1.0)]
    m, V = build(scen, K=K, with_bromelain=with_bromelain, **kw)
    m.setParam("limits/time", time_limit); m.setParam("limits/gap", gap)
    t0 = time.time(); m.optimize()
    if m.getNSols() == 0:
        return dict(status=m.getStatus())
    r = extract(m, V, with_bromelain); r["t"] = time.time() - t0
    return r


def brief(r):
    s = r["scen"][0] if r.get("scen") else {}
    return (f"{r['status']} gap {r['gap']:.3%} obj {r['obj']:,.0f} | FCI {r['FCI']:,.0f} | {r['sizes']} T3={r['turno3']} | "
            f"pérdida {sum(x['loss'] for x in r['scen']) / sum(x['supply'] for x in r['scen']):.1%} | cambios {s.get('changeovers', 0):.0f}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["E1", "E2", "E3", "E4", "E5"]
    path = f"{RES}/dimensionamiento.json"
    out = json.load(open(path)) if os.path.exists(path) else {}
    save = lambda: json.dump(out, open(path, "w"), default=float)
    print("Lang eq.", round(LANG, 3), "AF", round(AF, 4), "turno 3 MM COP/año", round(shift_cost() / 1e6, 1),
          {k: round(v_) for k, v_ in margins().items()}, flush=True)
    if "E1" in which:   # óptimo vs referencia TRL-9
        for lab, kw in (("Referencia TRL-9 (planta_trl9, 6 200 t)", dict(fix=REFERENCE)),
                        ("Referencia con prensa única de 3 t/h compartida", dict(fix=dict(REFERENCE, **{"Prensa": "3 t/h", "Prensa cáscara": "no"}))),
                        ("Óptimo económico", {}),
                        ("Óptimo sin pérdida de fruta", dict(loss_max=0.0))):
            r = solve(**kw); out[f"E1|{lab}"] = r; save(); print("E1", lab, brief(r), flush=True)
    if "E2" in which:   # regla de dimensionamiento: tamaños óptimos según la oferta (0,5× a la base de la tesis)
        for f in (0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 21856 / SUPPLY):
            r = solve(scen=[dict(sup=f, p=1.0)], time_limit=300); out[f"E2|{f:.3f}"] = r; save(); print("E2", round(f, 3), brief(r), flush=True)
    if "E3" in which:   # valor del almacenamiento aséptico y del tercer turno, a 2× la oferta actual
        sc2 = [dict(sup=2.0, p=1.0)]
        for lab, kw in (("libre (almacén y turno 3 disponibles)", {}),
                        ("sin almacén aséptico (≤ 25 m³)", dict(store_max=25)),
                        ("sin turno 3", dict(allow_shift=False)),
                        ("sin almacén ni turno 3", dict(store_max=25, allow_shift=False))):
            r = solve(scen=sc2, time_limit=300, **kw); out[f"E3|{lab}"] = r; save(); print("E3", lab, brief(r), flush=True)
    if "E4" in which:   # dimensionamiento estocástico (oferta 0,7 / 1,0 / 1,3) — Grossmann cap. 14
        import estocastico as es
        sc = [dict(sup=a, p=pa) for a, pa in es.SUP_F]
        rp = solve(scen=sc, time_limit=600); out["E4|RP"] = rp; save(); print("E4 RP", brief(rp), flush=True)
        ev = solve(scen=[dict(sup=sum(a * pa for a, pa in es.SUP_F), p=1.0)]); out["E4|EV"] = ev; save(); print("E4 EV", brief(ev), flush=True)
        fixev = dict(ev["sizes"], turno3=ev["turno3"])
        eev = solve(scen=sc, fix=fixev, time_limit=600); out["E4|EEV"] = eev; save(); print("E4 EEV", brief(eev), flush=True)
        ws = [solve(scen=[dict(sup=a, p=1.0)]) for a, pa in es.SUP_F]
        out["E4|WS"] = dict(obj=sum(r["obj"] * pa for r, (a, pa) in zip(ws, es.SUP_F)), each=[dict(sup=a, obj=r["obj"], sizes=r["sizes"], turno3=r["turno3"]) for r, (a, pa) in zip(ws, es.SUP_F)])
        save(); print("E4 WS", out["E4|WS"]["obj"], "VSS", rp["obj"] - eev["obj"], "EVPI", out["E4|WS"]["obj"] - rp["obj"], flush=True)
    if "E5" in which:   # configuración B con bromelaína: ¿prensa compartida o dedicada?
        for lab, kw in (("B referencia (prensas dedicadas TRL-9)", dict(fix=REFERENCE_B)),
                        ("B óptimo económico", {}), ("B óptimo con pérdida ≤ 1 %", dict(loss_max=0.01))):
            r = solve(with_bromelain=True, **kw); out[f"E5|{lab}"] = r; save(); print("E5", lab, brief(r), flush=True)
    save()
