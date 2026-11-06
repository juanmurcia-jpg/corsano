# Verificación del diseño óptimo v12 en SuperPro Designer

Este paquete lo genera `superpro_paquete.py` a partir de `results/dimensionamiento.json` («E1|Óptimo económico»). Sirve para la
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
