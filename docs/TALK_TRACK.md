# Talking about the TbCu7 Stability Screen

*Every number below matches `report/stats.json` (v0.1.0 draft). Re-check after any rebuild.*

## 60-second version
**The problem:** New rare-earth-lean magnets increasingly start with a computer search: researchers look up which alloys a materials database says are stable, then make those. For samarium-iron magnets, the best candidates are frozen-in phases made by ultrafast cooling, and it was not known whether the databases describe them well enough to guide that first choice.
**What I built:** An open, citable table. It compares six public databases (Materials Project, AFLOW, JARVIS, NOMAD, OQMD and Google DeepMind's GNoME) with 30 scored lab observations of what actually formed in samarium-iron alloys and eleven alloy families.
**What it shows:** Three of the largest databases put no samarium-iron compound on the stability line, not even the textbook-stable Sm2Fe17. Their energies for a stable phase, the useful frozen-in TbCu7 phase and a phase that does not form all sit within about 4 meV/atom of each other. That is too close to tell them apart. A fourth database orders them correctly but overshoots. Two have no relevant entries at all.
**Who can use it:** Magnet researchers choosing compositions, database teams prioritizing fixes, and anyone building AI screening pipelines for metastable materials.
**Where it is:** Zenodo, https://doi.org/10.5281/zenodo.23456632

## Two-sentence version
I built an open benchmark that checks six major materials databases against real experiments on samarium-iron magnet alloys made by rapid solidification or milling. It shows that, for these metastable phases, today's database stability numbers cannot yet separate what forms from what does not, and it pinpoints why.

## Questions you may be asked
1. **Where does the data come from?** Public database interfaces, queried on 13 October 2026 (628 entries), plus 38 published experiments, each cited by DOI.
2. **What are its limits?** No database contains the disordered TbCu7 crystal, so I estimate it from its ordered relatives. Some lab compositions are assumed from abstracts. The "does not form" test rests on one composition. Details are in `docs/LIMITATIONS.md`.
3. **Why does it matter?** Rare-earth magnets are critical for motors and generators. Screening tools that work for metastable, rare-earth-lean phases would shorten development and reduce dependence on heavy rare earths. This project shows where those tools need fixing first.
