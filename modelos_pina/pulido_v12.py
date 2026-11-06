"""
Pulido de las soluciones de la versión 12 (dimensionamiento.py); generaliza pulido_v11.py.

v12: la embotelladora entra a los tamaños vecinos; el diseño de la v11 del mismo caso es candidato; E6 se indexa por el precio
de venta al público del vino embotellado y E9 barre la demanda de vino, el PVP y el vino a granel sin impuesto.

v11: el diseño de la v10 para el mismo caso es candidato; la bodega de jugos entra a los tamaños vecinos; los casos que
cambian una opción global (sin azúcar, sin tope de demanda, barridos E7 y E8) se pulen con esa opción puesta (clave _g).

v10: además de caldera, pretratamiento y enzima, cada candidato se evalúa con el tamaño vecino (uno abajo, uno arriba
y «no») de las unidades nuevas: extractora de hojas, bodega de etanol, destilación, digestor, motor a biogás y
productos del hub. Las evaluaciones son MILP pequeños con tamaños fijos.

v9: además del tamaño de la caldera de corona, cada candidato se evalúa con el pretratamiento de la cáscara alternativo
(agua o cal) y con las opciones de separación de enzima más pequeñas (no, precipitación o UF de 0,25 y 0,5 t/h).

Con la caldera de corona, la relajación lineal del MILP se debilita y SCIP termina varias corridas por tiempo con
brechas grandes; en algunas, la solución encontrada es peor que la de un caso más restringido (lo que es imposible en
el óptimo). Para cada caso afectado se evalúan con tamaños fijos (MILP pequeño, exacto) varios diseños candidatos:
el propio con cada tamaño de caldera y los de los casos hermanos. Se conserva el mejor. La cota dual de la corrida
libre sigue siendo válida, de modo que la brecha se recalcula contra ella.
"""
import json, os
import dimensionamiento as dm
import estocastico as es

RES = dm.RES
path = os.environ.get("DIM_OUT", f"{RES}/dimensionamiento.json")
d = json.load(open(path))
BOILERS = ["no", "100 kWt", "200 kWt", "300 kWt"]
D10 = json.load(open(f"{RES}/v11/dimensionamiento.json")) if os.path.exists(f"{RES}/v11/dimensionamiento.json") else {}   # v12: diseños de la v11
NEW10 = ("Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás", "Ácido cítrico", "Xantana")
PRETREAT = ["agua", "cal 0,1 %"]
ENZ = ["no", "Precipitación 0.5 t/h", "Precipitación 1 t/h"]
VARY = ["Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás", "Ácido cítrico", "Xantana", "Secador", "Acetificador",
        "Bodega cáscara", "Embotelladora", "Almacén de mosto", "Bodega"]
_O = dm.options(False)


def neighbors(u, lab):
    labs = [o["lab"] for o in _O[u]]
    if lab not in labs:
        return []
    i = labs.index(lab)
    return sorted({labs[j] for j in (0, i - 1, i + 1) if 0 <= j < len(labs)} - {lab})


def allowed(sz, kw):
    for u, pref in kw.get("allow", {}).items():
        if not any(sz.get(u, "").startswith(p_) for p_ in pref):
            return False
    return True


def bound(r):
    g, o = r.get("gap"), r.get("obj")
    if g is None or o is None or g > 10 or o <= 0:
        return None
    return o * (1 + g)


def fixed(sizes, turno3, **kw):
    kw = dict(kw); g_ = kw.pop("_g", {})
    old = {k: getattr(dm, k) for k in g_}
    for k, v in g_.items():
        setattr(dm, k, v)
    try:
        r = dm.solve(fix=dict(sizes, turno3=turno3), time_limit=90, gap=0.002, **kw)
        return r if r.get("scen") else None
    except Exception as ex:
        print("   inviable:", ex, flush=True)
        return None
    finally:
        for k, v in old.items():
            setattr(dm, k, v)


