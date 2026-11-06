"""
Comparación entre las versiones 11 y 12.

1) Descomposición del margen del óptimo v11 con su diseño fijo, en pasos acumulados:
   a) óptimo v11 (vino a granel a 3 000 COP/L, sin impuesto al consumo, sin tope de demanda de vino);
   b) + vino embotellado con impuesto al consumo (Ley 1816 de 2016), IVA y margen de distribución, con la embotelladora
      que elija el modelo;
   c) + tope de demanda de vino embotellado (registro, [S]) = diseño v11 con parámetros v12;
   luego la reoptimización de dimensionamiento.py (óptimo v12).
2) Productos, TEA (con el escenario de prórroga ZOMAC) y barrido de demanda de vino (E9) de las dos versiones.
Salida: results/comparativo_v11_v12.json y figs/fig47_comparativo_v11_v12.png.
"""
import json, os, sys
import numpy as np
import dimensionamiento as dm
import datos as DT

RES = dm.RES


def decompose():
    v11 = json.load(open(f"{RES}/v11/dimensionamiento.json"))["E1|Óptimo económico"]
    fix = dict(v11["sizes"], turno3=v11["turno3"])
    base = dict(B=dm.BOTTLED, W=dm.WINE_DEMAND_M3)
    steps = []
    for lab, bott, wdem in (("Óptimo v11 (vino a granel, sin impuesto)", False, None),
                            ("Vino embotellado con impuesto al consumo", True, None),
                            (f"Demanda de vino ≤ {DT.val('demanda_vino_botellas'):,.0f} botellas/año".replace(",", " "), True, base["W"])):
        dm.BOTTLED, dm.WINE_DEMAND_M3 = bott, wdem
        r = dm.solve(fix=fix, time_limit=150, mg=dm.margins())
        p = r["scen"][0]["products"]
        steps.append(dict(label=lab, obj=r["obj"], vinagre_m3=p["vinagre_m3"], vino_vendido_m3=p["vino_m3"] - p["vino_a_vinagre_m3"],
                          botellas=p.get("botellas", 0.0), azucar_kg=p.get("azucar_kg", 0.0), embotelladora=r["sizes"].get("Embotelladora")))
        print(lab, round(r["obj"]), flush=True)
    dm.BOTTLED, dm.WINE_DEMAND_M3 = base["B"], base["W"]
    dm.margins()
    return steps


PRODS = [("Vino vendido (m³)", lambda p: p["vino_m3"] - p.get("vino_a_vinagre_m3", 0)), ("Vino a vinagre (m³)", lambda p: p.get("vino_a_vinagre_m3", 0)),
         ("Jugo de cáscara a vinagre (t)", lambda p: p.get("jugo_cascara_vinagre_t", 0)), ("Jugo de hojas a vinagre (t)", lambda p: p.get("jugo_hojas_vinagre_t", 0)),
         ("Panela añadida (t)", lambda p: p.get("azucar_kg", 0) / 1000), ("Vinagre al 5 % (m³)", lambda p: p.get("vinagre_m3", 0)),
         ("Harina (t)", lambda p: p["harina_t"] + p.get("harina_lias_t", 0)), ("Hojas acopiadas (t)", lambda p: p.get("hojas_t", 0)),
         ("Botellas vendidas (miles)", lambda p: p.get("botellas", 0) / 1000)]
CASES_TEA = [("Referencia TRL-9", "A · Referencia TRL-9"), ("Óptimo", "A · Óptimo con la superestructura ampliada"),
             ("Sin vinagre", "A · Óptimo sin vinagre"), ("Sin caldera de corona", "A · Óptimo sin caldera de corona"),
             ("B con bromelaína de corazón", "B · Óptimo con la superestructura ampliada")]
E9_KEYS = [("250 mil", "E9|demanda 250 000 botellas/año"), ("500 mil (central)", "E1|Óptimo económico"), ("1 millón", "E9|demanda 1 000 000 botellas/año"),
           ("2 millones", "E9|demanda 2 000 000 botellas/año"), ("sin tope", "E1|Óptimo sin tope de demanda de vino")]


