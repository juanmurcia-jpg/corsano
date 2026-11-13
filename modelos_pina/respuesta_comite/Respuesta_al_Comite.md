# Respuesta al Comité Evaluador

**Tesis:** *Designing for the Absent Grid: Simultaneous Synthesis, Sizing and Seasonal Operation of an Off-Grid Pineapple Whole-Plant Biorefinery in Bajo Atrato, Colombia* (borrador v2).
**Informe respondido:** «Informe de evaluación doctoral», Comité de Ingeniería Química y PSE. Veredicto: *Aprobado con cambios mayores*.
**Alcance:**
- las cinco críticas adversariales del informe (§3.1–3.5);
- el bloque P0 del informe (§5.1);
- los defectos que el árbitro de esta respuesta añadió en sus tres rondas (§5).

**Base de cálculo.** Todos los números nuevos salen de re-ejecutar los modelos de la tesis en la rama `modelos-corsano-pina`.
- `modelos_pina/respuesta_comite.py` contiene todas las corridas y se invoca por grupo: `python respuesta_comite.py <grupo>`.
- `modelos_pina/respuesta_cifras.py` produce las cifras canónicas en `results/respuesta/cifras.json`.
- Los resultados están en `modelos_pina/results/respuesta/`: 52 re-optimizaciones del MILP con su TEA.
- Lo que es estimación y no corrida se marca como tal.

---

## 0. Nota para la gestión (en español)

### 0.1 Qué cambia en la tesis

**1. Etanol del jugo de hoja.** El valor central baja de 21,8 a 20,7 kg/t y su rango pasa a 6,5–20,7 kg/t. El diseño no cambia. Las cifras centrales quedan así:

| Cifra | Antes | Ahora |
|---|---|---|
| Margen | 3 196 MM COP/año | 3 164 MM COP/año |
| VPN | 5 397 MM COP | 5 273 MM COP |
| TIRM | 13,5 % | 13,4 % |
| P(VPN > 0) | 0,79 | 0,78 |
| Panela | 146 t | 155 t |
| GWP neto (inventario) | +334 t | +339 t |

Por qué cambia:
- El par etanol–azúcar del registro comparaba el etanol con los azúcares libres. Sobre el carbohidrato del jugo (44,9 g/kg por diferencia), el dato de la fuente equivale al 95 % del máximo estequiométrico.
- El balance de la fuente no cierra: etanol y levadura juntos exigen más azúcar del que hay.
- El valor de diseño se fija en el 90 % del máximo (20,7 kg/t). El extremo inferior del rango, 6,5 kg/t, es el máximo etanol compatible con la levadura que reporta la misma fuente.
- En ese extremo el mejor diseño hallado conserva el mismo equipo (brecha ≤ 14,5 %), con margen de 2 803 MM COP/año, VPN de 3 857 MM COP y 288 t de panela.

**2. Frontera de viabilidad (H4), juzgada por VPN del TEA.** Para la planta sin fruta se usa un TEA real, no la secante:
- sin vinagre: desde ≈ 890 000 botellas;
- con 500 000 botellas: a lo sumo ≈ 1 950 m³ de vinagre;
- con 250 000 botellas: a lo sumo ≈ 2 600 m³;
- sin vino: a lo sumo ≈ 2 750 m³.

Los tres últimos valores interpolan entre diseños hallados; en los puntos de 1 500 m³ no se puede descartar un diseño mejor, así que la frontera real puede estar más abajo. A 3 000 m³, la planta solo de vinagre tiene VPN +1 393 MM COP y TIRM 11,2 %.

Se retira el titular «viable desde 500 000 botellas», porque ese diseño tiene VPN −5 409 MM COP.

**3. Riesgo fiscal.**
- Con el componente específico triplicado, o con las tarifas del Decreto 1474/2025, el mejor diseño hallado abandona el vino (es óptimo certificado con las tarifas del decreto y del proyecto). Queda la planta solo de vinagre: 1 868 MM COP/año y VPN +1 393 MM COP.
- El diseño actual, si se mantuviera, tendría VPN −993 MM COP.
- La planta de vinagre es viable al menos hasta unos 8 kg/t de etanol en el jugo de hoja: su VPN es +553 a 13,5 kg/t y +269 a 11,1 kg/t. Con 6,5 kg/t el mejor diseño hallado tiene VPN −154, pero su cota (1 872) no descarta uno viable.
- Es una planta delgada: TIRM 11,2 % frente a una tasa de descuento del 10 %; su precio de equilibrio del vinagre es 2 074 COP/L, 5,7 % bajo el supuesto de 2 200.
- El riesgo fiscal cambia el producto, no la viabilidad del proyecto, salvo en el extremo más bajo del jugo de hoja.

**4. Neutralidad (H3).**
- El compromiso del borrador (w = 0,75) ya no es neutro con el valor corregido: emite +40 t.
- El diseño de emisión neta nula usa el mismo equipo y cuesta 83 MM COP/año (a lo sumo 129, certificado). Su VPN es 4 873 MM COP.
- Ese diseño es neutro solo con un factor de descomposición ≥ 190 kg/t y si se acepta el crédito de 221 t por 1 162 t de fruta adicional. Sin ese crédito emite +221 t.
- Su caldera quema pulpa de hoja (198 t), no coronas (5,7 t).
- El óptimo económico emite más que el sitio sin planta con cualquier factor: de +121 a +558 t (inventario).

**5. Certificación.**
- El óptimo central queda certificado dentro del 1,5 %; antes se reportaba una brecha de 16,9 %. Hay dos razones: la oferta actúa solo como tope, de modo que los escenarios están anidados, y un rendimiento de hoja mayor nunca reduce el óptimo.
- VSS y EVPI quedan entre 0 y 38 MM COP/año.
- Un punto del frente H3 estaba dominado. Con ε = −645 t pasa de 1 077 a 1 849 MM COP/año y de −873 a −965 t.
- En el mapa H4 se encontraron mejores soluciones en tres puntos.

### 0.2 Desviaciones deliberadas del encargo

1. **Capital.** No se rotula 12 640 MM COP como «~5 021».
   - Los 12 640 MM COP son el capital fijo que estima el MILP: 4 026 MM COP de compra de catálogo multiplicados por el factor de Lang equivalente, 3,14.
   - La compra detallada del TEA es de 5 225 MM COP. La diferencia, 1 199 MM COP, es equipo que el MILP no dimensiona: 930 en tanques de vinagre y de guarda, 128 en el generador de N₂, 85 en la empacadora de harina, 35 en el cuarto frío y 21 en el dosificador de nutrientes.
   - El «~5 021» del comité se acerca a 5 225, pero no es un número del modelo.
2. **Mapa H4.** Se usa el VPN del TEA en los 28 diseños que construyen planta, también los que no procesan fruta. La secante del informe queda como verificación cruzada y como relación para interpretar las cotas duales, que están en margen.
3. **Neutralidad.** El desglose no reparte en «GLP/compost» frente a «crédito de fruta». En el diseño neutro el compostaje *sube* (+54 t). El reparto correcto es:

   | Componente | t CO₂e/año |
   |---|---|
   | Reducción técnica | −183 |
   | Compra de fruta (casi todo es crédito de línea base) | −193 |
   | Menor acopio de hojas | +32 |
   | Otros | +16 |

4. **Tarifas fiscales.**
   - Confirmado por fuentes públicas:
     - el Auto 082 del 29-ene-2026 (exp. RE-387);
     - la Sentencia C-079 de 2026;
     - el Oficio DIAN 4031 de 2026 (IVA del 5 %);
     - el proyecto de «ley de rescate» de 2026, que llevaría el vino al IVA del 19 %.
   - No se pudieron verificar los 750 COP/grado ni los ad valorem del 30 % y el 35 %, porque el texto del decreto y del proyecto no fue accesible desde esta sesión. Se usan como escenario «según el informe del comité», marcado [verify].

### 0.3 Lo que no se re-ejecutó con el valor corregido

Estas partes se calcularon con 21,8 kg/t, el extremo superior del rango, y así se declaran:
- el barrido de autonomía H2;
- el interior del frente H3 (sus dos anclas sí se recalcularon);
- los barridos de precios de §5.4;
- el análisis multiescala de §5.11.

En el óptimo, la corrección baja el margen en 32 MM COP/año (1,0 %) sin cambiar el diseño.

**Queda abierta la conciliación partida por partida** entre la contribución del MILP (6 478 MM COP/año) y el ingreso menos costos variables del TEA (6 992 MM COP/año). Son 514 MM COP/año, el 7 %. Se declara como ítem pendiente (§2.15).

**Paginación.** El borrador es un documento vivo sin paginación fija, así que la matriz cita secciones y tablas.

---

## 1. Matriz de respuesta (Response to Reviewers)

