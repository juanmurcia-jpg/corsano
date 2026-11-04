"""
Cinéticas y discretización trapezoidal (Corsano et al. 2004, ec. 8-11), adaptadas a jugo de piña.

- Fermentación alcohólica (S. cerevisiae): Monod + inhibición lineal por etanol + muerte celular.
- Propagación aerobia: Monod + muerte (operación 1 de Corsano).
- Acetificación (Acetobacter): Monod en etanol + inhibición por ácido acético (dos tecnologías).
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import params as p


# ------------------------------------------------------------------ RHS genéricos (numpy y casadi)
def rhs_wine(X, S, P, k, fmax=None):
    """Devuelve dX, dS, dP. Funciona con numpy o casadi (no usa funciones no diferenciables)."""
    inhib = (1 - P / k["Pmax"])
    mu = k["mu_max"] * S / (k["Ks"] + S) * inhib
    dX = mu * X - k["kd"] * X
    dS = -mu * X / k["Yxs"]
    dP = k["Yps"] * mu * X / k["Yxs"]
    return dX, dS, dP


def rhs_prop(X, S, k, Yxs=None):
    Y = k["Yxs"] if Yxs is None else Yxs
    mu = k["mu_max"] * S / (k["Ks"] + S)
    return mu * X - k["kd"] * X, -mu * X / Y


def simulate_wine(k, X0, S0, P0=0.0, T=12.5, n=400):
    f = lambda t, y: np.array(rhs_wine(max(y[0], 0), max(y[1], 0), y[2], k))
    sol = solve_ivp(f, (0, T), [X0, S0, P0], t_eval=np.linspace(0, T, n), rtol=1e-9, atol=1e-11, method="LSODA")
    return sol.t, sol.y


def calibrate_mu(X0=p.X0_REF, S_end=2.0):
    """mu_max tal que, con X0 dado, el azúcar residual a 12.5 h sea S_end (≈ conversión 98.7 %)."""
    k = dict(p.KIN_WINE)
    def g(mu):
        k["mu_max"] = mu
        return simulate_wine(k, X0, p.S_JUICE, T=p.T_REF, n=5)[1][1, -1] - S_end
    mu = brentq(g, 0.05, 2.0, xtol=1e-8)
    k["mu_max"] = mu
    return k


KIN_WINE = calibrate_mu()          # parámetros calibrados por defecto


# ------------------------------------------------------------------ trapezoidal (numpy, para validar)
def trapezoid_wine(k, X0, S0, T, N):
    """Integra con el método trapezoidal implícito (Newton por nodo) para comparar con LSODA."""
    h = T / (N - 1)
    y = np.array([X0, S0, 0.0])
    out = [y.copy()]
    F = lambda v: np.array(rhs_wine(v[0], v[1], v[2], k))
    for _ in range(N - 1):
        z = y.copy()
        for _ in range(50):
            r = z - y - h / 2 * (F(y) + F(z))
            # jacobiano numérico
            J = np.eye(3)
            for i in range(3):
                d = np.zeros(3); d[i] = 1e-7 * max(1, abs(z[i]))
                J[:, i] -= h / 2 * (F(z + d) - F(z)) / d[i]
            dz = np.linalg.solve(J, -r)
            z = z + dz
            if np.max(np.abs(dz)) < 1e-10:
                break
        y = z
        out.append(y.copy())
    return np.linspace(0, T, N), np.array(out).T


# ------------------------------------------------------------------ acetificación
KIN_ACET = {
    # superficie/estática ("current practice", Roda et al. 2017a: 30 d -> 50 g/L, 32 °C)
    "estatica": dict(mu_max=None, Ke=5.0, Amax=70.0, Yxe=0.10, Yae=1.30 * 0.97, kd=0.0005),
    # sumergida tipo acetador (Emde 2017: 40-60 kg/m3/d) -> se calibra a ~50 kg/m3/d medio
    "acetador": dict(mu_max=None, Ke=5.0, Amax=140.0, Yxe=0.10, Yae=1.30 * 0.97, kd=0.002),
}
E0_WINE = P_E0 = p.P_REF        # g/L etanol del vino que entra a acetificación   [T]


def rhs_acet(X, E, A, k):
    mu = k["mu_max"] * E / (k["Ke"] + E) * (1 - A / k["Amax"])
    return mu * X - k["kd"] * X, -mu * X / k["Yxe"], k["Yae"] * mu * X / k["Yxe"]


def simulate_acet(k, X0, E0, T, n=300):
    f = lambda t, y: np.array(rhs_acet(max(y[0], 0), max(y[1], 0), y[2], k))
    sol = solve_ivp(f, (0, T), [X0, E0, 0.0], t_eval=np.linspace(0, T, n), rtol=1e-9, atol=1e-11, method="LSODA")
    return sol.t, sol.y


def calibrate_acet():
    """estática: 50 g/L ácido en 720 h con X0=0.05 g/L; acetador: 50 g/L en 24 h con X0=1 g/L (≈50 kg/m3/d)."""
    out = {}
    for name, (X0, T, A_target) in {"estatica": (0.05, 720.0, 50.0), "acetador": (1.0, 24.0, 50.0)}.items():
        k = dict(KIN_ACET[name])
        def g(mu):
            k["mu_max"] = mu
            return simulate_acet(k, X0, E0_WINE, T, n=5)[1][2, -1] - A_target
        k["mu_max"] = brentq(g, 1e-4, 3.0, xtol=1e-9)
        k["X0"] = X0
        out[name] = k
    return out


KIN_ACET_CAL = calibrate_acet()

if __name__ == "__main__":
    print("mu_max vino calibrado:", KIN_WINE["mu_max"])
    t, y = simulate_wine(KIN_WINE, p.X0_REF, p.S_JUICE, T=12.5)
    print("P(12.5h)=", y[2, -1], " S=", y[1, -1])
    for k, v in KIN_ACET_CAL.items():
        print(k, v["mu_max"])
