"""English versions of the figures (FIG_LANG=en).

figuras.save() and superestructura_dibujo.text() call tr() on every text of a figure when FIG_LANG=en, and the
figures go to figs/en/. Strings are looked up whole in fig_en_dict.json (Spanish -> English); numbers written the
Spanish way (decimal comma, space as thousands separator) are converted afterwards. Strings with no entry are
appended to figs/en/_missing.txt so the dictionary can be completed and the figures run again.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ON = os.environ.get("FIG_LANG", "").lower() == "en"
OUT = os.path.join(HERE, "figs", "en")
_DICT_P = os.path.join(HERE, "fig_en_dict.json")
_D = json.load(open(_DICT_P, encoding="utf-8")) if os.path.exists(_DICT_P) else {}
_MISSING = os.path.join(OUT, "_missing.txt")
_seen = set()

# words and phrases replaced inside strings that have no whole-string entry (longest first)
_W = sorted(_D.get("__phrases__", {}).items(), key=lambda kv: -len(kv[0]))


_MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def months():
    """Month abbreviations in the language of the figures (Spanish 'mar' is March here, Tuesday in days())."""
    return list(_MON if ON else _MES)


def days():
    return list(_DAYS if ON else _DIAS)


def month_initials():
    return list("JFMAMJJASOND" if ON else "EFMAMJJASOND")


def figdir(base):
    """figs/ or figs/en/ depending on FIG_LANG."""
    if ON:
        os.makedirs(OUT, exist_ok=True)
        return OUT
    return base


def _numbers(s):
    s = re.sub(r"(?<=\d),(?=\d)", ".", s)                       # 0,36 -> 0.36
    s = re.sub(r"(?<=\d)[   ](?=\d{3}\b)", ",", s)      # 6 146 -> 6,146
    return s


def tr(s):
    if not ON or not isinstance(s, str) or not s.strip():
        return s
    if s in _D:
        return _D[s]
    if re.fullmatch(r"[\s\d.,−\-+%×/()]*", s):
        return _numbers(s)
    t = s
    for a, b in _W:
        t = t.replace(a, b)
    if s not in _seen:
        _seen.add(s)
        os.makedirs(OUT, exist_ok=True)
        with open(_MISSING, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    return _numbers(t)


def translate_fig(fig):
    """Translate every text of a matplotlib figure in place (titles, labels, legends, annotations, tick labels)."""
    if not ON:
        return
    import matplotlib.text as mtext
    import matplotlib.ticker as mticker
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for which in ("major", "minor"):
                fmt = axis.get_major_formatter() if which == "major" else axis.get_minor_formatter()
                if isinstance(fmt, mticker.FixedFormatter):
                    fmt.seq = [tr(x) for x in fmt.seq]
                elif isinstance(fmt, mticker.FuncFormatter):
                    f0 = fmt.func
                    fmt.func = (lambda f: (lambda x, pos=None: tr(f(x, pos))))(f0)
    for t in fig.findobj(mtext.Text):
        s = t.get_text()
        if s:
            t.set_text(tr(s))
