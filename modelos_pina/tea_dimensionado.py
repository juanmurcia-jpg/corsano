"""
TEA de Burk recalculado con los tamaños óptimos de dimensionamiento.py.

Para cada diseño (referencia TRL-9 u óptimo) se arma un caso TEA de planta (estructura de tea_burk.py y de los
libros de asaí y coco):
  - equipos: la lista de catálogo de cada opción elegida por el MILP (con sus equipos acompañantes), más los que
    no dependen del dimensionamiento (tanques de guarda de 90 d, cuarto frío, empacadoras);
  - producción: la del programa anual del diseño (fruta realmente procesada, vino, harina, bromelaína), no la
    nominal; consumos y servicios del balance de planta_trl9 a esa fruta procesada;
  - materia prima: toda la fruta procesada a 400 COP/kg (no solo las fracciones asignadas a cada línea) y el
    compostaje de las fracciones sin uso;
  - calendario: lun–sáb con 2 turnos, o con 3 turnos si el MILP eligió el tercer turno;
  - personal compartido (75 %) e ingenieros de planta como en tea_lineas.integrated_case.
El vino es el producto principal (precio 3 000 COP/L, como en el plan del MILP); harina, jugo de cáscara,
bromelaína y polvo entran como subproductos. Salidas: VPN, MIRR, LCOP, precio de equilibrio del vino, tornado,
Monte Carlo LHS + Iman–Conover y libros Excel verificados con LibreOffice (TEA_excel/).
"""
import json, os, math, copy
import numpy as np
import tea_burk as tb
import tea_lineas as tl
import planta_trl9 as pt
import capacidad as cp
import dimensionamiento as dm
import datos as DT
import tea_excel_run as tx

RES = os.path.join(os.path.dirname(__file__), "results")
WINE_PRICE = dm.WINE_PRICE


def E(cat, need, name):
    n, s, _ = pt.pick(cat, need)
    k = pt.CAT[cat]
    return dict(name=name, qty=n, size=s, ref_size=k["ref"][0], ref_USD=k["ref"][1], n=k["n"])


