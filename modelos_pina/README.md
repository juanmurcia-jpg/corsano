# Modelos tipo Corsano adaptados a la biorrefinería de piña del Bajo Atrato

Implementación en Python (CasADi + IPOPT/Bonmin) de los cuatro marcos de modelado de
Corsano, Montagna, Iribarren y Aguirre, adaptados a la tesis *Biorrefinería de piña – Bajo Atrato*.

| Archivo | Marco de Corsano | Qué modela en la tesis |
|---|---|---|
| `kinetics.py` | Corsano et al. (2004), ec. 1-11 (Monod + trapecios) | Cinética alcohólica calibrada con Murcia Palacios (2013); acetificación (Roda 2017a / Emde 2017) |
| `m1_superestructura_vino.py` | Corsano et al. (2004; 2006a) — superestructura NLP sin binarias, ZW, series/paralelo | Tren de vino de pulpa (§4.2.3-4.2.4): propagación + fermentación, restricción de llenado |
| `m2_hub_etanol_reciclo.py` | Corsano et al. (2006b) — reciclo de vinaza, penalización ec. 37-38, destilación | Línea de etanol del hub de azúcares (§4.6): mezcla cáscara / hidrolizado / permeado UF |
| `m3_m4_campanas_multiplanta.py` | Corsano et al. (2007) y libro (2009) cap. 4-5; 2006c | Planta multiproducto con campañas mixtas (vino + etanol + vinagre) vs complejo multiplanta |
| `m1_experimentos.py`, `m1_post.py`, `m2_experimentos.py`, `m2_F5.py`, `m34_experimentos.py` | — | Experimentos numéricos (multiarranque, barridos, Pareto, Sobol, MINLP, pulido por estructura) |
| `m1_global.py` | — | Certificación global (SCIP) de un subproblema y comparación con Bonmin B-BB / B-OA e IPOPT |
| `informe.html` | — | Informe técnico con figuras y análisis |
| `moresi.py`, `moresi_experimentos.py`, `moresi_pina.py` | Moresi (1989a, b) | Réplica cinética y de costos (Tabla 3) y aplicación al vino de piña |
| `capacidad.py` | — | Balance fruta → fracciones → productos; oferta EVA 2022; cuellos de botella |
| `planta_trl9.py` | — | Diseño TRL-9: catálogo de tecnologías y dimensionamiento con tamaños discretos |
| `tea_burk.py`, `tea_lineas.py` | Burk (estructura de los TEA de asaí v5.19 y coco v12) | TEA por línea y planta integrada; tornado; Monte Carlo LHS + Iman–Conover |
| `excel_export.py`, `tea_excel_run.py` | — | Libros Excel con fórmulas vivas en `TEA_excel/`, verificados con LibreOffice |
| `planificacion_milp.py` | Grossmann (2021), cap. 6, 7, 10 | MILP de síntesis y planificación mensual: qué procesar con la oferta actual |
| `programacion_stn.py` | Maravelias (2021), cap. 7.2.2 | Programa semanal STN en tiempo discreto (prensa compartida) |
| `estocastico.py` | Grossmann (2021), cap. 14 | Programa estocástico de dos etapas (27 escenarios oferta × precios): RP, EV, EEV, VSS, WS, EVPI y media-CVaR |
| `anual_continuo.py` | Maravelias (2021), cap. 7.3, 8.2, 9 y 10 | Programa anual en tiempo continuo con estacionalidad mensual: reparto de prensa, cambios de modo, inventarios |
| `dimensionamiento.py` | Grossmann (2021), cap. 7, 10 y 14; Maravelias (2021); Moresi (1989b); Morata (2022); Quesada Salas (2013); Emde (2017); Bekatorou (2020); Seguí y Fito (2018); Campos et al. (2020) | Dimensionamiento óptimo de equipos acoplado al programa anual, con superestructura del mosto (prensa o decantadora; MF, flotación o centrífuga; MF de lías; HTST, SO₂ o UHPH), lías y retenidos a harina y rutas de vinagre (vino desviado y jugo de cáscara, acetificador Frings), caldera de corona (v8); pretratamiento de la cáscara con cal y bromelaína del jugo de cáscara por precipitación o UF, con rendimientos de cáscara medidos (v9); barrido de precios vino–vinagre; tamaños de catálogo, almacén aséptico, tercer turno; barrido por escala y versión estocástica |
| `tea_dimensionado.py` | Burk (TEA de asaí y coco) | TEA completo con los tamaños óptimos y la producción del programa anual: referencia vs óptimo, con y sin bromelaína, regla por escala; libros Excel verificados |
| `figuras.py`, `figuras_v2.py`, `figuras_v3.py`, `figuras_v4.py`, `gen_informe_v2.py` | — | Figuras 1-47 (incl. Gantt anual, de bodega y del diseño óptimo, TEA dimensionado) e informe HTML (v12) |
| `superestructura_dibujo.py`, `balance_dibujo.py`, `balance_energia_dibujo.py`, `pfd_dibujo.py`, `layout_dibujo.py`, `gantt_dibujo.py` | — | Ilustraciones a mano alzada (figs. 33–38): superestructura, balances de masa y de energía, diagrama de flujo del proceso, layout de la planta y diagrama de Gantt |
| `pulido_v9.py`, `comparativo_v8_v9.py` | Seguí y Fito (2018); Campos et al. (2020) | Pulido de soluciones con tamaños fijos (caldera, cal y enzima) y comparación v8–v9: descomposición del margen, variantes, precio de equilibrio de la bromelaína, Fig. 39 |
| `datos.py`, `datos/parametros.csv` | Bertran, Tula y Gani (2022); Heinzle et al. (2006) | Registro único de parámetros (valor, rango, distribución, etiqueta [T]/[C]/[L]/[S], fuente); `python datos.py check` compara con las constantes del código |
| `cinetica_jugos.py` | Krishnan et al. (1999); Murcia Palacios (2013); Seguí y Fito (2018); Chen et al. (2020) | Cinética glucosa–xilosa de los jugos de cáscara y de hojas, calibrada; tiempo de proceso de la bodega de jugos (Fig. 41) |
| `localizacion.py` | Bertran et al. (2022, sec. 5.1); Liao et al. (2026) | MILP estilizado de localización: planta central o depósitos de extracción para las hojas; costo de acopio (Fig. 42) |
| `pulido_v10.py`, `comparativo_v9_v10.py` | — | Pulido v10 con tamaños vecinos y comparación v9–v10 (Fig. 45) |
| `pulido_v11.py`, `comparativo_v10_v11.py` | Ebrahimi (2026); Iakovchenko (2026); Ahamed y Li (2026) | v11: panela añadida a los jugos, tope de demanda de vinagre (E8), xantana con residuo de piña, efluentes; pulido y comparación v10–v11 (Fig. 46). Los resultados y figuras de la v10 quedan en `results/v10/` y `figs/v10/` |
| `pulido_v12.py`, `comparativo_v11_v12.py` | Ley 1816 de 2016; Ley 1819 de 2016 (ZOMAC); Palacios et al. (2019) | v12: vino embotellado con impuesto al consumo e IVA, línea de embotellado, tope de demanda de botellas (E9), renta por año según el tamaño de la empresa y el régimen ZOMAC; regla de tiempo máximo de llenado de la bodega (llenado directo en ≤ `tau_llenado_max` o carga desde el almacén de mosto, disyunción por periodo; `check_fill()` revisa soluciones guardadas); pulido y comparación v11–v12 (Fig. 47). Los resultados y figuras de la v11 quedan en `results/v11/` y `figs/v11/` |
| `acv.py` | Heinzle et al. (2006); IPCC AR6 | ACV de la cuna a la puerta: GWP100, energía fósil, agua, MP evitado, línea base sin planta, expansión del sistema, asignación económica (Fig. 40) |
| `social.py` | Heinzle et al. (2006, cap. 4.4) | Empleos, pagos a productores y valor que queda en el territorio |
| `multiobjetivo.py` | Bertran et al. (2022); Liao et al. (2026) | Frente de Pareto margen–GWP por ε-restricción (Fig. 43) |
| `puntos_calientes.py` | Bertran et al. (2022), etapa 3 | Puntos calientes por sección y objetivos de mejora (Fig. 44) |
| `superpro_paquete.py` | Foo (2023), caps. 10–11 | Paquete de verificación en SuperPro Designer (`superpro/`): procedimientos, corrientes, indicadores con tolerancia |
| `html2blocks.py`, `make_docx.js` | — | Conversión del informe HTML a Word (`Informe_Corsano_Moresi_TEA_pina_v12.docx`) |
| `revisor_v13.py`, `revisor_v13_post.py` | Kenkel (2022, OUTDOOR); Kenkel et al. (2022); Arpagaus et al. (2018) | v13, respuesta al revisor: líneas base con la misma superestructura (flujos promedio y secuencial por fracciones, H1), malla de demanda botellas × vinagre con pulido cruzado (H4), bomba de calor del acetificador al secador y barrido de energía fósil (H2), frente margen–huella neta con la pulpa de hojas devuelta al campo y diseños de compromiso por distancia ponderada al ideal (H3); resultados en `results/v13/`, Figs. 48–49 |
| `multiescala_v14.py`, `multiescala_v14_post.py` | Grossmann y Westerberg (2000); Maravelias (2021); Corsano et al. (2004, 2006a); Krishnan et al. (1999) | v14, análisis multiescala: banda cinética no identificable llevada al MILP (U), STN cíclica horaria de la semana pico con los tamaños del óptimo (D1; abril y festivo en dos semanas), modelo 1 al flujo del óptimo (D2) y configuraciones de acopio (T); tabla del valor de cada acople y Figs. 50–51; resultados en `results/v14/` |
| `fig_en.py`, `fig_en_dict.json` | — | Versión en inglés de las figuras: con `FIG_LANG=en`, `figuras.save()` y el dibujo a mano alzada traducen cada texto con el diccionario y guardan en `figs/en/`; meses y días por contexto (`fig_en.months()`, `fig_en.days()`); las cadenas sin entrada quedan en `figs/en/_missing.txt` |
| `params.py` | — | Base de diseño con la procedencia de cada parámetro: [T] tesis, [C] Corsano, [L] literatura, [S] supuesto |

