"""
v13: TEA de los diseños de revisor_v13.py, frontera de demanda mínima viable y figuras 48–49.

  python revisor_v13_post.py            -> results/v13/resumen.json, figs/fig48_h1_h4.png, figs/fig49_h2_h3.png
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import dimensionamiento as dm
import tea_burk as tb
import tea_dimensionado as td
from figuras import C, INK, INK2, save

OUT = os.path.join(dm.RES, "v13")
L = lambda g: json.load(open(os.path.join(OUT, f"{g}.json"))) if os.path.exists(os.path.join(OUT, f"{g}.json")) else {}


def tea(full, label, mc=False):
    """VPN, TIRM y FCI del diseño con el TEA de Burk (tea_dimensionado); con mc=True también P(VPN>0)."""
    if not full or not full.get("scen") or full["scen"][0]["products"].get("fruta_t", 0.0) < 1:
        return None                          # sin fruta procesada: el TEA por líneas no aplica (se reporta el margen)
    c = td.build_case(full, label, False)
    if mc:
        r = td.run(c, mc_n=500)
        return dict(NPV=r["res"]["NPV"] / 1e6, MIRR=r["res"]["MIRR"], FCI=r["res"]["FCI"] / 1e6, P_pos=r["mc"]["P_pos"], breakeven=r["breakeven"])
    r = tb.evaluate(c)
    return dict(NPV=r["NPV"] / 1e6, MIRR=r["MIRR"], FCI=r["FCI"] / 1e6)


def summary():
    h1, h4, h2, h3 = L("H1"), dict(L("H4a"), **L("H4b")), L("H2"), L("H3")
    h4.update({k: v for k, v in L("H4p").items() if not k.startswith("_")})     # malla pulida (monótona)
    for i in range(3):                                                           # pulido con todos los diseños hallados
        h4.update({k: v for k, v in L(f"H4q{i}").items() if not k.startswith("_")})
    h3 = L("H3b") or h3                                                          # frente con la contabilidad corregida (v13)
    if L("H2p").get("sweep"):
        h2["sweep"] = L("H2p")["sweep"]                                          # barrido de autonomía pulido
    h1b = L("H1c") or L("H1b")                                                  # H1c: óptimo estacional repetido con mejor arranque
    S = dict(H1={}, H4={}, H2={}, H3={})
    d12 = json.load(open(os.path.join(dm.RES, "dimensionamiento.json")))["E1|Óptimo económico"]
    dm.HP_ON = False
    S["H1"]["optimo"] = dict(margin=d12["scen"][0]["margin"], tea=tea(d12, "Óptimo v12", mc=True), sizes=d12["sizes"])
    for k in ("promedio", "secuencial", "secuencial_promedio"):
        if k in h1 and h1[k]["evaluado"].get("full"):
            e = h1[k]["evaluado"]
            dis = h1[k].get("diseno", {})
            S["H1"][k] = dict(margin=e["margin"], esperado=dis.get("margin"), sizes=e["sizes"], products=e["products"],
                              tea=tea(e["full"], f"Línea base {k}", mc=True), etapas=h1[k].get("etapas"))
            print("H1", k, round(e["margin"]), S["H1"][k]["tea"], flush=True)
    S["H1"]["escala"] = {}
    for k, v in h1b.items():
        if k.startswith("_"):
            continue
        S["H1"]["escala"][k] = dict(estacional=v["estacional"].get("obj"), promedio_diseno=v["promedio_diseno"].get("obj"),
                                    promedio_evaluado=v["promedio_evaluado"].get("obj"),
                                    sizes_estacional=v["estacional"].get("sizes"), sizes_promedio=v["promedio_diseno"].get("sizes"))
    for key, r in h4.items():
        if key.startswith("_") or not r.get("full"):
            continue
        b, v = key.split("|")
        t = tea(r["full"], f"Mercado {b} botellas, {v} m³")
        S["H4"][key] = dict(bottles=int(b), vinegar=float(v), margin=r["margin"], NPV=t["NPV"] if t else None,
                            fruit=r["products"]["fruta_t"], leaves=r["products"]["hojas_t"])
    print("H4", len(S["H4"]), "puntos", flush=True)
    dm.HP_ON = True
    if h2.get("optimo_v13", {}).get("full"):
        o = h2["optimo_v13"]
        S["H2"]["optimo"] = dict(margin=o["margin"], sizes=o["sizes"], products=o["products"], tea=tea(o["full"], "Óptimo v13", mc=True))
        S["H2"]["sweep"] = [dict(frac=s["frac"], fossil_max=s["fossil_max"], status=s.get("status"),
                                 margin=s.get("margin"), products=s.get("products"), sizes=s.get("sizes")) for s in h2.get("sweep", [])]
    if h3:
        S["H3"]["extremos"] = {k: dict(margin=v["margin"], products=v["products"], sizes=v["sizes"]) for k, v in h3.get("extremos", {}).items()}
        S["H3"]["frente"] = [dict(margin=p["margin"], gwp_neto=p["products"]["gwp_neto_kg"], sizes=p["sizes"]) for p in h3.get("frente", [])]
        S["H3"]["mcda"] = []
        for p in h3.get("mcda", []):
            S["H3"]["mcda"].append(dict(w=p["w"], margin=p["margin"], gwp_neto=p["products"]["gwp_neto_kg"], sizes=p["sizes"],
                                        products=p["products"], tea=tea(p.get("full"), f"Compromiso w={p['w']}")))
    json.dump(S, open(os.path.join(OUT, "resumen.json"), "w"), default=float, indent=1)
    return S


def fig48(S):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    labs = [("secuencial_promedio", "Secuencial por fracciones\ncon flujos promedio"), ("promedio", "Simultáneo con\nflujos promedio"),
            ("secuencial", "Secuencial por fracciones\ncon estacionalidad"), ("optimo", "Simultáneo con\nestacionalidad (óptimo)")]
    labs = [(k, t) for k, t in labs if k in S["H1"]]
    x = np.arange(len(labs))
    mg = [S["H1"][k]["margin"] for k, _ in labs]
    npv = [S["H1"][k]["tea"]["NPV"] if S["H1"][k].get("tea") else np.nan for k, _ in labs]
    w = 0.38
    b1 = ax[0].bar(x - w / 2, mg, w, color=C[0], label="Margen anual del MILP (MM COP/año)")
    b2 = ax[0].bar(x + w / 2, npv, w, color=C[2], label="VPN al 10 % (MM COP)")
    for bars in (b1, b2):
        for r_ in bars:
            h = r_.get_height()
            if np.isfinite(h):
                ax[0].annotate(f"{h:,.0f}".replace(",", " "), (r_.get_x() + r_.get_width() / 2, h), ha="center",
                               va="bottom" if h >= 0 else "top", fontsize=7.5)
    for i, (k, _) in enumerate(labs):
        e = S["H1"][k].get("esperado")
        if e is not None:
            ax[0].plot([i - w], [e], marker="_", ms=14, color=INK2)
    ax[0].axhline(0, color=INK2, lw=0.8)
    ax[0].set_ylim(top=1.3 * max(np.nanmax(mg), np.nanmax(npv)))
    ax[0].set_xticks(x); ax[0].set_xticklabels([t for _, t in labs], fontsize=8)
    ax[0].set_title("H1: la misma superestructura diseñada de cuatro maneras", fontsize=9)
    ax[0].legend(fontsize=7.5, loc="upper left")
    # H4: margen y VPN en la malla de demanda
    pts = S["H4"]
    B = sorted({p["bottles"] for p in pts.values()}); Vv = sorted({p["vinegar"] for p in pts.values()})
    Z = np.full((len(Vv), len(B)), np.nan)
    for p in pts.values():
        Z[Vv.index(p["vinegar"]), B.index(p["bottles"])] = p["margin"]
    if np.isfinite(Z).any():
        im = ax[1].imshow(Z, origin="lower", cmap="RdYlGn", aspect="auto", vmin=-np.nanmax(np.abs(Z)), vmax=np.nanmax(np.abs(Z)))
        for i in range(len(Vv)):
            for j in range(len(B)):
                if np.isfinite(Z[i, j]):
                    ax[1].text(j, i, f"{Z[i, j]:,.0f}".replace(",", " "), ha="center", va="center", fontsize=7.5)
        try:
            ax[1].contour(Z, levels=[0.0], colors=INK, linewidths=1.6)
        except Exception:
            pass
        ax[1].set_xticks(range(len(B))); ax[1].set_xticklabels([f"{b / 1000:,.0f} mil".replace(",", " ") for b in B], fontsize=8)
        ax[1].set_yticks(range(len(Vv))); ax[1].set_yticklabels([f"{v:,.0f}".replace(",", " ") for v in Vv], fontsize=8)
        ax[1].set_xlabel("Demanda de vino embotellado (botellas/año)"); ax[1].set_ylabel("Demanda de vinagre al 5 % (m³/año)")
        cb = fig.colorbar(im, ax=ax[1]); cb.set_label("Margen anual del óptimo (MM COP/año)")
        ax[1].set_title("H4: margen del óptimo por par de mercados (línea: margen = 0)", fontsize=9)
    fig.suptitle("Fig. 48  Valor del diseño simultáneo con la superestructura fija (H1) y frontera de demanda mínima viable (H4)",
                 fontsize=10.5, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig48_h1_h4.png")


def fig49(S):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    sw = [s for s in S["H2"].get("sweep", [])]
    o = S["H2"].get("optimo")
    if o:
        xs = [1.0] + [s["frac"] for s in sw if s.get("margin") is not None]
        ys = [o["margin"]] + [s["margin"] for s in sw if s.get("margin") is not None]
        ax[0].plot([100 * x_ for x_ in xs], ys, "o-", color=C[0])
        for x_, y_, s in zip(xs, ys, [o] + [s for s in sw if s.get("margin") is not None]):
            hp = s["sizes"].get("Bomba de calor", "no") if s.get("sizes") else "no"
            ax[0].annotate(f"BC {hp}", (100 * x_, y_), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7)
        for s in sw:
            if s.get("margin") is None:
                ax[0].plot([100 * s["frac"]], [min(ys) if ys else 0], "x", color=C[7], ms=9)
                ax[0].annotate("infactible", (100 * s["frac"], min(ys) if ys else 0), textcoords="offset points", xytext=(0, -12),
                               ha="center", fontsize=7, color=C[7])
        ax[0].invert_xaxis()
        ax[0].set_xlabel("Tope de energía fósil (% del óptimo sin tope: diésel + GLP)")
        ax[0].set_ylabel("Margen anual (MM COP/año)")
        ax[0].set_title("H2: costo de la autonomía energética (BC = bomba de calor elegida)", fontsize=9)
    fr = S["H3"].get("frente", []); ex = S["H3"].get("extremos", {})
    pts = ([ex["economico"]] if "economico" in ex else []) + [dict(margin=p["margin"], products=dict(gwp_neto_kg=p["gwp_neto"])) for p in fr] \
        + ([ex["ambiental"]] if "ambiental" in ex else [])
    if pts:
        pts = pts + [dict(margin=p["margin"], products=dict(gwp_neto_kg=p["gwp_neto"])) for p in S["H3"].get("mcda", [])]
        pts = [p for p in pts if not any(q["products"]["gwp_neto_kg"] <= p["products"]["gwp_neto_kg"] + 1 and q["margin"] > p["margin"] + 1
                                         for q in pts)]                    # solo puntos no dominados
        g = [p["products"]["gwp_neto_kg"] / 1000 for p in pts]; mgs = [p["margin"] for p in pts]
        order = np.argsort(g)
        ax[1].plot(np.array(g)[order], np.array(mgs)[order], "o-", color=C[0], label="Frente por ε-restricción")
        for p in S["H3"].get("mcda", []):
            ax[1].plot([p["gwp_neto"] / 1000], [p["margin"]], "D", ms=8, color=C[1])
            ax[1].annotate(f"compromiso w = {p['w']:.2f}", (p["gwp_neto"] / 1000, p["margin"]), textcoords="offset points", xytext=(6, -10),
                           fontsize=7, color=C[1])
        ax[1].axvline(0, color=INK2, lw=0.8, ls=":")
        ax[1].set_xlabel("Huella neta frente a la línea base sin planta (t CO₂e/año)")
        ax[1].set_ylabel("Margen anual (MM COP/año)")
        ax[1].set_title("H3: frente margen–huella neta y diseños de compromiso (Kenkel et al. 2022)", fontsize=9)
        ax[1].legend(fontsize=7.5)
    fig.suptitle("Fig. 49  Autonomía energética con bomba de calor (H2) y frente margen–huella neta (H3)",
                 fontsize=10.5, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig49_h2_h3.png")


if __name__ == "__main__":
    import sys
    S = json.load(open(os.path.join(OUT, "resumen.json"))) if "fig" in sys.argv[1:] else summary()
    fig48(S)
    fig49(S)
