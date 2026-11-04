"""
¿Qué procesar con la producción actual y en qué cantidades?  MILP de síntesis + planificación (Grossmann 2021).

Formulación (Grossmann, Advanced Optimization for PSE: cap. 6 cargos fijos con 0-1; cap. 7 lógica proposicional
a desigualdades y disyunciones; cap. 10 GDP con envolvente convexa — aquí la disyunción es la elección de un
tamaño de catálogo por línea, cuya envolvente convexa es exacta con variables 0-1 SOS1):

  max  Σ_m Σ_l (p_l·η_l − c_l)·x_lm − Σ_m [c_GLP·(Q_dem,m − Q_cald,m)⁺ + c_el·(E_dem,m − E_gas,m)⁺]
       − Σ_l Σ_k (CRF·FCI_lk + F_lk)·z_lk − c_comp·(fracciones no usadas)
  s.a. Σ_k z_lk ≤ 1                                  (un tamaño por línea, disyunción)
       x_lm ≤ Σ_k cap_lk·z_lk·h_m/H                  (capacidad mensual)
       fruta_m ≤ oferta_m (estacional, perecedera: sin inventario entre meses)
       pulpa/cáscara/corazón/corona_m = fracción·fruta_m ;  x_l ≤ fracción disponible
       vino_m ≥ vino a vinagre_m ; jugo de cáscara_m ≥ etanol_m
       lógica: z_vinagre ≤ z_vino ; z_etanol ≤ z_harina ; z_vino, z_brom, z_harina ≤ z_frente
El costo de cada opción (FCI, costo fijo, costos y precios por unidad) sale del motor TEA de Burk (tea_burk.py)
evaluado con el diseño TRL-9 de esa escala (planta_trl9.py): es un enfoque polilítico (Kallrath 2021): el MILP
elige y el TEA completo, con impuestos, evalúa la elección.
"""
import json, os, math
import numpy as np
from pyscipopt import Model, quicksum
import tea_burk as tb
import tea_lineas as tl
import planta_trl9 as pt
import capacidad as cp
import params as p

RES = os.path.join(os.path.dirname(__file__), "results")
SCALES = [300, 600, 1000, 1500, 2200, 3200, 4500, 6200, 9000, 13000, 22000]      # t fruta/año equivalentes
LINES = {   # clave del caso TEA, insumo (en el diseño), clave del flujo de entrada, producto, flujo de producto
    "vino": ("L1 Vino de piña (rápido, 30 °C)", "vino", "pulp_t"),
    "vinagre": ("L3 Vinagre (acetador sumergido)", "vinagre", "wine_in_m3"),
    "bromelaina": ("L4 Bromelaína + polvo nutracéutico", "bromelaina", "core_t"),
    "harina": ("L5 Harina de fibra de cáscara", "harina", "peel_t"),
    "etanol": ("L6 Etanol hidratado (jugo de cáscara)", "etanol", "peel_juice_t"),
    "caldera": ("L7b Caldera de biomasa (TRL 9)", None, "crown_t"),
    "gasificador": ("L7a Isla de gasificación (TRL 8)", "energia", "crown_t"),
}
SEASON = np.array([0.80, 0.78, 0.95, 1.20, 1.25, 1.00, 0.85, 0.85, 1.05, 1.20, 1.15, 0.92])   # [S] dos cosechas
SEASON = SEASON / SEASON.mean()
COMPOST_COP_kg = 30.0      # disposición de fracciones no usadas [S]


