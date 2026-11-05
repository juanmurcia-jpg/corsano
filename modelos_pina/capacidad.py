"""
Análisis de capacidad de la planta diseñada (biorrefinería de piña, Bajo Atrato).

C1  Balance de masa fruta -> fracciones -> productos para la base de diseño de la tesis (78 300 hL/año de vino)
C2  Cuánta fruta exige esa base frente a la oferta documentada (Chocó 2008: 3 883 t; rechazo en Quibdó: 12 t/mes)
C3  Capacidad que soporta cada escenario de oferta (inverso de C1)
C4  Cuello de botella por línea: alimentación, cinética, equipos y energía (calor de secado vs isla de gasificación)
C5  Efecto del calendario de operación (continuo 7 500 h vs plantilla Burk: lun–sáb, 2 turnos de 6 h efectivas)
Todos los parámetros con procedencia: [T] tesis, [L] literatura, [S] supuesto, [B] libro de Bekatorou (2020).
"""
import json, os
import numpy as np
import params as p

RES = os.path.join(os.path.dirname(__file__), "results")

# ---------------------------------------------------------------------------------- base de datos de fracciones
FR = {  # fracción másica de la fruta entera fresca con corona: central, mínimo, máximo
    "pulpa":  (0.45, 0.25, 0.55),   # [L] 0,25 si se toma el 75 % de residuo de Abdullah (2007) citado en [B] p. 269
    "cascara": (0.30, 0.25, 0.35),  # [L]
    "corazon": (0.10, 0.08, 0.12),  # [L] (tallo+corazón en la tesis; aquí solo corazón de la fruta)
    "corona": (0.15, 0.10, 0.20),   # [L]
}
JUICE_YIELD_PULP = 0.87          # [T] §4.2.1 (Quesada Salas 2013)
RHO_JUICE = 1.06                 # t/m3 [L]
WINE_LOSS = 0.03                 # lías y trasiegos [S]
SUPPLY = {                        # t de fruta entera por año
    "Rechazo Quibdó (12 t/mes)": 144.0,                  # [T] §3.3 (Murcia Palacios 2013)
    "Chocó, producción total 2008": 3883.0,             # [T] §3.3
    "Chocó, producción total 2022 (EVA)": 6146.0,       # UPRA, documento regional Chocó (EVA 2022)
    "Chocó 2022 × 25 % de pérdida poscosecha": 6146.0 * 0.25,   # [S] pérdida poscosecha típica de frutas
}


def fruit_for_wine(wine_m3, pulp_share=FR["pulpa"][0]):
    juice_m3 = wine_m3 / (1 - WINE_LOSS)
    pulp_t = juice_m3 * RHO_JUICE / JUICE_YIELD_PULP
    return pulp_t / pulp_share, pulp_t, juice_m3


def wine_from_fruit(fruit_t, pulp_share=FR["pulpa"][0]):
    pulp_t = fruit_t * pulp_share
    juice_m3 = pulp_t * JUICE_YIELD_PULP / RHO_JUICE
    return juice_m3 * (1 - WINE_LOSS)


# ---------------------------------------------------------------------------------- rendimientos de cada línea
Y = dict(
    peel_juice_frac=0.578,      # v9: jugo / cáscara con extractora (Campos et al. 2020, Foods 9:60, fig. 1); v8: 0,50 [S]
    peel_cake_moist=0.75,       # humedad de la torta [L]
    peel_dm=0.1765,             # v9: materia seca de la cáscara fresca, humedad 82,35 % (Campos 2020, tabla 1); v8: 0,14 [L]
    cake_dm_ret=0.41,           # v9: fracción de la materia seca de la cáscara que queda en la torta (Campos 2020: torta 42,2 % con 17,03 % MS); v8: 0,75 [S]
    flour_moist=0.10,           # humedad final de la harina [L]
    core_juice_frac=0.60,       # [S]
    bromelain_g_per_kg_core=3.0,  # bromelaína cruda [S] (rango 1–6)
    powder_frac_core=0.04,      # polvo nutracéutico / corazón [S]
    crown_dm=0.20,              # materia seca de corona [L]
    crown_to_gasifier=0.6,      # fracción de la materia seca de corona que va al gasificador (resto al hidrolizado) [S]
    HHV_MJ_kg=17.0,             # [L]
    eta_el=0.22, eta_th=0.40,   # gasificador + MCI con recuperación de calor [L]
    dryer_MJ_per_kg_water=3.2,  # secador de banda con aire caliente [L]
    acid_from_ethanol=1.304 * 0.90,   # g ácido / g etanol (90 % del estequiométrico) [L]
    vinegar_acidity=50.0,       # g/L [T] Roda 2017a
)


