"""
Comparación entre las versiones 8 y 9 del dimensionamiento y del TEA.

1) Descomposición del margen anual (MILP de dimensionamiento.py) de la v8 a la v9, en pasos acumulados:
   a) óptimo v8 (parámetros v8);
   b) el mismo diseño con el rendimiento de jugo y la materia seca de la torta de Campos et al. (2020);
   c) + rendimiento de fermentación del jugo de cáscara de Seguí y Fito (2018);
   d) + SO₂ del jugo de cáscara  (= diseño v8 con parámetros v9);
   e) reoptimización sin las opciones nuevas; f) + prensado con cal; g) + enzima del jugo de cáscara (óptimo v9).
   Los pasos a–d evalúan el diseño v8 con tamaños fijos (MILP exacto y pequeño); e–g son corridas de dimensionamiento.py.
2) Productos, cuellos y TEA (VPN, MIRR, P(VPN > 0)) de los casos comparables.
Salida: results/comparativo_v8_v9.json y figs/fig39_comparativo_v8_v9.png.
"""
import json, os, sys
import numpy as np
import capacidad as cp
import planta_trl9 as pt
import dimensionamiento as dm

RES = dm.RES
V9_Y = dict(cp.Y)
V9_A, V9_PJVC = dm.A_PJ, dm.PJ_VC


def set_params(juice=True, ferm=True, so2=True):
    """Restituye los parámetros de la v8 o de la v9 por grupos y recalcula las constantes derivadas del MILP."""
    cp.Y.update(V9_Y if juice else dict(peel_juice_frac=0.50, peel_dm=0.14, cake_dm_ret=0.75))
    dm.B1 = cp.full_balance(1.0)
    dm.FR = dict(pulpa=dm.B1["pulp_t"], cascara=dm.B1["peel_t"], corazon=dm.B1["core_t"])
    dm.CAKE = 1 - cp.Y["peel_juice_frac"]
    dm.FLOUR_PC = (dm.B1["flour_t"] / dm.B1["peel_t"]) / dm.CAKE
    dm.DRY_W = 1 - dm.FLOUR_PC
    dm.LEES_DRY_EQ = (1 - dm.LEES_FLOUR) / dm.DRY_W
    D = pt.design(6200)
    dm.Q_CAKE = D["lines"]["harina"]["heat_MJ"] / (D["lines"]["harina"]["flows"]["peel_t"] * dm.CAKE)
    dm.PJ_FRAC = {"agua": cp.Y["peel_juice_frac"], "cal 0,1 %": 0.684 * 0.95}
    dm.CAKE_FRAC = {"agua": dm.CAKE, "cal 0,1 %": 1 - 0.684}
    dm.ENZ_Y = 0.45 / cp.Y["peel_juice_frac"]
    dm.A_PJ = V9_A if ferm else 104.0 * 0.46 * 0.95 * 60 / 46 * dm.ACET_YIELD
    dm.PJ_VC = V9_PJVC if so2 else V9_PJVC - dm.SO2_VC


def decompose():
    v8 = json.load(open(f"{RES}/dimensionamiento_v8.json"))["E1|Óptimo económico"]
    fix = dict(v8["sizes"], **{"Pretratamiento cáscara": "agua", "Enzima cáscara": "no", "turno3": v8["turno3"]})
    steps = []
    for lab, kw in (("Óptimo v8 (parámetros v8)", dict(juice=False, ferm=False, so2=False)),
                    ("Jugo 0,578 y torta con 17 % de MS (Campos 2020)", dict(juice=True, ferm=False, so2=False)),
                    ("Fermentación del jugo 0,36 g/g (Seguí 2018)", dict(juice=True, ferm=True, so2=False)),
                    ("SO₂ del jugo de cáscara", dict(juice=True, ferm=True, so2=True))):
        set_params(**kw)
        r = dm.solve(fix=fix, time_limit=120)
        pr = r["scen"][0]["products"]
        steps.append(dict(label=lab, obj=r["obj"], harina_t=pr["harina_t"] + pr.get("harina_lias_t", 0), vinagre_m3=pr["vinagre_m3"],
                          vino_vendido_m3=pr["vino_m3"] - pr["vino_a_vinagre_m3"], calor_corona_GJ=pr["calor_corona_GJ"],
                          jugo_cascara_t=pr.get("jugo_cascara_t", 0)))
        print(lab, round(r["obj"]), {k: round(v) for k, v in steps[-1].items() if k not in ("label", "obj")}, flush=True)
    set_params()
    return steps


