"""
v14: análisis multiescala del diseño (micro → equipo → planta → territorio → economía).

El óptimo de la tesis resulta de modelos a cinco escalas acoplados por pocas variables. Este guion mide qué pasa en
las interfaces que hasta v13 se trataban en un solo sentido:

  U  hacia arriba (cinética → planta): un solo punto final del ensayo (65,3 g/L de etanol a 12,5 h; Murcia Palacios
     2013) no fija la escala de velocidad y el inóculo por separado (fig. 3). Si la planta inocula distinto del ensayo,
     todos los tiempos de fermentación quedan definidos solo dentro de una banda. Se toma la banda de Krishnan et al.
     (1999) calibrada sobre la curva no identificable (inóculo del ensayo de 0,05 a 2 g/L, planta a 0,5 g/L), se lleva
     a los tiempos de proceso del MILP y se reoptimiza en los extremos; también se evalúa el diseño central con
     los tiempos extremos (lo que se pierde por no saber la cinética).
  D1 hacia abajo (planta → semana): con los tamaños del óptimo, una red estado-tarea (STN) cíclica de 168 h en
     tiempo discreto de una hora (Maravelias 2021, ecs. 7.4–7.6; programa periódico, cap. 10) programa la semana de
     más fruta procesada: turnos, limpieza al cambiar de material en la prensa compartida, lotes enteros de 10 m³,
     llenado de los fermentadores como ocupación del recipiente (Moresi 1989b) y pulmones finitos. Pregunta: ¿cabe
     en horas lo que el MILP mensual reparte en promedios?
  D2 hacia abajo (planta → tren de fermentación): el modelo 1 (Corsano et al. 2004, 2006a) se dimensionó con la base
     de diseño de la tesis original (7 830 m³ de vino al año). Se recalcula el valor de decidir cinética y tamaños a
     la vez (jerárquico frente a simultáneo) con el flujo real del óptimo (375 m³/año).
  T  planta ↔ territorio: el costo de acopio de hojas sale de la localización estilizada (sitio B, sin depósitos).
     Se mide el valor de acoplar esa decisión: óptimo de planta con el costo de cada configuración de acopio y
     pérdida de un diseño hecho con el costo equivocado.

Uso: python multiescala_v14.py U | D1 | D2 | T        (cada grupo escribe results/v14/<grupo>.json)
"""
import json, math, os, sys, time
import numpy as np
import dimensionamiento as dm

OUT = os.path.join(dm.RES, "v14")
os.makedirs(OUT, exist_ok=True)
D12 = json.load(open(os.path.join(dm.RES, "dimensionamiento.json")))
OPT = D12["E1|Óptimo económico"]
T0 = dict(T_PROC=dm.T_PROC, T_PEEL=dm.T_PEEL, T_LEAF=dm.T_LEAF)
CLEAN = 2.5                                     # h de descarga y limpieza incluidas en cada tiempo de proceso


def design(r):
    return dict(r["sizes"], turno3=r["turno3"])


def save(name, res):
    json.dump(res, open(os.path.join(OUT, f"{name}.json"), "w"), indent=1, default=float)


def short(r):
    if not r.get("scen"):
        return dict(status=r.get("status"))
    s = r["scen"][0]; p = s["products"]
    keep = ("fruta_t", "hojas_t", "vino_m3", "botellas", "vinagre_m3", "harina_t", "jugo_cascara_vinagre_t", "jugo_hojas_vinagre_t",
            "azucar_kg", "acido_kg", "gwp_kg")
    return dict(status=r["status"], gap=r["gap"], obj=r["obj"], margin=s["margin"], FCI=r["FCI"], sizes=r["sizes"], turno3=r["turno3"],
                products={k: p.get(k, 0.0) for k in keep}, util={k: max(v) for k, v in s["util"].items()})


def tea(full, label):
    import tea_dimensionado as td, tea_burk as tb
    if not full or not full.get("scen") or full["scen"][0]["products"].get("fruta_t", 0.0) < 1:
        return None
    c = td.build_case(full, label, False)
    r = tb.evaluate(c)
    return dict(NPV=r["NPV"] / 1e6, MIRR=r["MIRR"], FCI=r["FCI"] / 1e6)


