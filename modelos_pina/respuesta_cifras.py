"""Cifras canónicas de la respuesta al comité (base: etanol del jugo de hoja = 20,7 kg/t salvo donde se indica). Salida: results/respuesta/cifras.json"""
import json, os
import dimensionamiento as dm
R = lambda f: json.load(open(os.path.join(dm.RES, "respuesta", f)))
T, H = R("tablas.json"), R("hoja.json")
C = {}
# ---- secante del informe
a, b = (184.0, -5409.0), (3196.0, 5397.0); s = (b[1] - a[1]) / (b[0] - a[0]); m0 = a[0] - a[1] / s
sec = lambda m: a[1] + s * (m - a[0])
C["secant"] = dict(slope=s, m0=m0)
# error de la secante sobre los diseños con TEA (mapa a 20,7)
v13 = json.load(open(os.path.join(dm.RES, "v13", "resumen.json")))["H4"]
rows21 = {(r["bottles"], r["vinegar"]): r for r in T["H4"]["rows"]}
c207 = {}
for p in range(5):
    for k, v in R(f"c207_{p}.json").items():
        c207[tuple(int(x) for x in k.split("|"))] = v
grid = {}
for (bt, vin), r in rows21.items():
    if vin >= 1500:
        v = c207[(bt, vin)]
        m = v["best"]["margin"]; npv = v["tea"]["NPV"] if v.get("tea") else None
        bound = v["free"].get("bound"); fruit = v["best"]["products"]["fruta_t"]
    else:
        m, npv, bound, fruit = r["margin"], r["NPV"], r["bound"], r["fruit_t"]
    grid[f"{bt}|{vin}"] = dict(bottles=bt, vinegar=vin, margin=m, NPV=npv, NPV_secant=sec(m), bound=bound, fruit=fruit)
NV = R("novino.json")
for v in (1500, 3000, 6000, 12000):                      # TEA de las plantas sin fruta (tea_any)
    grid[f"100000|{v}"]["NPV"] = NV[f"100000|{v}|90 % of theoretical on carbohydrate"]["tea"]["NPV"]; grid[f"100000|{v}"]["tea_nofruit"] = True
dev = [abs(g["NPV"] - g["NPV_secant"]) for g in grid.values() if g["NPV"] is not None and abs(g["margin"] - 184) > 1 and abs(g["margin"] - 3196) > 1]
C["secant"].update(n_tea=sum(1 for g in grid.values() if g["NPV"] is not None), n_dev=len(dev), dev_mean=sum(dev) / len(dev), dev_max=max(dev))
C["secant"]["band_margin"] = C["secant"]["dev_max"] / s
C["H4"] = grid
def interp(x0, y0, x1, y1):
    return x0 + (x1 - x0) * (-y0) / (y1 - y0)
g = lambda bt, vin: grid[f"{bt}|{vin}"]
C["frontier"] = dict(
    wine_only=interp(500000, g(500000, 0)["NPV"], 1000000, g(1000000, 0)["NPV"]),
    at500k=interp(1500, g(500000, 1500)["NPV"], 3000, g(500000, 3000)["NPV"]),
    at250k=interp(1500, g(250000, 1500)["NPV"], 3000, g(250000, 3000)["NPV"]),
    vin_only=interp(1500, g(100000, 1500)["NPV"], 3000, g(100000, 3000)["NPV"]))
C["flip"] = {k: dict(bound=grid[k]["bound"], npv_sec_at_bound=sec(grid[k]["bound"]), deviation_to_flip=-sec(grid[k]["bound"]))
             for k in ("250000|0", "500000|0", "250000|1500", "500000|1500") if grid[k]["bound"] is not None}
h3p = R("h3full_1.json"); C["secant"]["h3_dev"] = abs(h3p["new_tea"]["NPV"] - sec(h3p["new"]["margin"]))
# ---- central y jugo de hoja
c = c207[(500000, 3000)]
tea207 = R("tea207.json"); C["central"] = dict(margin=c["best"]["margin"], free_bound=c["free"]["bound"], nest=R("nest207.json"),
                                              tea=tea207["eval"], mc=tea207["mc"], panela_t=c["best"]["products"]["azucar_kg"] / 1000)
