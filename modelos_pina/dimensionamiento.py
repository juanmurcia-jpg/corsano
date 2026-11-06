"""
Dimensionamiento óptimo de equipos acoplado al programa anual con estacionalidad (diseño + operación simultáneos).

Idea: el tamaño de cada equipo no se fija por el flujo medio de diseño (planta_trl9.py) sino que lo elige un MILP
que, al mismo tiempo, programa la operación de todo el año en tiempo continuo (el modelo de anual_continuo.py).
Así los flujos quedan balanceados: ningún equipo sobra mientras otro topa la producción.

Formulación (referencias):
  - Grossmann (2021), cap. 10: elección de un tamaño de catálogo por equipo como disyunción
        ∨_s [ y_us ;  cap_u = cap_us ;  costo_u = C_us ]  ,  Σ_s y_us = 1
    con su envolvente convexa; el producto «tamaño × horas disponibles» se linealiza de forma exacta
    (variable 0-1 × continua acotada, Glover 1975; Grossmann cap. 7.3).
  - Grossmann (2021), cap. 14: versión estocástica en dos etapas: tamaños en la primera etapa (aquí y ahora),
    operación anual en la segunda etapa por escenario de oferta.
  - Maravelias (2021), cap. 7.3, 8.2, 9.3.2 y 10: rejilla continua anclada a los meses, procesos continuos con
    tasa ≤ capacidad, prensa en tiempo compartido con limpiezas σ, inventarios con capacidad y programa periódico.
  - Moresi (1989b): N_F = Q·Δt_c/V_F con Δt_c = V_F/Q + t_proc  ⇒  Q ≤ (N_F − 1)·V_F/t_proc (lineal en N_F):
    mientras un fermentador se llena, los demás fermentan.
  - Burk (estructura de los TEA de asaí y coco): costo de compra -> FCI con el factor equivalente de Lang del
    motor tea_burk.py; cargo anual = FCI·(CRF + mantenimiento + impuestos locales).

Decisiones de diseño (todas discretas, del catálogo de planta_trl9.CAT):
  frente (lavado + peladoras), prensa principal (pulpa y, si se comparte, cáscara/corazón), prensa dedicada de
  cáscara (0 = no hay), MF + pasteurizador, bodega (N_F fermentadores de 10 m³ + chiller + centrífuga),
  secador de banda + caldera + molino, almacenamiento aséptico de mosto (nivela meses pico y valle),
  tercer turno en el frente (alternativa operativa a comprar equipo), y en la configuración B, módulo de bromelaína
  (aspersión + UF + centrífuga) y prensa dedicada de corazón.
"""
import json, os, math, sys, copy, time
import numpy as np
from pyscipopt import Model, quicksum
import capacidad as cp
import planta_trl9 as pt
import planificacion_milp as pm
import tea_burk as tb
import tea_lineas as tl
import params as p
import moresi as mo
import datos as DT

RES = os.path.join(os.path.dirname(__file__), "results")
DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
HM = DAYS * 24.0
A2 = cp.calendar_hours("burk") / 8766.0          # lun–sáb, 2 turnos de 6 h efectivas
A3 = 1.5 * A2                                     # con tercer turno
AC = 0.9                                          # procesos continuos (bodega, secador)
C = tb.COMMON
CRF = C["tasa"] * (1 + C["tasa"]) ** C["anios"] / ((1 + C["tasa"]) ** C["anios"] - 1)
VF, T_PROC = 10.0, 12.5 + 2.5                     # fermentador de 10 m³; fermentación + descarga/limpieza (h)
SUPPLY = 6146.0                                    # EVA 2022, Chocó
WINE_PRICE = 3000.0                                # COP/L (plan del MILP y moda del programa estocástico)
FRUIT_PRICE = 400.0                                # COP/kg puesto en planta (TEA)
COMPOST = pm.COMPOST_COP_kg
CH_COST = 2e4                                      # COP por cambio de material en la prensa (aguas, CIP corto)
SIGMA = 1.0                                        # h de limpieza por cambio


# ----------------------------------------------------------------------------- costos de las opciones
def _lang():
    D = pt.design(6200)
    x = tb.capex(tl.to_equipment(D["lines"]["vino"]["equipment"] + D["lines"]["harina"]["equipment"]))
    return x["FCI"] / x["purchase"]


LANG = _lang()
AF = LANG * (CRF + C["mantenimiento"] + C["impuestos_locales"])     # COP/año por COP de compra


def buy(cat, need):
    """Costo de compra (COP base) de la combinación de catálogo más barata que cubre 'need'."""
    if need <= 0:
        return 0.0
    n, s, _ = pt.pick(cat, need)
    k = pt.CAT[cat]
    return tb.equipment_cost(dict(qty=n, size=s, ref_size=k["ref"][0], ref_USD=k["ref"][1], n=k["n"]))[0]


FIXED_EQ_COST = None   # se calcula tras definir buy(): generador de N2 + dosificador de nutrientes


def ferm_cost(n):
    return tb.equipment_cost(dict(qty=n, size=VF, ref_size=VF, ref_USD=pt.fermenter_moresi(VF, True), n=1.0))[0]


FIXED_EQ_COST = buy("generador_N2", 1) + buy("dosificador_nutrientes", 1)
_Dref = pt.design(6200)
Q_CAKE = _Dref["lines"]["harina"]["heat_MJ"] / (_Dref["lines"]["harina"]["flows"]["peel_t"] * (1 - cp.Y["peel_juice_frac"]))   # MJ/t de torta
B1 = cp.full_balance(1.0)
FR = dict(pulpa=B1["pulp_t"], cascara=B1["peel_t"], corazon=B1["core_t"])
JUICE = cp.JUICE_YIELD_PULP / cp.RHO_JUICE                 # m³ jugo / t pulpa
CAKE = 1 - cp.Y["peel_juice_frac"]                         # t torta / t cáscara
CORE_J = cp.Y["core_juice_frac"]
FLOUR_PC = (B1["flour_t"] / B1["peel_t"]) / CAKE           # t harina / t torta
WINE_PM = 1 - cp.WINE_LOSS                                 # m³ vino / m³ mosto
HEAT_KW_PER_M3H = 1000 * p.S_JUICE / 180.16 * 96.6 / 3600 * 2.0
# ---- superestructura ampliada (White Wine Technology, Morata ed. 2022): costos variables por unidad de flujo   [S]
E_COP, H_COP = C["elec_COP_kWh"], C["calor_COP_MJ"]
HTST_VC = 1000 * 4.0 * (75 - 28) / 1000 * 0.15 * H_COP     # COP/m³: calentar a 75 °C con 85 % de regeneración
SO2_VC = 1_500.0                                            # COP/m³: metabisulfito ≈ 0,1 kg/m³ (≈ 50 mg/L de SO2)
UHPH_VC = 100.0 * E_COP                                     # COP/m³: trabajo de compresión a 300 MPa ≈ 0,083 kWh/L / η 0,83
FLOT_VC = 1_500.0 + 1.0 * E_COP                             # COP/m³: coadyuvantes de clarificación + bomba presurizadora
CENT_VC = 2.0 * E_COP                                       # COP/m³: centrífuga de discos
DEC_VC = 4.5 * E_COP                                        # COP/t pulpa: decantadora frente a prensa de banda (+4,5 kWh/t)
LEES_MF_VC = 1.0 * E_COP                                    # COP/m³ de lías filtradas
LEES_DISP = 30.0 * 1000                                     # COP/m³ de lías a compostaje
LEES_REC = 0.60                                             # v7: jugo recuperable de lodos de piña (SIS 10,5 % m/m, Quesada Salas 2013) [S]
# ---- v7: calibración con Quesada Salas (2013), MFT de jugo pulposo de piña en planta piloto
MF_FLUX = 45.0                                              # L/m²·h sostenido (40–50 en ensayos de 6 h, FRV 3,7)
MF_LOSS = 0.27                                              # retenido: rendimiento de jugo clarificado 73 % (FRV 3,7)
CENT_LOSS, FLOT_LOSS = 0.12, 0.18                           # lodos y espumas con SIS 10,5 % m/m (uva: 2–15 %) [S]
LEES_FLOUR = 0.11                                           # t harina / t lías o retenido (≈ 10 % de sólidos, harina al 10 % de humedad) [S]
DRY_W = 1 - FLOUR_PC                                       # t de agua evaporada por t de torta (v9: 0,81; v8: 0,77)
LEES_DRY_EQ = (1 - LEES_FLOUR) / DRY_W                     # carga del secador por t de lías, en t de torta equivalentes
# ---- v7: vinagre (Emde 2017, Ullmann's Food and Feed: acetificador Frings; Bekatorou 2020)
ACET_PROD = 50.0                                            # kg ácido acético/(m³·d): 40–60 en acetificadores Frings
ACET_YIELD = 0.94                                           # fracción del rendimiento teórico (46 g etanol -> 60 g ácido)
ACID_HEAT = 493.0 / 60.0                                    # MJ/kg ácido (ΔH = −493 kJ/mol)
AERATION_KW_M3 = 1.2                                        # kW por m³ de acetificador (turbina autoaspirante, 0,1–0,15 vvm) [S]
VIN_ACID = 50.0                                             # kg/m³ (vinagre al 5 %)
A_WINE = 65.4 * 60 / 46 * ACET_YIELD                        # kg ácido / m³ de vino (≈ 8,3 % v/v de etanol)
PJ_SUGAR = 104.0                                           # g de azúcares fermentables / kg de jugo de cáscara (Seguí y Fito 2018: 103 ± 15 g/L)
PJ_ETOH = 0.36                                             # v9: g etanol / g azúcar en fermentación directa del jugo (Seguí y Fito 2018, tabla 2,
                                                           #     S. bayanus); rango 0,23–0,43; v8: 0,46·0,95 = 0,437
