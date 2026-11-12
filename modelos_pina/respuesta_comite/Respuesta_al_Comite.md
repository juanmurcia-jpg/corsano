# Respuesta al Comité Evaluador

**Tesis:** *Designing for the Absent Grid: Simultaneous Synthesis, Sizing and Seasonal Operation of an Off-Grid Pineapple Whole-Plant Biorefinery in Bajo Atrato, Colombia* (borrador v2).
**Informe respondido:** «Informe de evaluación doctoral», Comité de Ingeniería Química y PSE, veredicto *Aprobado con cambios mayores*.
**Alcance de esta respuesta:** las cinco críticas adversariales (§3.1–3.5 del informe) y el bloque P0 (§5.1 del informe).
**Base de cálculo:** todos los números nuevos salen de re-ejecutar los modelos de la tesis. Se usaron `respuesta_comite.py`, `dimensionamiento.py`, `tea_dimensionado.py` y `acv.py`, en la rama `modelos-corsano-pina`, con los resultados en `modelos_pina/results/respuesta/`. Donde un número es una estimación y no una corrida, se dice.

---

## 0. Nota para la gestión (en español)

**Qué se hizo.** Se recalcularon, con los modelos de la tesis:
- el mapa H4 en VPN;
- la prueba estequiométrica de todo el registro y el efecto de limitar el etanol del jugo de hoja;
- cinco regímenes fiscales del vino;
- la sensibilidad del ACV al factor de descomposición, junto con el desglose de la neutralidad del diseño w = 0,75;
- los intervalos entre solución y cota dual de H2, H3 y H4;
- el wait-and-see del programa estocástico.

Hubo 24 re-optimizaciones del MILP con su TEA, todas registradas en `results/respuesta/`.

**Tres desviaciones deliberadas del encargo**, porque los datos verificados las contradicen. Un director no firmaría la versión literal del encargo en estos tres puntos.

1. **El dato `etanol_jugo_hojas` = 21,8 kg/t no se rebaja como valor central. Se corrige su base y su rango.**
   - La violación estequiométrica que detectó el comité es real, pero está en el par del registro. Los 21,8 kg de etanol se compararon con los 27 g/L de azúcares *libres*.
   - La fuente (Chen et al. 2020, vía el balance de Liao et al. 2022) da 1,0 kg de etanol por 46 kg de jugo, es decir 21,7 kg/t, en un caldo con 3,6 % v/v.
   - El jugo contiene 44,9 g/kg de carbohidrato por diferencia: sólidos 6,2 % menos proteína, cenizas y grasa. Sobre esa base, el rendimiento es 0,485 g/g, el 95 % del teórico. Pasa el límite estequiométrico, pero cerca del techo.
   - El límite superior del registro (24,5 kg/t) sí viola la estequiometría en cualquier base. Se corrige el rango a 11,1–21,8 kg/t.
   - Se re-ejecutó el óptimo en los cuatro valores. El diseño no cambia. El margen cae a 3 164, 2 965 y 2 897 MM COP/año, y la panela sube +9, +66 y +85 t/año. El caso extremo coincide con los +83 t que estima el comité.
   - La sección 5.1.2 reescrita presenta ese rango como el golpe acotado.
2. **Los 12 640 MM COP no se rotulan como «~5 021».**
   - En el código, 12 640 MM COP es el capital fijo que estima el MILP: 4 026 MM COP de compra de equipos de catálogo × 3,14 (Lang equivalente).
   - La carga anual de capital es 3 314 MM COP/año: 3 068 de AF × compra, más 246 de fijos.
   - La compra que lista el TEA es 5 225 MM COP, porque incluye los tanques de vinagre y de guarda que no están en el catálogo del MILP.
   - El «~5 021» del comité es una reconstrucción indirecta que se acerca a esos 5 225, pero no es el número del modelo. Se usan los valores exactos.
3. **H4 usa el VPN del TEA de cada diseño, no solo la secante.**
   - Los VPN de 25 de los 30 puntos ya se habían calculado con el TEA completo. La secante del informe (184 ↔ −5 409; 3 196 ↔ +5 397; pendiente 3,588; margen de equilibrio 1 692 MM COP/año) se usa en dos cosas:
     - para los 5 puntos sin fruta, a 100 000 botellas, que son plantas solo de vinagre a las que el TEA por líneas no se aplica;
     - como verificación cruzada.
   - Las dos fronteras coinciden.
   - El titular corregido es el que pide el encargo, con más precisión:
     - sin vinagre, desde unas 890 000 botellas;
     - con 3 000 m³ de vinagre, desde 250 000 botellas (VPN del TEA +2 115) o aun sin vino (estimación por secante, ≈ +750).

**Hallazgos nuevos que el comité no pidió y que cambian el texto:**
- **Riesgo fiscal.** Con cualquier régimen que triplique el impuesto, el modelo abandona el vino y queda una planta solo de vinagre de 1 902 MM COP/año. Esa planta queda certificada como óptima: la cota dual coincide con la solución. Su VPN estimado por secante es ≈ +750 MM COP. El diseño central, en cambio, cae a un VPN de −869. El riesgo fiscal no tumba el proyecto, pero sí la línea de vino.
- **Neutralidad.** El diseño w = 0,75 es neutro solo con el factor central. Con 90 kg/t emite +352 t, y sin el crédito de la fruta adicional, +216 t. El óptimo económico suma GWP con cualquier factor (+116 a +552 t), así que el signo de ese titular es robusto.
- **Frente H3.** Una corrida libre más larga mejoró un punto: en ε = −645 t pasa de 1 077 a 1 849 MM COP/año. El frente publicado no era un frente en ese tramo. Se reporta corregido, con sus cotas.
- **Estocástico.** Re-resueltos los tres escenarios, WS = 3 195,6 ≥ RP = 3 195,5. El EVPI es +0,08 MM COP. La prueba ya se cumple.

**Verificación externa del bloque fiscal.** Se confirmaron por fuentes públicas:
- el Auto 082 del 29-ene-2026 (exp. RE-387), que suspendió el Decreto Legislativo 1474/2025;
- la Sentencia C-079 de 2026, que lo declaró inexequible y ordenó devolver lo recaudado;
- el Oficio DIAN 4031 de 2026, que confirma el IVA del 5 %;
- un proyecto de «ley de rescate» presentado en 2026, que llevaría el IVA del vino al 19 %.

**No se pudo confirmar** el valor de 750 COP/grado ni los ad valorem de 30 % y 35 %: el texto del decreto y del proyecto no fueron accesibles desde esta sesión. Se usan como escenario «según el informe del comité», con la marca [verify] en las referencias.

**Paginación.** El borrador es un documento vivo sin paginación fija. La matriz cita secciones y tablas.

---

## 1. Matriz de respuesta (Response to Reviewers)