def option_table():
    """Coeficientes por línea y escala a partir del TEA (evaluado en cada escala)."""
    tab = {l: [] for l in LINES}
    tab["_front_share"] = []
    for s in SCALES:
        D = pt.design(s)
        tab["_front_share"].append(front_share(D))
        cs = tl.cases_from_design(D)
        for l, (ck, lk, fk) in LINES.items():
            c = cs[ck]
            r = tb.evaluate(c)
            if lk:
                inp = D["lines"][lk]["flows"][fk]
            else:
                inp = D["balance"]["crown_t"]
            # separar servicios del costo variable para modelar la sustitución por caldera/gasificador
            heat = sum(u["qty_year"] for u in c["utilities"] if u["name"].startswith("Calor"))
            elec = sum(u["qty_year"] for u in c["utilities"] if u["name"] == "Electricidad")
            main_raw = sum(rr["qty_year"] * rr["price"] for rr in c["raw"] if rr.get("main"))
            var_other = r["var"] - heat * tb.COMMON["calor_COP_MJ"] - elec * tb.COMMON["elec_COP_kWh"] - main_raw
            rev = r["revenue"] / (tb.COMMON["vendido"])                       # ingreso por producción (antes del 95 %)
            out_main = c["product"]["qty_year"]
            crf = 0.1 * 1.1 ** 10 / (1.1 ** 10 - 1)
            tab[l].append(dict(scale=s, cap=inp, FCI=r["FCI"], fixed=r["fixed"], ann=crf * r["FCI"] + r["fixed"],
                               var_per=var_other / inp, heat_per=heat / inp, elec_per=elec / inp,
                               rev_per=rev * tb.COMMON["vendido"] / inp, out_per=out_main / inp,
                               heat_out_per=(heat_boiler(D) / inp if l == "caldera" else 0.0),
                               elec_out_per=(D["lines"]["energia"]["flows"]["E_el_MWh"] * 1000 / inp if l == "gasificador" else 0.0),
                               workers=r["payroll"]["workers"]))
    return tab


def heat_boiler(D):
    return D["balance"]["crown_dm_t"] * 1000 * 17.0 * 0.80


def front_share(D):
    """Fracción del FCI de la línea de vino que corresponde al frente común (lavado + pelado-descorazonado)."""
    eqs = tl.to_equipment(D["lines"]["vino"]["equipment"])
    return tb.capex(eqs[:2])["FCI"] / tb.capex(eqs)["FCI"]