def polish(key, kw, extra_keys=(), light=()):
    """light: casos cuyo diseño se prueba tal cual, sin tamaños vecinos (v11: escalas vecinas en E2)."""
    r0 = d[key]; b0 = bound(r0)
    # v12: el propio diseño se re-evalúa primero, con la regla de llenado de la bodega (las corridas libres no la tenían)
    cands = [(dict(r0["sizes"]), r0["turno3"])] if r0.get("sizes") else []
    cands += [(dict(d[k2]["sizes"]), d[k2]["turno3"]) for k2 in light if d.get(k2, {}).get("sizes")]
    for k2 in (key,) + tuple(extra_keys):
        r2 = d.get(k2)
        if not r2 or not r2.get("sizes"):
            continue
        base = r2["sizes"]
        for bo in BOILERS:
            cands.append((dict(base, **{"Caldera de corona": bo}), r2["turno3"]))
        for pt_ in PRETREAT:
            cands.append((dict(base, **{"Pretratamiento cáscara": pt_}), r2["turno3"]))
        for ez in ENZ:
            cands.append((dict(base, **{"Enzima cáscara": ez}), r2["turno3"]))
        for u in VARY:
            for lab in neighbors(u, base.get(u, "no")):
                cands.append((dict(base, **{u: lab}), r2["turno3"]))
    if key in D10 and D10[key].get("sizes"):   # v12: el diseño de la v11 para el mismo caso también es candidato
        z = D10[key]
        cands.append((dict(z["sizes"]), z["turno3"]))
        for b in ("500 botellas/h", "1000 botellas/h"):
            cands.append((dict(z["sizes"], **{"Embotelladora": b}), z["turno3"]))
        for lab in neighbors("Acetificador", z["sizes"].get("Acetificador", "no")):
            cands.append((dict(z["sizes"], **{"Acetificador": lab}), z["turno3"]))
    seen, best = set(), None
    for sz, t3 in cands:
        sig = (json.dumps(sz, sort_keys=True), t3)
        if sig in seen:
            continue
        seen.add(sig)
        if (kw.get("allow_shift") is False and t3) or not allowed(sz, kw):
            continue
        r = fixed(sz, t3, **kw)
        if r and (best is None or r["obj"] > best["obj"] + 1e-6):
            best = r
    best = best or r0
    if best is not r0:
        best["status"] = "pulida"
        best["gap"] = (b0 - best["obj"]) / best["obj"] if b0 else None
        best["polished_from"] = r0["obj"]
        d[key] = best
    print(f"{key}: {r0['obj']:,.0f} -> {best['obj']:,.0f} | caldera {best['sizes'].get('Caldera de corona')} | "
          f"cáscara {best['sizes'].get('Pretratamiento cáscara')} | enzima {best['sizes'].get('Enzima cáscara')} | "
          f"brecha {best['gap'] if best['gap'] is None else round(best['gap'] * 100, 2)} %", flush=True)
    json.dump(d, open(path, "w"), default=float)