| # | Crítica | Acción tomada | Nuevo dato o ecuación | Dónde se corrige |
|---|---|---|---|---|
| 1 | §3.1 / P0-1: H4 en margen, anunciado en VPN | Mapa H4 en VPN con TEA en los 28 diseños que construyen planta. Las filas con vinagre se re-optimizaron con el etanol de hoja corregido. Cotas duales registradas; la no viabilidad se clasifica por la robustez frente al error de la relación margen–VPN. | Frontera: ≈ 890 000 botellas sin vinagre; a lo sumo ≈ 1 950 m³ a 500 000, ≈ 2 600 m³ a 250 000 y ≈ 2 750 m³ sin vino. Relación: VPN ≈ −5 409 + 3,588 (m − 184); m* = 1 692; error frente al TEA: media 881, máximo 2 706 MM COP (26 diseños). | Resumen; §5.9.2 (Tablas 5.9.2a–b); §5.10; §6.5 |
| 2 | §3.2 / P0-2: par etanol–azúcar del jugo de hoja: 0,82 g/g > 0,511 | Prueba estequiométrica y de cierre de todo el registro. Base corregida: carbohidrato por diferencia, 44,9 g/kg. Valor de diseño al 90 % del máximo: 20,7 kg/t. Rango ampliado a 6,5 kg/t, el valor compatible con la levadura que reporta la fuente. Óptimo, mapa H4, ACV, TEA y H1 re-ejecutados. | Central: margen 3 164; panela 154,6 t; VPN 5 273. Extremos: 2 965 / 2 897 / 2 803 MM COP/año; panela +57 / +76 / +133 t sobre el nuevo central (+66 / +85 / +142 sobre el anterior; el comité estimó +64 a +83); VPN 4 491 / 4 225 / 3 857. Mismo diseño. | §2.2.5 y Ap. B; §3.11; §5.1.1–5.1.2; §5.6.1; §6.5; §6.6 |
| 3 | §3.3 / P0-3: régimen fiscal sin escenario | Nueva §4.1.6 con la cronología verificada. Cinco regímenes evaluados por botella y con MILP + TEA, reoptimizando y con el diseño central fijo. TEA para la planta sin fruta. | Neto por botella a 16 000 COP: 4 667 / 1 306 / 583 / −332 / −537. Desde el específico ×3, el óptimo es la planta solo de vinagre: 1 868 MM COP/año, VPN +1 393. Es óptima certificada con los regímenes del decreto y del proyecto, y la mejor hallada con el específico ×3. Diseño central fijo: 1 567 y VPN −993 (específico ×3); 1 408 sin fruta (decreto y proyecto). | §4.1.6; §5.6.1 (Tabla 5.6.1b); §6.4.2; §6.5 |
| 4 | §3.4 / P1-9: línea base de un solo factor; neutralidad con crédito de fruta | Sensibilidad 190 ± 100 kg CO₂e/t para el óptimo (inventario) y para el diseño de emisión neta nula (MILP). Desglose término a término. Línea base de quema con igual jerarquía. GWP neto en los extremos del rango del jugo de hoja. | Óptimo: +558 / +339 / +121 t (descomposición); +853 / +1 009 / +1 166 t (quema). Diseño neto nulo: +357 / 0 / −357 t. Desglose de 328 t: técnica −183, fruta −193 (crédito −221), hojas +32, otros +16. Sin crédito de fruta: +221 t. Óptimo con la hoja baja: +363 / +374 / +447 t (MILP). | §5.6.4; §5.9.4; §5.10; §6.5 |
| 5 | §3.5 / P1-7: brechas no propagadas; WS < RP; cota de M1 importada | Intervalos [solución, cota dual] en H2, H3 y H4. Certificación del óptimo por anidamiento y por monotonía. WS re-resuelto. Punto dominado de H3 corregido. Cota de M1 sustituida por la medida a 375 m³/año (§5.11.3). | Óptimo: [3 164; 3 210] (≤ 1,5 %). WS = 3 195,6 ≥ RP = 3 195,5 (a 21,8); VSS y EVPI ∈ [0; 38] (a 20,7). H2: recorte del 60 %: 2 453 (solución), certificado entre 1 049 y 3 047. H3 (ε = −645 t): 1 077 → 1 849. | §3.10.2; §3.11; §5.6.3; §5.9.2–5.9.4; §5.10 |
| 6 | P0-4: inconsistencias de edición | Unificadas, cada una con su causa. Tabla canónica añadida (Tabla 5.1.1b). | Capital: 4 026 / 12 640 / 3 314 / 5 225 / 16 405. Caso de 1 500 m³ a 21,8: 1 164 (antes 817 y 926), cota 2 593. «a 60 % cut costs 2,453». Etiqueta de base en cada GWP. 27 libros. 375 m³ producidos, 95 % vendido. Celdas del mapa. Denominador del 33 %. | §2.15 |
| 7 | P0-5: referencias marcadas | Fuentes fiscales verificadas añadidas. Liao et al. 2022 añadida como fuente del balance de la hoja. Lista explícita de las 26 entradas y 7 citas aún marcadas. | — | §2.16 |

---

## 2. Texto reescrito (en inglés, listo para la tesis)

*Convention for all rewritten text: figures are at the corrected leaf-juice ethanol yield of 20.7 kg/t unless labelled «(at 21.8 kg/t)», the former value and upper end of the source's range. Values in MM COP; «t» in emission statements are tonnes of CO₂-equivalent.*

### 2.1 Abstract (third paragraph replaced)

> With bottled wine taxed under Law 1816 of 2016 and market caps of 500,000 bottles and 3,000 m³ of vinegar per year, the optimal plant processes 1,276 t/year of fruit (20.8 % of the supply) and 3,746 t/year of leaves. It sells wine, vinegar fermented from peel and leaf juices with panela, and fibre flour, for an annual margin of 3,164 MM COP, certified within 1.5 % of the optimum, and a net present value of 5,273 MM COP (MIRR 13.4 %, P(NPV > 0) = 0.78). Designing the same superstructure fraction by fraction gives an NPV of only 27 MM COP.
>
> Viability is judged by NPV, not by margin, and it depends on markets. The plant needs about 890,000 bottles a year without vinegar, or no more than about 1,950 m³ of vinegar with 500,000 bottles and about 2,600 m³ with 250,000 bottles. A plant that makes vinegar alone needs no more than about 2,750 m³; at 3,000 m³ its NPV is 1,393 MM COP. That vinegar plant is also the best design found if the wine excise rises to the rates of the emergency decree of December 2025, which the Constitutional Court struck down. Those rates roughly tripled the specific component, and under them wine stops paying.
>
> The ethanol yield of leaf juice rests on one source whose mass balance does not close. It is set at 90 % of its stoichiometric maximum, with a range down to the value compatible with the source's yeast yield. Across that range the design does not change, the NPV of the optimum stays between 3,857 and 5,273 MM COP, and the vinegar plant remains viable at least down to about 8 kg of ethanol per tonne of juice.
>
> Against a site where fruit and leaves decompose, the optimum emits 121–558 t CO₂e/year more over the plausible range of the decomposition factor, and 853–1,166 t more if the leaves would otherwise be burned. A design that burns leaf pulp in a biomass boiler reaches net zero for 83 MM COP/year. It does so only for a factor at or above the central value and with credit for the 1,162 t of extra fruit it buys.
>
> Linking the plant model to yeast kinetics, the fermentation train, an hourly weekly schedule and leaf collection shows that the value of integration lies inside the plant scale. The sugar hub, gasification, bromelain and ethanol are not selected. For Bajo Atrato the conditions of the project are now three: validating the vinegar market, measuring the leaf-juice fermentation and securing the fiscal treatment of fruit wine. Developing technology is not among them.

### 2.2 Section 5.1.1 — capital paragraph (replaces the last two sentences)

> There is no crown boiler, no bromelain module, no leaf ethanol, no digester and no hub product; crown and core are composted.
>
> **Capital.** The catalogue options chosen cost 4,026 MM COP to purchase. With the equivalent Lang factor of 3.14, the MILP estimates their fixed capital at 12,640 MM COP. The annualized capital charge it subtracts is 3,314 MM COP/year: 3,068 for annuity, maintenance and local taxes on purchased equipment (AF = 0.762), plus 246 of fixed costs tied to the chosen options and to the nitrogen generator and nutrient doser.
>
> The itemized TEA lists 5,225 MM COP of purchased equipment. The difference of 1,199 MM COP is equipment the MILP catalogue does not size:
> - storage tanks for 30 days of vinegar and 90 days of wine ageing (930);
> - the nitrogen generator (128), which the MILP charges as a fixed item;
> - the flour packer (85);
> - a cold room (35);
> - the nutrient doser (21), which the MILP charges as a fixed item.
>
> The TEA arrives at a fixed-capital investment of 16,405 MM COP: 10,936 direct, 3,281 engineering, procurement and construction, and 2,187 contingency. Section 6.6 discusses the consequence of leaving storage out of the MILP. Table 5.1.1b gathers the canonical figures of this design.
>
> **Certification.** The margin of this design is 3,164 MM COP/year at the corrected leaf-juice yield, and it is certified within 1.5 % of the optimum. Two properties of the model give the certificate:
> - Supply enters the MILP only as an upper limit (unprocessed fruit and leaves carry no cost), so a larger supply cannot lower the optimum.
> - A higher leaf-juice yield cannot lower it either: the same flows make more acid, and the panela or juice they no longer need can be dropped.
>
> The optimum at 20.7 kg/t is therefore bounded by the dual bound of the run with 1.3 times the supply at 21.8 kg/t, 3,210 MM COP/year.

### 2.3 Section 5.1.2 — «Vinegar carries the plant» (replaced)

> **Vinegar carries the plant.** Without the vinegar routes the optimum earns 184 MM COP/year; with them, 3,164. Its substrate is mostly leaf juice with panela: 2,847 t of leaf juice against 221 t of peel juice, and no wine diverted.
>
> **The source and its two checks.** The acid potential of leaf juice rests on one source, and that source does not close. In Chen et al. (2020), as balanced by Liao et al. (2022), 46 kg of juice give 35 kg of broth at 3.6 % v/v ethanol and 11 kg of wet yeast: 1.0 kg of ethanol, or 21.7 kg per tonne of juice. Two checks follow:
> - **Ethanol alone.** The free sugars of the juice (27 g/L at most) cannot produce that much ethanol (0.82 g/g). On the 44.9 g/kg of carbohydrate the juice holds by difference, the yield is 0.485 g/g, 95 % of the stoichiometric maximum.
> - **Ethanol and yeast together.** The same source reports 16.1 kg of yeast dry matter per tonne of juice. At a biomass yield of 0.5 g/g, that yeast alone consumes about 32 kg of sugar, which leaves room for at most 6.5 kg of ethanol. Ethanol and yeast cannot both be right.
>
> **The value adopted.** This thesis takes the ethanol figure, which rests on a measured broth concentration, as the design basis, capped at 90 % of the stoichiometric maximum: 20.7 kg/t. The range extends down to 6.5 kg/t, the ethanol compatible with the reported yeast (Table 5.1.2a). The yeast figure is used only by the leaf-ethanol route, which no economic design selects. It is flagged in the registry.
>
> **Effect on the optimum.** The design is the same at every value of the range: the same equipment and the same 3,000 m³ of vinegar. Panela makes up the acid the leaf juice no longer supplies, from 155 t/year to as much as 288 t/year. The margin falls from 3,164 to 2,803 MM COP/year and the NPV from 5,273 to 3,857 MM COP at the lower end, losses of 11 % and 27 %. The designs at the lower values are the best found within the time limit; the table gives their gaps to the bound of Section 5.1.1, up to 14.5 % at 6.5 kg/t.
>
> The leaf-juice yield changes the cost of vinegar, not whether vinegar is made. A plant that makes only vinegar is viable at least down to about 8 kg/t; below that its viability is not established (Section 5.6.1). A fermentation of Chocó leaf juice with the plant's strain is the measurement that would close this range (Section 6.7).

*Table 5.1.2a. Optimum against the leaf-juice ethanol yield (500,000 bottles; 3,000 m³ of vinegar).*

| Leaf-juice ethanol (kg/t juice) | Basis | Acid potential (kg/t juice) | Margin (MM COP/year) | Upper bound (gap) | Panela (t/year) | NPV (MM COP) | Net GWP (t; MILP) |
|---|---|---|---|---|---|---|---|
| 21.8 (former value) | source ethanol; 95 % of maximum on carbohydrate | 26.7 | 3,196 | 3,210 (0.4 %) | 145.6 | 5,397 | +323 |
| **20.7 (design value)** | **90 % of maximum on 44.9 g/kg carbohydrate** | **25.3** | **3,164** | **3,210 (1.5 %)** | **154.6** | **5,273** | **+328** |
| 13.5 | maximum (0.511 g/g) on free sugars only | 16.6 | 2,965 | 3,210 (8.3 %) | 211.6 | 4,491 | +363 |
| 11.1 | 0.42 g/g on free sugars only | 13.6 | 2,897 | 3,210 (10.8 %) | 230.8 | 4,225 | +374 |
| 6.5 | compatible with the source's yeast yield | 8.0 | 2,803 | 3,210 (14.5 %) | 287.7 | 3,857 | +447 |