if __name__ == "__main__":
    out_p = f"{RES}/comparativo_v8_v9.json"
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    if "decomp" in sys.argv[1:] or "decomp" not in out:
        out["decomp"] = decompose()
        json.dump(out, open(out_p, "w"), default=float)


def variants(opt_key="E1|Óptimo económico"):
    """El óptimo v9 con cada opción nueva impuesta (tamaños fijos): cuánto cuesta o aporta cada una a la escala del Chocó."""
    d9 = json.load(open(f"{RES}/dimensionamiento.json"))
    o = d9[opt_key]; out = []
    for lab, ch in (("Óptimo v9", {}), ("Prensado con cal", {"Pretratamiento cáscara": "cal 0,1 %"}),
                    ("Enzima por precipitación 0,25 t/h", {"Enzima cáscara": "Precipitación 0.25 t/h"}),
                    ("Enzima por precipitación 0,5 t/h", {"Enzima cáscara": "Precipitación 0.5 t/h"}),
                    ("Enzima por UF 0,25 t/h", {"Enzima cáscara": "UF 0.25 t/h"}),
                    ("Cal + precipitación 0,5 t/h", {"Pretratamiento cáscara": "cal 0,1 %", "Enzima cáscara": "Precipitación 0.5 t/h"})):
        r = dm.solve(fix=dict(o["sizes"], **ch, turno3=o["turno3"]), time_limit=90)
        p = r["scen"][0]["products"]
        out.append(dict(label=lab, obj=r["obj"], FCI=r["FCI"], harina_t=p["harina_t"] + p.get("harina_lias_t", 0), jugo_t=p.get("jugo_cascara_t", 0),
                        vino_vendido_m3=p["vino_m3"] - p["vino_a_vinagre_m3"], enzima_kg=p.get("enzima_cascara_kg", 0), sizes=r["sizes"]))
        print(lab, round(r["obj"]), flush=True)
    return out


def breakeven_bromelain(opt_key="E1|Óptimo económico", options=("Precipitación 0.25 t/h", "Precipitación 0.5 t/h", "Precipitación 1 t/h", "UF 0.25 t/h")):
    """Precio de la bromelaína (COP/kg) desde el cual agregar la separación de enzima al óptimo v9 sube el margen."""
    d9 = json.load(open(f"{RES}/dimensionamiento.json"))
    o = d9[opt_key]; base = o["obj"]; p0 = dm.BROM_PRICE
    res = []
    for lab in options:
        fix = dict(o["sizes"], **{"Enzima cáscara": lab, "turno3": o["turno3"]})
        f = lambda pr: (setattr(dm, "BROM_PRICE", pr), dm.solve(fix=fix, time_limit=60)["obj"])[1] - base
        lo, hi = p0, 4 * p0
        if f(hi) < 0:
            res.append(dict(option=lab, breakeven=None, at_base=f(p0) + base)); continue
        at_base = f(p0) + base
        for _ in range(14):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        res.append(dict(option=lab, breakeven=0.5 * (lo + hi), at_base=at_base))
        print("precio de equilibrio de la bromelaína", lab, round(res[-1]["breakeven"]), flush=True)
    dm.BROM_PRICE = p0
    return dict(base=base, price=p0, options=res)


# ----------------------------------------------------------------------------- comparación de resultados y figura 39
CASES_TEA = [("Referencia TRL-9", "A · Referencia TRL-9"), ("Topología anterior", "A · Óptimo con la topología anterior"),
             ("Óptimo (superestructura)", "A · Óptimo con la superestructura ampliada"), ("Sin vinagre", "A · Óptimo sin vinagre"),
             ("Sin caldera de corona", "A · Óptimo sin caldera de corona"), ("B con bromelaína de corazón", "B · Óptimo con la superestructura ampliada")]
PRODS = [("Vino vendido (m³)", lambda p: p["vino_m3"] - p.get("vino_a_vinagre_m3", 0)), ("Vino a vinagre (m³)", lambda p: p.get("vino_a_vinagre_m3", 0)),
         ("Jugo de cáscara a vinagre (t)", lambda p: p.get("jugo_cascara_vinagre_t", 0)), ("Vinagre al 5 % (m³)", lambda p: p.get("vinagre_m3", 0)),
         ("Harina (t)", lambda p: p["harina_t"] + p.get("harina_lias_t", 0)), ("Calor de corona (GJ)", lambda p: p.get("calor_corona_GJ", 0)),
         ("Bromelaína de cáscara (kg)", lambda p: p.get("enzima_cascara_kg", 0))]


