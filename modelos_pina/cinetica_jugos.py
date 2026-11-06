"""
Cinética de fermentación de los jugos de cáscara y de hojas (v10) y su acoplamiento con el dimensionamiento.

Modelo de Krishnan et al. (1999) para glucosa y xilosa con inhibición por sustrato y por producto, tal como lo
presenta el ejemplo 8.1 («Model the fermentor for second-generation bioethanol production»):
    μ_g = μm,g·G/(Ks,g + G + G²/Ki,g)·(1 − (P/Pm,g)^β_g)          (crecimiento en glucosa; igual en xilosa)
    (1/X)·dX/dt = G/(G+Xy)·μ_g + Xy/(G+Xy)·μ_x
    ν_g = νm,g·G/(K's,g + G + G²/K'i,g)·(1 − (P/P'm,g)^γ_g)        (producción de etanol)
    (1/X)·dP/dt = ν_g + ν_x ;  −dG/dt = ν_g·X/Yps,g ;  −dXy/dt = ν_x·X/Yps,x
Parámetros en datos/parametros.csv (grupo «cinetica»), con la primera rama de Pm, P'm, β y γ (P ≤ 95 g/L).

Acoplamiento (Heinzle et al. 2006, cap. 7: acoplar el modelo de la bioreacción con el modelo de planta):
  - el tiempo de proceso de la bodega de jugo de cáscara y de la de jugo de hojas deja de ser un supuesto y sale
    del tiempo en que se consume el 95 % del azúcar;
  - el rendimiento sigue calibrado con lo medido (Seguí y Fito 2018 para la cáscara; Chen et al. 2020 para las
    hojas): el modelo da el rendimiento ideal y el factor de calibración absorbe pérdidas y contaminación.
Salida: results/cinetica_jugos.json y figs/fig41_cinetica_jugos.png.
"""
import json, os
import numpy as np
from scipy.integrate import solve_ivp
import datos as D

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")


def params(s):
    g = lambda k: D.val(f"kin_{k}_{s}")
    return {k: g(k) for k in ("mu_m", "nu_m", "Ks", "Ks_p", "Ki", "Ki_p", "Pm", "Pm_p", "beta", "gamma", "m", "Yps", "Yxs")}


PG, PX = params("glu"), params("xil")


def rhs(t, y):
    X, G, Xy, P = (max(v, 0.0) for v in y)
    inh = lambda p_, Pm, e: max(0.0, 1 - (p_ / Pm) ** e) if p_ < Pm else 0.0
    mu = lambda S, q: q["mu_m"] * S / (q["Ks"] + S + S * S / q["Ki"]) * inh(P, q["Pm"], q["beta"])
    nu = lambda S, q: q["nu_m"] * S / (q["Ks_p"] + S + S * S / q["Ki_p"]) * inh(P, q["Pm_p"], q["gamma"])
    tot = G + Xy
    wg, wx = (G / tot, Xy / tot) if tot > 1e-9 else (0.0, 0.0)
    mu_t = wg * mu(G, PG) + wx * mu(Xy, PX)
    ng, nx = nu(G, PG), nu(Xy, PX)
    return [mu_t * X, -ng * X / PG["Yps"], -nx * X / PX["Yps"], (ng + nx) * X]


def batch(G0, X0y, X0=1.0, t_end=96.0):
    sol = solve_ivp(rhs, (0, t_end), [X0, G0, X0y, 0.0], method="LSODA", max_step=0.25, dense_output=True, rtol=1e-7, atol=1e-9)
    t = np.linspace(0, t_end, 961)
    Y = sol.sol(t)
    S0 = G0 + X0y
    left = Y[1] + Y[2]
    i95 = int(np.argmax(left <= 0.05 * S0)) if np.any(left <= 0.05 * S0) else len(t) - 1
    return dict(t=t, X=Y[0], G=Y[1], Xy=Y[2], P=Y[3], t95=float(t[i95]), P95=float(Y[3][i95]),
                Y_model=float(Y[3][i95] / (S0 - left[i95])) if S0 - left[i95] > 0 else 0.0, S0=S0)


X0 = 0.5   # g/L de inóculo [S] (≈ 10⁷ células/mL)


