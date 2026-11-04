// Construye el informe .docx a partir de los bloques de html2blocks.py (docx-js).
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  ImageRun, AlignmentType, LevelFormat, BorderStyle, Footer, Header, PageNumber, TableOfContents, PageBreak,
} = require("docx");

const [, , blocksPath, outPath] = process.argv;
const blocks = JSON.parse(fs.readFileSync(blocksPath, "utf8"));
const PAGE_W = 12240, MARGIN = 1300, CONTENT = PAGE_W - 2 * MARGIN;   // carta, márgenes 0,9"
const ACCENT = "1F6B52", INK2 = "4C5650", RULE = "D9DDD6", HEADFILL = "E8EDE9", NOTEFILL = "FBF1DA";

function tr(r, base = {}) {
  if (r.br) return new TextRun({ break: 1 });
  const o = { text: r.text, bold: r.bold || base.bold, italics: r.italics || base.italics,
              size: base.size || (r.small ? 17 : undefined), color: base.color };
  if (r.subScript) o.subScript = true;
  if (r.superScript) o.superScript = true;
  if (r.mono) o.font = "Consolas";
  return new TextRun(o);
}
const R = (runs, base) => (runs || []).map((r) => tr(r, base));
const plain = (runs) => (runs || []).map((r) => r.text || "").join("");

function table(b) {
  const ncol = b.head.length;
  const weights = b.head.map((h, j) => {
    let m = Math.max(4, plain(h).length * 0.8);
    for (const row of b.rows) m = Math.max(m, Math.min(60, plain(row[j] || []).length));
    return Math.sqrt(m);
  });
  const tot = weights.reduce((a, c) => a + c, 0);
  let widths = weights.map((w) => Math.round((w / tot) * CONTENT));
  widths[widths.length - 1] += CONTENT - widths.reduce((a, c) => a + c, 0);
  const fs_ = ncol >= 8 ? 14 : ncol >= 6 ? 15 : 17;
  const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (runs, j, head) => new TableCell({
    width: { size: widths[j], type: WidthType.DXA }, borders,
    shading: head ? { fill: HEADFILL, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    children: [new Paragraph({ spacing: { before: 0, after: 0 },
      alignment: (!head && j > 0 && /^[-−+]?[\d\s.,%—–]+[%]?$/.test(plain(runs).trim())) ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: R(runs, { size: fs_, bold: head }) })],
  });
  return new Table({
    width: { size: CONTENT, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: b.head.map((h, j) => cell(h, j, true)) }),
           ...b.rows.map((row) => new TableRow({ children: b.head.map((_, j) => cell(row[j] || [], j, false)) }))],
  });
}

const children = [];
let first = true;
for (const b of blocks) {
  if (b.type === "title") {
    children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: R(b.runs) }));
  } else if (b.type === "h2") {
    if (!first) children.push(new Paragraph({ children: [new PageBreak()] }));
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: R(b.runs) }));
    first = false;
  } else if (b.type === "h3") {
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: R(b.runs) }));
  } else if (b.type === "p") {
    children.push(new Paragraph({ spacing: { after: 120 }, children: R(b.runs, b.kicker ? { color: ACCENT, bold: true, size: 18 } : b.lede ? { color: INK2, size: 24 } : {}) }));
    if (b.lede) { children.push(new Paragraph({ children: [] })); children.push(new TableOfContents("Contenido", { hyperlink: true, headingStyleRange: "1-2" })); }
  } else if (b.type === "list") {
    b.items.forEach((it) => children.push(new Paragraph({ numbering: { reference: b.ordered ? "num" : "bul", level: 0 }, spacing: { after: 60 }, children: R(it) })));
  } else if (b.type === "pre") {
    b.lines.filter((l) => l.trim()).forEach((l) => children.push(new Paragraph({
      spacing: { before: 0, after: 0 }, shading: { fill: "EEF1EC", type: ShadingType.CLEAR, color: "auto" },
      children: [new TextRun({ text: l, font: "Consolas", size: 15 })] })));
    children.push(new Paragraph({ children: [] }));
  } else if (b.type === "figure") {
    const wpx = 624, hpx = Math.round((b.h / b.w) * wpx);
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(b.src), transformation: { width: wpx, height: hpx },
        altText: { title: plain(b.caption).slice(0, 60), description: plain(b.caption), name: "figura" } })] }));
    children.push(new Paragraph({ style: "Caption", children: R(b.caption) }));
  } else if (b.type === "table") {
    children.push(table(b));
    children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  } else if (b.type === "findings") {
    b.items.forEach((it) => {
      children.push(new Paragraph({ spacing: { before: 120, after: 20 }, keepNext: true,
        border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 6 } },
        children: [new TextRun({ text: it.n, bold: true, color: ACCENT, size: 26 })] }));
      children.push(new Paragraph({ spacing: { after: 20 }, border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 6 } }, children: R(it.t) }));
      if (it.s) children.push(new Paragraph({ spacing: { after: 100 }, border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 6 } },
        children: [new TextRun({ text: it.s, size: 16, color: INK2 })] }));
    });
  } else if (b.type === "note") {
    children.push(new Paragraph({ spacing: { before: 120, after: 160 }, shading: { fill: NOTEFILL, type: ShadingType.CLEAR, color: "auto" },
      border: { left: { style: BorderStyle.SINGLE, size: 18, color: "9A6A00", space: 6 } }, children: R(b.runs) }));
  }
}

const doc = new Document({
  features: { updateFields: true },
  creator: "Biorrefinería de piña — Bajo Atrato", title: "Modelos Corsano para la piña",
  styles: {
    default: { document: { run: { font: "Calibri", size: 21 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: "Cambria", size: 44, bold: true, color: "17201B" }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Cambria", size: 32, bold: true, color: "17201B" }, paragraph: { spacing: { before: 240, after: 140 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Cambria", size: 25, bold: true, color: ACCENT }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 1 } },
      { id: "Caption", name: "Caption", basedOn: "Normal", run: { size: 17, italics: true, color: INK2 }, paragraph: { spacing: { before: 0, after: 200 } } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1200, bottom: 1200, left: MARGIN, right: MARGIN } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Biorrefinería de piña · Bajo Atrato · Modelos y TEA", size: 16, color: INK2 })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 16, color: INK2 })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("docx escrito", outPath); });