def compare():
    d8, d9 = (json.load(open(f"{RES}/{f}")) for f in ("dimensionamiento_v8.json", "dimensionamiento.json"))
    t8, t9 = (json.load(open(f"{RES}/{f}")) for f in ("tea_dimensionado_v8.json", "tea_dimensionado.json"))
    o8, o9 = d8["E1|Óptimo económico"], d9["E1|Óptimo económico"]
    p8, p9 = o8["scen"][0]["products"], o9["scen"][0]["products"]
    milp = []
    for k in sorted(set(d8) | set(d9)):
        if k.startswith("E1|") or k.startswith("E5|") or k.startswith("E4|R") or k.startswith("E4|E"):
            a, b = d8.get(k, {}), d9.get(k, {})
            milp.append(dict(key=k, v8=a.get("obj"), v9=b.get("obj"), FCI8=a.get("FCI"), FCI9=b.get("FCI"),
                             sizes8=a.get("sizes"), sizes9=b.get("sizes")))
    scale = [dict(f=k.split("|")[1], v8=d8.get(k, {}).get("obj"), v9=d9[k]["obj"], sizes8=d8.get(k, {}).get("sizes"), sizes9=d9[k]["sizes"],
                  t3_8=d8.get(k, {}).get("turno3"), t3_9=d9[k]["turno3"]) for k in d9 if k.startswith("E2|")]
    tea = []
    for lab, key in CASES_TEA:
        a, b = t8["cases"].get(key), t9["cases"].get(key)
        if a and b:
            tea.append(dict(label=lab, NPV8=a["res"]["NPV"], NPV9=b["res"]["NPV"], MIRR8=a["res"]["MIRR"], MIRR9=b["res"]["MIRR"],
                            P8=a["mc"]["P_pos"], P9=b["mc"]["P_pos"], FCI8=a["res"]["FCI"], FCI9=b["res"]["FCI"],
                            BEv8=a.get("breakeven_vinegar"), BEv9=b.get("breakeven_vinegar")))
    prods = [dict(label=l, v8=f(p8), v9=f(p9)) for l, f in PRODS]
    util8, util9 = ({u: max(v) for u, v in o["scen"][0]["util"].items()} for o in (o8, o9))
    return dict(milp=milp, scale=scale, tea=tea, prods=prods, util8=util8, util9=util9, sizes8=o8["sizes"], sizes9=o9["sizes"],
                tornado9=t9["cases"]["A · Óptimo con la superestructura ampliada"]["tornado"][:9])


