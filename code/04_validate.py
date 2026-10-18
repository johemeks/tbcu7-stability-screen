"""04_validate.py: score each database against what labs actually observed.

Plain-language note: for every lab observation in data/curated/observations.csv
this script asks each database "would you have said this phase can form?"
and records hit, miss, false alarm, or "no data". It also checks whether each
database gets the known stable Sm-Fe compounds right, and compares computed
iron magnetic moments with measured ones. Outputs (data/processed/):
  validation_matrix.csv     one row per observation x database
  db_scorecard.csv          one row per database (the headline table)
  hull_fidelity.csv         known stable Sm-Fe compounds vs each database
  magnetization_comparison.csv
  sensitivity.csv           scorecard at 25, 50 and 100 meV/atom windows
  qa_report.txt, stats.json
Run: python code/04_validate.py
"""
import csv
import json
import math
from collections import defaultdict

from common import (CUR, PROC, REPORT, DATABASES, TAU_ACCESSIBLE, TAU_SENSITIVITY, TOL_ON_HULL, COMP_WINDOW,
                    T_QUENCH, KB, MU_B, MU_0, delta_from_x, s_conf_per_atom)
import importlib.util

spec = importlib.util.spec_from_file_location("proxy", str(PROC.parents[1] / "code" / "03_proxy.py"))
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)

TB_FAMILIES = proxy.TB_FAMILIES
FAMILY_MAP = {"TbCu7": "TbCu7", "ThMn12": "ThMn12", "Th2Zn17": "2:17", "Th2Ni17": "2:17", "CaCu5": "CaCu5",
              "Sm5Fe17": "Sm5Fe17", "omega": "omega", "MgCu2": "MgCu2"}


def comp_distance(obs, r):
    fs, fm = obs["phase_frac_Sm"], obs["phase_frac_M"]
    ff = 1 - fs - fm
    rs, rm = r["frac_Sm"], r["frac_M"]
    rf = 1 - rs - rm
    return max(abs(fs - rs), abs(fm - rm), abs(ff - rf))


def metric_for(obs, db, rows, models):
    """Return (metric eV/atom, coverage label, entry/description, distance)."""
    fam = FAMILY_MAP.get(obs["test_family"])
    sys_ = obs["system"]
    pool = [r for r in rows if r["database"] == db and r["ehull_eV_atom"] is not None]
    cands = []
    if fam == "TbCu7":
        if sys_ != "Sm-Fe":
            for r in pool:
                if r["system"] == sys_ and r["family"] in TB_FAMILIES:
                    d = comp_distance(obs, r)
                    if d <= COMP_WINDOW:
                        cands.append((r["ehull_eV_atom"], "ternary approximant", f"{r['entry_id']} {r['formula']} ({r['family']})", d))
        p = proxy.tbcu7_binary_proxy(models.get(db), obs["phase_x_TM_per_R"])
        if p is not None:
            label = "binary-path model" if sys_ == "Sm-Fe" else "binary-path model (M ignored)"
            cands.append((p["dE"], label, f"ordered-parent envelope at x={obs['phase_x_TM_per_R']:g}", obs["phase_frac_M"]))
    elif fam in ("ThMn12", "2:17", "CaCu5", "Sm5Fe17", "MgCu2", "omega"):
        for r in pool:
            if r["family"] != fam or r["system"] not in (sys_, "Sm-Fe"):
                continue
            d = comp_distance(obs, r)
            if d > COMP_WINDOW:
                continue
            if r["system"] == "Sm-Fe" and sys_ != "Sm-Fe":
                label = "binary entry (M ignored)"
            else:
                label = "ternary entry" if sys_ != "Sm-Fe" else "binary entry"
            cands.append((r["ehull_eV_atom"], label, f"{r['entry_id']} {r['formula']}", d))
    if not cands:
        return None, "none", "", None
    best = min(cands, key=lambda c: c[0])
    return best


def decide(outcome, metric, tau):
    if metric is None:
        return "no data"
    if outcome == "formed":
        return "hit" if metric <= tau else "miss"
    if outcome == "not_formed":
        return "correct reject" if metric > tau else "false alarm"
    return "n/a"


