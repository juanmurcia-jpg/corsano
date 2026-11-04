"""
MODELO 5 — Modelo de Moresi (1989a, b) para fermentadores de vino blanco y diseño óptimo de la unidad
de fermentación, replicado y adaptado al jugo de piña.

Moresi (1989a), cap. 8: estequiometría (ec. 1-8), cinética de Monod con inhibición por sustrato y etanol y
muerte celular (ec. 9), parámetros dependientes de T (Tabla 1), fase de latencia (ec. 10-11).
Moresi (1989b), cap. 9: balances dinámicos (ec. 12-26), carga de refrigeración (ec. 27-28, Tabla 1),
arrastre de etanol por CO2 (ec. 29-42), procedimiento de diseño de 11 pasos (ec. 43-48), costos (Tabla 3).

Simplificaciones declaradas:
  * se ignora el tiempo de saturación de CO2 (tau -> 0): q_C = V_F · Y_C · r_X / Y_X desde el inicio;
  * calores latentes y capacidades caloríficas molares de literatura (Perry) para el término de arrastre.
"""
import numpy as np
from scipy.integrate import solve_ivp

MW = dict(S=180.16, X=23.75, E=46.07, W=18.015, C=44.01, G=92.09, A=60.05)  # CH1.75O0.45N0.2 = 23.75
TR_KIN = 289.0          # K, referencia de la Tabla 1 (Moresi 1989a)
TR_H = 25.0             # °C, referencia entálpica (Moresi 1989b, Tabla 2)
P_TOP = 103.0           # kPa
LAM = dict(E=42.32e3, W=43.99e3)          # J/mol a 25 °C [L]
CPV = dict(C=37.1, E=65.4, W=33.6)        # J/mol/K vapor [L]


def params_T(T):
    """Tabla 1 de Moresi (1989a). T en °C."""
    TK = T + 273.15
    a = 1 / TK - 1 / TR_KIN
    vM = 0.812 * np.exp(-7161 * a) - 0.187 * np.exp(-16551 * a)
    KE = 0.875 * np.exp(5938 * a)
    Ks = 0.988 * np.exp(5938 * a)
    KSI = 0.159 * np.exp(5938 * a)
    KD = 913.0
    Yx = 0.052 + 2.9e-3 * T
    YE = 1.897 - 1.46e-3 * T
    YC = 1.961 - 3.14e-3 * T
    return vM, KE, Ks, KSI, KD, Yx, YE, YC


def yields_T(T):
    vM, KE, Ks, KSI, KD, Yx, YE, YC = params_T(T)
    YG = 2 * (YC - YE) - 0.125 * Yx                      # ec. 22
    YA = 3 - 0.3126 * Yx - 3.5 * YC + 2 * YE             # ec. 23
    YW = 0.55 * Yx - YC + YE                             # ec. 24
    dHR = (194.76 + 2.48 * Yx + 193.37 * YE - 240.85 * YC) / Yx   # kJ/mol biomasa (ec. 25)
    return Yx, YE, YC, YG, YA, YW, dHR


def strip_ratios(E, W, T):
    """H_E, H_W: moles de etanol y agua arrastrados por mol de CO2 (ec. 35-42)."""
    xE = E / (E + W); xW = 1 - xE
    AEW, AWE = 0.67, 0.42
    gE = 10 ** (AEW / (1 + AEW * xE / (AWE * xW + 1e-12)) ** 2)
    gW = 10 ** (AWE / (1 + AWE * xW / (AEW * xE + 1e-12)) ** 2)
    PsE = np.exp(19.729 - 4243.08 / (T + 245.54))      # mmHg
    PsW = np.exp(18.613 - 4004.0 / (T + 234.24))       # mmHg
    P = P_TOP * 7.50062                                 # kPa -> mmHg
    yE = gE * xE * PsE / P; yW = gW * xW * PsW / P
    yC = max(1 - yE - yW, 1e-6)
    return yE / yC, yW / yC


