# Your verification checklist

> **Sign-off:** Joshua Chukwuemeka Ejeka (ORCID 0009-0005-5885-5073) reported on 2026-10-18 that he had verified the package and approved publication. The package was released as built, which corresponds to Option A for every decision in Part 4.

*Before anything goes public under your name, you check it. Total time: about 1.5 to 2 hours. Tick each box and add the date.*

## Part 1: Make sure the results can be rebuilt (15 min)

Pick one:
- [ ] **Option A: run it yourself.** In a terminal, inside the project folder, paste:
  ```
  pip install matplotlib
  cd code && python3 02_build.py && python3 03_proxy.py && python3 04_validate.py && python3 05_figures.py && python3 06_document.py
  ```
  The screen should show `Computed entries in screen: 628` and `Validation matrix rows: 180`.
- [ ] **Option B: ask Claude.** In a new chat with Opus 5.5 or Fable 5, upload the zip and say: "Re-run this pipeline from scratch and give me the headline numbers." Compare them to these: MP TbCu7 proxy 19.3 meV/atom; JARVIS 89.4; NOMAD (Alexandria) 15.6; OQMD 18.1; MP hits 23 / misses 1 / false alarms 1.

Then:
- [ ] `data/processed/qa_report.txt` says `entries with |diff| > 5 meV/atom: 0`.
- [ ] Every number in `README.md` matches `report/stats.json`. This is automatic, since `06_document.py` copies them.

## Part 2: Check the sources (15 min)

- [ ] Each link opens: https://materialsproject.org · https://aflow.org · https://jarvis.nist.gov · https://nomad-lab.eu · https://alexandria.icams.rub.de · https://oqmd.org · https://github.com/google-deepmind/materials_discovery
- [ ] Licenses allow reuse with credit: MP CC BY 4.0; OQMD CC BY 4.0; NOMAD/Alexandria CC BY 4.0; GNoME CC BY 4.0; JARVIS (NIST) public domain; AFLOW (no data used).

## Part 3: Check rows by hand (45 min)

**Database values.** Open the file, find the row, then open the link and look for the same number. The Materials Project page may show a "verify you are human" check; that's normal.
- [ ] `computed_entries.csv`, MP `mp-1426` Fe17Sm2: energy above hull **0.0229 eV/atom**. Check at https://next-gen.materialsproject.org/materials/mp-1426 ("Energy Above Hull"). ___
- [ ] MP `mp-1566` Fe5Sm: **0.0065**. Check at https://next-gen.materialsproject.org/materials/mp-1566 ___
- [ ] JARVIS `JVASP-85844` Fe17Sm2: ehull **0.0519**, formation energy **0.032 eV/atom**. Search "JVASP-85844" at https://jarvis.nist.gov/jarvisdft ___
- [ ] OQMD `4818030` Fe17Sm2: stability **0.020**. Check at https://oqmd.org/materials/entry/4818030 ___
- [ ] Alexandria `agm005529553` Fe17Sm2: hull distance **0.0194**, magnetization **39.82 μB per cell**. Check at https://alexandria.icams.rub.de/pbe/v1/structures/agm005529553 ___
- [ ] GNoME `82e7ee41aa` SmZr2Fe9: decomposition energy **−0.0132 eV/atom**. This is row "Fe9Sm1Zr2" in `stable_materials_summary.csv`. ___
- [ ] AFLOW: open https://aflow.org/API/aflux/?species(Sm),species(Fe),compound,paging(0),format(json). It should show `[]` (no entries). ___

**Extreme values** (most likely to be wrong):
- [ ] Largest TbCu7 proxy: JARVIS **89.4 meV/atom** at SmFe9 (`tbcu7_binary_path.csv`). It is driven by JARVIS's Sm2Fe17 at 0.0519 and SmFe12 at 0.2608 (JVASP-37997). Check both on JARVIS. ___
- [ ] Smallest proxy: Alexandria **15.6** (a line between SmFe5 at 0.007 and SmFe12 at 0.0186). ___

**Lab observations.** Open the DOI and read the abstract.
- [ ] O01 Katter 1991, https://doi.org/10.1063/1.349302: TbCu7 above 15 m/s, a = 4.88 Å, c = 4.23 Å, Tc = 210 °C, Js = 1.25 T. ___
- [ ] O03/O04 Nakayama 2010, https://doi.org/10.2497/jjspm.57.357: TbCu7 at 8.7 and 12.7 at% Sm. ___
- [ ] O10 Tamura 2020, https://doi.org/10.1016/j.jallcom.2020.154010: amorphous at SmFe12 composition. ___
- [ ] O25 Sakurada 1996, https://doi.org/10.1063/1.361679: TbCu7, Js above 1.7 T. ___
- [ ] O32 Djega-Mariadassou 2001, https://doi.org/10.1103/PhysRevB.65.014419: single-phase Th2Zn17. ___

## Part 4: Your decisions (15 min)

These choices were made provisionally. Agree with each one or change it.
- [ ] **Formability window.** It is 50 meV/atom. Option A: keep 50 (common in the literature). Option B: 25. That turns 2 MP hits and 3 Alexandria hits into misses (the ternary 1:12 and 2:17 cases), and leaves the TbCu7 and false-alarm verdicts unchanged. Option C: 100. JARVIS then rises from 1 to 16 hits. See `sensitivity.csv`. Recommended: A. Your choice: ___
- [ ] **Assumed phase compositions** (rows labelled "assumed" in `observations.csv`: O16, O18, O19, O25, O29, O30, O31, O33, O34, O35). Option A: keep the assumptions and flag them. Option B: check the full texts and replace them. Recommended: B for O25 and O29. Your choice: ___
- [ ] **Minor-cobalt observations** (O21–O24: 4–4.5 at% Co). Option A: score them as Sm-Fe-M (current). Option B: drop them. That removes 4 TbCu7 observations: hits for MP, OQMD and Alexandria, misses for JARVIS. Recommended: A. Your choice: ___
- [ ] **Title-only evidence** (O08, O09, O16, O17, O30). Option A: keep them. Option B: drop them. Recommended: A, labeled as now. Your choice: ___

## Part 5: Before it goes public (20 min)

- [ ] Rewrite the "In plain words" paragraph of `README.md` (in `docs/README.template.md`) in your own words.
- [ ] Your name, ORCID, affiliation and email are correct in `AUTHORS.json`, `CITATION.cff` and `.zenodo.json`.
- [ ] You have read `docs/LIMITATIONS.md` and agree with it.
- [ ] Ask Claude to regenerate with `--final` (`python3 code/05_figures.py --final && python3 code/06_document.py --final`) and to run the publish gate.

**When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.**