def main():
    rows = proxy.load()
    models = proxy.binary_models(rows)
    obs = list(csv.DictReader(open(CUR / "observations.csv")))
    for o in obs:
        for k in ("phase_x_TM_per_R", "phase_frac_Sm", "phase_frac_M"):
            o[k] = float(o[k]) if o[k] not in ("", None) else None
    scored = [o for o in obs if o["scored"] == "yes"]

    # ---- validation matrix
    vm = []
    for o in scored:
        for db in DATABASES:
            m, cov, ent, dist = metric_for(o, db, rows, models)
            rec = {"obs_id": o["obs_id"], "system": o["system"], "test_family": o["test_family"], "test_outcome": o["test_outcome"],
                   "process": o["process"], "doi": o["doi"], "database": db,
                   "metric_eV_atom": "" if m is None else round(m, 4), "coverage": cov, "matched": ent,
                   "comp_distance": "" if dist is None else round(dist, 3)}
            if o["test_family"] == "TbCu7" and m is not None:
                ts = KB * T_QUENCH * s_conf_per_atom(o["phase_x_TM_per_R"])
                rec["metric_minus_TS_conf"] = round(m - ts, 4)
            else:
                rec["metric_minus_TS_conf"] = ""
            for tau in TAU_SENSITIVITY:
                rec[f"verdict_{int(tau*1000)}meV"] = decide(o["test_outcome"], m, tau)
            vm.append(rec)
    cols = list(vm[0].keys())
    with open(PROC / "validation_matrix.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(vm)

    # ---- hull fidelity (known equilibrium Sm-Fe compounds; Katter 1991 abstract lists Sm2Fe17, SmFe3, SmFe2)
    eq = [("Sm2Fe17", "Fe17Sm2", "2:17"), ("SmFe3", "Fe3Sm", "PuNi3"), ("SmFe2", "Fe2Sm", "MgCu2")]
    hf = []
    for db in DATABASES:
        for name, formula, fam in eq:
            c = [r for r in rows if r["database"] == db and r["formula"] == formula and r["ehull_eV_atom"] is not None]
            if not c:
                hf.append([db, name, "", "", "no entry"])
                continue
            b = min(c, key=lambda r: r["ehull_eV_atom"])
            hf.append([db, name, b["entry_id"], b["ehull_eV_atom"], "pass" if b["ehull_eV_atom"] <= TOL_ON_HULL else "fail"])
    with open(PROC / "hull_fidelity.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["database", "known_stable_phase", "best_entry", "ehull_eV_atom", f"verdict_(<= {TOL_ON_HULL} eV/atom)"])
        w.writerows(hf)

    # binary hull shape: does the DB have ANY stable Sm-Fe compound?
    stable_any = {}
    for db in DATABASES:
        m = models.get(db)
        if m is None:
            stable_any[db] = None
        else:
            stable_any[db] = [f"{p[0]:.3f}" for p in m["hull"] if 0 < p[0] < 1]

    # ---- magnetization comparison (O01 Katter 1991 TbCu7 SmFe9; O12 Zheng 2019)
    def kuzmin(tau, s, p=2.5):
        return (1 - s * tau ** 1.5 - (1 - s) * tau ** p) ** (1 / 3)

    mag = []
    o1 = next(o for o in obs if o["obs_id"] == "O01")
    a, c = float(o1["lattice_a_A"]), float(o1["lattice_c_A"])
    V = math.sqrt(3) / 2 * a * a * c * 1e-30
    x = 9.0
    d = delta_from_x(x)
    n_fe = 5 + 2 * d
    js = float(o1["Js_T"])
    mu_fe_rt = js / MU_0 * V / MU_B / n_fe
    tau = float(o1["Js_temp_K"]) / float(o1["Tc_K"])
    m0_lo, m0_hi = mu_fe_rt / kuzmin(tau, 0.3), mu_fe_rt / kuzmin(tau, 0.7)
    for db in DATABASES:
        mdl = models.get(db)
        val, note = None, ""
        if mdl is not None:
            p = proxy.tbcu7_binary_proxy(mdl, x)
            if p:
                ends = []
                for fx in p["bracket"]:
                    e = [r for r in mdl["fam"] if abs(r["frac_Fe"] - fx) < 1e-3 and r["m_Fe_muB"] is not None]
                    ends.append(min(e, key=lambda r: r["eform_eV_atom"]) if e else None)
                if all(ends):
                    f = x / (1 + x)
                    f1, f2 = p["bracket"]
                    w_ = 0 if f2 == f1 else (f - f1) / (f2 - f1)
                    val = (1 - w_) * ends[0]["m_Fe_muB"] + w_ * ends[1]["m_Fe_muB"]
                    note = f"interpolated between {ends[0]['formula']} ({ends[0]['m_Fe_muB']}) and {ends[1]['formula']} ({ends[1]['m_Fe_muB']})"
                else:
                    note = "database exposes no per-site or per-cell moments"
        else:
            note = "no Sm-Fe entries"
        mag.append({"obs_id": "O01", "database": db, "phase": "TbCu7 SmFe9", "computed_m_Fe_muB_0K": "" if val is None else round(val, 3),
                    "measured_m_Fe_muB_RT": round(mu_fe_rt, 3), "measured_m_Fe_muB_0K_est_low": round(m0_lo, 3),
                    "measured_m_Fe_muB_0K_est_high": round(m0_hi, 3),
                    "ratio_computed_to_0K_mid": "" if val is None else round(val / ((m0_lo + m0_hi) / 2), 3), "note": note})
        # O12: whole-ribbon average incl. alpha-Fe, temperature not stated
        mag.append({"obs_id": "O12", "database": db, "phase": "TbCu7 + alpha-Fe ribbon (SmFe12 nominal)",
                    "computed_m_Fe_muB_0K": "" if val is None else round(val, 3), "measured_m_Fe_muB_RT": 1.75,
                    "measured_m_Fe_muB_0K_est_low": "", "measured_m_Fe_muB_0K_est_high": "",
                    "ratio_computed_to_0K_mid": "", "note": "sample average, includes alpha-Fe; measurement temperature not stated in abstract"})
    with open(PROC / "magnetization_comparison.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(mag[0].keys()))
        w.writeheader()
        w.writerows(mag)

    # ---- scorecard
    sc, sens = [], []
    for tau in TAU_SENSITIVITY:
        key = f"verdict_{int(tau*1000)}meV"
        for db in DATABASES:
            v = [r for r in vm if r["database"] == db]
            cnt = defaultdict(int)
            for r in v:
                cnt[r[key]] += 1
            formed = [r for r in v if r["test_outcome"] == "formed"]
            covered_formed = [r for r in formed if r[key] != "no data"]
            native = [r for r in v if r["coverage"] in ("ternary approximant", "ternary entry", "binary entry")]
            row = {"database": db, "tau_eV_atom": tau, "n_observations": len(v),
                   "n_with_any_prediction": sum(1 for r in v if r[key] != "no data"),
                   "n_with_native_entry": len(native),
                   "hits": cnt["hit"], "misses": cnt["miss"], "false_alarms": cnt["false alarm"],
                   "correct_rejects": cnt["correct reject"], "no_data": cnt["no data"],
                   "hit_rate_when_covered": round(cnt["hit"] / len(covered_formed), 3) if covered_formed else "",
                   "coverage_rate": round(sum(1 for r in v if r[key] != "no data") / len(v), 3)}
            hfd = [h for h in hf if h[0] == db]
            row["hull_fidelity_pass"] = sum(1 for h in hfd if h[4] == "pass")
            row["hull_fidelity_tested"] = sum(1 for h in hfd if h[4] in ("pass", "fail"))
            row["stable_SmFe_compounds_on_hull"] = "" if stable_any[db] is None else len(stable_any[db])
            sens.append(row)
            if tau == TAU_ACCESSIBLE:
                sc.append(row)
    with open(PROC / "db_scorecard.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sc[0].keys()))
        w.writeheader()
        w.writerows(sc)
    with open(PROC / "sensitivity.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sens[0].keys()))
        w.writeheader()
        w.writerows(sens)

    # ---- stats + QA
    path = list(csv.DictReader(open(PROC / "tbcu7_binary_path.csv")))
    p9 = {r["database"]: r for r in path if abs(float(r["x_TM_per_R"]) - 9.0) < 1e-6}
    st = {
        "n_observations_total": len(obs), "n_observations_scored": len(scored),
        "n_systems_scored": len({o["system"] for o in scored}),
        "systems_scored": sorted({o["system"] for o in scored}),
        "core_M_without_any_observation": sorted(set(["Co", "Ti", "V", "Zr", "Nb", "Cu", "Si", "Ga", "Al", "Mo", "Cr", "Mn", "Hf"])
                                                 - {o["M"] for o in scored}),
        "n_computed_entries": len(rows),
        "entries_by_db": {db: sum(1 for r in rows if r["database"] == db) for db in DATABASES},
        "tau_eV_atom": TAU_ACCESSIBLE, "comp_window": COMP_WINDOW, "T_quench_K": T_QUENCH,
        "tbcu7_proxy_x9_meV": {db: (round(float(p9[db]["dE_proxy_eV_atom"]) * 1000, 1) if p9.get(db) and p9[db]["dE_proxy_eV_atom"] else None) for db in DATABASES},
        "TS_conf_x9_meV": round(KB * T_QUENCH * s_conf_per_atom(9.0) * 1000, 1),
        "stable_SmFe_compounds_on_hull": {db: v for db, v in stable_any.items()},
        "hull_fidelity": {db: [h[1] + ":" + h[4] + ("" if h[3] == "" else f"({h[3]})") for h in hf if h[0] == db] for db in DATABASES},
        "scorecard": {r["database"]: {k: r[k] for k in ("hits", "misses", "false_alarms", "correct_rejects", "no_data", "coverage_rate", "hit_rate_when_covered", "n_with_native_entry")} for r in sc},
        "magnetization_O01": {"measured_m_Fe_RT": round(mu_fe_rt, 3), "measured_m_Fe_0K_range": [round(m0_lo, 3), round(m0_hi, 3)],
                              "computed": {r["database"]: r["computed_m_Fe_muB_0K"] for r in mag if r["obs_id"] == "O01"}},
    }
    # discrimination: Sm-Fe phases with different observed fates
    disc = {}
    for db in DATABASES:
        mdl = models.get(db)
        if mdl is None:
            disc[db] = None
            continue
        def best_e(formula):
            c = [r["ehull_eV_atom"] for r in mdl["entries"] if r["formula"] == formula]
            return min(c) if c else None
        e217, e112 = best_e("Fe17Sm2"), best_e("Fe12Sm")
        p = proxy.tbcu7_binary_proxy(mdl, 9.0)
        etb = p["dE"] if p else None
        vals = [v for v in (e217, etb, e112) if v is not None]
        disc[db] = {"Sm2Fe17_stable_meV": None if e217 is None else round(e217 * 1000, 1),
                    "TbCu7_x9_metastable_meV": None if etb is None else round(etb * 1000, 1),
                    "SmFe12_not_formed_by_RS_meV": None if e112 is None else round(e112 * 1000, 1),
                    "spread_meV": round((max(vals) - min(vals)) * 1000, 1) if len(vals) > 1 else None,
                    "Sm2Fe17_ranked_below_TbCu7": None if (e217 is None or etb is None) else e217 < etb}
    st["discrimination"] = disc
    with open(PROC / "discrimination.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["database", "phase", "lab_outcome", "ehull_meV_atom", "spread_meV_atom"])
        for db, v in disc.items():
            if not v:
                continue
            for k, ph, out in [("Sm2Fe17_stable_meV", "Sm2Fe17", "stable (equilibrium)"),
                               ("TbCu7_x9_metastable_meV", "TbCu7 SmFe9 (proxy)", "forms by melt spinning"),
                               ("SmFe12_not_formed_by_RS_meV", "SmFe12", "does not form by melt spinning")]:
                w.writerow([db, ph, out, v[k], v["spread_meV"]])
    REPORT.mkdir(exist_ok=True)
    json.dump(st, open(REPORT / "stats.json", "w"), indent=2)

    qa = []
    qa.append("QA REPORT - TbCu7 stability screen (generated by code/04_validate.py)")
    qa.append("Plain-language note: this file lists counts and checks. Read it before trusting any number.\n")
    qa.append(f"Computed entries in screen: {len(rows)}  by database: {st['entries_by_db']}")
    qa.append(f"Observations: {len(obs)} curated, {len(scored)} scored, systems scored: {st['systems_scored']}")
    qa.append(f"Core M with no scored observation: {st['core_M_without_any_observation']}")
    hr = list(csv.DictReader(open(PROC / "hull_recheck.csv")))
    mx = max(hr, key=lambda r: float(r["abs_diff"]))
    qa.append(f"Hull re-check (our Sm-Fe hull vs database-reported ehull): {len(hr)} entries, max |diff| = {mx['abs_diff']} eV/atom ({mx['database']} {mx['formula']})")
    bad = [r for r in hr if float(r["abs_diff"]) > 0.005]
    qa.append(f"  entries with |diff| > 5 meV/atom: {len(bad)}")
    qa.append(f"Validation matrix rows: {len(vm)} (= {len(scored)} observations x {len(DATABASES)} databases)")
    qa.append("Range checks: all metrics in [0, 2] eV/atom: " + str(all(0 <= float(r['metric_eV_atom']) <= 2 for r in vm if r['metric_eV_atom'] != '')))
    qa.append("\nNamed spot checks (verify by hand against the source links in docs/VERIFY_CHECKLIST.md):")
    for db, eid in [("MP", "mp-1426"), ("MP", "mp-1566"), ("JARVIS", "JVASP-85844"), ("NOMAD-Alexandria", "agm005529553"), ("OQMD", "oqmd-4818030"), ("GNoME", "82e7ee41aa")]:
        r = next((r for r in rows if r["database"] == db and r["entry_id"] == eid), None)
        if r:
            qa.append(f"  {db} {eid} {r['formula']}: ehull={r['ehull_eV_atom']} eform={r['eform_eV_atom']} m_Fe={r['m_Fe_muB']}")
    qa.append("\nScorecard at tau = 50 meV/atom:")
    for r in sc:
        qa.append("  " + ", ".join(f"{k}={r[k]}" for k in ("database", "hits", "misses", "false_alarms", "correct_rejects", "no_data", "hull_fidelity_pass", "hull_fidelity_tested")))
    open(PROC / "qa_report.txt", "w").write("\n".join(qa) + "\n")
    print("\n".join(qa))


if __name__ == "__main__":
    main()