def option_equipment(u, lab):
    """Equipos de catálogo que componen la opción 'lab' del equipo 'u' (mismos que dimensionamiento.options)."""
    num = lambda: float(lab.split()[0].split("×")[0])
    if lab == "no":
        return []
    if u == "Frente":
        s = num(); return [E("lavado_seleccion", s, "Recepción, lavado y selección"), E("peladora_descorazonadora", s, "Peladora-descorazonadora")]
    if u == "Prensa":
        s = num(); return [E("prensa_banda", s, "Prensa de banda (pulpa)"), E("trituradora", s, "Trituradora de pulpa"),
                           E("macerador_camisa", s / 1.06 * 1.2, "Macerador enzimático con camisa")]
    if u in ("Prensa cáscara", "Prensa corazón"):
        s = num(); w = "cáscara" if "cáscara" in u else "corazón"
        return [E("prensa_banda", s, f"Prensa de {w}"), E("trituradora", s, f"Trituradora de {w}")]
    if u == "Decantadora":
        s = num(); return [E("decantadora", s, "Decantadora centrífuga de pulpa"), E("trituradora", s, "Trituradora de pulpa"),
                           E("macerador_camisa", s / 1.06 * 1.2, "Macerador enzimático con camisa")]
    if u == "Clarificación":
        tech, q = lab.split()[0], float(lab.split()[1])
        cat = {"MF": "MF_ceramica", "Flotación": "flotador_mosto", "Centrífuga": "centrifuga_discos"}[tech]
        name = {"MF": "Microfiltración cerámica de mosto", "Flotación": "Flotador de mosto (saturador + tanque)", "Centrífuga": "Centrífuga de discos para mosto"}[tech]
        return [E(cat, q, name)]
    if u == "MF lías":
        return [E("MF_lias", num(), "Microfiltración tangencial de lías")]
    if u == "Estabilización":
        if lab.startswith("SO"):
            return [E("dosificador_SO2", 1, "Dosificador de SO2")]
        tech, q = lab.split()[0], float(lab.split()[1])
        return [E("pasteurizador_placas", q, "Pasteurizador flash de mosto")] if tech == "HTST" else [E("UHPH", q, "Homogeneizador UHPH (300 MPa)")]
    if u == "Bodega":
        n = int(lab.split("×")[0]); q = (n - 1) * dm.VF / dm.T_PROC
        return [dict(name=f"Fermentador inox con camisa {dm.VF:.0f} m³", qty=n, size=dm.VF, ref_size=dm.VF, ref_USD=pt.fermenter_moresi(dm.VF, True), n=1.0),
                E("chiller", q * dm.HEAT_KW_PER_M3H * 1.1, "Chiller agua-glicol"), E("centrifuga_discos", q * 1.5, "Centrífuga clarificadora"),
                E("filtro_cartuchos", q * 1.5, "Filtración final"), E("propagador", 0.5, "Propagador / pie de cuba")]
    if u == "Secador":
        s = num(); return [E("secador_banda", s, "Secador de banda"), E("caldera", s * 3.2 / 3.6 * 1.1, "Generador de aire caliente / caldera"),
                           E("molino_tamiz", s / 1000 / dm.DRY_W * dm.FLOUR_PC * 1000, "Molino y tamizadora")]
    if u == "Almacén de mosto":
        V = num()
        if V <= 50:
            return [E("tanque_pulmon", V, "Tanque pulmón de mosto")]
        e = E("tanque_guarda", V, "Almacén aséptico de mosto"); e["ref_USD"] *= 1.4; return [e]
    if u == "Aspersión":
        s = num(); j = s / 1000 / 0.12
        return [E("spray_dryer", s, "Secador por aspersión"), E("UF_bromelaina", s / 0.12 / 25, "Ultrafiltración 10 kDa"),
                E("centrifuga_discos", j, "Centrífuga de jugo de corazón"), E("tanque_precipitacion", j * 0.4, "Tanques de precipitación"),
                E("cuarto_frio", 10, "Cuarto frío de producto")]
    if u == "Bodega cáscara":
        n = int(lab.split("×")[0]); q = (n - 1) * dm.VF / dm.T_PEEL
        return [dict(name=f"Fermentador de jugo de cáscara {dm.VF:.0f} m³", qty=n, size=dm.VF, ref_size=dm.VF, ref_USD=pt.fermenter_moresi(dm.VF, True), n=1.0),
                E("chiller", q * dm.HEAT_KW_PER_M3H * 1.1, "Chiller de la bodega de cáscara")]
    if u == "Caldera de corona":
        q = num(); e = E("caldera", q, "Caldera de biomasa (corona), alimentación y cenizas"); e["ref_USD"] *= 1.3
        return [e, E("astilladora_secador_biomasa", q * 3.6 / dm.CROWN_MJ_T, "Picadora y secador de corona")]
    if u == "Acetificador":
        V = num(); kgh = V * dm.ACET_PROD / 24.0
        return [E("acetador", V, "Acetificador sumergido (turbina autoaspirante)"), E("chiller", kgh * dm.ACID_HEAT / 3.6 * 1.1, "Chiller del acetificador"),
                E("grupo_electrogeno", dm.AERATION_KW_M3 * V * 1.25 + kgh * dm.ACID_HEAT / 3.6 / 4.0, "Grupo electrógeno de emergencia"),
                E("centrifuga_espuma", 1, "Centrífuga de espuma"), E("lavador_gases", 1, "Condensador y lavador de gases"),
                E("MF_vinagre", kgh / dm.VIN_ACID * 1000 / 100.0, "Microfiltración de vinagre")]
    if u == "Pretratamiento cáscara":
        return [] if lab == "agua" else [E("mezclador_cal", 2, "Mezclador de cáscara con Ca(OH)2 al 0,1 %"),
                                         E("dosificador_nutrientes", 1, "Dosificador de lechada de cal")]
    if u == "Enzima cáscara":
        tech, q = lab.split()[0], float(lab.split()[1])
        T = dm.ENZ_TECH[tech]
        lio = E("liofilizador", q * 12 * T["wet"] * (0.83 if tech == "Precipitación" else 0.95), "Liofilizador de enzima")
        if tech == "Precipitación":
            return [E("tanque_precipitacion", q, "Tanques de precipitación con polisacárido (×2)") | dict(qty=2 * pt.pick("tanque_precipitacion", q)[0]),
                    E("centrifuga_discos", q, "Centrífuga del precipitado"), lio]
        return [E("centrifuga_discos", q, "Centrífuga de prefiltrado"), E("UF_bromelaina", q * 1000 / 25, "Ultrafiltración 10 kDa del jugo de cáscara"), lio]
    # ---- v10
    if u == "Extractora hojas":
        return [E("extrusora_hojas", num(), "Extractora de jugo de hojas (tornillo)")]
    if u == "Bodega etanol":
        n = int(lab.split("×")[0]); q = (n - 1) * dm.VF / dm.T_LEAF
        return [dict(name=f"Fermentador de jugo de hojas {dm.VF:.0f} m³", qty=n, size=dm.VF, ref_size=dm.VF, ref_USD=pt.fermenter_moresi(dm.VF, True), n=1.0),
                E("centrifuga_discos", q, "Centrífuga de levadura (proteína unicelular)")]
    if u == "Destilación":
        return [E("columna_destilacion", num(), "Columna de destilación de etanol hidratado")]
    if u == "Digestor":
        return [E("digestor_anaerobio", num(), "Digestor anaerobio CSTR (35 °C) con gasómetro")]
    if u == "Motor biogás":
        return [E("motor_biogas", num(), "Motor-generador a biogás con limpieza de H2S")]
    if u in dm.HUB:
        H_ = dm.HUB[u]; s = num(); ref = H_["cap"] * 1000 / (dm.AC * 8766)
        return [dict(name=f"Planta de {u.lower()} (escalada del ejemplo de SuperPro)", qty=1, size=s, ref_size=ref, ref_USD=H_["tci"] / dm.LANG, n=0.6)]
    raise KeyError(u)


