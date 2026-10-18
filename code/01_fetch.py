"""01_fetch.py: re-download the raw database data.

Plain-language note: this script asks each public database for its Sm-Fe-M
entries and saves the answers in data/raw/. You only need it to REFRESH the
data. The files already in data/raw/ are the exact snapshot used for the
results (retrieved 2026-10-13), so scripts 02-05 rerun without internet.

How the v0.1 snapshot was made: the build environment could not reach the
databases directly, so the same queries below were run from a web browser
(JavaScript fetch against the same URLs) and the responses saved verbatim
into data/raw/*.json. This script reproduces those queries in Python. It
writes to data/raw/refresh_<date>/ so it never overwrites the snapshot.
Status: the query logic mirrors the browser run, but this Python script was
not itself executed in the build environment (no network there).

Usage:
    pip install requests
    python code/01_fetch.py            # all databases
    python code/01_fetch.py --only mp  # one database
Optional: set MP_API_KEY to also pull Materials Project magnetic moments
(the keyless OPTIMADE endpoint does not expose them).
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CORE_M = ["Co", "Ti", "V", "Zr", "Nb", "Cu", "Si", "Ga", "Al", "Mo", "Cr", "Mn", "Hf"]
ALLOWED = set(["Sm", "Fe"] + CORE_M)
TODAY = dt.date.today().isoformat()
OUT = ROOT / "data" / "raw" / f"refresh_{TODAY}"
S = requests.Session()
S.headers["User-Agent"] = "tbcu7-stability-screen/0.1 (research; contact in AUTHORS.json)"


def log(path, url, payload: bytes):
    """Append a provenance line: file, bytes, sha256, url, date."""
    with open(OUT / "PROVENANCE.txt", "a") as fh:
        fh.write(f"{path.name}\t{len(payload)}\t{hashlib.sha256(payload).hexdigest()}\t{url}\t{TODAY}\n")


def optimade_all(base, flt, fields, timeout=120):
    url = f"{base}/structures"
    params = {"filter": flt, "page_limit": 100, "response_fields": fields}
    out = []
    while url:
        r = S.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        out += j.get("data", [])
        nxt = (j.get("links") or {}).get("next")
        url = (nxt if isinstance(nxt, str) else (nxt or {}).get("href")) if nxt else None
        if url:
            url = url.replace("http://", "https://")
        params = None
    return out


def keep(els):
    return set(els) <= ALLOWED


def save(name, obj):
    p = OUT / name
    b = json.dumps(obj).encode()
    p.write_bytes(b)
    return p, b


def fetch_mp():
    base = "https://optimade.materialsproject.org/v1"
    f = "id,chemical_formula_reduced,elements,nsites,lattice_vectors,_mp_stability"
    rows = []
    for flt in ['elements HAS ALL "Sm","Fe" AND nelements<=3', 'elements HAS ALL "Sm","Co" AND nelements=2']:
        for e in optimade_all(base, flt, f):
            a = e["attributes"]
            if not keep(a["elements"]) and "Co" not in a["elements"]:
                continue
            st = a.get("_mp_stability") or {}
            g, m, r2 = st.get("gga_gga+u", {}), st.get("gga_gga+u_r2scan", {}), st.get("r2scan", {})
            rows.append([e["id"], a["chemical_formula_reduced"], a["nsites"], None, g.get("energy_above_hull"),
                         g.get("formation_energy_per_atom"), m.get("energy_above_hull"), r2.get("energy_above_hull")])
    p, b = save("mp_optimade.json", {"source": base, "data": rows})
    log(p, base, b)


def fetch_jarvis():
    base = "https://jarvis.nist.gov/optimade/jarvisdft/v1"
    rows = []
    for flt in ['elements HAS ALL "Sm","Fe"', 'elements HAS ALL "Sm","Co"']:
        for e in optimade_all(base, flt, ""):
            a = e["attributes"]
            if not keep(a["elements"]):
                continue
            rows.append([a["_jarvis_jid"], a["chemical_formula_reduced"], a["nsites"], a["_jarvis_spg_symbol"],
                         a["_jarvis_spg_number"], a["_jarvis_icsd"], a["_jarvis_ehull"], a["_jarvis_formation_energy_peratom"],
                         a["_jarvis_magmom_outcar"], a["_jarvis_magmom_oszicar"], a["_jarvis_func"]])
    p, b = save("jarvis_optimade.json", {"source": base, "data": rows})
    log(p, base, b)


def fetch_alexandria():
    base = "https://alexandria.icams.rub.de/pbe/v1"
    f = ("id,chemical_formula_reduced,elements,nsites,_alexandria_space_group,_alexandria_hull_distance,"
         "_alexandria_formation_energy_per_atom,_alexandria_magnetization,_alexandria_magnetic_moments,species_at_sites")
    rows = []
    for flt in ['elements HAS ALL "Sm","Fe" AND nelements<=3', 'elements HAS ALL "Sm","Co" AND nelements=2']:
        for e in optimade_all(base, flt, f):
            a = e["attributes"]
            if not keep(a["elements"]):
                continue
            mm, sp = a.get("_alexandria_magnetic_moments") or [], a.get("species_at_sites") or []

            def avg(el):
                v = [m for m, s in zip(mm, sp) if s == el]
                return round(sum(v) / len(v), 3) if v else None
            rows.append([e["id"].replace("agm", ""), a["chemical_formula_reduced"], a["nsites"], a["_alexandria_space_group"],
                         a["_alexandria_hull_distance"], a["_alexandria_formation_energy_per_atom"], a["_alexandria_magnetization"],
                         avg("Fe"), avg("Sm"), avg("Co")])
    p, b = save("nomad_alexandria.json", {"source": base, "data": rows})
    log(p, base, b)


def fetch_oqmd():
    base = "https://oqmd.org/optimade"
    f = "chemical_formula_reduced,elements,_oqmd_delta_e,_oqmd_stability,_oqmd_prototype,_oqmd_spacegroup,nsites"
    conv = lambda e: [e["id"], e["attributes"]["chemical_formula_reduced"], e["attributes"]["nsites"], e["attributes"]["_oqmd_prototype"],
                      e["attributes"]["_oqmd_spacegroup"], e["attributes"]["_oqmd_delta_e"], e["attributes"]["_oqmd_stability"]]
    binary = [conv(e) for e in optimade_all(base, 'elements HAS ALL "Sm","Fe" AND nelements=2', f, timeout=300)]
    p, b = save("oqmd_smfe_binary.json", {"source": base, "data": binary})
    log(p, base, b)
    systems = {}
    for m in CORE_M:
        try:
            systems[m] = [conv(e) for e in optimade_all(base, f'elements HAS ALL "Sm","Fe","{m}" AND nelements=3', f, timeout=300)]
        except Exception as exc:  # OQMD is slow; record the failure instead of stopping
            systems[m] = f"FAILED: {exc}"
    systems["Sm-Co binary"] = [conv(e) for e in optimade_all(base, 'elements HAS ALL "Sm","Co" AND nelements=2', f, timeout=300)]
    p, b = save("oqmd_ternary.json", {"source": base, "systems": systems})
    log(p, base, b)


def fetch_aflow():
    base = "https://aflow.org/API/aflux/"
    out = {}
    for q in ["species(Sm),nspecies(2),compound,paging(0),format(json)",
              "species(Sm),nspecies(3),compound,paging(0),format(json)",
              "species(Sm),species(Fe),compound,paging(0),format(json)"]:
        r = S.get(base + "?" + q, timeout=120)
        out[q] = r.json()
    p, b = save("aflow_aflux_raw.json", out)
    log(p, base, b)


def fetch_gnome():
    base = "https://storage.googleapis.com/gdm_materials_discovery/gnome_data/"
    res = {}
    for name in ["stable_materials_summary.csv", "stable_materials_r2scan.csv"]:
        r = S.get(base + name, timeout=600, stream=True)
        r.raise_for_status()
        text = r.content.decode()
        rd = csv.DictReader(io.StringIO(text))
        keep_rows = []
        for row in rd:
            els = [x.strip(" '") for x in row["Elements"].strip("[]").split(",")]
            if "Sm" in els and set(els) <= ALLOWED | {"Co"} and ("Fe" in els or set(els) == {"Sm", "Co"}):
                keep_rows.append(row)
        res.update({name: keep_rows})
        with open(OUT / "PROVENANCE.txt", "a") as fh:
            fh.write(f"{name}\t{len(r.content)}\t{hashlib.sha256(r.content).hexdigest()}\t{base+name}\t{TODAY}\n")
    save("gnome_filtered_rows.json", res)


def fetch_nomad_inventory():
    url = "https://nomad-lab.eu/prod/v1/api/v1/entries/query"
    rows, after = [], None
    while True:
        pg = {"page_size": 100}
        if after:
            pg["page_after_value"] = after
        body = {"owner": "public", "query": {"results.material.elements": {"all": ["Sm", "Fe"]}, "results.material.n_elements": {"lte": 3}},
                "pagination": pg, "required": {"include": ["entry_id", "upload_id", "upload_name", "main_author.name", "references",
                                                           "datasets.dataset_name", "results.material.chemical_formula_reduced",
                                                           "results.material.elements", "mainfile"]}}
        j = S.post(url, json=body, timeout=120).json()
        rows += j.get("data", [])
        after = j.get("pagination", {}).get("next_page_after_value")
        if not after:
            break
    p, b = save("nomad_inventory_raw.json", rows)
    log(p, url, b)


FETCHERS = {"mp": fetch_mp, "jarvis": fetch_jarvis, "alexandria": fetch_alexandria, "oqmd": fetch_oqmd,
            "aflow": fetch_aflow, "gnome": fetch_gnome, "nomad": fetch_nomad_inventory}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(FETCHERS))
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for k, fn in FETCHERS.items():
        if a.only and k != a.only:
            continue
        print("fetching", k)
        try:
            fn()
        except Exception as exc:
            print("  FAILED:", exc)
    print("done ->", OUT)