tor = tea207["tornado"][0]
C["central"]["breakeven_vinegar"] = tor["worst"] + (tor["base"] - tor["worst"]) * (-tor["NPV_worst"]) / (tea207["eval"]["NPV"] * 1e6 - tor["NPV_worst"])
C["leaf"] = {k: dict(E=v["E_LJ"], A=v["A_LJ"], margin=v["reopt"]["margin"], bound=v["reopt"]["bound"], panela=v["reopt"]["products"]["azucar_kg"] / 1000,
                     NPV=v["reopt_tea"]["NPV"], vinegar=v["reopt"]["products"]["vinagre_m3"]) for k, v in H.items()}
C["vin_only_tea"] = {"20.7": NV["100000|3000|90 % of theoretical on carbohydrate"]["tea"], "13.5": NV["100000|3000|theoretical on free sugars"]["tea"],
                     "11.1": NV["100000|3000|0.42 g/g on free sugars"]["tea"], "6.5": NV["100000|3000|closure"]["tea"]}
C["closure"] = dict(E=NV["500000|3000|closure"]["E"], central=dict(margin=NV["500000|3000|closure"]["margin"], bound=NV["500000|3000|closure"]["free_bound"],
                    tea=NV["500000|3000|closure"]["tea"], panela=NV["500000|3000|closure"]["best"]["products"]["azucar_kg"] / 1000,
                    net=NV["500000|3000|closure"]["best"]["products"]["gwp_neto_kg"] / 1000),
                    vin_only=dict(margin=NV["100000|3000|closure"]["margin"], bound=NV["100000|3000|closure"]["free_bound"]))
C["mono"] = R("mono.json")
WS = R("ws.json"); b13 = [e for e in WS["each"] if e["sup"] == 1.3][0]["bound"]; b07 = R("nest207.json")["0.7"]["bound"]
C["cert"] = dict(bound_218_13=b13, gap_central=(b13 - c207[(500000, 3000)]["best"]["margin"]) / c207[(500000, 3000)]["best"]["margin"],
                 ws_ub=0.25 * b07 + 0.75 * b13, evpi_ub=0.25 * b07 + 0.75 * b13 - c207[(500000, 3000)]["best"]["margin"])
C["vin_only"] = {"20.7": c207[(100000, 3000)]["best"]["margin"], "13.5": R("c135_vin.json")["100000|3000"]["best"]["margin"],
                 "11.1": R("c111_vin.json")["100000|3000"]["best"]["margin"]}
C["vin_only_bound"] = {"20.7": c207[(100000, 3000)]["free"]["bound"], "13.5": R("c135_vin.json")["100000|3000"]["free"]["bound"],
                       "11.1": R("c111_vin.json")["100000|3000"]["free"]["bound"]}
C["vin_only_npv"] = {k: sec(v) for k, v in C["vin_only"].items()}
# ---- fiscal (20,7)
F = R("fiscal207.json")
C["fiscal"] = {k: dict(best=v["best"]["margin"], bottles=v["best"]["products"]["botellas"], bound=v["free_bound"], best_npv=(v["best_tea"] or {}).get("NPV"),
                       best_npv_sec=sec(v["best"]["margin"]), central=v["central"]["margin"], central_fruit=v["central"]["products"]["fruta_t"],
                       central_npv=(v["central_tea"] or {}).get("NPV")) for k, v in F.items()}
C["fiscal_bottle"] = T["fiscal_bottle"]
# ---- ACV (20,7)
A = R("acv207.json"); gw = A["gwp"]; base = A["base"]
dep = gw["Compostaje de fracciones sin uso"] + gw["Pulpa y jugo de hojas devueltos al campo"]; fixed = A["gwp_total"] - dep; f0 = dm.EF_COMP
C["lca"] = dict(ledger={k: v / 1000 for k, v in gw.items()}, total=A["gwp_total"] / 1000, base={k: v / 1000 for k, v in base.items()},
                rows=[dict(f=f, process=(fixed + f / f0 * dep) / 1000, base_dec=f / f0 * (base["fruta"] + base["hojas_descomposicion"]) / 1000,
                           net_dec=(fixed + f / f0 * dep - f / f0 * (base["fruta"] + base["hojas_descomposicion"])) / 1000,
                           base_burn=(f / f0 * base["fruta"] + base["hojas_quema"]) / 1000,
                           net_burn=(fixed + f / f0 * dep - f / f0 * base["fruta"] - base["hojas_quema"]) / 1000) for f in (f0 - 100, f0, f0 + 100)],
                alloc=A.get("asignacion"), pm=A["pm_evitado_kg"])