*The upper bound is the dual bound of the run at 1.3 times the supply and 21.8 kg/t, valid at every lower yield by nesting and monotonicity (Section 5.1.1). The bounds of the runs at each yield are weaker (3,439; 4,424; 4,396) and are not used.*

### 2.4 Section 5.6.1 — Techno-economic assessment (text after the case table rewritten)

*(Case table: the first row becomes «Optimum (configuration A): FCI 16,405; NPV 5,273; MIRR 13.4 %; payback 5.0 years; P(NPV > 0) 0.78; medium». A new row is added: «Vinegar only (100,000-bottle cap or high excise): FCI 13,721; NPV 1,393; MIRR 11.2 %». The other rows were computed at 21.8 kg/t and are labelled so.)*

> The TEA confirms the ranking of the MILP. From the TRL-9 reference to the optimum the NPV rises from −12,454 to 5,273 MM COP and the MIRR from −22.8 % to 13.4 %; P(NPV > 0) rises from 0 to 78 %. Without vinegar the optimum loses money (NPV −5,409 MM COP, P(NPV > 0) = 0.02).
>
> **Margin is not viability.** The annual margin of the MILP is computed after the annualized capital charge. It comes before payroll, supervision, the other fixed costs, income tax and the phased start-up, which the TEA includes.
>
> Over the designs of the demand map, NPV and margin follow approximately
>
> NPV ≈ −5,409 + 3.588 (m − 184) MM COP. (5.1)
>
> The relation passes through the design without vinegar and the optimum at 21.8 kg/t. Against the full TEA of 26 other designs it deviates by 881 MM COP on average and by 2,706 at most; the largest deviation is at 12,000 m³ of vinegar, an extrapolation. It places the break-even margin at about 1,692 MM COP/year.
>
> The relation is empirical. It is used only to read the dual bounds of the MILP, which are in margin, as statements about NPV (Section 5.9.2), never in place of a TEA. For designs that process no fruit, the TEA sizes the wine and flour lines for a token 1 kg of fruit, which avoids a division by zero: their flows and consumables are zero, and the idle units the MILP selects are still costed, so the NPV of these designs is conservative. For designs with fruit the TEA is unchanged.
>
> **Cost structure of the optimum.**
> - Revenue is 12,089 MM COP/year: 5,362 from wine at the factory price and 6,727 from vinegar and flour.
> - Variable costs are 5,097 MM COP/year. Raw materials account for 4,497 of them: the excise on the 475,000 bottles sold (95 % of the 500,000 produced, the sales convention of Table 4.1) about 2,000, packaging about 1,140, panela 541, fruit 511 and leaf collection 133, with composting and chemicals making up the rest. Utilities cost 580 and waste treatment 21.
> - Fixed costs are 2,227 MM COP/year, working capital is 610 MM COP and operating cost totals 7,324 MM COP/year.
> - The payback is 5.0 years (6.6 discounted), and the break-even vinegar price is 1,723 COP/L, 22 % below the assumed 2,200.
> - Over 1,000 correlated Monte Carlo samples the NPV has a median of 3,543 MM COP, a 5th–95th percentile range of −4,127 to 11,526, and a CVaR at 5 % of −6,347.
>
> The excise is the largest single cost of the plant, and its rate is not stable (Section 4.1.6).
>
> **Fiscal sensitivity (Table 5.6.1b).** Under the current regime a bottle sold at 16,000 COP leaves 4,667 COP after excise, VAT, distribution and packaging. The other regimes leave:
> - 1,306 COP with the specific component tripled;
> - 583 COP with the rates of Decree 1474 of 2025 and 5 % VAT, and −332 COP with 19 % VAT;
> - −537 COP under the 2026 fiscal bill.
>
> **The re-optimized plant.** From the tripled specific component upwards, the re-optimized plant stops making wine. It becomes a vinegar plant fed by leaf juice and panela, earning 1,868 MM COP/year with an NPV of 1,393 MM COP and an MIRR of 11.2 %:
> - under the decree and bill rates this design is certified optimal, because its dual bound equals its margin;
> - with only the specific component tripled it is the best design found (dual bound 3,312).
>
> **The vinegar plant against the leaf-juice yield.** Its viability rests on the leaf-juice yield. Its NPV is 553 MM COP at 13.5 kg/t, 269 at 11.1 kg/t and −154 for the best design found at 6.5 kg/t, the value compatible with the source's yeast yield. It is therefore viable at least down to about 8 kg/t. At 6.5 kg/t a viable design is not ruled out: that run stopped far from its own bound, and by monotonicity the vinegar-only optimum there cannot exceed 1,872 MM COP/year, the bound at 20.7 kg/t.
>
> The vinegar plant is thin. Its MIRR of 11.2 % is close to the 10 % discount rate, and its break-even vinegar price is 2,074 COP/L, only 5.7 % below the assumed 2,200.
>
> **The current design kept.** If the design optimized for the current regime is kept, it does worse:
> - with the specific component tripled it earns 1,567 MM COP/year and its NPV is −993 MM COP;
> - under the decree and bill rates it stops buying fruit and earns 1,408 MM COP/year.
>
> The wine line is therefore the part of the project exposed to fiscal risk. A high excise changes what the plant sells, not whether it is viable, unless the leaf-juice yield is also at the low end of its range.
>
> **Company size and income tax.** By its revenue in UVT the optimum is a medium-sized company, so with start-up in 2030 it pays the general rate of 35 % in every year. At 21.8 kg/t, the proposed ZOMAC extension (Bill 435 of 2025) would raise the optimum's NPV by 1,632 MM COP; the no-cap designs would gain 6,457 (wine) and 10,448 (vinegar). The ZOMAC location does not exempt the wine from the departmental excise.

### 2.5 Section 5.6.3 — Stochastic design (rewritten)

> The two-stage program varies supply only, at 0.7, 1.0 and 1.3 times the central value with probabilities 0.25, 0.5 and 0.25.
>
> **The violated test.** At 21.8 kg/t the version 12 run reported RP = 3,196 and WS = 3,195 MM COP/year, which violates EEV ≤ RP ≤ WS. By the protocol of Section 3.11 that is an error, not a result. The wait-and-see problem of the central scenario had stopped at its time limit (3,193.7), below a design already known; the mean-value problem EV is the same scenario and had stopped at the same value. Re-solving each scenario from that design gives WS = 3,195.6 ≥ RP = 3,195.5 MM COP/year, with the same design in every scenario.
>
> **Bounds.** Supply enters the MILP only as an upper limit, so the feasible sets are nested and the optimum with more supply bounds the optimum with less. A higher leaf-juice yield likewise cannot lower the optimum. At the corrected yield the runs give:
>
> | Supply scenario | Solution at 20.7 kg/t | Valid upper bound |
> |---|---|---|
> | 0.7 | 3,164.1 | 3,178.1 (its own run) |
> | 1.0 | 3,164.0 | 3,210.1 (run at 1.3 times the supply, 21.8 kg/t) |
> | 1.3 | 3,164.1 | 3,210.1 (same run) |
>
> Hence:
> - 3,164.0 ≤ RP ≤ WS ≤ 0.25 × 3,178.1 + 0.75 × 3,210.1 = 3,202.1;
> - EVPI and VSS lie between 0 and 38 MM COP/year, 1.2 % of the margin;
> - the same bounds certify the central optimum within 1.5 %.
>
> **What the program shows.** The stochastic design is the deterministic one. This was expected: with both markets capped, supply is not an active constraint, and even the low scenario offers more fruit than the wine market absorbs. The two-stage program answers only the supply question, and the answer is that supply does not matter at this scale.
>
> Market and fiscal uncertainty, which do matter, are not represented in this program. They are treated by the demand map (Section 5.9.2), the price tornado and the Monte Carlo (Section 5.6.2), and the fiscal regimes (Table 5.6.1b). A two-stage program with demand and excise as uncertain parameters is future work (Section 6.7).

### 2.6 Section 5.6.4 — Life-cycle assessment (rewritten)

*(Contribution table: Panela becomes 93 t; process total becomes 1,293 t; the other rows are unchanged.)*

> Process GWP is 1,293 t CO₂e/year, or 1,013 kg per tonne of fruit processed. The largest item is the leaf pulp the extractor returns to the field: 674 t/year that carry about two thirds of the leaves' dry matter and still decompose there. Earlier versions credited the plant for all the leaves it collects but did not count this return. The correction (Section 4.2) raises process GWP and changes the sign of the net result. Diesel electricity and glass bottles follow. Effluent treatment removes 97 % of 7.9 t of COD for 11 t CO₂e.
>
> **The net result and its two assumptions.** The net GWP subtracts what the site would emit without a plant. It rests on two assumptions:
> - **One decomposition factor.** A single IPCC factor (4 g CH₄ and 0.3 g N₂O per kg of wet material, 190 kg CO₂e/t) values the fruit and leaves in the baseline, the fractions composted in the plant and the leaf pulp returned to the field.
> - **The fate of the leaves.** Without a plant they would decompose, or they would be burned.
>
> Table 5.6.4b varies both:
> - From 90 to 290 kg CO₂e/t, the optimum adds between 121 and 558 t CO₂e/year against a decomposing baseline, and between 853 and 1,166 t against a burning baseline.
> - Raising the factor lowers the net result, because it multiplies 954 t CO₂e of baseline emissions but only 539 t CO₂e of process emissions.
> - The sign is robust: under every combination tested, the economic optimum emits more than the site without a plant.
> - At the lower end of the leaf-juice range, the optimum needs more panela, and its net GWP on the MILP basis rises to +447 t (Table 5.1.2a).
>
> Burning leaves emits little GWP but much particulate matter, and the plant then avoids 4.8 t/year of particulates.
>
> The figures of this section use the life-cycle inventory: 1,293 t of process emissions and +339 t net. The MILP carries a linear GWP of 1,282 t (+328 t) that omits effluent treatment (11 t). Each figure in this thesis names its basis.
>
> **The supply premise.** The baseline also assumes that the fruit the plant buys would otherwise be discarded. This thesis takes the 2022 production of Chocó as the supply available to the plant. The only measured reject stream, however, is 144 t/year in one municipality (Murcia Palacios, 2013), and Section 2.1.3 gives a scenario of 1,536 t at 25 % shrinkage. At 1,276 t/year the optimum stays within that scenario. Fruit diverted from the fresh market would carry no baseline credit; Section 5.9.4 shows why this matters for the low-GWP designs.
>
> **Credits and allocation.** System-expansion credits are zero for the optimum, which makes neither ethanol nor surplus power. By economic allocation, a bottle of wine carries 1.15 kg CO₂e (44 % of the burden), a litre of vinegar 0.22 kg (52 %) and a kilogram of flour 1.22 kg (4 %).

*Table 5.6.4b. Net GWP of the economic optimum against the decomposition factor and the leaf counterfactual (t CO₂e/year; life-cycle inventory).*

