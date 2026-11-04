"""
Diseño industrial TRL-9 de la biorrefinería de piña.

1. Materia prima a procesar: base de la tesis (78 300 hL/año de vino -> fruta requerida, capacidad.py) y oferta
   actual (EVA 2022, UPRA: Chocó 1 039 ha sembradas, 888 ha cosechadas, 6 146 t, 6,92 t/ha).
2. Selección TRL-9: solo tecnologías con planta comercial operando (TRL 9). Las de TRL < 9 se listan aparte.
3. Dimensionamiento con tamaños de catálogo (unidades discretas) a partir del balance de masa y del calendario:
   frente de extracción con el escenario 3 de la plantilla (lun–sáb, 2 turnos, 6 h efectivas) y procesos
   biológicos continuos (24/7).
Los costos de referencia son de orden de magnitud [S] (USD 2024, ex-works, inox 304) salvo los fermentadores,
que vienen de las correlaciones de Moresi (1989b) [C]; deben reemplazarse por cotizaciones, como en los TEA de
asaí y coco (Agrosavia).
"""
import math
import numpy as np
import capacidad as cp
import moresi as mo
import params as p

EVA2022 = dict(area_sembrada_ha=1039, area_cosechada_ha=888, produccion_t=6146, rend_t_ha=6.92)   # UPRA, Chocó

TECH = {   # tecnología: (TRL, nota)
    "Lavado, selección y pelado-descorazonado mecánico": (9, "estándar en enlatadoras y jugos"),
    "Maceración enzimática + prensado": (9, "práctica industrial en jugos de fruta"),
    "Microfiltración cerámica tangencial de jugo": (9, "clarificación industrial de jugos"),
    "Pasteurización flash de mosto (HTST)": (9, "alternativa TRL-9 a la UHPH"),
    "UHPH (Ypsicon)": (8, "unidades comerciales recientes; poca referencia en mosto de piña"),
    "Fermentación alcohólica en tanques inox con camisa": (9, "vinificación"),
    "Envejecimiento en tanques inox": (9, "vinificación"),
    "Acetificación sumergida (acetador tipo Frings/Cetotec)": (9, ">60 % del vinagre mundial (Emde 2017; Bekatorou 2020)"),
    "Acetificación estática de superficie": (9, "método tradicional (Orleans)"),
    "Bromelaína: extracción, UF y secado por aspersión": (9, "producción comercial en Tailandia y Costa Rica"),
    "Polvo nutracéutico por secado por aspersión": (9, "secado de jugos"),
    "Harina de fibra de cáscara (prensa + secador de banda + molino)": (9, "harinas de subproductos de frutas"),
    "Etanol hidratado: fermentación + destilación": (9, "industria alcoholera"),
    "Gasificación downdraft + motor (≤ 100 kWe)": (8, "paquetes comerciales; confiabilidad limitada con biomasa húmeda"),
    "Pretratamiento/deslignificación + hidrólisis enzimática de hojas/corona": (6, "piloto; no apto para diseño TRL-9"),
    "Ácido cítrico / xantana del hub": (7, "comercial con melazas/glucosa, no con hidrolizado de piña"),
    "Decantadora centrífuga de pulpa": (9, "extracción continua de jugos y mostos (Morata 2022, cap. 4)"),
    "Flotación de mosto": (9, "clarificación de mostos blancos, continua o por lotes (Morata 2022, cap. 8)"),
    "Centrífuga de discos para mosto": (9, "clarificación dinámica de mostos (Morata 2022, cap. 8)"),
    "Microfiltración tangencial de lías": (9, "recuperación de jugo de lías y espumas (Morata 2022, cap. 8)"),
    "Sulfitado del mosto (SO2)": (9, "práctica estándar de vinificación"),
    "UHPH del mosto (300 MPa)": (8, "equipos industriales hasta 10 000 L/h, un solo proveedor (Morata 2022, cap. 5)"),
    "Inertización con N2": (9, "protección del mosto y el vino frente al oxígeno (Morata 2022, caps. 23 y 25)"),
}

