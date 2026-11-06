// Paquete de verificación en SuperPro como .docx, a partir de superpro/*.csv
// Uso: NODE_PATH=$(npm root -g) node superpro_docx.js superpro superpro/Paquete_SuperPro_v12.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, PageOrientation, LevelFormat, BorderStyle, Footer, PageNumber,
} = require("docx");

const DIR = process.argv[2];
const OUT = process.argv[3];

function csv(file) {
  const txt = fs.readFileSync(path.join(DIR, file), "utf8").trim();
  const rows = [];
  for (const line of txt.split(/\r?\n/)) {
    const out = []; let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"') { q = !q; continue; }
      if (c === "," && !q) { out.push(cur); cur = ""; continue; }
      cur += c;
    }
    out.push(cur); rows.push(out);
  }
  return rows;
}

// números en formato colombiano: miles con espacio fino, decimales con coma
function num(v, dec) {
  const x = Number(v);
  if (!isFinite(x)) return v;
  if (x === 0) return "0";
  const d = dec !== undefined ? dec : (Math.abs(x) >= 100 ? 0 : Math.abs(x) >= 10 ? 1 : 2);
  let [ent, fr] = Math.abs(x).toFixed(d).split(".");
  ent = ent.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return (x < 0 ? "−" : "") + ent + (fr ? "," + fr : "");
}
// decimales con punto dentro de textos ("0.87 t/t", "12%") → coma y espacio antes de %
const fixTxt = (s) => s.replace(/(\d)\.(\d)/g, "$1,$2").replace(/(\d)%/g, "$1 %");

const FONT = "Arial";
const INK = "1F2933", MUTED = "5B6670", HEAD = "E8EEF3", BORDER = "B8C2CC", FILL = "FFF7E0";

const p = (text, opts = {}) => new Paragraph({
  spacing: { after: 120, line: 276 }, ...opts.para,
  children: (Array.isArray(text) ? text : [text]).map((t) => typeof t === "string" ? new TextRun({ text: t, font: FONT, size: 21, color: INK }) : t),
});
const r = (text, o = {}) => new TextRun({ text, font: FONT, size: 21, color: INK, ...o });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const bullet = (runs) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 276 }, children: runs.map((t) => typeof t === "string" ? r(t) : t) });
const step = (runs) => new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 100, line: 276 }, children: runs.map((t) => typeof t === "string" ? r(t) : t) });

const cellBorders = { top: { style: BorderStyle.SINGLE, size: 4, color: BORDER }, bottom: { style: BorderStyle.SINGLE, size: 4, color: BORDER },
  left: { style: BorderStyle.SINGLE, size: 4, color: BORDER }, right: { style: BorderStyle.SINGLE, size: 4, color: BORDER } };

function table(headers, rows, widths, opts = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const mk = (text, w, head, i, fill) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders: cellBorders,
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: HEAD } : fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({
      alignment: (opts.right || []).includes(i) && !head ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), font: FONT, size: opts.size || 18, bold: head, color: INK })],
    })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, widths[i], true, i)) })]
      .concat(rows.map((row) => new TableRow({ cantSplit: true, children: row.map((c, i) => mk(c, widths[i], false, i, (opts.fill || {})[i])) }))),
  });
}
const note = (t) => new Paragraph({ spacing: { before: 80, after: 200 }, children: [new TextRun({ text: t, font: FONT, size: 17, italics: true, color: MUTED })] });

// ---------------- datos
const proc = csv("procedimientos.csv");
const corr = csv("corrientes.csv");
const ver = csv("verificacion.csv");

const procRows = proc.slice(1).map((row) => row.map((c, i) => fixTxt(c.replace("capacidad.FR", "registro de parámetros"))));
// el jugo de hojas fermenta en la misma bodega que el jugo de cáscara
procRows.forEach((row) => {
  if (row[0] === "Fermentación del jugo de cáscara") {
    row[0] = "Fermentación de jugos (cáscara y hojas)";
    row[4] = "cáscara 12,6 h; hojas 14,5 h (cinética calibrada)";
    row[6] = "cáscara 0,36 g/g (Seguí y Fito 2018); hojas 21,8 kg de etanol/t de jugo (Chen et al. 2020)";
  }
});