| Decomposition factor (kg CO₂e/t wet) | 90 | 190 (central) | 290 |
|---|---|---|---|
| Process GWP | 1,009 | 1,293 | 1,577 |
| Baseline: fruit and leaves decompose | 452 | 954 | 1,456 |
| **Net GWP, decomposing baseline** | **+558** | **+339** | **+121** |
| Baseline: fruit decomposes, leaves burned | 156 | 284 | 412 |
| **Net GWP, burning baseline** | **+853** | **+1,009** | **+1,166** |

### 2.7 Section 5.9.2 — Minimum viable demand (H4), rewritten

> Section 3.12.4 defines the H4 frontier as the line NPV = 0. The design was re-optimized over 30 combinations of market size, and the dual bound of each free run was recorded:
> - the rows with 1,500 m³ of vinegar or more were re-optimized at the corrected leaf-juice yield;
> - the rows with 0 and 750 m³ use no leaf juice and are unchanged;
> - the TEA was run on every design that builds a plant, 28 points (Table 5.9.2a);
> - the two designs at 100,000 bottles with 0 or 750 m³ have as best design the mandatory minimum front end, with a margin of −1,090 MM COP/year; the real alternative, not building, has an NPV of 0.
>
> **The frontier.** Interpolating the NPV between grid points:
> - **Without vinegar,** the plant is viable from about 890,000 bottles a year (NPV −5,409 at 500,000; +1,500 at 1,000,000).
> - **With 500,000 bottles** it needs at most about 1,950 m³ of vinegar (NPV −2,239 at 1,500 m³; +5,273 at 3,000 m³).
> - **With 250,000 bottles** it needs at most about 2,600 m³ (NPV −5,837 at 1,500 m³; +1,995 at 3,000 m³).
> - **A plant that makes vinegar alone** needs at most about 2,750 m³ (NPV −7,128 at 1,500 m³; +1,393 at 3,000 m³).
> - **At 1,000,000 bottles and above,** every vinegar level is viable.
>
> The earlier reading of this map, «viable from about 500,000 bottles», took a positive margin for viability. It is withdrawn: that design has an NPV of −5,409 MM COP.
>
> **What the dual bounds establish.** The margins are the best solutions found, and their dual bounds limit what any design could earn at that point (Table 5.9.2b). Four points that decide the frontier have dual bounds below the break-even margin of about 1,692 MM COP/year. Turning a bound in margin into a statement about NPV requires Equation 5.1, which is empirical, so the strength of each conclusion is measured by the NPV error the relation would have to make for a viable design to exist there:
> - **Not viable, robustly:** 250,000 bottles without vinegar (error needed 8,514) and 500,000 bottles without vinegar (5,064). Both are far beyond the largest error observed, 2,706.
> - **Not viable as found, but not established:**
>   - 250,000 bottles with 1,500 m³ (error needed 2,390);
>   - 500,000 bottles with 1,500 m³ (error needed 616).
>
>   A better, viable design cannot be ruled out at these two points. The frontier at 500,000 bottles therefore lies somewhere between 1,500 and about 1,950 m³ of vinegar.
> - The 750 m³ points have no recorded bound.
>
> **Three points improved.** The re-optimization at the lower leaf-juice yield found better designs than the earlier map:
>
> | Point (bottles; vinegar) | New design at 20.7 kg/t | Earlier map |
> |---|---|---|
> | 500,000; 1,500 m³ | 1,150 MM COP/year | 926 |
> | 250,000; 1,500 m³ | 272 | −7 |
> | 2,000,000; 6,000 m³ | 11,847 | 10,563 |
>
> Evaluated at 21.8 kg/t, these designs earn 1,164, 287 and 11,902 MM COP/year. The earlier map's solutions at those points were not optimal, which the weak bounds of its free runs had allowed.
>
> **What H4 now says.** Viability depends on the demand for both products far more than on technology or supply. The frontier is more demanding than first reported:
> - Below about 890,000 bottles the plant cannot rest on wine.
> - The vinegar cap of 3,000 m³ is at least 50 % above the vinegar the plant needs at 500,000 bottles.
> - A vinegar plant without wine is viable at 3,000 m³ and, by interpolation of the designs found, from no more than about 2,750 m³.
>
> Vinegar demand is the market study that decides the project, and the wine market decides how much margin it has (Section 6.4).

*Table 5.9.2a. NPV of the re-optimized design for each pair of market sizes (MM COP; full TEA; leaf-juice ethanol 20.7 kg/t). At 100,000 bottles the designs process no fruit and make no wine; «not built» means that the best design builds nothing.*

| Vinegar (m³/year) \ bottles/year | 100,000 (no wine) | 250,000 | 500,000 | 1,000,000 | 2,000,000 |
|---|---|---|---|---|---|
| 0 | not built | −10,240 | −5,409 | 1,500 | 3,899 |
| 750 | not built | −10,240 | −5,409 | 1,500 | 8,577 |
| 1,500 | −7,128 | −5,837 | −2,239 | 3,224 | 13,318 |
| 3,000 | 1,393 | 1,995 | 5,273 | 11,440 | 22,312 |
| 6,000 | 15,653 | 16,301 | 19,614 | 25,860 | 36,650 |
| 12,000 | 43,536 | 43,474 | 46,746 | 52,764 | 55,967 |

*Table 5.9.2b. Points that decide the frontier: margin of the design found, dual bound of its free run (MM COP/year), NPV of the design found, and what the bound establishes. Break-even margin about 1,692; «error needed» is the NPV error of Equation 5.1 that would allow a viable design at the bound (largest observed error: 2,706).*

| Point (bottles; vinegar m³) | Margin found | Dual bound | NPV (TEA) | Error needed | Status |
|---|---|---|---|---|---|
| 250,000; 0 | −683 | −682 | −10,240 | 8,514 | not viable, robust |
| 500,000; 0 | 184 | 280 | −5,409 | 5,064 | not viable, robust |
| 1,000,000; 0 | 1,911 | 2,255 | 1,500 | — | viable |
| 250,000; 1,500 | 272 | 1,025 | −5,837 | 2,390 | not viable as found; not established |
| 500,000; 1,500 | 1,150 | 1,520 | −2,239 | 616 | not viable as found; not established |
| 100,000; 3,000 (vinegar only) | 1,868 | 1,872 | 1,393 | — | viable (margin within 0.25 % of its bound) |
| 250,000; 3,000 | 2,286 | 2,647 | 1,995 | — | viable |
| 500,000; 3,000 (central) | 3,164 | 3,210 | 5,273 | — | viable |

### 2.8 Section 5.9.3 — H2 table with intervals (replaces the table; at 21.8 kg/t)

> Lowering the cap on fossil energy (3,818 GJ/year in the optimum) gives the solutions below, with the dual bounds of their free runs. This sweep was computed at 21.8 kg/t with the heat pump available. In that model the unconstrained optimum is 3,196 MM COP/year, with a dual bound of 3,789.
>
> The certified cost range of each cut is computed as follows:
> - **Lower end.** A tighter cap only removes designs, so the true cost cannot fall as the cut deepens. The certified minimum cost of a cut is therefore the largest value of (3,196 − dual bound of the capped run) over that cut and all shallower ones.
> - **Upper end.** The certified maximum is 3,789 minus the margin found.
>
> The bounds are weak, so the costs at the solutions found are the ones this thesis reports.

| Fossil cap (% of optimum) | Margin found | Dual bound | Cost at the solutions found | Certified cost range |
|---|---|---|---|---|
| 100 | 3,196 | 3,789 | — | — |
| 80 (a 20 % cut) | 3,039 | 4,957 | 157 | 0 to 750 |
| 60 (a 40 % cut) | 1,673 | 2,488 | 1,523 | 708 to 2,116 |
| 40 (a 60 % cut) | 742 | 2,147 | 2,453 | 1,049 to 3,047 |
| 20 (an 80 % cut) | 30 | 2,660 | 3,166 | 1,049 to 3,759 |
| 0 (full autonomy) | −1,642 | none (no finite bound) | 4,838 | 1,049 to 5,431 |

> The first 20 % is cheap: 157 MM COP/year at the solutions found and at most 750 certified, and it is where the heat pump enters.
>
> A 60 % cut costs 2,453 MM COP/year at the solutions found, and between 1,049 and 3,047 with certainty. It cuts vinegar, because aeration of the acetifier is the largest electricity use and only diesel supplies it.
>
> Full autonomy means not operating.
>
> H2 is supported in the form tested here, the ε-constraint sweep. The flexibility index named in the original wording of H2 is formulated (Section 3.6.3) but not run, and the verdict does not rest on it.

### 2.9 Section 5.9.4 — H3: front with intervals and the anatomy of net zero (rewritten)

> The ε-constraint front was computed at 21.8 kg/t. Each interior point was re-solved with a longer free run, and its dual bound was recorded.
>
> At ε = −645 t the longer run found a design that earns 1,849 MM COP/year and emits −965 t net. The point published earlier (1,077 MM COP/year; −873 t) was dominated, and Table 5.9.4a replaces it.
>
> Along the front, at 21.8 kg/t, the margin falls monotonically as the cap tightens, so the front is non-degenerate. It is the best front found, not a certified one: its dual bounds lie well above the solutions, and the points that do not operate profitably have no finite bound.

*Table 5.9.4a. Margin–net GWP front (linear GWP of the MILP; at 21.8 kg/t).*

| Design | Margin found (MM COP/year) | Dual bound | Net GWP (t CO₂e/year) | NPV (MM COP) | What changes from the optimum |
|---|---|---|---|---|---|
| Economic optimum | 3,196 | 3,789 (with heat pump) | +323 | 5,397 | — |
| ε = −161 t | 2,525 | 3,548 | −288 | 2,407 | no leaves; 3 t/h front end, centrifuge, 100 kWt boiler |
| Compromise w = 0.50 | 2,330 | — | −502 | 1,495 | 5,555 t of fruit, 1,951 t of leaves, 100 kWt boiler |
| ε = −645 t (corrected) | 1,849 | 4,529 | −965 | −1,776 | 30,468 t of leaves, 10 t/h extractor, leaf ethanol, 300 kWt boiler |
| ε = −1,129 t | 125 | 4,485 | −1,129 | — | as above, operated for GWP |
| ε = −1,612 t and −2,096 t | −3,517 and −3,806 | none | −1,612 and −2,096 | — | all fruit and up to all leaves, digester and 200 kWe engine |
| Minimum net GWP | −4,084 | — | −2,580 | −31,880 | all 6,146 t of fruit and 32,469 t of leaves |

*The designs that use leaf ethanol (ε ≤ −645 t) also sell the yeast that the source reports (16.1 kg per tonne of juice). Section 5.1.2 shows that this figure cannot hold together with the source's ethanol, so their margins are upper values.*

