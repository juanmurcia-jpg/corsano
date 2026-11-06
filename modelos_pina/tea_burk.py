"""
Motor TEA según la metodología de Burk (Techno-Economic Modeling) tal como la implementan los TEA del usuario
(TEA_Asai_v5.19_corregido.xlsm y TEA_Preliminar_Agua_de_coco_v12.xlsm):

  Modelo del proceso -> Dimensionamiento -> Costos de equipos (ley de potencia + IPP + Fi + no listados + flete)
  -> CapEx (Sinnott & Towler 2022: OSBL 0,23 y obra civil 0,15 sobre ISBL; EPC 0,30 y contingencia 0,20 sobre
  costos directos) -> OpEx & Ingresos (variables; fijos: nómina colombiana con prestaciones, supervisión 0,6×MO,
  mantenimiento 5 % FCI, impuestos/seguros 3 % FCI, capital de trabajo = 1 mes) -> Flujo de caja (10 años,
  inversión 30/70, año 1 al 50 %, depreciación lineal 10 % ET art. 137, renta 35 % SAS o 20 % ESAL, impuesto con
  un año de rezago, arrastre de pérdidas, capital de trabajo recuperado en el año 10, 95 % vendido) -> VPN, MIRR,
  recuperación simple y descontada, costo nivelado, precio de equilibrio -> Tornado -> Monte Carlo (LHS,
  Beta-PERT λ = 4, correlación de rangos de Iman–Conover).
"""
import math
import numpy as np
from scipy import stats

# ----------------------------------------------------------------------------- parámetros comunes (plantilla)
COMMON = dict(
    SMMLV=1_750_905.0, aux_transporte=249_095.0, jornada_h_sem=42.0,
    salud=0.085, pension=0.12, cesantias=0.0833, int_cesantias=0.12, prima=0.0833, vacaciones=0.0417,
    ccf=0.04, icbf=0.0, sena=0.0, arl=0.02436, recargo_nocturno=0.35, horas_nocturnas_2t=3.0,
    ingeniero_mes=3_500_000.0,
    Fi=1.3, no_listados=0.10, flete=0.05, OSBL=0.23, civil=0.15, EPC=0.30, contingencia=0.20,
    supervision=0.6, mantenimiento=0.05, impuestos_locales=0.03, WC_meses=1.0, interes_WC=0.10,
    tasa=0.10, anios=10, renta=0.35, tope_perdidas=1.0, vendido=0.95, inv=(0.3, 0.7), tasa_op1=0.5,
    IPP_base=182.84, IPP_2024=172.0, TRM=4000.0,     # IPP 2026 de la plantilla; IPP 2024 y TRM [S]
    agua_COP_t=28_000.0, ARD_COP_t=1_620.98,
    elec_COP_kWh=1_400.0,          # ZNI, generación diésel [S] (la plantilla de asaí usa 1 029 COP/kWh de red)
    calor_COP_MJ=159.0,            # GLP en caldera al 85 % (2 812,5 COP/lb de la plantilla) [derivado]
)


def calendar(scen, c=COMMON, factor=0.9):
    """Escenarios de la plantilla: 1 = todos los días 1 turno | 2 = lun–sáb 1 turno | 3 = lun–sáb 2 turnos.
    'continuo' = 24/7 con 3 turnos (procesos biológicos). Un dict se usa tal cual (p. ej. lun–sáb con 3 turnos)."""
    if isinstance(scen, dict):
        return dict(scen)
    if scen == "continuo":
        return dict(days=365.25 * factor, shifts=3, h_shift=8.0, h_op=8.0)
    days = (365.25 if scen == 1 else 365.25 - 365.25 / 7 - 18) * factor
    return dict(days=days, shifts=2 if scen == 3 else 1, h_shift=8.0, h_op=6.0)