def full_balance(fruit_t, wine_frac_to_vinegar=0.16, pulp_share=FR["pulpa"][0], shares=None):
    sh = dict((k, v[0]) for k, v in FR.items())
    if shares:
        sh.update(shares)
    sh["pulpa"] = pulp_share
    pulp, peel, core, crown = (fruit_t * sh[k] for k in ("pulpa", "cascara", "corazon", "corona"))
    juice_m3 = pulp * JUICE_YIELD_PULP / RHO_JUICE
    wine_m3 = juice_m3 * (1 - WINE_LOSS)
    vin_wine_m3 = wine_m3 * wine_frac_to_vinegar
    acid_t = vin_wine_m3 * p.P_REF / 1000 * Y["acid_from_ethanol"]
    vinegar_m3 = acid_t * 1000 / Y["vinegar_acidity"]
    peel_juice_t = peel * Y["peel_juice_frac"]
    cake_t = peel - peel_juice_t
    cake_dm = peel * Y["peel_dm"] * Y["cake_dm_ret"]   # materia seca que queda en la torta (Campos 2020)
    flour_t = cake_dm / (1 - Y["flour_moist"])
    water_evap_t = cake_t - flour_t
    core_juice_t = core * Y["core_juice_frac"]
    bromelain_kg = core * 1000 * Y["bromelain_g_per_kg_core"] / 1000
    powder_t = core * Y["powder_frac_core"]
    crown_dm_t = crown * Y["crown_dm"]
    gas_dm_t = crown_dm_t * Y["crown_to_gasifier"]
    E_el_MWh = gas_dm_t * 1000 * Y["HHV_MJ_kg"] * Y["eta_el"] / 3600
    Q_th_GJ = gas_dm_t * Y["HHV_MJ_kg"] * Y["eta_th"]
    Q_dry_GJ = water_evap_t * Y["dryer_MJ_per_kg_water"]
    return dict(fruit_t=fruit_t, pulp_t=pulp, peel_t=peel, core_t=core, crown_t=crown, juice_m3=juice_m3,
                wine_m3=wine_m3, wine_hL=wine_m3 * 10, wine_sold_m3=wine_m3 - vin_wine_m3, vinegar_m3=vinegar_m3,
                peel_juice_t=peel_juice_t, flour_t=flour_t, water_evap_t=water_evap_t, core_juice_t=core_juice_t,
                bromelain_kg=bromelain_kg, powder_t=powder_t, crown_dm_t=crown_dm_t, gas_dm_t=gas_dm_t,
                E_el_MWh=E_el_MWh, P_el_kW_7500=E_el_MWh * 1000 / 7500, Q_th_GJ=Q_th_GJ, Q_dry_GJ=Q_dry_GJ,
                heat_cover=Q_th_GJ / Q_dry_GJ if Q_dry_GJ > 0 else np.nan)


def calendar(scen):
    days = (365.25 - 365.25 / 7 - 18) * 0.9
    return dict(days=days)


def calendar_hours(scenario):
    """Plantilla Burk de los TEA de coco/asaí: escenario 3 = lun–sáb sin festivos, 2 turnos, 6 h efectivas/turno."""
    if scenario == "continuo":
        return 7500.0
    days = (365.25 - 365.25 / 7 - 18) * 0.9
    return days * 2 * 6