| # | Crítica del comité (informe) | Acción tomada | Nuevo dato o ecuación | Dónde se corrige |
|---|---|---|---|---|
| 1 | §3.1 / P0-1: H4 se calculó en margen y se anunció en VPN; el diseño (500 000; 0) tiene VPN −5 409 | Mapa H4 rehecho en VPN. Se usa el TEA de cada diseño re-optimizado (25 puntos) y la secante del informe para las 5 plantas sin fruta. Frontera VPN = 0 por interpolación. Se clasifica cada punto con su cota dual. | VPN(m) ≈ −5 409 + 3,588 (m − 184); m* = 1 692 MM COP/año. Frontera: ≈ 890 000 botellas sin vinagre; ≈ 2 100 m³ a 500 000; ≈ 2 700 m³ a 250 000; ≈ 2 900 m³ solo vinagre (estimación). | Resumen; §5.9.2 (texto y Tabla 5.9.2a–b); §5.10 (H4); §6.5 (Obj. 4, 5, 6) |
| 2 | §3.2 / P0-2: par etanol–azúcar del jugo de hoja con 0,81 g/g, mayor que 0,511 | Prueba estequiométrica de todo el registro. Corrección de la base (carbohidrato por diferencia, 44,9 g/kg) y del rango del etanol (11,1–21,8 kg/t; el límite anterior de 24,5 era imposible). Re-optimización en 4 valores. | Y = 0,485 g/g (95 % del teórico) en la base corregida. Golpe: margen 3 196 → 3 164 / 2 965 / 2 897; panela 145,6 → 154,6 / 211,6 / 230,8 t; VPN 5 397 → 5 273 / 4 491 / 4 225; mismo diseño. | §2.2.5 y registro (Ap. B); §3.11 (nueva prueba); §5.1.2; §6.6 |
| 3 | §3.3 / P0-3: régimen fiscal 2025–2026 no escenificado | Nueva §4.1.6 con la cronología verificada y el escenario del comité. Cinco regímenes evaluados por botella y con el MILP + TEA (reoptimizado y diseño central fijo). | Neto por botella a 16 000 COP: 4 667 (vigente); 1 306 (específico ×3); 583 (D. 1474, IVA 5 %); −332 (D. 1474, IVA 19 %); −537 (proyecto de rescate). Desde ×3 el óptimo es una planta solo de vinagre de 1 902 MM COP/año (certificada); el diseño central fijo tiene VPN −869. | §4.1.6 (nueva); §5.6.1; §6.4.2; §6.5 |
| 4 | §3.4 / P1-9: línea base sensible a un factor; neutralidad con crédito de fruta | Sensibilidad 190 ± 100 kg CO₂e/t para el óptimo (inventario ACV) y para w = 0,75 (GWP lineal del MILP). Desglose término a término de la mejora de 328 t. Línea base de quema con la misma jerarquía en el resumen. | Óptimo: +552 / +334 / +116 t (descomposición) y +847 / +1 004 / +1 160 t (quema). w = 0,75: +352 / −5 / −362 t. De la mejora de 328 t: −243 t de proceso y −85 t de línea base neta (+221 t de crédito por 1 162 t de fruta; −135 t perdidas por 714 t menos de hojas). Sin el crédito de la fruta: +216 t. | §5.6.4; §5.9.4; §5.10 (H3); §6.5 (Obj. 4) |
| 5 | §3.5 / P1-7: brechas no propagadas; WS < RP | Intervalos [incumbente, cota dual] para H2, H3 y H4. WS re-resuelto por escenario. Nuevo punto del frente H3. Veredictos reclasificados con los intervalos. | WS = 3 195,6 ≥ RP = 3 195,5; EVPI = +0,08; VSS = 0. H2: un recorte del 60 % cuesta 2 454 (incumbente) y al menos 1 049 (certificado). H3 (ε = −645 t): 1 077 → 1 849. H4: (500 000; 1 500 m³) no certificado (cota 2 593 > 1 692). | §3.10.2; §3.11; §5.6.3; §5.9.3; §5.9.4; §5.10 |
| 6 | P0-4: inconsistencias de edición | Unificadas con su causa explicada. | 3 196 / 5 397 en todo el texto (el punto E9 de 3 194 / 5 389 es el mismo diseño, cortado dentro de la tolerancia de 0,2 %). Capital: 4 026 compra MILP; 12 640 capital fijo MILP; 3 314 carga anual; 5 225 compra TEA; 16 405 capital fijo TEA. Caso de 1 500 m³: 926 MM COP/año (no 817), con cota 2 593. «a 60 % cut costs 2,454». +334 (inventario ACV, 1 288 t) frente a +323 (GWP lineal del MILP, 1 277 t): diferencia de 11 t por efluentes. 27 libros en ambos sitios. 375 m³ producidos = 500 000 botellas; el TEA vende el 95 % (475 000). | §3.10.2; §3.11; §4.1.5; §5.1.1; §5.4.2; §5.6.1; §5.6.4; §5.9.4; §5.10 |
| 7 | P0-5: referencias [verify]/[complete] | Se añaden las fuentes fiscales verificadas. Las marcas existentes se listan para resolverlas a fuente primaria antes de la defensa; no se inventan datos bibliográficos. | Auto 082/2026; C-079/2026; DIAN 4031/2026; Liao et al. 2022 (fuente del balance del jugo de hoja). | Referencias |

---

## 2. Texto reescrito (en inglés, listo para la tesis)

### 2.1 Abstract (third paragraph replaced; first two unchanged)

> With bottled wine taxed under Law 1816 of 2016 and market caps of 500,000 bottles and 3,000 m³ of vinegar per year, the optimal plant processes 1,276 t/year of fruit (20.8 % of the supply) and 3,746 t/year of leaves. It sells wine, vinegar fermented from peel and leaf juices with panela, and fibre flour, for an annual margin of 3,196 MM COP and a net present value of 5,397 MM COP (MIRR 13.5 %, P(NPV > 0) = 0.79). Designing the same superstructure fraction by fraction gives an NPV of only 79 MM COP. Viability depends on markets, and it is judged here by NPV, not by margin. The plant needs about 890,000 bottles a year without vinegar, or about 2,100 m³ of vinegar with 500,000 bottles and about 2,700 m³ with 250,000 bottles. A plant that makes 3,000 m³ of vinegar and no wine is estimated to be marginally viable. If the wine excise were tripled, as the emergency decree of December 2025 would have done before the Constitutional Court struck it down, wine would stop paying and the optimum would become such a vinegar-only plant. Limiting leaf-juice ethanol to stoichiometric bounds leaves the design unchanged and lowers the margin by at most 9.4 %. Against a site where fruit and leaves decompose, the optimum emits 116–552 t CO₂e/year more over the plausible range of the decomposition factor, and 847–1,160 t more if the leaves would otherwise be burned. A compromise design with a crown boiler is net-neutral only at the central factor and with credit for the extra fruit it buys. The value of integration lies inside the plant scale, and the outer scales leave the design unchanged. The sugar hub, gasification, bromelain and ethanol are not selected. For Bajo Atrato, validating the vinegar market and securing the fiscal treatment of fruit wine, not developing technology, are the conditions of the project.

*(The Spanish Resumen receives the same changes; see §2.10.)*

### 2.2 Section 5.1.1 — corrected capital sentence