> **What makes a design net-zero (at 20.7 kg/t).** At the corrected leaf-juice yield, the compromise found earlier (w = 0.75) is no longer neutral: with its sizes fixed it earns 3,089 MM COP/year and emits +40 t.
>
> A free run with net GWP ≤ 0, started from that design, keeps the same equipment. It earns 3,081 MM COP/year at net zero, with an NPV of 4,873 MM COP. Net zero therefore costs 83 MM COP/year at the solutions found. It costs at most 129 with certainty in the superstructure without heat pump, because there the unconstrained optimum cannot exceed 3,210; the net-zero design uses no heat pump, so it is feasible in that superstructure.
>
> Its boiler, the option called «crown boiler» in the catalogue, burns 198 t of leaf pulp and only 5.7 t of crown. The earlier statement that this design buys fruit «partly for its crowns» is withdrawn.
>
> Table 5.9.4b decomposes the 328 t that separate it from the economic optimum into four groups:
> - **Technical reduction, −183 t.** Burning 198 t of leaf pulp instead of returning it to the field saves 141 t, and displacing all LPG heat saves 57 t, against +15 t of combustion emissions.
> - **Fruit purchase, −193 t.** Buying 1,162 t more fruit earns 221 t of baseline credit. Composting its cores and crowns adds +54 t and transporting it +5 t. Diverting 341 m³ of wine to vinegar saves 31 t of panela.
> - **Leaf boundary, +32 t.** Collecting 713 t fewer leaves avoids 91 t of field return and 13 t of collection diesel, but loses 135 t of baseline credit.
> - **Other, +16 t.** Electricity and chemicals.
>
> **Two conditions.** The net-zero design depends on both:
> - **The fruit credit.** Without it (if the extra fruit came from the fresh market rather than from reject), the design would emit +221 t. At 2,439 t/year it buys more fruit than the 1,536 t of the 25 %-shrinkage scenario of Section 2.1.3, so part of that credit is not supported by the supply data.
> - **The decomposition factor.** Its net GWP is zero or negative only for factors at or above the central 190 kg CO₂e/t: +357 t at 90 and −357 t at 290 (Table 5.9.4c).
>
> The economic optimum emits more than the no-plant site under every combination tested. The net-zero design remains the one this thesis recommends if the environmental objective is weighted at all: 183 t of its improvement come from a real change of technology, and it costs little. Its claim to net zero must state both conditions.

*Table 5.9.4b. Change in GWP from the economic optimum to the net-zero design (t CO₂e/year; linear GWP of the MILP; at 20.7 kg/t).*

| Term | Economic optimum | Net-zero design | Change | Group |
|---|---|---|---|---|
| Leaf pulp returned to the field: fewer leaves collected (713 t) | 478.8 | 247.0 | −91.2 | leaf boundary |
| Leaf pulp returned to the field: 198 t burned instead | (included above) | (included above) | −140.6 | technical |
| LPG heat | 57.2 | 0.0 | −57.2 | technical |
| Biomass boiler (CH₄, N₂O) | 0.0 | 15.0 | +15.0 | technical |
| Leaf collection (diesel) | 66.8 | 54.1 | −12.7 | leaf boundary |
| Composting of cores and crowns | 60.6 | 114.7 | +54.1 | fruit |
| Fruit transport | 5.2 | 9.9 | +4.7 | fruit |
| Panela | 92.8 | 61.4 | −31.4 | fruit |
| Diesel electricity (including aeration) | 207.0 | 214.1 | +7.0 | other |
| Glass bottles | 250.0 | 250.0 | 0.0 | other |
| Chemicals and other | 63.9 | 72.8 | +8.9 | other |
| **Process GWP** | **1,282.2** | **1,039.0** | **−243.2** | |
| Baseline: fruit (1,276 → 2,439 t) | 242.4 | 463.1 | credit +220.7 | fruit |
| Baseline: leaves (3,746 → 3,033 t) | 711.4 | 575.9 | credit −135.5 | leaf boundary |
| **Net GWP (process − baseline)** | **+328.4** | **0.0** | **−328.4** | |

*By group: technical −182.7; fruit −193.2; leaf boundary +31.6; other +15.9.*

*Table 5.9.4c. Net GWP against the decomposition factor (t CO₂e/year; linear GWP of the MILP; at 20.7 kg/t; decomposing baseline).*

| Decomposition factor (kg CO₂e/t wet) | 90 | 190 | 290 |
|---|---|---|---|
| Economic optimum | +547 | +328 | +110 |
| Net-zero design | +357 | 0 | −357 |

### 2.10 Section 5.10 — Testing hypotheses H1–H4 (table rewritten)

| Hypothesis | Verdict | Evidence |
|---|---|---|
| H1. Simultaneous synthesis, sizing and operation beat sequential design by fractions | Supported, with one qualification | The same superstructure designed by fractions in sequence earns 1,816 against 3,164 MM COP/year, 42.6 % less (NPV 27 against 5,273) (Section 5.9.1). The sequential protocol has no feedback between stages, so the gap measures sequential design without iteration. Seasonal coupling adds nothing at the capped scale and 4.4–12.2 % when capacity binds (at 21.8 kg/t). At train level the hierarchical chain costs 3.8–12.5 % more at the flow of the optimum (7.1–9.0 % at the original basis; Section 5.11). |
| H2. Energy autonomy has a measurable cost in margin and portfolio | Supported (ε-constraint sweep) | A 20 % cut in fossil energy costs 157 MM COP/year at the solutions found (0–750 certified), with the heat pump. A 60 % cut costs 2,453 (1,049–3,047 certified) and cuts vinegar. Full autonomy means not operating (Section 5.9.3; at 21.8 kg/t). The flexibility index of the original wording is formulated but not run, and the verdict does not rest on it. |
| H3. The margin–GWP front is non-dominated and non-degenerate, with GWP against a no-plant baseline | Partly supported | A non-degenerate front exists (at 21.8 kg/t). It is the best found, not certified: its dual bounds lie far above the solutions, and one published point was dominated and has been replaced (Table 5.9.4a). The economic optimum emits more than the no-plant site for every decomposition factor from 90 to 290 kg/t (+121 to +558 t on the inventory basis; +110 to +547 t on the MILP basis). Net zero costs 83 MM COP/year (at most 129). It holds only for factors at or above 190 kg/t and with credit for 1,162 t of extra fruit (Section 5.9.4). |
| H4. With the current supply, viability depends more on the demand and price of the main products than on technology | Supported, with a corrected frontier | Over 30 market pairs the NPV ranges from −10,240 to +55,967 MM COP. The frontier NPV = 0 lies at about 890,000 bottles without vinegar, and at no more than about 1,950 m³ of vinegar with 500,000 bottles, 2,600 m³ with 250,000 and 2,750 m³ without wine (interpolated from the designs found). The designs without vinegar at 250,000 and 500,000 bottles are robustly not viable (Section 5.9.2). At high excise rates the best design found is the vinegar-only plant (NPV 1,393; Section 5.6.1). Supply from 0.5 to 3.6 times the central value leaves the capped optimum unchanged (at 21.8 kg/t); EVPI and VSS are between 0 and 38 MM COP/year. |

> H1 needs two qualifications. First, at the scale of Chocó its gain comes from synthesis across fractions, not from coupling design with seasonal operation, which matters only when capacity binds. Second, it says nothing about sharing equipment between products: the multiplant–multiproduct comparison (Section 2.8.6) shows that question is close economically and decided by staffing, which in Bajo Atrato has social weight of its own.
>
> H4 is the hypothesis the thesis did not start with and the one its results support most strongly. Judged by NPV, its frontier is more demanding than first reported. It places the vinegar market, and the leaf-juice fermentation that feeds it, at the centre of the project.

### 2.11 Section 6.5 — Conclusions against each objective

> **Objective 1** (sentences added at the end). A stoichiometric and closure test of every sugar-to-product pair of the registry found one inconsistent source: the leaf juice, whose ethanol had been compared with its free sugars and whose reported ethanol and yeast cannot both hold. The design value was set at 90 % of the stoichiometric maximum on carbohydrate, 20.7 kg/t. The range extends to 6.5 kg/t, the value compatible with the reported yeast.
>
> **Objective 2: unit and train models.** The fermentation models were calibrated and verified:
> - The single measured point of pulp juice does not identify its kinetics: a family of parameter pairs fits it equally well and changes the design fermentation time by a factor of 2.3.
> - Moresi's winery model was replicated, with his numbers of fermenters reproduced exactly. Its kinetics were shown to be invalid at the 30 °C of the pineapple data, and the premium-line advantage claimed earlier is an artefact of changing model.
> - The glucose–xylose kinetics of the juices cut the processing time of the juice winery from 32.5 to 12.6 h.
> - Fixing kinetics before sizing costs 7.1–9.0 % of the fermentation-train cost at the original design basis and 3.8–12.5 % at the wine flow of the optimum. The band of fermentation times left by the single point does not change the plant design (Section 5.11).
>
> **Objective 3** (sentences added at the end). The dual bounds of the free runs are now reported beside every hypothesis test. Two properties of the model, supply as an upper limit and the monotonic effect of the leaf-juice yield, certify the central optimum within 1.5 %. The bounds show, robustly against the largest observed error of Equation 5.1, that the designs without vinegar at 250,000 and 500,000 bottles are not viable, but they do not certify the margin–GWP front, whose bounds remain weak.
>
> **Objective 4: assessment under uncertainty.** The optimum has an NPV of 5,273 MM COP, an MIRR of 13.4 % and P(NPV > 0) = 0.78, with a break-even vinegar price 22 % below the assumed price. Two uncertainties outside the Monte Carlo were quantified:
> - **The leaf-juice yield.** Across its range it lowers the NPV of the optimum to as little as 3,857 MM COP, without changing the design.
> - **The wine excise.** At three times its current specific rate, or at the rates of the annulled Decree 1474 of 2025, wine stops paying. The best design found is then a vinegar-only plant of 1,868 MM COP/year and NPV 1,393, viable at least down to a leaf-juice yield of about 8 kg/t, but with a break-even vinegar price only 5.7 % below the assumed price. The current design kept unchanged would have an NPV of −993 MM COP.
>
> The plant emits 1,293 t CO₂e/year in process. Against a site where fruit and leaves decompose, it adds 121–558 t over the plausible range of the decomposition factor; if the leaves would otherwise be burned, it adds 853–1,166 t. Burning leaf pulp in a biomass boiler makes it net-zero for 83 MM COP/year, but only at the central factor or above and with credit for the extra fruit it buys.
>
> The plant retains 2,021 MM COP/year in the territory with about 17 jobs (local purchases 555 MM COP/year with the extra panela). Supply uncertainty has no value (VSS and EVPI between 0 and 38 MM COP/year); market and fiscal uncertainty dominate.
>
> **Objective 5: the Bajo Atrato biorefinery.** The optimal plant processes 1,276 t/year of fruit and 3,746 t/year of leaves into 500,000 bottles of wine, 3,000 m³ of vinegar and 40 t of fibre flour. Its equipment:
> - a 1 t/h front end, one shared press, flotation and SO₂;
> - two 10 m³ fermenters and a 500 bottles/h line;
> - a juice winery and a 10 m³ acetifier;
> - a 2 t/h leaf extractor and a small dryer.
>
> Under the current excise it is viable if vinegar sells above 1,723 COP/L and wine near 16,000 COP per bottle. The hypotheses come out as follows:
> - **H1** is supported against a sequential design of the same superstructure (NPV 27 against 5,273 MM COP).
> - **H2** is supported by the autonomy sweep.
> - **H3** is partly supported: the front is non-degenerate but not certified, and net zero is conditional.
> - **H4** is supported with a corrected frontier: the plant is viable from about 890,000 bottles without vinegar, or with no more than about 1,950 m³ of vinegar at 500,000 bottles, 2,600 m³ at 250,000, or 2,750 m³ without wine.
>
> **Objective 6: rules and policy.** Markets, the excise on fruit wine and one fermentation datum now limit the project, not feedstock or technology. The design rules for a larger wine market are known from the scale sweep: front end first; then presses, centrifugation and the crown boiler; enzyme recovery and a third shift only from three times the supply.
>
> The vinegar line carries the project under every fiscal regime tested, as long as the leaf-juice yield is not at the bottom of its range. Without wine, however, the margin of safety is small: the vinegar-only plant breaks even at 2,074 COP/L, 5.7 % below the assumed vinegar price. The order of work is therefore:
> 1. a study of vinegar demand;
> 2. a fermentation of Chocó leaf juice with the plant's strain;
> 3. a study of the volume and price of bottled fruit wine.
>
> The policy levers are demand, a stable and differentiated excise for small regional fruit-wine producers, and renewable electricity.