def build_case(r, label, with_bromelain):
    """Caso TEA de planta a partir de una solución de dimensionamiento.py (primer escenario)."""
    sc = r["scen"][0]; pr = sc["products"]
    F = pr["fruta_t"]
    D = pt.design(F)
    L = D["lines"]; b = D["balance"]
    v, h, br = L["vino"], L["harina"], L["bromelaina"]
    eqs = []
    for u, lab in r["sizes"].items():
        eqs += option_equipment(u, lab)
    wine_m3 = pr["vino_m3"] - pr.get("vino_a_vinagre_m3", 0.0)           # vino vendido
    vin_m3, acid_kg, pj_t = pr.get("vinagre_m3", 0.0), pr.get("acido_kg", 0.0), pr.get("jugo_cascara_vinagre_t", 0.0)
    enz_lab = r["sizes"].get("Enzima cáscara", "no"); enz_t, enz_kg = pr.get("jugo_enzima_t", 0.0), pr.get("enzima_cascara_kg", 0.0)
    has_enz = enz_lab != "no" and enz_kg > 0
    torta_t = pr.get("torta_t", pr["harina_t"] / dm.FLOUR_PC)
    juice_t = pr.get("jugo_cascara_t", torta_t / dm.CAKE * cp.Y["peel_juice_frac"])
    has_vin = r["sizes"].get("Acetificador", "no") != "no"
    if vin_m3 > 0:
        eqs.append(E("tanque_guarda", vin_m3 * 30 / 365 * 1.1, "Tanques de vinagre (30 d)"))
    eqs += [E("tanque_guarda", max(wine_m3, 1.0) * 90 / 365 * 1.1, "Tanques de guarda (90 d)"), E("cuarto_frio", 10, "Cuarto frío (levaduras, enzimas)"),
            E("empacadora", 1, "Empacadora de harina"), E("generador_N2", 1, "Generador de N2 (inertización de tanques)"),
            E("dosificador_nutrientes", 1, "Dosificador de nutrientes (DAP)")]
    if with_bromelain:
        eqs.append(E("empacadora", 1, "Empacadora de bromelaína y polvo"))
    for e in eqs:
        e.setdefault("TRL", 9)
    brom_frac = (pr["bromelaina_kg"] / br["flows"]["bromelain_kg"]) if with_bromelain and br["flows"]["bromelain_kg"] > 0 else 0.0
    clar, stab = r["sizes"]["Clarificación"], r["sizes"]["Estabilización"]
    rows = sc["periods"]
    must = pr.get("mosto_m3", sum(x["mf"] for x in rows))                 # mosto que entra a clarificación
    stab_m3 = sum(x.get("stab", 0.0) for x in rows)
    dec_t = sum(x["Pd"].get("pulpa", 0.0) for x in rows)
    mem = 0.0
    if clar.startswith("MF"):
        mem += 0.15 * dm.buy("MF_ceramica", float(clar.split()[1]))
    if r["sizes"].get("MF lías", "no") != "no":
        mem += 0.15 * dm.buy("MF_lias", float(r["sizes"]["MF lías"].split()[0]))
    raw = [dict(name="Fruta de rechazo puesta en planta", qty_year=F * 1000, price=tl.M("fruta_kg"), main=True),
           dict(name="Pectinasa", qty_year=v["consumables"]["pectinasa_kg"], price=tl.M("pectinasa_kg")),
           dict(name="Levadura seca activa", qty_year=v["consumables"]["levadura_kg"], price=tl.M("levadura_kg")),
           dict(name="Reposición de membranas MF (COP)", qty_year=1, price=mem),
           dict(name="Nutrientes (DAP, 200 mg/L)", qty_year=must, price=dm.DAP_VC),
           dict(name="Metabisulfito (SO2, ≈ 50 mg/L)", qty_year=(stab_m3 if stab.startswith("SO") else 0.0), price=dm.SO2_VC),
           dict(name="Coadyuvantes de flotación", qty_year=(must if clar.startswith("Flot") else 0.0), price=dm.FLOT_VC - 1.0 * dm.E_COP),
           dict(name="Empaques de harina (COP)", qty_year=(pr["harina_t"] + pr.get("harina_lias_t", 0.0)) * 1000 / 25, price=2_500),
           dict(name="Levadura, nutrientes y SO2 del jugo de cáscara (t)", qty_year=pj_t, price=dm.PJ_VC),
           dict(name="Cal y mezcla de la cáscara (t)", qty_year=pr.get("cascara_cal_t", 0.0), price=dm.LIME_VC),
           dict(name="Reactivos, energía y liofilización de la enzima (t de jugo)", qty_year=enz_t if has_enz else 0.0,
                price=dm.ENZ_TECH[enz_lab.split()[0]]["vc"] if has_enz else 0.0),
           dict(name="Nutrientes y filtración del vinagre (kg ácido)", qty_year=acid_kg, price=500.0),
           # v10: hojas, etanol, biogás y hub
           dict(name="Acopio de hojas puestas en planta (t)", qty_year=pr.get("hojas_t", 0.0), price=dm.ACOPIO_VC, key="acopio"),
           dict(name="Levadura e inóculo del jugo de hojas (t)", qty_year=pr.get("jugo_hojas_etanol_t", 0.0), price=dm.ETOH_VC),
           dict(name="Levadura, nutrientes y SO2 del jugo de hojas a vinagre (t)", qty_year=pr.get("jugo_hojas_vinagre_t", 0.0), price=dm.PJ_VC),
           dict(name="Operación del motor a biogás (kWh)", qty_year=pr.get("elec_bio_kWh", 0.0), price=dm.BIO_OM)]
    for prod, key in (("Ácido cítrico", "citrico_kg"), ("Xantana", "xantana_kg")):
        if pr.get(key, 0.0) > 0:
            raw.append(dict(name=f"Servicios y reactivos de {prod.lower()} (kg)", qty_year=pr[key], price=dm.HUB[prod]["vc"]))
    lines = [v, h] + ([br] if with_bromelain else [])
    scale = [1.0, torta_t / (h["flows"]["peel_t"] * dm.CAKE)] + ([brom_frac] if with_bromelain else [])   # v9: la línea de harina sigue a la torta secada
    kwh_extra = (dec_t * 4.5 + must * {"MF": 0.0, "Flotación": 1.0, "Centrífuga": 2.0}[clar.split()[0]] + pr.get("lias_MF_m3", 0.0) * 1.0
                 + (stab_m3 * 100.0 if stab.startswith("UHPH") else 0.0) + pr["vino_m3"] * 0.5
                 + (dm.AERATION_KW_M3 * float(r["sizes"]["Acetificador"].split()[0]) * 0.9 * 8766 if has_vin else 0.0)
                 + acid_kg * dm.ACID_HEAT / 3.6 / 4.0 + pr.get("corona_caldera_t", 0.0) * 10.0
                 + dm.KWH_LEAF["ext"] * pr.get("hojas_extraidas_t", 0.0) + dm.KWH_LEAF["etoh"] * pr.get("jugo_hojas_etanol_t", 0.0)
                 + dm.KWH_LEAF["ad"] * pr.get("jugo_hojas_digestor_t", 0.0) + dm.KWH_LEAF["pulp"] * pr.get("pulpa_hojas_caldera_t", 0.0)
                 - pr.get("elec_bio_usada_kWh", 0.0))                                                       # v10: hojas y biogás
    heat_past = 0.0 if stab.startswith("HTST") else v["flows"]["juice_m3"] * dm.HTST_VC / dm.H_COP   # MJ de pasteurización que no se gastan
    heat_past -= pr.get("lias_secador_t", 0.0) * dm.LEES_DRY_EQ * h["heat_MJ"] / (h["flows"]["peel_t"] * dm.CAKE)   # secado de lías y retenidos
    heat_past += pr.get("calor_corona_GJ", 0.0) * 1000                                                          # calor de la caldera (corona y pulpa de hojas)
    heat_past -= dm.Q_DEST * pr.get("etanol_kg", 0.0) + dm.Q_AD * pr.get("jugo_hojas_digestor_t", 0.0)          # v10: destilación y digestor
    heat_past += pr.get("calor_bio_usado_MJ", 0.0)                                                              # v10: calor del motor a biogás
    util = [dict(name="Electricidad", qty_year=sum(l["elec_kWh"] * 1.3 * f for l, f in zip(lines, scale)) + kwh_extra, price_key="elec_COP_kWh"),
            dict(name="Calor de proceso (MJ)", qty_year=sum(l["heat_MJ"] * f for l, f in zip(lines, scale)) - heat_past, price_key="calor_COP_MJ",
                 crown_MJ=pr.get("calor_corona_GJ", 0.0) * 1000),
            dict(name="Agua de planta (t)", qty_year=sum(l["water_t"] * f for l, f in zip(lines, scale)), price_key="agua_COP_t")]
    unused = b["crown_t"] - pr.get("corona_caldera_t", 0.0) + (b["core_t"] * (1 - brom_frac) if with_bromelain else b["core_t"]) + pr.get("cascara_compost_t", 0.0)
    waste = [dict(name="Aguas residuales (t)", qty_year=util[2]["qty_year"], price=tb.COMMON["ARD_COP_t"]),
             dict(name="Compostaje de fracciones sin uso (t)", qty_year=unused, price=dm.COMPOST * 1000),
             dict(name="Lías y espumas a compostaje (m³)", qty_year=pr.get("lias_compost_m3", 0.0), price=dm.LEES_DISP)]
    byp = [dict(name="harina", qty_year=(pr["harina_t"] + pr.get("harina_lias_t", 0.0)) * 1000, price=tl.M("harina_kg")),
           dict(name="jugo", qty_year=max(juice_t * 1000 - pj_t * 1000, 0.0), price=tl.M("jugo_cascara_kg"))]
    for nm_, key, price in (("etanol", "etanol_L", dm.ETOH_PRICE), ("levadura", "levadura_kg", dm.YEAST_PRICE),
                            ("electricidad_excedente", "elec_excedente_kWh", dm.VAL_EXC), ("citrico", "citrico_kg", dm.HUB["Ácido cítrico"]["price"]),
                            ("xantana", "xantana_kg", dm.HUB["Xantana"]["price"])):
        if pr.get(key, 0.0) > 1e-6:
            byp.append(dict(name=nm_, qty_year=pr[key], price=price))
    if has_enz:
        byp.append(dict(name="bromelaina_cascara", qty_year=enz_kg, price=dm.BROM_PRICE * dm.ENZ_TECH[enz_lab.split()[0]]["pf"]))
    if vin_m3 > 0:
        byp.append(dict(name="vinagre", qty_year=vin_m3 * 1000, price=dm.VIN_PRICE))
    if with_bromelain:
        raw += [dict(name="Reposición de membranas UF (COP)", qty_year=1, price=0.2 * pt.pick("UF_bromelaina", float(r["sizes"]["Aspersión"].split()[0]) / 0.12 / 25)[2] * tl.TRM),
                dict(name="Empaques y reactivos de bromelaína (COP)", qty_year=pr["bromelaina_kg"], price=8_000)]
        byp += [dict(name="bromelaina", qty_year=pr["bromelaina_kg"], price=tl.M("bromelaina_kg")),
                dict(name="polvo", qty_year=br["flows"]["powder_t"] * brom_frac * 1000, price=tl.M("polvo_kg"))]
    lv_pos = (1 if pr.get("hojas_extraidas_t", 0) > 0 else 0) + (1 if pr.get("etanol_kg", 0) > 0 else 0) + (1 if pr.get("ch4_kg", 0) > 0 else 0) \
        + sum(1 for k_ in ("citrico_kg", "xantana_kg") if pr.get(k_, 0) > 0)
    pos = math.ceil((4 + 2 + (2 if with_bromelain else 0) + (1 if has_vin else 0) + (1 if has_enz else 0) + lv_pos) * 0.75)
    cal = dict(tb.calendar(3), shifts=3) if r.get("turno3") else 3
    vin_share_pj = (dm.A_PJ * pj_t / acid_kg) if acid_kg > 0 else 0.0
    return dict(name=label, vin_share_pj=vin_share_pj, product=dict(name="Vino de piña a granel", unit="L", qty_year=wine_m3 * 1000, price=WINE_PRICE),
                raw=raw, utilities=util, waste=waste, equipment=eqs, positions=pos, calendar=cal, byproducts=byp,
                engineer=2 if with_bromelain else 1)


