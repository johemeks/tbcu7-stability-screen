"""02_build.py: merge every database pull into one table.

Plain-language note: each database stores its numbers differently. This
script puts all of them into one spreadsheet-like file,
data/processed/computed_entries.csv, with the same columns for every
database. You do not need to edit it. Run: python code/02_build.py
"""
import csv
import json

from common import RAW, PROC, CORE_M, parse_formula, fractions, family_of, tm_per_r

SG_NUM = {"P6/mmm": 191, "R-3m": 166, "P63/mmc": 194, "I4/mmm": 139, "Cmcm": 63, "Cmmm": 65,
          "Immm": 71, "Fd-3m": 227, "Fm-3m": 225, "F-43m": 216, "Pm-3m": 221, "P4/mmm": 123,
          "Pmma": 51, "Pbcm": 57, "Pnma": 62, "R-3c": 167, "C2/c": 15, "Cmca": 64, "P-6m2": 187,
          "P42/mnm": 136, "P-3m1": 164, "Amm2": 38, "Imma": 74, "P4/nmm": 129, "P4mm": 99,
          "P21/m": 11, "C2/m": 12, "I4mm": 107, "P4/mnc": 128, "Im-3m": 229, "Pbam": 55, "P63mc": 186, "R-3": 148, "P-62m": 189, "P-3m1": 164}

ALLOWED = {"Sm", "Fe", "Co"} | set(CORE_M)


def system_of(counts):
    els = set(counts)
    if not els <= ALLOWED or "Sm" not in els:
        return None
    if "Fe" not in els:
        return "Sm-Co" if els == {"Sm", "Co"} else None
    others = sorted(els - {"Sm", "Fe"})
    if len(others) > 1:
        return None   # quaternaries are outside the ternary screen
    return "Sm-Fe" if not others else f"Sm-Fe-{others[0]}"


rows = []


def add(db, eid, formula, nsites, sg, ehull, eform, m_fe=None, mag_cell=None, ehull_kind="", note="", url=""):
    c = parse_formula(formula)
    sys_ = system_of(c)
    if sys_ is None:
        return
    fr = fractions(c)
    m_el = [e for e in c if e not in ("Sm", "Fe")]
    m_el = m_el[0] if (sys_.startswith("Sm-Fe-") and m_el) else ""
    rows.append({
        "database": db, "entry_id": eid, "formula": formula, "system": sys_, "M": m_el,
        "frac_Sm": round(fr.get("Sm", 0), 4), "frac_Fe": round(fr.get("Fe", 0), 4),
        "frac_M": round(fr.get(m_el, 0), 4) if m_el else 0.0,
        "nsites": nsites, "sg_number": sg if sg else "",
        "family": family_of(c, sg, nsites),
        "x_TM_per_R": round(tm_per_r(c)[0], 3), "R_site": "+".join(tm_per_r(c)[1]),
        "ehull_eV_atom": ehull, "ehull_kind": ehull_kind,
        "eform_eV_atom": eform, "m_Fe_muB": m_fe if m_fe is not None else "",
        "magnetization_muB_cell": mag_cell if mag_cell is not None else "",
        "note": note, "source_url": url,
    })


# Materials Project (OPTIMADE, _mp_stability GGA/GGA+U mixing scheme)
mp = json.load(open(RAW / "mp_optimade.json"))
for r in mp["data"]:
    eid, f, ns, lat, eh, ef, eh_mix, eh_r2 = r
    add("MP", eid, f, ns, None, eh, ef, ehull_kind="GGA/GGA+U (MP2020 corrections)",
        note=f"GGA/GGA+U/r2SCAN mixed ehull={eh_mix}; r2SCAN ehull={eh_r2}",
        url=f"https://next-gen.materialsproject.org/materials/{eid}")

# JARVIS-DFT (OptB88vdW); magmom per cell; Sm moment not separated
ja = json.load(open(RAW / "jarvis_optimade.json"))
seen = set()
for r in ja["data"]:
    jid, f, ns, spg, spgn, icsd, eh, ef, mo, mz, func = r
    key = (f, spgn, eh)
    dup = key in seen
    seen.add(key)
    c = parse_formula(f)
    n_fe_cell = ns * c.get("Fe", 0) / sum(c.values())
    m_fe = round(mo / n_fe_cell, 3) if n_fe_cell and mo and mo > -9999 else None
    add("JARVIS", jid, f, ns, int(spgn), eh, ef, m_fe=m_fe, mag_cell=mo, ehull_kind="OptB88vdW",
        note="duplicate structure of another JVASP id" if dup else "m_Fe = cell moment / N_Fe (Sm moment assumed 0)",
        url=f"https://www.ctcms.nist.gov/~knc6/jsmol/{jid}.html")

# Alexandria PBE (hosted on NOMAD)
ax = json.load(open(RAW / "nomad_alexandria.json"))
for r in ax["data"]:
    aid, f, ns, sg, eh, ef, mag, mfe, msm, mco = r
    add("NOMAD-Alexandria", "agm" + aid, f, ns, sg, eh, ef, m_fe=mfe, mag_cell=mag, ehull_kind="PBE (Alexandria)",
        note=f"mean m_Sm={msm}" + (f"; mean m_Co={mco}" if mco is not None else ""),
        url=f"https://alexandria.icams.rub.de/pbe/v1/structures/agm{aid}")

# OQMD (binary + ternary); 'stability' = distance to OQMD hull
ob = json.load(open(RAW / "oqmd_smfe_binary.json"))
ot = json.load(open(RAW / "oqmd_ternary.json"))
oq_rows = list(ob["data"])
for k, v in ot["systems"].items():
    if isinstance(v, list):
        oq_rows += v
for r in oq_rows:
    oid, f, ns, proto, sgs, de, st = r
    add("OQMD", "oqmd-" + oid, f, ns, SG_NUM.get(sgs), st, de, ehull_kind="PBE(+U) OQMD",
        note=f"prototype={proto}; spacegroup={sgs}", url=f"https://oqmd.org/materials/entry/{oid}")

# GNoME (decomposition energy vs MP+OQMD hull; <= 0 means on/below hull)
gn = json.load(open(RAW / "gnome.json"))
r2 = {r[0]: r for r in gn["r2scan"]}
for r in gn["summary"]:
    mid, comp, red, els, ns, sgs, sgn, cs, ef, ed = r[:10]
    note = f"GNoME decomposition energy {ed} eV/atom"
    if mid in r2:
        note += f"; r2SCAN decomposition {r2[mid][2]} eV/atom"
    add("GNoME", mid, comp, ns, sgn, max(0.0, ed), ef, ehull_kind="GNoME PBE vs MP+OQMD hull (clipped at 0)",
        note=note, url="gs://gdm_materials_discovery/gnome_data/stable_materials_summary.csv")

cols = list(rows[0].keys())
PROC.mkdir(parents=True, exist_ok=True)
with open(PROC / "computed_entries.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

from collections import Counter
print("rows:", len(rows))
print(Counter(r["database"] for r in rows))
print(Counter((r["database"], r["family"]) for r in rows if r["family"] in ("CaCu5", "2:17", "ThMn12", "TbCu7-approximant", "Sm5Fe17")))