> **Resumen (Spanish abstract), third paragraph replaced:**
>
> «Con el vino embotellado y su impuesto al consumo (Ley 1816 de 2016), y con topes de mercado de 500 000 botellas y 3 000 m³ de vinagre al año, el óptimo procesa 1 276 t/año de fruta y 3 746 t/año de hojas. Vende vino, vinagre de jugos de cáscara y de hojas con panela y harina de fibra. Da un margen de 3 164 MM COP/año, certificado dentro del 1,5 % del óptimo, y un VPN de 5 273 MM COP (TIRM 13,4 %; P(VPN > 0) = 0,78). Diseñar la misma superestructura fracción por fracción deja un VPN de solo 27 MM COP.
>
> La viabilidad se juzga por el VPN y depende del mercado. Hacen falta unas 890 000 botellas sin vinagre, o no más de unos 1 950 m³ de vinagre con 500 000 botellas y unos 2 600 m³ con 250 000. Una planta solo de vinagre necesita no más de unos 2 750 m³; a 3 000 m³ su VPN es de 1 393 MM COP. Esa planta de vinagre es también el mejor diseño hallado si el impuesto al vino sube a las tarifas del decreto de emergencia de diciembre de 2025, que la Corte declaró inexequible. Esas tarifas aproximadamente triplicaban el componente específico, y con ellas el vino deja de pagar.
>
> El rendimiento en etanol del jugo de hoja se apoya en una sola fuente cuyo balance no cierra. Se fija en el 90 % de su máximo estequiométrico, con un rango que baja hasta el valor compatible con la levadura que reporta la fuente. En todo ese rango el diseño no cambia, el VPN del óptimo queda entre 3 857 y 5 273 MM COP y la planta de vinagre sigue siendo viable al menos hasta unos 8 kg de etanol por tonelada de jugo.
>
> Frente a un sitio donde la fruta y las hojas se descomponen, el óptimo emite entre 121 y 558 t CO₂e/año más según el factor de descomposición, y entre 853 y 1 166 t más si las hojas se quemaran. Un diseño que quema pulpa de hoja en una caldera de biomasa alcanza emisión neta nula por 83 MM COP/año, pero solo con un factor igual o mayor al central y con el crédito de las 1 162 t de fruta adicional que compra.
>
> El valor de integrar queda dentro de la escala de planta. Ni el hub de azúcares, ni la gasificación, ni la bromelaína, ni el etanol entran. Validar el mercado del vinagre, medir la fermentación del jugo de hoja y asegurar el tratamiento fiscal del vino de fruta, no desarrollar tecnología, son ahora las condiciones del proyecto.»

### 2.12 New Section 4.1.6 — Regulatory risk of the wine excise (Chapter 4)

> **4.1.6 Regulatory risk of the wine excise**
>
> **The rates in force.** The excise rates of Section 4.1.3 are those in force in 2026:
> - a specific component of 243 COP per alcoholic degree in 750 cm³ (Certification 003 of 2025, Ministry of Finance);
> - an ad valorem component of 20 % (Law 1816 of 2016, art. 20);
> - VAT of 5 % (Tax Code, art. 468-1; DIAN, Oficio 4031 of 2026).
>
> **Why they are in force.** They are in force because of a court decision. Legislative Decree 1474 of 29 December 2025, issued under a declared economic emergency, raised the taxes on liquors and wines. The Constitutional Court suspended it provisionally on 29 January 2026 (Order 082, file RE-387). It then declared it unconstitutional in Ruling C-079 of 2026 and ordered the indirect taxes collected under it to be refunded. A fiscal bill presented to Congress in 2026 would again move wines from 5 % to the general 19 % VAT and raise the consumption tax, mainly from 2027.
>
> **The rates proposed.** According to the evaluation committee:
> - the decree set a specific component of 750 COP per degree, with a 30 % ad valorem component and 19 % VAT;
> - the 2026 bill proposes 750 COP per degree with a 35 % ad valorem component, indexed at inflation plus four points from 2028. That indexation would bring the specific component to roughly 900–1,000 COP per degree by 2030.
>
> These rates are taken from the committee's report and remain to be verified against the texts. For a project that starts in 2030 and whose largest single cost is this excise, the rate is a project risk, not a constant.
>
> **The regimes evaluated.** Five regimes are evaluated, per bottle by the relation of Section 4.1.3 and for the whole plant by re-solving the MILP and the TEA (Table 5.6.1b):
> 1. the current one;
> 2. the specific component tripled (729 COP per degree);
> 3. the decree rates with 5 % VAT;
> 4. the decree rates with 19 % VAT;
> 5. the 2026 bill without indexation.
>
> Indexation would only deepen the loss on wine. From regime 2 onwards the best design already makes no wine, so its result also holds for the indexed bill.

### 2.13 Chapter 2, Section 2.2.5 — replacement paragraph on leaf juice, and registry rows (Appendix B)

> **Leaf juice.** Extraction yields 0.76 t of juice per tonne of leaves (Liao et al., 2026; 0.77 in Chen et al., 2020).
>
> **Composition.**
> - The juice holds 6.2 % solids, of which 14 % is crude protein, 10.0 % ash and 3.5 % fat (Liao et al., 2022, Table 1, from Chen et al., 2020). By difference it holds about 44.9 g of carbohydrate per kg.
> - The free monosaccharides reported are 10.6 g/L of glucose and 16.4 g/L of xylose (Chen et al., 2020). Liao et al. (2022) give 0.6 g/L of C6 sugars for the same juice, a discrepancy to be resolved in the original.
>
> **Fermentation.** Fermented by *Kluyveromyces marxianus* at 35 °C without supplements, 46 kg of juice gave 35 kg of broth at 3.6 % v/v ethanol and 11 kg of wet yeast. That is about 1.0 kg of ethanol, or 21.7 kg per tonne of juice, and 16.1 kg of yeast dry matter per tonne.
>
> **Checks.**
> - The ethanol is 0.485 g/g of carbohydrate, 95 % of the stoichiometric maximum. The free sugars alone could not produce it (0.82 g/g on them), so the yeast must also use part of the soluble oligosaccharides.
> - Ethanol and yeast together do not close. At a biomass yield of 0.5 g/g, the yeast alone would consume about 32 kg of sugar per tonne, which leaves room for at most 6.5 kg of ethanol.
>
> **Value adopted.**
> - This thesis takes the ethanol figure, which rests on a measured broth concentration, capped at 90 % of the stoichiometric maximum: 20.7 kg/t is the design value.
> - Its range is 6.5–20.7 kg/t. The lower end is the most ethanol compatible with the reported yeast (100 % of theory on the residual sugar and the maximum biomass yield; 5.9 kg/t with the 0.90 ceiling). It is not a pessimistic floor.
> - The yeast figure is flagged; it is used only by the leaf-ethanol route.
>
> A fermentation of Chocó leaf juice that measures ethanol, residual sugars and biomass together is the first measurement this thesis asks for (Section 6.7).

*Registry rows (Appendix B), before → after:*

| Key | Before | After |
|---|---|---|
| `azucar_jugo_hojas` | 27.0 g/L (glucose 10.6 + xylose 16.4) | renamed `azucar_libre_jugo_hojas`, 27.0 g/L, [L], Chen et al. 2020 (C6 0.6 g/L in Liao et al. 2022: [verify]) |
| `carbohidrato_jugo_hojas` (new) | — | 44.9 g/kg, [L, derived], by difference from Liao et al. 2022, Table 1 |
| `etanol_jugo_hojas` | 21.8 (18–24.5) kg/t, [L] | 20.7 (6.5–20.7) kg/t, PERT, [L/S]: 90 % of the stoichiometric maximum on carbohydrate. Source value 21.8 (95 %) kept in the notes. Old upper bound 24.5 removed (0.545 g/g, above stoichiometry). Lower end: the most ethanol compatible with the reported yeast (at most 6.5; 5.9 with the 0.90 ceiling). |
| `levadura_jugo_hojas` | 16.1 kg DM/t, [L] | 16.1 kg DM/t, [L, flagged]: inconsistent with the source's ethanol (closure test, Section 3.11); used only by the leaf-ethanol route |

### 2.14 Section 3.10.2 — table rows corrected

| Case | Free run | After polishing | Best known | Dual bound | Reported gap |
|---|---|---|---|---|---|
| Optimum (at 20.7 kg/t; certified by nesting and monotonicity, Section 5.1.1) | — | — | 3,164 | 3,210 | 1.5 % |
| Vinegar demand 1,500 m³ (at 21.8 kg/t) | 245 | 592 (v12) | 1,164 (design found at 20.7 kg/t, evaluated at 21.8) | 2,593 (version 13 map) | 123 % |
| Vinegar demand 6,000 m³ (at 21.8 kg/t) | 5,548 | 6,634 (v12) | 7,086 (version 13 map) | 7,619 | 7.5 % |
| 1 million bottles (at 21.8 kg/t) | 4,366 | 4,469 (v12) | 4,942 (version 13 map) | 6,757 | 36.7 % |

> *Note for the text.*
> - The vinegar case of 1,500 m³ was reported as 817 MM COP/year in version 12 and as 926 in the version 13 map. The design found in the re-optimization at 20.7 kg/t earns 1,164 at 21.8 kg/t, which supersedes both values. Its dual bound comes from the free run of the version 13 map.
> - The optimum's former gap of 16.9 % is superseded by the certificate of Section 5.1.1.

### 2.15 Editorial corrections (exact replacements)