def set_times(f=None, **t):
    """f = factor sobre la parte de fermentación de los tres tiempos (la descarga de 2,5 h no cambia)."""
    if f is not None:
        t = {k: (v - CLEAN) * f + CLEAN for k, v in T0.items()}
    for k, v in (t or T0).items():
        setattr(dm, k, v)
    return {k: getattr(dm, k) for k in T0}


# ================================================================== U: banda cinética → MILP
def kinetic_band():
    """Curva no identificable (escala de velocidad, inóculo del ensayo) con la cinética de Krishnan: para cada inóculo
    supuesto del ensayo x se calibra el factor de tiempo k(x) que reproduce 65,3 g/L a 12,5 h y se calculan los tiempos
    de la planta. Caso A: la planta inocula como el ensayo (x). Caso B: la planta inocula a 0,5 g/L (cinetica_jugos)."""
    import cinetica_jugos as cj, params as p, datos as D
    tP = lambda r, P: float(r["t"][int(np.argmax(r["P"] >= P))])
    gx = D.val("xilosa_jugo_hojas"); gg = 45.0 - gx; Sp = D.val("azucar_jugo_cascara") * 1.06
    X0p = cj.X0
    pulp_p, peel_p, leaf_p = cj.batch(p.S_JUICE, 0, X0=X0p), cj.batch(Sp, 0, X0=X0p), cj.batch(gg, gx, X0=X0p)
    rows = []
    for x in np.geomspace(0.05, 2.0, 13):
        ref = cj.batch(p.S_JUICE, 0, X0=x, t_end=200)
        k = p.T_REF / tP(ref, p.P_REF)
        pe, le = cj.batch(Sp, 0, X0=x, t_end=300), cj.batch(gg, gx, X0=x, t_end=300)
        rows.append(dict(x=float(x), k=k,
                         A=dict(pulpa=p.T_REF, cascara=k * pe["t95"], hojas=k * le["t95"]),
                         B=dict(pulpa=k * tP(pulp_p, p.P_REF), cascara=k * peel_p["t95"], hojas=k * leaf_p["t95"])))
    kc = next(r["k"] for r in rows if abs(r["x"] - X0p) / X0p < 0.05) if any(abs(r["x"] - X0p) / X0p < 0.05 for r in rows) \
        else float(np.interp(np.log(X0p), [math.log(r["x"]) for r in rows], [r["k"] for r in rows]))
    for r in rows:
        r["f"] = r["k"] / kc                      # factor común de tiempo (caso B) frente al supuesto central
    fA = [r["A"]["cascara"] for r in rows]
    return dict(rows=rows, k_central=kc, f_min=min(r["f"] for r in rows), f_max=max(r["f"] for r in rows),
                caseA_cascara=(min(fA), max(fA)))


def run_U():
    res = dict(band=kinetic_band()); save("U", res)
    b = res["band"]
    print(f"banda: f {b['f_min']:.2f}–{b['f_max']:.2f}; caso A cáscara {b['caseA_cascara'][0]:.1f}–{b['caseA_cascara'][1]:.1f} h", flush=True)
    dm.HP_ON = False
    res["central"] = dict(times=set_times(), opt=short(OPT), tea=tea(OPT, "central"))
    for lab, f in (("rapido", b["f_min"]), ("lento", b["f_max"])):
        t = set_times(f)
        r = dm.solve(time_limit=420, hint=design(OPT))
        e = dm.solve(fix=design(OPT), time_limit=200, gap=0.002)
        res[lab] = dict(f=f, times=t, reopt=short(r), reopt_tea=tea(r, lab), central_fijo=short(e), central_fijo_tea=tea(e, lab + "_fijo"))
        save("U", res)
        print(lab, {k: round(v, 1) for k, v in t.items()}, "reopt", round(r.get("obj", float("nan"))), r.get("sizes", {}).get("Bodega"),
              r.get("sizes", {}).get("Bodega cáscara"), "| central fijo", round(e.get("obj", float("nan"))), flush=True)
    # extremo más exigente: la cinética lenta y la bodega de jugos al límite del registro (27,1 h de Krishnan para hojas)
    t = set_times(T_PROC=res["lento"]["times"]["T_PROC"], T_PEEL=res["lento"]["times"]["T_PEEL"], T_LEAF=27.08)
    r = dm.solve(time_limit=420, hint=design(OPT)); e = dm.solve(fix=design(OPT), time_limit=200, gap=0.002)
    res["lento_hojas_krishnan"] = dict(times=t, reopt=short(r), reopt_tea=tea(r, "lento_k"), central_fijo=short(e),
                                       central_fijo_tea=tea(e, "lento_k_fijo"))
    save("U", res); set_times()
    print("lento + hojas 27,1 h: reopt", round(r.get("obj", float("nan"))), "central fijo", round(e.get("obj", float("nan"))), flush=True)