class Must:
    def __init__(self, S0_gL=220.0, N0_gL=1.2, X0_gL=0.2, rho=1080.0, cp=3850.0, T_in=25.0):
        self.S0 = S0_gL / MW["S"]; self.X0 = X0_gL / MW["X"]; self.N0 = N0_gL
        self.rho, self.cp, self.T_in = rho, cp, T_in
        self.W0 = (rho - S0_gL - 10.0) / MW["W"]          # mol/L de agua (10 g/L otros solutos)
        self.tlag = 3.12 * X0_gL ** (-0.585)               # ec. 11


def rhs(t, y, must, mode, ctrl):
    """y = [X, S, E, W, T, Qcum] (mol/L, °C, J/L).
    Separación crecimiento/muerte: r_X = r_g - r_d, con r_g = v_M S X /((1+E/K_E)(K_S+S+S²/K_SI)) y r_d = (E/K_D) X.
    El consumo de sustrato, la formación de etanol y CO2 y el calor siguen a r_g (Moresi usa r_X, que con
    r_X < 0 haría 'devolver' azúcar y etanol; con r_X > 0 ambas formas coinciden salvo el término de muerte)."""
    X, S, E, W, T, _ = y
    S = max(S, 0.0)
    vM, KE, Ks, KSI, KD, Yx, YE, YC = params_T(T)
    Yx, YE, YC, YG, YA, YW, dHR = yields_T(T)
    if t <= must.tlag:
        rg, rd = 0.0, 0.0
    else:
        rg = vM * S / ((1 + E / KE) * (Ks + S + S * S / KSI)) * X
        rd = E / KD * X
    qc = YC * rg / Yx
    HE, HW = strip_ratios(max(E, 1e-9), W, T)
    dS = -rg / Yx
    dE = YE * rg / Yx - qc * HE
    dW = YW * rg / Yx - qc * HW
    rhocp = must.rho * must.cp / 1000.0
    gen = dHR * 1000.0 * rg
    strip = qc * (CPV["C"] * (T - TR_H) + HE * (LAM["E"] + CPV["E"] * (T - TR_H)) + HW * (LAM["W"] + CPV["W"] * (T - TR_H)))
    if mode == "closed":
        qR = gen - strip
    elif mode == "open":
        qR = ctrl["qR"](t, T, gen - strip, rhocp)
    else:
        qR = 0.0
    dT = (gen - strip - qR) / rhocp
    return [rg - rd, dS, dE, dW, dT, qR]


def ferment(must, T0=15.0, mode="closed", Ts=22.0, dtR=4.0, t_end=400.0, util=0.85, dt_out=0.25):
    """Simula un lote. Devuelve diccionario con perfiles y el tiempo para consumir 'util' del azúcar."""
    state = dict(cooling=False, t_start=None)
    def qR_open(t, T, net, rhocp):
        if not state["cooling"] and T >= Ts:
            state["cooling"] = True; state["t_start"] = t
        if state["cooling"]:
            if T <= T0 + 1e-6 or t - state["t_start"] > dtR * 1.5:
                state["cooling"] = False
                return 0.0
            return net + rhocp * (Ts - T0) / dtR         # baja de Ts a T0 en dtR horas (5 °C máx por paso)
        return 0.0
    ctrl = dict(qR=qR_open)
    y0 = [must.X0, must.S0, 0.0, must.W0, T0, 0.0]
    ts = np.arange(0, t_end + dt_out, dt_out)
    Y = np.zeros((len(ts), 6)); Y[0] = y0
    y = np.array(y0, float)
    for i in range(1, len(ts)):           # integración por pasos (permite el control conmutado)
        sol = solve_ivp(rhs, (ts[i - 1], ts[i]), y, args=(must, mode, ctrl), method="LSODA", rtol=1e-7, atol=1e-10)
        y = sol.y[:, -1]; Y[i] = y
    X, S, E, W, T, Qc = Y.T
    S = np.maximum(S, 0)
    idx = np.argmax(S <= (1 - util) * must.S0) if np.any(S <= (1 - util) * must.S0) else len(ts) - 1
    qR = np.gradient(Qc, ts)                              # J/(L h)
    return dict(t=ts, X=X * MW["X"], S=S * MW["S"], E=E * MW["E"], T=T, qR_W_per_m3=qR * 1000 / 3600,
                tF=float(ts[idx]), E_at_tF=float(E[idx] * MW["E"]), S_at_tF=float(S[idx] * MW["S"]),
                E_final=float(E[-1] * MW["E"]), S_final=float(S[-1] * MW["S"]))


