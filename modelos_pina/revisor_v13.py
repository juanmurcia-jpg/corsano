"""
v13: análisis pedidos por la revisión (revisor 2) con ideas de OUTDOOR (Kenkel et al., 2022).

  H1  línea base: el mismo modelo y la misma superestructura resueltos (a) con flujos promedio (diseño en estado
      estacionario, como OUTDOOR) y (b) por fracciones en secuencia (pulpa → cáscara → hojas), y (c) ambas cosas.
      Cada diseño se evalúa después con la operación estacional del año. La diferencia con el óptimo mide el valor
      de decidir síntesis, tamaños y operación a la vez, con la superestructura fija.
  H4  mapa de demanda: margen óptimo en una malla de botellas × m³ de vinagre (barrido cruzado de OUTDOOR); el VPN de
      cada diseño se calcula después con tea_dimensionado (frontera de demanda mínima viable).
  H2  bomba de calor (calor del acetificador al secador) como opción nueva y barrido de autonomía: tope de energía
      fósil primaria (diésel + GLP) del 100 % al 0 % del óptimo.
  H3  frente margen–huella neta (contra la línea base sin planta) por ε-restricción y diseños de compromiso con pesos
      (distancia L1 ponderada al punto ideal, Kenkel et al. 2022).

Uso: python revisor_v13.py H1 | H4a | H4b | H2 | H3      (cada grupo escribe results/v13/<grupo>.json)
"""
import json, os, sys, time
import numpy as np
import dimensionamiento as dm

OUT = os.path.join(dm.RES, "v13")
os.makedirs(OUT, exist_ok=True)
D12 = json.load(open(os.path.join(dm.RES, "dimensionamiento.json")))
OPT12 = D12["E1|Óptimo económico"]
PULP = ["Frente", "Prensa", "Decantadora", "Clarificación", "MF lías", "Estabilización", "Bodega", "Almacén de mosto", "Embotelladora"]
PEEL = ["Prensa cáscara", "Pretratamiento cáscara", "Enzima cáscara", "Secador", "Bodega cáscara", "Acetificador", "Caldera de corona",
        "Ácido cítrico", "Xantana"]
LEAF = ["Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás"]
MINIMAL = {"Secador": ["50 kg"], "Pretratamiento cáscara": ["agua"]}       # unidades sin opción «no»: el tamaño mínimo


def design(r):
    return dict(r["sizes"], turno3=r["turno3"])


def short(r):
    if not r.get("scen"):
        return dict(status=r.get("status"))
    s = r["scen"][0]; p = s["products"]
    keep = ("fruta_t", "hojas_t", "vino_m3", "botellas", "vinagre_m3", "harina_t", "azucar_kg", "calor_glp_MJ", "calor_bomba_MJ",
            "elec_demanda_kWh", "fosil_MJ", "gwp_kg", "gwp_neto_kg", "jugo_hojas_vinagre_t", "jugo_cascara_vinagre_t", "vino_a_vinagre_m3")
    return dict(status=r["status"], gap=r["gap"], obj=r["obj"], margin=s["margin"], FCI=r["FCI"], sizes=r["sizes"], turno3=r["turno3"],
                products={k: p.get(k, 0.0) for k in keep}, loss=s["loss"], t=r.get("t"), full=r)


def stage_allow(free, extra_fixed):
    """allow: las unidades que no están en 'free' ni fijas quedan en «no» (o en su tamaño mínimo)."""
    allow = {}
    for u in PULP + PEEL + LEAF + (["Bomba de calor"] if dm.HP_ON else []):
        if u in free or u in extra_fixed:
            continue
        allow[u] = MINIMAL.get(u, ["no"])
    return allow