> There is no crown boiler, no bromelain module, no leaf ethanol, no digester and no hub product; crown and core are composted. The catalogue options chosen cost 4,026 MM COP to purchase. With the equivalent Lang factor of 3.14, the MILP estimates their fixed capital at 12,640 MM COP. The annualized capital charge it subtracts is 3,314 MM COP/year: 3,068 for the annuity, maintenance and local taxes on purchased equipment (AF = 0.762), plus 246 of fixed costs tied to the chosen options. The itemized TEA lists 5,225 MM COP of purchased equipment, which adds the vinegar and ageing tanks that the MILP catalogue does not size. It arrives at a fixed-capital investment of 16,405 MM COP: 10,936 direct, 3,281 engineering, procurement and construction, and 2,187 contingency (Section 5.6).

### 2.3 Section 5.1.2 — paragraph «Vinegar carries the plant» replaced

> **Vinegar carries the plant.** Without the vinegar routes the optimum earns 184 MM COP/year; with them, 3,196. Its substrate is mostly leaf juice with panela: 2,847 t of leaf juice against 221 t of peel juice, and no wine diverted.
>
> The acid potential of leaf juice rests on one source. Chen et al. (2020) report 1.0 kg of ethanol from 46 kg of juice (21.7 kg/t; broth at 3.6 % v/v; mass balance in Liao et al., 2022). The free sugars of that juice (27 g/L at most) cannot produce that much ethanol. The juice does contain 44.9 g/kg of carbohydrate by difference (6.2 % solids, less protein, ash and fat), which puts the conversion at 0.485 g/g, 95 % of the stoichiometric maximum. The yield is possible but at the edge, so the optimum was re-solved at three lower values (Table 5.1.2a).
>
> The design does not change in any case: the same 23 decisions and the same 3,000 m³ of vinegar. Panela makes up the acid the leaf juice no longer supplies, from 146 to 155–231 t/year. The margin falls from 3,196 to between 2,897 and 3,164 MM COP/year and the NPV from 5,397 to between 4,225 and 5,273 MM COP. The leaf-juice yield therefore changes the cost of vinegar, not whether vinegar is made. A fermentation of the Chocó leaf juice with its own strain is the measurement that would close this range (Section 6.7).

*Table 5.1.2a. Optimum with the leaf-juice ethanol yield limited by stoichiometry.*

| Leaf-juice ethanol (kg/t) | Basis | Acid potential (kg/t juice) | Margin (MM COP/year) | Panela (t/year) | NPV (MM COP) | Design |
|---|---|---|---|---|---|---|
| 21.8 | source mass balance (0.485 g/g on 44.9 g/kg carbohydrate) | 26.7 | 3,196 | 145.6 | 5,397 | optimum |
| 20.7 | 90 % of theoretical on carbohydrate | 25.3 | 3,164 | 154.6 | 5,273 | same |
| 13.5 | theoretical (0.511 g/g) on free sugars only | 16.6 | 2,965 | 211.6 | 4,491 | same |
| 11.1 | 0.42 g/g on free sugars only (panela convention) | 13.6 | 2,897 | 230.8 | 4,225 | same |

### 2.4 Section 5.6.1 — Techno-economic assessment (rewritten)

> The TEA confirms the ranking of the MILP (Table 5.6.1). From the TRL-9 reference to the optimum the NPV rises from −12,454 to 5,397 MM COP and the MIRR from −22.8 % to 13.5 %, with 4,040 MM COP more capital; P(NPV > 0) rises from 0 to 79 %. Without vinegar the optimum loses money (NPV −5,409 MM COP, P(NPV > 0) = 0.02): the vinegar routes add 10,806 MM COP of NPV at 2,200 COP/L.
>
> The annual margin of the MILP is not a measure of viability. It is computed after the annualized capital charge but before payroll, supervision, the remaining fixed costs, income tax and the phased start-up that the TEA includes. On the designs computed, NPV and margin are related by NPV ≈ −5,409 + 3.588 (m − 184) MM COP. The relation passes through the designs without vinegar (m = 184) and the optimum (m = 3,196), and reproduces the full TEA of the other 23 designs of the demand map with a mean deviation of 777 MM COP and a maximum of 1,840 MM COP, under 3 % of the range of NPV they span. It places the break-even margin at about 1,692 MM COP/year. Every viability statement in this thesis uses the NPV of the TEA, or this relation where the TEA does not apply (Section 5.9.2).
>
> **Cost structure of the optimum.**
> - Revenue is 12,089 MM COP/year: 5,362 from wine at the factory price and 6,727 from vinegar and flour.
> - Variable costs are 5,066 MM COP/year. Raw materials account for 4,465 of them: the excise on the 475,000 bottles sold (95 % of the 500,000 produced, the sales convention of Table 4.1) is about 2,000, packaging about 1,140, fruit 511, panela 510 and leaf collection 133; composting and chemicals make up the rest. Utilities cost 580 and waste treatment 21.
> - Fixed costs are 2,227 MM COP/year: payroll 572, supervision 343, maintenance 820, and local taxes and insurance 492.
> - Working capital is 608 MM COP. Operating cost totals 7,293 MM COP/year, and the discounted payback is 6.5 years.
>
> The excise is the largest single cost of the plant, and its rate is not stable (Section 4.1.6).
>
> **Fiscal sensitivity.** Table 5.6.1b evaluates five excise regimes, each by the net revenue per bottle and by re-solving the MILP and the TEA:
> - Under the current regime a bottle sold at 16,000 COP leaves 4,667 COP after excise, VAT, distribution and packaging.
> - Tripling the specific component leaves 1,306 COP. The rates of Decree 1474 of 2025 leave 583 COP with 5 % VAT and −332 COP with 19 % VAT. The 2026 fiscal-rescue bill leaves −537 COP.
>
> From the tripled specific component upwards, the re-optimized plant stops making wine. It becomes a vinegar plant fed by leaf juice and panela, earning 1,902 MM COP/year with a zero optimality gap; its NPV, estimated by the relation above, is about +750 MM COP. The design optimized for the current regime does worse if it is kept:
> - with the specific component tripled it earns 1,599 MM COP/year and its NPV is −869 MM COP;
> - under the rates of Decree 1474 it stops buying fruit, and its margin falls to 1,442 MM COP/year.
>
> The wine line is therefore the part of the project exposed to fiscal risk. The vinegar line carries the project under every regime tested.
>
> **Company size and income tax.** By its revenue in UVT the optimum is a medium-sized company, so with start-up in 2030 it pays the general rate of 35 % in every year. Under the proposed ZOMAC extension (Bill 435 of 2025) its NPV would rise to 7,029 MM COP (+1,632); the no-cap designs would gain 6,457 (wine) and 10,448 (vinegar). The ZOMAC location does not exempt the wine from the departmental excise.

### 2.5 Section 5.6.3 — Stochastic design (rewritten)