# ----------------------------------------------------------------------------- equipos y CapEx
def equipment_cost(eq, c=COMMON):
    """eq: dict(name, qty, size, ref_size, ref_USD, n, quoted_installed=False, ipp_ref=IPP_2024).
    Costo en COP del año base: qty · ref · (S/S0)^n · TRM · IPP_base/IPP_ref."""
    scale = (eq["size"] / eq["ref_size"]) ** eq["n"] if eq.get("ref_size") else 1.0
    purchase = eq["qty"] * eq["ref_USD"] * scale * c["TRM"] * c["IPP_base"] / eq.get("ipp_ref", c["IPP_2024"])
    installed = purchase * (1.0 if eq.get("quoted_installed") else c["Fi"])
    return purchase, installed


def capex(equipment, c=COMMON):
    rows = []
    listed, exworks = 0.0, 0.0
    for e in equipment:
        pur, ins = equipment_cost(e, c)
        rows.append(dict(e, purchase_COP=pur, installed_COP=ins))
        listed += ins
        if not e.get("quoted_installed"):
            exworks += ins
    unlisted = listed * c["no_listados"] / (1 - c["no_listados"])
    freight = c["flete"] * (exworks + unlisted)
    ISBL = listed + unlisted + freight
    OSBL = c["OSBL"] * ISBL; civil = c["civil"] * ISBL
    direct = ISBL + OSBL + civil
    EPC = c["EPC"] * direct; cont = c["contingencia"] * direct
    FCI = direct + EPC + cont
    purchase_total = sum(r["purchase_COP"] for r in rows)
    return dict(rows=rows, listed=listed, unlisted=unlisted, freight=freight, ISBL=ISBL, OSBL=OSBL, civil=civil,
                direct=direct, EPC=EPC, contingency=cont, FCI=FCI, purchase=purchase_total,
                lang_equivalent=FCI / purchase_total if purchase_total else np.nan)


# ----------------------------------------------------------------------------- nómina colombiana (plantilla)
def payroll(positions_per_shift, cal, c=COMMON, engineer=1, salary=None):
    salary = salary or c["SMMLV"]
    hours = positions_per_shift * cal["days"] * cal["h_shift"] * cal["shifts"]
    fte = hours / (c["jornada_h_sem"] * 52)
    n = math.ceil(fte - 1e-9)
    def person_cost(n_, sal):
        K = n_ * sal * 12
        L = K + (c["aux_transporte"] * 12 * n_ if sal <= 2 * c["SMMLV"] else 0)
        ces = L * c["cesantias"]
        return (L + K * c["salud"] + K * c["pension"] + ces + ces * c["int_cesantias"] + L * c["prima"]
                + K * c["vacaciones"] + K * (c["ccf"] + c["icbf"] + c["sena"]) + K * c["arl"])
    aux = person_cost(n, salary)
    eng = person_cost(engineer, c["ingeniero_mes"]) if engineer else 0.0
    night = 0.0
    if cal["shifts"] >= 2:
        hourly = salary / (c["jornada_h_sem"] * 52 / 12)
        night = (n / cal["shifts"]) * hourly * c["recargo_nocturno"] * c["horas_nocturnas_2t"] * cal["days"]
        if cal["shifts"] >= 3:
            night *= 8.0 / c["horas_nocturnas_2t"] / 2 + 1   # turno nocturno completo [S]
    return dict(positions=positions_per_shift, fte=fte, workers=n, aux_cost=aux, eng_cost=eng, night=night,
                total=aux + eng + night)