def sequential(flat):
    """Diseño secuencial por fracciones: pulpa y vino, luego cáscara, luego hojas; cada etapa fija lo anterior."""
    fixed, log = {}, []
    for name, free in (("pulpa", PULP), ("cáscara", PEEL), ("hojas", LEAF)):
        kw = dict(allow=stage_allow(free, fixed), flat=flat, time_limit=240)
        if fixed:
            kw["fix"] = dict(fixed)
        r = dm.solve(**kw)
        if not r.get("scen"):
            log.append(dict(stage=name, status=r.get("status"))); break
        for u in free:
            fixed[u] = r["sizes"][u]
        fixed["turno3"] = r["turno3"]
        log.append(dict(stage=name, obj=r["obj"], sizes={u: r["sizes"][u] for u in free}))
        print("  etapa", name, round(r["obj"]), {u: r["sizes"][u] for u in free if r["sizes"][u] not in ("no",)}, flush=True)
    for u in PULP + PEEL + LEAF:
        fixed.setdefault(u, MINIMAL.get(u, ["no"])[0] if u not in MINIMAL else r["sizes"][u])
    return fixed, log


def evaluate(fx):
    """Operación estacional del año con el diseño fijo."""
    return dm.solve(fix=fx, time_limit=180, gap=0.002)


def run_H1(res):
    dm.HP_ON = False                                    # mismas opciones que el óptimo v12
    res["optimo_v12"] = dict(obj=OPT12["obj"], margin=OPT12["scen"][0]["margin"], sizes=OPT12["sizes"], turno3=OPT12["turno3"])
    # (a) flujos promedio, simultáneo
    ra = dm.solve(flat=True, time_limit=300, hint=design(OPT12))
    ea = evaluate(design(ra))
    res["promedio"] = dict(diseno=short(ra), evaluado=short(ea)); save(res)
    print("H1 promedio: diseño", round(ra["obj"]), "evaluado", round(ea.get("obj", float("nan"))), flush=True)
    # (b) secuencial por fracciones, estacional
    fb, lb = sequential(flat=False)
    eb = evaluate(fb)
    res["secuencial"] = dict(etapas=lb, evaluado=short(eb)); save(res)
    print("H1 secuencial:", round(eb.get("obj", float("nan"))), flush=True)
    # (c) secuencial por fracciones con flujos promedio (diseño clásico)
    fc, lc = sequential(flat=True)
    ec = evaluate(fc)
    res["secuencial_promedio"] = dict(etapas=lc, evaluado=short(ec)); save(res)
    print("H1 secuencial con flujos promedio:", round(ec.get("obj", float("nan"))), flush=True)


def run_H1b(res):
    """Flujos promedio frente a estacionalidad cuando la capacidad aprieta: 2× la oferta y la base de diseño (3,56×), sin topes de mercado."""
    dm.HP_ON = False
    base_w, base_v = dm.WINE_DEMAND_M3, dm.VIN_DEMAND
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = None, None
    for f in (2.0, 21856 / dm.SUPPLY):
        sc = [dict(sup=f, p=1.0)]
        rs = dm.solve(scen=sc, time_limit=300, hint=design(OPT12))
        rf = dm.solve(scen=sc, flat=True, time_limit=300, hint=design(OPT12))
        ef = dm.solve(scen=sc, fix=design(rf), time_limit=180, gap=0.002)
        res[f"{f:.3f}"] = dict(estacional=short(rs), promedio_diseno=short(rf), promedio_evaluado=short(ef))
        save(res)
        print("H1b", round(f, 2), "estacional", round(rs.get("obj", float("nan"))), "promedio: diseño", round(rf.get("obj", float("nan"))),
              "evaluado", round(ef.get("obj", float("nan"))), flush=True)
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = base_w, base_v