> With supply at 0.7, 1.0 and 1.3 times the central value, RP = 3,195.5, EV = 3,194 and EEV = 3,195.5 MM COP/year. The version 12 run reported WS = 3,195 MM COP/year, below RP, which violates EEV ≤ RP ≤ WS. By the protocol of Section 3.11 that is an error, not a result: the wait-and-see problem of the central scenario had stopped at its time limit (3,193.7) below a design already known. Re-solving each scenario with that design as a starting point gives:
>
> | Supply scenario | Probability | WS solution | Dual bound | Design |
> |---|---|---|---|---|
> | 0.7 | 0.25 | 3,195.6 | 3,195.6 | optimum |
> | 1.0 | 0.50 | 3,195.6 | 3,356.0 | optimum |
> | 1.3 | 0.25 | 3,195.6 | 3,210.1 | optimum |
>
> WS = 3,195.6 ≥ RP = 3,195.5, EVPI = 0.08 MM COP/year and VSS = 0. The stochastic design is the deterministic one. This result is expected: with both markets capped, supply is not an active constraint, and even the low scenario offers more fruit than the wine market absorbs. The two-stage program therefore answers only the supply question, and the answer is that supply does not matter at this scale. Market uncertainty, which does matter, is treated with the demand map of Section 5.9.2, the price tornado and the Monte Carlo of Section 5.6.2, and the fiscal regimes of Table 5.6.1b. A two-stage program with demand as the uncertain parameter is listed as future work (Section 6.7).

### 2.6 Section 5.6.4 — Life-cycle assessment (rewritten)

*(The contribution table of the current §5.6.4 is kept unchanged; the text after it is replaced.)*

> Process GWP is 1,288 t CO₂e/year, or 1,009 kg per tonne of fruit processed. The largest item is the leaf pulp the extractor returns to the field: 674 t/year that carry about two thirds of the leaves' dry matter and still decompose there. Earlier versions credited the plant for all the leaves it collects but did not count this return. The correction (Section 4.2) raises process GWP from 809 to 1,288 t and changes the sign of the net result. Diesel electricity and glass bottles follow. Effluent treatment removes 97 % of 7.9 t of COD for 11 t CO₂e. Fossil energy is 4.7 TJ/year and water 2,936 m³/year.
>
> **The net result and its two assumptions.** The net GWP subtracts what the site would emit without a plant, and it rests on two assumptions:
> - **The decomposition factor.** One IPCC factor, 4 g CH₄ and 0.3 g N₂O per kg of wet material (190 kg CO₂e/t), values the fruit and leaves in the baseline, the fractions composted in the plant and the leaf pulp returned to the field.
> - **What would happen to the leaves without a plant.** They would either decompose or be burned.
>
> Table 5.6.4b varies both. Over 90 to 290 kg CO₂e/t, the optimum adds between 116 and 552 t CO₂e/year against a decomposing baseline, and between 847 and 1,160 t against a burning baseline. Raising the factor raises the baseline faster than the process emissions, because the baseline holds 954 t of decomposing material against 539 t in the process, so the net falls but stays positive. The sign of the result is therefore robust: under every combination tested, the economic optimum emits more than the site without a plant. Burning leaves emits little GWP but much particulate matter, and the plant avoids 4.8 t/year of particulates in that case.
>
> The net figure uses the inventory of this section (1,288 t, +334 t). The MILP carries a linear GWP of 1,277 t (+323 t) that omits effluent treatment (11 t). Both are reported, each labelled with its basis.
>
> The baseline also assumes that the fruit the plant buys would otherwise be discarded. This thesis takes the 2022 production of Chocó as the supply available to the plant. The only measured reject stream is 144 t/year in one municipality (Murcia Palacios, 2013), and Section 2.1.3 gives a scenario of 1,536 t at 25 % shrinkage. At 1,276 t/year the optimum stays within that scenario. Any fruit diverted from the fresh market would carry no baseline credit; the effect of that on the compromise design is quantified in Section 5.9.4.
>
> System-expansion credits are zero for the optimum, which makes neither ethanol nor surplus power. By economic allocation, a bottle of wine carries 1.14 kg CO₂e (44 % of the burden), a litre of vinegar 0.22 kg (52 %) and a kilogram of flour 1.21 kg (4 %).

*Table 5.6.4b. Net GWP of the economic optimum against the decomposition factor and the leaf counterfactual (t CO₂e/year; life-cycle inventory).*

| Decomposition factor (kg CO₂e/t wet) | 90 | 190 (central) | 290 |
|---|---|---|---|
| Process GWP | 1,004 | 1,288 | 1,572 |
| Baseline: fruit and leaves decompose | 452 | 954 | 1,456 |
| **Net GWP, decomposing baseline** | **+552** | **+334** | **+116** |
| Baseline: fruit decomposes, leaves burned | 156 | 284 | 412 |
| **Net GWP, burning baseline** | **+847** | **+1,004** | **+1,160** |

### 2.7 Section 5.9.2 — Minimum viable demand (H4), rewritten

> Section 3.12.4 defines the H4 frontier as the line NPV = 0. The margin of the re-optimized design was computed over 30 combinations of market size, together with the dual bound of each free run. The TEA was then run on every design that processes fruit (Table 5.9.2a).
>
> The five designs at 100,000 bottles process no fruit and make no wine: they are vinegar plants fed by leaves and panela, to which the itemized TEA does not apply. Their NPV is estimated with the margin–NPV relation of Section 5.6.1 (NPV ≈ −5,409 + 3.588 (m − 184)). Across the 25 designs with a full TEA, the relation deviates from it by 777 MM COP on average and by 1,840 MM COP at most, under 3 % of the NPV range of the map; it places the break-even margin at 1,692 MM COP/year.
>
> **The frontier.** Interpolating the NPV between grid points:
> - Without vinegar, the plant is viable from about 890,000 bottles a year (NPV −5,409 at 500,000 bottles; +1,500 at 1,000,000).
> - With 500,000 bottles it needs about 2,100 m³ of vinegar (2,070 by interpolation), with 250,000 bottles about 2,700 m³ (2,670), and as a vinegar-only plant about 2,900 m³ (2,870, estimate).
> - At 2,000,000 bottles every vinegar level is viable.
>
> The earlier reading of this map, «viable from about 500,000 bottles», took a positive margin for viability. It is withdrawn: that design has an NPV of −5,409 MM COP.
>
> **Certification of the frontier.** The margins are the best solutions found. Their dual bounds (Table 5.9.2b) separate three regions:
> - **Certified not viable.** The designs without vinegar at 100,000, 250,000 and 500,000 bottles have dual bounds of −1,090, −682 and 280 MM COP/year. These are below the break-even margin, so no better design exists there.
> - **Viable by the TEA of the solution found.** All points with positive NPV in Table 5.9.2a.
> - **Not certified.** At 500,000 bottles and 1,500 m³ the solution has an NPV of −3,312 MM COP, but the dual bound (2,593 MM COP/year) is above the break-even margin. A better design there cannot be ruled out, and the frontier at 500,000 bottles lies somewhere between 1,500 and about 2,100 m³ of vinegar.
>
> H4 survives in substance and its frontier moves. Viability depends on the demand for both products far more than on technology or supply. The central caps, however, are not twice the viable minimum, as stated before: the vinegar cap of 3,000 m³ sits about 45 % above the vinegar needed at 500,000 bottles (about 2,100 m³), and the plant is not viable on the wine market alone below about 890,000 bottles. The market studies of Section 6.4 must locate vinegar demand first.

