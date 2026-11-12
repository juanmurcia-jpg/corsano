# Respuesta al Comité Evaluador

**Tesis:** *Designing for the Absent Grid: Simultaneous Synthesis, Sizing and Seasonal Operation of an Off-Grid Pineapple Whole-Plant Biorefinery in Bajo Atrato, Colombia* (borrador v2).
**Informe respondido:** «Informe de evaluación doctoral», Comité de Ingeniería Química y PSE. Veredicto: *Aprobado con cambios mayores*.
**Alcance:** las cinco críticas adversariales (§3.1–3.5 del informe), el bloque P0 (§5.1) y los defectos que el árbitro de esta respuesta añadió en sus rondas (§5).
**Base de cálculo:** cada número nuevo sale de re-ejecutar los modelos de la tesis.
- Rama: `modelos-corsano-pina`.
- Scripts: `modelos_pina/respuesta_comite.py` (corridas) y `modelos_pina/respuesta_cifras.py` (cifras canónicas).
- Resultados: `modelos_pina/results/respuesta/` (40 re-optimizaciones del MILP con su TEA). Todas las cifras de las secciones 2–4 están en `results/respuesta/cifras.json`.
- Las estimaciones que no salen de una corrida se marcan como tales.

---

## 0. Nota para la gestión (en español)

### 0.1 Qué cambia en la tesis

**El valor central del etanol del jugo de hoja baja de 21,8 a 20,7 kg/t, y con él todas las cifras centrales:**

| Cifra | Antes | Ahora |
|---|---|---|
| Margen | 3 196 MM COP/año | 3 164 MM COP/año |
| VPN | 5 397 MM COP | 5 273 MM COP |
| TIRM | 13,5 % | 13,4 % |
| P(VPN > 0) | 0,79 | 0,78 |
| Panela | 146 t | 155 t |
| GWP neto | +334 t | +339 t |

- El diseño no cambia.
- El par etanol–azúcar violaba la estequiometría porque comparaba el etanol con los azúcares libres. Sobre el carbohidrato del jugo (44,9 g/kg por diferencia) el dato de la fuente da 0,485 g/g, el 95 % del máximo teórico.
- Ese dato está por encima del techo de 90 % que la nueva prueba de §3.11 fija para un dato de diseño. Además, el balance de la propia fuente no cierra: etanol + CO₂ + levadura suman 58,8 kg/t frente a 55,8 kg/t de sólidos orgánicos.
- Por eso el valor de diseño pasa al 90 % del máximo (20,7 kg/t) y el rango queda en 11,1–20,7 kg/t.

**La frontera de viabilidad (H4) se juzga por VPN y queda así:**

| Caso | Vinagre necesario |
|---|---|
| Sin vinagre | desde ≈ 890 000 botellas |
| 500 000 botellas | ≈ 1 950 m³ |
| 250 000 botellas | ≈ 2 600 m³ |
| Planta solo de vinagre | 3 000 m³ queda justo en el umbral (VPN estimado +632 MM COP, dentro del error de la estimación) |

El titular «viable desde 500 000 botellas» se retira: ese diseño tiene VPN −5 409 MM COP.

**Riesgo fiscal.**
- Con el componente específico triplicado o con las tarifas del Decreto 1474/2025, el óptimo abandona el vino. Queda una planta solo de vinagre de 1 868 MM COP/año, en el umbral de viabilidad.
- El diseño actual mantenido tendría VPN −993 MM COP.
- Si además el jugo de hoja rinde menos que el valor central, la planta solo de vinagre deja de ser viable: a 13,5 kg/t su VPN es ≈ −137 MM COP y a 11,1 kg/t ≈ −396.
- Conclusión: con el impuesto alto, el proyecto depende del rendimiento del jugo de hoja.

**Neutralidad (H3).**
- El diseño de compromiso del borrador (w = 0,75) ya no es neutro con el valor corregido: emite +40 t.
- El diseño neutro con el valor corregido usa el mismo equipo, cuesta 83 MM COP/año y tiene VPN 4 873 MM COP.
- Su neutralidad depende de dos condiciones:
  - el factor de descomposición (+357 t con 90 kg/t; −357 t con 290 kg/t);
  - el crédito de 221 t por las 1 162 t de fruta adicional. Sin ese crédito emite +221 t.
- La caldera de ese diseño quema sobre todo pulpa de hoja (198 t), no coronas (5,7 t). Se retira «fruta comprada en parte por sus coronas».
- El óptimo económico emite más que el sitio sin planta con cualquier factor: de +121 a +558 t con el inventario de ACV.

**Certificación.**
- El óptimo central queda certificado dentro del 3,7 % (antes se reportaba 16,9 %). La razón es que la oferta solo actúa como tope, así que los escenarios de oferta están anidados.
- Un punto del frente H3 estaba dominado: con ε = −645 t pasa de 1 077 a 1 849 MM COP/año y de −873 a −965 t.
- Re-resuelto, el wait-and-see cumple WS ≥ RP, y VSS y EVPI quedan acotados entre 0 y 91 MM COP/año.

### 0.2 Desviaciones deliberadas del encargo

1. **Capital.** No se rotula 12 640 MM COP como «~5 021».
   - El modelo da 4 026 MM COP de compra de equipos de catálogo, que por el factor de Lang equivalente 3,14 dan los 12 640 de capital fijo.
   - La carga anual de capital es de 3 314 MM COP/año.
   - La compra detallada del TEA es de 5 225 MM COP, porque incluye 930 MM COP de tanques de vinagre y de guarda que el catálogo del MILP no dimensiona.
   - El «~5 021» del comité es una reconstrucción cercana a esos 5 225, no un número del modelo.
2. **Mapa H4.** Usa el VPN del TEA de cada diseño (24 puntos con fruta). La secante del informe (184 ↔ −5 409; 3 196 ↔ +5 397) se usa para dos cosas:
   - para las plantas sin fruta, con su banda de error;
   - como verificación cruzada.
3. **Reparto de la neutralidad.** El desglose no reparte la neutralidad en «GLP/compost» frente a «crédito de fruta», como pedía el encargo.
   - El compostaje *sube* (+54 t) en el diseño neutro.
   - El reparto correcto tiene cuatro partes: la reducción técnica (quemar pulpa de hoja en lugar de devolverla y desplazar el GLP: −183 t), el paquete de la fruta comprada (−193 t, casi todo crédito de línea base), el menor acopio de hojas (+32 t) y otros (+16 t).
4. **Tarifas fiscales.** No se pudieron verificar los 750 COP/grado ni los ad valorem de 30–35 %, porque el texto del decreto y del proyecto no fueron accesibles desde esta sesión. Sí se confirmaron por fuentes públicas:
   - el Auto 082 del 29-ene-2026 (exp. RE-387), que suspendió el Decreto Legislativo 1474/2025;
   - la Sentencia C-079 de 2026, que lo declaró inexequible y ordenó devolver lo recaudado;
   - el Oficio DIAN 4031 de 2026, que confirma el IVA del 5 %;
   - el proyecto de «ley de rescate» de 2026, que llevaría el IVA del vino al 19 %.

   Las tarifas se usan como escenario «según el informe del comité», marcado [verify].

### 0.3 Lo que no se re-ejecutó con el valor corregido

Estas partes se calcularon con 21,8 kg/t, el extremo superior del rango corregido, y así se declaran en el texto:
- el barrido de autonomía H2;
- el frente ε de H3, salvo sus dos extremos, que sí se recalcularon;
- la escalera de reducción de margen del wait-and-see a 21,8 (el anidamiento sí se recalculó con 20,7);
- el análisis multiescala de §5.11;
- los barridos de precios de §5.4.

Su efecto, medido en el óptimo, es una caída del margen de 32 MM COP/año (1,0 %) sin cambio de diseño.

**Paginación.** El borrador es un documento vivo sin paginación fija, así que la matriz cita secciones y tablas.

---

## 1. Matriz de respuesta (Response to Reviewers)