## Reproducir

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install casadi numpy scipy matplotlib pandas SALib pyscipopt
python m1_experimentos.py E1 E3 E4 E5 E6 E7 E8   # ~25 min con 4 núcleos
python m1_post.py V1 E6 E5b
python m2_experimentos.py && python m2_F5.py
python m1_global.py
python m34_experimentos.py
python figuras.py
python moresi_experimentos.py && python moresi_pina.py
python capacidad.py && python tea_lineas.py && python tea_excel_run.py
python planificacion_milp.py && python programacion_stn.py
python figuras_v2.py
python estocastico.py && python anual_continuo.py   # ~10 min (SCIP)
python datos.py check                               # v10: registro de parámetros frente a las constantes del código
python cinetica_jugos.py && python localizacion.py  # v10: tiempos de la bodega de jugos y costo de acopio de hojas
python dimensionamiento.py E1 E2 E3 E4 E5 E6 E7 E8 E9 # ~3 h en serie; en paralelo: DIM_OUT=archivo python dimensionamiento.py E2 (y fusionar)
python pulido_v12.py                                # pulido con tamaños vecinos (acepta grupos: FIJOS E1 E2 ...); en paralelo, DIM_OUT por grupo
CRUCE=1 python pulido_v12.py                        # segunda pasada: cada caso con los mejores diseños de E1 (sin vecinos)
python tea_dimensionado.py                          # TEA con tamaños óptimos + libros Excel
python acv.py && python social.py && python puntos_calientes.py && python superpro_paquete.py && NODE_PATH=$(npm root -g) node superpro_docx.js superpro superpro/Paquete_SuperPro_v12.docx
python multiobjetivo.py                             # frente de Pareto margen–GWP (~40 min)
python comparativo_v11_v12.py decomp && python comparativo_v11_v12.py compare # descomposición v11 → v12 y Fig. 47 (lee results/v11/)
python figuras_v3.py && python figuras_v4.py
for f in superestructura balance balance_energia pfd layout gantt; do NODE_PATH=$(npm root -g) python ${f}_dibujo.py; done
python gen_informe_v2.py
for g in H1 H1b H1c H4a H4b H2 H2p; do python revisor_v13.py $g; done   # v13 (en paralelo por grupo); luego H4q 0/1/2 y H3b
python revisor_v13_post.py                         # TEA de los diseños v13 y Figs. 48–49
for g in U T D2 D1; do python multiescala_v14.py $g; done   # v14 (en paralelo); luego D1b abril y D1b festivo2
python multiescala_v14_post.py                     # tabla de acoples y Figs. 50–51
FIG_LANG=en python figuras.py   # y los demás scripts de figuras: versión en inglés en figs/en/ (ver fig_en.py)
python html2blocks.py informe.html blocks.json && node make_docx.js blocks.json Informe_Corsano_Moresi_TEA_pina_v12.docx
```

## Advertencia sobre los parámetros

Los parámetros marcados **[S]** en `params.py` (costos unitarios, concentraciones y disponibilidades del hub,
coeficientes del rendimiento de mezcla, precios del etanol y del vinagre, salario) son supuestos ilustrativos.
Las conclusiones **estructurales** (qué arquitectura gana y por qué) son robustas en los barridos reportados.
Las cifras **absolutas** en USD no deben citarse como resultado de la tesis hasta sustituir esos valores por
datos del proyecto.
