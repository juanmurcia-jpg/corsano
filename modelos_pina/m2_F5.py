"""F5 (rediseñado): asignación del hub bajo escasez. Se eleva la producción de etanol hasta agotar el jugo de
cáscara y se observa qué corrientes completa el óptimo según la inhibición del hidrolizado (alpha)."""
import json
import m2_experimentos as ex
d = json.load(open(f"{ex.RES}/m2_all.json"))
PRs = [40, 100, 150, 180, 210, 240]
alphas = [0.0, 0.3, 0.6]
rs = ex.run([dict(PR=pr, alpha=a, _tag=(a, pr)) for a in alphas for pr in PRs])
d["F5"] = [ex.slim(r) for r in rs]
for r in rs:
    print("F5", r["tag"], r.get("ok"), round(r.get("TAC", 0)), {k: round(v) for k, v in r.get("use_yr", {}).items()})
json.dump(d, open(f"{ex.RES}/m2_all.json", "w"), default=float)