def solve(supply_t, tab, wine_price=None, mode="fruta", force=None, label="", fruit_price=None):
    """mode='fruta': se compra fruta de rechazo entera; mode='residuos': cáscara, corazón y corona de un procesador
    existente a costo de recolección (sin pulpa ni frente de pelado)."""
    b1 = cp.full_balance(1.0)
    sh = dict(pulp=b1["pulp_t"], peel=b1["peel_t"], core=b1["core_t"], crown=b1["crown_t"])
    juice_per_peel = b1["peel_juice_t"] / b1["peel_t"]
    wpp = b1["wine_m3"] / b1["pulp_t"]
    vin_per_wine = b1["vinegar_m3"] / (b1["wine_m3"] * 0.16)
    fs = tab["_front_share"]
    m = Model("planificacion"); m.hideOutput()
    months = range(12)
    sup = supply_t * SEASON / 12.0
    nk = {l: len(tab[l]) for l in LINES}
    z = {(l, k): m.addVar(vtype="B", name=f"z_{l}_{k}") for l in LINES for k in range(nk[l])}
    x = {(l, t): m.addVar(lb=0, name=f"x_{l}_{t}") for l in LINES for t in months}
    F = {t: m.addVar(lb=0, ub=sup[t], name=f"fruta_{t}") for t in months}
    zF = {k: m.addVar(vtype="B", name=f"zF_{k}") for k in range(len(SCALES))}
    LPG = {t: m.addVar(lb=0, name=f"glp_{t}") for t in months}
    DIE = {t: m.addVar(lb=0, name=f"diesel_{t}") for t in months}
    Z = lambda l: quicksum(z[l, k] for k in range(nk[l]))
    for l in LINES:
        m.addCons(Z(l) <= 1)                                               # disyunción: un tamaño
        for t in months:
            m.addCons(x[l, t] <= quicksum(tab[l][k]["cap"] / 12.0 * z[l, k] for k in range(nk[l])))
    m.addCons(quicksum(zF[k] for k in zF) <= 1)
    for t in months:
        if mode == "fruta":
            m.addCons(F[t] <= quicksum(SCALES[k] / 12.0 * zF[k] for k in zF))
        m.addCons(x["vino", t] <= (sh["pulp"] * F[t] if mode == "fruta" else 0))
        m.addCons(x["harina", t] <= sh["peel"] * F[t])
        m.addCons(x["bromelaina", t] <= sh["core"] * F[t])
        m.addCons(x["caldera", t] + x["gasificador", t] <= sh["crown"] * F[t])
        m.addCons(x["vinagre", t] <= wpp * x["vino", t])
        m.addCons(x["etanol", t] <= juice_per_peel * x["harina", t])
        heat_dem = quicksum(float(np.mean([o["heat_per"] for o in tab[l]])) * x[l, t] for l in LINES)
        heat_sup = float(np.mean([o["heat_out_per"] for o in tab["caldera"]])) * x["caldera", t]
        m.addCons(LPG[t] >= heat_dem - heat_sup)
        elec_dem = quicksum(float(np.mean([o["elec_per"] for o in tab[l]])) * x[l, t] for l in LINES)
        elec_sup = float(np.mean([o["elec_out_per"] for o in tab["gasificador"]])) * x["gasificador", t]
        m.addCons(DIE[t] >= elec_dem - elec_sup)
    if mode == "fruta":                                                    # lógica proposicional (Grossmann cap. 7)
        for l in ("vino", "bromelaina", "harina"):
            m.addCons(Z(l) <= quicksum(zF[k] for k in zF))
    m.addCons(Z("vinagre") <= Z("vino"))
    m.addCons(Z("etanol") <= Z("harina"))
    if force:
        for l, val in force.items():
            m.addCons(Z(l) == val)
    wp = wine_price or tl.M("vino_L")
    fp = fruit_price if fruit_price is not None else (tl.M("fruta_kg") if mode == "fruta" else tl.M("corona_kg"))
    mean = lambda l, key: float(np.mean([o[key] for o in tab[l]]))
    obj = 0
    for t in months:
        # vino: todo el vino producido menos el desviado a vinagre, al 95 % vendido
        obj += 0.95 * wp * 1000 * (wpp * x["vino", t] - x["vinagre", t]) - mean("vino", "var_per") * x["vino", t]
        for l in ("vinagre", "bromelaina", "harina", "etanol"):
            obj += (mean(l, "rev_per") - mean(l, "var_per")) * x[l, t]
        obj -= mean("caldera", "var_per") * x["caldera", t] + mean("gasificador", "var_per") * x["gasificador", t]
        obj -= tl.M("jugo_cascara_kg") * 1000 * 0.95 * x["etanol", t]          # el jugo usado deja de venderse
        obj -= fp * 1000 * F[t]
        obj -= COMPOST_COP_kg * 1000 * ((F[t] - x["vino", t] - x["harina", t] - x["bromelaina", t] - x["caldera", t]
                                         - x["gasificador", t]) if mode == "fruta" else
                                        ((sh["peel"] + sh["core"] + sh["crown"]) * F[t] - x["harina", t] - x["bromelaina", t]
                                         - x["caldera", t] - x["gasificador", t]))
        obj -= tb.COMMON["calor_COP_MJ"] * LPG[t] + tb.COMMON["elec_COP_kWh"] * DIE[t]
    for l in LINES:
        for k in range(nk[l]):
            ann = tab[l][k]["ann"] * ((1 - fs[k]) if l == "vino" else 1.0)
            obj -= ann * z[l, k]
    obj -= quicksum(fs[k] * tab["vino"][k]["ann"] * zF[k] for k in zF)
    m.setObjective(obj, "maximize")
    m.setParam("limits/time", 120)
    m.optimize()
    sol = dict(label=label, mode=mode, supply_t=supply_t, wine_price=wp, status=m.getStatus(), obj=m.getObjVal(), gap=m.getGap())
    sol["lines"] = {}
    for l in LINES:
        ks = [k for k in range(nk[l]) if m.getVal(z[l, k]) > 0.5]
        sol["lines"][l] = dict(size_scale=(tab[l][ks[0]]["scale"] if ks else None), cap=(tab[l][ks[0]]["cap"] if ks else 0.0),
                               processed=sum(m.getVal(x[l, t]) for t in months), monthly=[m.getVal(x[l, t]) for t in months],
                               FCI=(tab[l][ks[0]]["FCI"] * ((1 - fs[ks[0]]) if l == "vino" else 1) if ks else 0.0))
    sol["fruit_bought"] = sum(m.getVal(F[t]) for t in months)
    sol["fruit_monthly"] = [m.getVal(F[t]) for t in months]
    sol["supply_monthly"] = sup.tolist()
    ksF = [k for k in zF if m.getVal(zF[k]) > 0.5]
    sol["front_scale"] = SCALES[ksF[0]] if ksF else None
    sol["front_FCI"] = fs[ksF[0]] * tab["vino"][ksF[0]]["FCI"] if ksF else 0.0
    sol["LPG_MJ"] = sum(m.getVal(LPG[t]) for t in months); sol["diesel_kWh"] = sum(m.getVal(DIE[t]) for t in months)
    return sol