*Table 5.9.2a. Net present value of the re-optimized design for each pair of market sizes (MM COP). Values marked * are estimates for vinegar-only plants (no fruit processed), from the margin–NPV relation of Section 5.6.1.*

| Vinegar (m³/year) \ bottles/year | 100,000* | 250,000 | 500,000 | 1,000,000 | 2,000,000 |
|---|---|---|---|---|---|
| 0 | −9,981* | −10,240 | −5,409 | 1,500 | 3,899 |
| 750 | −9,981* | −10,240 | −5,409 | 1,500 | 8,577 |
| 1,500 | −7,778* | −7,491 | −3,312 | 3,272 | 13,350 |
| 3,000 | 753* | 2,115 | 5,397 | 11,554 | 22,410 |
| 6,000 | 14,648* | 16,511 | 19,823 | 26,070 | 31,632 |
| 12,000 | 40,864* | 43,850 | 47,128 | 53,275 | 56,474 |

*Table 5.9.2b. Margin of the design found and dual bound of the free run (MM COP/year), for the points that decide the frontier. Break-even margin: 1,692.*

| Point (bottles; vinegar m³) | Margin found | Dual bound | NPV (TEA) | Status |
|---|---|---|---|---|
| 100,000; 0 | −1,090 | −1,090 | −9,981* | certified not viable |
| 250,000; 0 | −683 | −682 | −10,240 | certified not viable |
| 500,000; 0 | 184 | 280 | −5,409 | certified not viable |
| 1,000,000; 0 | 1,911 | 2,255 | 1,500 | viable |
| 500,000; 1,500 | 926 | 2,593 | −3,312 | not certified |
| 250,000; 3,000 | 2,317 | 3,001 | 2,115 | viable |
| 100,000; 3,000 | 1,902 | 3,105 | 753* | viable (estimate) |
| 500,000; 3,000 (central) | 3,196 | 3,726 | 5,397 | viable |

### 2.8 Section 5.9.3 — H2: table with intervals (replaces the table; the text keeps its reading)

> Lowering the cap on fossil energy (3,818 GJ/year in the optimum) gives the solutions below with the dual bounds of their free runs. Costs are measured from the unconstrained optimum, whose solution is 3,196 MM COP/year and whose dual bound is 3,789. The certified minimum cost is the solution of the optimum minus the dual bound of the capped case. The bounds are weak, so the certified costs are lower limits, and the costs at the solutions found are what this thesis reports.

| Fossil cap (% of optimum) | Margin found | Dual bound | Cost at the solutions found | Certified minimum cost |
|---|---|---|---|---|
| 100 | 3,196 | 3,789 | — | — |
| 80 (a 20 % cut) | 3,039 | 4,957 | 157 | not certified |
| 60 (a 40 % cut) | 1,673 | 2,488 | 1,523 | 708 |
| 40 (a 60 % cut) | 742 | 2,147 | 2,454 | 1,049 |
| 20 (an 80 % cut) | 30 | 2,660 | 3,166 | 536 |
| 0 (full autonomy) | −1,642 | no finite bound | 4,838 | not certified |

*Note: the certified minimum cost of the 80 % cut (536) is below that of the 60 % cut (1,049). Each certified cost comes from the dual bound of a different free run, and those bounds are weak, so the certified costs need not be monotone; the true cost of cutting more fossil energy cannot be lower.*

> The first 20 % is cheap, 157 MM COP/year, and is where the heat pump enters. A 60 % cut costs 2,454 MM COP/year at the solutions found and at least 1,049 with certainty, and it cuts vinegar, because aeration of the acetifier is the largest electricity use and only diesel supplies it. Full autonomy means not operating. H2 is supported in the form tested here, the ε-constraint sweep. The flexibility index named in the original wording of H2 is formulated (Section 3.6.3) but not run, and the verdict does not rest on it.

### 2.9 Section 5.9.4 — H3: certified front and the anatomy of neutrality

*(The front table is replaced with Table 5.9.4a; the paragraph on the compromise is replaced. Values are the linear GWP of the MILP.)*

**[TABLA 5.9.4a — se completa con las corridas h3 / h3full; ver §3.4 de esta respuesta]**

> **What makes the compromise neutral.** The compromise at w = 0.75 moves the net GWP from +323 to −5 t CO₂e/year, an improvement of 328 t, for 90 MM COP/year of margin. Table 5.9.4b decomposes that change term by term.
>
> **Process emissions fall by 243 t:**
> - The crown boiler replaces all LPG heat: −57 t, against +15 t of combustion emissions.
> - The design collects 714 t fewer leaves and burns 200 t of leaf pulp instead of returning it to the field: −233 t.
> - It uses 51 t less panela, because it diverts 341 m³ of wine to vinegar: −30 t.
> - Composting the cores and crowns of the extra fruit adds +55 t.
>
> **The baseline grows by 85 t net:**
> - The design buys 1,162 t more fruit, which earns 221 t of credit for fruit that would otherwise decompose.
> - It collects 714 t fewer leaves, which loses 135 t of credit.
>
> Two consequences follow:
> - Without the credit for the extra fruit, if that fruit came from the fresh market rather than from reject, the compromise design would emit +216 t: it would not be neutral.
> - The compromise is neutral only near the central decomposition factor. Its net GWP is +352 t at 90 kg CO₂e/t and −362 t at 290 (Table 5.9.4c).
>
> The extra fruit is also beyond what the supply data support: at 2,439 t/year the compromise buys more than the 1,536 t of the 25 %-shrinkage scenario of Section 2.1.3, so part of its fruit would have to come from the fresh market, where it carries no baseline credit. Neutrality is therefore conditional on both the supply premise and the factor. The economic optimum, by contrast, emits more than the no-plant site under every combination tested. The compromise remains the design this thesis recommends if the environmental objective is weighted at all, because most of its improvement (243 of 328 t) is a real cut in process emissions. Its claim of neutrality, however, must carry these two conditions.

*Table 5.9.4b. Change in GWP from the economic optimum to the compromise w = 0.75 (t CO₂e/year; linear GWP of the MILP).*

| Term | Economic optimum | Compromise w = 0.75 | Change |
|---|---|---|---|
| LPG heat | 57.2 | 0.0 | −57.2 |
| Crown boiler (CH₄, N₂O) | 0.0 | 15.0 | +15.0 |
| Leaf pulp and juice returned to the field | 478.8 | 245.4 | −233.4 |
| Leaf collection (diesel) | 66.8 | 54.1 | −12.7 |
| Panela | 87.4 | 57.0 | −30.3 |
| Composting of cores and crowns | 60.6 | 115.8 | +55.2 |
| Fruit transport | 5.2 | 9.9 | +4.7 |
| Diesel electricity (including aeration) | 207.5 | 217.8 | +10.3 |
| Glass bottles | 250.0 | 250.0 | 0.0 |
| Chemicals and other | 63.4 | 69.0 | +5.6 |
| **Process GWP** | **1,276.8** | **1,034.0** | **−242.8** |
| Baseline: fruit (1,276 → 2,439 t) | 242.4 | 463.1 | +220.7 |
| Baseline: leaves (3,746 → 3,033 t) | 711.4 | 575.9 | −135.5 |
| **Baseline** | **953.8** | **1,039.0** | **+85.2** |
| **Net GWP (process − baseline)** | **+323.0** | **−5.0** | **−328.0** |

