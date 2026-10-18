"""03_proxy.py: build the stability proxy table.

Plain-language note: no public database contains the TbCu7 structure itself,
because it is a disordered (randomly mixed) crystal and these databases only
compute perfectly ordered ones. This script estimates how far above the
"stable line" (the convex hull) a TbCu7 phase would sit, using its ordered
relatives (CaCu5-type SmFe5, 2:17-type Sm2Fe17, 3:29, ThMn12-type SmFe12)
from each database. Output files:
  data/processed/stability_proxy_table.csv   best entry per database, system and structure family
  data/processed/tbcu7_binary_path.csv       the TbCu7 estimate along the Sm-Fe composition line
  data/processed/hull_recheck.csv            our recomputed Sm-Fe hull vs each database's own number
Run: python code/03_proxy.py
"""
import csv
from collections import defaultdict

from common import PROC, DATABASES, T_QUENCH, KB, delta_from_x, s_conf_per_atom

TB_FAMILIES = ("CaCu5", "2:17", "3:29", "ThMn12", "TbCu7-approximant")


def lower_hull(points):
    """Lower convex hull of (x, y) points, sorted by x (monotone chain)."""
    pts = sorted(set(points))
    hull = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def interp(hull, x):
    for (x1, y1), (x2, y2) in zip(hull, hull[1:]):
        if x1 - 1e-12 <= x <= x2 + 1e-12:
            w = 0 if x2 == x1 else (x - x1) / (x2 - x1)
            return y1 + w * (y2 - y1), (x1, x2)
    return None, None


def load():
    rows = list(csv.DictReader(open(PROC / "computed_entries.csv")))
    for r in rows:
        for k in ("frac_Sm", "frac_Fe", "frac_M", "ehull_eV_atom", "eform_eV_atom", "x_TM_per_R"):
            r[k] = float(r[k]) if r[k] not in ("", None) else None
        r["m_Fe_muB"] = float(r["m_Fe_muB"]) if r["m_Fe_muB"] not in ("", None) else None
    return rows


def binary_models(rows):
    """Per database: Sm-Fe hull and TbCu7-family envelope in (frac_Fe, E_form) space."""
    out = {}
    for db in DATABASES:
        b = [r for r in rows if r["database"] == db and r["system"] == "Sm-Fe" and r["eform_eV_atom"] is not None]
        if not b:
            out[db] = None
            continue
        pts = [(r["frac_Fe"], r["eform_eV_atom"]) for r in b] + [(0.0, 0.0), (1.0, 0.0)]
        hull = lower_hull(pts)
        fam = [r for r in b if r["family"] in TB_FAMILIES]
        env = lower_hull([(r["frac_Fe"], r["eform_eV_atom"]) for r in fam]) if fam else []
        out[db] = {"hull": hull, "env": env, "entries": b, "fam": fam}
    return out


def tbcu7_binary_proxy(model, x):
    """Enthalpy (eV/atom) of the TbCu7 ordered-parent envelope above the hull at TM/R = x."""
    if model is None or len(model["env"]) == 0:
        return None
    f = x / (1 + x)
    e_env, br = interp(model["env"], f)
    e_hull, _ = interp(model["hull"], f)
    if e_env is None:
        return None
    return {"f_Fe": f, "E_env": e_env, "E_hull": e_hull, "dE": e_env - e_hull, "bracket": br}


