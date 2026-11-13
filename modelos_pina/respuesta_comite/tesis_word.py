"""Arma el Word de la tesis a partir de la exportación .docx del borrador (Claude Docs).

  python tesis_word.py <exportado.docx> <salida.docx>

1. Ecuaciones: cada bloque de código LaTeX ('bongo_lang_latex_*' o 'bongo_lang_math_*') se convierte en una ecuación nativa
   de Word (OMML, editable con el editor de ecuaciones) usando pandoc/texmath, y se numera por capítulo: (2.1), (3.1)… y
   (A.1)… en el Apéndice A. Cada ecuación va en una tabla sin bordes de una fila: la ecuación centrada en la celda ancha y
   su número alineado a la derecha en la celda estrecha. Así una ecuación larga se parte dentro de su celda sin empujar el número.
2. Referencias: 'Equation 5.6.1' (la numeración provisional del borrador) pasa al número que recibe esa ecuación.
3. Figuras: las imágenes que la exportación dejó como texto '[image: …]' (por tamaño) se reponen desde figs/en/.
"""
import html, os, re, shutil, subprocess, sys, tempfile, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "..", "figs", "en")
FIGMAP = {  # texto alternativo de la exportación -> figura local (informe de modelos)
    "Figure 5.8: from version 11 to version 12": "fig47_comparativo_v11_v12.png",
    "Figure 5.9: destination of wine by price pair": "fig32_vinagre_precios.png",
    "Figure 5.11: TEA of the optimal designs": "fig31_tea_dimensionado.png",
    "Figure 5.12: LCA of the designs with the field-return correction": "fig40_acv.png",
    "Figure 5.14: comparison of versions 8 and 9": "fig39_comparativo_v8_v9.png",
    "Figure 5.15: comparison of versions 9 and 10": "fig45_comparativo_v9_v10.png",
    "Figure 5.16: comparison of versions 10 and 11": "fig46_comparativo_v10_v11.png",
    "Figure 5.17: hot spots of the optimum": "fig44_puntos_calientes.png",
    "Figure 5.18: H1 at 20.7 kg/t and H4 demand map in NPV": "fig52_h1_h4_vpn.png",
    "Figure 5.19: H2 autonomy sweep and H3 net front with dual bounds": "fig53_h2_h3_cotas.png",
    "Figure 5.20. Multiscale tests of the optimum": "fig51_multiescala_resultados.png",
}
NS_M = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'
TEXT_W = 9360          # ancho útil en twips (carta, márgenes de 1 in)
NUM_W = 1000
IMG_CX = 5943600       # 6.5 in en EMU
PARA_RE = re.compile(r'<w:p[ >](?:(?!<w:p[ >]).)*?</w:p>', re.S)
txt = lambda p: html.unescape("".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)))


M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ORDER = {  # orden de hijos que exige el esquema OMML (pandoc a veces lo altera)
    "dPr": ["begChr", "sepChr", "endChr", "grow", "shp", "ctrlPr"],
    "rPr": ["lit", "nor", "scr", "sty", "brk", "aln"],
    "mcPr": ["count", "mcJc"],
}


def fix_order(xml):
    from lxml import etree
    root = etree.fromstring(f'<x xmlns:m="{M}" xmlns:w="{W}">{xml}</x>')
    for tag, order in ORDER.items():
        for el in root.iter(f"{{{M}}}{tag}"):
            kids = list(el)
            key = lambda k: order.index(etree.QName(k).localname) if etree.QName(k).localname in order else len(order)
            for k in kids:
                el.remove(k)
            names = {etree.QName(k).localname for k in kids}
            for k in sorted(kids, key=key):
                if tag == "rPr" and "nor" in names and etree.QName(k).localname in ("scr", "sty"):
                    continue          # el esquema admite nor o (scr, sty), no ambos
                el.append(k)
    # une runs contiguos con el mismo formato (pandoc escribe una letra por run): más fácil de editar en Word
    ops = set("=≈≤≥<>+−-×·,;∈∀∑∏")
    for parent in list(root.iter()):
        kids = list(parent)
        i = 0
        while i < len(kids) - 1:
            a, b = kids[i], kids[i + 1]
            if a.tag == b.tag == f"{{{M}}}r":
                pa, pb = a.find(f"{{{M}}}rPr"), b.find(f"{{{M}}}rPr")
                sa = etree.tostring(pa) if pa is not None else b""
                sb = etree.tostring(pb) if pb is not None else b""
                ta, tb = a.find(f"{{{M}}}t"), b.find(f"{{{M}}}t")
                if sa == sb and ta is not None and tb is not None and not (set(ta.text or "") | set(tb.text or "")) & ops:
                    ta.text = (ta.text or "") + (tb.text or "")
                    parent.remove(b)
                    kids.pop(i + 1)
                    continue
            i += 1
    out = "".join(etree.tostring(c, encoding="unicode") for c in root)
    return re.sub(r' xmlns:(m|w)="[^"]+"', "", out)


