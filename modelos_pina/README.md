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
| `dimensionamiento.py` | Grossmann (2021), cap. 7, 10 y 14; Maravelias (2021); Moresi (1989b); Morata (2022); Quesada Salas (2013); Emde (2017); Bekatorou (2020) | Dimensionamiento óptimo de equipos acoplado al programa anual, con superestructura del mosto (prensa o decantadora; MF, flotación o centrífuga; MF de lías; HTST, SO₂ o UHPH), lías y retenidos a harina y rutas de vinagre (vino desviado y jugo de cáscara, acetificador Frings), caldera de corona (v8); barrido de precios vino–vinagre; tamaños de catálogo, almacén aséptico, tercer turno; barrido por escala y versión estocástica |
| `tea_dimensionado.py` | Burk (TEA de asaí y coco) | TEA completo con los tamaños óptimos y la producción del programa anual: referencia vs óptimo, con y sin bromelaína, regla por escala; libros Excel verificados |
| `figuras.py`, `figuras_v2.py`, `figuras_v3.py`, `figuras_v4.py`, `gen_informe_v2.py` | — | Figuras 1-36 (incl. Gantt anual, de bodega y del diseño óptimo, TEA dimensionado) e informe HTML (v8) |
| `superestructura_dibujo.py`, `balance_dibujo.py`, `balance_energia_dibujo.py`, `pfd_dibujo.py` | — | Ilustraciones a mano alzada (figs. 33–36): superestructura, balances de masa y de energía, diagrama de flujo del proceso |
| `html2blocks.py`, `make_docx.js` | — | Conversión del informe HTML a Word (`Informe_Corsano_Moresi_TEA_pina_v8.docx`) |
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
python dimensionamiento.py E1 E2 E3 E4 E5          # ~40 min (SCIP)
python pulido_v8.py                                 # pulido de soluciones con tamaños fijos (v8)
python tea_dimensionado.py                          # TEA con tamaños óptimos + libros Excel
python figuras_v3.py && python figuras_v4.py && python gen_informe_v2.py
python html2blocks.py informe.html blocks.json && node make_docx.js blocks.json Informe_Corsano_Moresi_TEA_pina_v8.docx
```

## Advertencia sobre los parámetros

Los parámetros marcados **[S]** en `params.py` (costos unitarios, concentraciones y disponibilidades del hub,
coeficientes del rendimiento de mezcla, precios del etanol y del vinagre, salario) son supuestos ilustrativos.
Las conclusiones **estructurales** (qué arquitectura gana y por qué) son robustas en los barridos reportados.
Las cifras **absolutas** en USD no deben citarse como resultado de la tesis hasta sustituir esos valores por
datos del proyecto.