| Location | Before | After |
|---|---|---|
| §5.4.2, price grid, row PVP 16,000 / vinegar 2,200 | 3,194 · 5,389 | 3,196 · 5,397, labelled «(at 21.8 kg/t)». The whole grid was computed at that value, and that grid point had stopped 0.06 % below the optimum, within the 0.2 % fixed-design tolerance. |
| §5.4.2, column header | «Wine sold (m³)» | «Wine produced (m³)». The TEA sells 95 % of it (Table 4.1). |
| §5.4.3 and E8 table, vinegar demand 1,500 m³ | 817 | 1,164 (at 21.8 kg/t; Section 3.10.2) |
| §5.4.3, vinegar demand 6,000 m³ | 6,634 | 7,086 (at 21.8 kg/t) |
| §5.4.x, 250,000 bottles | 2,319 | 2,317 (at 21.8 kg/t) |
| §3.10.2 and §5.4.x, 1 million bottles | 4,941 | 4,942 (at 21.8 kg/t) |
| §5.10 (H2) | «60 % costs 2,454» | «a 60 % cut costs 2,453» (3,195.6 − 742.3) |
| §5.6.4, §5.9.4, abstract | «+334», «+323» without basis | «+339 t (life-cycle inventory, 1,293 t)» and «+328 t (linear GWP of the MILP, 1,282 t; the 11 t difference is effluent treatment)». At 21.8 kg/t: +334 and +323. |
| §3.11 and §4.1.5 | «16 workbooks» | «27 workbooks» (all current workbooks; Appendix D) |
| §5.6.1 | «the excise on 475,000 bottles sold» | «the excise on the 475,000 bottles sold (95 % of the 500,000 produced, the sales convention of Table 4.1)» |
| §2.7.3 | «2,675 GJ of recoverable heat (33 %)» | «2,675 GJ of recoverable heat (33 % of the 8,043 GJ drying demand)» |
| §5.1.1 | «The equivalent purchased-equipment cost entering the capital charge is 12,640 MM COP» | text of §2.2 of this response |
| Preamble of Chapter 5 | «the kinetics bound (7.1–9.0 % …) applies to every figure» | «the kinetics–train coupling is worth 3.8–12.5 % of the fermentation-train cost at the flow of the optimum (Section 5.11.3), and the kinetic band does not change the plant design (Section 5.11.1)» |
| New §6.6 item | — | «**Storage outside the MILP.** Storage tanks for vinegar (30 days) and wine ageing (90 days), 930 MM COP of purchased equipment, are costed by the TEA but not sized by the MILP. Its objective therefore omits about 709 MM COP/year of capital charge (AF × 930), 22 % of the margin of the optimum. Every NPV reported includes them. Vinegar is produced in eight times the volume of wine and stored a third as long, so its tanks are about 2.7 times larger (620 of the 930 MM COP); leaving storage out therefore favours vinegar in the MILP's choice. The size of the omission makes adding storage to the catalogue the next model change.» |
| New §6.6 item | — | «**Results at the former leaf-juice yield.** The autonomy sweep (H2), the interior of the margin–GWP front (H3), the price sweeps of Section 5.4 and the multiscale tests of Section 5.11 were computed at 21.8 kg/t, the upper end of the corrected range. At the optimum the correction lowers the margin by 32 MM COP/year (1.0 %) without changing the design.» |
| New §6.6 item | — | «**MILP contribution and TEA.** The contribution of the MILP before capital charge (6,478 MM COP/year) and the revenue less variable costs of the TEA (6,992 MM COP/year) differ by 514 MM COP/year (7 %). The two accountings use different price and cost conventions (Sections 3.9 and 4.1) and were not built to coincide. An item-by-item reconciliation is pending. Every viability statement uses the TEA.» |

### 2.16 References

**Added (verified):**
- Corte Constitucional de Colombia (2026). Auto 082 de 2026, 29 January 2026, expediente RE-387 (provisional suspension of Legislative Decrees 1390 and 1474 of 2025).
- Corte Constitucional de Colombia (2026). Sentencia C-079 de 2026 (Legislative Decree 1474 of 2025 declared unconstitutional).
- DIAN (2026). Oficio 4031 de 2026 (VAT of 5 % on wines after the suspension of Decree 1474 of 2025).
- Liao, C. Y., Guan, Y. J., & Bustamante-Román, M. (2022). Techno-economic analysis and life cycle assessment of pineapple leaves utilization in Costa Rica. *Energies*, 15(16), 5784. https://doi.org/10.3390/en15165784

**Added (to be verified):**
- Presidencia de la República de Colombia (2025). Decreto Legislativo 1474 de 2025, 29 December 2025 [verify rates].
- Ministerio de Hacienda y Crédito Público (2026). Fiscal bill presented to Congress in 2026 («ley de rescate») [verify number and rates].

**Still marked, to be resolved against the original before the defence:**
- **26 reference-list entries:** Arpagaus et al. 2018; Burk 2026 [complete]; Castro et al. 2018; Celis Cabeza et al. 2024; Corsano et al. 2009; Dak et al. 2008; Galanopoulos et al. 2020; García García et al. 2023; Guillén-Gosálbez et al. 2019; Hossain et al. 2016; Huang et al. 2020; Indrawan et al. 2020; Kasani et al. 2022; Kouakou et al. 1987; Martín et al. 2023; Morales-Rodriguez et al. 2012; Moreno et al. 2022; Nickel et al. 2020; OECD 2022; OECD 2023; Steingass et al. 2015; Towler & Sinnott 2022; Uslu et al. 2024; Vaillant et al. 1999; Zhang & Rosentrater 2019.
- **Citation chains:** «cited by Ebrahimi, 2026» and «cited by Iakovchenko, 2026».
- **7 citations in the text:** Hossain et al. 2016; Celis Cabeza et al. 2024; Bustos et al. 2014; the lignin content of crown and leaves (Saini et al. 2022); Kouakou et al. 1987; the income-tax schedule (statute); Balanzó Guzmán et al. 2021.

---

## 3. Nuevas tablas de datos

### 3.1 Tabla de sensibilidad fiscal del vino (Table 5.6.1b, for the thesis)

*Table 5.6.1b. Wine excise regimes: net revenue per 750 mL bottle and whole-plant result (leaf-juice ethanol 20.7 kg/t). Net = factory price − excise − packaging (2,400 COP); factory price = retail price / (1 + VAT) / (1 + distribution margin). The excise follows the relation of Section 4.1.3.*

| Regime (specific COP/degree; ad valorem; VAT) | Excise per bottle at 16,000 COP | Net per bottle at 10,000 / 16,000 / 25,000 COP | Re-optimized plant (MM COP/year; NPV) | Current design kept: margin (MM COP/year) and NPV (MM COP) |
|---|---|---|---|---|
| Current (243; 20 %; 5 %) | 4,220 | 1,387 / 4,667 / 9,588 | 3,164; NPV 5,273 (500,000 bottles; 3,000 m³) | 3,164; 5,273 |
| Specific component tripled (729; 20 %; 5 %) | 7,582 | −1,975 / 1,306 / 6,226 | 1,868, vinegar only (best found; dual bound 3,312); NPV 1,393 | 1,567; −993 |
| Decree 1474/2025 rates, 5 % VAT (750; 30 %; 5 %) | 8,305 | −2,332 / 583 / 4,954 | 1,868, vinegar only (certified); NPV 1,393 | 1,408, buys no fruit |
| Decree 1474/2025 rates, 19 % VAT (750; 30 %; 19 %) | 7,891 | −2,903 / −332 / 3,525 | 1,868, vinegar only (certified); NPV 1,393 | 1,408, buys no fruit |
| 2026 fiscal bill, no indexation (750; 35 %; 19 %) | 8,097 | −2,965 / −537 / 3,104 | 1,868, vinegar only (certified); NPV 1,393 | 1,408, buys no fruit |
| *Vinegar-only plant at lower leaf-juice yields* | — | — | NPV 553 at 13.5 kg/t; 269 at 11.1 kg/t; −154 at 6.5 kg/t | — |

*With 19 % VAT the excise per bottle is lower than with 5 %, because the ad valorem base, the retail price before VAT, is smaller. The net per bottle is still lower.*

### 3.2 Tabla de H4 en VPN

Tables 5.9.2a and 5.9.2b in §2.7 above.

### 3.3 Tablas del desglose de la neutralidad y de la sensibilidad del ACV

Tables 5.9.4b and 5.9.4c in §2.9 above, and Table 5.6.4b in §2.6.

### 3.4 Tabla del frente H3 con intervalos

Table 5.9.4a in §2.9 above.

### 3.5 Tabla del jugo de hoja

Table 5.1.2a in §2.3 above.

### 3.6 Tabla canónica del diseño central (new Table 5.1.1b)

*Table 5.1.1b. Canonical figures of the central design (500,000 bottles; 3,000 m³ of vinegar; leaf-juice ethanol 20.7 kg/t).*

| Quantity | Value | Basis |
|---|---|---|
| Annual margin | 3,164 MM COP/year | MILP; certified within 1.5 % (upper bound 3,210) |
| Contribution before capital charge | 6,478 MM COP/year | MILP |
| Annualized capital charge | 3,314 MM COP/year | MILP: AF × 4,026 purchase + 246 fixed |
| Purchased equipment | 4,026 (MILP catalogue) / 5,225 (TEA, with storage and auxiliaries) MM COP | |
| Fixed-capital investment | 12,640 (MILP, Lang 3.14) / 16,405 (TEA) MM COP | |
| Revenue; revenue less variable costs | 12,089; 6,992 MM COP/year | TEA (95 % of production sold) |
| Variable / fixed / operating costs | 5,097 / 2,227 / 7,324 MM COP/year | TEA |
| NPV; MIRR; payback | 5,273 MM COP; 13.4 %; 5.0 years (6.6 discounted) | TEA |
| P(NPV > 0); median NPV; CVaR 5 % | 0.78; 3,543; −6,347 MM COP | Monte Carlo, 1,000 samples |
| Break-even vinegar price | 1,723 COP/L | TEA tornado |
| Panela | 154.6 t/year | MILP |
| Process GWP; net GWP | 1,293 t; +339 t (inventory) / 1,282 t; +328 t (MILP) | ACV / MILP |

---

## 4. Nota metodológica para el Capítulo 3 (§3.11): prueba de coherencia estequiométrica y de cierre

> **Stoichiometric coherence and closure of the registry.** Every pair in the registry that links a sugar to a fermentation product is tested in three steps.
>
> 1. **Stoichiometric bound.** The apparent yield Y = product / fermentable substrate must not exceed the stoichiometric maximum:
>    - glucose and fructose give at most 2 mol of ethanol per mol (0.511 g/g);
>    - xylose gives at most 5 mol of ethanol per 3 mol, also 0.511 g/g;
>    - acetic acid from ethanol is bounded by 60/46 g/g, before the acetification yield of 0.94.
>
>    The substrate must be stated with its basis: free sugars, total carbohydrate by difference, or sugar equivalent after hydrolysis.
> 2. **Design ceiling.** A design value above 0.90 of the maximum is not accepted, because industrial fermentations rarely exceed 90–92 % of theory once yeast growth and by-products are accounted for. Above that ceiling, the design value is set at 0.90 of the maximum and the source value is kept in the notes.
> 3. **Closure of the source.** When the source also reports biomass, the sugar consumed must not exceed the fermentable substrate: product / 0.511 + biomass / 0.5 ≤ carbohydrate, with the biomass yield on sugar taken at its aerobic maximum of 0.5 g/g. A source that fails this test cannot have all its outputs right. The thesis then states which output it adopts and why, and it extends the parameter's range to the value compatible with the other output.
>
> The test runs with the registry-against-code test before every model version. A failure stops the run, as an implementation error would.