def breakeven_vinegar(case, lo=0.0, hi=20_000.0):
    """Precio del vinagre (COP/L) que hace VPN = 0; None si el caso no produce vinagre."""
    if not any(bp["name"] == "vinagre" and bp["qty_year"] > 0 for bp in case["byproducts"]):
        return None
    f = lambda pr_: tb.evaluate(case, overrides={"bp_price_vinagre": pr_})["NPV"]
    if f(lo) > 0:
        return lo
    if f(hi) < 0:
        return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi)


def run(case, mc_n=1000):
    r = tb.evaluate(case)
    be = tb.breakeven_price(case)
    be_vin = breakeven_vinegar(case)
    specs, dists, R = tl.tornado_specs(case), tl.mc_dists(case), [list(rw) for rw in tl.MC_R]
    vp = next((bp["price"] for bp in case["byproducts"] if bp["name"] == "vinagre" and bp["qty_year"] > 0), None)
    if vp:   # el precio del vinagre también es incierto: mismo rango ±30 % que el del vino, independiente
        specs = specs + [("Precio del vinagre", "bp_price_vinagre", 0.7 * vp, vp, 1.3 * vp)]
        dists = dists + [("bp_price_vinagre", 0.7 * vp, vp, 1.3 * vp)]
        R = [rw + [0.0] for rw in R] + [[0.0] * len(R) + [1.0]]
    # v9: rendimiento de fermentación del jugo de cáscara (Seguí y Fito 2018: 0,23–0,43 g/g) y corona que llega a planta (Campos 2020:
    # en la industria la corona se retira en el campo y además es material de siembra)
    s_pj = case.get("vin_share_pj", 0.0)
    if vp and s_pj > 0:
        lo, mo_, hi = (1 + s_pj * (a_ / dm.A_PJ - 1) for a_ in dm.A_PJ_RANGE)
        specs = specs + [("Rendimiento del jugo de cáscara (0,23–0,43 g/g)", "bp_qty_vinagre", lo, mo_, hi)]
        dists = dists + [("bp_qty_vinagre", lo, mo_, hi)]
        R = [rw + [0.0] for rw in R] + [[0.0] * len(R) + [1.0]]
    ep = next((bp["price"] for bp in case["byproducts"] if bp["name"] == "etanol" and bp["qty_year"] > 0), None)
    if ep:   # v10: precio del etanol (rango de tea_lineas.M) y costo de acopio de hojas (registro de parámetros)
        lo, mo_, hi = DT.tri("precio_etanol_L")
        specs = specs + [("Precio del etanol", "bp_price_etanol", lo, mo_, hi)]
        dists = dists + [("bp_price_etanol", lo, mo_, hi)]
        R = [rw + [0.0] for rw in R] + [[0.0] * len(R) + [1.0]]
    if any(r_.get("key") == "acopio" and r_["qty_year"] > 0 for r_ in case["raw"]):
        lo, mo_, hi = DT.tri("costo_acopio_hojas")
        specs = specs + [("Costo de acopio de hojas", "raw_price_acopio", hi, mo_, lo)]
        dists = dists + [("raw_price_acopio", lo, mo_, hi)]
        R = [rw + [0.0] for rw in R] + [[0.0] * len(R) + [1.0]]
    if any(u.get("crown_MJ", 0) > 0 for u in case["utilities"]):
        specs = specs + [("Corona que llega a planta (40–100 %)", "crown_avail", 0.4, 0.9, 1.0)]
        dists = dists + [("crown_avail", 0.4, 0.9, 1.0)]
        R = [rw + [0.0] for rw in R] + [[0.0] * len(R) + [1.0]]
    _, tor = tb.tornado(case, specs)
    mc = tb.monte_carlo(case, dists, R, n=mc_n)
    return dict(res={k: v for k, v in r.items() if k != "capex"}, capex={k: v for k, v in r["capex"].items() if k != "rows"},
                equipment=r["capex"]["rows"], breakeven=be, breakeven_vinegar=be_vin, tornado=tor,
                mc=dict(P_pos=mc["P_pos"], P5=mc["P5"], P50=mc["P50"], P95=mc["P95"], CVaR5=mc["CVaR5"], NPV=mc["NPV"].tolist()),
                case=case)