A_PJ = PJ_SUGAR * PJ_ETOH * 60 / 46 * ACET_YIELD           # kg ácido / t de jugo de cáscara (v9: 45,9; v8: 55,7)
A_PJ_RANGE = tuple(PJ_SUGAR * e * 60 / 46 * ACET_YIELD for e in (0.23, 0.36, 0.43))
T_PEEL = DT.val("t_proc_jugo_cascara")                      # h: fermentación + descarga. v10: cinética de Krishnan calibrada
                                                            #     (cinetica_jugos.py) = 12,6 h; v9 suponía 30 + 2,5 h
VIN_PRICE = tl.M("vinagre_L")
DAP_VC = 0.2 * 8_000.0                                      # COP/m³ de mosto: 200 mg/L de fosfato diamónico (YAN < 140 mg/L)
N2_VC = 0.5 * E_COP                                         # COP/m³ de vino: generador PSA de N2 para inertizar tanques
PJ_VC = 0.2 * 60_000 + DAP_VC + SO2_VC                      # COP/t jugo de cáscara: levadura + nutrientes + SO₂ (v9: el jugo sin tratar
                                                           #     se contamina con bacterias acéticas, Seguí y Fito 2018)
VIN_VC = ACID_HEAT / 3.6 / 4.0 * E_COP + 500.0              # COP/kg ácido: frío con COP 4 (trópico) + nutrientes y filtración [S]
ALLOW_OLD = {"Decantadora": ["no"], "Clarificación": ["MF"], "MF lías": ["no"], "Estabilización": ["HTST"], "Caldera de corona": ["no"],
             "Acetificador": ["no"], "Bodega cáscara": ["no"], "Pretratamiento cáscara": ["agua"], "Enzima cáscara": ["no"],
             "Extractora hojas": ["no"], "Bodega etanol": ["no"], "Destilación": ["no"], "Digestor": ["no"], "Motor biogás": ["no"],
             "Ácido cítrico": ["no"], "Xantana": ["no"]}   # topología v5
NO_V9 = {"Pretratamiento cáscara": ["agua"], "Enzima cáscara": ["no"]}     # v9 sin sus opciones nuevas
NO_LIME = {"Pretratamiento cáscara": ["agua"]}
NO_ENZ = {"Enzima cáscara": ["no"]}
NO_SO2 = {"Estabilización": ["HTST", "UHPH"]}
NO_VIN = {"Acetificador": ["no"], "Bodega cáscara": ["no"]}
NO_BOILER = {"Caldera de corona": ["no"]}
# ---- v8: caldera de biomasa con corona (línea L7b del TEA, TRL 9)
CROWN_MJ_T = cp.Y["crown_dm"] * 17_000.0 * 0.80             # MJ útiles por t de corona (20 % MS, 17 MJ/kg, caldera al 80 %)
CROWN_VC = 10.0 * E_COP                                     # COP/t de corona: picado y secado (10 kWh/t)
Q_MAC = 3.9 * (55 - 28) * 0.4                               # MJ/t de pulpa: maceración a 55 °C con 60 % de recuperación
HEAT_COP = C["calor_COP_MJ"]                                # COP/MJ útil con GLP (caldera al 85 %, plantilla)
# ---- v9: Seguí y Fito (2018, J. Clean. Prod. 172:1224) y Campos et al. (2020, Foods 9:60)
PJ_FRAC = {"agua": cp.Y["peel_juice_frac"], "cal 0,1 %": 0.684 * 0.95}   # t de jugo (equivalente en azúcar) / t de cáscara:
                                                           #     extractora 0,578 (Campos); con Ca(OH)₂ al 0,1 % 0,684 (Seguí), 5 % de dilución [S]
CAKE_FRAC = {"agua": 1 - cp.Y["peel_juice_frac"], "cal 0,1 %": 1 - 0.684}  # t de torta / t de cáscara (misma MS de la torta, 17 %)
LIME_VC = 1.0 * 1_500.0 + 1.0 * E_COP                      # COP/t de cáscara: 1 kg de Ca(OH)₂ + mezcla [S]
ENZ_Y = 0.45 / cp.Y["peel_juice_frac"]                     # kg de enzima cruda seca / t de jugo de cáscara: 0,26 % de la cáscara en
                                                           #     fracción húmeda con 17,2 % de MS (Campos 2020, fig. 1) = 0,45 kg/t cáscara
ENZ_GAIN = 0.10                                            # aumento del etanol del jugo sin proteasas: Seguí mide +25 % (30 ± 5 frente a
                                                           #     23,9 g/L); se toma 10 % por la dispersión [S]
BROM_PRICE = tl.M("bromelaina_kg")                         # COP/kg de bromelaína cruda grado alimentario (≈ 1 200 GDU/g) [S]
ENZ_TECH = {   # separación de la enzima del jugo de cáscara antes de fermentarlo
    "Precipitación": dict(pf=1.0, sl=0.01, wet=ENZ_Y / 0.172,                 # precipitación con polisacárido, sin solventes (Campos 2020)
                          vc=30_000.0 + 2.0 * E_COP + ENZ_Y / 0.172 * 0.83 * 1.5 * E_COP),   # polisacárido [S], centrífuga, liofilización 1,5 kWh/kg
    "UF": dict(pf=0.5, sl=0.05, wet=50.0,                                       # UF 10 kDa con FCV 20 (Seguí 2018): 340–805 GDU/g frente a
               vc=3.0 * E_COP + 2_000.0 + 50.0 * 0.95 * 1.5 * E_COP),          #     1 400–2 800 de la comercial → pf 0,5; liofilizar 50 kg/t
}
# ---- v10: residuos de planta (Chen et al. 2020; Liao et al. 2022 y 2026), hub (SuperPro) y balances de energía y GWP
HOJAS_SUPPLY = DT.val("area_sembrada_ha") * DT.val("hojas_t_ha_ano") * DT.val("frac_acopio_hojas")   # t/año que se pueden acopiar
JF_H, PF_H = DT.val("jugo_hojas_frac"), DT.val("pulpa_hojas_frac")             # t jugo y t pulpa húmeda / t hojas
ACOPIO_VC = DT.val("costo_acopio_hojas")                                    # COP/t de hojas puestas en planta
T_LEAF = DT.val("t_proc_jugo_hojas")                                        # h por lote de jugo de hojas (12 h + descarga)
E_LJ = DT.val("etanol_jugo_hojas")                                          # kg etanol / t jugo de hojas
YEAST_LJ = DT.val("levadura_jugo_hojas")                                    # kg levadura seca / t jugo
L_PER_KG = 1 / 0.789 / 0.95                                                 # L de etanol hidratado (95 % v/v) por kg de etanol
ETOH_PRICE, YEAST_PRICE = DT.val("precio_etanol_L"), DT.val("precio_levadura_seca")
ETOH_VC = 0.2 * 60_000.0                                                    # COP/t jugo: inóculo (planta_trl9, línea L6)
Q_DEST = DT.val("vapor_destilacion") * 2.257 * 1.2                          # MJ/kg etanol
A_LJ = E_LJ * 60 / 46 * ACET_YIELD                                          # kg ácido / t jugo de hojas por la ruta del vinagre
CH4_T = DT.val("biogas_jugo_hojas") * DT.val("ch4_biogas") * 0.717          # kg CH4 / t jugo digerido
CH4_MJ = CH4_T * 50.0                                                       # MJ (PCI) / t jugo
ETA_EL_B, ETA_TH_B = DT.val("eta_el_biogas"), DT.val("eta_th_biogas")
Q_AD = DT.val("calor_digestor")                                             # MJ/t jugo para mantener 35 °C
BIO_OM = 80.0                                                               # COP/kWh de operación del motor a biogás [S]
VAL_EXC = DT.val("valor_excedente_elec")                                    # COP/kWh de excedente a la red local
MS_P = DT.val("ms_pulpa_hojas")
PULP_MJ_T = (MS_P * DT.val("hhv_pulpa_hojas") - 2.44 * (1 - MS_P) - 1.3 * MS_P) * 1000 * 0.80   # MJ útiles / t pulpa húmeda
KWH_LEAF = dict(ext=DT.val("elec_extraccion_hojas"), etoh=DT.val("elec_etanol"), ad=DT.val("elec_digestor"), pulp=10.0)
HUB = {   # ácido cítrico y goma xantana a partir del jugo de cáscara (ejemplos de SuperPro)
    "Ácido cítrico": dict(y=DT.val("y_citrico"), tci=DT.val("tci_citrico_ref"), cap=DT.val("cap_citrico_ref"), vc=DT.val("vc_citrico") * DT.val("TRM"),
                          price=DT.val("precio_citrico")),
    "Xantana": dict(y=DT.val("y_xantana"), tci=DT.val("tci_xantana_ref"), cap=DT.val("cap_xantana_ref"), vc=DT.val("vc_xantana") * DT.val("TRM"),
                    price=DT.val("precio_xantana")),
}
# ---- v10: coeficientes de electricidad (kWh) y de GWP (kg CO2e) por unidad de flujo, para el balance y el ε-restricción
_V = pt.design(6200)["lines"]["vino"]; _B = cp.full_balance(6200.0)
KWH = dict(fruit=8 * 1.3, bod=1.3 * (_V["elec_kWh"] - 6200 * 8) / _B["juice_m3"] + 0.5 * (1 - cp.WINE_LOSS), peel=12 * 1.3,
           flour=40 * 1.3, crown=10.0, lees_mf=1.0, dec=4.5)
