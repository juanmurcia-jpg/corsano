"""
Exporta un caso TEA a un libro Excel con la estructura de los TEA del usuario (asaí v5.19 / coco v12):
Inicio, Tablero, Modelo del proceso, Costos de Equipos, CapEx, OpEx & Ingresos, Flujo de Caja, Tornado,
Break-Even, Monte Carlo. Costos de equipos, CapEx, OpEx (incluida la nómina colombiana) y flujo de caja
quedan con fórmulas vivas que leen el Tablero; el modelo del proceso, el tornado y el Monte Carlo llevan
los valores calculados en Python.
"""
import math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
import tea_burk as tb

BLUE = Font(color="1F4E79"); BOLD = Font(bold=True); H1 = Font(bold=True, size=14)
INPUT = PatternFill("solid", fgColor="FFF2CC"); LINK = PatternFill("solid", fgColor="E2EFDA")
NUM = '#,##0'; PCT = '0.0%'


def _t(ws, cell, v, font=None, fill=None, fmt=None):
    ws[cell] = v
    if font: ws[cell].font = font
    if fill: ws[cell].fill = fill
    if fmt: ws[cell].number_format = fmt


def export(case, res, tor, mc, be, path, flows=None, note=""):
    c = tb.COMMON
    wb = Workbook()
    ws0 = wb.active; ws0.title = "Inicio"
    T = wb.create_sheet("Tablero"); MP = wb.create_sheet("Modelo del proceso"); CE = wb.create_sheet("Costos de Equipos")
    CX = wb.create_sheet("CapEx"); OX = wb.create_sheet("OpEx & Ingresos"); FC = wb.create_sheet("Flujo de Caja")
    TO = wb.create_sheet("Tornado"); BE = wb.create_sheet("Break-Even"); MC = wb.create_sheet("Monte Carlo")
    # ------------------------------------------------------------------ Tablero (entradas)
    _t(T, "A1", "Panel de Control", H1)
    _t(T, "B2", "Celdas amarillas: supuestos editables. Metodología Techno-Economic Modeling (Burk); CapEx según Sinnott & Towler (2022).")
    cal = res["calendar"]
    inputs = [
        ("Valor del producto principal", case["product"]["price"], f"COP/{case['product'].get('unit', 'u')}"),
        ("Producción anual del producto principal", case["product"]["qty_year"], case["product"].get("unit", "u")),
        ("Factor de producción (multiplicador)", 1.0, "-"),
        ("Fracción vendida", c["vendido"], "-"),
        ("Salario mínimo (SMMLV)", c["SMMLV"], "COP/mes"),
        ("Auxilio de transporte", c["aux_transporte"], "COP/mes"),
        ("Tasa de descuento (real)", c["tasa"], "/año"),
        ("Periodo de evaluación", c["anios"], "años"),
        ("Impuesto de renta (SAS, ET art. 240)", c["renta"], "-"),
        ("Factor de instalación Fi", c["Fi"], "x compra"),
        ("Asignación equipos no listados", c["no_listados"], "fracción"),
        ("Transporte y seguro", c["flete"], "x listados"),
        ("OSBL", c["OSBL"], "x ISBL"), ("Edificación e ingeniería civil", c["civil"], "x ISBL"),
        ("EPC", c["EPC"], "x directos"), ("Contingencia", c["contingencia"], "x directos"),
        ("Supervisión y gastos generales", c["supervision"], "x mano de obra"),
        ("Mantenimiento", c["mantenimiento"], "x capital fijo"), ("Impuestos locales, seguros, alquiler", c["impuestos_locales"], "x capital fijo"),
        ("Capital de trabajo", c["WC_meses"], "meses de OpEx"), ("Interés sobre capital de trabajo", c["interes_WC"], "/año"),
        ("TRM", c["TRM"], "COP/USD"), ("IPP año base (2026)", c["IPP_base"], "-"), ("IPP de las cotizaciones (2024)", c["IPP_2024"], "-"),
        ("Electricidad (ZNI, diésel)", c["elec_COP_kWh"], "COP/kWh"), ("Calor de proceso (GLP)", c["calor_COP_MJ"], "COP/MJ"),
        ("Agua de planta", c["agua_COP_t"], "COP/t"), ("Tratamiento de aguas residuales", c["ARD_COP_t"], "COP/t"),
        ("Días de producción al año", cal["days"], "días"), ("Turnos por día", cal["shifts"], "-"), ("Horas por turno", cal["h_shift"], "h"),
        ("Puestos por turno", case["positions"], "-"), ("Jornada legal semanal", c["jornada_h_sem"], "h"),
        ("Salario ingeniero de planta", c["ingeniero_mes"], "COP/mes"), ("Ingenieros de planta", case.get("engineer", 1), "-"),
        ("Inversión año 0", c["inv"][0], "fracción"), ("Inversión año 1", c["inv"][1], "fracción"), ("Tasa operativa año 1", c["tasa_op1"], "-"),
    ]
    ref = {}
    _t(T, "B4", "Parámetro", BOLD); _t(T, "C4", "Valor", BOLD); _t(T, "D4", "Unidad", BOLD)
    for q, (lab, v, u) in enumerate(inputs):
        r = 5 + q
        _t(T, f"B{r}", lab); _t(T, f"C{r}", v, fill=INPUT); _t(T, f"D{r}", u)
        ref[lab] = f"Tablero!$C${r}"
    R = lambda k: ref[k]
    T.column_dimensions["B"].width = 44; T.column_dimensions["C"].width = 18
    # ------------------------------------------------------------------ Modelo del proceso (valores)
    _t(MP, "A1", "Modelo del proceso — balance de masa (calculado en Python: planta_trl9.py / capacidad.py)", H1)
    r = 3
    for k, v in (flows or {}).items():
        _t(MP, f"B{r}", k); _t(MP, f"C{r}", float(v), fmt='#,##0.0'); r += 1
    if note:
        _t(MP, f"B{r + 1}", note)
    # ------------------------------------------------------------------ Costos de equipos
    _t(CE, "A1", "Estimación del costo del equipo (ley de potencias + IPP + Fi)", H1)
    hdr = ["Equipo", "Cantidad", "Tamaño", "Tamaño ref.", "Costo ref. (USD 2024)", "Exponente n", "Compra (COP año base)", "Instalado (COP)"]
    for q, h in enumerate(hdr):
        _t(CE, f"{L(2 + q)}4", h, BOLD)
    r0 = 5
    for q, e in enumerate(case["equipment"]):
        r = r0 + q
        _t(CE, f"B{r}", e["name"]); _t(CE, f"C{r}", e["qty"], fill=INPUT); _t(CE, f"D{r}", e["size"], fill=INPUT)
        _t(CE, f"E{r}", e["ref_size"], fill=INPUT); _t(CE, f"F{r}", e["ref_USD"], fill=INPUT, fmt=NUM); _t(CE, f"G{r}", e["n"], fill=INPUT)
        _t(CE, f"H{r}", f"=C{r}*F{r}*(D{r}/E{r})^G{r}*{R('TRM')}*{R('IPP año base (2026)')}/{R('IPP de las cotizaciones (2024)')}", fmt=NUM)
        _t(CE, f"I{r}", f"=H{r}*{R('Factor de instalación Fi')}", fmt=NUM)
    rl = r0 + len(case["equipment"]) - 1
    rs = rl + 2
    _t(CE, f"B{rs}", "Equipos listados (instalados)", BOLD); _t(CE, f"I{rs}", f"=SUM(I{r0}:I{rl})", fmt=NUM)
    _t(CE, f"B{rs+1}", "Asignación para equipos no listados"); _t(CE, f"I{rs+1}", f"=I{rs}*{R('Asignación equipos no listados')}/(1-{R('Asignación equipos no listados')})", fmt=NUM)
    _t(CE, f"B{rs+2}", "Transporte y seguro"); _t(CE, f"I{rs+2}", f"={R('Transporte y seguro')}*(I{rs}+I{rs+1})", fmt=NUM)
    _t(CE, f"B{rs+3}", "Total ISBL instalado", BOLD); _t(CE, f"I{rs+3}", f"=SUM(I{rs}:I{rs+2})", fmt=NUM)
    _t(CE, f"B{rs+4}", "Costo de compra total"); _t(CE, f"I{rs+4}", f"=SUM(H{r0}:H{rl})", fmt=NUM)
    ISBL = f"'Costos de Equipos'!$I${rs+3}"
    CE.column_dimensions["B"].width = 52
    for col in "HI":
        CE.column_dimensions[col].width = 18
    # ------------------------------------------------------------------ CapEx
    _t(CX, "A1", "Estimación de costos de capital (Sinnott & Towler 2022)", H1)
    rows = [("Equipo ISBL instalado", f"={ISBL}"), ("Gastos de OSBL", f"={R('OSBL')}*C5"),
            ("Edificación e ingeniería civil", f"={R('Edificación e ingeniería civil')}*C5"), ("Costos directos totales", "=SUM(C5:C7)"),
            ("Costos EPC", f"={R('EPC')}*C8"), ("Contingencia", f"={R('Contingencia')}*C8"), ("Inversión de capital fijo", "=C8+C9+C10"),
            ("Factor Lang equivalente (FCI / compra)", f"=C11/'Costos de Equipos'!I{rs+4}")]
    for q, (lab, f) in enumerate(rows):
        _t(CX, f"B{5+q}", lab, BOLD if lab.startswith("Inversión") else None); _t(CX, f"C{5+q}", f, fmt=NUM if q < 7 else '0.00')
    FCI = "CapEx!$C$11"
    CX.column_dimensions["B"].width = 42; CX.column_dimensions["C"].width = 20
    # ------------------------------------------------------------------ OpEx & Ingresos
    _t(OX, "A1", "Costos operativos e ingresos", H1)
    _t(OX, "B3", "Concepto", BOLD); _t(OX, "C3", "Cantidad/año", BOLD); _t(OX, "D3", "COP/unidad", BOLD); _t(OX, "E3", "COP/año", BOLD)
    r = 4
    _t(OX, f"B{r}", "INGRESOS", BOLD); r += 1
    rev_start = r
    _t(OX, f"B{r}", case["product"]["name"]); _t(OX, f"C{r}", f"={R('Producción anual del producto principal')}*{R('Factor de producción (multiplicador)')}*{R('Fracción vendida')}", fmt=NUM)
    _t(OX, f"D{r}", f"={R('Valor del producto principal')}", fmt=NUM); _t(OX, f"E{r}", f"=C{r}*D{r}", fmt=NUM); r += 1
    for bp in case.get("byproducts", []):
        _t(OX, f"B{r}", f"Subproducto: {bp['name']}"); _t(OX, f"C{r}", f"={bp['qty_year']}*{R('Factor de producción (multiplicador)')}*{R('Fracción vendida')}", fmt=NUM)
        _t(OX, f"D{r}", bp["price"], fill=INPUT, fmt=NUM); _t(OX, f"E{r}", f"=C{r}*D{r}", fmt=NUM); r += 1
    rev_end = r - 1
    _t(OX, f"B{r}", "Ingresos totales", BOLD); _t(OX, f"E{r}", f"=SUM(E{rev_start}:E{rev_end})", fmt=NUM); REV = f"'OpEx & Ingresos'!$E${r}"; r += 2
    _t(OX, f"B{r}", "COSTOS VARIABLES", BOLD); r += 1
    var_start = r
    for it in case["raw"]:
        _t(OX, f"B{r}", it["name"]); _t(OX, f"C{r}", f"={it['qty_year']}*{R('Factor de producción (multiplicador)')}", fmt=NUM)
        _t(OX, f"D{r}", it["price"], fill=INPUT, fmt=NUM); _t(OX, f"E{r}", f"=C{r}*D{r}", fmt=NUM); r += 1
    pk = {"elec_COP_kWh": "Electricidad (ZNI, diésel)", "calor_COP_MJ": "Calor de proceso (GLP)", "agua_COP_t": "Agua de planta"}
    for u in case["utilities"]:
        _t(OX, f"B{r}", u["name"]); _t(OX, f"C{r}", f"={u['qty_year']}*{R('Factor de producción (multiplicador)')}", fmt=NUM)
        _t(OX, f"D{r}", f"={R(pk[u['price_key']])}" if "price_key" in u else u["price"], fmt=NUM); _t(OX, f"E{r}", f"=C{r}*D{r}", fmt=NUM); r += 1
    for w in case.get("waste", []):
        _t(OX, f"B{r}", w["name"]); _t(OX, f"C{r}", f"={w['qty_year']}*{R('Factor de producción (multiplicador)')}", fmt=NUM)
        _t(OX, f"D{r}", f"={R('Tratamiento de aguas residuales')}", fmt=NUM); _t(OX, f"E{r}", f"=C{r}*D{r}", fmt=NUM); r += 1
    var_end = r - 1
    _t(OX, f"B{r}", "Costos variables totales", BOLD); _t(OX, f"E{r}", f"=SUM(E{var_start}:E{var_end})", fmt=NUM); VAR = f"'OpEx & Ingresos'!$E${r}"; r += 2
    # nómina (plantilla)
    _t(OX, f"B{r}", "NÓMINA (plantilla: prestaciones colombianas)", BOLD); r += 1
    _t(OX, f"B{r}", "Horas de operario al año"); _t(OX, f"E{r}", f"={R('Puestos por turno')}*{R('Días de producción al año')}*{R('Horas por turno')}*{R('Turnos por día')}", fmt=NUM); rh = r; r += 1
    _t(OX, f"B{r}", "Auxiliares de operación (personas)"); _t(OX, f"E{r}", f"=ROUNDUP(E{rh}/({R('Jornada legal semanal')}*52)-0.0000001,0)"); rn = r; r += 1
    def person(rowlabel, n_ref, sal_ref):
        nonlocal r
        _t(OX, f"B{r}", rowlabel)
        K = f"({n_ref}*{sal_ref}*12)"
        Lx = f"({K}+IF({sal_ref}<=2*{R('Salario mínimo (SMMLV)')},{R('Auxilio de transporte')}*12*{n_ref},0))"
        f = (f"={Lx}+{K}*{c['salud']}+{K}*{c['pension']}+{Lx}*{c['cesantias']}*(1+{c['int_cesantias']})+{Lx}*{c['prima']}"
             f"+{K}*{c['vacaciones']}+{K}*{c['ccf'] + c['icbf'] + c['sena']}+{K}*{c['arl']}")
        _t(OX, f"E{r}", f, fmt=NUM); rr = r; r += 1
        return rr
    ra = person("Costo de auxiliares", f"E{rn}", R("Salario mínimo (SMMLV)"))
    re_ = person("Costo de ingeniero(s) de planta", R("Ingenieros de planta"), R("Salario ingeniero de planta"))
    night = res["payroll"]["night"]
    _t(OX, f"B{r}", "Recargo nocturno (calculado)"); _t(OX, f"E{r}", night, fmt=NUM); rnt = r; r += 1
    _t(OX, f"B{r}", "Mano de obra", BOLD); _t(OX, f"E{r}", f"=E{ra}+E{re_}+E{rnt}", fmt=NUM); LAB = f"E{r}"; r += 1
    _t(OX, f"B{r}", "Supervisión y gastos generales"); _t(OX, f"E{r}", f"={R('Supervisión y gastos generales')}*{LAB}", fmt=NUM); SUP = f"E{r}"; r += 1
    _t(OX, f"B{r}", "Mantenimiento"); _t(OX, f"E{r}", f"={R('Mantenimiento')}*{FCI}", fmt=NUM); MAN = f"E{r}"; r += 1
    _t(OX, f"B{r}", "Impuestos locales, seguros y alquiler"); _t(OX, f"E{r}", f"={R('Impuestos locales, seguros, alquiler')}*{FCI}", fmt=NUM); TXL = f"E{r}"; r += 1
    _t(OX, f"B{r}", "Costos fijos (flujo de caja)", BOLD); _t(OX, f"E{r}", f"={LAB}+{SUP}+{MAN}+{TXL}", fmt=NUM); FIX = f"'OpEx & Ingresos'!$E${r}"; r += 1
    _t(OX, f"B{r}", "Capital de trabajo"); _t(OX, f"E{r}", f"={R('Capital de trabajo')}*({VAR}+{LAB}+{SUP}+{MAN}+{TXL})/12", fmt=NUM); WC = f"'OpEx & Ingresos'!$E${r}"; r += 1
    _t(OX, f"B{r}", "Interés sobre capital de trabajo (solo costo nivelado)"); _t(OX, f"E{r}", f"={R('Interés sobre capital de trabajo')}*{WC}", fmt=NUM); IWC = f"E{r}"; r += 1
    _t(OX, f"B{r}", "Factor de recuperación de capital"); _t(OX, f"E{r}", f"={R('Tasa de descuento (real)')}*(1+{R('Tasa de descuento (real)')})^{R('Periodo de evaluación')}/((1+{R('Tasa de descuento (real)')})^{R('Periodo de evaluación')}-1)", fmt='0.0000'); CRF = f"E{r}"; r += 1
    _t(OX, f"B{r}", "Costo nivelado de producción (neto de subproductos)", BOLD)
    bpsum = f"-SUM(E{rev_start+1}:E{rev_end})" if rev_end > rev_start else ""
    _t(OX, f"E{r}", f"=({CRF}*{FCI}+{VAR}+{FIX}+{IWC}{bpsum})/C{rev_start}", fmt=NUM); LCOP = f"'OpEx & Ingresos'!$E${r}"
    OX.column_dimensions["B"].width = 50; OX.column_dimensions["E"].width = 20
    # ------------------------------------------------------------------ Flujo de caja (fórmulas de la plantilla)
    _t(FC, "A1", "Análisis de flujo de efectivo", H1)
    N = c["anios"]
    _t(FC, "B4", "Año", BOLD)
    labels = {5: "Inversión de capital fijo", 6: "Tasa operativa", 7: "Costos fijos", 8: "Costos variables", 9: "Ingresos",
              10: "Ganancia bruta", 11: "Depreciación (línea recta 10 %, ET art. 137)", 12: "Renta líquida gravable",
              13: "Impuesto pagado (rezago de un año)", 14: "Ganancia neta", 15: "Pérdida fiscal acumulada (ET art. 147)",
              16: "Flujo de caja", 17: "Flujo de caja descontado", 18: "Flujo acumulado", 19: "Flujo descontado acumulado"}
    for rr, lab in labels.items():
        _t(FC, f"B{rr}", lab)
    for t in range(N + 1):
        col = L(3 + t); prev = L(2 + t)
        _t(FC, f"{col}4", t, BOLD)
        invf = R("Inversión año 0") if t == 0 else (R("Inversión año 1") if t == 1 else "0")
        _t(FC, f"{col}5", f"={invf}*{FCI}", fmt=NUM)
        _t(FC, f"{col}6", 0 if t == 0 else (f"={R('Tasa operativa año 1')}" if t == 1 else 1))
        _t(FC, f"{col}7", f"=IF({col}6=0,0,{FIX})", fmt=NUM)
        _t(FC, f"{col}8", f"={col}6*{VAR}", fmt=NUM)
        _t(FC, f"{col}9", f"={col}6*{REV}", fmt=NUM)
        _t(FC, f"{col}10", f"={col}9-{col}7-{col}8", fmt=NUM)
        _t(FC, f"{col}11", 0 if t == 0 else f"={FCI}*0.1", fmt=NUM)
        pool_prev = "0" if t == 0 else f"{prev}15"
        _t(FC, f"{col}12", f"=MAX({col}10-{col}11-MIN({pool_prev},MAX({col}10-{col}11,0)),0)", fmt=NUM)
        if t == 0:
            _t(FC, f"{col}13", 0)
        elif t < N:
            _t(FC, f"{col}13", f"={prev}12*{R('Impuesto de renta (SAS, ET art. 240)')}", fmt=NUM)
        else:
            _t(FC, f"{col}13", f"=({prev}12+{col}12)*{R('Impuesto de renta (SAS, ET art. 240)')}", fmt=NUM)
        _t(FC, f"{col}14", f"={col}10-{col}13", fmt=NUM)
        _t(FC, f"{col}15", f"={pool_prev}-MIN({pool_prev},MAX({col}10-{col}11,0))+MAX({col}11-{col}10,0)", fmt=NUM)
        wc = "" if t not in (1, N) else (f"-{WC}" if t == 1 else f"+{WC}")
        _t(FC, f"{col}16", f"={col}14-{col}5{wc}", fmt=NUM)
        _t(FC, f"{col}17", f"={col}16/(1+{R('Tasa de descuento (real)')})^{col}4", fmt=NUM)
        _t(FC, f"{col}18", f"=SUM($C$16:{col}16)", fmt=NUM)
        _t(FC, f"{col}19", f"=SUM($C$17:{col}17)", fmt=NUM)
    last = L(3 + N)
    _t(FC, "B22", "Valor Presente Neto (COP)", BOLD); _t(FC, "C22", f"=SUM(C17:{last}17)", fmt=NUM)
    _t(FC, "B23", "TIR modificada (MIRR)", BOLD); _t(FC, "C23", f"=MIRR(C16:{last}16,{R('Tasa de descuento (real)')},{R('Tasa de descuento (real)')})", fmt=PCT)
    _t(FC, "B24", "Costo nivelado (COP/unidad)", BOLD); _t(FC, "C24", f"={LCOP}", fmt=NUM)
    FC.column_dimensions["B"].width = 44
    # ------------------------------------------------------------------ Tornado / Break-even / MC (valores de Python)
    _t(TO, "A1", "Tornado — VPN (COP) al variar cada parámetro entre peor y mejor caso", H1)
    for q, h in enumerate(["Parámetro", "Peor", "Base", "Mejor", "VPN peor", "VPN mejor", "Rango"]):
        _t(TO, f"{L(2 + q)}3", h, BOLD)
    for q, rr in enumerate(tor):
        for qq, v in enumerate([rr["label"], rr["worst"], rr["base"], rr["best"], rr["NPV_worst"], rr["NPV_best"], rr["range"]]):
            _t(TO, f"{L(2 + qq)}{4 + q}", v, fmt=NUM if qq >= 4 else None)
    _t(BE, "A1", "Punto de equilibrio del precio del producto", H1)
    _t(BE, "B3", "Precio actual"); _t(BE, "C3", f"={R('Valor del producto principal')}", fmt=NUM)
    _t(BE, "B4", "Costo nivelado (PE contable)"); _t(BE, "C4", f"={LCOP}", fmt=NUM)
    _t(BE, "B5", "Precio de equilibrio VPN = 0 (bisección en Python)"); _t(BE, "C5", be if be == be else "n/d", fmt=NUM)
    _t(MC, "A1", "Monte Carlo — hipercubo latino, Beta-PERT λ = 4, correlación de rangos Iman–Conover (ρ precio–MP = 0,45)", H1)
    for q, (lab, v) in enumerate([("Iteraciones", len(mc["NPV"])), ("P(VPN > 0)", mc["P_pos"]), ("VPN P5", mc["P5"]),
                                  ("VPN P50", mc["P50"]), ("VPN P95", mc["P95"]), ("CVaR 5 % del VPN", mc["CVaR5"])]):
        _t(MC, f"B{3+q}", lab); _t(MC, f"C{3+q}", v, fmt=PCT if "P(" in lab else NUM)
    _t(MC, "E2", "VPN por iteración", BOLD)
    for q, v in enumerate(mc["NPV"]):
        MC[f"E{3+q}"] = float(v)
    # ------------------------------------------------------------------ Inicio
    _t(ws0, "B2", f"Modelo Tecno-Económico — {case['name']}", H1)
    _t(ws0, "B3", "Biorrefinería de piña, Bajo Atrato (Chocó) · diseño TRL-9 · COP de 2026")
    _t(ws0, "B5", "Valor Presente Neto (COP)"); _t(ws0, "C5", "='Flujo de Caja'!C22", fmt=NUM)
    _t(ws0, "B6", "MIRR"); _t(ws0, "C6", "='Flujo de Caja'!C23", fmt=PCT)
    _t(ws0, "B7", "Inversión de capital fijo (COP)"); _t(ws0, "C7", f"={FCI}", fmt=NUM)
    _t(ws0, "B8", "Costo nivelado (COP/unidad)"); _t(ws0, "C8", f"={LCOP}", fmt=NUM)
    _t(ws0, "B9", "Precio de venta (COP/unidad)"); _t(ws0, "C9", f"={R('Valor del producto principal')}", fmt=NUM)
    _t(ws0, "B10", "P(VPN > 0), Monte Carlo"); _t(ws0, "C10", mc["P_pos"], fmt=PCT)
    _t(ws0, "B12", "Metodología: Techno-Economic Modeling (Burk) · CapEx según Sinnott & Towler (2022) · estructura de los TEA de asaí v5.19 y coco v12.")
    _t(ws0, "B13", "Supuestos [S] (costos de referencia de equipos, precios) deben reemplazarse por cotizaciones locales.")
    ws0.column_dimensions["B"].width = 40; ws0.column_dimensions["C"].width = 22
    wb.save(path)
    return path