| # | Crítica (informe) | Acción tomada | Nuevo dato o ecuación | Dónde se corrige |
|---|---|---|---|---|
| 1 | §3.1 / P0-1: H4 calculado en margen y anunciado en VPN | Mapa H4 en VPN con el TEA de cada diseño re-optimizado (24 puntos). Secante del informe para las plantas sin fruta, con banda de error. Cada punto se clasifica con su cota dual. Frontera VPN = 0 por interpolación. Las filas con vinagre se re-optimizaron con el etanol de hoja corregido. | VPN ≈ −5 409 + 3,588 (m − 184); m* = 1 692 MM COP/año. Error de la secante frente al TEA: media 804, máximo 1 798 MM COP (±501 de margen). Frontera: ≈ 890 000 botellas sin vinagre; ≈ 1 950 m³ a 500 000; ≈ 2 600 m³ a 250 000; solo vinagre: en el umbral a 3 000 m³. | Resumen; §5.9.2 (Tablas 5.9.2a–b); §5.10 (H4); §6.5 |
| 2 | §3.2 / P0-2: par etanol–azúcar del jugo de hoja con 0,82 g/g > 0,511 | Prueba estequiométrica de todo el registro. Nueva base de cálculo (carbohidrato por diferencia, 44,9 g/kg). Valor de diseño al 90 % del máximo (20,7 kg/t); rango 11,1–20,7. Óptimo y mapa H4 re-optimizados. | Central: margen 3 196 → 3 164; panela 145,6 → 154,6 t; VPN 5 397 → 5 273. Extremos: margen 2 965 / 2 897; panela +66 / +85 t (el comité estimó +64 a +83); VPN 4 491 / 4 225. Mismo diseño. | §2.2.5 y Ap. B; §3.11 (prueba nueva); §5.1.1–5.1.2; §5.6.1; §6.5; §6.6 |
| 3 | §3.3 / P0-3: régimen fiscal 2025–2026 no escenificado | Nueva §4.1.6 con la cronología verificada. Cinco regímenes evaluados por botella y con MILP + TEA: reoptimizado y con el diseño central fijo. | Neto por botella a 16 000 COP: 4 667 (vigente); 1 306 (específico ×3); 583 (D. 1474, IVA 5 %); −332 (D. 1474, IVA 19 %); −537 (proyecto 2026). Desde el específico ×3, el óptimo es una planta solo de vinagre de 1 868 MM COP/año (certificada para los tres regímenes del decreto y del proyecto; VPN ≈ +632 ± 1 798). Con el diseño central fijo: 1 567 y VPN −993 (específico ×3); 1 408 sin fruta (regímenes del decreto y del proyecto). | §4.1.6 (nueva); §5.6.1 (Tabla 5.6.1b); §6.5; §6.4.2 |
| 4 | §3.4 / P1-9: línea base con un solo factor; neutralidad con crédito de fruta | Sensibilidad 190 ± 100 kg CO₂e/t para el óptimo (inventario ACV) y para el diseño neutro (GWP lineal del MILP). Desglose término a término de la mejora de 328 t. Línea base de quema con la misma jerarquía en el resumen. | Óptimo: +558 / +339 / +121 t (descomposición); +853 / +1 009 / +1 166 t (quema). Diseño neutro: +357 / 0 / −357 t. Mejora de 328 t = −183 técnica + −193 fruta (de ella, −221 de crédito) + 32 hojas + 16 otros. Sin el crédito de la fruta: +221 t. | §5.6.4 (Tabla 5.6.4b); §5.9.4 (Tablas 5.9.4b–c); §5.10 (H3); §6.5 |
| 5 | §3.5 / P1-7: brechas no propagadas; WS < RP; cota de M1 importada | Intervalos [solución, cota dual] para H2, H3 y H4. Certificación del óptimo por anidamiento de escenarios. WS re-resuelto. Punto dominado del frente H3 corregido. Cota de M1 sustituida por la medida a 375 m³/año (§5.11.3). | Óptimo: [3 164; 3 280] (≤ 3,7 %). A 21,8: WS = 3 195,6 ≥ RP = 3 195,5. VSS y EVPI ∈ [0; 91] MM COP/año a 20,7. H2: un recorte del 60 % cuesta 2 453 (solución) y ≥ 1 049 (certificado). H3 (ε = −645 t): 1 077 → 1 849. | §3.10.2; §3.11; §5.6.3; §5.9.3; §5.9.4; §5.10 |
| 6 | P0-4: inconsistencias de edición | Unificadas, con su causa. Tabla canónica añadida. | Capital: 4 026 compra MILP; 12 640 capital fijo MILP; 3 314 carga anual; 5 225 compra TEA; 16 405 capital fijo TEA. Caso de 1 500 m³: 926 (no 817), cota 2 589. «a 60 % cut costs 2,453». Etiqueta de base para cada GWP neto. 27 libros. 375 m³ producidos y 95 % vendido. Celdas del mapa (7 086; 2 317; 4 942) usadas también en §3.10.2 y §5.4.3. Denominador del 33 % explicado. | §2.15 de esta respuesta |
| 7 | P0-5: referencias [verify]/[complete] | Fuentes fiscales verificadas añadidas. Liao et al. 2022 añadida como fuente del balance del jugo de hoja. Lista explícita de las 26 entradas y 7 citas en el texto aún marcadas. | §2.16 de esta respuesta | Referencias |

---

## 2. Texto reescrito (en inglés, listo para la tesis)

*Convention for all rewritten text: figures are at the corrected leaf-juice ethanol yield of 20.7 kg/t unless labelled «(at 21.8 kg/t)». Values at 21.8 kg/t are the upper end of the corrected range.*

### 2.1 Abstract (third paragraph replaced)

> With bottled wine taxed under Law 1816 of 2016 and market caps of 500,000 bottles and 3,000 m³ of vinegar per year, the optimal plant processes 1,276 t/year of fruit (20.8 % of the supply) and 3,746 t/year of leaves. It sells wine, vinegar fermented from peel and leaf juices with panela, and fibre flour, for an annual margin of 3,164 MM COP and a net present value of 5,273 MM COP (MIRR 13.4 %, P(NPV > 0) = 0.78). The margin is certified within 3.7 % of the optimum. Designing the same superstructure fraction by fraction gives an NPV of only 27 MM COP.
>
> Viability is judged by NPV, not by margin, and it depends on markets. The plant needs about 890,000 bottles a year without vinegar, or about 1,950 m³ of vinegar with 500,000 bottles and about 2,600 m³ with 250,000 bottles. A plant making 3,000 m³ of vinegar and no wine sits at the viability threshold.
>
> Two risks bound this frontier:
> - The emergency decree of December 2025, before the Constitutional Court struck it down, would have roughly tripled the specific component of the wine excise and raised its ad valorem rate. Under such rates wine stops paying, and the optimum becomes that threshold vinegar plant.
> - The ethanol yield of leaf juice rests on one source and is set at 90 % of its stoichiometric maximum. At the lower end of its range the margin falls by about 8 % with the same design, and the vinegar-only plant is no longer viable.
>
> Against a site where fruit and leaves decompose, the optimum emits 121–558 t CO₂e/year more over the plausible range of the decomposition factor, and 853–1,166 t more if the leaves would otherwise be burned. A design burning leaf pulp in a biomass boiler reaches net zero for 83 MM COP/year, but only at the central factor and with credit for the 1,162 t of extra fruit it buys. Linking the plant model to yeast kinetics, the fermentation train, an hourly weekly schedule and leaf collection shows that the value of integration lies inside the plant scale. The sugar hub, gasification, bromelain and ethanol are not selected. For Bajo Atrato, validating the vinegar market, measuring the leaf-juice fermentation and securing the fiscal treatment of fruit wine, not developing technology, are now the conditions of the project.

### 2.2 Section 5.1.1 — capital paragraph (replaces the last two sentences)

> There is no crown boiler, no bromelain module, no leaf ethanol, no digester and no hub product; crown and core are composted.
>
> The catalogue options chosen cost 4,026 MM COP to purchase. With the equivalent Lang factor of 3.14, the MILP estimates their fixed capital at 12,640 MM COP. The annualized capital charge it subtracts is 3,314 MM COP/year: 3,068 for the annuity, maintenance and local taxes on purchased equipment (AF = 0.762), plus 246 of fixed costs tied to the chosen options.
>
> The itemized TEA lists 5,225 MM COP of purchased equipment. It includes 930 MM COP of storage tanks, for 30 days of vinegar and 90 days of wine ageing, that the MILP catalogue does not size. The TEA arrives at a fixed-capital investment of 16,405 MM COP: 10,936 direct, 3,281 engineering, procurement and construction, and 2,187 contingency. The omission of these tanks from the MILP is discussed in Section 6.6.
>
> The margin of this design is 3,164 MM COP/year at the corrected leaf-juice yield (3,196 at 21.8 kg/t; Section 5.1.2). It is certified within 3.7 % of the optimum: because supply enters the MILP only as an upper limit, the optimum with 1.3 times the supply bounds the central one, and the dual bound of that run is 3,280 MM COP/year.

### 2.3 Section 5.1.2 — «Vinegar carries the plant» (replaced)

