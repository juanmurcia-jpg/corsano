"""
Experimentos del Modelo 5 (Moresi 1989a, b).

R1 réplica cinética: t_F(85 %) cerrado/abierto vs Tabla 3; calibración de un solo parámetro (inóculo viable)
R2 réplica del modelo de costos (pasos 4-10) con los t_F publicados: cada partida vs Tabla 3
R3 curva C_v vs V_F para 30 000 / 60 000 / 120 000 hL (análogo a la Fig. 5) con la cinética calibrada
P1 mosto de piña (158,83 g/L, 28 °C de entrada): tiempos para 85 % y 97,5 % de consumo según T y modo;
   contraste con el dato de Murcia Palacios (12,5 h a 30 °C)
P2 diseño de la unidad de fermentación de piña (78 300 hL/año) con el procedimiento de Moresi:
   operación estacional (28 d, como Moresi) vs continua (7 500 h/año); V_F óptimo; cerrado vs abierto
P3 línea premium (ciclo 15–22 °C, 5 d) vs línea rápida: conversión, etanol por t de azúcar, costo
"""
import json, os, time
import numpy as np
from scipy.optimize import brentq
from multiprocessing import Pool
import moresi as mo
import params as p

RES = os.path.join(os.path.dirname(__file__), "results")
USD = mo.MLIT_TO_USD2024


def batch(args):
    S0, X0, T0, mode, t_end, util, T_in, Ts = args
    m = mo.Must(S0_gL=S0, X0_gL=X0, T_in=T_in, rho=1000 + 0.38 * S0)
    b = mo.ferment(m, T0=T0, mode=mode, Ts=Ts, t_end=t_end, util=util, dt_out=0.5)
    b["args"] = args
    return b


def t_util(b, frac, S0):
    S = np.array(b["S"]); t = np.array(b["t"])
    ok = S <= (1 - frac) * S0
    return float(t[np.argmax(ok)]) if ok.any() else np.nan


def slim(b):
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in b.items()}


if __name__ == "__main__":
    out = {}
    t0 = time.time()
    # ---------------------------------------------------------------- R1
    with Pool(4) as pl:
        nominal = pl.map(batch, [(220, 0.2, 15, "closed", 200, 0.85, 25, 22), (220, 0.2, 15, "open", 200, 0.85, 25, 22)])
    def tF_closed(X0):
        return batch((220, X0, 15, "closed", 200, 0.85, 25, 22))["tF"] - 81.0
    X0_eff = brentq(tF_closed, 0.03, 0.2, xtol=2e-3)
    with Pool(4) as pl:
        cal = pl.map(batch, [(220, X0_eff, 15, "closed", 200, 0.85, 25, 22), (220, X0_eff, 15, "open", 200, 0.85, 25, 22),
                             (220, X0_eff, 15, "free", 200, 0.85, 25, 22)])
    out["R1"] = dict(X0_eff=X0_eff, nominal=[slim(b) for b in nominal], calibrated=[slim(b) for b in cal],
                     published=dict(closed=81, open=79))
    print("R1 X0_eff", round(X0_eff, 4), "nominal", nominal[0]["tF"], nominal[1]["tF"], "cal", cal[0]["tF"], cal[1]["tF"], flush=True)
    # ---------------------------------------------------------------- R2 (con t_F publicados y lote calibrado para la forma de q_R)
    rows = []
    for Qp, ref in mo.MORESI_TABLE3.items():
        b = cal[0] if ref["closed"] else cal[1]
        bb = dict(b); bb["tF"] = ref["tF"]
        bb = {k: (np.array(v) if isinstance(v, list) else v) for k, v in bb.items()}
        d = mo.design_unit(Qp, ref["VF"], ref["closed"], bb, mo.Must(X0_gL=0.2))
        rows.append(dict(Qp=Qp, ref=ref, model={k: (v if not isinstance(v, dict) else v) for k, v in d.items()}))
        print("R2", Qp, "NF", d["NF"], ref["NF"], "QRT", round(d["QRT"]), ref["QRT"], "CI", round(d["CI"], 1), ref["CI"],
              "Co", round(d["Co"], 1), ref["Co"], "Cv", round(d["Cv_lit_L"], 1), ref["Cv"], flush=True)
    out["R2"] = rows
    # ---------------------------------------------------------------- R3 curva Cv(VF)
    r3 = []
    for Qp in (30000, 60000, 120000):
        for closed in (True, False):
            b = cal[0] if closed else cal[1]
            bb = {k: (np.array(v) if isinstance(v, list) else v) for k, v in b.items()}
            for VF in (10, 20, 30, 40, 50, 70, 90, 110):
                d = mo.design_unit(Qp, VF, closed, bb, mo.Must(X0_gL=0.2))
                r3.append(dict(Qp=Qp, closed=closed, VF=VF, Cv=d["Cv_lit_L"], NF=d["NF"], NE=d["NE"], QRT=d["QRT"]))
    out["R3"] = r3
    print("R3 listo", flush=True)
    # ---------------------------------------------------------------- P1 piña
    S0 = p.S_JUICE
    jobs = []
    for T0 in (15, 18, 20, 22, 25, 28, 30):
        jobs.append((S0, X0_eff, T0, "closed", 240, 0.975, 28, 22))
    for (T0, Ts) in ((15, 22), (18, 25), (20, 27)):
        jobs.append((S0, X0_eff, T0, "open", 240, 0.975, 28, Ts))
    jobs.append((S0, 0.2, 30, "closed", 240, 0.975, 28, 22))       # inóculo nominal, condición de Murcia
    with Pool(4) as pl:
        P1 = pl.map(batch, jobs)
    p1 = []
    for b in P1:
        S0_, X0_, T0_, mode_, *_ , Ts_ = b["args"]
        p1.append(dict(T0=T0_, mode=mode_, Ts=Ts_, X0=X0_, t85=t_util(b, 0.85, S0), t975=t_util(b, 0.975, S0),
                       E_975=float(np.interp(t_util(b, 0.975, S0), b["t"], b["E"])) if not np.isnan(t_util(b, 0.975, S0)) else np.nan,
                       E_125=float(np.interp(12.5, b["t"], b["E"])), S_125=float(np.interp(12.5, b["t"], b["S"])),
                       E_final=b["E_final"], profile=slim(b) if (T0_ in (15, 20, 30) or mode_ == "open") else None))
        print("P1", mode_, T0_, Ts_, X0_, "t85", p1[-1]["t85"], "t97.5", p1[-1]["t975"], "E(12.5h)", round(p1[-1]["E_125"], 1), flush=True)
    out["P1"] = p1
    json.dump(out, open(f"{RES}/moresi_R_P1.json", "w"), default=float)
    print("total", round(time.time() - t0), "s")