if __name__ == "__main__":
    out = {}
    W = p.WINE_VOL_YR
    # C1-C2
    req = {}
    for lab, ps in (("central", FR["pulpa"][0]), ("pulpa alta 55 %", FR["pulpa"][2]), ("pulpa baja 25 % (75 % residuo)", FR["pulpa"][1])):
        f, pulp, juice = fruit_for_wine(W, ps)
        req[lab] = dict(fruit_t=f, pulp_t=pulp, juice_m3=juice, x_choco=f / SUPPLY["Chocó, producción total 2008"],
                        x_quibdo=f / SUPPLY["Rechazo Quibdó (12 t/mes)"])
    out["C2"] = req
    print("C2", {k: (round(v["fruit_t"]), round(v["x_choco"], 1), round(v["x_quibdo"])) for k, v in req.items()})
    out["C1_design"] = full_balance(req["central"]["fruit_t"])
    # C3
    out["C3"] = {k: full_balance(v) for k, v in SUPPLY.items()}
    for k, v in out["C3"].items():
        print("C3", k, "vino hL", round(v["wine_hL"]), "% diseño", round(100 * v["wine_hL"] / (W * 10), 1))
    # C4 cuellos de botella (base de diseño)
    b = out["C1_design"]
    H_c, H_b = calendar_hours("continuo"), calendar_hours("burk")
    stat_days, acet_kg_m3_d = 30.0, 50.0                           # [T] Roda 2017a; [T]/[B] Emde/Frings
    acid_t = b["vinegar_m3"] * Y["vinegar_acidity"] / 1000
    C4 = dict(
        aging_m3=b["wine_m3"] * 90 / 365,                         # 90 d de envejecimiento [T]
        vinegar_static_m3=b["vinegar_m3"] * stat_days / 365 * 1.1,   # volumen de trabajo de acetificación estática
        vinegar_acetator_m3=acid_t * 1000 / (acet_kg_m3_d * 365 * 0.9),
        frings_rule_m3=b["vinegar_m3"] / 100.0,                   # [B] p. 93: 200 L -> 20 000 L/año (100 ×)
        cetotec_rule_m3=b["vinegar_m3"] * (5.0 / 10.0) / 1570.0,  # [B] p. 93: 100 L -> 157 000 L/año al 10 %
        juice_flow_continuo_m3h=b["juice_m3"] / H_c, juice_flow_burk_m3h=b["juice_m3"] / H_b,
        fruit_flow_continuo_th=b["fruit_t"] / H_c, fruit_flow_burk_th=b["fruit_t"] / H_b,
        UHPH_util_continuo=b["juice_m3"] / H_c / 10.0, UHPH_util_burk=b["juice_m3"] / H_b / 10.0,   # Ypsicon 10 000 L/h [T]
        heat_cover=b["heat_cover"], P_el_kW=b["P_el_kW_7500"], H_c=H_c, H_b=H_b,
    )
    out["C4"] = C4
    print("C4", {k: round(v, 3) for k, v in C4.items()})
    # C5: sensibilidad de la oferta requerida a la fracción de pulpa
    ps = np.linspace(0.25, 0.55, 13)
    out["C5"] = dict(pulp_share=ps.tolist(), fruit_t=[fruit_for_wine(W, s)[0] for s in ps])
    # curva de capacidad: vino posible vs fruta disponible
    ft = np.geomspace(100, 30000, 60)
    out["curve"] = dict(fruit_t=ft.tolist(), wine_hL=[wine_from_fruit(x) * 10 for x in ft],
                        wine_hL_lo=[wine_from_fruit(x, 0.25) * 10 for x in ft], wine_hL_hi=[wine_from_fruit(x, 0.55) * 10 for x in ft])
    json.dump(out, open(f"{RES}/capacidad.json", "w"), default=float, indent=1)
    print("diseño:", {k: round(v, 1) for k, v in b.items()})