KWH_CLAR = {"MF": 0.0, "Flotación": 1.0, "Centrífuga": 2.0}
EF_KWH = DT.val("ef_diesel") / (DT.val("pci_diesel") * DT.val("eta_grupo_diesel") / 3.6)   # kg CO2e por kWh del grupo diésel
EF_GLP_UTIL = DT.val("ef_glp") / DT.val("eta_caldera_glp")                                   # kg CO2e por MJ útil de GLP
EF_BIO_FUEL = (DT.val("ef_caldera_bio_ch4") * DT.val("gwp_ch4") + DT.val("ef_caldera_bio_n2o") * DT.val("gwp_n2o")) / 1000 / 0.80   # por MJ útil
EF_COMP = (DT.val("compost_ch4") * DT.val("gwp_ch4") + DT.val("compost_n2o") * DT.val("gwp_n2o"))          # kg CO2e / t húmeda compostada
EF_LEAK = DT.val("fuga_ch4_biogas") * DT.val("gwp_ch4")                                      # por kg de CH4 producido
EF_ACOPIO = DT.val("diesel_acopio_hojas") / DT.val("pci_diesel") * DT.val("ef_diesel")       # kg CO2e / t hojas acopiadas
EF_FRUIT_T = DT.val("dist_fruta_km") * DT.val("ef_transporte")                               # kg CO2e / t fruta transportada
EF_CHEM = dict(dap=0.2 * DT.val("ef_dap"), so2=0.1 * DT.val("ef_metabisulfito"), yeast=0.2 * DT.val("ef_levadura"),
               lime=1.0 * DT.val("ef_cal"), pect=DT.val("ef_enzima") * _V["consumables"]["pectinasa_kg"] / _B["pulp_t"])
BLEND = True                                                                # v10: restricción de mezcla del vinagre (solo diluir)
NO_LEAVES = {"Extractora hojas": ["no"]}
NO_AD = {"Digestor": ["no"], "Motor biogás": ["no"]}
NO_ETOH = {"Bodega etanol": ["no"], "Destilación": ["no"]}
NO_HUB = {"Ácido cítrico": ["no"], "Xantana": ["no"]}
NO_V10 = dict(NO_LEAVES, **NO_AD, **NO_ETOH, **NO_HUB)