def run_H1c(res):
    """Repite el óptimo estacional de H1b con arranque desde el diseño de flujos promedio y más tiempo (el de 300 s no convergió a 3,56×)."""
    dm.HP_ON = False
    base_w, base_v = dm.WINE_DEMAND_M3, dm.VIN_DEMAND
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = None, None
    h1b = L_("H1b")
    for k, v in h1b.items():
        if k.startswith("_"):
            continue
        f = float(k); sc = [dict(sup=f, p=1.0)]
        best = v["estacional"]
        for hint in (dict(v["promedio_diseno"]["sizes"], turno3=v["promedio_diseno"]["turno3"]),
                     dict(v["estacional"]["sizes"], turno3=v["estacional"]["turno3"]) if v["estacional"].get("sizes") else None):
            if hint is None:
                continue
            r = dm.solve(scen=sc, time_limit=900, hint=hint)
            if r.get("scen") and r["obj"] > (best.get("obj") or -1e18) + 1:
                best = short(r)
        res[k] = dict(estacional=best, promedio_diseno=v["promedio_diseno"], promedio_evaluado=v["promedio_evaluado"]); save(res)
        print("H1c", k, "estacional", round(best["obj"]), "promedio evaluado", round(v["promedio_evaluado"]["obj"]), flush=True)
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = base_w, base_v


BOTTLES = (100_000, 250_000, 500_000, 1_000_000, 2_000_000)
VINEGAR = (0.0, 750.0, 1500.0, 3000.0, 6000.0, 12000.0)


def run_H4(res, bottles):
    dm.HP_ON = False
    base_w, base_v = dm.WINE_DEMAND_M3, dm.VIN_DEMAND
    for b in bottles:
        for v in VINEGAR:
            dm.WINE_DEMAND_M3, dm.VIN_DEMAND = b * dm.BOTTLE_L / 1000, v
            r = dm.solve(time_limit=150, hint=design(OPT12))
            res[f"{b}|{v:.0f}"] = short(r); save(res)
            print("H4", b, v, round(r.get("obj", float("nan"))), flush=True)
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = base_w, base_v


def run_H2(res):
    dm.HP_ON = True
    h = dict(design(OPT12), **{"Bomba de calor": "25 kWt"})
    r0 = dm.solve(time_limit=360, hint=h)
    res["optimo_v13"] = short(r0); save(res)
    F0 = r0["scen"][0]["products"]["fosil_MJ"]
    print("H2 óptimo v13", round(r0["obj"]), r0["sizes"].get("Bomba de calor"), "fósil GJ", round(F0 / 1000), flush=True)
    prev = design(r0)
    res["sweep"] = []
    for f in (0.8, 0.6, 0.4, 0.2, 0.0):
        r = dm.solve(fossil_max=f * F0, time_limit=240, hint=prev)
        if not r.get("scen"):   # el arranque puede no cumplir el tope: se intenta sin pista
            r = dm.solve(fossil_max=f * F0, time_limit=240)
        res["sweep"].append(dict(frac=f, fossil_max=f * F0, **short(r))); save(res)
        print("H2 fósil ≤", f, round(r.get("obj", float("nan"))), r.get("sizes", {}).get("Bomba de calor"), flush=True)
        if r.get("scen"):
            prev = design(r)


