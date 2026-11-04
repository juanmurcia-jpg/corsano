"""Genera los libros TEA (estructura Burk de la plantilla del usuario) y verifica las fórmulas con LibreOffice."""
import json, os, subprocess, re, glob, shutil
import numpy as np
import openpyxl
import tea_burk as tb, tea_lineas as tl, planta_trl9 as pt, capacidad as cp, excel_export as xe
import params as p

OUT = os.path.join(os.path.dirname(__file__), "TEA_excel"); os.makedirs(OUT, exist_ok=True)
RES = os.path.join(os.path.dirname(__file__), "results")


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:60]


def make(case, flows, tag, note=""):
    r = tb.evaluate(case)
    be = tb.breakeven_price(case) if case["product"]["price"] > 1 else float("nan")
    _, tor = tb.tornado(case, tl.tornado_specs(case))
    mc = tb.monte_carlo(case, tl.mc_dists(case), tl.MC_R, n=500)
    path = os.path.join(OUT, f"TEA_{slug(tag)}_{slug(case['name'])}.xlsx")
    xe.export(case, r, tor, mc, be, path, flows=flows, note=note)
    return path, r


def recalc_check(paths_results):
    tmp = os.path.join(OUT, "_recalc"); os.makedirs(tmp, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", tmp] + [p_ for p_, _ in paths_results],
                   capture_output=True, timeout=600)
    rows = []
    for path, r in paths_results:
        f = os.path.join(tmp, os.path.basename(path))
        wb = openpyxl.load_workbook(f, data_only=True)
        npv_x = wb["Flujo de Caja"]["C22"].value; mirr_x = wb["Flujo de Caja"]["C23"].value; fci_x = wb["CapEx"]["C11"].value
        lcop_x = wb["Flujo de Caja"]["C24"].value
        rows.append(dict(file=os.path.basename(path), NPV_py=r["NPV"], NPV_xl=npv_x, FCI_py=r["FCI"], FCI_xl=fci_x,
                         MIRR_py=r["MIRR"], MIRR_xl=mirr_x, LCOP_py=r["LCOP"], LCOP_xl=lcop_x,
                         dNPV_rel=(abs(npv_x - r["NPV"]) / max(abs(r["NPV"]), 1)) if isinstance(npv_x, (int, float)) else None))
    shutil.rmtree(tmp, ignore_errors=True)
    return rows


if __name__ == "__main__":
    made = []
    fruit = cp.fruit_for_wine(p.WINE_VOL_YR)[0]
    D = pt.design(fruit); cs = tl.cases_from_design(D)
    keys_int = ["L1 Vino de piña (rápido, 30 °C)", "L3 Vinagre (acetador sumergido)", "L4 Bromelaína + polvo nutracéutico",
                "L5 Harina de fibra de cáscara", "L6 Etanol hidratado (jugo de cáscara)", "L7b Caldera de biomasa (TRL 9)"]
    cs["Planta integrada TRL-9"] = tl.integrated_case(cs, keys_int)
    lk = {"L1": "vino", "L2": "vino", "L3": "vinagre", "L4": "bromelaina", "L5": "harina", "L6": "etanol", "L7a": "energia"}
    for k, c in cs.items():
        flows = D["lines"].get(lk.get(k.split()[0], ""), {}).get("flows", D["balance"] if k.startswith("Planta") else {})
        made.append(make(c, flows, "Base_tesis_21856t", note=f"Diseño TRL-9 a {fruit:,.0f} t/año de fruta (base de la tesis)."))
    # planes recomendados con la producción actual (Chocó 2022)
    import copy
    D2 = pt.design(6200.0); cs2 = tl.cases_from_design(D2)
    h = copy.deepcopy(cs2["L5 Harina de fibra de cáscara"])
    for rr in h["raw"]:
        if rr.get("main"):
            rr["price"] = tl.M("corona_kg")
    h["name"] = "Plan Choco 2022 - harina con residuos de procesador"
    made.append(make(h, D2["lines"]["harina"]["flows"], "Choco2022", note="Residuos a 80 COP/kg (recolección)."))
    I = tl.integrated_case(cs2, ["L1 Vino de piña (rápido, 30 °C)", "L5 Harina de fibra de cáscara"], name="Plan Choco 2022 - vino + harina (vino 3 000 COP/L)")
    for bp in I["byproducts"]:
        if bp["name"] == "L1 Vino de piña":
            bp["price"] = 3000.0
    made.append(make(I, D2["balance"], "Choco2022", note="Fruta de rechazo a 400 COP/kg; vino a granel a 3 000 COP/L."))
    chk = recalc_check(made)
    for c in chk:
        print(c["file"], "VPN py", round(c["NPV_py"] / 1e6, 1), "xl", None if c["NPV_xl"] is None else round(c["NPV_xl"] / 1e6, 1), "dRel", c["dNPV_rel"])
    json.dump(chk, open(f"{RES}/tea_excel_check.json", "w"), default=float)
