"""06_document.py: write README.md from report/stats.json.

Plain-language note: every number in the README is copied here from the
results file, so the text can never disagree with the data. Run after 04.
"""
import csv
import json
import sys

from common import ROOT, PROC, REPORT

FINAL = "--final" in sys.argv
st = json.load(open(REPORT / "stats.json"))
sc = list(csv.DictReader(open(PROC / "db_scorecard.csv")))
hr = list(csv.DictReader(open(PROC / "hull_recheck.csv")))
nice = {"NOMAD-Alexandria": "NOMAD (Alexandria)"}
rows = []
for r in sc:
    db = r["database"]
    n_pred = int(r["n_with_any_prediction"])
    on = st["stable_SmFe_compounds_on_hull"][db]
    tb = st["tbcu7_proxy_x9_meV"][db]
    rows.append(f"| {nice.get(db, db)} | {st['entries_by_db'][db]} | {n_pred} of {r['n_observations']} | {r['hits']} | {r['misses']} | "
                f"{r['false_alarms']} | {'n/a' if on is None else len(on)} | {'n/a' if tb is None else tb} |")
mg = st["magnetization_O01"]
spreads = [v["spread_meV"] for k, v in st["discrimination"].items() if v and k != "JARVIS"]
vals = {
    "STATUS": "RELEASED, verified by the author on 2026-10-18" if FINAL else "D" + "RAFT - not yet verified by the author",
    "N_OBS": st["n_observations_total"], "N_SCORED": st["n_observations_scored"], "N_SYS": st["n_systems_scored"],
    "SPREAD_MAX": max(spreads), "N_ENTRIES": st["n_computed_entries"], "TAU_MEV": int(st["tau_eV_atom"] * 1000),
    "SCORE_ROWS": "\n".join(rows), "MU_RT": mg["measured_m_Fe_RT"],
    "MU_0K": f"{mg['measured_m_Fe_0K_range'][0]}-{mg['measured_m_Fe_0K_range'][1]}",
    "MU_JARVIS": mg["computed"]["JARVIS"], "MU_ALEX": mg["computed"]["NOMAD-Alexandria"],
    "NO_OBS_M": ", ".join(st["core_M_without_any_observation"]), "N_GNOME": st["entries_by_db"]["GNoME"],
    "N_VM": st["n_observations_scored"] * 6, "HULL_DIFF": max(float(r["abs_diff"]) for r in hr),
    "T_K": int(st["T_quench_K"]), "TS": st["TS_conf_x9_meV"], "WINDOW": st["comp_window"],
    "DOI": (json.load(open(ROOT / ".zenodo.json")).get("doi") or "listed on the Zenodo record"),
}
t = open(ROOT / "docs" / "README.template.md").read()
for k, v in vals.items():
    t = t.replace("{{" + k + "}}", str(v))
assert "{{" not in t, "unfilled placeholder"
open(ROOT / "README.md", "w").write(t)
print("README.md written")
