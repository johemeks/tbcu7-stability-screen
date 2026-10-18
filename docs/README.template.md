**Status: {{STATUS}} · version 0.1.0 · data snapshot 2026-10-13**

# TbCu7 Stability Screen

*Validation of public DFT databases against observed metastable phases in Sm–Fe–M alloys, with a stability proxy table.*

## In plain words

Samarium–iron magnet alloys can form a "frozen-in" crystal called the TbCu7 type when molten metal is cooled very fast or ground in a ball mill. Researchers increasingly use big computer databases to choose which alloy recipes to try. This project checks those databases against what labs actually made. It collects **{{N_OBS}}** published experiments (**{{N_SCORED}}** of them scorable) in **{{N_SYS}}** alloy families. It then asks six databases (Materials Project, AFLOW, JARVIS-DFT, NOMAD, OQMD and GNoME) whether they would have predicted each result. The headline: three of the databases put **no Sm–Fe compound at all** on the stability line, not even the well-known stable Sm₂Fe₁₇. As a result, their energies for the stable phase, the TbCu7 phase and a phase that quenching does not produce sit within **{{SPREAD_MAX}} meV/atom** of each other, which is below normal calculation error. In this alloy family, energy above the hull from these databases cannot yet steer composition choices on its own.

## What is in this package

| Path | What it is |
|---|---|
| `data/processed/stability_proxy_table.csv` | **The stability proxy table.** For every alloy family × crystal family × database: best entry, energy above hull, formation energy, Fe moment, links. Includes the TbCu7 SmFe9 estimate per database. |
| `data/processed/tbcu7_binary_path.csv` | TbCu7 stability proxy along SmFe₅ → SmFe₁₂ per database, with an optional configurational-entropy correction. |
| `data/processed/validation_matrix.csv` | Every scored observation × database: matched entry, metric, verdict at 25/50/100 meV/atom. |
| `data/processed/db_scorecard.csv`, `sensitivity.csv` | Hits, misses, false alarms, coverage per database. |
| `data/processed/hull_fidelity.csv` | Known stable Sm–Fe compounds versus each database. |
| `data/processed/magnetization_comparison.csv` | Computed versus measured Fe moments. |
| `data/processed/computed_entries.csv` | All {{N_ENTRIES}} computed entries in one schema. |
| `data/curated/observations.csv` | The {{N_OBS}} curated lab observations with DOIs and evidence level. |
| `data/raw/` | Raw database responses (snapshot) and `PROVENANCE.txt`. |
| `report/figures/` | Four figures. `report/stats.json` holds every number quoted here. |
| `code/` | Numbered pipeline scripts. |
| `docs/` | Start here, glossary, codebook, limitations, verification checklist, next steps. |

## Headline results ({{TAU_MEV}} meV/atom formability window)

| Database | Entries in screen | Observations with a prediction | Hits | Misses | False alarms | Sm–Fe compounds on hull | TbCu7 SmFe9 proxy (meV/atom) |
|---|---|---|---|---|---|---|---|
{{SCORE_ROWS}}

**Fe moment, TbCu7 SmFe9.** Measured {{MU_RT}} μB/Fe at room temperature (Katter et al. 1991). That is about {{MU_0K}} μB/Fe after scaling to 0 K. JARVIS gives {{MU_JARVIS}} and Alexandria {{MU_ALEX}}. MP and OQMD publish no moments on their keyless interfaces.

**Coverage gaps.** No open-literature rapid-solidification or milling observation was found for M = {{NO_OBS_M}}. AFLOW holds no Sm–Fe entries. GNoME's public list holds only newly predicted compounds ({{N_GNOME}} in this chemical space), none at an observed composition.

## How to rerun

```bash
python3 code/02_build.py      # merge raw snapshot -> computed_entries.csv
python3 code/03_proxy.py      # stability proxy table + TbCu7 path
python3 code/04_validate.py   # validation matrix, scorecard, qa_report.txt, stats.json
python3 code/05_figures.py    # figures (add --final after verification)
python3 code/06_document.py   # this README from stats.json
# optional: python3 code/01_fetch.py  (refresh raw data from the live databases)
```
Python ≥ 3.9 with `matplotlib`. Scripts 02–06 need no internet. The final QA line should read `Validation matrix rows: {{N_VM}}`.

## Method in brief

1. **Computed data.** Queries are keyless: OPTIMADE for MP, JARVIS-DFT, OQMD and Alexandria (the PBE calculations hosted on NOMAD); AFLUX for AFLOW; the NOMAD search API for the inventory; and the public GNoME CSV files. Each database's own energy above hull is used. For Sm–Fe binaries, the hull is recomputed and agrees with the reported values (max difference {{HULL_DIFF}} eV/atom).
2. **Crystal families.** Entries are grouped by stoichiometry class: CaCu5 (1:5), 2:17, 3:29, ThMn12 (1:12), other TbCu7 approximants. Zr and Hf are placed on the Sm site when that gives a standard ratio.
3. **TbCu7 proxy.** TbCu7 R₁₋δT₅₊₂δ is the disordered parent of the 1:5, 2:17, 3:29 and 1:12 ordered structures. The proxy is the lower convex envelope of a database's ordered parents, minus its hull, at the observed Fe/Sm ratio. An ideal-mixing entropy term at {{T_K}} K ({{TS}} meV/atom at SmFe9) is reported separately.
4. **Validation.** Each observation is matched to the database's lowest entry of the same family within ±{{WINDOW}} in every atomic fraction. "Formed" phases count as hits at ≤ {{TAU_MEV}} meV/atom. The one "not formed" case (SmFe₁₂ by melt spinning) counts as a false alarm if it falls inside the window.

Limitations are listed in `docs/LIMITATIONS.md`. Please read them before citing any number.

## Sources

Materials Project (CC BY 4.0), AFLOW, JARVIS-DFT (NIST, public domain), NOMAD and Alexandria (CC BY 4.0), OQMD (CC BY 4.0), GNoME (CC BY 4.0, Merchant et al., *Nature* 624, 80, 2023). Literature records cite each paper's DOI. Only bibliographic facts and short paraphrases are included, no copied text.

## License and citation

Code: MIT (`LICENSE`). Data and documents: CC BY 4.0 (`LICENSE-DATA`). Please cite using `CITATION.cff` or https://doi.org/{{DOI}}.

AI assistance: data retrieval scripts, curation drafting and analysis code were prepared with an AI assistant (Claude). The author verified every number and decision before release.
