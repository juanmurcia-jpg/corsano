"""
Pulido de las soluciones de la versión 8 (dimensionamiento.py).

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
path = f"{RES}/dimensionamiento.json"
d = json.load(open(path))
BOILERS = ["no", "100 kWt", "200 kWt", "300 kWt"]


def bound(r):
    g, o = r.get("gap"), r.get("obj")
    if g is None or o is None or g > 10 or o <= 0:
        return None
    return o * (1 + g)


def fixed(sizes, turno3, **kw):
    try:
        r = dm.solve(fix=dict(sizes, turno3=turno3), time_limit=90, gap=0.002, **kw)
        return r if r.get("scen") else None
    except Exception as ex:
        print("   inviable:", ex, flush=True)
        return None


def polish(key, kw, extra_keys=()):
    r0 = d[key]; b0 = bound(r0)
    cands = []
    for k2 in (key,) + tuple(extra_keys):
        r2 = d.get(k2)
        if not r2 or not r2.get("sizes"):
            continue
        for bo in BOILERS:
            if "allow" in kw and "Caldera de corona" in kw["allow"] and bo not in kw["allow"]["Caldera de corona"]:
                continue
            cands.append((dict(r2["sizes"], **{"Caldera de corona": bo}), r2["turno3"]))
    seen, best = set(), r0
    for sz, t3 in cands:
        sig = (json.dumps(sz, sort_keys=True), t3)
        if sig in seen:
            continue
        seen.add(sig)
        if kw.get("allow_shift") is False and t3:
            continue
        r = fixed(sz, t3, **kw)
        if r and r["obj"] > best["obj"] + 1e-6:
            best = r
    if best is not r0:
        best["status"] = "pulida"
        best["gap"] = (b0 - best["obj"]) / best["obj"] if b0 else None
        best["polished_from"] = r0["obj"]
        d[key] = best
    print(f"{key}: {r0['obj']:,.0f} -> {best['obj']:,.0f} | caldera {best['sizes'].get('Caldera de corona')} | "
          f"brecha {best['gap'] if best['gap'] is None else round(best['gap'] * 100, 2)} %", flush=True)
    json.dump(d, open(path, "w"), default=float)


if __name__ == "__main__":
    sc2 = [dict(sup=2.0, p=1.0)]
    e3 = ("E3|libre (almacén y turno 3 disponibles)", "E3|sin almacén aséptico (≤ 25 m³)", "E3|sin turno 3", "E3|sin almacén ni turno 3")
    polish("E1|Óptimo económico", {})
    polish("E1|Óptimo sin SO₂", dict(allow=dm.NO_SO2), ("E1|Óptimo económico",))
    polish("E1|Óptimo sin vinagre", dict(allow=dm.NO_VIN))
    for f in (0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 21856 / dm.SUPPLY):
        k = f"E2|{f:.3f}"
        polish(k, dict(scen=[dict(sup=f, p=1.0)]), e3 if abs(f - 2.0) < 1e-9 else ())
    polish(e3[0], dict(scen=sc2), e3[1:] + ("E2|2.000",))
    polish(e3[1], dict(scen=sc2, store_max=25), e3[2:])
    polish(e3[2], dict(scen=sc2, allow_shift=False), (e3[1], e3[3]))
    for wp in (1600.0, 2200.0, 3000.0, 4000.0):
        for vp in (1500.0, 2200.0):
            polish(f"E6|{wp:.0f}|{vp:.0f}", dict(mg=dm.margins(wine_price=wp, vinegar_price=vp)))
    dm.margins()
    polish("E5|B óptimo económico", dict(with_bromelain=True))
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
        for sz, t3 in [(w["sizes"], w["turno3"])] + ([(d[k]["sizes"], d[k]["turno3"])] if k else []):
            for bo in BOILERS:
                r = fixed(dict(sz, **{"Caldera de corona": bo}), t3, scen=[dict(sup=a, p=1.0)])
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
