"""
Comparación entre las versiones 10 y 11.

1) Descomposición del margen del óptimo v10 con su diseño fijo, en pasos acumulados:
   a) óptimo v10 (parámetros v10: sin panela, sin tope de demanda, xantana a 0,6 g/g);
   b) + rendimiento de xantana con residuo de piña (0,083 g/g; Rashidi et al. 2024 en Iakovchenko 2026);
   c) + tope de demanda de vinagre (registro, [S]);
   d) + panela añadida a los jugos (Ebrahimi 2026; Tanamool et al. 2020) = diseño v10 con parámetros v11;
   luego las reoptimizaciones de dimensionamiento.py: sin azúcar añadido y óptimo v11.
2) Productos, TEA y barrido de demanda (E8) de las dos versiones.
Salida: results/comparativo_v10_v11.json y figs/fig46_comparativo_v10_v11.png.
"""
import json, os, sys
import numpy as np
import dimensionamiento as dm
import datos as DT

RES = dm.RES


def decompose():
    v10 = json.load(open(f"{RES}/v10/dimensionamiento.json"))["E1|Óptimo económico"]
    fix = dict(v10["sizes"], turno3=v10["turno3"])
    base = dict(SUGAR=dm.SUGAR, VIN_DEMAND=dm.VIN_DEMAND, y=dm.HUB["Xantana"]["y"])
    steps = []
    for lab, sugar, dem, y in (("Óptimo v10 (parámetros v10)", False, None, DT.val("y_xantana")),
                               ("Xantana con residuo de piña (0,083 g/g)", False, None, base["y"]),
                               (f"Demanda de vinagre ≤ {base['VIN_DEMAND']:,.0f} m³/año".replace(",", " "), False, base["VIN_DEMAND"], base["y"]),
                               ("Panela añadida a los jugos", True, base["VIN_DEMAND"], base["y"])):
        dm.SUGAR, dm.VIN_DEMAND, dm.HUB["Xantana"]["y"] = sugar, dem, y
        r = dm.solve(fix=fix, time_limit=120)
        p = r["scen"][0]["products"]
        steps.append(dict(label=lab, obj=r["obj"], vinagre_m3=p["vinagre_m3"], vino_vendido_m3=p["vino_m3"] - p["vino_a_vinagre_m3"],
                          azucar_kg=p.get("azucar_kg", 0.0), hojas_t=p.get("hojas_t", 0.0)))
        print(lab, round(r["obj"]), flush=True)
    dm.SUGAR, dm.VIN_DEMAND, dm.HUB["Xantana"]["y"] = base["SUGAR"], base["VIN_DEMAND"], base["y"]
    return steps


PRODS = [("Vino vendido (m³)", lambda p: p["vino_m3"] - p.get("vino_a_vinagre_m3", 0)), ("Vino a vinagre (m³)", lambda p: p.get("vino_a_vinagre_m3", 0)),
         ("Jugo de cáscara a vinagre (t)", lambda p: p.get("jugo_cascara_vinagre_t", 0)), ("Jugo de hojas a vinagre (t)", lambda p: p.get("jugo_hojas_vinagre_t", 0)),
         ("Panela añadida (t)", lambda p: p.get("azucar_kg", 0) / 1000), ("Vinagre al 5 % (m³)", lambda p: p.get("vinagre_m3", 0)),
         ("Harina (t)", lambda p: p["harina_t"] + p.get("harina_lias_t", 0)), ("Hojas acopiadas (t)", lambda p: p.get("hojas_t", 0))]
CASES_TEA = [("Referencia TRL-9", "A · Referencia TRL-9"), ("Óptimo", "A · Óptimo con la superestructura ampliada"),
             ("Sin vinagre", "A · Óptimo sin vinagre"), ("Sin caldera de corona", "A · Óptimo sin caldera de corona"),
             ("B con bromelaína de corazón", "B · Óptimo con la superestructura ampliada")]
E8_KEYS = [("1 500", "E8|demanda 1 500 m³/año"), ("3 000 (central)", "E1|Óptimo económico"), ("6 000", "E8|demanda 6 000 m³/año"),
           ("12 000", "E8|demanda 12 000 m³/año"), ("sin tope", "E1|Óptimo sin tope de demanda de vinagre")]