*Table 3.11b. Stoichiometric coherence and closure of the registry.*

| Stream | Substrate (basis) | Product | Apparent yield (g/g) | Fraction of maximum | Result |
|---|---|---|---|---|---|
| Pulp juice (Murcia Palacios, 2013) | 158.8 g/L sugar | 65.3 g/L ethanol | 0.411 | 0.80 | pass |
| Peel juice (Seguí and Fito, 2018) | 104 g/kg sugar | 37.4 g/kg ethanol | 0.360 | 0.70 | pass |
| Panela (registry) | 850 g/kg fermentable sugar | 357 g/kg ethanol | 0.420 | 0.82 | pass |
| Leaf juice, source ethanol on free sugars (glucose 10.6 + xylose 16.4) | 27 g/L | 22.2 g/L ethanol | 0.824 | 1.61 | **fail** |
| Leaf juice, source ethanol on carbohydrate by difference | 44.9 g/kg | 21.8 g/kg ethanol | 0.485 | 0.95 | above the design ceiling |
| Leaf juice, closure with the source's yeast (16.1 kg/t) | 44.9 g/kg | sugar used: 42.7 (ethanol) + 32.2 (yeast) = 74.9 g/kg | — | 1.67 | **fail**: ethanol and yeast cannot both hold |
| Leaf juice, old upper bound | 44.9 g/kg | 24.5 g/kg ethanol | 0.545 | 1.07 | **fail** (removed) |
| **Leaf juice, design value adopted** | **44.9 g/kg** | **20.7 g/kg ethanol** | **0.460** | **0.90** | **pass**; yeast flagged |
| Leaf juice, lower end of the range (closure with the yeast) | 44.9 g/kg | 6.5 g/kg ethanol + 16.1 g/kg yeast | 0.145 | 1.00 of the substrate | closes |

> **Rows to change in Table 3.11 (version 12 status):**
> - **Stochastic program.** «EEV ≤ RP ≤ WS — satisfied after each wait-and-see scenario was re-solved from the known design (the first run had stopped at its time limit); at 20.7 kg/t, 3,164.0 ≤ RP ≤ WS ≤ 3,202.1».
> - **TEA.** «relative difference below 10⁻¹⁴ in the 27 current workbooks».
> - **New row: stoichiometric coherence and closure.** «Y ≤ 0.511 g/g for every sugar–product pair; design ceiling 0.90; closure with reported biomass — one source failed (leaf juice) and was corrected (Section 2.2.5)».
> - **New row: optimality intervals.** «every hypothesis verdict reports [solution, dual bound]; the central optimum is certified by nesting of supply and monotonicity in the leaf-juice yield — reported in Sections 5.1.1, 5.6.3 and 5.9.2–5.9.4».

---

## 5. Resumen del árbitro adversarial

**Mandato.** El árbitro actuó como el comité. Tenía que verificar uno por uno los seis puntos del listón y cada cifra contra los JSON de `results/respuesta/` y el código. Podía re-ejecutar cualquier corrida, pero no editar el entregable. Hubo tres rondas: 46 defectos en total y cuatro corridas nuevas a raíz de ellos.

| Ronda | Versión revisada | Veredicto | Defectos | Qué obligó a cambiar |
|---|---|---|---|---|
| 1 | v1 | Rechazo | 19 (D1–D19) | Valor central de la hoja, certificaciones falsas, atribución de la neutralidad |
| 2 | v2 | Rechazo («revisión menor») | 13 (N1–N13) | Cierre de la fuente, robustez de la no viabilidad, TEA de la planta sin fruta |
| 3 | v3 | **Aceptado**, sujeto a 14 correcciones de texto (R1–R14), todas aplicadas | 14 | Calificativos de frontera, cotas por monotonía, precio de equilibrio de la planta de vinagre |

### 5.1 Ronda 1: textos rechazados y correcciones

- **D1. Certificación falsa.** Se rechazó «the vinegar-only plant is certified optimal under the tripled excise». La corrida tenía brecha de 11,9 %. Ahora: «best design found (dual bound 3,312)»; solo los regímenes del decreto y del proyecto quedan certificados (cota = margen).
- **D3. Los puntos de 100 000 botellas que no construyen nada.** Antes se leían como «no viables», pero su mejor diseño es no construir (VPN 0). Ahora se rotulan «not built».
- **D5. Valor central de la hoja.** 21,8 kg/t equivale al 95 % del máximo y viola el techo de diseño de 0,90. El central bajó a 20,7 kg/t y se re-ejecutaron el óptimo, el mapa H4, el ACV, el TEA y H1.
- **D6. «The same design».** Se afirmaba sobre corridas con brecha; ahora dice «best found».
- **D8. Atribución de la neutralidad.** Se rechazó «buys fruit partly for its crowns»: la caldera quema 198 t de pulpa de hoja y solo 5,7 t de corona. De ahí sale el desglose de la Tabla 5.9.4b.
- **D11. Cotas del programa estocástico.** El EV y el WS(1,0) de la v12 se habían detenido en 3 193,7. Se sustituyeron por las cotas de anidamiento.
- **D15, D19. Valores editoriales y referencias.** Corregidos 7 086, 2 317 y 4 942, el denominador del 33 % y el encabezado del vino.
- **D18. Tanques de almacenamiento.** Están fuera del MILP; se declararon en §6.6.

### 5.2 Ronda 2: textos rechazados y correcciones

- **N1. El valor 20,7 tampoco cierra con la levadura de la fuente** (56,6 > 55,8 kg/t). Se eligió explícitamente el dato de etanol, se marcó la levadura y el rango se amplió hasta 6,5 kg/t. Se corrió el óptimo en ese extremo: 2 803 MM COP/año y VPN 3 857.
- **N2. Se rechazó «certified not viable» para el mapa H4.** La cota está en margen y la relación margen–VPN es empírica (desviación de hasta 2 706). Ahora cada punto se clasifica por el error que haría falta para voltear el juicio; solo 250 000 y 500 000 botellas sin vinagre son robustamente no viables.
- **N3. La planta solo de vinagre se juzgaba con la secante sobre corridas con ~100 % de brecha.** Ahora tiene TEA real: VPN +1 393 a 20,7 kg/t, +553 a 13,5, +269 a 11,1 y −154 a 6,5.
- **N4. El óptimo central se reportaba con 3,7 % de brecha.** Ahora está certificado dentro del 1,45 %, por anidamiento de la oferta y monotonía en el rendimiento de hoja. También se registra el tercer punto mejorado (2M;6 000 = 11 847).
- **N5. Resumen.** Se rechazó «only at the central factor»; ahora dice «at or above the central value».
- **N6. Costo de la neutralidad.** El costo de 83 venía de una corrida libre con brecha de 49 %. Ahora: «83 at the solutions found, at most 129 with certainty».
- **N8. Brecha de compras TEA–MILP.** Se rechazó «slightly». Los 1 199 MM COP se desglosan partida por partida, el cargo omitido por almacenamiento (709 MM COP/año, 22 % del margen) se declara y la brecha de contribución de 514 MM COP/año queda como ítem abierto.
- **N9. Procedencia.** Las corridas hechas con guiones auxiliares pasaron a funciones de `respuesta_comite.py`.
- **N10–N13.** Corregidos 0,25 % (antes 0,2 %), el específico ×3 como «best found», la rejilla de §5.4.2 rotulada a 21,8 y la panela +57/+76/+133 sobre el nuevo central.

### 5.3 Ronda 3: correcciones finales (todas aplicadas)

- **R1. Objetivo 3.** Se rechazó «designs without vinegar below about 890,000 bottles are not viable»; ahora queda limitado a 250 000 y 500 000 botellas.
- **R2. Umbral de la planta de vinagre.** Se rechazó «decides viability below about 8 kg/t». Ahora: «viable at least down to about 8 kg/t». A 6,5 kg/t no queda establecido, porque la cota por monotonía (1 872) no descarta un diseño viable.
- **R3. Frontera.** Los valores de 1 950, 2 600 y 2 750 m³ pasan a «a lo sumo», porque interpolan desde puntos de 1 500 m³ que no están establecidos.
- **R4. Tabla 5.1.2a.** Se reemplazaron las cotas propias, más débiles, por 3 210, válida por monotonía. Las brechas quedan en 8,3 %, 10,8 % y 14,5 %.
- **R5. Bomba de calor en H3.** El frente H3 se corrió con bomba de calor, así que la cota del óptimo es 3 789. El «≤ 129» de la neutralidad vale en la superestructura sin bomba, que el diseño neutro no usa.
- **R6. TEA sin fruta.** Se rechazó «their cost is zero»: los equipos ociosos sí se costean, así que el VPN es conservador.
- **R7. Tanques.** Se rechazó «eight times the volume» aplicado al almacenamiento. Los tanques de vinagre son unas 2,7 veces mayores (620 de los 930 MM COP).
- **R8. Nota en español.** Se alineó con el inglés: «mejor diseño hallado» donde no hay certificado.
- **R9. Redacción.** «to as little as 3,857».
- **R10. Fruta adicional.** 2 438,65 − 1 276,50 = 1 162 t, no 1 163.
- **R11. Puntos que no construyen.** Se corrigió la redacción contradictoria.
- **R12. Caso de 1 500 m³.** La cota pasa a la del mapa v13 (2 593; 123 %).
- **R13. Valor de 6,5 kg/t.** Se aclara que es el máximo compatible con la levadura, no un piso pesimista (5,9 kg/t con el techo de 0,90).
- **R14. Margen de seguridad de la planta de vinagre.** Corrida nueva (`python respuesta_comite.py be_vin`): su precio de equilibrio del vinagre es 2 074 COP/L, 5,7 % bajo el supuesto de 2 200. Se añadió esa salvedad en §0.1, §2.4 y las conclusiones.

### 5.4 Lo que el árbitro verificó por su cuenta en la ronda 3

- Releyó el código del MILP (`dimensionamiento.py`) para confirmar el anidamiento: la fruta sobrante va a una pérdida sin precio y las hojas entran solo como tope.
- Confirmó la monotonía en el rendimiento de hoja con las corridas `mono` (1 164 > 1 150; 287 > 272; 11 902 > 11 847).
- Recalculó el desglose de 1 199 MM COP desde los precios del TEA.
- Verificó todas las cifras de §0–§4 contra los JSON.

**Veredicto final del árbitro:** los seis puntos del listón quedan en PASS y los defectos de las rondas anteriores, cerrados.