> **Vinegar carries the plant.** Without the vinegar routes the optimum earns 184 MM COP/year; with them, 3,164. Its substrate is mostly leaf juice with panela: 2,847 t of leaf juice against 221 t of peel juice, and no wine diverted.
>
> The acid potential of leaf juice rests on one source, and that source does not close. In Chen et al. (2020), as balanced by Liao et al. (2022), 46 kg of juice give 35 kg of broth at 3.6 % v/v ethanol and 11 kg of wet yeast. That is 1.0 kg of ethanol, or 21.7 kg per tonne of juice.
>
> Three checks bear on that figure:
> - **Free sugars.** The juice has at most 27 g/L of free sugars, which cannot produce that much ethanol (0.82 g/g).
> - **Total carbohydrate.** On the 44.9 g/kg of carbohydrate the juice holds by difference, the yield is 0.485 g/g, 95 % of the stoichiometric maximum.
> - **Mass balance.** With the 16.1 kg of yeast dry matter per tonne reported by the same source, ethanol, CO₂ and yeast add up to 58.8 kg per tonne, against 55.8 kg of organic solids in the juice. At least one output is therefore overstated.
>
> The design value is set at 90 % of the stoichiometric maximum on carbohydrate, 20.7 kg/t. Its range runs down to 11.1 kg/t, the yield if only the free sugars fermented at the 0.42 g/g used for panela (Table 5.1.2a).
>
> The design is the same at every value of the range: the same equipment and the same 3,000 m³ of vinegar. Panela makes up the acid the leaf juice no longer supplies. The margin falls from 3,164 to 2,897 MM COP/year and the NPV from 5,273 to 4,225 MM COP, an 8 % and a 20 % loss at the lower end. These designs are the best found within the time limit, not proven optima.
>
> The leaf-juice yield changes the cost of vinegar, not whether vinegar is made. A vinegar-only plant has no wine to absorb that cost, so there the leaf-juice yield decides viability (Section 5.6.1). A fermentation of Chocó leaf juice with the plant's own strain is the measurement that would close this range (Section 6.7).

*Table 5.1.2a. Optimum against the leaf-juice ethanol yield (500,000 bottles; 3,000 m³ of vinegar).*

| Leaf-juice ethanol (kg/t juice) | Basis | Acid potential (kg/t juice) | Margin (MM COP/year) | Dual bound | Panela (t/year) | NPV (MM COP) |
|---|---|---|---|---|---|---|
| 21.8 (former value) | source mass balance; 95 % of maximum on carbohydrate | 26.7 | 3,196 | 3,500 | 145.6 | 5,397 |
| **20.7 (design value)** | **90 % of maximum on 44.9 g/kg carbohydrate** | **25.3** | **3,164** | **3,280** | **154.6** | **5,273** |
| 13.5 | maximum (0.511 g/g) on free sugars only | 16.6 | 2,965 | 3,439 | 211.6 | 4,491 |
| 11.1 | 0.42 g/g on free sugars only | 13.6 | 2,897 | 4,424 | 230.8 | 4,225 |

### 2.4 Section 5.6.1 — Techno-economic assessment (rewritten text after the case table)

*(The case table of §5.6.1 replaces its first row by «Optimum (configuration A): FCI 16,405; NPV 5,273; MIRR 13.4 %; payback 5.0 years; P(NPV > 0) 0.78; medium». The other rows were computed at 21.8 kg/t and are labelled so.)*

> The TEA confirms the ranking of the MILP. From the TRL-9 reference to the optimum the NPV rises from −12,454 to 5,273 MM COP and the MIRR from −22.8 % to 13.4 %; P(NPV > 0) rises from 0 to 78 %. Without vinegar the optimum loses money (NPV −5,409 MM COP, P(NPV > 0) = 0.02).
>
> **Margin is not viability.** The annual margin of the MILP is computed after the annualized capital charge. It comes before payroll, supervision and the other fixed costs, income tax and the phased start-up, all of which the TEA includes. Over the designs of the demand map, NPV and margin follow
>
> NPV ≈ −5,409 + 3.588 (m − 184) MM COP. (5.6.1)
>
> The relation passes through the design without vinegar and the optimum at 21.8 kg/t. It reproduces the TEA of the 22 other designs of the map with a mean deviation of 804 MM COP and a maximum of 1,798 MM COP, the equivalent of ±501 MM COP/year of margin. It places the break-even margin at 1,692 MM COP/year. Every viability statement in this thesis uses the TEA, or Equation 5.6.1 with that error band where the itemized TEA does not apply (designs that process no fruit).
>
> **Cost structure of the optimum.**
> - Revenue is 12,089 MM COP/year: 5,362 from wine at the factory price and 6,727 from vinegar and flour.
> - Variable costs are 5,097 MM COP/year. Raw materials account for 4,497 of them: the excise on the 475,000 bottles sold (95 % of the 500,000 produced, the sales convention of Table 4.1) is about 2,000, packaging about 1,140, fruit 511, panela 541 and leaf collection 133; composting and chemicals make up the rest. Utilities cost 580 and waste treatment 21.
> - Fixed costs are 2,227 MM COP/year. Working capital is 610 MM COP.
> - Operating cost totals 7,324 MM COP/year. The payback is 5.0 years (6.6 discounted).
> - The break-even vinegar price is 1,723 COP/L, 22 % below the assumed 2,200.
> - Over 1,000 correlated Monte Carlo samples the NPV has a median of 3,543 MM COP, a 5th–95th percentile range of −4,127 to 11,526, and a CVaR at 5 % of −6,347.
>
> The excise is the largest single cost of the plant, and its rate is not stable (Section 4.1.6).
>
> **Fiscal sensitivity** (Table 5.6.1b). Under the current regime a bottle sold at 16,000 COP leaves 4,667 COP after excise, VAT, distribution and packaging. The other regimes leave much less:
> - tripling the specific component: 1,306 COP;
> - the rates of Decree 1474 of 2025: 583 COP with 5 % VAT and −332 COP with 19 % VAT;
> - the 2026 fiscal bill: −537 COP.
>
> Re-solving the MILP gives the same answer for all four. From the tripled specific component upwards, the plant stops making wine and becomes a vinegar plant fed by leaf juice and panela, earning 1,868 MM COP/year. That design is certified optimal under the decree and bill regimes (its dual bound equals its margin) and is the best design found when only the specific component is tripled (dual bound 3,312). Its NPV, by Equation 5.6.1, is about +632 MM COP. That is within the error of the relation, so the vinegar plant sits at the viability threshold.
>
> It falls below the threshold if the leaf-juice yield is lower: its margin is 1,654 MM COP/year at 13.5 kg/t and 1,581 at 11.1 kg/t, for estimated NPVs of about −137 and −396 MM COP.
>
> The design optimized for the current regime does worse if it is kept:
> - with the specific component tripled it earns 1,567 MM COP/year, and its NPV is −993 MM COP;
> - under the decree and bill rates it stops buying fruit and earns 1,408 MM COP/year, below the break-even margin.
>
> The wine line is therefore the part of the project exposed to fiscal risk. Under high excise rates, the project survives only as a vinegar plant whose viability rests on the leaf-juice yield.
>
> **Company size and income tax.** By its revenue in UVT the optimum is a medium-sized company, so with start-up in 2030 it pays the general rate of 35 % in every year. The following figures were computed at 21.8 kg/t:
> - Under the proposed ZOMAC extension (Bill 435 of 2025), the optimum's NPV rises by 1,632 MM COP.
> - The no-cap designs would gain 6,457 (wine) and 10,448 (vinegar).
>
> The ZOMAC location does not exempt the wine from the departmental excise.

### 2.5 Section 5.6.3 — Stochastic design (rewritten)

> The two-stage program varies supply only, at 0.7, 1.0 and 1.3 times the central value with probabilities 0.25, 0.5 and 0.25. At 21.8 kg/t the version 12 run reported RP = 3,196 and WS = 3,195 MM COP/year, which violates EEV ≤ RP ≤ WS. By the protocol of Section 3.11 that is an error, not a result. The wait-and-see problem of the central scenario had stopped at its time limit (3,193.7), below a design already known, and the mean-value problem EV, which is the same scenario, had stopped at the same value.
>
> Re-solving each scenario from that design gives WS = 3,195.6 ≥ RP = 3,195.5 MM COP/year (at 21.8 kg/t), and the same design in every scenario.
>
> **Bounds.** Supply enters the MILP only as an upper limit: unprocessed fruit has no cost. The feasible sets are therefore nested, and the optimum with more supply bounds the optimum with less. At the corrected leaf-juice yield the runs give:
>
> | Supply scenario | Solution | Dual bound |
> |---|---|---|
> | 0.7 | 3,164.1 | 3,178.1 |
> | 1.0 | 3,164.0 | ≤ bound of 1.3 |
> | 1.3 | 3,164.1 | 3,280.0 |
>
> Hence 3,164.0 ≤ RP ≤ WS ≤ 0.25 × 3,178.1 + 0.75 × 3,280.0 = 3,254.5, and both EVPI and VSS lie between 0 and 91 MM COP/year, under 2.9 % of the margin. The same nesting certifies the central optimum within 3.7 %.
>
> The stochastic design is the deterministic one. This was expected: with both markets capped, supply is not an active constraint, and even the low scenario offers more fruit than the wine market absorbs. The two-stage program answers only the supply question, and the answer is that supply does not matter at this scale.
>
> Market and fiscal uncertainty, which do matter, are not represented in this program. They are treated by the demand map (Section 5.9.2), the price tornado and the Monte Carlo (Section 5.6.2) and the fiscal regimes (Table 5.6.1b). A two-stage program with demand and excise as uncertain parameters is future work (Section 6.7).

### 2.6 Section 5.6.4 — Life-cycle assessment (rewritten)

*(Contribution table: Panela becomes 93 t; process total becomes 1,293 t; the other rows are unchanged.)*