def compare():
    d10, d11 = (json.load(open(f)) for f in (f"{RES}/v10/dimensionamiento.json", f"{RES}/dimensionamiento.json"))
    t10, t11 = (json.load(open(f)) for f in (f"{RES}/v10/tea_dimensionado.json", f"{RES}/tea_dimensionado.json"))
    o10, o11 = d10["E1|Óptimo económico"], d11["E1|Óptimo económico"]
    p10, p11 = o10["scen"][0]["products"], o11["scen"][0]["products"]
    tea = []
    for lab, key in CASES_TEA:
        a, b = t10["cases"].get(key), t11["cases"].get(key)
        if a and b:
            tea.append(dict(label=lab, NPV10=a["res"]["NPV"], NPV11=b["res"]["NPV"], MIRR10=a["res"]["MIRR"], MIRR11=b["res"]["MIRR"],
                            P10=a["mc"]["P_pos"], P11=b["mc"]["P_pos"], FCI10=a["res"]["FCI"], FCI11=b["res"]["FCI"]))
    e8 = []
    for lab, key in E8_KEYS:
        r = d11.get(key)
        if r and r.get("scen"):
            p = r["scen"][0]["products"]
            e8.append(dict(label=lab, key=key, obj=r["obj"], vinagre_m3=p["vinagre_m3"], vino_vendido_m3=p["vino_m3"] - p["vino_a_vinagre_m3"],
                           azucar_t=p.get("azucar_kg", 0) / 1000, hojas_t=p.get("hojas_t", 0), sizes=r["sizes"]))
    extra = {k.split("|")[1]: dict(obj=r["obj"], vinagre_m3=r["scen"][0]["products"]["vinagre_m3"], azucar_t=r["scen"][0]["products"].get("azucar_kg", 0) / 1000,
                                   vino_vendido_m3=r["scen"][0]["products"]["vino_m3"] - r["scen"][0]["products"]["vino_a_vinagre_m3"])
             for k, r in d11.items() if k.startswith("E8|") and r.get("scen") and ("sin azúcar" in k or "panela" in k)}
    scale = [dict(f=float(k.split("|")[1]), v10=d10.get(k, {}).get("obj"), v11=d11[k]["obj"], sizes11=d11[k]["sizes"]) for k in d11 if k.startswith("E2|")]
    milp = [dict(key=k, v10=d10.get(k, {}).get("obj"), v11=d11[k].get("obj"), sizes11=d11[k].get("sizes")) for k in d11
            if k[:3] in ("E1|", "E5|", "E7|", "E8|")]
    return dict(prods=[dict(label=l, v10=f(p10), v11=f(p11)) for l, f in PRODS], tea=tea, e8=e8, e8_extra=extra,
                scale=sorted(scale, key=lambda s: s["f"]), milp=milp,
                tornado11=t11["cases"]["A · Óptimo con la superestructura ampliada"]["tornado"][:10])


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK, INK2, save
    d11 = json.load(open(f"{RES}/dimensionamiento.json"))
    g = lambda k: d11[k]["obj"] if k in d11 else None
    seq = [(s["label"], s["obj"]) for s in out["decomp"]]
    seq += [("Reoptimización sin azúcar añadido", g("E1|Óptimo sin azúcar añadido")), ("Reoptimización con panela (óptimo v11)", g("E1|Óptimo económico"))]
    seq = [(l, v) for l, v in seq if v is not None] + [("Óptimo v11", g("E1|Óptimo económico"))]
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
    a.set_ylabel("Margen anual del MILP (MM COP/año)"); a.set_title("De la v10 a la v11: datos nuevos con el diseño v10 fijo y reoptimización", fontsize=9)
    b = ax[0, 1]; E = out["e8"]
    x = np.arange(len(E))
    b.bar(x - 0.2, [e["vinagre_m3"] for e in E], 0.4, color=C[3], label="vinagre al 5 % (m³/año)")
    b.bar(x + 0.2, [e["vino_vendido_m3"] for e in E], 0.4, color=C[0], label="vino vendido (m³/año)")
    b2 = b.twinx(); b2.plot(x, [e["obj"] for e in E], "-o", color=C[2], label="margen"); b2.set_ylabel("Margen (MM COP/año)", color=C[2])
    b.set_xticks(x); b.set_xticklabels([e["label"] for e in E], fontsize=8); b.set_xlabel("Demanda de vinagre (m³/año)")
    b.set_ylabel("m³/año"); b.legend(fontsize=7.5, loc="upper left")
    b.set_title("E8: la demanda de vinagre decide cuánto vino se vende", fontsize=9)
    c = ax[1, 0]; P = [p_ for p_ in out["prods"] if max(p_["v10"], p_["v11"]) > 0]
    y = np.arange(len(P))
    c.barh(y - 0.2, [p_["v10"] for p_ in P], 0.4, color=C[0], label="v10"); c.barh(y + 0.2, [p_["v11"] for p_ in P], 0.4, color=C[2], label="v11")
    c.set_yticks(y); c.set_yticklabels([p_["label"] for p_ in P], fontsize=8); c.invert_yaxis(); c.legend(fontsize=8)
    c.set_title("Productos e insumos del óptimo por año", fontsize=9)
    dd = ax[1, 1]; T = out["tea"]; x = np.arange(len(T))
    dd.bar(x - 0.2, [t["NPV10"] / 1e6 for t in T], 0.4, color=C[0], label="VPN v10"); dd.bar(x + 0.2, [t["NPV11"] / 1e6 for t in T], 0.4, color=C[2], label="VPN v11")
    for xi, t in zip(x, T):
        dd.text(xi - 0.2, max(t["NPV10"], 0) / 1e6 + 150, f"{t['P10']:.2f}", ha="center", fontsize=7.5, color=C[0])
        dd.text(xi + 0.2, max(t["NPV11"], 0) / 1e6 + 150, f"{t['P11']:.2f}", ha="center", fontsize=7.5, color=C[2])
    dd.axhline(0, color=INK2, lw=0.8); dd.set_xticks(x); dd.set_xticklabels([t["label"] for t in T], rotation=15, ha="right", fontsize=8)
    dd.set_ylabel("VPN (MM COP)"); dd.legend(fontsize=8); dd.set_title("TEA: VPN de los casos comparables (número: P(VPN > 0))", fontsize=9)
    fig.suptitle("Fig. 46  Comparación entre las versiones 10 y 11", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig46_comparativo_v10_v11.png")


if __name__ == "__main__":
    out_p = f"{RES}/comparativo_v10_v11.json"
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    if "decomp" in sys.argv[1:] or "decomp" not in out:
        out["decomp"] = decompose()
        json.dump(out, open(out_p, "w"), default=float)
    if "compare" in sys.argv[1:]:
        out.update(compare())
        figure(out)
    json.dump(out, open(out_p, "w"), default=float)