const unitOf = (name) => (name.match(/\((m³|L)\)/) || [])[1] || "t/año";
const corrRows = corr.slice(1).map(([n, v]) => {
  const u = unitOf(n); const name = n.replace(/ \((m³|L)\)/, "");
  const unit = u === "m³" ? "m³/año" : u === "L" ? "L/año" : "t/año";
  return [name, Number(v) === 0 ? "0 (no se usa en el óptimo)" : num(v), unit];
});

const verRows = ver.slice(1).map(([ind, model, , , tol]) => {
  const isOcc = ind.startsWith("Ocupación");
  return [ind, isOcc ? num(Number(model) * 100, 0) + " %" : num(model), "", "", tol.replace("±", "± ")];
});

// ---------------- documento
const PORTRAIT = { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1300, left: 1300, right: 1300 } };
const LANDSCAPE = { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1100, bottom: 1100, left: 1100, right: 1100 } };
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
  new TextRun({ text: "Paquete de verificación en SuperPro · diseño óptimo v12 · página ", font: FONT, size: 16, color: MUTED }),
  new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: MUTED })] })] });

const intro = [
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Paquete de verificación en SuperPro Designer", font: FONT, size: 40, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Diseño óptimo de la versión 12 · Biorrefinería de piña del Bajo Atrato (Chocó)", font: FONT, size: 24, color: MUTED })] }),
  new Paragraph({ spacing: { after: 280 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: BORDER, space: 6 } },
    children: [new TextRun({ text: "Generado con superpro_paquete.py a partir de results/dimensionamiento.json (caso «E1 | Óptimo económico», oferta Chocó 2022) · noviembre de 2026", font: FONT, size: 18, color: MUTED })] }),

  h1("1. Para qué sirve"),
  p("Este documento reúne lo necesario para armar en SuperPro Designer el diseño óptimo que eligió el MILP de dimensionamiento y comparar el simulador con los modelos de Python. Corresponde a la etapa 2 del marco de Bertran, Tula y Gani (2022): el diseño que sale de la síntesis se verifica con un simulador antes de pasar a la etapa de innovación. El armado sigue a Foo (2023), capítulos 10 y 11 (procesos por lotes y fermentadores escalonados)."),
  p("SuperPro no corre en el entorno de los modelos. Quien tiene la licencia arma el modelo con las tablas de este documento, llena las columnas vacías de la sección 6 y devuelve los resultados para corregir los coeficientes del registro de parámetros (datos/parametros.csv)."),

  h1("2. Diseño que se verifica"),
  p("Oferta de 6 146 t/año de fruta de rechazo (EVA 2022), de las que se procesan 1 276 t/año: con el vino topado en 500 000 botellas/año y el vinagre en 3 000 m³/año, la planta queda limitada por el mercado y no por la fruta. Se acopian 3 746 t/año de hojas de la planta en la renovación del cultivo y se añaden 146 t/año de panela a los jugos. Margen del MILP: 3 196 MM COP/año."),
  table(["Sección", "Equipos y tamaños del modelo"], [
    ["Frente y pulpa", "Recepción y lavado 1 t/h · prensa de banda 1 t/h, compartida por pulpa y cáscara · macerador a 55 °C"],
    ["Mosto y vino", "Flotación 0,5 m³/h · SO₂ · almacén aséptico de mosto 10 m³ (los fermentadores se llenan desde él con bomba) · bodega de vino 2 × 10 m³ · embotelladora de 500 botellas/h"],
    ["Cáscara y harina", "Cáscara prensada en la prensa compartida (sin pretratamiento) · secador de banda 50 kg de agua/h · molino"],
    ["Vinagre", "Bodega de jugos 2 × 10 m³ (cáscara y hojas, con panela) · acetificador Frings 10 m³"],
    ["Hojas", "Extractora de tornillo 2 t/h; la pulpa de hojas vuelve al campo"],
    ["Servicios", "Caldera a GLP para el secador (sin caldera de corona) · grupo electrógeno diésel · chillers agua-glicol · generador de N₂"],
  ], [2400, 6906]),
  note("No se eligen en el óptimo: etanol de hojas, destilación, digestor y motor de biogás, ácido cítrico y xantana. No hace falta modelarlos."),

  h1("3. Cómo armar el modelo"),
  step([r("Crear un proceso por lotes con cinco secciones: "), r("Mosto y vino", { bold: true }), r(", "), r("Cáscara y harina", { bold: true }), r(", "), r("Hojas", { bold: true }), r(", "), r("Vinagre", { bold: true }), r(" y "), r("Servicios", { bold: true }), r(".")]),
  step(["Registrar los componentes: agua, sacarosa, glucosa, fructosa, xilosa, etanol, ácido acético, CO₂, O₂, biomasa, fibra (celulosa como sustituto) y cenizas."]),
  step(["Agregar los procedimientos de la sección 4 con su modo y tamaño. Para la bodega de vino y la de jugos usar fermentadores escalonados (staggered) con el número de unidades del modelo, como en el ejemplo de ácido cítrico de Koulouris (Foo 2023, cap. 11). El tiempo de ciclo de la receta es el llenado de un fermentador."]),
  step(["Cargar las estequiometrías y los datos de la sección 3.1, con los rendimientos medidos y no los teóricos."]),
  step(["Alimentar las entradas anuales de la sección 5 y correr la programación del año."]),
  step(["Anotar los resultados de SuperPro en la tabla de la sección 6 y calcular la diferencia relativa."]),

  h2("3.1 Estequiometrías y datos de reacción"),
  table(["Reacción o equipo", "Dato que se carga", "Fuente"], [
    ["Fermentación alcohólica del mosto", "C₆H₁₂O₆ → 2 C₂H₅OH + 2 CO₂; 65,3 g/L de etanol a las 12,5 h; 30 °C", "Murcia Palacios (2013)"],
    ["Fermentación del jugo de cáscara", "0,36 g de etanol por g de azúcar; 12,6 h por lote", "Seguí y Fito (2018); cinética calibrada"],
    ["Fermentación del jugo de hojas", "21,8 kg de etanol por t de jugo; 14,5 h por lote", "Chen et al. (2020)"],
    ["Acetificación", "C₂H₅OH + O₂ → CH₃COOH + H₂O; 46 g de etanol → 60 g de ácido al 94 % del teórico; ΔH = −493 kJ/mol; 50 kg/m³·d; aireación 1,2 kW/m³; vinagre al 5 % (50 kg/m³)", "Emde (2017)"],
    ["Mezcla del vinagre", "El acetificador solo diluye: la panela añadida (hasta 150 g/L) lleva los jugos fermentados de cáscara y hojas al 5 % sin vino; el agua de dilución cierra el balance", "Restricción del MILP; Tanamool et al. (2020) en Ebrahimi (2026)"],
    ["Maceración enzimática", "42 MJ por t de pulpa con 60 % de recuperación de calor; 55 °C", "Modelo de planta"],
    ["Secado de torta", "0,81 t de agua por t de torta; 2 590 MJ por t de torta", "Campos et al. (2020); modelo de planta"],
    ["Caldera de corona", "2 720 MJ útiles por t de corona (20 % de materia seca, 17 MJ/kg, eficiencia 80 %)", "Línea L7b del TEA"],
  ], [2500, 4806, 2000]),
];