> Process GWP is 1,293 t CO₂e/year, or 1,013 kg per tonne of fruit processed. The largest item is the leaf pulp the extractor returns to the field: 674 t/year that carry about two thirds of the leaves' dry matter and still decompose there. Earlier versions credited the plant for all the leaves it collects but did not count this return. The correction (Section 4.2) raises process GWP and changes the sign of the net result. Diesel electricity and glass bottles follow. Effluent treatment removes 97 % of 7.9 t of COD for 11 t CO₂e.
>
> **The net result and its two assumptions.** The net GWP subtracts what the site would emit without a plant, and it rests on two assumptions:
> - **The decomposition factor.** One IPCC factor, 4 g CH₄ and 0.3 g N₂O per kg of wet material (190 kg CO₂e/t), values the fruit and leaves in the baseline, the fractions composted in the plant and the leaf pulp returned to the field.
> - **What would happen to the leaves without a plant.** They would either decompose or be burned.
>
> Table 5.6.4b varies both:
> - From 90 to 290 kg CO₂e/t, the optimum adds between 121 and 558 t CO₂e/year against a decomposing baseline, and between 853 and 1,166 t against a burning baseline.
> - Raising the factor lowers the net result, because the factor multiplies 954 t CO₂e of baseline emissions but only 539 t CO₂e of process emissions.
> - The sign is robust: under every combination tested, the economic optimum emits more than the site without a plant.
>
> Burning leaves emits little GWP but much particulate matter, and the plant then avoids 4.8 t/year of particulates.
>
> The net figure of this section uses the life-cycle inventory: 1,293 t of process emissions and +339 t net. The MILP carries a linear GWP of 1,282 t (+328 t) that omits effluent treatment (11 t). Each figure in this thesis names its basis.
>
> The baseline also assumes that the fruit the plant buys would otherwise be discarded. This thesis takes the 2022 production of Chocó as the supply available to the plant. The only measured reject stream, however, is 144 t/year in one municipality (Murcia Palacios, 2013), and Section 2.1.3 gives a scenario of 1,536 t at 25 % shrinkage. At 1,276 t/year the optimum stays within that scenario. Fruit diverted from the fresh market would carry no baseline credit; Section 5.9.4 shows why this matters for the low-GWP designs.
>
> System-expansion credits are zero for the optimum, which makes neither ethanol nor surplus power. By economic allocation, a bottle of wine carries 1.15 kg CO₂e (44 % of the burden), a litre of vinegar 0.22 kg (52 %) and a kilogram of flour 1.22 kg (4 %).

*Table 5.6.4b. Net GWP of the economic optimum against the decomposition factor and the leaf counterfactual (t CO₂e/year; life-cycle inventory). «t» are tonnes of CO₂-equivalent.*

| Decomposition factor (kg CO₂e/t wet) | 90 | 190 (central) | 290 |
|---|---|---|---|
| Process GWP | 1,009 | 1,293 | 1,577 |
| Baseline: fruit and leaves decompose | 452 | 954 | 1,456 |
| **Net GWP, decomposing baseline** | **+558** | **+339** | **+121** |
| Baseline: fruit decomposes, leaves burned | 156 | 284 | 412 |
| **Net GWP, burning baseline** | **+853** | **+1,009** | **+1,166** |

### 2.7 Section 5.9.2 — Minimum viable demand (H4), rewritten

> Section 3.12.4 defines the H4 frontier as the line NPV = 0. The design was re-optimized over 30 combinations of market size, and the dual bound of each free run was recorded. The rows with 1,500 m³ of vinegar or more were re-optimized at the corrected leaf-juice yield. The rows with 0 and 750 m³ use no leaf juice and are unchanged. The TEA was run on every design that processes fruit (24 points); Table 5.9.2a gives the NPV.
>
> The designs at 100,000 bottles process no fruit. Two of them build nothing (the margin of −1,090 is the fixed cost of the minimum front end, so the real alternative is not to build, with NPV 0). The other four are vinegar plants fed by leaves and panela, to which the itemized TEA does not apply. Their NPV is estimated by Equation 5.6.1, with its error of ±1,798 MM COP. The estimates at 6,000 and 12,000 m³ extrapolate beyond the optimum used to fit the relation.
>
> **The frontier.** Interpolating the NPV between grid points:
> - **Without vinegar,** the plant is viable from about 890,000 bottles a year (NPV −5,409 at 500,000; +1,500 at 1,000,000).
> - **With 500,000 bottles** it needs about 1,950 m³ of vinegar (NPV −2,239 at 1,500 m³; +5,273 at 3,000 m³).
> - **With 250,000 bottles** it needs about 2,600 m³ (NPV −5,837 at 1,500 m³; +1,995 at 3,000 m³).
> - **A vinegar-only plant** at 3,000 m³ earns 1,868 MM COP/year, certified to within 0.2 % by its dual bound of 1,872. Its estimated NPV, +632 MM COP, is within the error of the estimate: the plant sits at the threshold.
> - **At 1,000,000 bottles and above** every vinegar level is viable.
>
> The earlier reading of this map, «viable from about 500,000 bottles», took a positive margin for viability. It is withdrawn: that design has an NPV of −5,409 MM COP.
>
> **Certification.** The margins are the best solutions found. A point is certified not viable when its dual bound lies below the break-even margin minus the error band (1,692 − 501 = 1,191 MM COP/year), because then no design there can be viable. The status of each point that decides the frontier is in Table 5.9.2b:
> - **Certified not viable:**
>   - 250,000 bottles without vinegar (dual bound −682);
>   - 500,000 bottles without vinegar (dual bound 280);
>   - 250,000 bottles with 1,500 m³ (dual bound 1,025).
> - **Not certified:** 500,000 bottles with 1,500 m³. Its solution has NPV −2,239, but its dual bound (1,520) does not rule out a viable design, so the frontier at 500,000 bottles lies between 1,500 and about 1,950 m³ of vinegar. The 750 m³ points have no recorded bound.
>
> **Two points improved.** The re-optimization at the lower leaf-juice yield found better designs than the earlier map at two points:
> - 500,000 bottles with 1,500 m³: 1,150 against 926 MM COP/year;
> - 250,000 bottles with 1,500 m³: 272 against −7.
>
> The earlier map's solutions at those points were therefore not optimal, which the weak bounds of its free runs had allowed.
>
> **What H4 now says.** Viability depends on the demand for both products far more than on technology or supply. The frontier is more demanding than first reported. Below about 890,000 bottles the plant cannot rest on wine, and the vinegar cap of 3,000 m³ sits about 50 % above the vinegar it needs at 500,000 bottles. Vinegar demand is the market study that decides the project, and the wine market decides how much margin it has (Section 6.4).

*Table 5.9.2a. NPV of the re-optimized design for each pair of market sizes (MM COP; leaf-juice ethanol 20.7 kg/t). Values marked * are estimates for plants that process no fruit, by Equation 5.6.1 (±1,798); «not built» means that the best design builds nothing.*

| Vinegar (m³/year) \ bottles/year | 100,000 | 250,000 | 500,000 | 1,000,000 | 2,000,000 |
|---|---|---|---|---|---|
| 0 | not built | −10,240 | −5,409 | 1,500 | 3,899 |
| 750 | not built | −10,240 | −5,409 | 1,500 | 8,577 |
| 1,500 | −6,594* (margin −146) | −5,837 | −2,239 | 3,224 | 13,318 |
| 3,000 | 632* | 1,995 | 5,273 | 11,440 | 22,312 |
| 6,000 | 14,429* | 16,301 | 19,614 | 25,860 | 36,650 |
| 12,000 | 40,830* | 43,474 | 46,746 | 52,764 | 55,967 |

*Table 5.9.2b. Margin of the design found, dual bound of its free run (MM COP/year) and status, for the points that decide the frontier. Break-even margin 1,692; certified not viable below 1,191.*

| Point (bottles; vinegar m³) | Margin found | Dual bound | NPV | Status |
|---|---|---|---|---|
| 250,000; 0 | −683 | −682 | −10,240 | certified not viable |
| 500,000; 0 | 184 | 280 | −5,409 | certified not viable |
| 1,000,000; 0 | 1,911 | 2,255 | 1,500 | viable |
| 250,000; 1,500 | 272 | 1,025 | −5,837 | certified not viable |
| 500,000; 1,500 | 1,150 | 1,520 | −2,239 | not viable as found; not certified |
| 100,000; 3,000 (vinegar only) | 1,868 | 1,872 | 632* | at the threshold |
| 250,000; 3,000 | 2,286 | 2,647 | 1,995 | viable |
| 500,000; 3,000 (central) | 3,164 | 3,280 | 5,273 | viable |

### 2.8 Section 5.9.3 — H2 table with intervals (replaces the table; at 21.8 kg/t)

