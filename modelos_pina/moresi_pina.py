"""
P2-P3: diseño de la unidad de fermentación del vino de piña con el procedimiento de Moresi (1989b).

P2  78 300 hL/año: operación estacional (28 d, perfil de Moresi) vs continua (7 500 h/año); V_F óptimo;
    sistema cerrado (camisa, isotérmico 15 °C) vs abierto (15–22 °C con intercambiador externo).
P3  línea premium (ciclo 15–22 °C, 5 d) vs línea rápida (30 °C, 12,5 h, dato de Murcia Palacios):
    conversión, etanol por t de azúcar (descomposición en rendimiento estequiométrico y conversión),
    unidad de fermentación y costo específico.
Costos: correlaciones f.o.b. de Moresi (recuperadas de su Tabla 3) pasadas a USD 2024 (×1 906 USD/MLit:
1 296 Lit/USD en 1987 y CEPCI 323,8 → 800), factores de módulo de Guthrie de Moresi, y costos operativos de
Colombia/ZNI (electricidad 0,35 USD/kWh, levadura 15 USD/kg, operario 7 500 USD/año).
"""
import json, os
import numpy as np
import moresi as mo
import params as p

RES = os.path.join(os.path.dirname(__file__), "results")
USD = mo.MLIT_TO_USD2024
D = json.load(open(f"{RES}/moresi_R_P1.json"))
X0_EFF = D["R1"]["X0_eff"]
S0 = p.S_JUICE
QY = p.WINE_VOL_YR * 10            # hL/año = 78 300


def get_batch(mode, T0, Ts=22, t_end=240):
    m = mo.Must(S0_gL=S0, X0_gL=X0_EFF, T_in=28.0, rho=1000 + 0.38 * S0)
    return m, mo.ferment(m, T0=T0, mode=mode, Ts=Ts, t_end=t_end, util=0.975, dt_out=0.5)


def heat_batch_fast(VF):
    """Perfil de calor para la línea rápida (30 °C, cinética de Murcia/Monod calibrada, kinetics.py)."""
    from kinetics import KIN_WINE, simulate_wine
    t, y = simulate_wine(KIN_WINE, 1.0, S0, T=12.5, n=101)          # pie de cuba 1 g/L
    dS = -np.gradient(y[1], t)                                        # g/(L h)
    q = dS / 180.16 * 96.6e3 / 3600.0                                 # W/L (96,6 kJ/mol glucosa, ec. 25 de Moresi)
    return t, q * 1000                                                 # W/m3


def unit_cost_usd(QM_h, tproc, VF, closed, qprofile_t, qprofile_Wm3, oper_h, T_in, T0, labour_workers, X0_gL):
    """Pasos 4-10 de Moresi en USD 2024 con costos operativos colombianos.
    Corrección para caudal bajo: el llenado dura V_F/Q_M (Moresi supone 1,5 h porque en vendimia Q_M es alto):
    Δt_c = max(1,5; V_F/Q_M) + t_F + 1,5 (vaciado) + 1 (limpieza)."""
    fill = max(1.5, VF / QM_h)
    dtc = fill + tproc + 2.5
    NF = int(np.ceil(QM_h * dtc / VF - 1e-9))
    rho, cp = 1000 + 0.38 * S0, 3850.0
    QRM = max(rho * QM_h / 3600 * cp * (T_in - T0) / 1000.0, 0.0)
    lag = VF / QM_h
    horizon = np.arange(0, dtc * 4, 0.25); tot = np.zeros_like(horizon)
    q = np.asarray(qprofile_Wm3) * VF / 1000.0
    for k in range(int(4 * dtc / lag) + 2):
        tt = horizon - k * lag; msk = (tt >= 0) & (tt <= qprofile_t[-1])
        tot[msk] += np.interp(tt[msk], qprofile_t, q)
    QRF = float(tot[horizon > dtc].max()) if np.any(horizon > dtc) else float(tot.max())
    QRT = 1.1 * (QRF + QRM); NR = QRT / 3.0
    if closed:
        NE = 0
    else:
        cool = np.asarray(qprofile_Wm3) > 1.0
        NE = max(1, int(np.ceil(NF * np.mean(cool))))
    fob = dict(F=NF * mo.CF(VF, closed), P=NE * 0.35, EF=NE * 3.6, EM=mo.CEM(max(QM_h, 0.5)), R=mo.CR(max(QRT, 20)))
    xiF = mo.XI["F_c"] if closed else mo.XI["F_o"]
    CI = (xiF * fob["F"] + mo.XI["P"] * fob["P"] + mo.XI["E"] * (fob["EF"] + fob["EM"]) + mo.XI["R"] * fob["R"]) * USD
    fab = (xiF * fob["F"] + mo.XI["E"] * (fob["EF"] + fob["EM"])) * USD
    mach = CI - fab
    dep = fab * mo.crf(0.15, 10) + mach * mo.crf(0.15, 5)
    maint = 0.03 * CI
    elec = (NR * 0.6 + 0.75 * NE) * oper_h * p.C_ELEC_ZNI        # 60 % de carga media del compresor [S]
    vol_L = QY * 100.0
    inoc = vol_L * X0_gL / 1000.0 * p.C_ADY
    man = labour_workers * p.SHIFTS * p.WAGE_YR * (oper_h / 7500.0 if oper_h < 7500 else 1.0)
    Co = dep + maint + elec + inoc + man
    return dict(VF=VF, NF=NF, NE=NE, QRT=QRT, NR=NR, CI=CI, dep=dep, maint=maint, elec=elec, inoc=inoc, man=man,
                Co=Co, Cv=Co / vol_L, closed=closed, dtc=dtc, fill_h=fill, QM_h=QM_h)