*Table 5.9.4c. Net GWP of the two designs against the decomposition factor (t CO₂e/year; linear GWP of the MILP; decomposing baseline).*

| Decomposition factor (kg CO₂e/t wet) | 90 | 190 | 290 |
|---|---|---|---|
| Economic optimum | +541 | +323 | +105 |
| Compromise w = 0.75 | +352 | −5 | −362 |

### 2.10 Section 5.10 — Testing hypotheses H1–H4 (table rewritten)

| Hypothesis | Verdict | Evidence |
|---|---|---|
| H1. Simultaneous synthesis, sizing and operation beat sequential design by fractions | Supported, with one qualification | The same superstructure designed by fractions in sequence earns 1,836 against 3,196 MM COP/year (NPV 79 against 5,397) (Section 5.9.1). The sequential protocol has no feedback between stages, so the gap measures sequential design without iteration. Seasonal coupling adds nothing at the capped scale and 4.4–12.2 % when capacity binds. At train level, the hierarchical chain costs 3.8–12.5 % more at the flow of the optimum (7.1–9.0 % at the original basis; Section 5.11). |
| H2. Energy autonomy has a measurable cost in margin and portfolio | Supported (ε-constraint sweep) | A 20 % cut in fossil energy costs 157 MM COP/year (heat pump). A 60 % cut costs 2,454 at the solutions found and at least 1,049 certified, and it cuts vinegar. Full autonomy means not operating (Section 5.9.3). The flexibility index of the original wording is formulated but not run, and the verdict does not rest on it. |
| H3. The margin–GWP front is non-dominated and non-degenerate, with GWP against a no-plant baseline | Partly supported | A non-degenerate front exists: margin falls monotonically as the net GWP cap tightens, from +323 t at the optimum. The front is the best one found, not a certified one: its dual bounds lie well above the solutions (Table 5.9.4a), and one published point was improved by 772 MM COP/year. The economic optimum emits more than the no-plant site for every decomposition factor from 90 to 290 kg/t (+105 to +541 t). The net-neutral compromise (w = 0.75, 90 MM COP/year) holds only at the central factor and with credit for 1,162 t of extra fruit (Section 5.9.4). |
| H4. With the current supply, viability depends more on the demand and price of the main products than on technology | Supported, with a corrected frontier | Over 30 market pairs the NPV ranges from −10,240 to +56,474 MM COP. The frontier NPV = 0 lies at about 890,000 bottles without vinegar, or about 2,100 m³ of vinegar with 500,000 bottles and about 2,700 m³ with 250,000 bottles; a vinegar-only plant needs about 2,900 m³ (estimate). The designs without vinegar below 500,000 bottles are certified not viable (Section 5.9.2). Tripling the wine excise turns the optimum into a vinegar-only plant (Section 5.6.1). Supply from 0.5 to 3.6 times the central value leaves the capped optimum unchanged (VSS = 0; EVPI = 0.08 MM COP/year). |

> H1 needs two qualifications. First, at the scale of Chocó its gain comes from synthesis across fractions, not from coupling design with seasonal operation, which matters only when capacity binds. Second, it says nothing about sharing equipment between products: the multiplant–multiproduct comparison (Section 2.8.6) shows that question is close economically and decided by staffing, which in Bajo Atrato has social weight of its own. H4 is the hypothesis the thesis did not start with and the one its results support most strongly. Judged by NPV, its frontier is more demanding than first reported, and it places the vinegar market, not the wine market, at the centre of the project.

### 2.11 Section 6.5 — Conclusions against each objective (Objectives 2, 4, 5 and 6 rewritten; 1 and 3 receive one sentence each)

> **Objective 1** (one sentence added at the end). A stoichiometric test of every sugar-to-product pair of the registry found one inconsistent pair: the ethanol yield of leaf juice had been compared with its free sugars. On the carbohydrate it holds, the yield is 95 % of the theoretical maximum, and the registry range was corrected to 11.1–21.8 kg/t.
>
> **Objective 2: unit and train models.** The fermentation models were calibrated and verified. The single measured point of pulp juice does not identify its kinetics: a family of parameter pairs fits it equally well and changes the design fermentation time by a factor of 2.3. Moresi's winery model was replicated, with his numbers of fermenters reproduced exactly, and its kinetics were shown to be invalid at the 30 °C of the pineapple data; the premium-line advantage claimed earlier is an artefact of changing model. The glucose–xylose kinetics of the juices cut the processing time of the juice winery from 32.5 to 12.6 h. Fixing kinetics before sizing costs 7.1–9.0 % of the fermentation-train cost at the original design basis and 3.8–12.5 % at the wine flow of the optimum, and the band of fermentation times left by the single point does not change the plant design (Section 5.11).
>
> **Objective 3** (one sentence added at the end). The dual bounds of the free runs are now reported beside every hypothesis test. They certify the non-viable region of the demand map but not the margin–GWP front, whose dual bounds remain weak.
>
> **Objective 4: assessment under uncertainty.** The optimum has an NPV of 5,397 MM COP, an MIRR of 13.5 % and P(NPV > 0) = 0.79, with a break-even vinegar price 22 % below the assumed price. Two uncertainties outside the Monte Carlo were quantified:
> - **The leaf-juice yield.** Limited by stoichiometry, it lowers the NPV to 4,225–5,273 MM COP without changing the design.
> - **The wine excise.** At three times its current specific rate, or at the rates of the annulled Decree 1474 of 2025, wine stops paying. The optimum then becomes a vinegar-only plant of 1,902 MM COP/year (NPV about +750), while the current design kept unchanged would lose 869 MM COP of NPV.
>
> The plant emits 1,288 t CO₂e/year in process. Against a site where fruit and leaves decompose, it adds 116–552 t over the plausible range of the decomposition factor; if the leaves would otherwise be burned, it adds 847–1,160 t. A crown boiler makes it net-neutral for 90 MM COP/year, but only at the central factor and with credit for the extra fruit it buys. The plant retains 2,011 MM COP/year in the territory with about 17 jobs. Supply uncertainty has no value (VSS = 0, EVPI = 0.08 MM COP/year after the wait-and-see problems were re-solved); market and fiscal uncertainty dominate.
>
> **Objective 5: the Bajo Atrato biorefinery.** The optimal plant processes 1,276 t/year of fruit and 3,746 t/year of leaves into 500,000 bottles of wine, 3,000 m³ of vinegar and 40 t of fibre flour. Its equipment is:
> - a 1 t/h front end, one shared press, flotation and SO₂;
> - two 10 m³ fermenters and a 500 bottles/h line;
> - a juice winery and a 10 m³ acetifier;
> - a 2 t/h leaf extractor and a small dryer.
>
> It is viable if vinegar sells above 1,712 COP/L and wine near 16,000 COP per bottle. The hypotheses come out as follows:
> - H1 is supported against a sequential design of the same superstructure (NPV 79 against 5,397 MM COP).
> - H2 is supported by the autonomy sweep.
> - H3 is partly supported: the front is non-degenerate but not certified, and neutrality is conditional.
> - H4 is supported with a corrected frontier: the plant is viable from about 890,000 bottles without vinegar, or with about 2,100 m³ of vinegar at 500,000 bottles and about 2,700 m³ at 250,000.
>
> **Objective 6: rules and policy.** Markets and the excise on fruit wine, not feedstock or technology, now limit the project. The design rules for a larger wine market are known from the scale sweep: front end first, then presses, centrifugation and the crown boiler, and enzyme recovery and a third shift only from three times the supply. Because the vinegar line carries the project under every fiscal regime tested, the first market study should establish vinegar demand, and the second the volume and price of bottled fruit wine. The policy levers are demand, a stable and differentiated excise for small regional fruit-wine producers, and renewable electricity.

