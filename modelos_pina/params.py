"""
Base de diseño para los modelos tipo Corsano adaptados a la biorrefinería de piña (Bajo Atrato).

Cada parámetro lleva su procedencia:
  [T]  dato tomado de la tesis (sección indicada)
  [C]  dato tomado de Corsano et al. (2004, 2006a, 2006b, 2007)
  [L]  valor típico de literatura de bioprocesos (no específico de piña)
  [S]  SUPUESTO ILUSTRATIVO de este trabajo -> debe reemplazarse por dato de proyecto
"""

# ----------------------------------------------------------------------------- horizonte
H = 7500.0            # h/año de operación                                   [C] (Corsano usa 7500 h)
CCF = 0.225           # factor de cargo de capital (0.10 amortización+0.125 mant.) [C] 2006b

# ----------------------------------------------------------------------------- tren de pulpa: vino
WINE_VOL_YR = 78_300 * 100 / 1000.0   # m3 vino/año  (78 300 hL/año)        [T] §4.2.5
S_JUICE = 158.83      # g/L azúcar fermentable del jugo (fruta de rechazo)    [T] §3.2.1 (Murcia Palacios 2013)
P_REF = 65.31         # g/L etanol alcanzado en 12.5 h, 30 °C, pH 4.5          [T] §4.2.3
T_REF = 12.5          # h                                                     [T] §4.2.3
Y_PS = 65.31 / (158.83 - 2.0)  # =0.4164 g/g; la tesis redondea a 0.41 [T] §4.2.3 (consistente con S_res=2 g/L)
PR_ETOH = WINE_VOL_YR * P_REF / H      # kg etanol/h que debe salir del tren (≈68.2)
S_RES_MAX = 4.0       # g/L azúcar residual máximo en vino seco               [L]

# cinética alcohólica (Monod + inhibición lineal por etanol + muerte)  — calibrada en kinetics.py
KIN_WINE = dict(mu_max=None,   # se calibra para reproducir P_REF a T_REF
                Ks=1.0,        # g/L                                          [L]
                Pmax=95.0,     # g/L etanol de inhibición total               [L]
                Yxs=0.08,      # g biomasa/g azúcar (anaerobio)               [L]
                kd=0.01,       # 1/h                                          [L]
                Yps=Y_PS)
X0_REF = 0.20         # g/L levadura seca activa en el ensayo de referencia (20 g/hL)  [S]

# propagación aerobia de levadura (operación 1 de Corsano: "biomass fermentation")
KIN_PROP = dict(mu_max=0.45,   # 1/h                                          [C]≈0.5 / [L]
                Ks=5.0,        # g/L                                          [L]
                Yxs=0.45,      # g/g (aerobio, sin Crabtree si S0≤20 g/L)     [L]
                kd=0.02)       # 1/h                                          [C]
S0_PROP_MAX = 20.0    # g/L  límite para evitar efecto Crabtree               [L]
KW_AIR = 0.5          # kW/m3 de aireación en propagación                     [L]

# ----------------------------------------------------------------------------- costos
# costo instalado de fermentador:  C = A_FERM * V^B_FERM   (USD, V en m3)
A_FERM = 25_000.0     #                                                       [S]
B_FERM = 0.60         # regla de los seis décimos usada en la tesis           [T] §4.2.4
A_PROP = 1.5 * A_FERM # propagador aireado y estéril más caro                 [S]
C_JUICE = 40.0        # USD/m3 jugo de pulpa de rechazo                       [S]
C_WATER = 0.05        # USD/m3                                                [C]
C_ADY = 15.0          # USD/kg levadura seca activa                           [L] (Corsano: 10 USD/kg inóculo)
C_ELEC_ZNI = 0.35     # USD/kWh, generación diésel en ZNI                    [S] (cf. tesis §1.2)
TAU_FILL = 12.5       # h, tiempo de llenado máximo por defecto (sin restricción activa)

# ----------------------------------------------------------------------------- hub de azúcares (modelo 2)
# tres corrientes candidatas del hub (tesis §4.6) + vinaza reciclada + agua
HUB = {
    #            S [g/L]  costo [USD/m3]  disponibilidad [m3/h]   procedencia
    "peel":   dict(S=110.0, c=6.0,  Fmax=3.0),     # jugo de cáscara      [T] §4.4 (cualitativo) / [S] valores
    "hydro":  dict(S=60.0,  c=9.0,  Fmax=4.0),     # hidrolizado hojas/corona [T] §4.5 / [S]
    "perm":   dict(S=80.0,  c=3.0,  Fmax=1.5),     # permeado UF tallo+corazón [T] §4.3 / [S]
}
# rendimiento biomasa/sustrato en función de la mezcla: análogo directo de la ec. 6 de Corsano (2004)
# Y = sum a_k x_k + sum b_kl x_k x_l     (x: fracción del azúcar aportado por cada fuente)       [S] coeficientes
YXS_BLEND = dict(peel=0.40, hydro=0.28, perm=0.38, vin=0.22,
                 peel_hydro=0.10, peel_perm=0.05, hydro_perm=0.12, perm_vin=0.08)
ALPHA_INHIB_HYDRO = 0.45   # pérdida relativa de mu_max por fracción de hidrolizado (furfural/HMF) [S]
PR_ETOH_HUB = 40.0         # kg/h etanol anhidro de la línea de etanol del hub              [S]
# penalización de vinaza no reciclada (Corsano 2006b, ec. 37-38; Bates 1981)
ZF = 2.0                   # USD/m3 por volumen                                             [S]≈[C]
ZE_ZT = 0.9                # USD/m3 recepción + tratamiento primario                        [S]
ZBO = 0.10                 # USD/m3 de oxidación biológica por unidad de (DBO/Os)            [S]
NF_VIN = 15.0              # kg/m3 carga orgánica NO fermentable de la vinaza (glicerol, ácidos) [S]
X0_MIN_FERM = 1.0          # g/L levadura mínima al inicio de la fermentación (pitching)      [L]
OS = 0.2                   # kg/m3 concentración de agua residual sedimentada               [C]
C_STEAM = 30.0             # USD/t vapor (caldera de biomasa/gasificador)                   [S]
DH_VAP = 1046.7            # kJ/kg azeótropo                                                 [C]
ALPHA_LH = 2.75            # volatilidad relativa azeótropo/agua                             [C]

# ----------------------------------------------------------------------------- precios (modelos 3-4)
PRICE = dict(wine=0.40,      # USD/L vino (≈400 USD/t, "illustrative")      [T] §4.2.5
             ethanol=0.85,   # USD/kg etanol anhidro                        [S]
             vinegar=0.55)   # USD/L vinagre 5 % p/v                        [S]
WAGE_YR = 7_500.0            # USD/año costo total de un operario en Chocó [S]
SHIFTS = 4.2                 # dotaciones para 24/7                         [L]