# ----------------------------------------------------------------------------- costos de Moresi (Tabla 3)
# Costos f.o.b. (MLit, CEPCI julio 1987) recuperados de la Tabla 3 de Moresi (1989b) y ajustados:
#   fermentador abierto (sin camisa):    C_F = a V^n con (30 m3: 6.932; 40 m3: 8.523)  -> n = 0.717
#   fermentador cerrado (con camisa):    110 m3: 32.08 (un solo punto; mismo exponente supuesto)
#   refrigeración:                        C_R(Q_RT) ajuste log-log a (288, 117.8), (517, 196.1), (1000, 364)
#   intercambiador de placas p/ fermento: 3.85 (60 000 hL) y 3.32 (120 000 hL) por unidad -> 3.6
#   preenfriador del mosto C_EM(Q_M):     (6.25 m3/h: 3.1), (12.5: 4.6), (25: 7.7)
#   bomba centrífuga:                     0.375 / 0.32 por unidad -> 0.35
XI = dict(F_c=2.00, F_o=2.13, E=1.78, P=1.78, R=2.13)     # factores de módulo de Guthrie (Tabla 2)
_nF = np.log(8.523 / 6.932) / np.log(40 / 30)
_aF_o = 8.523 / 40 ** _nF
_aF_c = 32.08 / 110 ** _nF
_cr = np.polyfit(np.log([288, 517, 1000]), np.log([117.8, 196.1, 364.0]), 1)
_cem = np.polyfit(np.log([6.25, 12.5, 25.0]), np.log([3.1, 4.6, 7.7]), 1)
LIT_PER_USD_1987 = 1296.0                 # promedio 1987 [L]
CEPCI_1987, CEPCI_2024 = 323.8, 800.0     # [L]
MLIT_TO_USD2024 = 1e6 / LIT_PER_USD_1987 * CEPCI_2024 / CEPCI_1987


def CF(V, closed):
    return (_aF_c if closed else _aF_o) * V ** _nF


def CR(Q):
    return float(np.exp(np.polyval(_cr, np.log(Q))))


def CEM(Qm_h):
    return float(np.exp(np.polyval(_cem, np.log(Qm_h))))


def crf(i, n):
    return i * (1 + i) ** n / ((1 + i) ** n - 1)