const procSection = [
  h1("4. Procedimientos unitarios"),
  p("Un procedimiento de SuperPro por fila. El tamaño es el del catálogo que eligió el MILP; las horas de los equipos con personal son las de dos turnos de seis horas efectivas de lunes a sábado."),
  table(proc[0].map((h) => h === "Tiempo de ciclo u horas" ? "Ciclo u horas" : h === "Procedimiento de SuperPro sugerido" ? "Procedimiento de SuperPro" : h),
    procRows, [2150, 2550, 1450, 1450, 2250, 1450, 3336], { size: 17 }),
];

const restSection = [
  h1("5. Corrientes anuales que el modelo debe reproducir"),
  p("Base anual del diseño óptimo. Las dos primeras filas son entradas; las demás son resultados del balance del modelo de Python que SuperPro debe reproducir."),
  table(["Corriente", "Valor", "Unidad"], corrRows, [4500, 3000, 1806], { right: [1] }),
  note("La pulpa de hojas vuelve al campo y no pasa por la caldera; el etanol no se produce en el óptimo."),

  h1("6. Indicadores de verificación"),
  p([r("Llenar las columnas «SuperPro» y «Diferencia» con "), r("diferencia = (SuperPro − modelo) / modelo", { italics: true }), r(". Una diferencia fuera de la tolerancia señala el coeficiente del registro que hay que revisar. Las columnas en amarillo son las que se llenan con los resultados de SuperPro.")]),
  table(["Indicador", "Modelo (Python)", "SuperPro", "Diferencia", "Tolerancia"], verRows, [3700, 1500, 1500, 1400, 1206], { right: [1], fill: { 2: FILL, 3: FILL } }),

  h1("7. Qué se compara y qué hacer con las diferencias"),
  bullet([r("Calor y electricidad. ", { bold: true }), r("El modelo de Python usa coeficientes por unidad de flujo y SuperPro calcula entalpías. Si la diferencia supera la tolerancia, se corrige el coeficiente correspondiente en datos/parametros.csv (consumo por tonelada, calor de maceración o de secado, aireación).")]),
  bullet([r("Ciclos. ", { bold: true }), r("El llenado de los fermentadores sale de la bodega de Moresi (Q ≤ (N − 1)·V/t) y el ciclo de la bodega de jugos, de la cinética calibrada. La programación de lotes de SuperPro los verifica.")]),
  bullet([r("Producción. ", { bold: true }), r("Vino, vinagre y harina deben coincidir dentro de pocos puntos si los balances están bien cerrados. Una diferencia grande apunta a una pérdida o un rendimiento mal cargado.")]),
  bullet([r("Ocupación del acetificador. ", { bold: true }), r("El MILP lo deja al 100 % en los meses pico; SuperPro debe confirmar que 10 m³ alcanzan con la aireación y el frío del modelo.")]),
  p("Con la tabla de la sección 6 llena, los resultados se cargan en el informe y, si hace falta, se reoptimiza con los coeficientes corregidos.", { para: { spacing: { before: 160, after: 120 } } }),

  h2("Fuentes"),
  p("Bertran, Tula y Gani (2022); Campos et al. (2020); Ebrahimi (2026); Chen et al. (2020); Emde (2017); Foo (2023), caps. 10 y 11; Moresi (1989b); Murcia Palacios (2013); Seguí y Fito (2018). Las referencias completas están en la bibliografía del informe v12."),
];

const doc = new Document({
  creator: "Modelos Corsano para la piña",
  title: "Paquete de verificación en SuperPro – diseño óptimo v12",
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 28, bold: true, color: INK }, paragraph: { spacing: { before: 320, after: 140 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 24, bold: true, color: INK }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] },
  ] },
  sections: [
    { properties: { page: PORTRAIT }, footers: { default: footer }, children: intro },
    { properties: { page: LANDSCAPE }, footers: { default: footer }, children: procSection },
    { properties: { page: PORTRAIT }, footers: { default: footer }, children: restSection },
  ],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("ok", OUT, b.length); });