if __name__ == "__main__":
    tab = option_table()
    json.dump(tab, open(f"{RES}/milp_options.json", "w"), default=float)
    sols = []
    for lab, s in (("Chocó 2022 completo (6 146 t)", 6146.0), ("50 % de Chocó 2022", 3073.0),
                   ("Pérdida poscosecha 25 % (1 537 t)", 1536.5), ("Base de la tesis (21 856 t)", cp.fruit_for_wine(p.WINE_VOL_YR)[0])):
        for mode, wp, wl in (("fruta", None, "fruta 400 COP/kg, vino 1 600"), ("fruta", 3000.0, "fruta 400 COP/kg, vino 3 000"),
                             ("residuos", None, "residuos de procesador, 80 COP/kg")):
            so = solve(s, tab, wine_price=wp, mode=mode, label=f"{lab} | {wl}")
            sols.append(so)
            act = {l: (round(v['processed']), v['size_scale']) for l, v in so["lines"].items() if v["size_scale"]}
            print(so["label"], so["status"], f"obj {so['obj']/1e6:,.0f} MM COP/año", "fruta", round(so["fruit_bought"]), "frente", so["front_scale"], act, flush=True)
    json.dump(sols, open(f"{RES}/milp_planes.json", "w"), default=float)
    # ---------------------------------------------------------------- barrido oferta × precio del vino × régimen
    sweep = []
    for mode in ("fruta", "residuos"):
        for wp in (1600.0, 2200.0, 3000.0, 4000.0):
            for s_ in (1000, 1500, 2200, 3000, 4000, 5000, 6146, 8000, 11000, 15000, 22000):
                so = solve(float(s_), tab, wine_price=wp, mode=mode, label=f"{mode}|{wp}|{s_}")
                sweep.append(dict(mode=mode, wp=wp, supply=s_, obj=so["obj"],
                                  lines=[l for l, v in so["lines"].items() if v["size_scale"]],
                                  processed={l: v["processed"] for l, v in so["lines"].items()}, fruit=so["fruit_bought"]))
            print("barrido", mode, wp, [round(r["obj"] / 1e6) for r in sweep if r["mode"] == mode and r["wp"] == wp], flush=True)
    json.dump(sweep, open(f"{RES}/milp_barrido.json", "w"), default=float)
    # ---------------------------------------------------------------- evaluación rigurosa (TEA con impuestos) del plan elegido
    ev = []
    for so in sols:
        act = [l for l, v in so["lines"].items() if v["size_scale"]]
        if not act:
            continue
        scale = max(v["size_scale"] for v in so["lines"].values() if v["size_scale"])
        D = pt.design(scale)
        cs = tl.cases_from_design(D)
        keys = [LINES[l][0] for l in act]
        if so["mode"] == "residuos":
            for k in keys:                                   # residuos a costo de recolección
                for r in cs[k]["raw"]:
                    if r.get("main") and "fruta" in r["name"]:
                        r["price"] = tl.M("corona_kg")
        I = tl.integrated_case(cs, keys, name="Plan óptimo: " + so["label"])
        if so["mode"] == "residuos":
            I["equipment"] = [e for e in I["equipment"] if e["name"] not in ("Recepción, lavado y selección", "Peladora-descorazonadora")]
        for bp in I["byproducts"]:
            if bp["name"] == "L1 Vino de piña":
                bp["price"] = so["wine_price"]
        r = tb.evaluate(I)
        mc = tb.monte_carlo(I, [("raw_scale", 0.5, 1.0, 1.8), ("f_prod", 0.8 / 0.9, 1.0, 0.98 / 0.9), ("tasa", 0.06, 0.10, 0.18),
                                ("capex_scale", 0.8, 1.0, 1.5)], None, n=400)
        ev.append(dict(label=so["label"], lines=act, scale=scale, FCI=r["FCI"], NPV=r["NPV"], MIRR=r["MIRR"], payback=r["payback"],
                       revenue=r["revenue"], opex=r["opex"], workers=r["payroll"]["workers"], P_pos=mc["P_pos"], P5=mc["P5"], P95=mc["P95"]))
        print("TEA plan", so["label"], act, f"FCI {r['FCI']/1e6:,.0f} | VPN {r['NPV']/1e6:,.0f} MM | MIRR {r['MIRR']} | P(VPN>0) {mc['P_pos']:.2f}", flush=True)
    json.dump(ev, open(f"{RES}/milp_tea_planes.json", "w"), default=float)