if __name__ == "__main__":
    sc2 = [dict(sup=2.0, p=1.0)]
    e3 = ("E3|libre (almacén y turno 3 disponibles)", "E3|sin almacén aséptico (≤ 25 m³)", "E3|sin turno 3", "E3|sin almacén ni turno 3")
    import sys
    which = sys.argv[1:] or ["FIJOS", "E1", "E2", "E3", "E6", "E5", "E4", "E7", "E8", "E9"]
    if "E1" in which:
        polish("E1|Óptimo económico", {})
        polish("E1|Óptimo sin SO₂", dict(allow=dm.NO_SO2), ("E1|Óptimo económico",))
        polish("E1|Óptimo sin vinagre", dict(allow=dm.NO_VIN))
        polish("E1|Óptimo sin opciones v10 (sin hojas ni hub)", dict(allow=dm.NO_V10), ("E1|Diseño v11 con parámetros v12",))
        polish("E1|Óptimo sin azúcar añadido", dict(_g=dict(SUGAR=False)), ("E1|Óptimo económico", "E1|Diseño v11 con parámetros v12"))
        polish("E1|Óptimo sin tope de demanda de vinagre", dict(_g=dict(VIN_DEMAND=None)), ("E1|Diseño v11 con parámetros v12", "E1|Óptimo económico"))
        polish("E1|Óptimo sin tope de demanda de vino", dict(_g=dict(WINE_DEMAND_M3=None)), ("E1|Diseño v11 con parámetros v12", "E1|Óptimo económico"))
        polish("E1|Óptimo sin etanol de hojas", dict(allow=dm.NO_ETOH), ("E1|Óptimo económico",))
        polish("E1|Óptimo sin digestor", dict(allow=dm.NO_AD), ("E1|Óptimo económico",))
        polish("E1|Óptimo económico", {}, ("E1|Óptimo sin etanol de hojas", "E1|Óptimo sin digestor", "E1|Óptimo sin opciones v10 (sin hojas ni hub)",
                                          "E1|Óptimo sin azúcar añadido", "E1|Diseño v11 con parámetros v12", "E1|Óptimo sin SO₂",
                                          "E1|Óptimo sin caldera de corona", "E1|Óptimo sin vinagre"), light=("E2|0.750", "E2|0.500"))
        polish("E1|Óptimo sin caldera de corona", dict(allow=dm.NO_BOILER), ("E1|Óptimo económico",))
    if "FIJOS" in which:   # v12: casos de diseño fijo o no pulidos, re-evaluados con la regla de llenado
        for k, kw in (("E1|Referencia TRL-9 (planta_trl9, 6 200 t)", {}), ("E1|Referencia con prensa única de 3 t/h compartida", {}),
                      ("E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)", {}), ("E1|Diseño v11 con parámetros v12", {}),
                      ("E5|B referencia (prensas dedicadas TRL-9)", dict(with_bromelain=True)),
                      ("E5|B óptimo con la topología anterior", dict(with_bromelain=True))):
            if k in d and d[k].get("sizes"):
                r = fixed(d[k]["sizes"], d[k]["turno3"], **kw)
                if r:
                    print(f"{k}: {d[k]['obj']:,.0f} -> {r['obj']:,.0f} (regla de llenado)", flush=True)
                    r["gap"] = d[k].get("gap"); d[k] = r
        json.dump(d, open(path, "w"), default=float)
    if "E2" in which:
        fs = (0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 21856 / dm.SUPPLY)
        for i, f in enumerate(fs):
            k = f"E2|{f:.3f}"
            near = tuple(f"E2|{fs[j]:.3f}" for j in (i - 1, i + 1) if 0 <= j < len(fs)) + ("E1|Óptimo económico",)
            polish(k, dict(scen=[dict(sup=f, p=1.0)]), e3 if abs(f - 2.0) < 1e-9 else (), light=near)
    if "E3" in which:
        polish(e3[0], dict(scen=sc2), e3[1:] + ("E2|2.000",))
        polish(e3[1], dict(scen=sc2, store_max=25), e3[2:])
        polish(e3[2], dict(scen=sc2, allow_shift=False), (e3[1], e3[3]))
    if "E6" in which:
        for pvp in (10000.0, 16000.0, 25000.0):
            wp = dm.wine_bottle(pvp=pvp)["neto_L"]
            for vp in (1500.0, 2200.0):
                if f"E6|{wp:.0f}|{vp:.0f}" not in d:
                    continue
                polish(f"E6|{wp:.0f}|{vp:.0f}", dict(mg=dm.margins(wine_price=wp, vinegar_price=vp)),
                       light=tuple(k_ for k_ in d if k_.startswith("E6|")) + ("E1|Óptimo económico", "E1|Óptimo sin vinagre"))
        dm.margins()
    if "E5" in which:
        polish("E5|B óptimo económico", dict(with_bromelain=True), ("E1|Óptimo económico",))
    if "E4" in which:
        # E4: el RP no puede ser peor que el diseño de valor medio evaluado en los escenarios (EEV)
        sc = [dict(sup=a, p=pa) for a, pa in es.SUP_F]
        polish("E4|EV", dict(scen=[dict(sup=sum(a * pa for a, pa in es.SUP_F), p=1.0)]), ("E1|Óptimo económico",))
        polish("E4|RP", dict(scen=sc), ("E4|EV",))
        ev = d["E4|EV"]
        eev = fixed(ev["sizes"], ev["turno3"], scen=sc)
        if eev:
            d["E4|EEV"] = eev
        ws_each = []
        for i, (a, pa) in enumerate(es.SUP_F):
            k = f"E2|{a:.3f}" if f"E2|{a:.3f}" in d else None
            w = d["E4|WS"]["each"][i]
            best = None
            # v11: el WS de cada escenario también se evalúa con los diseños del RP, del EV y del óptimo (WS ≥ RP por construcción)
            extra = [(d[k2]["sizes"], d[k2]["turno3"]) for k2 in ("E4|RP", "E4|EV", "E1|Óptimo económico") if d.get(k2, {}).get("sizes")]
            for sz, t3 in [(w["sizes"], w["turno3"])] + ([(d[k]["sizes"], d[k]["turno3"])] if k else []) + extra:
                for bo in BOILERS:
                    r = fixed(dict(sz, **{"Caldera de corona": bo}), t3, scen=[dict(sup=a, p=1.0)]) if sz else None
                    if r and (best is None or r["obj"] > best["obj"]):
                        best = r
            w0 = w["obj"]
            if best and best["obj"] > w0:
                ws_each.append(dict(sup=a, obj=best["obj"], sizes=best["sizes"], turno3=best["turno3"]))
            else:
                ws_each.append(w)
            print("WS", a, round(w0), "->", round(ws_each[-1]["obj"]), flush=True)
        d["E4|WS"] = dict(obj=sum(w["obj"] * pa for w, (a, pa) in zip(ws_each, es.SUP_F)), each=ws_each)
        print("E4: RP", round(d["E4|RP"]["obj"]), "EV", round(d["E4|EV"]["obj"]), "EEV", round(d["E4|EEV"]["obj"]),
              "WS", round(d["E4|WS"]["obj"]), "VSS", round(d["E4|RP"]["obj"] - d["E4|EEV"]["obj"]),
              "EVPI", round(d["E4|WS"]["obj"] - d["E4|RP"]["obj"]), flush=True)
    json.dump(d, open(path, "w"), default=float)
    if "E7" in which:   # v11: sensibilidad de las hojas, con la opción global de cada caso
        base = dm.HOJAS_SUPPLY
        for lab, g_ in (("fracción de acopio 0,10", dict(HOJAS_SUPPLY=base * 0.10 / dm.DT.val("frac_acopio_hojas"))),
                        ("fracción de acopio 0,50", dict(HOJAS_SUPPLY=base * 0.50 / dm.DT.val("frac_acopio_hojas"))),
                        ("costo de acopio 80 000 COP/t", dict(ACOPIO_VC=80_000.0)), ("etanol a 3 000 COP/L", dict(ETOH_PRICE=3_000.0))):
            if f"E7|{lab}" in d:
                polish(f"E7|{lab}", dict(_g=g_), ("E1|Óptimo económico",))
    if "E8" in which:   # v11: demanda de vinagre y precio de la panela
        for lab, g_ in (("demanda 1 500 m³/año", dict(VIN_DEMAND=1500.0)), ("demanda 6 000 m³/año", dict(VIN_DEMAND=6000.0)),
                        ("demanda 12 000 m³/año", dict(VIN_DEMAND=12000.0)), ("panela a 5 000 COP/kg", dict(AZ_PRICE=5000.0)),
                        ("demanda 6 000 m³/año sin azúcar", dict(VIN_DEMAND=6000.0, SUGAR=False))):
            if f"E8|{lab}" in d:
                polish(f"E8|{lab}", dict(_g=g_), ("E1|Óptimo económico", "E1|Óptimo sin tope de demanda de vinagre", "E1|Diseño v11 con parámetros v12"))
    if "E9" in which:   # v12: demanda de vino, PVP y vino a granel sin impuesto
        W = lambda n: n * dm.BOTTLE_L / 1000
        for lab, kw in (("demanda 250 000 botellas/año", dict(_g=dict(WINE_DEMAND_M3=W(250000)))),
                        ("demanda 1 000 000 botellas/año", dict(_g=dict(WINE_DEMAND_M3=W(1e6)))),
                        ("demanda 2 000 000 botellas/año", dict(_g=dict(WINE_DEMAND_M3=W(2e6)))),
                        ("PVP 10 000 COP/botella", dict(mg=dm.margins(wine_price=dm.wine_bottle(pvp=10000.0)["neto_L"]))),
                        ("PVP 25 000 COP/botella", dict(mg=dm.margins(wine_price=dm.wine_bottle(pvp=25000.0)["neto_L"]))),
                        ("vino a granel sin impuesto (v11)", dict(_g=dict(BOTTLED=False, WINE_DEMAND_M3=None)))):
            if f"E9|{lab}" in d:
                polish(f"E9|{lab}", kw, ("E1|Óptimo económico", "E1|Óptimo sin tope de demanda de vino", "E1|Diseño v11 con parámetros v12"))
        dm.margins()
    json.dump(d, open(path, "w"), default=float)