def run():
    import params as p
    # calibración del tiempo con un dato medido en piña: el jugo de pulpa (158,8 g/L) llega a 65,3 g/L de etanol en
    # 12,5 h a 30 °C (Murcia Palacios 2013, tesis §4.2.3). La cinética de Krishnan, de una cepa recombinante, es más rápida.
    ref = batch(p.S_JUICE, 0.0, X0=X0)
    i_ref = int(np.argmax(ref["P"] >= p.P_REF)) if np.any(ref["P"] >= p.P_REF) else len(ref["t"]) - 1
    k_t = p.T_REF / float(ref["t"][i_ref])
    # jugo de cáscara: azúcares (sacarosa, glucosa, fructosa) como hexosa; 104 g/kg ≈ 110 g/L
    pj = batch(D.val("azucar_jugo_cascara") * 1.06, 0.0, X0=X0)
    # jugo de hojas: 45 g/L de carbohidratos (Chen 2020): xilosa 16,4 g/L; el resto como hexosa equivalente
    gx = D.val("xilosa_jugo_hojas"); gg = 45.0 - gx
    lj = batch(gg, gx, X0=X0)
    measured_peel = D.val("etanol_jugo_cascara")                          # g/g (Seguí y Fito)
    measured_leaf = D.val("etanol_jugo_hojas") / 1.02 / 45.0              # g etanol / g carbohidrato (Chen)
    out = dict(
        cascara=dict(S0_gL=pj["S0"], t95_h=pj["t95"], P95_gL=pj["P95"], Y_modelo=pj["Y_model"], Y_medido=measured_peel,
                     factor=measured_peel / pj["Y_model"], t95_calibrado_h=pj["t95"] * k_t, t_proc_h=pj["t95"] * k_t + 2.5),
        hojas=dict(S0_gL=lj["S0"], t95_h=lj["t95"], P95_gL=lj["P95"], Y_modelo=lj["Y_model"], Y_medido=measured_leaf,
                   factor=min(1.0, measured_leaf / lj["Y_model"]), t95_calibrado_h=lj["t95"] * k_t, t_proc_h=lj["t95"] * k_t + 2.5,
                   t_medido_h=D.val("t_ferm_hojas")),
        calibracion=dict(t_modelo_jugo_pulpa_h=float(ref["t"][i_ref]), t_medido_h=p.T_REF, factor_tiempo=k_t),
        sensibilidad=[dict(S0=s0, X0=x0, t95=batch(s0, 0.0, X0=x0)["t95"] * k_t) for s0 in (60.0, 90.0, 110.0, 130.0) for x0 in (0.25, 0.5, 1.0)],
    )
    json.dump(out, open(os.path.join(RES, "cinetica_jugos.json"), "w"), indent=1)
    return out, pj, lj


def figure(pj, lj, out):
    k = out["calibracion"]["factor_tiempo"]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from figuras import C, INK2, save
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.3))
    for a, r, tit in ((ax[0], pj, "Jugo de cáscara (hexosas)"), (ax[1], lj, "Jugo de hojas (hexosas + xilosa)")):
        a.plot(r["t"], r["G"], color=C[0], label="hexosas (g/L)")
        if r["Xy"].max() > 0.1:
            a.plot(r["t"], r["Xy"], color=C[3], label="xilosa (g/L)")
        a.plot(r["t"], r["P"], color=C[2], label="etanol (g/L)")
        a.plot(r["t"], r["X"], color=C[4], ls="--", label="células (g/L)")
        a.axvline(r["t95"], color=INK2, ls=":", lw=1)
        a.text(r["t95"] + 0.3, a.get_ylim()[1] * 0.92, f"95 % del azúcar a las {r['t95']:.1f} h\n(calibrado: {r['t95'] * k:.1f} h)", fontsize=8, color=INK2)
        a.set_xlim(0, min(96, r["t95"] * 2.2 + 6)); a.set_xlabel("h (tiempo del modelo)"); a.set_title(tit, fontsize=9); a.legend(fontsize=7.5)
    s = out["sensibilidad"]
    for j, x0 in enumerate((0.25, 0.5, 1.0)):
        pts = [r for r in s if r["X0"] == x0]
        ax[2].plot([r["S0"] for r in pts], [r["t95"] for r in pts], "-o", color=C[j], label=f"inóculo {x0:g} g/L")
    ax[2].set_xlabel("Azúcar inicial (g/L)"); ax[2].set_ylabel("Tiempo calibrado al 95 % (h)"); ax[2].legend(fontsize=8)
    ax[2].set_title("El inóculo pesa más que la concentración inicial", fontsize=9)
    fig.suptitle("Fig. 41  Cinética de Krishnan et al. (1999) para los jugos de cáscara y de hojas: tiempos de fermentación que usa el dimensionamiento v10",
                 fontsize=10, fontweight="bold", x=0.01, ha="left")
    save(fig, "fig41_cinetica_jugos.png")


if __name__ == "__main__":
    out, pj, lj = run()
    print(json.dumps({k: v for k, v in out.items() if k != "sensibilidad"}, indent=1))
    figure(pj, lj, out)