> Lowering the cap on fossil energy (3,818 GJ/year in the optimum) gives the solutions below, with the dual bounds of their free runs. This sweep was computed at 21.8 kg/t, where the unconstrained optimum is 3,196 MM COP/year with a dual bound of 3,789 when the heat pump is available.
>
> Because a tighter cap removes designs, the true cost of a cut cannot fall as the cut deepens. The certified minimum cost of a cut is therefore the largest value of (3,196 − dual bound of the capped run) among that cut and the shallower ones.
>
> The bounds are weak. The certified costs are lower limits, and the costs at the solutions found are the ones this thesis reports.

| Fossil cap (% of optimum) | Margin found | Dual bound | Cost at the solutions found | Certified cost range |
|---|---|---|---|---|
| 100 | 3,196 | 3,789 | — | — |
| 80 (a 20 % cut) | 3,039 | 4,957 | 157 | 0 to 750 |
| 60 (a 40 % cut) | 1,673 | 2,488 | 1,523 | 708 to 2,116 |
| 40 (a 60 % cut) | 742 | 2,147 | 2,453 | 1,049 to 3,047 |
| 20 (an 80 % cut) | 30 | 2,660 | 3,166 | 1,049 to 3,759 |
| 0 (full autonomy) | −1,642 | none (no finite bound) | 4,838 | 1,049 to 5,431 |

*Upper ends: dual bound of the unconstrained run minus the margin found.*

> The first 20 % is cheap, 157 MM COP/year at the solutions found and at most 750 certified, and it is where the heat pump enters. A 60 % cut costs 2,453 MM COP/year at the solutions found and at least 1,049 with certainty. It cuts vinegar, because aeration of the acetifier is the largest electricity use and only diesel supplies it. Full autonomy means not operating.
>
> H2 is supported in the form tested here, the ε-constraint sweep. The flexibility index named in the original wording of H2 is formulated (Section 3.6.3) but not run, and the verdict does not rest on it.

### 2.9 Section 5.9.4 — H3: front with intervals and the anatomy of neutrality (rewritten)

> The ε-constraint front was computed at 21.8 kg/t. Each point was re-solved with a longer free run, and its dual bound was recorded. At ε = −645 t the longer run found a design that earns 1,849 MM COP/year and emits −965 t net. The point published earlier (1,077 MM COP/year; −873 t) was dominated, and Table 5.9.4a replaces it.
>
> The front is non-degenerate: the margin falls monotonically as the cap tightens. It is the best front found, not a certified one. Its dual bounds lie well above the solutions, and the points that do not operate profitably have no finite bound.

*Table 5.9.4a. Margin–net GWP front (linear GWP of the MILP; at 21.8 kg/t unless stated).*

| Design | Margin found (MM COP/year) | Dual bound | Net GWP (t CO₂e/year) | NPV (MM COP) | What changes from the optimum |
|---|---|---|---|---|---|
| Economic optimum (at 20.7 kg/t) | 3,164 | 3,280 | +328 | 5,273 | — |
| Net-zero design (at 20.7 kg/t) | 3,081 | 4,597 | 0 | 4,873 | biomass boiler burning 198 t of leaf pulp; 2,439 t of fruit; 341 m³ of wine to vinegar |
| ε = −161 t | 2,525 | 3,548 | −288 | 2,407 | no leaves; 3 t/h front end, centrifuge, 100 kWt boiler |
| Compromise w = 0.50 | 2,330 | — | −502 | 1,495 | 5,555 t of fruit, 1,951 t of leaves, 100 kWt boiler |
| ε = −645 t (corrected) | 1,849 | 4,529 | −965 | −1,776 | 30,468 t of leaves, 10 t/h extractor, leaf ethanol, 300 kWt boiler |
| ε = −1,129 t | 125 | 4,485 | −1,129 | — | as above, operated for GWP |
| ε = −1,612 t and −2,096 t | −3,517 and −3,806 | none | −1,612 and −2,096 | — | all fruit and up to all leaves, digester and 200 kWe engine |
| Minimum net GWP | −4,084 | — | −2,580 | −31,880 | all 6,146 t of fruit and 32,469 t of leaves |

> **What makes a design neutral.** At the corrected leaf-juice yield, the compromise found earlier (w = 0.75) is no longer neutral: with its sizes fixed it earns 3,089 MM COP/year and emits +40 t. Imposing net GWP ≤ 0 on the same equipment gives the net-zero design of Table 5.9.4a: 3,081 MM COP/year, 83 less than the optimum, with an NPV of 4,873 MM COP.
>
> Its boiler, the option called «crown boiler» in the catalogue, burns 198 t of leaf pulp and only 5.7 t of crown. The earlier statement that this design buys fruit «partly for its crowns» is withdrawn.
>
> Table 5.9.4b decomposes the 328 t that separate it from the optimum into four groups:
> - **Technical reduction, −183 t.** Burning 198 t of leaf pulp instead of returning it to the field (−141 t) and displacing all LPG heat (−57 t), against +15 t of combustion emissions.
> - **Fruit purchase, −193 t.** Buying 1,162 t more fruit earns 221 t of baseline credit. Composting its cores and crowns adds +54 t and transporting it +5 t. Diverting 341 m³ of wine to vinegar saves 31 t of panela.
> - **Leaf boundary, +32 t.** Collecting 713 t fewer leaves avoids 91 t of field return and 13 t of collection diesel but loses 135 t of baseline credit.
> - **Other, +16 t.** Electricity and chemicals.
>
> Two consequences follow:
> - **Without the fruit credit** (if the extra fruit came from the fresh market rather than from reject) the design would emit +221 t. At 2,439 t/year it buys more fruit than the 1,536 t of the 25 %-shrinkage scenario of Section 2.1.3, so part of that credit is not supported by the supply data.
> - **Its neutrality holds only for decomposition factors at or above the central 190 kg CO₂e/t.** Its net GWP is +357 t at 90 and −357 t at 290 (Table 5.9.4c).
>
> The economic optimum emits more than the no-plant site under every combination tested. The net-zero design remains the one this thesis recommends if the environmental objective is weighted at all: 183 t of its 328 t improvement come from a real change of technology, and it costs only 83 MM COP/year. Its claim to be net-zero, however, must state both conditions.

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
| *By group:* technical −182.7; fruit −193.2; leaf boundary +31.6; other +15.9 | | | | |

*Table 5.9.4c. Net GWP against the decomposition factor (t CO₂e/year; linear GWP of the MILP; at 20.7 kg/t; decomposing baseline).*

| Decomposition factor (kg CO₂e/t wet) | 90 | 190 | 290 |
|---|---|---|---|
| Economic optimum | +547 | +328 | +110 |
| Net-zero design | +357 | 0 | −357 |

### 2.10 Section 5.10 — Testing hypotheses H1–H4 (table rewritten)

| Hypothesis | Verdict | Evidence |
|---|---|---|
| H1. Simultaneous synthesis, sizing and operation beat sequential design by fractions | Supported, with one qualification | The same superstructure designed by fractions in sequence earns 1,816 against 3,164 MM COP/year, 42.6 % less (NPV 27 against 5,273) (Section 5.9.1). The sequential protocol has no feedback between stages, so the gap measures sequential design without iteration. Seasonal coupling adds nothing at the capped scale and 4.4–12.2 % when capacity binds (at 21.8 kg/t). At train level, the hierarchical chain costs 3.8–12.5 % more at the flow of the optimum (7.1–9.0 % at the original basis; Section 5.11). |
| H2. Energy autonomy has a measurable cost in margin and portfolio | Supported (ε-constraint sweep) | A 20 % cut in fossil energy costs 157 MM COP/year at the solutions found (0–750 certified; heat pump). A 60 % cut costs 2,453 (1,049–3,047 certified) and cuts vinegar. Full autonomy means not operating (Section 5.9.3, at 21.8 kg/t). The flexibility index of the original wording is formulated but not run, and the verdict does not rest on it. |
| H3. The margin–GWP front is non-dominated and non-degenerate, with GWP against a no-plant baseline | Partly supported | A non-degenerate front exists. It is the best found, not certified: its dual bounds lie far above the solutions, and one published point was dominated and has been replaced (Table 5.9.4a). The economic optimum emits more than the no-plant site for every decomposition factor from 90 to 290 kg/t (inventory basis +121 to +558 t; MILP basis +110 to +547 t). The net-zero design costs 83 MM COP/year and holds only for factors at or above 190 kg/t and with credit for 1,162 t of extra fruit (Section 5.9.4). |
| H4. With the current supply, viability depends more on the demand and price of the main products than on technology | Supported, with a corrected frontier | Over 30 market pairs the NPV ranges from −10,240 to +55,967 MM COP. The frontier NPV = 0 lies at about 890,000 bottles without vinegar, or about 1,950 m³ of vinegar with 500,000 bottles and about 2,600 m³ with 250,000; a vinegar-only plant of 3,000 m³ sits at the threshold. The designs without vinegar at 250,000 and 500,000 bottles are certified not viable (Section 5.9.2). At three times the current specific excise the optimum is that vinegar-only plant (Section 5.6.1). Supply from 0.5 to 3.6 times the central value leaves the capped optimum unchanged (at 21.8 kg/t; EVPI and VSS between 0 and 91 MM COP/year at 20.7 kg/t). |