def run_H3(res):
    dm.HP_ON = True
    r2 = json.load(open(os.path.join(OUT, "H2.json"))) if os.path.exists(os.path.join(OUT, "H2.json")) else {}
    eco = r2.get("optimo_v13", {}).get("full") or dm.solve(time_limit=360, hint=dict(design(OPT12), **{"Bomba de calor": "no"}))
    g_eco = eco["scen"][0]["products"]["gwp_neto_kg"]; m_eco = eco["scen"][0]["margin"]
    low = dm.solve(objective="gwp", gwp_net=True, time_limit=360, hint=design(eco))
    g_min = low["scen"][0]["products"]["gwp_neto_kg"]; m_low = low["scen"][0]["margin"]
    res["extremos"] = dict(economico=short(eco), ambiental=short(low)); save(res)
    print("H3 extremos: económico", round(m_eco), round(g_eco / 1000), "| ambiental", round(m_low), round(g_min / 1000), flush=True)
    pts, prev = [], design(eco)
    for eps in np.linspace(g_eco, g_min, 6)[1:-1]:
        r = dm.solve(gwp_max=float(eps), gwp_net=True, time_limit=240, hint=prev)
        if r.get("scen"):
            pts.append(dict(eps=float(eps), **short(r))); prev = design(r)
            print("H3 ε", round(eps / 1000), round(r["scen"][0]["margin"]), round(r["scen"][0]["products"]["gwp_neto_kg"] / 1000), flush=True)
    res["frente"] = pts; save(res)
    res["mcda"] = []
    for w in (0.25, 0.5, 0.75):
        r = dm.solve(mcda=dict(w=w, m=(m_eco, m_low), g=(g_min, g_eco)), gwp_net=True, time_limit=240, hint=design(eco))
        res["mcda"].append(dict(w=w, **short(r))); save(res)
        print("H3 MCDA w", w, round(r["scen"][0]["margin"]), round(r["scen"][0]["products"]["gwp_neto_kg"] / 1000), flush=True)


def polish_H4(res):
    """Pulido monótono de la malla: con topes de mercado más holgados el óptimo no puede empeorar, así que cada punto se
    evalúa también con los diseños de sus vecinos de menor demanda (botellas y vinagre) y se queda con el mejor."""
    dm.HP_ON = False
    g = dict(L_("H4a"), **L_("H4b"))
    base_w, base_v = dm.WINE_DEMAND_M3, dm.VIN_DEMAND
    for b in BOTTLES:
        for v in VINEGAR:
            key = f"{b}|{v:.0f}"
            cur = g.get(key, {})
            cands = []
            for nb in ((BOTTLES[BOTTLES.index(b) - 1], v) if BOTTLES.index(b) > 0 else None,
                       (b, VINEGAR[VINEGAR.index(v) - 1]) if VINEGAR.index(v) > 0 else None):
                if nb and f"{nb[0]}|{nb[1]:.0f}" in g and g[f"{nb[0]}|{nb[1]:.0f}"].get("sizes"):
                    nr = g[f"{nb[0]}|{nb[1]:.0f}"]
                    if not cur.get("obj") or nr["obj"] > cur["obj"] + 1:
                        cands.append(dict(nr["sizes"], turno3=nr["turno3"]))
            dm.WINE_DEMAND_M3, dm.VIN_DEMAND = b * dm.BOTTLE_L / 1000, v
            for fx in cands:
                r = dm.solve(fix=fx, time_limit=120, gap=0.002)
                if r.get("scen") and r["obj"] > (cur.get("obj") or -1e18) + 1:
                    print("H4 pulido", key, round(cur.get("obj") or float("nan")), "->", round(r["obj"]), flush=True)
                    cur = short(r); cur["pulido"] = True
            g[key] = cur
            res[key] = cur; save(res)
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = base_w, base_v


def polish_H2(res):
    """Pulido del barrido de autonomía: cada tope se evalúa con los diseños de los demás topes, con bomba de 0 a 100 kWt."""
    dm.HP_ON = True
    h2 = L_("H2")
    designs = [dict(h2["optimo_v13"]["sizes"], turno3=h2["optimo_v13"]["turno3"])] + \
              [dict(s["sizes"], turno3=s["turno3"]) for s in h2.get("sweep", []) if s.get("sizes")]
    sw = h2.get("sweep", [])
    for i, s in enumerate(sw):
        best = s
        near = [designs[0]] + [dict(x["sizes"], turno3=x["turno3"]) for x in sw[max(0, i - 1):i + 2] if x.get("sizes")]
        for d0 in near:
            for hp in ("no", "25 kWt", "50 kWt", "100 kWt"):
                fx = dict(d0, **{"Bomba de calor": hp})
                r = dm.solve(fix=fx, fossil_max=s["fossil_max"], time_limit=90, gap=0.002)
                if r.get("scen") and r["obj"] > (best.get("obj") if best.get("obj") is not None else -1e18) + 1:
                    print("H2 pulido", s["frac"], round(best.get("obj") or float("nan")), "->", round(r["obj"]), hp, flush=True)
                    best = dict(frac=s["frac"], fossil_max=s["fossil_max"], pulido=True, **short(r))
        res.setdefault("sweep", []).append(best); save(res)