def options(with_bromelain=False):
    """Opciones discretas por equipo: lista de dict(lab, cap, cost[COP compra]). cap en la unidad de flujo del equipo."""
    O = {}
    O["Frente"] = [dict(lab=f"{s:g} t/h", cap=s, cost=buy("lavado_seleccion", s) + buy("peladora_descorazonadora", s))
                   for s in (1, 2, 3, 5, 8)]
    O["Prensa"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{s:g} t/h", cap=s, cost=buy("prensa_banda", s) + buy("trituradora", s) + buy("macerador_camisa", s / 1.06 * 1.2))
        for s in (1, 2, 3, 5, 8)]
    O["Decantadora"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{s:g} t/h", cap=s, cost=buy("decantadora", s) + buy("trituradora", s) + buy("macerador_camisa", s / 1.06 * 1.2))
        for s in (1, 2, 3, 5)]
    O["Prensa cáscara"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{s:g} t/h", cap=s, cost=buy("prensa_banda", s) + buy("trituradora", s)) for s in (1, 2, 3)]
    O["Clarificación"] = (
        [dict(lab=f"MF {A:g} m²", cap=A * MF_FLUX / 1000, cost=buy("MF_ceramica", A), loss=MF_LOSS, vc=0.0, fixed=0.15 * buy("MF_ceramica", A), ret=True)
         for A in (10, 20, 30, 40, 60, 80)]
        + [dict(lab=f"Flotación {q:g} m³/h", cap=q, cost=buy("flotador_mosto", q), loss=FLOT_LOSS, vc=FLOT_VC) for q in (0.5, 1, 2, 4)]
        + [dict(lab=f"Centrífuga {q:g} m³/h", cap=q, cost=buy("centrifuga_discos", q), loss=CENT_LOSS, vc=CENT_VC) for q in (0.5, 1, 2, 3, 5)])
    O["MF lías"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{A:g} m²", cap=A * 30 / 1000, cost=buy("MF_lias", A), fixed=0.15 * buy("MF_lias", A)) for A in (2, 5, 10)]
    O["Estabilización"] = (
        [dict(lab=f"HTST {L} L/h", cap=L / 1000, cost=buy("pasteurizador_placas", L), vc=HTST_VC) for L in (500, 1000, 2000, 3000)]
        + [dict(lab="SO₂", cap=50.0, cost=buy("dosificador_SO2", 1), vc=SO2_VC)]
        + [dict(lab=f"UHPH {L} L/h", cap=L / 1000, cost=buy("UHPH", L), vc=UHPH_VC) for L in (500, 1000, 2000)])
    O["Bodega"] = [dict(lab=f"{n}×10 m³", cap=(n - 1) * VF / T_PROC,
                        cost=ferm_cost(n) + buy("chiller", (n - 1) * VF / T_PROC * HEAT_KW_PER_M3H * 1.1)
                        + buy("centrifuga_discos", (n - 1) * VF / T_PROC * 1.5) + buy("filtro_cartuchos", (n - 1) * VF / T_PROC * 1.5)
                        + buy("propagador", 0.5))
                   for n in range(2, 13)]
    O["Secador"] = [dict(lab=f"{s:g} kg agua/h", cap=s / 1000 / DRY_W,
                         cost=buy("secador_banda", s) + buy("caldera", s * 3.2 / 3.6 * 1.1) + buy("molino_tamiz", s / 1000 / DRY_W * FLOUR_PC * 1000))
                    for s in (50, 100, 200, 300, 500, 800)]
    O["Bodega cáscara"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{n}×10 m³", cap=(n - 1) * VF / T_PEEL, cost=ferm_cost(n) + buy("chiller", (n - 1) * VF / T_PEEL * HEAT_KW_PER_M3H * 1.1))
        for n in (2, 3, 4, 6, 8)]
    O["Acetificador"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{V:g} m³", cap=V * ACET_PROD / 24.0,
             cost=(buy("acetador", V) + buy("chiller", V * ACET_PROD / 24.0 * ACID_HEAT / 3.6 * 1.1)
                   + buy("grupo_electrogeno", AERATION_KW_M3 * V * 1.25 + V * ACET_PROD / 24.0 * ACID_HEAT / 3.6 / 4.0)
                   + buy("centrifuga_espuma", 1) + buy("lavador_gases", 1) + buy("MF_vinagre", V * ACET_PROD / 24.0 / VIN_ACID * 1000 / 100.0)),
             fixed=AERATION_KW_M3 * V * 0.9 * 8766 * E_COP)
        for V in (2, 4, 6, 10, 20, 40)]
    O["Caldera de corona"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{q} kWt", cap=q * 3.6, cost=1.3 * buy("caldera", q) + buy("astilladora_secador_biomasa", q * 3.6 / CROWN_MJ_T))
        for q in (100, 200, 300, 500)]
    O["Pretratamiento cáscara"] = [dict(lab="agua", cap=0.0, cost=0.0),
                                   dict(lab="cal 0,1 %", cap=0.0, cost=buy("mezclador_cal", 2) + buy("dosificador_nutrientes", 1))]
    op1 = tb.payroll(1, tb.calendar(3), engineer=0)["total"] * (1 + C["supervision"])        # un operario por turno
    O["Enzima cáscara"] = [dict(lab="no", cap=0.0, cost=0.0)]
    for q in (0.25, 0.5, 1):
        O["Enzima cáscara"].append(dict(lab=f"Precipitación {q:g} t/h", cap=q, tech="Precipitación", fixed=op1,
                                        cost=2 * buy("tanque_precipitacion", q) + buy("centrifuga_discos", q)
                                        + buy("liofilizador", q * 12 * ENZ_TECH["Precipitación"]["wet"] * 0.83)))
        O["Enzima cáscara"].append(dict(lab=f"UF {q:g} t/h", cap=q, tech="UF", fixed=op1 + 0.2 * buy("UF_bromelaina", q * 1000 / 25),
                                        cost=buy("centrifuga_discos", q) + buy("UF_bromelaina", q * 1000 / 25)
                                        + buy("liofilizador", q * 12 * ENZ_TECH["UF"]["wet"] * 0.95)))
    # ---- v10: residuos de planta, etanol, digestión anaerobia y productos del hub
    O["Extractora hojas"] = [dict(lab="no", cap=0.0, cost=0.0)] + [dict(lab=f"{s:g} t/h", cap=s, cost=buy("extrusora_hojas", s)) for s in (2, 5, 10, 20, 40, 60)]
    O["Bodega etanol"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{n}×10 m³", cap=(n - 1) * VF / T_LEAF * 1.02, cost=ferm_cost(n) + buy("centrifuga_discos", (n - 1) * VF / T_LEAF))
        for n in (2, 3, 4, 6, 8, 10, 12, 16, 20, 24)]                       # cap en t de jugo de hojas por hora (Moresi)
    O["Destilación"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{s:g} L/h", cap=s / L_PER_KG, cost=buy("columna_destilacion", s)) for s in (10, 25, 50, 100, 200, 400)]   # cap en kg etanol/h
    O["Digestor"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
        dict(lab=f"{V:g} m³", cap=V / (DT.val("trh_digestor") * 24) / 1.1, cost=buy("digestor_anaerobio", V)) for V in (250, 500, 1000, 2000, 4000, 8000)]
    O["Motor biogás"] = [dict(lab="no", cap=0.0, cost=0.0)] + [dict(lab=f"{q:g} kWe", cap=q, cost=buy("motor_biogas", q)) for q in (50, 100, 200, 400, 800)]
    for prod, sizes in (("Ácido cítrico", (5, 10, 25, 50, 100)), ("Xantana", (2, 5, 10, 25))):
        H_ = HUB[prod]; ref_kgh = H_["cap"] * 1000 / (AC * 8766)
        O[prod] = [dict(lab="no", cap=0.0, cost=0.0)] + [
            dict(lab=f"{s:g} kg/h", cap=s, cost=H_["tci"] / LANG * C["TRM"] * (s / ref_kgh) ** 0.6) for s in sizes]   # compra equivalente = TCI/Lang [S]
    O["Almacén de mosto"] = [dict(lab=f"{V:g} m³", cap=V, cost=(buy("tanque_pulmon", V) if V <= 50 else 1.4 * buy("tanque_guarda", V)))
                             for V in (10, 25, 50, 100, 200, 400, 800)]
    if with_bromelain:
        O["Aspersión"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
            dict(lab=f"{s:g} kg agua/h", cap=s / 1000 / 0.12,
                 cost=buy("spray_dryer", s) + buy("UF_bromelaina", s / 0.12 / 25) + buy("centrifuga_discos", s / 1000 / 0.12)
                 + buy("tanque_precipitacion", s / 1000 / 0.12 * 0.4) + buy("cuarto_frio", 10))
            for s in (5, 10, 25, 50)]
        O["Prensa corazón"] = [dict(lab="no", cap=0.0, cost=0.0)] + [
            dict(lab=f"{s:g} t/h", cap=s, cost=buy("prensa_banda", s) + buy("trituradora", s)) for s in (1, 2)]
    return O


REFERENCE = {   # diseño TRL-9 a 6 200 t/año (planta_trl9.design): lavado 2 t/h, prensa de pulpa 1 t/h + prensa de cáscara 1 t/h,
    "Frente": "2 t/h", "Prensa": "1 t/h", "Prensa cáscara": "1 t/h", "Decantadora": "no", "Clarificación": "MF 20 m²",
    "MF lías": "no", "Estabilización": "HTST 1000 L/h", "Bodega": "2×10 m³", "Acetificador": "no", "Bodega cáscara": "no", "Caldera de corona": "no",
    "Secador": "300 kg agua/h", "Almacén de mosto": "10 m³", "Pretratamiento cáscara": "agua", "Enzima cáscara": "no",
    "Extractora hojas": "no", "Bodega etanol": "no", "Destilación": "no", "Digestor": "no", "Motor biogás": "no", "Ácido cítrico": "no", "Xantana": "no", "turno3": 0,                                    # secador 300, pulmón 10 m³
}
REFERENCE_B = dict(REFERENCE, **{"Aspersión": "10 kg agua/h", "Prensa corazón": "1 t/h"})


def margins(wine_price=WINE_PRICE, flour_price=None, vinegar_price=None):
    """Márgenes de contribución por unidad de flujo (COP), del TEA de cada línea a 6 200 t/año."""
    D = pt.design(6200)
    cs = tl.cases_from_design(D)
    def var_noraw(key):
        c = cs[key]; r = tb.evaluate(c)
        return r["var"] - sum(rr["qty_year"] * rr["price"] for rr in c["raw"] if rr.get("main"))
    jm = D["lines"]["vino"]["flows"]["juice_m3"]
    membr = D["lines"]["vino"]["consumables"]["membranas_USD"] * tl.TRM
    v_w = (var_noraw("L1 Vino de piña (rápido, 30 °C)") - membr - jm * HTST_VC) / jm + DAP_VC + N2_VC * WINE_PM   # COP/m³ mosto
    v_h = var_noraw("L5 Harina de fibra de cáscara") / (D["lines"]["harina"]["flows"]["peel_t"] * CAKE)       # COP/t torta
    v_b = var_noraw("L4 Bromelaína + polvo nutracéutico") / (D["lines"]["bromelaina"]["flows"]["core_t"] * CORE_J)   # COP/t jugo de corazón
    fp = flour_price or tl.M("harina_kg")
    global VIN_PRICE
    VIN_PRICE = vinegar_price or tl.M("vinagre_L")
    brom_rev = (B1["bromelain_kg"] * tl.M("bromelaina_kg") + B1["powder_t"] * 1000 * 40000.0) / (B1["core_t"] * CORE_J)
    return dict(
        wine=C["vendido"] * wine_price * 1000 * WINE_PM - v_w,
        flour=C["vendido"] * fp * 1000 * FLOUR_PC - v_h,
        brom=C["vendido"] * brom_rev - v_b,
        peel_juice=cp.Y["peel_juice_frac"] * 150.0 * 1000,          # crédito del jugo de cáscara al hub, por t de cáscara prensada
        flour_t=C["vendido"] * fp * 1000 - v_h / FLOUR_PC,          # COP por t de harina (para la harina de lías y retenidos)
        v_cake=v_h,                                                 # COP por t de torta secada
        wine_m3=C["vendido"] * wine_price * 1000,                   # ingreso por m³ de vino vendido
        vin_kg=C["vendido"] * VIN_PRICE * 1000 / VIN_ACID,          # ingreso por kg de ácido vendido como vinagre al 5 %
        vin_tank=AF * buy("tanque_guarda", 100) / 100 * 30 / 365 * 1.1 / VIN_ACID,   # tanques de vinagre (30 d), por kg de ácido/año
        guard=AF * buy("tanque_guarda", 160) / 160 * 90 / 365 * 1.1,  # tanques de guarda (90 d), COP/año por m³ de vino/año
    )


def shift_cost(with_bromelain=False):
    pos = 4 + 2 + (2 if with_bromelain else 0)
    c2 = tb.calendar(3); c3 = dict(c2, shifts=3)
    return (tb.payroll(pos, c3, engineer=0)["total"] - tb.payroll(pos, c2, engineer=0)["total"]) * (1 + C["supervision"])


# ----------------------------------------------------------------------------- modelo
def build(scen, K=2, with_bromelain=False, fix=None, loss_max=None, allow_shift=True, mg=None, store_max=None, allow=None,
          gwp_max=None, objective="margin"):
    """scen: lista de dict(sup=factor de oferta, p=probabilidad). Devuelve (modelo, variables)."""
    O = options(with_bromelain)
    mg = mg or margins()
    modes = ["pulpa", "cascara"] + (["corazon"] if with_bromelain else [])
    ded = {"pulpa": "Decantadora", "cascara": "Prensa cáscara", "corazon": "Prensa corazón"}
    nm = len(modes)
    m = Model("dimensionamiento"); m.hideOutput()
    # ---------------- primera etapa: tamaños
    y = {(u, k): m.addVar(vtype="B", name=f"y_{u}_{k}") for u in O for k in range(len(O[u]))}
    for u in O:
        m.addCons(quicksum(y[u, k] for k in range(len(O[u]))) == 1)
    y3 = m.addVar(vtype="B", name="turno3", ub=1 if allow_shift else 0)
    fix = fix or {}
    for u, lab in fix.items():
        if u == "turno3":
            m.addCons(y3 == lab); continue
        if u not in O:
            continue
        k = [o["lab"] for o in O[u]].index(lab)
        m.addCons(y[u, k] == 1)
    for u, pref in (allow or {}).items():
        for k, o in enumerate(O[u]):
            if not any(o["lab"].startswith(p_) for p_ in pref):
                m.addCons(y[u, k] == 0)
    if store_max is not None:
        m.addCons(quicksum(O["Almacén de mosto"][k]["cap"] * y["Almacén de mosto", k] for k in range(len(O["Almacén de mosto"]))) <= store_max)
    yded = {j: quicksum(y[ded[j], k] for k in range(1, len(O[ded[j]]))) for j in modes if j in ded and ded[j] in O}
    capex_ann = (quicksum((AF * O[u][k]["cost"] + O[u][k].get("fixed", 0.0)) * y[u, k] for u in O for k in range(len(O[u])))
                 + shift_cost(with_bromelain) * y3 + AF * FIXED_EQ_COST)
    Hx = float(HM.max())
    MT = [(mo_, t) for mo_ in range(12) for t in range(K)]
    chi_fix = dict(fruta=None, pulpa=1.5, cascara=3.0, corazon=2.0, jugo=4.0, torta=12.0, jcor=3.0, lias=2.0, ret=4.0, hojas=None)
    gwp_total = 0.0
    second = 0.0
    V = dict(y=y, y3=y3, O=O, modes=modes, MT=MT, scen=[])
    for sc in scen:
        supply = SUPPLY * sc["sup"]
        rate_in = supply * pm.SEASON / 12.0 / HM
        rate_h = HOJAS_SUPPLY * sc["sup"] * pm.SEASON / 12.0 / HM                 # v10: hojas disponibles (t/h), con el perfil de la cosecha [S]
        chi = dict(chi_fix, fruta=3 * 24 * max(rate_in), hojas=3 * 24 * max(rate_h))
        d = {mt: m.addVar(lb=0, ub=HM[mt[0]]) for mt in MT}
        w = {mt: m.addVar(lb=0, ub=HM[mt[0]]) for mt in MT}                    # w = y3·d
        Hs = {}
        for mo_ in range(12):
            m.addCons(quicksum(d[mo_, t] for t in range(K)) == HM[mo_])
        for mt in MT:
            m.addCons(w[mt] <= d[mt]); m.addCons(w[mt] <= HM[mt[0]] * y3)
            Hs[mt] = A2 * d[mt] + (A3 - A2) * w[mt]                            # horas con personal
        # horas por tamaño elegido (0-1 × continua): g[u,k,mt] ≤ cap_h·y ; Σ_k g ≤ horas disponibles
        def cap_expr(u, mt, staffed):
            g = {k: m.addVar(lb=0) for k in range(len(O[u]))}
            for k in g:
                m.addCons(g[k] <= Hx * y[u, k])
            m.addCons(quicksum(g.values()) <= (Hs[mt] if staffed else AC * d[mt]))
            return quicksum(O[u][k]["cap"] * g[k] for k in g)
        def opt_flows(u, mt, staffed):   # flujo por opción (para costos y pérdidas que dependen de la opción elegida)
            g = {k: m.addVar(lb=0) for k in range(len(O[u]))}; x = {k: m.addVar(lb=0) for k in range(len(O[u]))}
            for k in g:
                m.addCons(g[k] <= Hx * y[u, k]); m.addCons(x[k] <= O[u][k]["cap"] * g[k])
            m.addCons(quicksum(g.values()) <= (Hs[mt] if staffed else AC * d[mt]))
            return x
        tau = {(i, k, mt): m.addVar(lb=0) for i in modes for k in range(len(O["Prensa"])) for mt in MT}
        ncy = {mt: m.addVar(vtype="I", lb=0, ub=4 * HM[mt[0]]) for mt in MT}
        P = {(i, mt): m.addVar(lb=0) for i in modes for mt in MT}
        Pd = {(j, mt): m.addVar(lb=0) for j in yded for mt in MT}
        fe = {mt: m.addVar(lb=0) for mt in MT}; mfv = {mt: m.addVar(lb=0) for mt in MT}
        bod = {mt: m.addVar(lb=0) for mt in MT}; sec = {mt: m.addVar(lb=0) for mt in MT}
        asp = {mt: m.addVar(lb=0) for mt in MT}
        loss = {mt: m.addVar(lb=0) for mt in MT}
        ml = {mt: m.addVar(lb=0) for mt in MT}; ld = {mt: m.addVar(lb=0) for mt in MT}     # lías a MF y a compostaje
        XC, SB = {}, {}
        ldry = {mt: m.addVar(lb=0) for mt in MT}; rdry = {mt: m.addVar(lb=0) for mt in MT}; rd = {mt: m.addVar(lb=0) for mt in MT}
        pj = {mt: m.addVar(lb=0) for mt in MT}; wv = {mt: m.addVar(lb=0) for mt in MT}; acid = {mt: m.addVar(lb=0) for mt in MT}
        hb = {mt: m.addVar(lb=0) for mt in MT}; cr = {mt: m.addVar(lb=0) for mt in MT}     # calor de la caldera (MJ) y corona quemada (t)
        comp = {mt: m.addVar(lb=0) for mt in MT}                                # cáscara sin prensar a compostaje
        OPT, OE = O["Pretratamiento cáscara"], O["Enzima cáscara"]
        Pco = {(k, mt): m.addVar(lb=0) for k in range(len(OPT)) for mt in MT}   # v9: cáscara prensada con cada pretratamiento
        XE = {}                                                                # v9: jugo de cáscara que pasa por la separación de enzima
        nv = lambda: {mt: m.addVar(lb=0) for mt in MT}
        hh, hx, hje, hjv, hjd, hjr, hpb = nv(), nv(), nv(), nv(), nv(), nv(), nv()   # v10: hojas acopiadas y extraídas; jugo a etanol, vinagre,
        et, eb, eu, hbio, hbu = nv(), nv(), nv(), nv(), nv()                       #      digestor o campo; pulpa a caldera; etanol (kg); electricidad
        pjc, pjx = nv(), nv()                                                       #      y calor del biogás; jugo de cáscara a ácido cítrico y xantana
        Edem, Hdem, G = {}, {}, {}
        compk = {mt: m.addVar(lb=0) for mt in MT}                               # corazón sin procesar a compostaje
        st = list(chi) + ["mosto"]
        nq = len(MT)
        I = {(k_, q): m.addVar(lb=0, ub=(chi[k_] if k_ in chi else None)) for k_ in st for q in range(nq + 1)}
        for q in range(nq + 1):
            m.addCons(I["mosto", q] <= quicksum(O["Almacén de mosto"][k]["cap"] * y["Almacén de mosto", k] for k in range(len(O["Almacén de mosto"]))))
        for k_ in st:
            m.addCons(I[k_, 0] == I[k_, nq])
        nF = len(O["Frente"])
        for q, mt in enumerate(MT):
            mo_ = mt[0]
            m.addCons(quicksum(tau[i, k, mt] for i in modes for k in range(len(O["Prensa"]))) + SIGMA * ncy[mt] <= Hs[mt])
            for i in modes:
                for k in range(len(O["Prensa"])):
                    m.addCons(tau[i, k, mt] <= Hx * y["Prensa", k])
                m.addCons(P[i, mt] <= quicksum(O["Prensa"][k]["cap"] * tau[i, k, mt] for k in range(len(O["Prensa"]))))
                if i in yded:   # si la fracción tiene prensa dedicada, no pasa por la principal
                    m.addCons(quicksum(tau[i, k, mt] for k in range(len(O["Prensa"]))) <= Hx * (1 - yded[i]))
            # acoplamiento con los pulmones perecederos (anual_continuo.py), con F_max = capacidad del frente elegida:
            #   fr_j · F_max · n_m · τ_i ≤ χ_j · n_ciclos ; F_max·τ_i = Σ_f cap_f · v_fi, v_fi = y_f·τ_i (exacto)
            for i in modes:
                ti = quicksum(tau[i, k, mt] for k in range(len(O["Prensa"])))
                v = {f: m.addVar(lb=0) for f in range(nF)}
                for f in range(nF):
                    m.addCons(v[f] <= Hx * y["Frente", f]); m.addCons(v[f] <= ti)
                    m.addCons(v[f] >= ti - Hx * (1 - y["Frente", f]))
                for j in modes:
                    if j == i:
                        continue
                    Mbig = FR[j] * nm * max(o["cap"] for o in O["Frente"]) * Hx
                    m.addCons(FR[j] * nm * quicksum(O["Frente"][f]["cap"] * v[f] for f in range(nF))
                              <= chi[j] * ncy[mt] + (Mbig * yded[j] if j in yded else 0))
            m.addCons(fe[mt] <= cap_expr("Frente", mt, True))
            XC[mt] = opt_flows("Clarificación", mt, True); SB[mt] = opt_flows("Estabilización", mt, True)
            OC, OS = O["Clarificación"], O["Estabilización"]
            m.addCons(mfv[mt] == quicksum(XC[mt].values()))
            m.addCons(quicksum(SB[mt].values()) == quicksum((1 - OC[k]["loss"]) * XC[mt][k] for k in XC[mt]) + LEES_REC * ml[mt])
            m.addCons(ml[mt] <= cap_expr("MF lías", mt, True))
            m.addCons(bod[mt] <= cap_expr("Bodega", mt, False))
            m.addCons(sec[mt] + LEES_DRY_EQ * (ldry[mt] + rdry[mt]) <= cap_expr("Secador", mt, False))
            # vinagre: jugo de cáscara fermentado y vino desviado, acetificados en continuo (24/7)
            m.addCons((pj[mt] + hjv[mt] * T_LEAF / T_PEEL) / 1.05 <= cap_expr("Bodega cáscara", mt, False))
            m.addCons(wv[mt] <= WINE_PM * bod[mt])
            XE[mt] = opt_flows("Enzima cáscara", mt, True)
            m.addCons(quicksum(XE[mt].values()) <= pj[mt])
            m.addCons(acid[mt] == A_WINE * wv[mt] + A_PJ * pj[mt] + A_LJ * hjv[mt]
                      + quicksum(A_PJ * ((1 + ENZ_GAIN) * (1 - ENZ_TECH[OE[k]["tech"]]["sl"]) - 1) * XE[mt][k] for k in XE[mt] if k > 0))
            m.addCons(acid[mt] <= cap_expr("Acetificador", mt, False))
            # v10: mezcla del vinagre. El acetificador solo diluye: el vinagre al 5 % (acid/VIN_ACID m³) no puede tener menos volumen que el
            # líquido que entra (vino 80 kg/m³; jugo de cáscara 46 y de hojas 27 kg de ácido por m³, por debajo del 5 %). Sin esta
            # restricción el jugo de hojas se vendería como vinagre al 5 % sin concentrarlo.
            if BLEND:
                m.addCons(wv[mt] + pj[mt] / cp.RHO_JUICE + hjv[mt] / 1.02 <= acid[mt] / VIN_ACID)
            # ---- v10: hojas → extractora → jugo (etanol, vinagre, digestor o campo) + pulpa (caldera o campo)
            m.addCons(hh[mt] <= rate_h[mo_] * d[mt])
            m.addCons(hx[mt] <= cap_expr("Extractora hojas", mt, True))
            m.addCons(hje[mt] + hjv[mt] + hjd[mt] + hjr[mt] == JF_H * hx[mt])
            m.addCons(hpb[mt] <= PF_H * hx[mt])
            m.addCons(hje[mt] <= cap_expr("Bodega etanol", mt, False))
            m.addCons(et[mt] == E_LJ * hje[mt])
            m.addCons(et[mt] <= cap_expr("Destilación", mt, False))
            m.addCons(hjd[mt] <= cap_expr("Digestor", mt, False))
            m.addCons(eb[mt] <= ETA_EL_B * CH4_MJ / 3.6 * hjd[mt])
            m.addCons(eb[mt] <= cap_expr("Motor biogás", mt, False))
            m.addCons(eu[mt] <= eb[mt])
            m.addCons(hbio[mt] <= ETA_TH_B / ETA_EL_B * 3.6 * eb[mt])
            m.addCons(hbu[mt] <= hbio[mt])
            for prod, var in (("Ácido cítrico", pjc), ("Xantana", pjx)):
                m.addCons(PJ_SUGAR * HUB[prod]["y"] * var[mt] <= cap_expr(prod, mt, False))
            # caldera de corona: capacidad, corona disponible y demanda de calor del periodo (secado + maceración)
            m.addCons(hb[mt] <= cap_expr("Caldera de corona", mt, False))
            m.addCons(hb[mt] == CROWN_MJ_T * cr[mt] + PULP_MJ_T * hpb[mt])      # corona y pulpa de hojas quemadas = calor que pide la caldera
            m.addCons(cr[mt] <= B1["crown_t"] * fe[mt])
            Hdem[mt] = (Q_CAKE * (sec[mt] + LEES_DRY_EQ * (ldry[mt] + rdry[mt])) + Q_MAC * (P["pulpa", mt] + (Pd["pulpa", mt] if "pulpa" in yded else 0))
                        + Q_DEST * et[mt] + Q_AD * hjd[mt])
            m.addCons(hb[mt] + hbu[mt] <= Hdem[mt])
            for j in yded:
                m.addCons(Pd[j, mt] <= cap_expr(ded[j], mt, True))
            if with_bromelain:
                m.addCons(asp[mt] <= cap_expr("Aspersión", mt, True))
            else:
                m.addCons(asp[mt] == 0)
            Pc = P["cascara", mt] + (Pd["cascara", mt] if "cascara" in yded else 0)
            Mpc = FR["cascara"] * max(o["cap"] for o in O["Frente"]) * Hx
            m.addCons(quicksum(Pco[k, mt] for k in range(len(OPT))) == Pc)
            for k in range(len(OPT)):
                m.addCons(Pco[k, mt] <= Mpc * y["Pretratamiento cáscara", k])
            m.addCons(pj[mt] + pjc[mt] + pjx[mt] <= quicksum(PJ_FRAC[OPT[k]["lab"]] * Pco[k, mt] for k in range(len(OPT))))
            # ---- v10: demanda de electricidad (sin la aireación fija, que se suma por mes) y GWP del periodo
            Edem[mt] = (KWH["fruit"] * fe[mt] + KWH["bod"] * bod[mt] + KWH["peel"] * Pc + KWH["flour"] * FLOUR_PC * sec[mt]
                        + quicksum(KWH_CLAR[OC[k]["lab"].split()[0]] * XC[mt][k] for k in XC[mt]) + KWH["lees_mf"] * ml[mt]
                        + quicksum((100.0 if OS[k]["lab"].startswith("UHPH") else 0.0) * SB[mt][k] for k in SB[mt])
                        + (KWH["dec"] * Pd["pulpa", mt] if "pulpa" in yded else 0) + ACID_HEAT / 3.6 / 4.0 * acid[mt] + KWH["crown"] * cr[mt]
                        + KWH_LEAF["ext"] * hx[mt] + KWH_LEAF["etoh"] * hje[mt] + KWH_LEAF["ad"] * hjd[mt] + KWH_LEAF["pulp"] * hpb[mt])
            G[mt] = (EF_KWH * (Edem[mt] - eu[mt]) + EF_GLP_UTIL * (Hdem[mt] - hb[mt] - hbu[mt]) + EF_BIO_FUEL * hb[mt]
                     + EF_COMP * ((FR["corazon"] * (0 if with_bromelain else 1) + B1["crown_t"]) * fe[mt] - cr[mt] + comp[mt] + compk[mt] + ld[mt] + rd[mt])
                     + EF_LEAK * CH4_T * hjd[mt] + EF_ACOPIO * hh[mt] + EF_FRUIT_T * fe[mt]
                     + EF_CHEM["dap"] * mfv[mt] + EF_CHEM["yeast"] * (bod[mt] + pj[mt] + hjv[mt] + hje[mt]) + EF_CHEM["pect"] * P["pulpa", mt]
                     + EF_CHEM["so2"] * quicksum(SB[mt][k] for k in SB[mt] if OS[k]["lab"].startswith("SO"))
                     + EF_CHEM["lime"] * quicksum(Pco[k, mt] for k in range(len(OPT)) if OPT[k]["lab"] != "agua"))
            Pk = (P["corazon", mt] + (Pd["corazon", mt] if "corazon" in yded else 0)) if with_bromelain else 0
            bal = {
                "fruta": rate_in[mo_] * d[mt] - fe[mt] - loss[mt],
                "pulpa": FR["pulpa"] * fe[mt] - P["pulpa", mt] - (Pd["pulpa", mt] if "pulpa" in yded else 0),
                "cascara": FR["cascara"] * fe[mt] - Pc - comp[mt],
                "corazon": (FR["corazon"] * fe[mt] - Pk - compk[mt]) if with_bromelain else 0,
                "jugo": JUICE * (P["pulpa", mt] + (Pd["pulpa", mt] if "pulpa" in yded else 0)) - mfv[mt],
                "lias": quicksum(OC[k]["loss"] * XC[mt][k] for k in XC[mt] if not OC[k].get("ret")) - ml[mt] - ld[mt] - ldry[mt],
                "ret": quicksum(OC[k]["loss"] * XC[mt][k] for k in XC[mt] if OC[k].get("ret")) - rdry[mt] - rd[mt],
                "mosto": quicksum(SB[mt].values()) - bod[mt],
                "torta": quicksum(CAKE_FRAC[OPT[k]["lab"]] * Pco[k, mt] for k in range(len(OPT))) - sec[mt],
                "jcor": (CORE_J * Pk - asp[mt]) if with_bromelain else 0,
                "hojas": hh[mt] - hx[mt],
            }
            for k_ in st:
                m.addCons(I[k_, q + 1] == I[k_, q] + bal[k_])
        if loss_max is not None:
            m.addCons(quicksum(loss.values()) <= loss_max * supply)
        # v10: la electricidad del biogás solo reemplaza diésel hasta la demanda del mes (aireación del acetificador incluida)
        OA = O["Acetificador"]
        for mo_ in range(12):
            aer = quicksum(AERATION_KW_M3 * (float(OA[k]["lab"].split()[0]) if OA[k]["lab"] != "no" else 0.0) * AC * HM[mo_] * y["Acetificador", k]
                           for k in range(len(OA)))
            m.addCons(quicksum(eu[mo_, t_] for t_ in range(K)) <= quicksum(Edem[mo_, t_] for t_ in range(K)) + aer)
            for t_ in range(K):
                G[mo_, t_] = G[mo_, t_] + EF_KWH * aer / K
        gwp_s = quicksum(G.values())
        gwp_total = gwp_total + sc["p"] * gwp_s
        unused = FR["corazon"] * (0 if with_bromelain else 1) + B1["crown_t"]
        Pcas = lambda mt: P["cascara", mt] + (Pd["cascara", mt] if "cascara" in yded else 0)
        pjtot = lambda mt: quicksum(PJ_FRAC[OPT[k]["lab"]] * Pco[k, mt] for k in range(len(OPT)))
        enz = lambda mt: quicksum((C["vendido"] * BROM_PRICE * ENZ_TECH[OE[k]["tech"]]["pf"] * ENZ_Y - ENZ_TECH[OE[k]["tech"]]["vc"]) * XE[mt][k]
                                  for k in XE[mt] if k > 0)
        contrib = quicksum(mg["wine"] * bod[mt] + mg["flour"] * sec[mt] + mg["brom"] * asp[mt] + 150.0 * 1000 * pjtot(mt)
                           - LIME_VC * quicksum(Pco[k, mt] for k in range(len(OPT)) if OPT[k]["lab"] != "agua") + enz(mt)
                           - (FRUIT_PRICE * 1000 + COMPOST * 1000 * unused) * fe[mt] - COMPOST * 1000 * (comp[mt] + compk[mt]) - CH_COST * ncy[mt]
                           - mg["guard"] * WINE_PM * bod[mt]
                           - quicksum(O["Clarificación"][k].get("vc", 0.0) * XC[mt][k] for k in XC[mt])
                           - quicksum(O["Estabilización"][k].get("vc", 0.0) * SB[mt][k] for k in SB[mt])
                           - LEES_MF_VC * ml[mt] - LEES_DISP * (ld[mt] + rd[mt]) - (DEC_VC * Pd["pulpa", mt] if "pulpa" in yded else 0)
                           + (LEES_FLOUR * mg["flour_t"] - LEES_DRY_EQ * mg["v_cake"]) * (ldry[mt] + rdry[mt])
                           + (mg["vin_kg"] - VIN_VC - mg["vin_tank"]) * acid[mt]
                           - (mg["wine_m3"] - mg["guard"]) * wv[mt]
                           - (150.0 * 1000 + PJ_VC) * pj[mt]
                           + HEAT_COP * hb[mt] + (COMPOST * 1000 - CROWN_VC) * cr[mt]
                           # v10: hojas, etanol + levadura, biogás, pulpa a caldera y productos del hub
                           - ACOPIO_VC * hh[mt] - E_COP * (KWH_LEAF["ext"] * hx[mt] + KWH_LEAF["etoh"] * hje[mt] + KWH_LEAF["ad"] * hjd[mt] + KWH_LEAF["pulp"] * hpb[mt])
                           + (C["vendido"] * (ETOH_PRICE * L_PER_KG * E_LJ + YEAST_PRICE * YEAST_LJ) - ETOH_VC) * hje[mt]
                           - PJ_VC * hjv[mt]
                           - HEAT_COP * (Q_DEST * et[mt] + Q_AD * hjd[mt]) + HEAT_COP * hbu[mt]
                           + E_COP * eu[mt] + VAL_EXC * (eb[mt] - eu[mt]) - BIO_OM * eb[mt]
                           + quicksum((C["vendido"] * HUB[pr]["price"] - HUB[pr]["vc"]) * PJ_SUGAR * HUB[pr]["y"] * var[mt] - 150.0 * 1000 * var[mt]
                                      for pr, var in (("Ácido cítrico", pjc), ("Xantana", pjx)))
                           for mt in MT)
        second = second + sc["p"] * contrib
        V["scen"].append(dict(sc=sc, supply=supply, d=d, w=w, tau=tau, ncy=ncy, P=P, Pd=Pd, fe=fe, mfv=mfv, bod=bod, sec=sec,
                              asp=asp, loss=loss, comp=comp, I=I, contrib=contrib, Hs=Hs, XC=XC, SB=SB, ml=ml, ld=ld,
                              ldry=ldry, rdry=rdry, rd=rd, pj=pj, wv=wv, acid=acid, hb=hb, cr=cr, Pco=Pco, XE=XE,
                              hh=hh, hx=hx, hje=hje, hjv=hjv, hjd=hjd, hjr=hjr, hpb=hpb, et=et, eb=eb, eu=eu, hbio=hbio, hbu=hbu,
                              pjc=pjc, pjx=pjx, Edem=Edem, Hdem=Hdem, G=G, gwp=gwp_s))
    if gwp_max is not None:                                                    # v10: ε-restricción sobre el GWP esperado (kg CO2e/año)
        m.addCons(gwp_total <= gwp_max)
    if objective == "gwp":
        m.setObjective(gwp_total / 1e6 - 1e-6 * (second - capex_ann) / 1e6, "minimize")
    else:
        m.setObjective((second - capex_ann) / 1e6, "maximize")
    V["capex_ann"] = capex_ann; V["gwp_total"] = gwp_total
    return m, V


def extract(m, V, with_bromelain):
    v = m.getVal
    O = V["O"]
    sizes = {u: O[u][max(range(len(O[u])), key=lambda k: v(V["y"][u, k]))] for u in O}
    out = dict(status=m.getStatus(), gap=m.getGap(), obj=m.getObjVal(), sizes={u: s["lab"] for u, s in sizes.items()},
               caps={u: s["cap"] for u, s in sizes.items()}, turno3=int(round(v(V["y3"]))),
               capex_purchase=sum(s["cost"] for s in sizes.values()), capex_ann=v(V["capex_ann"]) / 1e6,
               FCI=LANG * sum(s["cost"] for s in sizes.values()) / 1e6, scen=[])
    a_st = A3 if out["turno3"] else A2
    for S in V["scen"]:
        rows, T0 = [], 0.0
        for mt in V["MT"]:
            dur = v(S["d"][mt])
            # tiempo efectivo de prensa por material = lo procesado / capacidad (τ del modelo es una cota superior)
            tau = {i: (v(S["P"][i, mt]) / sizes["Prensa"]["cap"] if sizes["Prensa"]["cap"] > 0 else 0.0) for i in V["modes"]}
            rows.append(dict(month=mt[0], k=mt[1], start=T0, dur=dur, tau=tau, W=v(S["ncy"][mt]),
                             P={i: v(S["P"][i, mt]) for i in V["modes"]}, Pd={j: v(S["Pd"][j, mt]) for j, _ in [(a, b) for (a, b) in S["Pd"] if b == mt]},
                             fe=v(S["fe"][mt]), mf=v(S["mfv"][mt]), bod=v(S["bod"][mt]), sec=v(S["sec"][mt]), asp=v(S["asp"][mt]),
                             stab=sum(v(x_) for x_ in S["SB"][mt].values()), ml=v(S["ml"][mt]), ld=v(S["ld"][mt]) + v(S["rd"][mt]),
                             ldry=v(S["ldry"][mt]) + v(S["rdry"][mt]), pj=v(S["pj"][mt]), wv=v(S["wv"][mt]), acid=v(S["acid"][mt]),
                             hb=v(S["hb"][mt]), cr=v(S["cr"][mt]),
                             pjt=sum(PJ_FRAC[O["Pretratamiento cáscara"][k]["lab"]] * v(S["Pco"][k, mt]) for k in range(len(O["Pretratamiento cáscara"]))),
                             cal=sum(v(S["Pco"][k, mt]) for k in range(len(O["Pretratamiento cáscara"])) if O["Pretratamiento cáscara"][k]["lab"] != "agua"),
                             enz=sum(v(x_) for k, x_ in S["XE"][mt].items() if k > 0),
                             hh=v(S["hh"][mt]), hx=v(S["hx"][mt]), hje=v(S["hje"][mt]), hjv=v(S["hjv"][mt]), hjd=v(S["hjd"][mt]), hjr=v(S["hjr"][mt]),
                             hpb=v(S["hpb"][mt]), et=v(S["et"][mt]), eb=v(S["eb"][mt]), eu=v(S["eu"][mt]), hbu=v(S["hbu"][mt]),
                             pjc=v(S["pjc"][mt]), pjx=v(S["pjx"][mt]), edem=v(S["Edem"][mt]), hdem=v(S["Hdem"][mt]), gwp=v(S["G"][mt]),
                             loss=v(S["loss"][mt]), comp=v(S["comp"][mt]), I_mosto=v(S["I"]["mosto", V["MT"].index(mt) + 1])))
            T0 += dur
        util = {}
        cap = out["caps"]
        for u, key, staffed in (("Frente", "fe", True), ("Clarificación", "mf", True), ("Estabilización", "stab", True), ("MF lías", "ml", True),
                                ("Acetificador", "acid", False), ("Caldera de corona", "hb", False),
                                ("Bodega", "bod", False), ("Secador", "sec", False), ("Aspersión", "asp", True), ("Enzima cáscara", "enz", True),
                                ("Extractora hojas", "hx", True), ("Bodega etanol", "hje", False), ("Destilación", "et", False),
                                ("Digestor", "hjd", False), ("Motor biogás", "eb", False)):
            if u == "Estabilización" and out["sizes"][u].startswith("SO"):
                continue
            if u not in cap or cap[u] <= 0:
                continue
            util[u] = [sum(r[key] for r in rows if r["month"] == mo_) / (cap[u] * (a_st if staffed else AC) * HM[mo_]) for mo_ in range(12)]
        util["Prensa"] = [(sum(sum(r["tau"].values()) for r in rows if r["month"] == mo_) + SIGMA * sum(r["W"] for r in rows if r["month"] == mo_))
                          / (a_st * HM[mo_]) for mo_ in range(12)]
        if cap.get("Prensa", 0) <= 0:
            util.pop("Prensa", None)
        for j, u in (("pulpa", "Decantadora"), ("cascara", "Prensa cáscara"), ("corazon", "Prensa corazón")):
            if u in cap and cap[u] > 0:
                util[u] = [sum(r["Pd"].get(j, 0) for r in rows if r["month"] == mo_) / (cap[u] * a_st * HM[mo_]) for mo_ in range(12)]
        prod = dict(fruta_t=sum(r["fe"] for r in rows), cascara_compost_t=sum(r["comp"] for r in rows),
                    mosto_m3=sum(r["mf"] for r in rows), lias_MF_m3=sum(r["ml"] for r in rows), lias_compost_m3=sum(r["ld"] for r in rows),
                    lias_secador_t=sum(r["ldry"] for r in rows), harina_lias_t=sum(r["ldry"] for r in rows) * LEES_FLOUR,
                    jugo_cascara_vinagre_t=sum(r["pj"] for r in rows), vino_a_vinagre_m3=sum(r["wv"] for r in rows),
                    acido_kg=sum(r["acid"] for r in rows), vinagre_m3=sum(r["acid"] for r in rows) / VIN_ACID,
                    calor_corona_GJ=sum(r["hb"] for r in rows) / 1000, corona_caldera_t=sum(r["cr"] for r in rows), vino_m3=sum(r["bod"] for r in rows) * WINE_PM,
                    harina_t=sum(r["sec"] for r in rows) * FLOUR_PC,
                    bromelaina_kg=sum(r["asp"] for r in rows) * B1["bromelain_kg"] / (B1["core_t"] * CORE_J),
                    torta_t=sum(r["sec"] for r in rows), jugo_cascara_t=sum(r["pjt"] for r in rows), cascara_cal_t=sum(r["cal"] for r in rows),
                    jugo_enzima_t=sum(r["enz"] for r in rows), enzima_cascara_kg=sum(r["enz"] for r in rows) * ENZ_Y,
                    hojas_t=sum(r["hh"] for r in rows), hojas_extraidas_t=sum(r["hx"] for r in rows),
                    jugo_hojas_etanol_t=sum(r["hje"] for r in rows), jugo_hojas_vinagre_t=sum(r["hjv"] for r in rows),
                    jugo_hojas_digestor_t=sum(r["hjd"] for r in rows), jugo_hojas_campo_t=sum(r["hjr"] for r in rows),
                    pulpa_hojas_caldera_t=sum(r["hpb"] for r in rows), pulpa_hojas_campo_t=sum(PF_H * r["hx"] - r["hpb"] for r in rows),
                    etanol_kg=sum(r["et"] for r in rows), etanol_L=sum(r["et"] for r in rows) * L_PER_KG, levadura_kg=sum(r["hje"] for r in rows) * YEAST_LJ,
                    ch4_kg=sum(r["hjd"] for r in rows) * CH4_T, elec_bio_kWh=sum(r["eb"] for r in rows), elec_bio_usada_kWh=sum(r["eu"] for r in rows),
                    elec_excedente_kWh=sum(r["eb"] - r["eu"] for r in rows), calor_bio_usado_MJ=sum(r["hbu"] for r in rows),
                    jugo_cascara_citrico_t=sum(r["pjc"] for r in rows), jugo_cascara_xantana_t=sum(r["pjx"] for r in rows),
                    citrico_kg=sum(r["pjc"] for r in rows) * PJ_SUGAR * HUB["Ácido cítrico"]["y"], xantana_kg=sum(r["pjx"] for r in rows) * PJ_SUGAR * HUB["Xantana"]["y"],
                    elec_demanda_kWh=sum(r["edem"] for r in rows), calor_demanda_MJ=sum(r["hdem"] for r in rows),
                    calor_glp_MJ=sum(r["hdem"] - r["hb"] - r["hbu"] for r in rows), gwp_kg=sum(r["gwp"] for r in rows))
        out["scen"].append(dict(sup=S["sc"]["sup"], p=S["sc"]["p"], supply=S["supply"], contrib=v(S["contrib"]) / 1e6, periods=rows,
                                util=util, loss=sum(r["loss"] for r in rows), loss_month=[sum(r["loss"] for r in rows if r["month"] == mo_) for mo_ in range(12)],
                                supply_month=(S["supply"] * pm.SEASON / 12.0).tolist(), changeovers=sum(r["W"] for r in rows), products=prod,
                                margin=v(S["contrib"]) / 1e6 - out["capex_ann"]))
    return out


def solve(scen=None, K=2, with_bromelain=False, time_limit=240, gap=0.005, hint=None, **kw):
    scen = scen or [dict(sup=1.0, p=1.0)]
    m, V = build(scen, K=K, with_bromelain=with_bromelain, **kw)
    if hint and "fix" not in kw:
        # arranque en caliente: se resuelve el mismo modelo con los tamaños fijos de una solución conocida y su solución
        # completa se carga en el modelo libre (las variables se crean en el mismo orden en los dos modelos)
        try:
            m1, _ = build(scen, K=K, with_bromelain=with_bromelain, fix=hint, **kw)
            m1.setParam("limits/time", 120); m1.setParam("limits/gap", 0.01); m1.optimize()
            if m1.getNSols() > 0:
                vals = [m1.getVal(x) for x in m1.getVars()]
                sol = m.createSol()
                for x, val in zip(m.getVars(), vals):
                    m.setSolVal(sol, x, val)
                print("    arranque en caliente:", "aceptado" if m.addSol(sol, free=True) else "rechazado", round(m1.getObjVal()), flush=True)
        except Exception as ex:   # un tamaño de la pista que ya no existe, etc.
            print("    sin arranque en caliente:", ex, flush=True)
    m.setParam("limits/time", time_limit); m.setParam("limits/gap", gap)
    t0 = time.time(); m.optimize()
    if m.getNSols() == 0:
        return dict(status=m.getStatus())
    r = extract(m, V, with_bromelain); r["t"] = time.time() - t0
    return r


def brief(r):
    s = r["scen"][0] if r.get("scen") else {}
    return (f"{r['status']} gap {r['gap']:.3%} obj {r['obj']:,.0f} | FCI {r['FCI']:,.0f} | {r['sizes']} T3={r['turno3']} | "
            f"pérdida {sum(x['loss'] for x in r['scen']) / sum(x['supply'] for x in r['scen']):.1%} | cambios {s.get('changeovers', 0):.0f}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]
    path = os.environ.get("DIM_OUT", f"{RES}/dimensionamiento.json")      # corridas en paralelo, cada una con su archivo
    out = json.load(open(path)) if os.path.exists(path) else {}
    save = lambda: json.dump(out, open(path, "w"), default=float)
    _H = json.load(open(f"{RES}/dimensionamiento_v9.json")) if os.path.exists(f"{RES}/dimensionamiento_v9.json") else {}
    NEW10 = ("Extractora hojas", "Bodega etanol", "Destilación", "Digestor", "Motor biogás", "Ácido cítrico", "Xantana")
    def leaves_hint(f):   # v10: arranque con jugo de hojas al vinagre, mezclado con el vino (a 1×: +1 590 MM COP/año sobre el diseño v9)
        pick = lambda opts, need: next((o for o in opts if o >= need), opts[-1])
        return {"Extractora hojas": f"{pick((2, 5, 10, 20, 40, 60), 5 * f):g} t/h", "Bodega cáscara": f"{pick((2, 3, 4, 6, 8), 4 * f)}×10 m³",
                "Acetificador": f"{pick((2, 4, 6, 10, 20, 40), 20 * f):g} m³"}
    def hint(key, each=None, f=1.0, leaves=True):
        r0 = _H.get(key, {})
        if each is not None:
            r0 = r0.get("each", [{}])[each] if r0.get("each") else {}
        if not r0.get("sizes"):
            r0 = _H.get("E1|Óptimo económico", {})
            if not r0.get("sizes"):
                return None
        hnt = dict(r0["sizes"], **{u: "no" for u in NEW10}, turno3=r0.get("turno3", 0))
        if leaves:
            hnt.update(leaves_hint(f))
        return hnt
    print("Lang eq.", round(LANG, 3), "AF", round(AF, 4), "turno 3 MM COP/año", round(shift_cost() / 1e6, 1),
          {k: round(v_) for k, v_ in margins().items()}, "hojas t/año", round(HOJAS_SUPPLY), "acopio COP/t", ACOPIO_VC, flush=True)
    if "E1" in which:   # óptimo vs referencia TRL-9
        v9 = _H.get("E1|Óptimo económico")
        if v9:   # v10: el diseño óptimo de la v9 evaluado con los parámetros de la v10 (descomposición v9 → v10)
            r = solve(fix=dict(v9["sizes"], **{u: "no" for u in NEW10}, turno3=v9["turno3"]))
            out["E1|Diseño v9 con parámetros v10"] = r; save(); print("E1 Diseño v9 con parámetros v10", brief(r), flush=True)
        for lab, kw, lv in (("Referencia TRL-9 (planta_trl9, 6 200 t)", dict(fix=REFERENCE), False),
                            ("Referencia con prensa única de 3 t/h compartida", dict(fix=dict(REFERENCE, **{"Prensa": "3 t/h", "Prensa cáscara": "no"})), False),
                            ("Óptimo con la topología anterior (prensa, MF de mosto, HTST)", dict(allow=ALLOW_OLD), False),
                            ("Óptimo económico", {}, True),
                            ("Óptimo sin SO₂", dict(allow=NO_SO2), True),
                            ("Óptimo sin vinagre", dict(allow=NO_VIN), True),
                            ("Óptimo sin caldera de corona", dict(allow=NO_BOILER), True),
                            ("Óptimo sin opciones v10 (sin hojas ni hub)", dict(allow=NO_V10), False),
                            ("Óptimo sin etanol de hojas", dict(allow=NO_ETOH), False),
                            ("Óptimo sin digestor", dict(allow=NO_AD), True)):
            h_ = hint(f"E1|{lab}", leaves=lv)
            if h_ and "allow" in kw:   # el arranque debe respetar las restricciones del caso
                for u, pref in kw["allow"].items():
                    if not any(h_.get(u, "").startswith(p_) for p_ in pref):
                        h_[u] = pref[0] if pref[0] != "MF" else "MF 20 m²"
            r = solve(hint=h_ if "fix" not in kw else None, **kw)
            out[f"E1|{lab}"] = r; save(); print("E1", lab, brief(r), flush=True)
    if "E2" in which:   # regla de dimensionamiento: tamaños óptimos según la oferta (0,5× a la base de la tesis)
        for f in (0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 21856 / SUPPLY):
            r = solve(scen=[dict(sup=f, p=1.0)], time_limit=180, hint=hint(f"E2|{f:.3f}", f=f)); out[f"E2|{f:.3f}"] = r; save(); print("E2", round(f, 3), brief(r), flush=True)
    if "E3" in which:   # valor del almacenamiento aséptico y del tercer turno, a 2× la oferta actual
        sc2 = [dict(sup=2.0, p=1.0)]
        for lab, kw in (("libre (almacén y turno 3 disponibles)", {}),
                        ("sin almacén aséptico (≤ 25 m³)", dict(store_max=25)),
                        ("sin turno 3", dict(allow_shift=False)),
                        ("sin almacén ni turno 3", dict(store_max=25, allow_shift=False))):
            r = solve(scen=sc2, time_limit=150, hint=hint(f"E3|{lab}", f=2.0), **kw); out[f"E3|{lab}"] = r; save(); print("E3", lab, brief(r), flush=True)
    if "E4" in which:   # dimensionamiento estocástico (oferta 0,7 / 1,0 / 1,3) — Grossmann cap. 14
        import estocastico as es
        sc = [dict(sup=a, p=pa) for a, pa in es.SUP_F]
        rp = solve(scen=sc, time_limit=600, hint=hint("E4|RP")); out["E4|RP"] = rp; save(); print("E4 RP", brief(rp), flush=True)
        ev = solve(scen=[dict(sup=sum(a * pa for a, pa in es.SUP_F), p=1.0)], hint=hint("E4|EV")); out["E4|EV"] = ev; save(); print("E4 EV", brief(ev), flush=True)
        fixev = dict(ev["sizes"], turno3=ev["turno3"])
        eev = solve(scen=sc, fix=fixev, time_limit=600); out["E4|EEV"] = eev; save(); print("E4 EEV", brief(eev), flush=True)
        ws = [solve(scen=[dict(sup=a, p=1.0)], hint=hint("E4|WS", i, f=a)) for i, (a, pa) in enumerate(es.SUP_F)]
        out["E4|WS"] = dict(obj=sum(r["obj"] * pa for r, (a, pa) in zip(ws, es.SUP_F)), each=[dict(sup=a, obj=r["obj"], sizes=r["sizes"], turno3=r["turno3"]) for r, (a, pa) in zip(ws, es.SUP_F)])
        save(); print("E4 WS", out["E4|WS"]["obj"], "VSS", rp["obj"] - eev["obj"], "EVPI", out["E4|WS"]["obj"] - rp["obj"], flush=True)
    if "E6" in which:   # precio del vino y del vinagre: ¿cuándo conviene acetificar?
        for wp in (1600.0, 2200.0, 3000.0, 4000.0):
            for vp in (1500.0, 2200.0):
                r = solve(mg=margins(wine_price=wp, vinegar_price=vp), time_limit=150, hint=hint(f"E6|{wp:.0f}|{vp:.0f}")); out[f"E6|{wp:.0f}|{vp:.0f}"] = r; save()
                print("E6", wp, vp, brief(r), {k: round(v_) for k, v_ in r["scen"][0]["products"].items()
                                               if k in ("vino_m3", "vino_a_vinagre_m3", "jugo_cascara_vinagre_t", "vinagre_m3")}, flush=True)
        margins()   # restituye el precio base del vinagre
    if "E5" in which:   # configuración B con bromelaína: ¿prensa compartida o dedicada?
        for lab, kw in (("B referencia (prensas dedicadas TRL-9)", dict(fix=REFERENCE_B)),
                        ("B óptimo con la topología anterior", dict(allow=ALLOW_OLD)), ("B óptimo económico", {})):
            r = solve(with_bromelain=True, hint=(hint(f"E5|{lab}") if "fix" not in kw else None), **kw); out[f"E5|{lab}"] = r; save(); print("E5", lab, brief(r), flush=True)
    if "E7" in which:   # v10: sensibilidad de las hojas (fracción acopiable, costo de acopio, precio del etanol)
        base = dict(HS=HOJAS_SUPPLY, AV=ACOPIO_VC, EP=ETOH_PRICE)
        for lab, ch in (("fracción de acopio 0,10", dict(HS=base["HS"] * 0.10 / DT.val("frac_acopio_hojas"))),
                        ("fracción de acopio 0,50", dict(HS=base["HS"] * 0.50 / DT.val("frac_acopio_hojas"))),
                        ("costo de acopio 80 000 COP/t", dict(AV=80_000.0)),
                        ("etanol a 3 000 COP/L", dict(EP=3_000.0))):
            HOJAS_SUPPLY, ACOPIO_VC, ETOH_PRICE = ch.get("HS", base["HS"]), ch.get("AV", base["AV"]), ch.get("EP", base["EP"])
            r = solve(time_limit=180, hint=hint("E1|Óptimo económico")); out[f"E7|{lab}"] = r; save(); print("E7", lab, brief(r), flush=True)
        HOJAS_SUPPLY, ACOPIO_VC, ETOH_PRICE = base["HS"], base["AV"], base["EP"]
    save()