> H1 needs two qualifications. First, at the scale of Chocó its gain comes from synthesis across fractions, not from coupling design with seasonal operation, which matters only when capacity binds. Second, it says nothing about sharing equipment between products: the multiplant–multiproduct comparison (Section 2.8.6) shows that question is close economically and decided by staffing, which in Bajo Atrato has social weight of its own.
>
> H4 is the hypothesis the thesis did not start with and the one its results support most strongly. Judged by NPV, its frontier is more demanding than first reported, and it places the vinegar market, and the leaf-juice fermentation that feeds it, at the centre of the project.

### 2.11 Section 6.5 — Conclusions against each objective

> **Objective 1** (sentence added at the end). A stoichiometric test of every sugar-to-product pair of the registry found one inconsistent pair: the ethanol yield of leaf juice had been compared with its free sugars. On the carbohydrate it holds, the source's yield is 95 % of the theoretical maximum, and the source's mass balance does not close. The design value was therefore set at 90 % of the maximum, 20.7 kg/t, with a range of 11.1–20.7 kg/t.
>
> **Objective 2: unit and train models.** The fermentation models were calibrated and verified. The single measured point of pulp juice does not identify its kinetics: a family of parameter pairs fits it equally well and changes the design fermentation time by a factor of 2.3. Moresi's winery model was replicated, with his numbers of fermenters reproduced exactly, and its kinetics were shown to be invalid at the 30 °C of the pineapple data; the premium-line advantage claimed earlier is an artefact of changing model. The glucose–xylose kinetics of the juices cut the processing time of the juice winery from 32.5 to 12.6 h. Fixing kinetics before sizing costs 7.1–9.0 % of the fermentation-train cost at the original design basis and 3.8–12.5 % at the wine flow of the optimum. The band of fermentation times left by the single point does not change the plant design (Section 5.11).
>
> **Objective 3** (sentences added at the end). The dual bounds of the free runs are now reported beside every hypothesis test. Because supply enters only as an upper limit, the central optimum is certified within 3.7 %. The bounds also certify the non-viable region of the demand map, but not the margin–GWP front, whose dual bounds remain weak.
>
> **Objective 4: assessment under uncertainty.** The optimum has an NPV of 5,273 MM COP, an MIRR of 13.4 % and P(NPV > 0) = 0.78, with a break-even vinegar price 22 % below the assumed price. Two uncertainties outside the Monte Carlo were quantified:
> - **The leaf-juice yield.** Within its corrected range it lowers the NPV to as little as 4,225 MM COP without changing the design.
> - **The wine excise.** At three times its current specific rate, or at the rates of the annulled Decree 1474 of 2025, wine stops paying. The optimum then becomes a vinegar-only plant of 1,868 MM COP/year, which sits at the viability threshold and falls below it if the leaf-juice yield is low. The current design kept unchanged would have an NPV of −993 MM COP.
>
> The plant emits 1,293 t CO₂e/year in process. Against a site where fruit and leaves decompose, it adds 121–558 t over the plausible range of the decomposition factor, and 853–1,166 t if the leaves would otherwise be burned. Burning leaf pulp in a biomass boiler makes it net-zero for 83 MM COP/year, but only at the central factor or above and with credit for the extra fruit it buys. The plant retains about 2,000 MM COP/year in the territory with about 17 jobs (at 21.8 kg/t). Supply uncertainty has no value (VSS and EVPI between 0 and 91 MM COP/year); market and fiscal uncertainty dominate.
>
> **Objective 5: the Bajo Atrato biorefinery.** The optimal plant processes 1,276 t/year of fruit and 3,746 t/year of leaves into 500,000 bottles of wine, 3,000 m³ of vinegar and 40 t of fibre flour. Its equipment is:
> - a 1 t/h front end, one shared press, flotation and SO₂;
> - two 10 m³ fermenters and a 500 bottles/h line;
> - a juice winery and a 10 m³ acetifier;
> - a 2 t/h leaf extractor and a small dryer.
>
> It is viable if vinegar sells above 1,723 COP/L and wine near 16,000 COP per bottle under the current excise. The hypotheses come out as follows:
> - H1 is supported against a sequential design of the same superstructure (NPV 27 against 5,273 MM COP).
> - H2 is supported by the autonomy sweep.
> - H3 is partly supported: the front is non-degenerate but not certified, and net-zero is conditional.
> - H4 is supported with a corrected frontier: the plant is viable from about 890,000 bottles without vinegar, or with about 1,950 m³ of vinegar at 500,000 bottles and about 2,600 m³ at 250,000.
>
> **Objective 6: rules and policy.** Markets, the excise on fruit wine and one fermentation datum, not feedstock or technology, now limit the project. The design rules for a larger wine market are known from the scale sweep: front end first, then presses, centrifugation and the crown boiler, and enzyme recovery and a third shift only from three times the supply.
>
> The vinegar line carries the project under every fiscal regime tested, but under a high excise only if the leaf-juice yield holds. The order of work is therefore:
> 1. a study of vinegar demand;
> 2. a fermentation of Chocó leaf juice with the plant's strain;
> 3. a study of the volume and price of bottled fruit wine.
>
> The policy levers are demand, a stable and differentiated excise for small regional fruit-wine producers, and renewable electricity.

> **Resumen (Spanish abstract), third paragraph replaced:** «Con el vino embotellado y su impuesto al consumo (Ley 1816 de 2016), y con topes de mercado de 500 000 botellas y 3 000 m³ de vinagre al año, el óptimo procesa 1 276 t/año de fruta y 3 746 t/año de hojas, vende vino, vinagre de jugos de cáscara y de hojas con panela y harina de fibra, y da un margen de 3 164 MM COP/año, certificado dentro del 3,7 % del óptimo, y un VPN de 5 273 MM COP (TIRM 13,4 %; P(VPN > 0) = 0,78). Diseñar la misma superestructura fracción por fracción deja un VPN de solo 27 MM COP. La viabilidad se juzga por el VPN y depende del mercado: hacen falta unas 890 000 botellas sin vinagre, o unos 1 950 m³ de vinagre con 500 000 botellas y unos 2 600 m³ con 250 000; una planta solo de vinagre de 3 000 m³ queda en el umbral. El decreto de emergencia de diciembre de 2025, antes de que la Corte lo declarara inexequible, habría aproximadamente triplicado el componente específico del impuesto al vino; con esas tarifas el vino deja de pagar y el óptimo se vuelve esa planta de vinagre en el umbral. El rendimiento en etanol del jugo de hoja se apoya en una sola fuente y se fija en el 90 % de su máximo estequiométrico; en el extremo bajo de su rango el margen cae hasta un 8 % con el mismo diseño y la planta solo de vinagre deja de ser viable. Frente a un sitio donde la fruta y las hojas se descomponen, el óptimo emite entre 121 y 558 t CO₂e/año más según el factor de descomposición, y entre 853 y 1 166 t más si las hojas se quemaran; un diseño que quema pulpa de hoja en una caldera de biomasa alcanza emisión neta nula por 83 MM COP/año, pero solo con el factor central o mayor y con el crédito de las 1 162 t de fruta adicional que compra. El valor de integrar queda dentro de la escala de planta. Ni el hub de azúcares, ni la gasificación, ni la bromelaína, ni el etanol entran. Validar el mercado del vinagre, medir la fermentación del jugo de hoja y asegurar el tratamiento fiscal del vino de fruta, no desarrollar tecnología, son ahora las condiciones del proyecto.»

### 2.12 New Section 4.1.6 — Regulatory risk of the wine excise (Chapter 4)

> **4.1.6 Regulatory risk of the wine excise**
>
> The excise rates of Section 4.1.3 are those in force in 2026:
> - a specific component of 243 COP per alcoholic degree in 750 cm³ (Certification 003 of 2025, Ministry of Finance);
> - an ad valorem component of 20 % (Law 1816 of 2016, art. 20);
> - VAT of 5 % (Tax Code, art. 468-1; DIAN, Oficio 4031 of 2026).
>
> They are in force because of a court decision. Legislative Decree 1474 of 29 December 2025, issued under a declared economic emergency, raised the taxes on liquors and wines. The Constitutional Court suspended it provisionally on 29 January 2026 (Order 082, file RE-387) and declared it unconstitutional in Ruling C-079 of 2026, ordering the indirect taxes collected under it to be refunded. A fiscal bill presented to Congress in 2026 would again move wines from 5 % to the general 19 % VAT and raise the consumption tax, mainly from 2027.
>
> According to the evaluation committee:
> - the decree set a specific component of 750 COP per degree with a 30 % ad valorem component and 19 % VAT;
> - the 2026 bill proposes 750 COP per degree with a 35 % ad valorem component and indexation at inflation plus four points from 2028, which would bring the specific component to roughly 900–1,000 COP per degree by 2030.
>
> These rates are taken from the committee's report and remain to be verified against the texts. For a project that starts in 2030 and whose largest single cost is this excise, the rate is a project risk, not a constant.
>
> Five regimes are evaluated, per bottle by the relation of Section 4.1.3 and for the whole plant by re-solving the MILP and the TEA (Table 5.6.1b):
> - the current one;
> - the specific component tripled (729 COP per degree);
> - the decree rates with 5 % VAT;
> - the decree rates with 19 % VAT;
> - the 2026 bill without indexation.
>
> Indexation would only deepen the loss on wine, so the conclusions drawn from the bill row also hold for the indexed bill.

