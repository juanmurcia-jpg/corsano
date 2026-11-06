"""
Comparación entre las versiones 9 y 10.

1) Descomposición del margen del óptimo v9 en pasos acumulados, con su diseño fijo:
   a) óptimo v9 (parámetros v9); b) + tiempo del jugo de cáscara de la cinética calibrada (12,6 h en lugar de 32,5 h);
   c) + restricción de mezcla del vinagre (solo se puede diluir) = diseño v9 con parámetros v10;
   luego, corridas de dimensionamiento.py: reoptimización sin opciones nuevas y óptimo v10 (hojas, etanol, biogás, hub).
2) Productos, TEA, ACV, social y escala de las dos versiones.
Salida: results/comparativo_v9_v10.json y figs/fig45_comparativo_v9_v10.png.
"""
import json, os, sys
import numpy as np
import dimensionamiento as dm

RES = dm.RES
NEW10 = ("Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás", "Ácido cítrico", "Xantana")


def decompose():
    v9 = json.load(open(f"{RES}/dimensionamiento_v9.json"))["E1|Óptimo económico"]
    fix = dict(v9["sizes"], turno3=v9["turno3"], **{u: "no" for u in NEW10})
    T0 = dm.T_PEEL
    steps = []
    for lab, T, blend in (("Óptimo v9 (parámetros v9)", 30.0 + 2.5, False), ("Jugo de cáscara en 12,6 h (cinética calibrada)", T0, False),
                          ("Restricción de mezcla del vinagre", T0, True)):
        dm.T_PEEL, dm.BLEND = T, blend
        r = dm.solve(fix=fix, time_limit=120)
        pr = r["scen"][0]["products"]
        steps.append(dict(label=lab, obj=r["obj"], vinagre_m3=pr["vinagre_m3"], vino_vendido_m3=pr["vino_m3"] - pr["vino_a_vinagre_m3"],
                          FCI=r["FCI"]))
        print(lab, round(r["obj"]), flush=True)
    dm.T_PEEL, dm.BLEND = T0, True
    return steps


PRODS = [("Vino vendido (m³)", lambda p: p["vino_m3"] - p.get("vino_a_vinagre_m3", 0)), ("Vino a vinagre (m³)", lambda p: p.get("vino_a_vinagre_m3", 0)),
         ("Jugo de cáscara a vinagre (t)", lambda p: p.get("jugo_cascara_vinagre_t", 0)), ("Jugo de hojas a vinagre (t)", lambda p: p.get("jugo_hojas_vinagre_t", 0)),
         ("Vinagre al 5 % (m³)", lambda p: p.get("vinagre_m3", 0)), ("Harina (t)", lambda p: p["harina_t"] + p.get("harina_lias_t", 0)),
         ("Hojas acopiadas (t)", lambda p: p.get("hojas_t", 0)), ("Etanol (L)", lambda p: p.get("etanol_L", 0)),
         ("Electricidad de biogás (kWh)", lambda p: p.get("elec_bio_kWh", 0))]
CASES_TEA = [("Referencia TRL-9", "A · Referencia TRL-9"), ("Óptimo", "A · Óptimo con la superestructura ampliada"),
             ("Sin vinagre", "A · Óptimo sin vinagre"), ("Sin caldera de corona", "A · Óptimo sin caldera de corona"),
             ("B con bromelaína de corazón", "B · Óptimo con la superestructura ampliada")]