CAT = {   # catálogo: tamaños discretos, unidad, referencia (tamaño, USD 2024), exponente   [S] salvo indicación
    "lavado_seleccion": dict(sizes=[1, 2, 3, 5, 8, 10], unit="t/h", ref=(3, 30_000), n=0.6),
    "peladora_descorazonadora": dict(sizes=[1.5], unit="t/h por unidad", ref=(1.5, 25_000), n=0.6),
    "trituradora": dict(sizes=[1, 2, 3, 5, 8], unit="t/h", ref=(3, 15_000), n=0.6),
    "macerador_camisa": dict(sizes=[1, 2, 3, 5, 8], unit="m3", ref=(5, 28_000), n=0.6),
    "prensa_banda": dict(sizes=[1, 2, 3, 5, 8], unit="t/h", ref=(3, 75_000), n=0.6),
    "MF_ceramica": dict(sizes=[5, 10, 20, 40, 60, 80], unit="m2", ref=(20, 110_000), n=0.7),
    "pasteurizador_placas": dict(sizes=[500, 1000, 2000, 3000, 5000], unit="L/h", ref=(2000, 45_000), n=0.6),
    "tanque_pulmon": dict(sizes=[5, 10, 20, 30, 50], unit="m3", ref=(30, 25_000), n=0.6),
    "propagador": dict(sizes=[0.5, 1, 2, 3], unit="m3", ref=(2, 18_000), n=0.6),
    "chiller": dict(sizes=[10, 20, 30, 50, 80, 120, 200], unit="kW", ref=(50, 28_000), n=0.7),
    "intercambiador_placas": dict(sizes=[1], unit="u", ref=(1, 10_000), n=1.0),
    "centrifuga_discos": dict(sizes=[0.5, 1, 2, 3, 5], unit="m3/h", ref=(2, 85_000), n=0.6),
    "tanque_guarda": dict(sizes=[10, 20, 30, 50, 80, 100, 160], unit="m3", ref=(100, 55_000), n=0.6),
    "filtro_cartuchos": dict(sizes=[0.5, 1, 2, 3], unit="m3/h", ref=(2, 18_000), n=0.6),
    "acetador": dict(sizes=[1, 2, 4, 6, 10, 20], unit="m3", ref=(10, 260_000), n=0.6),
    "tanque_estatico": dict(sizes=[10, 20, 50], unit="m3", ref=(50, 25_000), n=0.6),
    "UF_bromelaina": dict(sizes=[5, 10, 20, 40], unit="m2", ref=(20, 70_000), n=0.7),
    "tanque_precipitacion": dict(sizes=[0.5, 1, 2, 3], unit="m3", ref=(2, 15_000), n=0.6),
    "spray_dryer": dict(sizes=[5, 10, 25, 50, 100], unit="kg agua/h", ref=(25, 120_000), n=0.6),
    "secador_banda": dict(sizes=[50, 100, 200, 300, 500, 800], unit="kg agua/h", ref=(300, 180_000), n=0.6),
    "molino_tamiz": dict(sizes=[50, 100, 200, 400], unit="kg/h", ref=(200, 15_000), n=0.6),
    "empacadora": dict(sizes=[1], unit="u", ref=(1, 20_000), n=1.0),
    "columna_destilacion": dict(sizes=[10, 25, 50, 100], unit="L/h etanol", ref=(50, 180_000), n=0.6),
    "gasificador_MCI": dict(sizes=[20, 30, 50, 80, 100], unit="kWe", ref=(50, 150_000), n=0.7),
    "astilladora_secador_biomasa": dict(sizes=[0.2, 0.5, 1.0], unit="t/h", ref=(0.5, 30_000), n=0.6),
    "caldera": dict(sizes=[100, 200, 300, 500, 800], unit="kWt", ref=(300, 60_000), n=0.6),
    "cuarto_frio": dict(sizes=[10, 20, 40], unit="m3", ref=(20, 12_500), n=0.6),
    # superestructura ampliada con White Wine Technology (Morata, ed., 2022), caps. 4, 5, 8, 12, 23 y 25   [S]
    "decantadora": dict(sizes=[1, 2, 3, 5, 8], unit="t/h pulpa", ref=(3, 160_000), n=0.6),
    "flotador_mosto": dict(sizes=[0.5, 1, 2, 4, 8], unit="m3/h", ref=(2, 40_000), n=0.6),
    "UHPH": dict(sizes=[500, 1000, 2000, 5000, 10000], unit="L/h", ref=(1000, 400_000), n=0.6),
    "dosificador_SO2": dict(sizes=[1], unit="u", ref=(1, 6_000), n=1.0),
    "MF_lias": dict(sizes=[2, 5, 10, 20], unit="m2", ref=(5, 45_000), n=0.7),
    "generador_N2": dict(sizes=[1], unit="u", ref=(1, 30_000), n=1.0),
    "dosificador_nutrientes": dict(sizes=[1], unit="u", ref=(1, 5_000), n=1.0),
    # vinagre (Emde 2017, Ullmann's Food and Feed: planta Frings; Bekatorou 2020)   [S]
    "grupo_electrogeno": dict(sizes=[10, 20, 50, 100, 200], unit="kW", ref=(50, 25_000), n=0.7),
    "centrifuga_espuma": dict(sizes=[1], unit="u", ref=(1, 35_000), n=1.0),
    "lavador_gases": dict(sizes=[1], unit="u", ref=(1, 15_000), n=1.0),
    "MF_vinagre": dict(sizes=[2, 5, 10, 20], unit="m2", ref=(5, 40_000), n=0.7),
}