### 2.13 Chapter 2, Section 2.2.5 — replacement paragraph on leaf juice, and registry rows (Appendix B)

> **Leaf juice.** Extraction yields 0.76 t of juice per tonne of leaves (Liao et al., 2026; 0.77 in Chen et al., 2020).
>
> *Composition.*
> - The juice holds 6.2 % solids, of which 14 % is crude protein, 10.0 % ash and 3.5 % fat (Liao et al., 2022, Table 1, from Chen et al., 2020). By difference it therefore holds about 44.9 g of carbohydrate per kg.
> - The free monosaccharides reported are 10.6 g/L of glucose and 16.4 g/L of xylose (Chen et al., 2020). Liao et al. (2022) give 0.6 g/L of C6 sugars for the same juice, a discrepancy to be resolved in the original.
>
> *Fermentation.* Fermented by *Kluyveromyces marxianus* at 35 °C without supplements, 46 kg of juice gave 35 kg of broth at 3.6 % v/v ethanol and 11 kg of wet yeast: about 1.0 kg of ethanol, or 21.7 kg per tonne of juice.
>
> *Checks.*
> - That yield is 0.485 g/g of carbohydrate, 95 % of the stoichiometric maximum. The free sugars alone could not produce it (0.82 g/g on them), so the yeast must also use part of the soluble oligosaccharides.
> - With the 16.1 kg of yeast dry matter per tonne that the same source reports, ethanol (21.8 kg), CO₂ (20.9 kg) and yeast add up to 58.8 kg per tonne, against 55.8 kg of organic solids. The balance does not close, so at least one output is overstated.
>
> *Value adopted.* The registry takes 90 % of the stoichiometric maximum on carbohydrate, 20.7 kg/t, as the design value. Its range is 11.1–20.7 kg/t; the lower end assumes that only the free sugars ferment, at the 0.42 g/g used for panela. A fermentation of Chocó leaf juice is the first measurement this thesis asks for (Section 6.7).

*Registry rows (Appendix B), before → after:*

| Key | Before | After |
|---|---|---|
| `azucar_jugo_hojas` | 27.0 g/L (glucose 10.6 + xylose 16.4) | renamed `azucar_libre_jugo_hojas`, 27.0 g/L, [L], Chen et al. 2020 (C6 0.6 g/L in Liao et al. 2022: [verify]) |
| `carbohidrato_jugo_hojas` (new) | — | 44.9 g/kg, [L, derived], by difference from Liao et al. 2022, Table 1 |
| `etanol_jugo_hojas` | 21.8 (18–24.5) kg/t, [L] | 20.7 (11.1–20.7) kg/t, PERT, [L/S]: 90 % of the stoichiometric maximum on carbohydrate. Source value 21.8 (95 %) kept in the notes; old upper bound 24.5 removed (0.545 g/g, above stoichiometry). |

### 2.14 Section 3.10.2 — table rows corrected

| Case | Free run | After polishing | After cross pass | Dual bound | Reported gap |
|---|---|---|---|---|---|
| Optimum (at 20.7 kg/t; certified by nesting, Section 5.6.3) | — | — | 3,164 | 3,280 | 3.7 % |
| Vinegar demand 1,500 m³ (at 21.8 kg/t) | 245 | 592 | 926 (version 13 cross-design pass) | 2,589 | 180 % |
| Vinegar demand 6,000 m³ (at 21.8 kg/t) | 5,548 | 6,634 | 7,086 (version 13 map) | 7,619 | 7.5 % |
| 1 million bottles (at 21.8 kg/t) | 4,366 | 4,469 | 4,942 (version 13 map) | 6,757 | 36.7 % |

> Note for the text:
> - The version 12 polishing of the vinegar case of 1,500 m³ ended at 817 MM COP/year. Its free run gave a dual bound of 2,589. The version 13 cross-design pass of the demand map found 926 for the same case, and the thesis now reports 926 everywhere.
> - The cases of 6,000 m³ and of 1 million bottles likewise take the values of the demand map, and their bounds come from the map's free runs.
> - The optimum's former gap of 16.9 % is superseded by the nesting certificate.

### 2.15 Editorial corrections (exact replacements)

| Location | Before | After |
|---|---|---|
| §5.4.2, price grid, row PVP 16,000 / vinegar 2,200 | 3,194 · 5,389 | the central values of the thesis (3,164 · 5,273 at 20.7 kg/t; 3,196 · 5,397 at 21.8 kg/t). That grid point had stopped 0.06 % below the optimum, within the 0.2 % fixed-design tolerance. |
| §5.4.2, column header | «Wine sold (m³)» | «Wine produced (m³)». The TEA sells 95 % of it (Table 4.1). |
| §5.4.3 and E8 table, vinegar demand 1,500 m³ | 817 | 926 (at 21.8 kg/t) |
| §5.4.3, vinegar demand 6,000 m³ | 6,634 | 7,086 (at 21.8 kg/t) |
| §5.4.x, 250,000 bottles | 2,319 | 2,317 (at 21.8 kg/t) |
| §3.10.2 and §5.4.x, 1 million bottles | 4,941 | 4,942 (at 21.8 kg/t) |
| §5.10 (H2) | «60 % costs 2,454» | «a 60 % cut costs 2,453» (3,195.6 − 742.3) |
| §5.6.4, §5.9.4, abstract | «+334», «+323» without basis | «+339 t (life-cycle inventory, 1,293 t)» and «+328 t (linear GWP of the MILP, 1,282 t; the 11 t difference is effluent treatment)» |
| §3.11 and §4.1.5 | «16 workbooks» | «27 workbooks» (all current workbooks; Appendix D) |
| §5.6.1 | «the excise on 475,000 bottles sold» | «the excise on the 475,000 bottles sold (95 % of the 500,000 produced, the sales convention of Table 4.1)» |
| §2.7.3 | «2,675 GJ of recoverable heat (33 %)» | «2,675 GJ of recoverable heat (33 % of the 8,043 GJ drying demand)» |
| §5.1.1 | «The equivalent purchased-equipment cost entering the capital charge is 12,640 MM COP» | text of §2.2 of this response |
| Preamble of Chapter 5 | «the kinetics bound (7.1–9.0 % …) applies to every figure» | «the kinetics–train coupling is worth 3.8–12.5 % of the fermentation-train cost at the flow of the optimum (Section 5.11.3), and the kinetic band does not change the plant design (Section 5.11.1)» |
| New §6.6 item | — | «**Storage outside the MILP.** The vinegar tanks (30 days) and wine-ageing tanks (90 days), 930 MM COP of purchased equipment, are costed by the TEA but not sized by the MILP, whose objective therefore omits about 709 MM COP/year of capital charge (AF × 930). Every NPV reported includes them. The choice between more vinegar and more wine could shift slightly towards wine if they entered the objective. Adding storage to the catalogue is the next model change.» |
| New §6.6 item | — | «**Results at the former leaf-juice yield.** The autonomy sweep (H2), the interior of the margin–GWP front (H3), the price sweeps of Section 5.4 and the multiscale tests of Section 5.11 were computed at 21.8 kg/t, the upper end of the corrected range. At the optimum the correction lowers the margin by 32 MM COP/year (1.0 %) without changing the design.» |

### 2.16 References

**Added (verified):**
- Corte Constitucional de Colombia (2026). Auto 082 de 2026, 29 January 2026, expediente RE-387 (provisional suspension of Legislative Decrees 1390 and 1474 of 2025).
- Corte Constitucional de Colombia (2026). Sentencia C-079 de 2026 (Legislative Decree 1474 of 2025 declared unconstitutional).
- DIAN (2026). Oficio 4031 de 2026 (VAT of 5 % on wines after the suspension of Decree 1474 of 2025).
- Liao, C. Y., Guan, Y. J., & Bustamante-Román, M. (2022). Techno-economic analysis and life cycle assessment of pineapple leaves utilization in Costa Rica. *Energies*, 15(16), 5784. https://doi.org/10.3390/en15165784

**Added (to be verified):**
- Presidencia de la República de Colombia (2025). Decreto Legislativo 1474 de 2025, 29 December 2025 [verify rates: specific component, ad valorem, VAT].
- Ministerio de Hacienda y Crédito Público (2026). Fiscal bill presented to Congress in 2026 («ley de rescate») [verify number and rates].