> **Resumen (Spanish abstract), third paragraph replaced:** «Con el vino embotellado y su impuesto al consumo (Ley 1816 de 2016), y con topes de mercado de 500 000 botellas y 3 000 m³ de vinagre al año, el óptimo procesa 1 276 t/año de fruta y 3 746 t/año de hojas, vende vino, vinagre de jugos de cáscara y de hojas con panela y harina de fibra, y da un margen de 3 196 MM COP/año y un VPN de 5 397 MM COP (TIRM 13,5 %; P(VPN > 0) = 0,79). Diseñar la misma superestructura fracción por fracción deja un VPN de solo 79 MM COP. La viabilidad depende del mercado y se juzga por el VPN: hacen falta unas 890 000 botellas sin vinagre, o unos 2 100 m³ de vinagre con 500 000 botellas y unos 2 700 m³ con 250 000. Si el impuesto al vino se triplicara, como lo habría hecho el decreto de emergencia de 2025 que la Corte declaró inexequible, el vino dejaría de pagar y el óptimo sería una planta solo de vinagre. Limitar el etanol del jugo de hoja por la estequiometría no cambia el diseño y baja el margen a lo sumo un 9,4 %. Frente a un sitio donde la fruta y las hojas se descomponen, el óptimo emite entre 116 y 552 t CO₂e/año más según el factor de descomposición, y entre 847 y 1 160 t más si las hojas se quemaran; un diseño de compromiso con caldera de corona es neutro solo con el factor central y con el crédito de la fruta adicional que compra. Ni el hub de azúcares ni la gasificación entran. Validar el mercado del vinagre y asegurar el tratamiento fiscal del vino de fruta, no desarrollar tecnología, son ahora las condiciones del proyecto.»

### 2.12 New Section 4.1.6 — Regulatory risk of the wine excise (Chapter 4)