def pick(cat, need, max_units=20):
    """Tamaño de catálogo y número de unidades: la menor combinación (n, tamaño) que cubre 'need'."""
    best = None
    for s in CAT[cat]["sizes"]:
        n = max(1, math.ceil(need / s - 1e-9))
        if n > max_units:
            continue
        cost = n * CAT[cat]["ref"][1] * (s / CAT[cat]["ref"][0]) ** CAT[cat]["n"]
        if best is None or cost < best[2]:
            best = (n, s, cost)
    if best is None:
        s = CAT[cat]["sizes"][-1]; n = math.ceil(need / s)
        best = (n, s, n * CAT[cat]["ref"][1] * (s / CAT[cat]["ref"][0]) ** CAT[cat]["n"])
    return best


def eq(name, cat, need, label, tech, **kw):
    n, s, _ = pick(cat, need)
    ref_s, ref_c = CAT[cat]["ref"]
    d = dict(name=label, cat=cat, qty=n, size=s, unit=CAT[cat]["unit"], ref_size=ref_s, ref_USD=ref_c,
             n=CAT[cat]["n"], need=need, tech=tech, TRL=TECH[tech][0])
    d.update(kw)
    return d


def fermenter_moresi(V, closed=True):
    """Fermentador inox de Moresi (f.o.b. 1987) llevado a USD 2024 [C]."""
    return mo.CF(V, closed) * mo.MLIT_TO_USD2024