def compare():
    d9, d10 = (json.load(open(f"{RES}/{f}")) for f in ("dimensionamiento_v9.json", "dimensionamiento.json"))
    t9, t10 = (json.load(open(f"{RES}/{f}")) for f in ("tea_dimensionado_v9.json", "tea_dimensionado.json"))
    o9, o10 = d9["E1|Óptimo económico"], d10["E1|Óptimo económico"]
    p9, p10 = o9["scen"][0]["products"], o10["scen"][0]["products"]
    tea = []
    for lab, key in CASES_TEA:
        a, b = t9["cases"].get(key), t10["cases"].get(key)
        if a and b:
            tea.append(dict(label=lab, NPV9=a["res"]["NPV"], NPV10=b["res"]["NPV"], MIRR9=a["res"]["MIRR"], MIRR10=b["res"]["MIRR"],
                            P9=a["mc"]["P_pos"], P10=b["mc"]["P_pos"], FCI9=a["res"]["FCI"], FCI10=b["res"]["FCI"]))
    scale = [dict(f=float(k.split("|")[1]), v9=d9.get(k, {}).get("obj"), v10=d10[k]["obj"], sizes10=d10[k]["sizes"]) for k in d10 if k.startswith("E2|")]
    milp = [dict(key=k, v9=d9.get(k, {}).get("obj"), v10=d10[k].get("obj"), sizes10=d10[k].get("sizes")) for k in d10 if k.startswith("E1|") or k.startswith("E5|") or k.startswith("E7|")]
    return dict(prods=[dict(label=l, v9=f(p9), v10=f(p10)) for l, f in PRODS], tea=tea, scale=sorted(scale, key=lambda s: s["f"]), milp=milp,
                tornado10=t10["cases"]["A · Óptimo con la superestructura ampliada"]["tornado"][:10])


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK, INK2, save
    d10 = json.load(open(f"{RES}/dimensionamiento.json"))
    g = lambda k: d10[k]["obj"] if k in d10 else None
    seq = [(s["label"], s["obj"]) for s in out["decomp"]]
    seq += [("Reoptimización sin opciones v10", g("E1|Óptimo sin opciones v10 (sin hojas ni hub)")), ("+ hojas, etanol, biogás y hub (óptimo v10)", g("E1|Óptimo económico"))]
    seq = [(l, v) for l, v in seq if v is not None] + [("Óptimo v10", g("E1|Óptimo económico"))]
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
    a.set_ylabel("Margen anual del MILP (MM COP/año)"); a.set_title("De la v9 a la v10: correcciones del modelo y opciones nuevas", fontsize=9)
    b = ax[0, 1]; S = out["scale"]
    xs = [s["f"] * dm.SUPPLY for s in S]
    b.plot(xs, [s["v9"] for s in S], "-o", color=C[0], label="v9"); b.plot(xs, [s["v10"] for s in S], "-s", color=C[2], label="v10")
    for x_, s in zip(xs, S):
        if s["sizes10"].get("Extractora hojas", "no") != "no":
            b.plot([x_], [s["v10"]], "o", ms=11, mfc="none", mec=C[3], mew=1.6)
    b.axvline(dm.SUPPLY, color="#cccccc", ls="--"); b.set_xlabel("Oferta de fruta (t/año)"); b.set_ylabel("Margen (MM COP/año)"); b.legend(fontsize=8)
    b.set_title("Margen según la oferta (círculo ámbar: la v10 acopia hojas)", fontsize=9)
    c = ax[1, 0]; T = out["tea"]; x = np.arange(len(T))
    c.bar(x - 0.2, [t["NPV9"] / 1e6 for t in T], 0.4, color=C[0], label="VPN v9"); c.bar(x + 0.2, [t["NPV10"] / 1e6 for t in T], 0.4, color=C[2], label="VPN v10")
    for xi, t in zip(x, T):
        c.text(xi - 0.2, max(t["NPV9"], 0) / 1e6 + 150, f"{t['P9']:.2f}", ha="center", fontsize=7.5, color=C[0])
        c.text(xi + 0.2, max(t["NPV10"], 0) / 1e6 + 150, f"{t['P10']:.2f}", ha="center", fontsize=7.5, color=C[2])
    c.axhline(0, color=INK2, lw=0.8); c.set_xticks(x); c.set_xticklabels([t["label"] for t in T], rotation=15, ha="right", fontsize=8)
    c.set_ylabel("VPN (MM COP)"); c.legend(fontsize=8); c.set_title("TEA: VPN de los casos comparables (número: P(VPN > 0))", fontsize=9)
    dd = ax[1, 1]; tor = [t for t in out["tornado10"] if abs(t["NPV_best"] - t["NPV_worst"]) > 1e6]   # sin barras de ancho cero (p. ej., el vino, que ya no se vende)
    base = json.load(open(f"{RES}/tea_dimensionado.json"))["cases"]["A · Óptimo con la superestructura ampliada"]["res"]["NPV"] / 1e6
    for i, t in enumerate(tor):
        lo, hi = sorted([t["NPV_worst"] / 1e6, t["NPV_best"] / 1e6])
        new = any(w in t["label"] for w in ("acopio", "etanol", "cáscara", "Corona"))
        dd.barh(i, hi - lo, left=lo, color=C[3] if new else C[0], height=0.6)
    dd.axvline(base, color=INK, lw=1); dd.set_yticks(range(len(tor))); dd.set_yticklabels([t["label"] for t in tor], fontsize=7.8); dd.invert_yaxis()
    dd.set_xlabel("VPN (MM COP)"); dd.set_title("Tornado del óptimo v10 (ámbar: incertidumbres de v9 y v10)", fontsize=9)
    fig.suptitle("Fig. 45  Comparación entre las versiones 9 y 10", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig45_comparativo_v9_v10.png")


if __name__ == "__main__":
    out_p = f"{RES}/comparativo_v9_v10.json"
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    if "decomp" in sys.argv[1:] or "decomp" not in out:
        out["decomp"] = decompose()
    if "compare" in sys.argv[1:]:
        out.update(compare())
        figure(out)
    json.dump(out, open(out_p, "w"), default=float)