# ---- neutralidad (20,7): óptimo → diseño de GWP neto ≤ 0
Gw, N = R("gwp207.json"), R("neutral207.json")
ta, tb_ = Gw["optimum"]["terms"], N["terms"]; po, pn = Gw["optimum"]["short"]["products"], N["products"]
EFB = dm.EF_BASE / 1000
dl = pn["hojas_t"] - po["hojas_t"]; df = pn["fruta_t"] - po["fruta_t"]
field_leaves = dm.EF_FIELD_PULP * dm.PF_H * dl / 1000
field_pulp = (tb_["Leaf pulp and juice returned to the field"] - ta["Leaf pulp and juice returned to the field"]) - field_leaves
d = {k: tb_[k] - ta[k] for k in ta}
cat = dict(leaf_boundary=field_leaves + d["Leaf collection (diesel)"] - EFB * dl,
           pulp_and_fuel=field_pulp + d["LPG heat"] + d["Biomass boiler (CH4, N2O)"],
           fruit=-EFB * df + d["Composting of unused fractions"] + d["Fruit transport"] + d["Panela"],
           other=d["Electricity (diesel genset)"] + d["Aeration and other fixed electricity"] + d["Chemicals and other"] + d["Glass bottles"])
C["neutral"] = dict(margin=(Gw["optimum"]["short"]["margin"], N["short"]["margin"]), bound=N["short"]["bound"], npv=(Gw["optimum"]["tea"]["NPV"], N["tea"]["NPV"]),
                    gwp=(po["gwp_kg"] / 1000, pn["gwp_kg"] / 1000), net=(po["gwp_neto_kg"] / 1000, pn["gwp_neto_kg"] / 1000),
                    base=(EFB * (po["fruta_t"] + po["hojas_t"]), EFB * (pn["fruta_t"] + pn["hojas_t"])), fruit=(po["fruta_t"], pn["fruta_t"]),
                    leaves=(po["hojas_t"], pn["hojas_t"]), terms_opt=ta, terms_neu=tb_, delta=d, base_fruit=EFB * df, base_leaf=EFB * dl,
                    field_leaves=field_leaves, field_pulp=field_pulp, categories=cat, products=pn, sizes=N["short"]["sizes"],
                    w075_fixed=dict(margin=Gw["w075"]["short"]["margin"], net=Gw["w075"]["short"]["products"]["gwp_neto_kg"] / 1000, npv=Gw["w075"]["tea"]["NPV"]))
sens = []
for lab, terms, bse in (("optimum", ta, C["neutral"]["base"][0]), ("neutral", tb_, C["neutral"]["base"][1])):
    dp = terms["Composting of unused fractions"] + terms["Leaf pulp and juice returned to the field"]; Gt = sum(terms.values())
    for f in (f0 - 100, f0, f0 + 100):
        k = f / f0; sens.append(dict(design=lab, f=f, net=Gt - dp + k * dp - k * bse))
C["neutral"]["sens"] = sens
json.dump(C, open(os.path.join(dm.RES, "respuesta", "cifras.json"), "w"), indent=1, default=float)
if __name__ == "__main__":
    print(json.dumps({k: C[k] for k in ("secant", "frontier", "vin_only", "vin_only_npv", "vin_only_bound")}, indent=1, default=float))
    print(json.dumps(C["central"], indent=1, default=float)[:1500])
    for k, v in sorted(grid.items(), key=lambda kv: (kv[1]["vinegar"], kv[1]["bottles"])):
        print(k, round(v["margin"]), v["NPV"] and round(v["NPV"]), round(v["NPV_secant"]), v["bound"] and round(v["bound"]), round(v["fruit"] or 0))
    for k, v in C["fiscal"].items(): print(k, {kk: (round(vv) if isinstance(vv, float) else vv) for kk, vv in v.items()})
    for r in C["lca"]["rows"]: print({kk: round(vv, 1) for kk, vv in r.items()})
    print({k: round(v, 1) for k, v in C["neutral"]["categories"].items()}, round(C["neutral"]["field_leaves"], 1), round(C["neutral"]["field_pulp"], 1), round(C["neutral"]["base_fruit"], 1), round(C["neutral"]["base_leaf"], 1))
    for r in sens: print(r)
    print(C["neutral"]["margin"], C["neutral"]["npv"], C["neutral"]["net"], C["neutral"]["w075_fixed"])
    print(json.dumps(C["leaf"], indent=1, default=float))