**Still marked, to be resolved against the original before the defence:**
- *26 reference-list entries:* Arpagaus et al. 2018; Burk 2026 [complete]; Castro et al. 2018; Celis Cabeza et al. 2024; Corsano et al. 2009; Dak et al. 2008; Galanopoulos et al. 2020; García García et al. 2023; Guillén-Gosálbez et al. 2019; Hossain et al. 2016; Huang et al. 2020; Indrawan et al. 2020; Kasani et al. 2022; Kouakou et al. 1987; Martín et al. 2023; Morales-Rodriguez et al. 2012; Moreno et al. 2022; Nickel et al. 2020; OECD 2022; OECD 2023; Steingass et al. 2015; Towler & Sinnott 2022; Uslu et al. 2024; Vaillant et al. 1999; Zhang & Rosentrater 2019; and the citation chains «cited by Ebrahimi, 2026» and «cited by Iakovchenko, 2026».
- *7 citations in the text:* Hossain et al. 2016; Celis Cabeza et al. 2024; Bustos et al. 2014; the lignin content of crown and leaves (Saini et al. 2022); Kouakou et al. 1987; the income-tax schedule (statute); Balanzó Guzmán et al. 2021.

---

## 3. Nuevas tablas de datos

### 3.1 Tabla de sensibilidad fiscal del vino (Table 5.6.1b, for the thesis)

*Table 5.6.1b. Wine excise regimes: net revenue per 750 mL bottle and whole-plant result (leaf-juice ethanol 20.7 kg/t). Net = factory price − excise − packaging (2,400 COP); factory price = retail price / (1 + VAT) / (1 + distribution margin). The excise is computed by the relation of Section 4.1.3.*

| Regime (specific COP/degree; ad valorem; VAT) | Excise per bottle at 16,000 COP | Net per bottle at 10,000 / 16,000 / 25,000 COP | Re-optimized plant (MM COP/year) | Current design kept: margin (MM COP/year) and NPV (MM COP) |
|---|---|---|---|---|
| Current (243; 20 %; 5 %) | 4,220 | 1,387 / 4,667 / 9,588 | 3,164; NPV 5,273 (500,000 bottles; 3,000 m³) | 3,164; 5,273 |
| Specific component tripled (729; 20 %; 5 %) | 7,582 | −1,975 / 1,306 / 6,226 | 1,868, vinegar only (best found; dual bound 3,312); NPV ≈ +632 ± 1,798 | 1,567; −993 |
| Decree 1474/2025 rates, 5 % VAT (750; 30 %; 5 %) | 8,305 | −2,332 / 583 / 4,954 | 1,868, vinegar only (certified) | 1,408, buys no fruit; below break-even |
| Decree 1474/2025 rates, 19 % VAT (750; 30 %; 19 %) | 7,891 | −2,903 / −332 / 3,525 | 1,868, vinegar only (certified) | 1,408, buys no fruit; below break-even |
| 2026 fiscal bill, no indexation (750; 35 %; 19 %) | 8,097 | −2,965 / −537 / 3,104 | 1,868, vinegar only (certified) | 1,408, buys no fruit; below break-even |
| *Vinegar-only plant at a lower leaf-juice yield* | — | — | 1,654 at 13.5 kg/t (NPV ≈ −137); 1,581 at 11.1 kg/t (NPV ≈ −396) | — |

*Note: with 19 % VAT the excise per bottle is lower than with 5 %, because the ad valorem base, the retail price before VAT, is smaller. The net per bottle is still lower.*

### 3.2 Tabla de H4 en VPN

Tables 5.9.2a and 5.9.2b in §2.7 above.

### 3.3 Tablas del desglose de la neutralidad y de la sensibilidad del ACV

Tables 5.9.4b and 5.9.4c in §2.9 above, and Table 5.6.4b in §2.6.

### 3.4 Tabla del frente H3 con intervalos

Table 5.9.4a in §2.9 above.

### 3.5 Tabla del jugo de hoja

Table 5.1.2a in §2.3 above.

### 3.6 Tabla canónica del diseño central (new Table 5.1.1b, cited from every section)

*Table 5.1.1b. Canonical figures of the central design (500,000 bottles; 3,000 m³ of vinegar; leaf-juice ethanol 20.7 kg/t).*

| Quantity | Value | Basis |
|---|---|---|
| Annual margin | 3,164 MM COP/year | MILP; certified within 3.7 % (dual bound 3,280) |
| Contribution before capital charge | 6,478 MM COP/year | MILP |
| Annualized capital charge | 3,314 MM COP/year | MILP: AF × 4,026 purchase + 246 fixed |
| Purchased equipment | 4,026 (MILP catalogue) / 5,225 (TEA, with storage) MM COP | |
| Fixed-capital investment | 12,640 (MILP, Lang 3.14) / 16,405 (TEA) MM COP | |
| Revenue | 12,089 MM COP/year | TEA (95 % of production sold) |
| Variable / fixed / operating costs | 5,097 / 2,227 / 7,324 MM COP/year | TEA |
| NPV; MIRR; payback | 5,273 MM COP; 13.4 %; 5.0 years (6.6 discounted) | TEA |
| P(NPV > 0); median NPV; CVaR 5 % | 0.78; 3,543; −6,347 MM COP | Monte Carlo, 1,000 samples |
| Break-even vinegar price | 1,723 COP/L | TEA tornado |
| Panela | 154.6 t/year | MILP |
| Process GWP; net GWP | 1,293 t; +339 t (inventory) / 1,282 t; +328 t (MILP) | ACV / MILP |

---

## 4. Nota metodológica para el Capítulo 3 (§3.11): prueba de coherencia estequiométrica

> **Stoichiometric coherence of the registry.** Every pair in the registry that links a sugar to a fermentation product must respect the stoichiometric maximum:
> - glucose and fructose give at most 2 mol of ethanol per mol (0.511 g/g);
> - xylose gives at most 5 mol of ethanol per 3 mol (also 0.511 g/g);
> - acetic acid from ethanol is bounded by 60/46 g/g, before the acetification yield of 0.94.
>
> **The test.** For each stream, the apparent yield Y = product / fermentable substrate must satisfy Y ≤ 0.511 g/g. The substrate must be stated with its basis: free sugars, total carbohydrate by difference, or sugar equivalent after hydrolysis.
>
> **The design ceiling.** A design value above 0.90 of the maximum is not accepted, because industrial fermentations rarely exceed 90–92 % of theory once yeast growth and by-products are accounted for. Above that ceiling, the design value is set at 0.90 of the maximum and the source value is kept in the notes.
>
> **Closure of the source.** When a source also reports biomass, the test checks that product, CO₂ and biomass do not exceed the organic matter of the substrate. A failure is resolved against the source, not by moving the parameter without stating why.
>
> **When it runs.** The test runs with the registry-against-code test before every model version. A failure stops the run, as an implementation error would.

*Table 3.11b. Stoichiometric coherence of the registry.*

| Stream | Substrate (basis) | Product | Apparent yield (g/g) | Fraction of maximum | Result |
|---|---|---|---|---|---|
| Pulp juice (Murcia Palacios, 2013) | 158.8 g/L sugar | 65.3 g/L ethanol | 0.411 | 0.80 | pass |
| Peel juice (Seguí and Fito, 2018) | 104 g/kg sugar | 37.4 g/kg ethanol | 0.360 | 0.70 | pass |
| Panela (registry) | 850 g/kg fermentable sugar | 357 g/kg ethanol | 0.420 | 0.82 | pass |
| Leaf juice, source value on free sugars (glucose 10.6 + xylose 16.4) | 27 g/L | 22.2 g/L ethanol | 0.824 | 1.61 | **fail** |
| Leaf juice, source value on carbohydrate by difference | 44.9 g/kg | 21.8 g/kg ethanol | 0.485 | 0.95 | above the design ceiling |
| Leaf juice, source mass balance (ethanol + CO₂ + yeast vs organic solids) | 55.8 g/kg organic solids | 58.8 g/kg outputs | — | 1.05 | **fail** |
| Leaf juice, old upper bound | 44.9 g/kg | 24.5 g/kg ethanol | 0.545 | 1.07 | **fail** (removed) |
| **Leaf juice, design value adopted** | **44.9 g/kg** | **20.7 g/kg ethanol** | **0.460** | **0.90** | **pass** |

> **Rows to change in Table 3.11 (version 12 status):**
> - *Stochastic program:* «EEV ≤ RP ≤ WS — satisfied after each wait-and-see scenario was re-solved from the known design (the first run had stopped at its time limit); at 20.7 kg/t, 3,164.0 ≤ RP ≤ WS ≤ 3,254.5».
> - *TEA:* «relative difference below 10⁻¹⁴ in the 27 current workbooks».
> - *New row — stoichiometric coherence:* «Y ≤ 0.511 g/g for every sugar–product pair; design ceiling 0.90; source closure — one pair failed (leaf juice) and was corrected (Section 2.2.5)».
> - *New row — optimality intervals:* «every hypothesis verdict reports [solution, dual bound]; the central optimum is certified by nesting of supply scenarios — reported in Sections 5.6.3 and 5.9.2–5.9.4».

---

## 5. Resumen del árbitro adversarial

**[en curso]**