def design(fruit_t, scen_front=3, wine_to_vinegar=0.16, vinegar_tech="acetador", premium=False,
           include_low_trl=False):
    """Devuelve el diseño por línea: flujos, equipos (con TRL), servicios y personal."""
    b = cp.full_balance(fruit_t, wine_frac_to_vinegar=wine_to_vinegar)
    H_front = cp.calendar_hours("burk") if scen_front == 3 else 7500.0
    H_cont = 365.25 * 0.9 * 24
    L = {}
    # ------------------------------------------------------------------ L1/L2 vino (frente común + bodega)
    f_th = fruit_t / H_front
    juice_m3h = b["juice_m3"] / H_front
    pulp_th = b["pulp_t"] / H_front
    eqs = [
        eq("lav", "lavado_seleccion", f_th, "Recepción, lavado y selección", "Lavado, selección y pelado-descorazonado mecánico"),
        eq("pel", "peladora_descorazonadora", f_th, "Peladora-descorazonadora", "Lavado, selección y pelado-descorazonado mecánico"),
        eq("tri", "trituradora", pulp_th, "Trituradora de pulpa", "Maceración enzimática + prensado"),
        eq("mac", "macerador_camisa", pulp_th * 1.0 / 1.06 * 1.2, "Macerador enzimático con camisa (1 h, 55 °C)", "Maceración enzimática + prensado"),
        eq("pre", "prensa_banda", pulp_th, "Prensa de banda", "Maceración enzimática + prensado"),
        eq("mf", "MF_ceramica", juice_m3h * 1000 / 60.0, "Microfiltración cerámica (60 L/m²·h)", "Microfiltración cerámica tangencial de jugo"),
        eq("pas", "pasteurizador_placas", juice_m3h * 1000, "Pasteurizador flash de mosto", "Pasteurización flash de mosto (HTST)"),
        eq("pul", "tanque_pulmon", b["juice_m3"] / cp.calendar(3)["days"] if hasattr(cp, "calendar") else juice_m3h * 12, "Tanque pulmón de mosto (1 día)", "Fermentación alcohólica en tanques inox con camisa"),
    ]
    # bodega: fermentación continua desde el pulmón (Q = jugo/H_cont)
    Q = b["juice_m3"] / H_cont
    if premium:
        tproc, VF, closed, NF_heat = 120.0, 10.0, False, True
    else:
        tproc, VF, closed, NF_heat = 12.5, 10.0, True, False
    fill = max(1.5, VF / Q); dtc = fill + tproc + 2.5
    NF = math.ceil(Q * dtc / VF)
    ferm = dict(name=f"Fermentador inox {'abierto + intercambiador' if not closed else 'con camisa'} {VF:.0f} m³",
                cat="fermentador_moresi", qty=NF, size=VF, unit="m3", ref_size=VF, ref_USD=fermenter_moresi(VF, closed),
                n=mo._nF, need=Q * dtc, tech="Fermentación alcohólica en tanques inox con camisa", TRL=9,
                note=f"Moresi (1989b): N_F = Q·Δt_c/V_F; Δt_c = llenado {fill:.1f} h + {tproc} h + 2,5 h")
    heat_kW = b["juice_m3"] / H_cont * 1000 * p.S_JUICE / 180.16 * 96.6 / 3600 * (2.0 if not premium else 1.3)
    preco = (Q * 1060 / 3600 * 3.85 * (28 - 15)) if premium else 0.0
    eqs += [ferm,
            eq("prop", "propagador", VF * 0.05, "Propagador / pie de cuba", "Fermentación alcohólica en tanques inox con camisa"),
            eq("chi", "chiller", (heat_kW + preco) * 1.1, "Chiller agua-glicol", "Fermentación alcohólica en tanques inox con camisa"),
            eq("cen", "centrifuga_discos", Q * 1.5, "Centrífuga clarificadora de discos", "Envejecimiento en tanques inox"),
            eq("guar", "tanque_guarda", b["wine_m3"] * 90 / 365 * 1.1, "Tanques de envejecimiento (90 d)", "Envejecimiento en tanques inox"),
            eq("fil", "filtro_cartuchos", Q * 1.5, "Filtración final", "Envejecimiento en tanques inox"),
            eq("cf", "cuarto_frio", 10, "Cuarto frío (levaduras, enzimas)", "Fermentación alcohólica en tanques inox con camisa")]
    if premium:
        eqs.append(dict(name="Intercambiadores de placas (ciclo 15–22 °C)", cat="intercambiador_placas", qty=max(1, math.ceil(NF * 0.2)),
                        size=1, unit="u", ref_size=1, ref_USD=10_000, n=1.0, need=NF * 0.2,
                        tech="Fermentación alcohólica en tanques inox con camisa", TRL=9))
    elec_kWh = (b["fruit_t"] * 8 + b["juice_m3"] * (2 + 1.5) + heat_kW / 3 * H_cont * 0.6 + (preco / 3 * H_cont if premium else 0)
                + b["wine_m3"] * 1.0)
    heat_MJ = b["pulp_t"] * 1000 * 3.9 * (55 - 28) / 1000 * 0.4 + b["juice_m3"] * 1000 * 4.0 * (75 - 28) / 1000 * 0.15   # recuperación 60 % y 85 %
    L["vino_premium" if premium else "vino"] = dict(
        flows=dict(fruit_t=fruit_t, pulp_t=b["pulp_t"], juice_m3=b["juice_m3"], wine_m3=b["wine_m3"], wine_sold_m3=b["wine_sold_m3"]),
        equipment=eqs, elec_kWh=elec_kWh, heat_MJ=heat_MJ, positions=4, calendar=3,
        consumables=dict(pectinasa_kg=b["pulp_t"] * 0.25, levadura_kg=b["juice_m3"] * 0.2 if not premium else b["juice_m3"] * 0.08,
                         membranas_USD=0.15 * pick("MF_ceramica", juice_m3h * 1000 / 60)[2]),
        water_t=fruit_t * 2.0, NF=NF, fill_h=fill)
    # ------------------------------------------------------------------ L3 vinagre
    vin_wine = b["wine_m3"] * wine_to_vinegar
    acid_t = b["vinegar_m3"] * cp.Y["vinegar_acidity"] / 1000
    if vinegar_tech == "acetador":
        Vacet = acid_t * 1000 / (50.0 * 365 * 0.9)
        ve = [eq("acet", "acetador", Vacet * 1.25, "Acetador sumergido", "Acetificación sumergida (acetador tipo Frings/Cetotec)")]
        elec_v = Vacet * 1.25 * 1.2 * H_cont               # aireador ≈ 1,2 kW/m³ [S]
        pos_v = 1
    else:
        Vstat = b["vinegar_m3"] * 30 / 365 * 1.1
        ve = [eq("est", "tanque_estatico", Vstat, "Tanques de acetificación estática (30 d)", "Acetificación estática de superficie")]
        elec_v = Vstat * 0.05 * H_cont
        pos_v = 1
    ve += [eq("tvin", "tanque_guarda", b["vinegar_m3"] * 30 / 365, "Tanques de vinagre (30 d)", "Acetificación sumergida (acetador tipo Frings/Cetotec)"),
           eq("fv", "filtro_cartuchos", b["vinegar_m3"] / H_cont * 2, "Filtración de vinagre", "Acetificación sumergida (acetador tipo Frings/Cetotec)")]
    L["vinagre"] = dict(flows=dict(wine_in_m3=vin_wine, vinegar_m3=b["vinegar_m3"], acid_t=acid_t), equipment=ve,
                        elec_kWh=elec_v, heat_MJ=0.0, positions=pos_v, calendar="continuo", consumables={}, water_t=b["vinegar_m3"] - vin_wine)
    # ------------------------------------------------------------------ L4 bromelaína + polvo
    core_th = b["core_t"] / H_front
    be = [eq("trc", "trituradora", core_th, "Trituradora de corazón", "Bromelaína: extracción, UF y secado por aspersión"),
          eq("prc", "prensa_banda", core_th, "Prensa de corazón", "Bromelaína: extracción, UF y secado por aspersión"),
          eq("cec", "centrifuga_discos", b["core_juice_t"] / H_front, "Centrífuga de jugo de corazón", "Bromelaína: extracción, UF y secado por aspersión"),
          eq("uf", "UF_bromelaina", b["core_juice_t"] * 1000 / H_front / 25.0, "Ultrafiltración 10 kDa (25 L/m²·h)", "Bromelaína: extracción, UF y secado por aspersión"),
          eq("tpr", "tanque_precipitacion", b["core_juice_t"] / H_front * 0.1 * 4, "Tanques de precipitación en frío", "Bromelaína: extracción, UF y secado por aspersión"),
          eq("spd", "spray_dryer", (b["core_juice_t"] * 0.10 + b["powder_t"] * 3) * 1000 / H_front, "Secador por aspersión (bromelaína y polvo)", "Polvo nutracéutico por secado por aspersión"),
          eq("emp", "empacadora", 1, "Empacadora", "Polvo nutracéutico por secado por aspersión"),
          eq("cfb", "cuarto_frio", 10, "Cuarto frío de producto", "Bromelaína: extracción, UF y secado por aspersión")]
    evap_spd = (b["core_juice_t"] * 0.10 + b["powder_t"] * 3) * 1000      # kg agua/año
    L["bromelaina"] = dict(flows=dict(core_t=b["core_t"], bromelain_kg=b["bromelain_kg"], powder_t=b["powder_t"]),
                           equipment=be, elec_kWh=b["core_t"] * 15 + evap_spd * 0.08, heat_MJ=evap_spd * 4.5,
                           positions=2, calendar=3, consumables=dict(membranas_USD=0.2 * pick("UF_bromelaina", b["core_juice_t"] * 1000 / H_front / 25)[2]),
                           water_t=b["core_t"] * 1.0)
    # ------------------------------------------------------------------ L5 harina de cáscara (+ jugo al hub)
    peel_th = b["peel_t"] / H_front
    evap_h = b["water_evap_t"] * 1000 / H_front
    fe = [eq("trp", "trituradora", peel_th, "Trituradora de cáscara", "Harina de fibra de cáscara (prensa + secador de banda + molino)"),
          eq("prp", "prensa_banda", peel_th, "Prensa de tornillo/banda", "Harina de fibra de cáscara (prensa + secador de banda + molino)"),
          eq("sec", "secador_banda", evap_h, "Secador de banda", "Harina de fibra de cáscara (prensa + secador de banda + molino)"),
          eq("mol", "molino_tamiz", b["flour_t"] * 1000 / H_front, "Molino y tamizadora", "Harina de fibra de cáscara (prensa + secador de banda + molino)"),
          eq("emh", "empacadora", 1, "Empacadora", "Harina de fibra de cáscara (prensa + secador de banda + molino)"),
          eq("cal", "caldera", evap_h * 3.2 / 3.6 * 1.1, "Generador de aire caliente / caldera", "Harina de fibra de cáscara (prensa + secador de banda + molino)")]
    L["harina"] = dict(flows=dict(peel_t=b["peel_t"], flour_t=b["flour_t"], peel_juice_t=b["peel_juice_t"], water_evap_t=b["water_evap_t"]),
                       equipment=fe, elec_kWh=b["peel_t"] * 12 + b["flour_t"] * 40, heat_MJ=b["Q_dry_GJ"] * 1000,
                       positions=2, calendar=3, consumables={}, water_t=b["peel_t"] * 1.0)
    # ------------------------------------------------------------------ L6 etanol del jugo de cáscara
    sugar_t = b["peel_juice_t"] * 0.104                                     # 110 g/L ≈ 104 g/kg [S]
    eth_kg = sugar_t * 1000 * 0.46 * 0.95
    eth_L = eth_kg / 0.789 / 0.95                                           # hidratado 95 % v/v
    Qe = b["peel_juice_t"] / 1.05 / H_cont
    VFe = 10.0; dtce = max(1.5, VFe / Qe) + 30 + 2.5
    ee = [dict(name="Fermentador inox 10 m³ (etanol)", cat="fermentador_moresi", qty=math.ceil(Qe * dtce / VFe), size=VFe, unit="m3",
               ref_size=VFe, ref_USD=fermenter_moresi(VFe, True), n=mo._nF, need=Qe * dtce, tech="Etanol hidratado: fermentación + destilación", TRL=9),
          eq("cee", "centrifuga_discos", Qe, "Centrífuga", "Etanol hidratado: fermentación + destilación"),
          eq("col", "columna_destilacion", eth_L / H_cont, "Columna de destilación + condensador + rehervidor", "Etanol hidratado: fermentación + destilación"),
          eq("tet", "tanque_guarda", eth_L / 1000 * 30 / 365 + 5, "Tanque de etanol", "Etanol hidratado: fermentación + destilación")]
    L["etanol"] = dict(flows=dict(peel_juice_t=b["peel_juice_t"], sugar_t=sugar_t, ethanol_L=eth_L), equipment=ee,
                       elec_kWh=b["peel_juice_t"] * 4, heat_MJ=eth_kg * 3.0 * 2.257 * 1.2, positions=1, calendar="continuo",
                       consumables=dict(levadura_kg=b["peel_juice_t"] * 0.2), water_t=b["peel_juice_t"] * 0.2)
    # ------------------------------------------------------------------ L7 isla energética (corona)
    Pkw = b["E_el_MWh"] * 1000 / H_cont
    ge = [eq("ast", "astilladora_secador_biomasa", b["crown_t"] / H_front, "Picadora y secador de corona", "Gasificación downdraft + motor (≤ 100 kWe)"),
          eq("gas", "gasificador_MCI", Pkw * 1.15, "Gasificador downdraft + motor-generador", "Gasificación downdraft + motor (≤ 100 kWe)")]
    L["energia"] = dict(flows=dict(crown_t=b["crown_t"], gas_dm_t=b["gas_dm_t"], E_el_MWh=b["E_el_MWh"], Q_th_GJ=b["Q_th_GJ"], P_kW=Pkw),
                        equipment=ge, elec_kWh=b["crown_t"] * 10, heat_MJ=0.0, positions=1, calendar="continuo", consumables={}, water_t=0.0)
    trl = {k: min(e["TRL"] for e in v["equipment"]) for k, v in L.items()}
    return dict(balance=b, lines=L, TRL=trl, H_front=H_front, H_cont=H_cont)


if __name__ == "__main__":
    W = p.WINE_VOL_YR
    fruit = cp.fruit_for_wine(W)[0]
    D = design(fruit)
    for k, v in D["lines"].items():
        print("==", k, "TRL min", D["TRL"][k], {a: round(b, 1) for a, b in v["flows"].items()})
        for e in v["equipment"]:
            print("   ", e["qty"], "×", e["name"], e["size"], e["unit"], "(nec.", round(e["need"], 2), ") TRL", e["TRL"])
