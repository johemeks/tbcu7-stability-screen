# Start Here: TbCu7 Stability Screen

*Read this first. It explains your project in plain language. Words in bold are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

A public, citable table that checks whether six big computer databases of materials correctly predict which samarium-iron magnet alloys labs can actually make by very fast cooling or ball milling.

## Why it matters

Samarium-iron (Sm-Fe) alloys are candidates for strong magnets that use less rare earth. Some of the best ones only exist in a "frozen-in" form called the TbCu7 structure. They appear when molten metal is cooled in a millisecond (melt spinning) or ground in a ball mill. Researchers increasingly pick which recipes to try by looking up computer predictions first. If those predictions are wrong for this kind of alloy, people waste months in the lab chasing the wrong compositions, or skip the right ones.

This project tests that first step. It takes what labs actually saw and asks each database whether it would have predicted it.

Think of it like checking a weather app against what actually happened last month, before you trust it to plan a trip.

## Where the information comes from

All sources are free and public.

| Source | In plain terms | What one row looks like | Link |
|---|---|---|---|
| Materials Project | The largest open database of computed materials | One compound: formula, energy above the "stable line" | https://materialsproject.org |
| AFLOW | A Duke University computed-materials library | Same idea | https://aflow.org |
| JARVIS-DFT | The US National Institute of Standards and Technology's computed-materials database | Same, plus magnetism | https://jarvis.nist.gov |
| NOMAD (Alexandria dataset) | A European archive of calculations; Alexandria is the large set of calculations it hosts that includes these alloys | Same, plus magnetism per atom | https://nomad-lab.eu , https://alexandria.icams.rub.de |
| OQMD | Northwestern University's Open Quantum Materials Database | Same idea | https://oqmd.org |
| GNoME | Google DeepMind's list of newly predicted stable crystals | One predicted compound and its stability | https://github.com/google-deepmind/materials_discovery |
| Published lab papers | 38 experiments on melt-spun or milled Sm-Fe-M alloys, each with its DOI | One experiment: recipe, process, crystal found, magnetism if reported | Listed in `data/curated/observations.csv` |

## What you will have at the end

- [x] **A data package on Zenodo** with a permanent citation number (**DOI**): https://doi.org/10.5281/zenodo.23456632
- [x] **The stability proxy table** (`data/processed/stability_proxy_table.csv`): best entry per database, alloy family and crystal type
- [x] **The validation results**: a hit/miss table per experiment and a scorecard per database
- [x] **Four figures** and a short web report
- [x] **A public GitHub page for the code**: https://github.com/johemeks/tbcu7-stability-screen
- [x] **A preprint of the paper on Zenodo**: https://doi.org/10.5281/zenodo.23457250

## How it connects to your work

Your proposed framework starts by using computer screening to choose compositions. This project measures, with real data, how far that first step can be trusted for metastable magnet phases, and where it breaks.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create ORCID, GitHub (optional) and Zenodo accounts | Now | 15 min |
| Send your name, ORCID and affiliation | Now | 2 min |
| Check the results using `docs/VERIFY_CHECKLIST.md` | Now that the draft is ready | 1 to 2 hours |
| Approve publishing | After checking | 5 min |
| Upload to Zenodo using `docs/PUBLISH_GUIDE.md` | After approval | 20 min |

## The steps ahead

1. **Data collected.** Done. 628 computed entries, six databases, snapshot of 2026-10-13.
2. **Data cleaned and combined.** Done. One table, one set of column names.
3. **Quality checks.** Done. See `data/processed/qa_report.txt`.
4. **Figures.** Done.
5. **Report.** Done.
6. **Checked and published.** Verified by the author on 2026-10-18.

*Status: released, version 0.1.0.*