# ----------------------------------------------------------------------------- caso TEA
def evaluate(case, c=COMMON, overrides=None):
    """case: dict con product(name, unit, qty_year, price), raw(list), utilities(list), waste(list), equipment,
    positions, calendar, byproducts(list opcional). overrides: {'price':x, 'raw_scale':x, ...}."""
    ov = overrides or {}
    c = dict(c, **{k: v for k, v in ov.items() if k in c})
    cal = calendar(case["calendar"])
    f_prod = ov.get("f_prod", 1.0)
    cap = capex(case["equipment"], c)
    FCI = cap["FCI"] * ov.get("capex_scale", 1.0)
    qty = case["product"]["qty_year"] * f_prod
    sold = qty * c["vendido"]
    price = ov.get("price", case["product"]["price"])
    revenue_main = price * sold
    rev_bp = 0.0
    for bp in case.get("byproducts", []):
        rev_bp += bp["qty_year"] * ov.get("bp_qty_" + bp["name"], 1.0) * f_prod * c["vendido"] * ov.get("bp_price_" + bp["name"], bp["price"])
    revenue = revenue_main + rev_bp
    raw = sum(r["qty_year"] * f_prod * ov.get("raw_price_" + r.get("key", ""), r["price"]) * (ov.get("raw_scale", 1.0) if r.get("main") else 1.0)
              for r in case["raw"])   # v10: raw_price_<key> cambia el precio de un insumo con clave (tornado y Monte Carlo)
    # v9: si solo llega a planta una fracción de la corona (crown_avail), el calor que no da la caldera se compra
    util = sum((u["qty_year"] + (1 - ov.get("crown_avail", 1.0)) * u.get("crown_MJ", 0.0)) * f_prod
               * (c[u["price_key"]] if "price_key" in u else u["price"]) for u in case["utilities"])
    waste = sum(w["qty_year"] * f_prod * w["price"] for w in case.get("waste", []))
    var = raw + util + waste
    pay = payroll(case["positions"], cal, c, engineer=case.get("engineer", 1))
    labor = pay["total"]
    sup = c["supervision"] * labor
    maint = c["mantenimiento"] * FCI
    taxes_loc = c["impuestos_locales"] * FCI
    WC = c["WC_meses"] * (var + labor + sup + maint + taxes_loc) / 12
    int_WC = c["interes_WC"] * WC
    fixed = labor + sup + maint + taxes_loc                    # el flujo excluye el interés del capital de trabajo
    crf = c["tasa"] * (1 + c["tasa"]) ** c["anios"] / ((1 + c["tasa"]) ** c["anios"] - 1)
    LCOP = (crf * FCI + var + fixed + int_WC - rev_bp) / sold if sold > 0 else np.inf   # neto de subproductos
    # ------------------------------------------------ flujo de caja (años 0..N)
    N = c["anios"]
    yrs = np.arange(N + 1)
    inv = np.zeros(N + 1); inv[0], inv[1] = c["inv"][0] * FCI, c["inv"][1] * FCI
    rate = np.ones(N + 1); rate[0] = 0.0; rate[1] = c["tasa_op1"]
    Fx = np.where(rate > 0, fixed, 0.0); Vx = rate * var; Rx = rate * revenue
    gross = Rx - Fx - Vx
    dep = np.zeros(N + 1); dep[1:] = FCI * 0.1
    pool = 0.0; taxable = np.zeros(N + 1)
    for t in range(N + 1):
        base = gross[t] - dep[t]
        use = min(pool, c["tope_perdidas"] * max(base, 0))
        taxable[t] = max(base - use, 0)
        pool = pool - use + max(-base, 0)
    tax_paid = np.zeros(N + 1)
    rv = np.array(ov.get("renta_years", case.get("renta_years", [c["renta"]] * (N + 1))), dtype=float)[:N + 1]   # v12: renta por año (ZOMAC)
    tax_paid[1:] = taxable[:-1] * rv[:-1]
    tax_paid[N] += taxable[N] * rv[N]
    net = gross - tax_paid
    cf = net - inv
    cf[1] -= WC
    cf[N] += WC
    disc = cf / (1 + c["tasa"]) ** yrs
    NPV = float(disc.sum())
    # MIRR (financiación y reinversión a la tasa de descuento)
    pos = np.where(cf > 0, cf, 0); neg = np.where(cf < 0, cf, 0)
    fv_pos = np.sum(pos * (1 + c["tasa"]) ** (N - yrs)); pv_neg = np.sum(neg / (1 + c["tasa"]) ** yrs)
    MIRR = (fv_pos / -pv_neg) ** (1 / N) - 1 if pv_neg < 0 and fv_pos > 0 else np.nan
    cum = np.cumsum(cf); cumd = np.cumsum(disc)
    def payback(cu, flows):
        idx = np.argmax(cu >= 0) if np.any(cu >= 0) else None
        if idx is None or idx == 0:
            return np.nan
        return float(yrs[idx - 1] - cu[idx - 1] / flows[idx])
    return dict(case=case["name"], FCI=FCI, capex=cap, revenue=revenue, revenue_main=revenue_main, revenue_bp=rev_bp, var=var, raw=raw, util=util, waste=waste,
                labor=labor, sup=sup, maint=maint, taxes_loc=taxes_loc, WC=WC, int_WC=int_WC, fixed=fixed,
                opex=var + fixed, qty=qty, sold=sold, price=price, LCOP=LCOP, NPV=NPV, MIRR=MIRR,
                payback=payback(cum, cf), payback_disc=payback(cumd, disc), cash=cf.tolist(), disc=disc.tolist(),
                taxes=tax_paid.tolist(), payroll=pay, gross_margin=(revenue - var - fixed) / revenue if revenue else np.nan,
                calendar=cal)


