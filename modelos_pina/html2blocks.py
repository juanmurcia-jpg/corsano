"""Convierte informe.html en una lista de bloques JSON para make_docx.js (mismo contenido que el HTML)."""
import json, sys, os, struct
from bs4 import BeautifulSoup, NavigableString, Tag


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def runs(node, fmt=None):
    fmt = dict(fmt or {})
    out = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            raw = str(ch)
            core = " ".join(raw.split())
            if core:
                t = (" " if raw[:1].isspace() else "") + core + (" " if raw[-1:].isspace() else "")
            else:
                t = " " if raw else ""
            if t:
                out.append(dict(text=t, **fmt))
        elif isinstance(ch, Tag):
            f2 = dict(fmt)
            if ch.name in ("b", "strong"):
                f2["bold"] = True
            elif ch.name in ("i", "em"):
                f2["italics"] = True
            elif ch.name == "sub":
                f2["subScript"] = True
            elif ch.name == "sup":
                f2["superScript"] = True
            elif ch.name == "code":
                f2["mono"] = True
            elif ch.name == "span" and "tag" in (ch.get("class") or []):
                f2["bold"] = True; f2["small"] = True
            elif ch.name == "br":
                out.append(dict(text="", br=True)); continue
            out += runs(ch, f2)
    # normaliza espacios entre runs
    clean = []
    for r in out:
        if clean and r.get("text", "").startswith(" ") and clean[-1].get("text", "").endswith(" "):
            r["text"] = r["text"].lstrip()
        clean.append(r)
    return clean


def walk(el, blocks, base):
    for ch in el.children:
        if not isinstance(ch, Tag):
            continue
        cls = ch.get("class") or []
        if ch.name == "h1":
            blocks.append(dict(type="title", runs=runs(ch)))
        elif ch.name in ("h2", "h3"):
            blocks.append(dict(type=ch.name, runs=runs(ch)))
        elif ch.name == "p":
            blocks.append(dict(type="p", runs=runs(ch), lede=("lede" in cls), kicker=("kicker" in cls)))
        elif ch.name in ("ul", "ol"):
            if "toc" in cls:
                continue
            blocks.append(dict(type="list", ordered=(ch.name == "ol"), items=[runs(li) for li in ch.find_all("li", recursive=False)]))
        elif ch.name == "pre":
            blocks.append(dict(type="pre", lines=ch.get_text().split("\n")))
        elif ch.name == "figure":
            img = ch.find("img"); cap = ch.find("figcaption")
            src = os.path.join(base, img["src"])
            w, h = png_size(src)
            blocks.append(dict(type="figure", src=src, w=w, h=h, caption=runs(cap) if cap else []))
        elif ch.name == "div" and "tbl" in cls:
            t = ch.find("table")
            head = [runs(th) for th in t.find("thead").find_all("th")]
            body = [[runs(td) for td in tr.find_all("td")] for tr in t.find("tbody").find_all("tr")]
            blocks.append(dict(type="table", head=head, rows=body))
        elif ch.name == "div" and "findings" in cls:
            items = []
            for f in ch.find_all("div", class_="finding"):
                items.append(dict(n=f.find(class_="n").get_text(" ", strip=True), t=runs(f.find(class_="t")),
                                  s=f.find(class_="s").get_text(" ", strip=True) if f.find(class_="s") else ""))
            blocks.append(dict(type="findings", items=items))
        elif ch.name == "div" and "note" in cls:
            blocks.append(dict(type="note", runs=runs(ch)))
        elif ch.name == "div" and "meta" in cls:
            blocks.append(dict(type="p", runs=[dict(text="  ·  ".join(s.get_text(strip=True) for s in ch.find_all("span")), small=True)]))
        else:
            walk(ch, blocks, base)


if __name__ == "__main__":
    src = sys.argv[1]; out = sys.argv[2]
    soup = BeautifulSoup(open(src, encoding="utf-8").read(), "html.parser")
    blocks = []
    walk(soup.find("main"), blocks, os.path.dirname(os.path.abspath(src)))
    json.dump(blocks, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(len(blocks), "bloques")