def design_unit(Qp_hL, VF, closed, batch, must, T0=15.0, Ts=22.0, dtR=4.0, season_days=28.0,
                peak_factor=1 / 20, util=0.85, year_round=False, H=7500.0, elec_price_lit=120.0,
                yeast_lit_kg=5000.0, labour="moresi"):
    """Procedimiento de 11 pasos de Moresi (1989b). Devuelve el desglose de costos (MLit, CEPCI 1987)."""
    tF = batch["tF"]
    dtc = tF + 1.5 + 1.5 + 1.0                               # ec. 43
    if year_round:                                           # adaptación: operación continua todo el año
        QM_h = Qp_hL / 10.0 / H                               # m3/h constante
        oper_h = H
    else:
        QM_h = Qp_hL / 10.0 * peak_factor / 24.0              # m3/h de pico (Fig. 2)
        oper_h = season_days * 24.0
    NF = int(np.ceil(QM_h * dtc / VF - 1e-9))                 # ec. 44
    QRM = must.rho * QM_h / 3600 * must.cp * (must.T_in - T0) / 1000.0   # kW (ec. 45)
    # carga de los fermentadores: superposición de NF lotes desfasados VF/QM horas
    t = batch["t"]; q = batch["qR_W_per_m3"] * VF / 1000.0    # kW por fermentador
    lag = VF / QM_h
    horizon = np.arange(0, dtc * 3, 0.25)
    tot = np.zeros_like(horizon)
    for k in range(int(3 * dtc / lag) + 2):
        tt = horizon - k * lag
        m = (tt >= 0) & (tt <= t[-1])
        tot[m] += np.interp(tt[m], t, q)
    QRF = float(tot[horizon > dtc].max()) if np.any(horizon > dtc) else float(tot.max())
    QRT = 1.1 * (QRF + QRM)                                   # ec. 46
    NR = QRT / 3.0                                            # COP = 3 (Tabla 3: N_R = Q_RT/3)
    if closed:
        NE = 0
    else:   # número de fermentadores enfriándose simultáneamente (cada uno con su intercambiador)
        cool = batch["qR_W_per_m3"] > 1.0
        frac = cool.mean() * (batch["t"][-1] / dtc) if dtc > 0 else 0
        frac = np.mean(cool[batch["t"] <= dtc]) if np.any(batch["t"] <= dtc) else 0.2
        NE = max(1, int(np.ceil(NF * frac)))
    fob = dict(F=NF * CF(VF, closed), P=NE * 0.35, EF=NE * 3.6, EM=CEM(QM_h), R=CR(QRT))
    CI = (XI["F_c"] if closed else XI["F_o"]) * fob["F"] + XI["P"] * fob["P"] + XI["E"] * (fob["EF"] + fob["EM"]) + XI["R"] * fob["R"]
    fabricated = (XI["F_c"] if closed else XI["F_o"]) * fob["F"] + XI["E"] * (fob["EF"] + fob["EM"])
    machinery = XI["R"] * fob["R"] + XI["P"] * fob["P"]
    dep_fab = fabricated * crf(0.15, 10); dep_mach = machinery * crf(0.15, 5)
    maint = 0.03 * CI
    elec = (NR + 0.75 * NE) * oper_h * elec_price_lit / 1e6
    vol_L = Qp_hL * 100.0
    inoc = vol_L * must.X0 * MW["X"] / 1000.0 * yeast_lit_kg / 1e6
    days = oper_h / 24.0
    man = (2 * 16 * 30000 + 8 * 50000) * days / 1e6 * (1 if closed else 2) if labour == "moresi" else 0.0
    Co = dep_fab + dep_mach + maint + elec + inoc + man
    return dict(Qp_hL=Qp_hL, VF=VF, closed=closed, tF=tF, dtc=dtc, NF=NF, NE=NE, QRF=QRF, QRM=QRM, QRT=QRT, NR=NR,
                fob=fob, CI=CI, dep_fab=dep_fab, dep_mach=dep_mach, maint=maint, elec=elec, inoc=inoc, man=man,
                Co=Co, Cv_lit_L=Co * 1e6 / vol_L, QM_h=QM_h)


MORESI_TABLE3 = {   # valores publicados (Moresi 1989b, Tabla 3)
    30000: dict(closed=True, VF=110, tF=81, dtc=85, NF=5, QRT=288, NR=96, NFCF=160.4, CEM=3.1, CR=117.8, CI=577.3,
                dep_fab=65.0, dep_mach=74.9, maint=17.3, elec=7.7, inoc=3, man=38.1, Co=206.0, Cv=68.7),
    60000: dict(closed=False, VF=40, tF=79, dtc=83, NF=26, QRT=517, NR=172, NFCF=221.6, CEM=4.6, CR=196.1, CI=927.8,
                NE=4, dep_fab=101.1, dep_mach=125.4, maint=27.8, elec=18.4, inoc=6, man=76.2, Co=354.9, Cv=59.1),
    120000: dict(closed=False, VF=30, tF=78, dtc=82, NF=69, QRT=1000, NR=334, NFCF=478.3, CEM=7.7, CR=364.0, CI=1872.4,
                 NE=10, dep_fab=217.4, dep_mach=233.0, maint=56.2, elec=26.9, inoc=12, man=76.2, Co=621.7, Cv=51.8),
}

if __name__ == "__main__":
    m = Must()
    for mode in ("closed", "open"):
        b = ferment(m, mode=mode, t_end=200)
        print(mode, "tF(85%)=", b["tF"], "E(tF)=", round(b["E_at_tF"], 1), "E_final=", round(b["E_final"], 1),
              "S_final=", round(b["S_final"], 1), "Tmax=", round(b["T"].max(), 2), "qRmax W/m3=", round(b["qR_W_per_m3"].max(), 1))