def figure(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK, INK2, GRID, save
    d9 = json.load(open(f"{RES}/dimensionamiento.json"))
    fig, ax = plt.subplots(2, 2, figsize=(15.5, 9.6))
    # A: cascada del margen
    st = out["decomp"]
    g = lambda k: d9[k]["obj"] if k in d9 else None
    seq = [(s["label"], s["obj"]) for s in st]
    seq += [("Reoptimización sin opciones nuevas", g("E1|Óptimo sin opciones v9 (sin cal ni enzima)")),
            ("+ prensado con cal (opción)", g("E1|Óptimo sin enzima de cáscara")), ("+ enzima del jugo (óptimo v9)", g("E1|Óptimo económico"))]
    seq = [(l, v) for l, v in seq if v is not None]
    a = ax[0, 0]; prev = 0.0
    seq = seq + [("Óptimo v9", seq[-1][1])]
    for i, (l, v) in enumerate(seq):
        if i == 0 or i == len(seq) - 1:
            a.bar(i, v, color=C[0] if i == 0 else C[2], width=0.62)
            a.text(i, v + 40, f"{v:,.0f}".replace(",", " "), ha="center", fontsize=8.5, fontweight="bold")
        else:
            dlt = v - prev
            a.bar(i, dlt if abs(dlt) > 1 else 1, bottom=prev, color=C[7] if dlt < 0 else C[2], alpha=0.85, width=0.62)
            a.text(i, max(prev, v) + 40, (f"{dlt:+,.0f}".replace(",", " ") if abs(dlt) >= 0.5 else "0"), ha="center", fontsize=8.5)
        if i:
            a.plot([i - 1.31, i - 0.69], [prev, prev], color=INK2, lw=0.8)
        prev = v
    a.set_xticks(range(len(seq))); a.set_xticklabels([l for l, _ in seq], rotation=28, ha="right", fontsize=7.6)
    a.set_ylabel("Margen anual del MILP (MM COP/año)"); a.set_ylim(0, max(v for _, v in seq) * 1.15)
    a.set_title("De la v8 a la v9: qué baja por los datos nuevos y qué recuperan las opciones nuevas", fontsize=9)
    # B: margen según la escala
    b = ax[0, 1]; S_ = sorted(out["scale"], key=lambda s: float(s["f"]))
    xs = [float(s["f"]) * dm.SUPPLY for s in S_]
    b.plot(xs, [s["v8"] for s in S_], "-o", color=C[0], label="v8")
    b.plot(xs, [s["v9"] for s in S_], "-s", color=C[2], label="v9")
    for x_, s in zip(xs, S_):
        ez = s["sizes9"].get("Enzima cáscara", "no")
        if ez != "no":
            b.annotate("enzima " + ez.replace("Precipitación", "prec.").replace(".", ","), (x_, s["v9"]), xytext=(6, -16), textcoords="offset points", fontsize=7.2, color=C[3])
            b.plot([x_], [s["v9"]], "o", ms=11, mfc="none", mec=C[3], mew=1.6)
    b.axvline(dm.SUPPLY, color=GRID, ls="--"); b.text(dm.SUPPLY * 1.02, b.get_ylim()[1] * 0.9, "Chocó 2022", fontsize=7.5, color=INK2)
    b.set_xlim(right=max(xs) * 1.14); b.set_xlabel("Oferta de fruta (t/año)"); b.set_ylabel("Margen anual del MILP (MM COP/año)"); b.legend(fontsize=8, loc="upper left")
    b.set_title("Margen del óptimo según la oferta (círculo ámbar: la v9 separa la enzima)", fontsize=9)
    # C: TEA
    c = ax[1, 0]; T = out["tea"]; x = np.arange(len(T))
    c.bar(x - 0.2, [t["NPV8"] / 1e6 for t in T], 0.4, color=C[0], label="VPN v8")
    c.bar(x + 0.2, [t["NPV9"] / 1e6 for t in T], 0.4, color=C[2], label="VPN v9")
    for xi, t in zip(x, T):
        c.text(xi - 0.2, max(t["NPV8"], 0) / 1e6 + 120, f"{t['P8']:.2f}", ha="center", fontsize=7.5, color=C[0])
        c.text(xi + 0.2, max(t["NPV9"], 0) / 1e6 + 120, f"{t['P9']:.2f}", ha="center", fontsize=7.5, color=C[2])
    c.axhline(0, color=INK2, lw=0.8); c.set_xticks(x); c.set_xticklabels([t["label"] for t in T], rotation=18, ha="right", fontsize=8)
    c.set_ylabel("VPN (MM COP)"); c.legend(fontsize=8, loc="upper left")
    c.set_title("TEA de Burk: VPN de los casos comparables (número: P(VPN > 0) del Monte Carlo)", fontsize=9)
    # D: tornado v9
    dd = ax[1, 1]; tor = out["tornado9"]
    base = json.load(open(f"{RES}/tea_dimensionado.json"))["cases"]["A · Óptimo con la superestructura ampliada"]["res"]["NPV"] / 1e6
    for i, t in enumerate(tor):
        lo, hi = sorted([t["NPV_worst"] / 1e6, t["NPV_best"] / 1e6])
        new = ("cáscara" in t["label"]) or ("Corona" in t["label"])
        dd.barh(i, hi - lo, left=lo, color=C[3] if new else C[0], height=0.6)
    dd.axvline(base, color=INK, lw=1); dd.set_yticks(range(len(tor))); dd.set_yticklabels([t["label"] for t in tor], fontsize=7.8); dd.invert_yaxis()
    dd.set_xlabel("VPN (MM COP)"); dd.set_title("Tornado del óptimo v9 (ámbar: incertidumbres nuevas de la v9)", fontsize=9)
    fig.suptitle("Fig. 39  Comparación entre las versiones 8 y 9 (Seguí y Fito 2018; Campos et al. 2020)", fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig39_comparativo_v8_v9.png")


if __name__ == "__main__" and "compare" in sys.argv[1:]:
    out = json.load(open(out_p))
    out.update(compare())
    out["variants"] = variants()
    out["brom_be"] = breakeven_bromelain()
    json.dump(out, open(out_p, "w"), default=float)
    figure(out)
