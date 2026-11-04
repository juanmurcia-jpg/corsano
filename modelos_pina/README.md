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
| `figuras.py` | — | Figuras 1-15 en `figs/` |
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
```

## Advertencia sobre los parámetros

Los parámetros marcados **[S]** en `params.py` (costos unitarios, concentraciones y disponibilidades del hub,
coeficientes del rendimiento de mezcla, precios del etanol y del vinagre, salario) son supuestos ilustrativos.
Las conclusiones **estructurales** (qué arquitectura gana y por qué) son robustas en los barridos reportados.
Las cifras **absolutas** en USD no deben citarse como resultado de la tesis hasta sustituir esos valores por
datos del proyecto.