def omml(latex_list):
    """LaTeX -> lista de <m:oMathPara> vía pandoc (un párrafo por ecuación)."""
    tmp = tempfile.mkdtemp()
    latex_list = [re.sub(r"(\d+)\{,\}(\d+)", lambda m: "\\text{%s,%s}" % (m.group(1), m.group(2)), l) for l in latex_list]
    md = "\n\n".join(f"$${l}$$" for l in latex_list)
    open(os.path.join(tmp, "e.md"), "w", encoding="utf8").write(md)
    out = os.path.join(tmp, "e.docx")
    subprocess.run(["pandoc", os.path.join(tmp, "e.md"), "-o", out], check=True)
    x = zipfile.ZipFile(out).read("word/document.xml").decode("utf8")
    paras = PARA_RE.findall(x)
    res = []
    for p in paras:
        m = re.search(r'<m:oMathPara>.*?</m:oMathPara>', p, re.S)
        res.append(fix_order(m.group(0)) if m else None)
    shutil.rmtree(tmp)
    return res


def eq_table(math, label):
    border = '<w:tblBorders>' + ''.join(f'<w:{b} w:val="nil"/>' for b in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:jc w:val="center"/>{border}'
            f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
            f'<w:tblLook w:val="0000"/></w:tblPr><w:tblGrid><w:gridCol w:w="{TEXT_W - NUM_W}"/><w:gridCol w:w="{NUM_W}"/></w:tblGrid>'
            f'<w:tr><w:trPr><w:cantSplit/></w:trPr>'
            f'<w:tc><w:tcPr><w:tcW w:w="{TEXT_W - NUM_W}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="120" w:after="120"/><w:jc w:val="center"/></w:pPr>{math}</w:p></w:tc>'
            f'<w:tc><w:tcPr><w:tcW w:w="{NUM_W}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="120" w:after="120"/><w:jc w:val="right"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">({label})</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')


def drawing(rid, n, alt, cx, cy):
    alt = html.escape(alt, quote=True)
    return (f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{n}" name="image{n}" descr="{alt}"/>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
            f'<pic:cNvPr id="{n}" name="image{n}" descr="{alt}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'</pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def main(src, dst):
    work = tempfile.mkdtemp()
    with zipfile.ZipFile(src) as z:
        z.extractall(work)
    dpath = os.path.join(work, "word", "document.xml")
    s = open(dpath, encoding="utf8").read()
    if "xmlns:m=" not in s[:2000]:
        s = s.replace("<w:document ", f"<w:document {NS_M} ", 1)
    # ---- 1. ecuaciones
    items = []          # (span, latex, label)
    chap, count = None, {}
    for m in PARA_RE.finditer(s):
        p = m.group(0)
        if 'w:val="Heading2"' in p:
            t = txt(p)
            mm = re.match(r'Chapter (\d+)\.', t)
            chap = mm.group(1) if mm else ("A" if t.startswith("Appendices") else None)
        if re.search(r'bongo_lang_(latex|math)_\d+', p):
            latex = re.sub(r'\\qquad\s*\(\d+(\.\d+)*\)\s*$', '', txt(p)).strip()
            count[chap] = count.get(chap, 0) + 1
            items.append((m.span(), latex, f"{chap}.{count[chap]}"))
    maths = omml([l for _, l, _ in items])
    bad = [lab for (_, _, lab), mt in zip(items, maths) if not mt]
    if bad or len(maths) != len(items):
        sys.exit(f"pandoc no convirtió: {bad} ({len(maths)} de {len(items)})")
    labels = {}
    for (span, latex, lab), mt in sorted(zip(items, maths), key=lambda x: -x[0][0][0]):
        s = s[:span[0]] + eq_table(mt, lab) + s[span[1]:]
        labels[latex] = lab
    npv = next(lab for l, lab in labels.items() if l.startswith(r"\mathrm{NPV} \approx"))
    s = s.replace("Equation 5.6.1", f"Equation {npv}")
    # ---- 2. figuras
    rpath = os.path.join(work, "word", "_rels", "document.xml.rels")
    rels = open(rpath, encoding="utf8").read()
    rid0 = max(int(x) for x in re.findall(r'Id="rId(\d+)"', rels))
    nimg = max([int(x) for x in re.findall(r'docPr id="(\d+)"', s)] + [0])
    done = []
    for alt, fn in FIGMAP.items():
        ph = f'[image: {alt}]'
        m = next((m for m in PARA_RE.finditer(s) if txt(m.group(0)).strip() == ph), None)
        if not m:
            continue
        rid0 += 1; nimg += 1
        name = f"media/fig_rep_{nimg}.png"
        shutil.copy(os.path.join(FIGS, fn), os.path.join(work, "word", name))
        w, h = Image.open(os.path.join(FIGS, fn)).size
        rels = rels.replace("</Relationships>", f'<Relationship Id="rId{rid0}" Type="http://schemas.openxmlformats.org/officeDocument/'
                                                f'2006/relationships/image" Target="{name}"/></Relationships>')
        s = s[:m.start()] + drawing(f"rId{rid0}", nimg, alt, IMG_CX, int(IMG_CX * h / w)) + s[m.end():]
        done.append(alt)
    open(rpath, "w", encoding="utf8").write(rels)
    open(dpath, "w", encoding="utf8").write(s)
    left = re.findall(r'\[image: [^\]]*\]', s)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(work):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, work))
    shutil.rmtree(work)
    by = {}
    for _, _, lab in items:
        by.setdefault(lab.split(".")[0], 0); by[lab.split(".")[0]] += 1
    print(f"ecuaciones: {len(items)} {by}; ecuación de la relación margen–VPN: ({npv}); figuras repuestas: {len(done)}; "
          f"marcadores sin reponer: {left}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
