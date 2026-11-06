"""
Paquete de verificación del diseño óptimo en SuperPro Designer (v12). Foo (ed., 2023), caps. 10 y 11; Bertran, Tula
y Gani (2022), etapa 2: el diseño de la síntesis se verifica con un simulador antes de seguir.

SuperPro no corre en este entorno; el script deja en superpro/ lo necesario para armar el modelo y comparar:
  - procedimientos.csv: cada procedimiento unitario de SuperPro con su equipo, modo (lote o continuo), tamaño,
    tiempo de ciclo, temperatura y la especificación clave (conversión, rendimiento, separación);
  - corrientes.csv: entradas y salidas anuales de la planta (t/año) que el modelo de SuperPro debe reproducir;
  - verificacion.csv: los valores del modelo (balances, servicios, ciclos, producción) con una columna vacía para el
    valor de SuperPro y la tolerancia aceptable;
  - LEEME.md: cómo armar las secciones, qué procedimientos usar y en qué orden comparar.
"""
import csv, json, os
import dimensionamiento as dm
import capacidad as cp
import params as p

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "superpro")


def build(key="E1|Óptimo económico"):
    d = json.load(open(os.path.join(dm.RES, "dimensionamiento.json")))
    r = d[key]; s = r["scen"][0]; pr = s["products"]; sz = r["sizes"]
    os.makedirs(OUT, exist_ok=True)
    F = pr["fruta_t"]; H_st = dm.A2 * 8766; H_c = dm.AC * 8766
    juice = pr["mosto_m3"]; bod = pr["vino_m3"] / dm.WINE_PM; Q = bod / H_c
    fill = dm.VF / Q if Q > 0 else 0
    store_fill = dm.TAU_FILL is not None and fill > dm.TAU_FILL   # v12: lote acumulado en el almacén y cargado con bomba (~1 h)
    has = lambda u: sz.get(u, "no") != "no"
    procs = [
        ("Recepción, lavado y selección", "Generic Box / Washing", "continuo (turnos)", sz["Frente"], f"{H_st:.0f} h/año", "28 °C", "fracciones 45/30/10/15 % (capacidad.FR)"),
        ("Extracción de pulpa", "Belt Filter Press" if sz["Prensa"] != "no" else "Decanter Centrifuge", "continuo (turnos)", sz["Prensa"], "", "28 °C",
         f"jugo {cp.JUICE_YIELD_PULP:.2f} t/t pulpa"),
        ("Maceración enzimática", "Blending Tank", "continuo", "", "", "55 °C", f"{dm.Q_MAC:.0f} MJ/t pulpa con 60 % de recuperación"),
        ("Clarificación", "Disk-Stack Centrifuge" if sz["Clarificación"].startswith("Centr") else sz["Clarificación"], "continuo (turnos)", sz["Clarificación"], "", "",
         f"lodos {dm.CENT_LOSS:.0%} del mosto"),
        ("MF de lías", "Microfiltration", "continuo (turnos)", sz["MF lías"], "", "", f"recupera {dm.LEES_REC:.0%} del jugo"),
        ("Estabilización", "Blending Tank (dosificación)" if sz["Estabilización"].startswith("SO") else "Heat Sterilizer", "continuo", sz["Estabilización"], "", "", "≈ 50 mg/L de SO₂"),
        ("Fermentación alcohólica", "Fermentation (Batch Stoich.) in Fermentor", "lote escalonado", sz["Bodega"],
         (f"carga desde el almacén 1 h (un lote cada {fill:.0f} h) + {p.T_REF} h + 2,5 h" if store_fill else f"llenado {fill:.1f} h + {p.T_REF} h + 2,5 h"), "30 °C", f"{p.P_REF} g/L de etanol a las {p.T_REF} h (Murcia Palacios)"),
        ("Prensa de cáscara", "Belt Filter Press", "continuo (turnos)", sz["Prensa cáscara"], "", "", f"jugo {dm.PJ_FRAC.get(sz.get('Pretratamiento cáscara', 'agua'), 0.578):.3f} t/t"),
        ("Secado de torta y molienda", "Belt Dryer + Grinder", "continuo 24/7", sz["Secador"], f"{H_c:.0f} h/año", "", f"{dm.DRY_W:.2f} t agua/t torta; {dm.Q_CAKE:.0f} MJ/t torta"),
        ("Fermentación del jugo de cáscara", "Fermentation in Fermentor", "lote escalonado", sz.get("Bodega cáscara", "no"),
         f"{dm.T_PEEL:.1f} h (cinética calibrada)", "30 °C", f"{dm.PJ_ETOH} g/g (Seguí y Fito 2018)"),
        ("Acetificación", "Fermentation in Airlift/Stirred Fermentor (semicontinuo)", "semicontinuo 24/7", sz.get("Acetificador", "no"), "descarga del 50 %",
         "30 °C con frío", f"{dm.ACET_PROD} kg/m³·d; ΔH = −493 kJ/mol; {dm.AERATION_KW_M3} kW/m³"),
        ("Caldera de biomasa", "Boiler / Generic Combustor", "continuo 24/7", sz.get("Caldera de corona", "no"), "", "", f"corona {dm.CROWN_MJ_T:.0f} MJ útiles/t; pulpa de hojas {dm.PULP_MJ_T:.0f}"),
    ]
    if has("Embotelladora"):   # v12
        procs.append(("Embotellado del vino", "Filling / Generic Box (llenado, tapado, etiquetado)", "continuo (turnos)", sz["Embotelladora"], "", "",
                      f"{pr.get('botellas', 0):,.0f} botellas de 750 mL al año"))
    if pr.get("azucar_kg", 0) > 1:   # v11
        procs.append(("Dosificación de panela a los jugos", "Blending Tank (disolución)", "continuo", "", "", "30 °C",
                      f"hasta {dm.AZ_MAX * 1000:.0f} g/L de jugo; {dm.A_AZ:.0f} kg de ácido por t de panela"))
    if has("Extractora hojas"):
        procs.append(("Extracción de jugo de hojas", "Screw Press", "continuo (turnos)", sz["Extractora hojas"], "", "", f"jugo {dm.JF_H} t/t; pulpa {dm.PF_H} t/t"))
    if has("Bodega etanol"):
        procs.append(("Fermentación del jugo de hojas (K. marxianus)", "Fermentation in Fermentor", "lote escalonado", sz["Bodega etanol"], f"{dm.T_LEAF} h", "35 °C", f"{dm.E_LJ} kg etanol/t jugo"))
    if has("Destilación"):
        procs.append(("Destilación", "Distillation Column (shortcut)", "continuo", sz["Destilación"], "", "", f"etanol 95 % v/v; {dm.Q_DEST:.1f} MJ/kg"))
    if has("Digestor"):
        procs.append(("Digestión anaerobia", "Anaerobic Digester", "continuo", sz["Digestor"], "TRH 20 d", "35 °C", f"{dm.CH4_T:.2f} kg CH4/t jugo"))
    with open(os.path.join(OUT, "procedimientos.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["Procedimiento", "Procedimiento de SuperPro sugerido", "Modo", "Tamaño del modelo", "Tiempo de ciclo u horas", "Temperatura", "Especificación clave"])
        w.writerows(procs)
    streams = [("Fruta de rechazo (entrada)", F), ("Hojas acopiadas (entrada)", pr.get("hojas_t", 0)), ("Mosto clarificado", juice),
               ("Vino producido (m³)", pr["vino_m3"]), ("Vino vendido (m³)", pr["vino_m3"] - pr.get("vino_a_vinagre_m3", 0)), ("Botellas de 750 mL", pr.get("botellas", 0)),
               ("Vino a vinagre (m³)", pr.get("vino_a_vinagre_m3", 0)), ("Jugo de cáscara a vinagre", pr.get("jugo_cascara_vinagre_t", 0)),
               ("Jugo de hojas a vinagre", pr.get("jugo_hojas_vinagre_t", 0)), ("Panela añadida", pr.get("azucar_kg", 0) / 1000), ("Vinagre al 5 % (m³)", pr.get("vinagre_m3", 0)),
               ("Torta de cáscara al secador", pr.get("torta_t", 0)), ("Harina", pr["harina_t"] + pr.get("harina_lias_t", 0)),
               ("Corona quemada", pr.get("corona_caldera_t", 0)), ("Pulpa de hojas quemada", pr.get("pulpa_hojas_caldera_t", 0)),
               ("Etanol hidratado (L)", pr.get("etanol_L", 0))]
    with open(os.path.join(OUT, "corrientes.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["Corriente", "t/año (o la unidad indicada)"]); w.writerows([(a, round(b, 1)) for a, b in streams])
    V_acet = float(sz["Acetificador"].split()[0]) if has("Acetificador") else 0.0
    checks = [("Calor de proceso total (GJ/año)", pr.get("calor_demanda_MJ", 0) / 1000, "±10 %"),
              ("Calor de la caldera de biomasa (GJ/año)", pr.get("calor_corona_GJ", 0), "±10 %"),
              ("Calor con GLP (GJ/año)", pr.get("calor_glp_MJ", 0) / 1000, "±15 %"),
              ("Electricidad de proceso sin aireación (MWh/año)", pr.get("elec_demanda_kWh", 0) / 1000, "±15 %"),
              ("Aireación del acetificador (MWh/año)", dm.AERATION_KW_M3 * V_acet * dm.AC * 8766 / 1000, "±15 %"),
              ("Frío del acetificador (GJ/año)", pr.get("acido_kg", 0) * dm.ACID_HEAT / 1000, "±10 %"),
              ("Agua evaporada en el secador (t/año)", pr.get("torta_t", 0) * dm.DRY_W, "±5 %"),
              (("Intervalo entre lotes de vino, acumulados en el almacén (h)" if store_fill else "Llenado de un fermentador de vino (h)"), fill, "±10 %"),
              ("Ciclo de la bodega de jugo de cáscara (h)", dm.T_PEEL, "±20 %"),
              ("Vino producido (m³/año)", pr["vino_m3"], "±3 %"), ("Vinagre al 5 % (m³/año)", pr.get("vinagre_m3", 0), "±3 %"),
              ("Harina (t/año)", pr["harina_t"] + pr.get("harina_lias_t", 0), "±5 %"), ("Ocupación pico del acetificador", max(s["util"].get("Acetificador", [0])), "±10 %")]
    with open(os.path.join(OUT, "verificacion.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["Indicador", "Modelo (Python)", "SuperPro", "Diferencia", "Tolerancia"])
        w.writerows([(a, round(b, 2), "", "", c) for a, b, c in checks])
    readme = f"""# Verificación del diseño óptimo v12 en SuperPro Designer

Este paquete lo genera `superpro_paquete.py` a partir de `results/dimensionamiento.json` («{key}»). Sirve para la
etapa 2 del marco de Bertran, Tula y Gani (2022): verificar con un simulador el diseño que eligió la síntesis.

## Cómo armarlo

1. Crear un proceso por lotes (Foo 2023, cap. 10) con cuatro secciones: **Mosto y vino**, **Cáscara y harina**,
   **Vinagre** y **Servicios** (más **Hojas** si el diseño usa la extractora).
2. Registrar los componentes: agua, sacarosa, glucosa, fructosa, xilosa, etanol, ácido acético, CO₂, O₂, biomasa,
   fibra (celulosa como sustituto) y cenizas.
3. Agregar los procedimientos de `procedimientos.csv` con su modo y tamaño. Para la bodega usar fermentadores
   escalonados (*staggered*) con el número de unidades del modelo, como en el ejemplo de ácido cítrico de
   Koulouris (Foo 2023, cap. 11); el tiempo de ciclo de la receta es el llenado de un fermentador. v12: si ese
   llenado supera el tiempo máximo (tau_llenado_max), el mosto se acumula en el almacén aséptico y cada lote se carga
   con bomba en ~1 h; el ciclo de la receta es entonces el intervalo entre lotes.
4. Cargar las estequiometrías: alcohólica con el rendimiento medido (no el teórico); acética 46 g etanol → 60 g
   ácido con 94 % del teórico y ΔH = −493 kJ/mol.
5. Usar las entradas de `corrientes.csv` como base anual y comparar con `verificacion.csv`.

## Qué se compara y por qué

- **Calor y electricidad**: el modelo de Python usa coeficientes por unidad de flujo; SuperPro calcula entalpías.
  Una diferencia mayor que la tolerancia señala qué coeficiente corregir en `datos/parametros.csv`.
- **Ciclos**: el llenado de los fermentadores y el ciclo del jugo de cáscara salen de Moresi y de la cinética
  calibrada; SuperPro los verifica con su programación de lotes.
- **Producción**: vino, vinagre y harina deben coincidir dentro de pocos puntos si los balances están bien cerrados.

Los resultados de SuperPro se escriben en la columna «SuperPro» de `verificacion.csv` y se vuelven a cargar en el
informe. SuperPro no está disponible en el entorno donde corren los modelos; este paso lo hace quien tiene licencia.
"""
    open(os.path.join(OUT, "LEEME.md"), "w", encoding="utf-8").write(readme)
    print("superpro/:", len(procs), "procedimientos,", len(streams), "corrientes,", len(checks), "indicadores")


if __name__ == "__main__":
    build()