def compare():
    d11, d12 = (json.load(open(f)) for f in (f"{RES}/v11/dimensionamiento.json", f"{RES}/dimensionamiento.json"))
    t11, t12 = (json.load(open(f)) for f in (f"{RES}/v11/tea_dimensionado.json", f"{RES}/tea_dimensionado.json"))
    o11, o12 = d11["E1|Óptimo económico"], d12["E1|Óptimo económico"]
    p11, p12 = o11["scen"][0]["products"], o12["scen"][0]["products"]
    tea = []
    for lab, key in CASES_TEA:
        a, b = t11["cases"].get(key), t12["cases"].get(key)
        if a and b:
            tea.append(dict(label=lab, NPV11=a["res"]["NPV"], NPV12=b["res"]["NPV"], MIRR11=a["res"]["MIRR"], MIRR12=b["res"]["MIRR"],
                            P11=a["mc"]["P_pos"], P12=b["mc"]["P_pos"], FCI11=a["res"]["FCI"], FCI12=b["res"]["FCI"],
                            NPV12_prorroga=b.get("NPV_zomac_prorroga"), size=b.get("size")))
    e9 = []
    for lab, key in E9_KEYS:
        r = d12.get(key)
        if r and r.get("scen"):
            p = r["scen"][0]["products"]
            e9.append(dict(label=lab, key=key, obj=r["obj"], botellas=p.get("botellas", 0), vino_vendido_m3=p["vino_m3"] - p["vino_a_vinagre_m3"],
                           vinagre_m3=p["vinagre_m3"], azucar_t=p.get("azucar_kg", 0) / 1000, sizes=r["sizes"]))
    extra = {k.split("|")[1]: dict(obj=r["obj"], botellas=r["scen"][0]["products"].get("botellas", 0), vinagre_m3=r["scen"][0]["products"]["vinagre_m3"],
                                   vino_m3=r["scen"][0]["products"]["vino_m3"])
             for k, r in d12.items() if k.startswith("E9|") and r.get("scen") and ("PVP" in k or "granel" in k)}
    scale = [dict(f=float(k.split("|")[1]), v11=d11.get(k, {}).get("obj"), v12=d12[k]["obj"], sizes12=d12[k]["sizes"]) for k in d12 if k.startswith("E2|")]
    return dict(prods=[dict(label=l, v11=f(p11), v12=f(p12)) for l, f in PRODS], tea=tea, e9=e9, e9_extra=extra,
                scale=sorted(scale, key=lambda s: s["f"]), wine_bottle=dm.wine_bottle(),
                tornado12=t12["cases"]["A · Óptimo con la superestructura ampliada"]["tornado"][:10])


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK, INK2, save
    d12 = json.load(open(f"{RES}/dimensionamiento.json"))
    g = lambda k: d12[k]["obj"] if k in d12 else None
    seq = [(s["label"], s["obj"]) for s in out["decomp"]]
    seq += [("Reoptimización del diseño (óptimo v12)", g("E1|Óptimo económico"))]
    seq = [(l, v) for l, v in seq if v is not None] + [("Óptimo v12", g("E1|Óptimo económico"))]
    fig, ax = plt.subplots(2, 2, figsize=(15.5, 9.6))
    a = ax[0, 0]; prev = 0.0
    for i, (l, v) in enumerate(seq):
        if i == 0 or i == len(seq) - 1:
            a.bar(i, v, color=C[0] if i == 0 else C[2], width=0.62); a.text(i, v + 50, f"{v:,.0f}".replace(",", " "), ha="center", fontsize=8.5, fontweight="bold")
        else:
            dl = v - prev
            a.bar(i, dl if abs(dl) > 1 else 1, bottom=prev, color=C[7] if dl < 0 else C[2], alpha=0.85, width=0.62)
            a.text(i, max(prev, v) + 50, f"{dl:+,.0f}".replace(",", " ") if abs(dl) >= 0.5 else "0", ha="center", fontsize=8.5)
        if i:
            a.plot([i - 1.31, i - 0.69], [prev, prev], color=INK2, lw=0.8)
        prev = v
    a.set_xticks(range(len(seq))); a.set_xticklabels([l for l, _ in seq], rotation=25, ha="right", fontsize=7.6)
    a.set_ylabel("Margen anual del MILP (MM COP/año)"); a.set_title("De la v11 a la v12: impuesto, embotellado y demanda de vino con el diseño v11 fijo", fontsize=9)
    b = ax[0, 1]; E = out["e9"]
    x = np.arange(len(E))
    b.bar(x - 0.2, [e["vinagre_m3"] for e in E], 0.4, color=C[3], label="vinagre al 5 % (m³/año)")
    b.bar(x + 0.2, [e["vino_vendido_m3"] for e in E], 0.4, color=C[0], label="vino embotellado vendido (m³/año)")
    b2 = b.twinx(); b2.plot(x, [e["obj"] for e in E], "-o", color=C[2], label="margen"); b2.set_ylabel("Margen (MM COP/año)", color=C[2])
    b.set_xticks(x); b.set_xticklabels([e["label"] for e in E], fontsize=8); b.set_xlabel("Demanda de vino embotellado (botellas/año)")
    b.set_ylabel("m³/año"); b.legend(fontsize=7.5, loc="upper left")
    b.set_title("E9: margen y destino del vino según la demanda de botellas (vinagre ≤ 3 000 m³/año)", fontsize=9)
    c = ax[1, 0]; P = [p_ for p_ in out["prods"] if max(p_["v11"], p_["v12"]) > 0]
    y = np.arange(len(P))
    c.barh(y - 0.2, [p_["v11"] for p_ in P], 0.4, color=C[0], label="v11"); c.barh(y + 0.2, [p_["v12"] for p_ in P], 0.4, color=C[2], label="v12")
    c.set_yticks(y); c.set_yticklabels([p_["label"] for p_ in P], fontsize=8); c.invert_yaxis(); c.legend(fontsize=8)
    c.set_title("Productos e insumos del óptimo por año", fontsize=9)
    dd = ax[1, 1]; T = out["tea"]; x = np.arange(len(T))
    dd.bar(x - 0.2, [t["NPV11"] / 1e6 for t in T], 0.4, color=C[0], label="VPN v11"); dd.bar(x + 0.2, [t["NPV12"] / 1e6 for t in T], 0.4, color=C[2], label="VPN v12")
    dd.plot(x + 0.2, [(t["NPV12_prorroga"] or float("nan")) / 1e6 for t in T], "D", color=C[3], ms=5, label="v12 con prórroga ZOMAC (PL 435/2025)")
    for xi, t in zip(x, T):
        dd.text(xi - 0.2, max(t["NPV11"], 0) / 1e6 + 150, f"{t['P11']:.2f}", ha="center", fontsize=7.5, color=C[0])
        dd.text(xi + 0.2, max(t["NPV12"], 0) / 1e6 + 150, f"{t['P12']:.2f}", ha="center", fontsize=7.5, color=C[2])
    dd.axhline(0, color=INK2, lw=0.8); dd.set_xticks(x); dd.set_xticklabels([t["label"] for t in T], rotation=15, ha="right", fontsize=8)
    dd.set_ylabel("VPN (MM COP)"); dd.legend(fontsize=8); dd.set_title("TEA: VPN de los casos comparables (número: P(VPN > 0))", fontsize=9)
    fig.suptitle("Fig. 47  Comparación entre las versiones 11 y 12", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig47_comparativo_v11_v12.png")


if __name__ == "__main__":
    out_p = f"{RES}/comparativo_v11_v12.json"
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    if "decomp" in sys.argv[1:] or "decomp" not in out:
        out["decomp"] = decompose()
        json.dump(out, open(out_p, "w"), default=float)
    if "compare" in sys.argv[1:]:
        out.update(compare())
        figure(out)
    json.dump(out, open(out_p, "w"), default=float)
