"""
Registro único de parámetros (v10): datos/parametros.csv.

Cada parámetro tiene valor, rango (mínimo, moda, máximo), distribución, unidad, etiqueta de procedencia
([T] tesis, [C] Corsano, [L] literatura, [S] supuesto) y fuente. Los módulos nuevos de la v10 (hojas, hub, ACV,
social, cinética, localización) leen sus valores de aquí; los módulos anteriores conservan sus constantes y
`python datos.py check` verifica que coincidan con el registro, de modo que el anexo de datos de la tesis y el
código no se separen.
"""
import csv, math, os, sys

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "parametros.csv")
_REG = None


def registro():
    global _REG
    if _REG is None:
        with open(PATH, encoding="utf-8") as fh:
            _REG = {r["clave"]: r for r in csv.DictReader(fh)}
    return _REG


def val(clave):
    """Valor central (float)."""
    return float(registro()[clave]["valor"])


def tri(clave):
    """(mínimo, moda, máximo); si el registro no trae rango, el valor central tres veces."""
    r = registro()[clave]
    v = float(r["valor"])
    f = lambda s, d: float(s) if s not in ("", None) else d
    return f(r["minimo"], v), f(r["moda"], v), f(r["maximo"], v)


def fuente(clave):
    r = registro()[clave]
    return f"[{r['etiqueta']}] {r['fuente']}"


def set_val(clave, v):
    """Cambia un valor en memoria (barridos de sensibilidad); no escribe el archivo."""
    registro()[clave]["valor"] = str(v)


def tabla(grupo=None):
    return [r for r in registro().values() if grupo is None or r["grupo"] == grupo]


# ----------------------------------------------------------------------------- coherencia con el código
def _code_values():
    import capacidad as cp, dimensionamiento as dm, tea_lineas as tl, tea_burk as tb
    out = {
        "oferta_fruta_t": dm.SUPPLY, "frac_pulpa": cp.FR["pulpa"][0], "frac_cascara": cp.FR["cascara"][0],
        "frac_corazon": cp.FR["corazon"][0], "frac_corona": cp.FR["corona"][0], "jugo_pulpa": cp.JUICE_YIELD_PULP,
        "jugo_cascara_frac": cp.Y["peel_juice_frac"], "ms_cascara": cp.Y["peel_dm"], "ms_retenida_torta": cp.Y["cake_dm_ret"],
        "ms_corona": cp.Y["crown_dm"], "azucar_jugo_cascara": dm.PJ_SUGAR, "etanol_jugo_cascara": dm.PJ_ETOH,
        "precio_vino_dimensionado": dm.WINE_PRICE, "TRM": tb.COMMON["TRM"], "tasa_descuento": tb.COMMON["tasa"],
        "horizonte": tb.COMMON["anios"], "fraccion_vendida": tb.COMMON["vendido"], "lang_equivalente": round(dm.LANG, 2),
    }
    for k in ("fruta_kg", "vino_L", "vinagre_L", "bromelaina_kg", "harina_kg", "jugo_cascara_kg", "etanol_L", "elec_kWh", "calor_MJ"):
        out["precio_" + k] = tl.M(k)
    return out


def check(verbose=True):
    bad = []
    for k, v in _code_values().items():
        r = val(k)
        if not math.isclose(r, float(v), rel_tol=1e-3, abs_tol=1e-9):
            bad.append((k, r, v))
    if verbose:
        print(f"{len(registro())} parámetros en el registro; {len(_code_values())} comparados con el código; "
              f"{len(bad)} diferencias" + (":" if bad else "."))
        for k, r, v in bad:
            print(f"  {k}: registro {r} · código {v}")
    return bad


if __name__ == "__main__":
    if "check" in sys.argv[1:]:
        sys.exit(1 if check() else 0)
    for g in sorted({r["grupo"] for r in registro().values()}):
        print(g, len(tabla(g)))
