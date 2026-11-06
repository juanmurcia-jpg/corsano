"""
Indicadores sociales por diseño (v10). Heinzle et al. (2006, cap. 4.4): empleo, ingresos y valor que queda en el
territorio. En el Bajo Atrato, una zona no interconectada con economía campesina, estos indicadores pesan tanto
como el VPN en la decisión pública.

Indicadores (por año):
  - empleos directos en planta (operarios equivalentes y profesionales) de la nómina del TEA (tea_burk.payroll);
  - empleos en el acopio de hojas (t de hojas por empleo, registro de parámetros) [S];
  - pagos a productores por la fruta de rechazo y servicio de acopio de hojas;
  - masa salarial que queda en la región (fracción local de la nómina) [S];
  - compras locales de insumos (fracción de los costos variables sin fruta) [S];
  - valor que queda en el territorio = suma de los tres anteriores, y por tonelada de fruta.
Salida: results/social.json (la tabla del informe la lee de ahí).
"""
import json, os
import datos as D
import dimensionamiento as dm
import tea_burk as tb

RES = dm.RES
CASES = [("Referencia TRL-9", "E1|Referencia TRL-9 (planta_trl9, 6 200 t)"), ("Diseño v9", "E1|Diseño v9 con parámetros v10"),
         ("Óptimo sin opciones v10", "E1|Óptimo sin opciones v10 (sin hojas ni hub)"), ("Óptimo sin vinagre", "E1|Óptimo sin vinagre"),
         ("Óptimo v10", "E1|Óptimo económico")]


def indicators(r, case):
    p = r["scen"][0]["products"]
    pay = tb.payroll(case["positions"], tb.calendar(case["calendar"]), engineer=case.get("engineer", 1))
    sup = tb.COMMON["supervision"] * pay["total"]
    jobs_plant = pay["workers"] + case.get("engineer", 1)
    jobs_leaves = p.get("hojas_t", 0.0) / D.val("empleos_acopio_hojas")
    fruit_pay = p["fruta_t"] * 1000 * dm.FRUIT_PRICE
    leaves_pay = p.get("hojas_t", 0.0) * dm.ACOPIO_VC
    local_wages = D.val("frac_nomina_local") * (pay["total"] + sup)
    raw_other = sum(x["qty_year"] * x["price"] for x in case["raw"] if not x.get("main") and x.get("key") != "acopio")
    local_buy = D.val("frac_compras_locales") * raw_other
    value = fruit_pay + leaves_pay + local_wages + local_buy
    return dict(empleos_planta=jobs_plant, empleos_acopio=jobs_leaves, empleos_total=jobs_plant + jobs_leaves,
                empleos_por_1000t_fruta=(jobs_plant + jobs_leaves) / p["fruta_t"] * 1000, pago_fruta=fruit_pay, pago_acopio_hojas=leaves_pay,
                nomina_local=local_wages, compras_locales=local_buy, valor_territorio=value, valor_territorio_por_t=value / p["fruta_t"])


def run():
    import tea_dimensionado as td
    d = json.load(open(os.path.join(RES, "dimensionamiento.json")))
    out = {}
    for lab, key in CASES:
        r = d.get(key)
        if r and r.get("scen"):
            out[lab] = indicators(r, td.build_case(r, lab, False))
            o = out[lab]
            print(f"{lab}: {o['empleos_planta']:.0f} empleos en planta + {o['empleos_acopio']:.0f} en acopio; "
                  f"valor en el territorio {o['valor_territorio'] / 1e6:,.0f} MM COP/año", flush=True)
    json.dump(out, open(os.path.join(RES, "social.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    run()