def L_(g):
    p_ = os.path.join(OUT, f"{g}.json")
    return json.load(open(p_)) if os.path.exists(p_) else {}


def pool_designs():
    """Todos los diseños distintos hallados (malla, barridos, v12): cualquiera es factible en cualquier punto, porque los topes de
    mercado y de energía solo limitan la operación."""
    pool = {}
    def add(sz, t3):
        if sz:
            d_ = dict(sz, turno3=t3); pool[json.dumps(d_, sort_keys=True)] = d_
    for g_ in ("H4a", "H4b", "H4p", "H2", "H2p", "H3"):
        for k, v in L_(g_).items():
            for it in (v if isinstance(v, list) else [v]):
                if isinstance(it, dict) and it.get("sizes"):
                    add(it["sizes"], it["turno3"])
                if isinstance(it, dict):
                    for vv in it.values():
                        if isinstance(vv, dict) and vv.get("sizes"):
                            add(vv["sizes"], vv["turno3"])
    for k, v in D12.items():
        if k.split("|")[0] in ("E1", "E6", "E7", "E8", "E9") and isinstance(v, dict) and v.get("sizes"):
            add(v["sizes"], v["turno3"])
    return list(pool.values())


def polish_H4_pool(res, part):
    dm.HP_ON = False
    g = dict(L_("H4a"), **L_("H4b")); g.update({k: v for k, v in L_("H4p").items() if not k.startswith("_")})
    pool = [{k: v for k, v in d_.items() if k != "Bomba de calor"} for d_ in pool_designs()]
    pool = list({json.dumps(d_, sort_keys=True): d_ for d_ in pool}.values())
    base_w, base_v = dm.WINE_DEMAND_M3, dm.VIN_DEMAND
    bot = BOTTLES[int(part)::3]
    print("H4 pool", len(pool), "diseños; botellas", bot, flush=True)
    for b in bot:
        for v in VINEGAR:
            key = f"{b}|{v:.0f}"; cur = g.get(key, {})
            dm.WINE_DEMAND_M3, dm.VIN_DEMAND = b * dm.BOTTLE_L / 1000, v
            for fx in pool:
                r = dm.solve(fix=fx, time_limit=60, gap=0.002)
                if r.get("scen") and r["obj"] > (cur.get("obj") if cur.get("obj") is not None else -1e18) + 1:
                    cur = short(r); cur["pulido"] = "pool"
            res[key] = cur; save(res)
            print("H4 pool", key, round(cur.get("obj") or float("nan")), flush=True)
    dm.WINE_DEMAND_M3, dm.VIN_DEMAND = base_w, base_v