def main():
    rows = load()
    models = binary_models(rows)

    # 1) hull re-check for every binary entry
    with open(PROC / "hull_recheck.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["database", "entry_id", "formula", "family", "eform_eV_atom", "ehull_reported", "ehull_recomputed", "abs_diff"])
        for db, m in models.items():
            if m is None:
                continue
            for r in m["entries"]:
                eh, _ = interp(m["hull"], r["frac_Fe"])
                rec = r["eform_eV_atom"] - eh
                w.writerow([db, r["entry_id"], r["formula"], r["family"], r["eform_eV_atom"], r["ehull_eV_atom"],
                            round(rec, 4), round(abs(rec - r["ehull_eV_atom"]), 4)])

    # 2) TbCu7 path along Sm-Fe
    grid = [5.0, 6.0, 7.0, 8.0, 8.5, 9.0, 9.5, 29 / 3, 10.0, 11.0, 12.0]
    with open(PROC / "tbcu7_binary_path.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["database", "x_TM_per_R", "delta_dumbbell", "frac_Fe", "E_envelope_eV_atom", "E_hull_eV_atom",
                    "dE_proxy_eV_atom", "TS_conf_eV_atom_at_T", "dG_proxy_eV_atom", "T_K", "bracket_frac_Fe"])
        for db in DATABASES:
            for x in grid:
                p = tbcu7_binary_proxy(models.get(db), x)
                if p is None:
                    w.writerow([db, round(x, 3), round(delta_from_x(x), 4), round(x / (1 + x), 4), "", "", "", "", "", T_QUENCH,
                                "no Sm-Fe TbCu7-family entries"])
                    continue
                ts = KB * T_QUENCH * s_conf_per_atom(x)
                w.writerow([db, round(x, 3), round(delta_from_x(x), 4), round(p["f_Fe"], 4), round(p["E_env"], 4),
                            round(p["E_hull"], 4), round(p["dE"], 4), round(ts, 4), round(p["dE"] - ts, 4), T_QUENCH,
                            f"{p['bracket'][0]:.3f}-{p['bracket'][1]:.3f}"])

    # 3) Stability proxy table: best entry per (database, system, family)
    systems = sorted({r["system"] for r in rows})
    fams = ["CaCu5", "2:17", "3:29", "ThMn12", "TbCu7-approximant", "PuNi3", "Sm5Fe17", "MgCu2"]
    best = {}
    for r in rows:
        if r["family"] not in fams or r["ehull_eV_atom"] is None:
            continue
        k = (r["database"], r["system"], r["family"])
        if k not in best or r["ehull_eV_atom"] < best[k]["ehull_eV_atom"]:
            best[k] = r
    count = defaultdict(int)
    for r in rows:
        count[(r["database"], r["system"], r["family"])] += 1
    with open(PROC / "stability_proxy_table.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["system", "family", "database", "n_entries", "best_entry_id", "best_formula", "x_TM_per_R", "R_site",
                    "frac_M", "ehull_eV_atom", "eform_eV_atom", "m_Fe_muB", "within_50meV", "on_hull_10meV", "source_url"])
        for s in systems:
            for f in fams:
                for db in DATABASES:
                    k = (db, s, f)
                    if k in best:
                        b = best[k]
                        w.writerow([s, f, db, count[k], b["entry_id"], b["formula"], b["x_TM_per_R"], b["R_site"], b["frac_M"],
                                    b["ehull_eV_atom"], b["eform_eV_atom"], "" if b["m_Fe_muB"] is None else b["m_Fe_muB"],
                                    b["ehull_eV_atom"] <= 0.050, b["ehull_eV_atom"] <= 0.010, b["source_url"]])
        # add the TbCu7 binary-path estimate at SmFe9 (x = 9) as its own rows
        for db in DATABASES:
            p = tbcu7_binary_proxy(models.get(db), 9.0)
            if p:
                ts = KB * T_QUENCH * s_conf_per_atom(9.0)
                w.writerow(["Sm-Fe", "TbCu7 proxy (x=9, ordered-parent envelope)", db, "", "", "SmFe9 (model)", 9.0, "Sm", 0,
                            round(p["dE"], 4), round(p["E_env"], 4), "", p["dE"] <= 0.050, p["dE"] <= 0.010,
                            f"envelope of parents; -T*S_conf at {T_QUENCH:.0f} K would subtract {ts:.4f} eV/atom"])
    print("wrote stability_proxy_table.csv, tbcu7_binary_path.csv, hull_recheck.csv")
    for db in DATABASES:
        p = tbcu7_binary_proxy(models.get(db), 9.0)
        print(db, None if p is None else round(p["dE"], 4))


if __name__ == "__main__":
    main()