# ================================================================== D1: STN semanal con los tamaños del óptimo
def week_loads(r, month=None):
    """Cargas de la semana (7/31 del mes de más fruta procesada) y razones de conversión tomadas del propio MILP."""
    S = r["scen"][0]
    per = [p for p in S["periods"] if p["dur"] > 0]
    agg = {}
    for p in per:
        a = agg.setdefault(p["month"], {})
        for k in ("fe", "mf", "bod", "sec", "ldry", "pj", "hx", "hjv", "acid", "wv", "az"):
            a[k] = a.get(k, 0.0) + p[k]
        a["Ppulpa"] = a.get("Ppulpa", 0.0) + p["P"]["pulpa"]; a["Pcasc"] = a.get("Pcasc", 0.0) + p["P"]["cascara"]
    if month is None:
        month = max(agg, key=lambda m: agg[m]["fe"])
    a = agg[month]; w = 7.0 / dm.DAYS[month]
    L = dict(month=month, fruta=a["fe"] * w, hojas=a["hx"] * w, acido=a["acid"] * w, botellado=(dm.WINE_PM * a["bod"] - a["wv"]) * w,
             mosto=a["bod"] * w)
    R = dict(pulpa=a["Ppulpa"] / a["fe"], cascara=a["Pcasc"] / a["fe"], jugo=a["mf"] / a["Ppulpa"], mosto=a["bod"] / a["mf"],
             lias=dm.LEES_DRY_EQ * a["ldry"] / a["mf"], pj=dm.PJ_FRAC["agua"], torta=dm.CAKE_FRAC["agua"], jh=dm.JF_H,
             acido=a["acid"] / (a["pj"] + a["hjv"]))
    return L, R