def run_H3b(res):
    """Frente margen–huella neta con la contabilidad corregida de la v13 (pulpa y jugo de hojas devueltos al campo) y pulido cruzado."""
    dm.HP_ON = True
    pool = pool_designs()
    eco_d = dict(design(OPT12), **{"Bomba de calor": "no"})
    variants = []
    for d_ in [eco_d] + [p_ for p_ in pool if p_.get("Extractora hojas", "no") != "no"][:12]:
        for cb in ("100 kWt", "200 kWt", "300 kWt", "500 kWt"):
            for hp in ("no", "25 kWt", "50 kWt"):
                variants.append(dict(d_, **{"Caldera de corona": cb, "Bomba de calor": hp}))
    pool = pool + variants
    print("H3b pool", len(pool), flush=True)
    eco = dm.solve(time_limit=240, hint=eco_d)
    m_eco, g_eco = eco["scen"][0]["margin"], eco["scen"][0]["products"]["gwp_neto_kg"]
    low = dm.solve(objective="gwp", gwp_net=True, time_limit=360, hint=eco_d)
    # el mínimo puede mejorarse con el pool (mínima huella; margen como desempate)
    best_low = low
    for fx in pool:
        r = dm.solve(fix=fx, objective="gwp", gwp_net=True, time_limit=40, gap=0.01)
        if r.get("scen"):
            gl = r["scen"][0]["products"]["gwp_neto_kg"]
            if gl < best_low["scen"][0]["products"]["gwp_neto_kg"] - 1:
                best_low = r
    low = best_low
    g_min, m_low = low["scen"][0]["products"]["gwp_neto_kg"], low["scen"][0]["margin"]
    res["extremos"] = dict(economico=short(eco), ambiental=short(low)); save(res)
    print("H3b extremos: económico", round(m_eco), round(g_eco / 1000), "| ambiental", round(m_low), round(g_min / 1000), flush=True)
    pts = []
    for eps in np.linspace(g_eco, g_min, 7)[1:-1]:
        r = dm.solve(gwp_max=float(eps), gwp_net=True, time_limit=240, hint=design(eco))
        best = r if r.get("scen") else None
        for fx in pool + [design(p_["full"]) for p_ in pts if p_.get("full")]:
            r2 = dm.solve(fix=fx, gwp_max=float(eps), gwp_net=True, time_limit=40, gap=0.005)
            if r2.get("scen") and (best is None or r2["obj"] > best["obj"] + 1):
                best = r2
        if best:
            pts.append(dict(eps=float(eps), **short(best))); res["frente"] = pts; save(res)
            print("H3b ε", round(eps / 1000), round(best["scen"][0]["margin"]), round(best["scen"][0]["products"]["gwp_neto_kg"] / 1000),
                  best["sizes"].get("Caldera de corona"), best["sizes"].get("Bomba de calor"), flush=True)
    res["mcda"] = []
    cand = pool + [design(p_["full"]) for p_ in pts] + [design(eco), design(low)]
    for w in (0.25, 0.5, 0.75):
        md = dict(w=w, m=(m_eco, m_low), g=(g_min, g_eco))
        best = dm.solve(mcda=md, gwp_net=True, time_limit=240, hint=design(eco))
        for fx in cand:
            r2 = dm.solve(fix=fx, mcda=md, gwp_net=True, time_limit=40, gap=0.005)
            if r2.get("scen") and (not best.get("scen") or r2["obj"] > best["obj"] + 1e-6):
                best = r2
        res["mcda"].append(dict(w=w, **short(best))); save(res)
        print("H3b MCDA w", w, round(best["scen"][0]["margin"]), round(best["scen"][0]["products"]["gwp_neto_kg"] / 1000), flush=True)


def save(res):
    json.dump(res, open(PATH, "w"), default=float, indent=0)


if __name__ == "__main__":
    grp = sys.argv[1]
    PATH = os.path.join(OUT, f"{grp}.json")
    res = {}
    t0 = time.time()
    if grp == "H1":
        run_H1(res)
    elif grp == "H1b":
        run_H1b(res)
    elif grp == "H1c":
        run_H1c(res)
    elif grp == "H4q":
        PATH = os.path.join(OUT, f"H4q{sys.argv[2]}.json")
        polish_H4_pool(res, sys.argv[2])
    elif grp == "H3b":
        run_H3b(res)
    elif grp == "H4p":
        polish_H4(res)
    elif grp == "H2p":
        polish_H2(res)
    elif grp == "H4a":
        run_H4(res, BOTTLES[:3])
    elif grp == "H4b":
        run_H4(res, BOTTLES[3:])
    elif grp == "H2":
        run_H2(res)
    elif grp == "H3":
        run_H3(res)
    res["_t"] = time.time() - t0
    save(res)