if __name__ == "__main__":
    out = {}
    # lotes de Moresi para la piña
    m, b_closed = get_batch("closed", 15)
    m, b_open = get_batch("open", 15, Ts=22)
    t975_c = b_closed["tF"]; t975_o = b_open["tF"]
    # línea premium de la tesis: ciclo de 5 d (120 h) con la política abierta 15-22 °C
    m, b_prem = get_batch("open", 15, Ts=22, t_end=120)
    tfast, qfast = heat_batch_fast(1.0)
    out["batches"] = dict(t975_closed=t975_c, t975_open=t975_o,
                          open_profile=dict(t=b_open["t"].tolist(), S=b_open["S"].tolist(), E=b_open["E"].tolist(),
                                            T=b_open["T"].tolist(), X=b_open["X"].tolist(), q=b_open["qR_W_per_m3"].tolist()),
                          closed_profile=dict(t=b_closed["t"].tolist(), S=b_closed["S"].tolist(), E=b_closed["E"].tolist(),
                                              q=b_closed["qR_W_per_m3"].tolist()))
    # --------------------------------------------------------- P3 descomposición del etanol por t de azúcar
    Yx, YE, *_ = mo.yields_T(15.0)
    YE_gg = YE * mo.MW["E"] / mo.MW["S"]
    conv_prem = 1 - b_prem["S_final"] / S0
    E_prem = b_prem["E_final"]
    E_fast = p.P_REF; conv_fast = 1 - 2.0 / S0
    out["P3"] = dict(YE_moresi_15C_gg=YE_gg, Yps_murcia=p.Y_PS, conv_prem=conv_prem, conv_fast=conv_fast,
                     E_prem=E_prem, E_fast=E_fast, ratio=E_prem / E_fast,
                     ratio_from_yield=YE_gg / p.Y_PS, ratio_from_conversion=conv_prem / conv_fast,
                     strip_loss_frac=1 - E_prem / (YE_gg * (S0 - b_prem["S_final"])))
    print("P3", {k: round(v, 4) for k, v in out["P3"].items()})
    # --------------------------------------------------------- P2 diseño: barrido V_F, modos, estacional vs continuo
    rows = []
    cases = {
        "rapida_30C (Murcia)": dict(dtc=12.5, closed=True, qt=tfast, qq=qfast, T0=30.0, X0=1.0, workers=1),
        "premium_abierto_15-22C_5d": dict(dtc=120.0, closed=False, qt=b_prem["t"], qq=b_prem["qR_W_per_m3"], T0=15.0, X0=X0_EFF, workers=2),
        "cerrado_15C_hasta_97.5%": dict(dtc=t975_c, closed=True, qt=b_closed["t"], qq=b_closed["qR_W_per_m3"], T0=15.0, X0=X0_EFF, workers=1),
        "abierto_15-22C_hasta_97.5%": dict(dtc=t975_o, closed=False, qt=b_open["t"], qq=b_open["qR_W_per_m3"], T0=15.0, X0=X0_EFF, workers=2),
    }
    for name, c in cases.items():
        for regime in ("continuo_7500h", "estacional_28d"):
            if regime == "continuo_7500h":
                QM_h = QY / 10.0 / 7500.0; oper = 7500.0
            else:
                QM_h = QY / 10.0 / 20.0 / 24.0; oper = 28 * 24.0
            for VF in (10, 13, 16, 20, 25, 30, 40, 50, 70, 90, 110):   # rango de validez de Moresi (Tabla 2)
                r = unit_cost_usd(QM_h, c["dtc"], VF, c["closed"], c["qt"], c["qq"], oper, 28.0, c["T0"], c["workers"], c["X0"])
                r.update(case=name, regime=regime)
                rows.append(r)
    out["P2"] = rows
    for name in cases:
        for regime in ("continuo_7500h", "estacional_28d"):
            sel = [r for r in rows if r["case"] == name and r["regime"] == regime]
            b = min(sel, key=lambda r: r["Cv"])
            print("P2", name, regime, "VF*", b["VF"], "NF", b["NF"], "llenado h", round(b["fill_h"], 1), "CI", round(b["CI"]), "Cv", round(b["Cv"], 4), "USD/L")
    json.dump(out, open(f"{RES}/moresi_P2_P3.json", "w"), default=float)