if __name__ == "__main__":
    dim = json.load(open(f"{RES}/dimensionamiento.json"))
    sel = [("A · Referencia TRL-9", "E1|Referencia TRL-9 (planta_trl9, 6 200 t)", False),
           ("A · Óptimo con la topología anterior", "E1|Óptimo con la topología anterior (prensa, MF de mosto, HTST)", False),
           ("A · Óptimo con la superestructura ampliada", "E1|Óptimo económico", False),
           ("A · Óptimo sin vinagre", "E1|Óptimo sin vinagre", False),
           ("A · Óptimo sin caldera de corona", "E1|Óptimo sin caldera de corona", False),
           ("A · Óptimo sin SO₂", "E1|Óptimo sin SO₂", False),
           ("A · Diseño v9 con parámetros v10", "E1|Diseño v9 con parámetros v10", False),
           ("A · Óptimo sin opciones v10", "E1|Óptimo sin opciones v10 (sin hojas ni hub)", False),
           ("A · Óptimo sin etanol de hojas", "E1|Óptimo sin etanol de hojas", False),
           ("A · Óptimo sin digestor", "E1|Óptimo sin digestor", False),
           ("B · Referencia TRL-9 con bromelaína", "E5|B referencia (prensas dedicadas TRL-9)", True),
           ("B · Óptimo con la topología anterior", "E5|B óptimo con la topología anterior", True),
           ("B · Óptimo con la superestructura ampliada", "E5|B óptimo económico", True)]
    out = dict(cases={}, scale=[], check=[])
    made = []
    for lab, key, wb in sel:
        c = build_case(dim[key], lab, wb)
        res = run(c)
        res["sizes"] = dim[key]["sizes"]; res["turno3"] = dim[key]["turno3"]; res["fruit_t"] = dim[key]["scen"][0]["products"]["fruta_t"]
        res["dim_margin"] = dim[key]["obj"]
        out["cases"][lab] = res
        r = res["res"]
        print(lab, f"FCI {r['FCI']/1e6:,.0f} | VPN {r['NPV']/1e6:,.0f} | MIRR {r['MIRR']*100:.1f} % | LCOP {r['LCOP']:,.0f} COP/L | "
                   f"PE vino {res['breakeven']:,.0f} | P(VPN>0) {res['mc']['P_pos']:.2f} | nómina {r['labor']/1e6:,.0f}", flush=True)
        made.append(tx.make(c, dict(dim[key]["scen"][0]["products"]), "Dimensionado_Choco2022",
                            note=f"Tamaños de dimensionamiento.py: {dim[key]['sizes']}" + ("; tercer turno" if dim[key]["turno3"] else "")))
    # regla por escala: TEA del óptimo de cada oferta (sin Monte Carlo)
    for k in sorted([k for k in dim if k.startswith("E2|")], key=lambda k: float(k.split("|")[1])):
        rr = dim[k]
        c = build_case(rr, f"Óptimo a {rr['scen'][0]['supply']:,.0f} t/año", False)
        r = tb.evaluate(c)
        out["scale"].append(dict(supply=rr["scen"][0]["supply"], fruit_t=rr["scen"][0]["products"]["fruta_t"], sizes=rr["sizes"], turno3=rr["turno3"],
                                 FCI=r["FCI"], NPV=r["NPV"], MIRR=r["MIRR"], LCOP=r["LCOP"], breakeven=tb.breakeven_price(c), labor=r["labor"],
                                 breakeven_vinegar=breakeven_vinegar(c), vinagre_m3=rr["scen"][0]["products"].get("vinagre_m3", 0.0)))
        print("escala", round(rr["scen"][0]["supply"]), f"FCI {r['FCI']/1e6:,.0f} VPN {r['NPV']/1e6:,.0f} PE {out['scale'][-1]['breakeven']:,.0f}", flush=True)
    # precios del vino y del vinagre: TEA del diseño óptimo de cada par de precios (E6)
    out["prices"] = []
    for k in sorted([k for k in dim if k.startswith("E6|")], key=lambda k: (float(k.split("|")[1]), float(k.split("|")[2]))):
        rr = dim[k]; wp, vp = float(k.split("|")[1]), float(k.split("|")[2])
        c = build_case(rr, f"Vino {wp:.0f} · vinagre {vp:.0f}", False)
        c["product"]["price"] = wp
        for bp in c["byproducts"]:
            if bp["name"] == "vinagre":
                bp["price"] = vp
        r = tb.evaluate(c); pr_ = rr["scen"][0]["products"]
        out["prices"].append(dict(wine_price=wp, vinegar_price=vp, sizes=rr["sizes"], NPV=r["NPV"], FCI=r["FCI"], MIRR=r["MIRR"],
                                  vino_vendido_m3=pr_["vino_m3"] - pr_.get("vino_a_vinagre_m3", 0.0), vino_a_vinagre_m3=pr_.get("vino_a_vinagre_m3", 0.0),
                                  jugo_cascara_vinagre_t=pr_.get("jugo_cascara_vinagre_t", 0.0), vinagre_m3=pr_.get("vinagre_m3", 0.0)))
        print("precios", wp, vp, f"VPN {r['NPV']/1e6:,.0f}", rr["sizes"].get("Acetificador"), flush=True)
    out["check"] = tx.recalc_check(made)
    for c in out["check"]:
        print(c["file"], "VPN py", round(c["NPV_py"] / 1e6, 1), "xl", None if c["NPV_xl"] is None else round(c["NPV_xl"] / 1e6, 1), "dRel", c["dNPV_rel"])
    json.dump(out, open(f"{RES}/tea_dimensionado.json", "w"), default=float)