> **4.1.6 Regulatory risk of the wine excise**
>
> The excise rates of Section 4.1.3 are those in force in 2026:
> - a specific component of 243 COP per alcoholic degree in 750 cm³ (Certification 003 of 2025, Ministry of Finance);
> - an ad valorem component of 20 % (Law 1816 of 2016, art. 20);
> - VAT of 5 % (Tax Code, art. 468-1; DIAN, Ruling 4031 of 2026).
>
> They are in force only because of a court decision. Legislative Decree 1474 of 29 December 2025, issued under a declared economic emergency, raised the taxes on liquors and wines. The Constitutional Court suspended it provisionally on 29 January 2026 (Order 082, file RE-387) and declared it unconstitutional in Ruling C-079 of 2026, ordering the indirect taxes collected under it to be refunded. A fiscal bill presented to Congress in 2026 would again move wines from 5 % to the general 19 % VAT and raise the consumption tax, mainly from 2027.
>
> According to the evaluation committee, the decree set a specific component of 750 COP per degree with a 30 % ad valorem component and 19 % VAT, and the 2026 bill proposes 750 COP per degree with 35 % ad valorem [these rates are taken from the committee's report and remain to be verified against the texts]. For a project that starts in 2030 and whose largest single cost is this excise, the rate is a project risk, not a constant.
>
> Five regimes are therefore evaluated:
> - the current one;
> - the specific component tripled;
> - the decree rates with 5 % VAT;
> - the decree rates with 19 % VAT;
> - the 2026 bill.
>
> Each regime is evaluated per bottle by the relation of Section 4.1.3 and for the whole plant by re-solving the MILP and the TEA (Table 5.6.1b).

### 2.13 Chapter 2, Section 2.2.5 — replacement paragraph on leaf juice, and registry rows (Appendix B)

> **Leaf juice.** Extraction yields 0.76 t of juice per tonne of leaves (Liao et al., 2026; 0.77 in Chen et al., 2020). The juice holds 6.2 % solids, of which 14 % is crude protein, 10.0 % ash and 3.5 % fat (Liao et al., 2022, Table 1, from Chen et al., 2020). By difference it therefore holds about 44.9 g of carbohydrate per kg. Of this, the free monosaccharides measured are 10.6 g/L of glucose and 16.4 g/L of xylose (Chen et al., 2020; Liao et al., 2022 give 0.6 g/L of C6 sugars for the same juice, a discrepancy to be checked in the original). Fermented by *Kluyveromyces marxianus* at 35 °C, 46 kg of juice gave 35 kg of broth at 3.6 % v/v ethanol, about 1.0 kg of ethanol, or 21.7 kg per tonne of juice. That yield is 0.485 g/g of carbohydrate (95 % of the stoichiometric maximum) and cannot come from the free sugars alone (0.82 g/g on them), so the yeast must also use part of the soluble oligosaccharides. The registry carries 21.8 kg/t as the central value and 11.1–21.8 kg/t as its range. The lower end assumes that only the free sugars ferment, at the 0.42 g/g used for panela.

*Registry rows (Appendix B), before → after:*

| Key | Before | After |
|---|---|---|
| `azucar_jugo_hojas` | 27.0 g/L (glucose 10.6 + xylose 16.4) | renamed `azucar_libre_jugo_hojas`, 27.0 g/L, [L], Chen et al. 2020 |
| `carbohidrato_jugo_hojas` (new) | — | 44.9 g/kg, [L/derived], by difference from Liao et al. 2022, Table 1 |
| `etanol_jugo_hojas` | 21.8 (18–24.5) kg/t, [L] | 21.8 (11.1–21.8) kg/t, PERT, [L]; basis: carbohydrate by difference; Y = 0.485 g/g (95 % of theoretical); upper bound 24.5 removed (0.545 g/g, above stoichiometry) |

### 2.14 Section 3.10.2 — table rows corrected

| Case | Free run | After polishing | After cross pass | Dual bound | Reported gap |
|---|---|---|---|---|---|
| Vinegar demand 1,500 m³ | 817 (version 13 free run) | — | 926 (version 13 cross-design pass) | 2,593 | 180 % |
| Stochastic RP | 2,511 | 2,709 | 3,196 | — | 47.7 % |

> Note for the text: the vinegar-demand case of 1,500 m³ is reported throughout as 926 MM COP/year, the best design found after the cross-design pass of version 13. The value of 817 was its version 12 incumbent. Both share the dual bound of 2,593, and the gap of 180 % is computed against 926. The row of the optimum is unchanged (16.9 %, against the bound of its own version 12 free run); the demand map of Section 5.9.2 reports the bound of the corresponding version 13 free run, 3,726.

### 2.15 Editorial corrections (exact replacements)

| Location | Before | After |
|---|---|---|
| §5.4.2, price grid, row PVP 16,000 / vinegar 2,200 | 3,194 · 5,389 | 3,196 · 5,397 (same design; that grid point had stopped 0.06 % below the optimum, within the 0.2 % fixed-design tolerance) |
| §5.4.3 / E8 sweep, vinegar demand 1,500 m³ | 817 | 926 |
| §5.10 (H2) | «60 % costs 2,454» | «a 60 % cut costs 2,454» |
| §5.9.4 and abstract | «+323» and «+334» without basis | «+334 t (life-cycle inventory, 1,288 t)» and «+323 t (linear GWP of the MILP, 1,277 t; the 11 t difference is effluent treatment)» |
| §3.11 and §4.1.5 | «16 workbooks» | «27 workbooks» (all current workbooks; Appendix D) |
| §5.6.1 | «the excise on 475,000 bottles sold» | «the excise on the 475,000 bottles sold (95 % of the 500,000 produced, the sales convention of Table 4.1)» |
| §5.1.1 | «The equivalent purchased-equipment cost entering the capital charge is 12,640 MM COP» | text of §2.2 of this response |

---

## 3. Nuevas tablas de datos

### 3.1 Tabla de sensibilidad fiscal del vino (Table 5.6.1b, for the thesis)

*Table 5.6.1b. Wine excise regimes: net revenue per 750 mL bottle and whole-plant result. Net = factory price − excise − packaging (2,400 COP); factory price = retail price / (1 + VAT) / (1 + distribution margin).*

| Regime (specific COP/degree; ad valorem; VAT) | Excise per bottle at 16,000 COP | Net per bottle at 10,000 / 16,000 / 25,000 COP | Re-optimized plant (MM COP/year) | Current design kept: margin and NPV |
|---|---|---|---|---|
| Current (243; 20 %; 5 %) | 4,220 | 1,387 / 4,667 / 9,588 | 3,196, NPV 5,397 (500,000 bottles; 3,000 m³) | 3,196; 5,397 |
| Specific component tripled (729; 20 %; 5 %) | 7,582 | −1,975 / 1,306 / 6,226 | 1,902, vinegar only, zero gap; NPV ≈ +750 (estimate) | 1,599; −869 (TEA) |
| Decree 1474/2025 rates, 5 % VAT (750; 30 %; 5 %) | 8,305 | −2,332 / 583 / 4,954 | 1,902, vinegar only | 1,442 (buys no fruit); ≈ −895 (estimate) |
| Decree 1474/2025 rates, 19 % VAT (750; 30 %; 19 %) | 7,891 | −2,903 / −332 / 3,525 | 1,902, vinegar only | 1,442 (buys no fruit); ≈ −895 (estimate) |
| 2026 fiscal bill (750; 35 %; 19 %) | 8,097 | −2,965 / −537 / 3,104 | 1,902, vinegar only | 1,442 (buys no fruit); ≈ −895 (estimate) |

*Estimates use the margin–NPV relation of Section 5.6.1, because the itemized TEA does not apply to designs that process no fruit.*

### 3.2 Tabla de H4 en VPN

Tables 5.9.2a and 5.9.2b in §2.7 above.

### 3.3 Tabla de desglose de la neutralidad (ACV)

Tables 5.9.4b and 5.9.4c in §2.9 above, and Table 5.6.4b in §2.6.

### 3.4 Tabla del frente H3 con intervalos

**[se completa con h3 / h3full]**

### 3.5 Tabla del jugo de hoja

Table 5.1.2a in §2.3 above.

---

## 4. Nota metodológica para el Capítulo 3 (§3.11): prueba de coherencia estequiométrica

> **Stoichiometric coherence of the registry.** Every pair in the registry that links a sugar to a fermentation product must respect the stoichiometric maximum. Glucose and fructose give at most 2 mol of ethanol per mol (0.511 g/g); xylose gives at most 5 mol of ethanol per 3 mol (also 0.511 g/g). Acetic acid from ethanol is bounded by 60/46 g/g, before the acetification yield of 0.94.
>
> The test computes, for each stream, the apparent yield Y = product / fermentable substrate and requires Y ≤ 0.511 g/g. Yields above 0.90 of the maximum are flagged for verification against the source, because industrial fermentations rarely exceed 90–92 % of theory once yeast growth and by-products are accounted for.
>
> The substrate must be stated with its basis: free sugars, total carbohydrate by difference, or sugar equivalent after hydrolysis. A failure on one basis is resolved by the source, not by moving the parameter.
>
> The test runs with the registry-against-code test before every model version, and a failure stops the run as an implementation error would.

*Table 3.11b. Stoichiometric coherence of the registry (version 12 data).*

| Stream | Substrate (basis) | Product | Apparent yield (g/g) | Fraction of maximum | Result |
|---|---|---|---|---|---|
| Pulp juice (Murcia Palacios, 2013) | 158.8 g/L sugar | 65.3 g/L ethanol | 0.411 | 0.80 | pass |
| Peel juice (Seguí and Fito, 2018) | 104 g/kg sugar | 37.4 g/kg ethanol | 0.360 | 0.70 | pass |
| Panela (registry) | 850 g/kg fermentable sugar | 357 g/kg ethanol | 0.420 | 0.82 | pass |
| Leaf juice, free sugars (glucose 10.6 + xylose 16.4) | 27 g/L | 22.2 g/L ethanol | 0.824 | 1.61 | **fail** |
| Leaf juice, carbohydrate by difference | 44.9 g/kg | 21.8 g/kg ethanol | 0.485 | 0.95 | pass, flagged |
| Leaf juice, old upper bound of the range | 44.9 g/kg | 24.5 g/kg ethanol | 0.545 | 1.07 | **fail** (bound removed) |

> Rows to change in Table 3.11 (version 12 status): «Stochastic program — EEV ≤ RP ≤ WS — RP 3,195.5, EEV 3,195.5, WS 3,195.6 MM COP/year: satisfied after each wait-and-see scenario was re-solved from the known design (the first run had stopped at its time limit)»; «TEA — … — relative difference below 10⁻¹⁴ in the 27 current workbooks»; new row «Stoichiometric coherence — Y ≤ 0.511 g/g for every sugar–product pair, flag above 0.90 — one pair failed (leaf juice on free sugars) and was corrected (Section 2.2.5)»; new row «Optimality intervals — every hypothesis verdict reports [solution, dual bound] — reported in Sections 5.9.2–5.9.4».

---

## 5. Resumen del árbitro adversarial

**[se completa tras las rondas de arbitraje]**