def breakeven_price(case, c=COMMON, lo=0.0, hi=None):
    hi = hi or case["product"]["price"] * 20
    f = lambda pr: evaluate(case, c, dict(price=pr))["NPV"]
    if f(hi) < 0:
        return np.nan
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def tornado(case, specs, c=COMMON):
    """specs: list of (label, key, worst, base, best). Devuelve el VPN en peor/mejor para cada parámetro."""
    base = evaluate(case, c)["NPV"]
    out = []
    for lab, key, w, b, be in specs:
        nw = evaluate(case, c, {key: w})["NPV"]; nb = evaluate(case, c, {key: be})["NPV"]
        out.append(dict(label=lab, key=key, worst=w, base=b, best=be, NPV_worst=nw, NPV_best=nb, range=abs(nb - nw)))
    return base, sorted(out, key=lambda r: -r["range"])


# ----------------------------------------------------------------------------- Monte Carlo (LHS + Iman–Conover)
def pert_ppf(u, a, m, b, lam=4.0):
    if b <= a:
        return np.full_like(u, a, dtype=float)
    al = 1 + lam * (m - a) / (b - a); be = 1 + lam * (b - m) / (b - a)
    return a + (b - a) * stats.beta.ppf(u, al, be)


def iman_conover(U, R):
    """Reordena columnas de U (n×k, marginales uniformes) para inducir la correlación de rangos R."""
    n, k = U.shape
    scores = stats.norm.ppf((np.arange(1, n + 1)) / (n + 1))
    rng = np.random.default_rng(12345)
    S = np.column_stack([rng.permutation(scores) for _ in range(k)])
    E = np.corrcoef(S, rowvar=False)
    P = np.linalg.cholesky(R); Q = np.linalg.cholesky(E)
    T = S @ np.linalg.inv(Q).T @ P.T
    out = np.empty_like(U)
    for j in range(k):
        out[np.argsort(np.argsort(T[:, j])), j] = np.sort(U[:, j])
    return out


def monte_carlo(case, dists, R=None, n=1000, seed=20260821, c=COMMON):
    """dists: list of (key, min, mode, max). Devuelve VPN, MIRR, costo nivelado por iteración."""
    rng = np.random.default_rng(seed)
    k = len(dists)
    U = (rng.permuted(np.tile(np.arange(n), (k, 1)), axis=1).T + rng.random((n, k))) / n   # LHS
    if R is not None:
        U = iman_conover(U, np.asarray(R))
    X = np.column_stack([pert_ppf(U[:, j], *dists[j][1:]) for j in range(k)])
    res = []
    for i in range(n):
        ov = {dists[j][0]: X[i, j] for j in range(k)}
        r = evaluate(case, c, ov)
        res.append((r["NPV"], r["MIRR"], r["LCOP"]))
    res = np.array(res)
    return dict(X=X, NPV=res[:, 0], MIRR=res[:, 1], LCOP=res[:, 2], P_pos=float(np.mean(res[:, 0] > 0)),
                P5=float(np.percentile(res[:, 0], 5)), P50=float(np.percentile(res[:, 0], 50)),
                P95=float(np.percentile(res[:, 0], 95)),
                CVaR5=float(res[:, 0][res[:, 0] <= np.percentile(res[:, 0], 5)].mean()))