def stn(L, R, caps, T_pulp, T_juice, open_hours, time_limit=240, label="", weeks=1, replicate=True):
    """weeks > 1: horizonte cíclico de varias semanas iguales (los lotes de 8–10 m³ pueden cruzar de una semana a otra)."""
    from pyscipopt import Model, quicksum
    HZ = 168 * weeks
    L = dict(L, **{k: L[k] * weeks for k in ("fruta", "hojas", "acido", "botellado", "mosto")})
    if replicate:
        open_hours = {h + 168 * w for h in open_hours for w in range(weeks)}
    VF = dm.VF
    VJ = VF * 1.04                                   # t de jugo por fermentador de 10 m³
    tp, tj = int(math.ceil(T_pulp - 1e-6)), int(math.ceil(T_juice - 1e-6))
    nP = nJ = 2
    shift = lambda n: (n % HZ) in open_hours
    # tareas: unidades, τ, consumo, producción, ¿con turno?, capacidad por lote
    T = {
        "Fraccionar": dict(u=["Frente"], tau=1, c={"fruta": 1.0}, p={"pulpa": R["pulpa"], "cascara": R["cascara"]}, sh=True, cap=caps["Frente"]),
        "Prensar pulpa": dict(u=["Prensa"], tau=1, c={"pulpa": 1.0}, p={"jugo": R["jugo"]}, sh=True, cap=caps["Prensa"]),
        "Prensar cáscara": dict(u=["Prensa"], tau=1, c={"cascara": 1.0}, p={"jj": R["pj"], "torta": R["torta"]}, sh=True, cap=caps["Prensa"]),
        "Flotar": dict(u=["Flotación"], tau=1, c={"jugo": 1.0}, p={"mosto": R["mosto"], "torta": R["lias"]}, sh=True, cap=caps["Clarificación"]),
        "Embotellar": dict(u=["Embotelladora"], tau=1, c={"vino": 1.0}, p={"botellado": 1.0}, sh=True, cap=caps["Embotelladora"]),
        "Extraer hojas": dict(u=["Extractora"], tau=1, c={"hojas": 1.0}, p={"jj": R["jh"]}, sh=True, cap=caps["Extractora hojas"]),
    }
    for j in range(nP):
        T[f"Llenar F{j + 1}"] = dict(u=[f"F{j + 1}"], tau=1, c={"mosto": 1.0}, p={f"cF{j + 1}": 1.0}, sh=False, cap=VF)
        T[f"Fermentar F{j + 1}"] = dict(u=[f"F{j + 1}"], tau=tp, c={f"cF{j + 1}": 1.0}, p={"vino": dm.WINE_PM}, sh=False, cap=VF, lo=0.8 * VF)
    for j in range(nJ):
        T[f"Llenar J{j + 1}"] = dict(u=[f"J{j + 1}"], tau=1, c={"jj": 1.0}, p={f"cJ{j + 1}": 1.0}, sh=False, cap=VJ)
        T[f"Fermentar J{j + 1}"] = dict(u=[f"J{j + 1}"], tau=tj, c={f"cJ{j + 1}": 1.0}, p={"vc": 1.0}, sh=False, cap=VJ, lo=0.8 * VJ)
    chi = dict(fruta=L["fruta"] / 6 / weeks * 3, pulpa=1.5, cascara=3.0, jugo=2.0, mosto=caps["Almacén de mosto"], vino=160.0, botellado=1e9,
               hojas=L["hojas"] / 6 / weeks * 2, jj=1.0, vc=10.0, torta=12.0)
    for j in range(nP):
        chi[f"cF{j + 1}"] = VF
    for j in range(nJ):
        chi[f"cJ{j + 1}"] = VJ
    deliv = {n for n in range(HZ) if n % 24 == 6 and (n % 168) // 24 < 6}
    m = Model("STN_v14"); m.hideOutput()
    X, B = {}, {}
    for i, d in T.items():
        for j in d["u"]:
            for n in range(HZ):
                if d["sh"] and not all(shift(n + q) for q in range(d["tau"])):
                    continue
                X[i, j, n] = m.addVar(vtype="B"); B[i, j, n] = m.addVar(lb=0, ub=d["cap"])
                m.addCons(B[i, j, n] <= d["cap"] * X[i, j, n])
                if d.get("lo"):
                    m.addCons(B[i, j, n] >= d["lo"] * X[i, j, n])
    units = sorted({j for d in T.values() for j in d["u"]})
    for j in units:                                                              # (7.4) cíclico
        for n in range(HZ):
            terms = [X[i, j, (n - q) % HZ] for i, d in T.items() if j in d["u"] for q in range(d["tau"]) if (i, j, (n - q) % HZ) in X]
            if len(terms) > 1:
                m.addCons(quicksum(terms) <= 1)
    for n in range(HZ):                                                          # limpieza de 1 h al cambiar de material
        for a, b in (("Prensar pulpa", "Prensar cáscara"), ("Prensar cáscara", "Prensar pulpa")):
            if (a, "Prensa", n) in X and (b, "Prensa", (n + 1) % HZ) in X:
                m.addCons(X[a, "Prensa", n] + X[b, "Prensa", (n + 1) % HZ] <= 1)
    I = {(k, n): m.addVar(lb=0, ub=chi[k]) for k in chi for n in range(HZ)}
    acet = {n: m.addVar(lb=0, ub=caps["Acetificador"]) for n in range(HZ)}       # kg ácido/h, continuo (aireación sin parar)
    dry = {n: m.addVar(lb=0, ub=caps["Secador"]) for n in range(HZ)}             # t torta/h, continuo
    over = {n: m.addVar(lb=0) for n in range(HZ)}                                # torta sobrante a compost
    dump = {(k, n): m.addVar(lb=0) for k in ("fruta", "hojas", "mosto", "jj", "vc") for n in range(HZ)}   # pérdidas (penalizadas)
    for n in range(HZ):                                                          # (7.6) cíclico
        n1 = (n + 1) % HZ
        for k in chi:
            prod = quicksum(d["p"][k] * B[i, j, (n - d["tau"] + 1) % HZ] for i, d in T.items() if k in d["p"] for j in d["u"]
                            if (i, j, (n - d["tau"] + 1) % HZ) in B)
            cons = quicksum(d["c"][k] * B[i, j, n] for i, d in T.items() if k in d["c"] for j in d["u"] if (i, j, n) in B)
            sup = (L["fruta"] / len(deliv) if k == "fruta" and n in deliv else 0.0) + (L["hojas"] / len(deliv) if k == "hojas" and n in deliv else 0.0)
            extra = 0.0
            if k == "vc":
                extra = -acet[n] / R["acido"]
            if k == "torta":
                extra = -dry[n] - over[n]
            if k == "botellado":
                continue
            dmp = dump[k, n] if (k, n) in dump else 0.0
            m.addCons(I[k, n1] == I[k, n] + prod - cons + sup + extra - dmp)
        for j in range(nP):                                                      # el fermentador arranca lleno y queda vacío
            if (f"Fermentar F{j + 1}", f"F{j + 1}", n) in X:
                m.addCons(I[f"cF{j + 1}", n1] <= VF * (1 - X[f"Fermentar F{j + 1}", f"F{j + 1}", n]))
        for j in range(nJ):
            if (f"Fermentar J{j + 1}", f"J{j + 1}", n) in X:
                m.addCons(I[f"cJ{j + 1}", n1] <= VJ * (1 - X[f"Fermentar J{j + 1}", f"J{j + 1}", n]))
    bott = quicksum(B["Embotellar", "Embotelladora", n] for n in range(HZ) if ("Embotellar", "Embotelladora", n) in B)
    s_acid = m.addVar(lb=0); s_bott = m.addVar(lb=0)
    m.addCons(quicksum(acet.values()) + s_acid >= L["acido"])
    m.addCons(bott + s_bott >= L["botellado"])
    nX = quicksum(X.values())
    m.setObjective(1000 * quicksum(dump.values()) + 10 * s_acid / R["acido"] + 1000 * s_bott + 0.001 * nX, "minimize")
    m.setParam("limits/time", time_limit); m.setParam("limits/gap", 1e-3)
    t0 = time.time(); m.optimize()
    if m.getNSols() == 0:
        return dict(status=m.getStatus(), label=label)
    v = m.getVal
    sched = [dict(task=i, unit=j, start=n, dur=T[i]["tau"], size=v(B[i, j, n])) for (i, j, n), x in X.items() if v(x) > 0.5]
    busy = {j: sum(s["dur"] for s in sched if s["unit"] == j) for j in units}
    avail = {j: (len(open_hours) if any(T[i]["sh"] for i in T if j in T[i]["u"]) else HZ) for j in units}
    dumps = {k: sum(v(dump[k, n]) for n in range(HZ)) for k in ("fruta", "hojas", "mosto", "jj", "vc")}
    out = dict(label=label, status=m.getStatus(), gap=m.getGap(), t=time.time() - t0, nbin=len(X), loads=L, ratios=R,
               T_pulp=T_pulp, T_juice=T_juice, weeks=weeks, tau=dict(pulpa=tp, jugos=tj), open_h=len(open_hours),
               schedule=sched, util={j: busy[j] / avail[j] for j in units}, dumps=dumps,
               acid=sum(v(a) for a in acet.values()), acid_target=L["acido"], short_acid=v(s_acid), bottled=v(bott), short_bott=v(s_bott),
               acet=[v(acet[n]) for n in range(HZ)], dry=[v(dry[n]) for n in range(HZ)],
               inv={k: [v(I[k, n]) for n in range(HZ)] for k in chi if k not in ("botellado",)},
               changeovers=sum(1 for n in range(HZ) for a, b in (("Prensar pulpa", "Prensar cáscara"), ("Prensar cáscara", "Prensar pulpa"))
                               if (a, "Prensa", n) in X and v(X[a, "Prensa", n]) > 0.5 and
                               any((b, "Prensa", (n + q) % HZ) in X and v(X[b, "Prensa", (n + q) % HZ]) > 0.5 for q in (2, 3))),
               batches={u: sum(1 for s in sched if s["unit"] == u and s["task"].startswith("Fermentar")) for u in ("F1", "F2", "J1", "J2")})
    print(f"STN {label}: {out['status']} gap {out['gap']:.3%} t {out['t']:.0f} s | pérdidas {({k: round(x, 2) for k, x in dumps.items()})} | "
          f"ácido {out['acid']:.0f}/{L['acido']:.0f} | embotellado {out['bottled']:.1f}/{L['botellado']:.1f} | "
          f"lotes {out['batches']} | util { {k: round(x, 2) for k, x in out['util'].items()} }", flush=True)
    return out


def opt_caps(r):
    O = dm.options()
    return {u: next(o["cap"] for o in O[u] if o["lab"] == r["sizes"][u]) for u in
            ("Frente", "Prensa", "Clarificación", "Embotelladora", "Extractora hojas", "Almacén de mosto", "Acetificador", "Secador")}


def hours(days=range(6), shifts=((6, 12), (14, 20))):
    """Turnos de 6 h efectivas (6–12 y 14–20 h) de lunes a sábado."""
    return {d * 24 + h for d in days for a, b in shifts for h in range(a, b)}


def run_D1():
    res = {}
    caps = opt_caps(OPT); L, R = week_loads(OPT)
    res["caps"] = caps
    res["base"] = stn(L, R, caps, dm.T_PROC, max(dm.T_PEEL, dm.T_LEAF), hours(), label="semana del mes pico"); save("D1", res)
    res["festivo"] = stn(L, R, caps, dm.T_PROC, max(dm.T_PEEL, dm.T_LEAF), hours(days=range(1, 6)), label="semana con lunes festivo"); save("D1", res)
    # banda cinética lenta (U) con el diseño central
    b = kinetic_band()
    t = {k: (v - CLEAN) * b["f_max"] + CLEAN for k, v in T0.items()}
    if True:
        res["lento"] = stn(L, R, caps, t["T_PROC"], max(t["T_PEEL"], t["T_LEAF"]), hours(), label="cinética lenta, diseño central"); save("D1", res)
    # mes del Gantt de la tesis (abril, máxima oferta)
    L4, R4 = week_loads(OPT, month=3)
    res["abril"] = stn(L4, R4, caps, dm.T_PROC, max(dm.T_PEEL, dm.T_LEAF), hours(), label="semana de abril"); save("D1", res)


# ================================================================== D2: modelo 1 con el flujo del óptimo
def run_D2():
    import params as p
    import m1_experimentos as mx
    wine = OPT["scen"][0]["products"]["vino_m3"]
    PR = wine * p.P_REF / p.H
    res = dict(vino_m3=wine, PR=PR, PR_base=p.PR_ETOH, vino_base_m3=p.WINE_VOL_YR)
    cases = {
        "jerarquico": dict(allow_prop=False, fix_T2=12.5, fix_X0=0.2, op2=[(1,), (2,), (3,), (4,), (6,), (8,), (12,)]),
        "intermedio": dict(fix_T2=12.5, op2=[(1,), (2,), (3,), (4,), (6,), (8,), (12,)]),
        "simultaneo": dict(),
    }
    for tau in (12.5, 3.0):
        res[str(tau)] = {}
        for name, kw in cases.items():
            if "op2" in kw:
                kw = dict(kw, op2=[a for a in kw["op2"] if a[0] * tau >= 12.5 - 1e-9])
            rs = mx.pool_map(mx.multistart_jobs(dict(kw, tau_fill=tau, PR=PR), range(8)))
            b = mx.best_of(rs)
            res[str(tau)][name] = mx.slim(b) if b.get("ok") else dict(ok=False, TAC=None)
            print("D2", tau, name, b.get("ok"), round(b["TAC"]) if b.get("ok") else None, b.get("label"), flush=True)
        j, s = res[str(tau)]["jerarquico"].get("TAC"), res[str(tau)]["simultaneo"].get("TAC")
        res[str(tau)]["ahorro"] = (j - s) / j if j and s else None
        save("D2", res)
    old = json.load(open(os.path.join(dm.RES, "m1_E6.json")))
    res["base_tesis"] = {t: (old[t]["jerarquico"]["TAC"] - old[t]["simultaneo"]["TAC"]) / old[t]["jerarquico"]["TAC"]
                         for t in ("12.5", "3.0") if old[t]["jerarquico"].get("TAC") and old[t]["simultaneo"].get("TAC")}
    save("D2", res)
    print("D2 ahorro simultáneo:", {t: res[t]["ahorro"] for t in ("12.5", "3.0")}, "base tesis", res["base_tesis"], flush=True)


# ================================================================== T: planta ↔ territorio
def run_T():
    import localizacion as lo
    dm.HP_ON = False
    loc = json.load(open(os.path.join(dm.RES, "localizacion.json")))
    H = loc["hojas_t"]
    configs = {k: v / H for k, v in loc["alternativas"].items()}
    res = dict(configs=configs, costo_central=dm.ACOPIO_VC)
    # ¿la localización cambia con lo que de verdad acopia el óptimo? (punto fijo)
    hojas_opt = OPT["scen"][0]["products"]["hojas_t"]
    fp = lo.solve(hojas_opt, verbose=False)
    res["punto_fijo"] = dict(hojas_t=hojas_opt, sitio=fp["sitio"], depositos=fp["depositos"], costo_t=fp["costo_t"])
    base = dm.ACOPIO_VC
    for lab, c in configs.items():
        dm.ACOPIO_VC = c
        r = dm.solve(time_limit=300, hint=design(OPT))
        dm.ACOPIO_VC = base
        e = dm.solve(fix=design(r), time_limit=180, gap=0.002) if r.get("scen") else {}
        res[lab] = dict(costo_t=c, opt=short(r), evaluado_costo_real=short(e))
        save("T", res)
        print("T", lab, round(c), "óptimo", round(r.get("obj", float("nan"))), "hojas", round(r["scen"][0]["products"]["hojas_t"]) if r.get("scen") else None,
              "| ese diseño con el costo real", round(e.get("obj", float("nan"))), flush=True)
    # acopio en el borde: ¿cuánto vale cada t de hojas? (precio sombra aproximado por diferencia)
    dm.ACOPIO_VC = base * 2
    r2 = dm.solve(time_limit=300, hint=design(OPT)); dm.ACOPIO_VC = base
    res["doble_costo"] = dict(costo_t=base * 2, opt=short(r2))
    save("T", res)
    print("T doble costo", round(r2.get("obj", float("nan"))), flush=True)


def run_D1b():
    """Repeticiones con más tiempo: abril con horizonte de dos semanas (14,6 m³ de mosto por semana no se parten en lotes
    de 8–10 m³ dentro de una sola semana cíclica) y la semana con lunes festivo."""
    which = sys.argv[2] if len(sys.argv) > 2 else "ambas"
    res = json.load(open(os.path.join(OUT, "D1.json")))
    caps = opt_caps(OPT)
    if which in ("abril", "ambas"):
        L4, R4 = week_loads(OPT, month=3)
        res["abril_2sem"] = stn(L4, R4, caps, dm.T_PROC, max(dm.T_PEEL, dm.T_LEAF), hours(), time_limit=1500, label="abril, dos semanas", weeks=2)
        json.dump(res, open(os.path.join(OUT, "D1b_abril.json"), "w"), indent=1, default=float)
    if which in ("festivo", "ambas"):
        L, R = week_loads(OPT)
        res["festivo_largo"] = stn(L, R, caps, dm.T_PROC, max(dm.T_PEEL, dm.T_LEAF), hours(days=range(1, 6)), time_limit=1500,
                                   label="semana con lunes festivo (1 500 s)")
        json.dump(res, open(os.path.join(OUT, "D1b_festivo.json"), "w"), indent=1, default=float)
    if which == "festivo2":
        # semana con lunes festivo seguida de una semana normal (ciclo de dos semanas): la fruta del festivo puede esperar en el patio
        L, R = week_loads(OPT)
        oh = hours(days=range(1, 6)) | {h + 168 for h in hours()}
        res["festivo_2sem"] = stn(L, R, caps, dm.T_PROC, max(dm.T_PEEL, dm.T_LEAF), oh, time_limit=1500,
                                  label="festivo y semana normal (dos semanas)", weeks=2, replicate=False)
        json.dump(res, open(os.path.join(OUT, "D1b_festivo2.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    if sys.argv[1:2] == ["D1b"]:
        run_D1b()
    else:
        for g in sys.argv[1:] or ["U", "D1", "D2", "T"]:
            dict(U=run_U, D1=run_D1, D2=run_D2, T=run_T)[g]()
