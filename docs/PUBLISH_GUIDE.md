# Publish guide: Zenodo upload (about 20 minutes)

*Plain-language note: do this only after every box in `VERIFY_CHECKLIST.md` is ticked. The upload was not done for you, because Zenodo needs your own login and your attestation as author.*

## Copy-ready text

**Title:** TbCu7 Stability Screen: validation of public DFT databases against observed metastable phases in Sm–Fe–M alloys (stability proxy table, v0.1.0)

**Upload type:** Dataset

**Version:** 0.1.0

**License:** Creative Commons Attribution 4.0 International (data and documents). The code inside is MIT.

**Keywords:** TbCu7; SmFe9; Sm-Fe-N; permanent magnets; metastable phases; melt spinning; mechanical alloying; energy above hull; DFT database validation; Materials Project; OQMD; JARVIS-DFT; NOMAD; Alexandria; AFLOW; GNoME

**Description (paste as-is, or edit in your own words):**
> This dataset tests whether public density-functional-theory (DFT) databases can guide composition selection for metastable magnet phases. It compares energy above the convex hull and computed Fe moments from Materials Project, AFLOW, JARVIS-DFT, NOMAD (Alexandria PBE calculations), OQMD and GNoME (628 entries, snapshot 2026-10-13). It checks them against 38 published observations of phases formed in Sm–Fe and Sm–Fe–M alloys (M = Co, Ti, V, Zr, Nb, Cu, Si, Ga, Al, Mo; no observations found for Cr, Mn, Hf) after rapid solidification or mechanical milling. 30 of those observations are scored. Because no database contains the disordered TbCu7 structure, a stability proxy is built from each database's ordered parents (CaCu5, 2:17, 3:29, ThMn12). The proxy and per-family best entries are given in `stability_proxy_table.csv`. Main finding: Materials Project, OQMD and Alexandria place no Sm–Fe compound on the convex hull. Their energies for equilibrium Sm2Fe17, metastable TbCu7 SmFe9 and SmFe12 (not formed by melt spinning) differ by less than 5 meV/atom. JARVIS ranks them correctly but overestimates the TbCu7 energy (89 meV/atom). AFLOW and GNoME contain no comparable entries. The package includes the raw snapshots with provenance, the curated observation table with DOIs, the numbered pipeline scripts, a QA report, four figures and full documentation (codebook, limitations).

**Related identifiers:** Add each DOI in `data/curated/observations.csv` (column `doi`) as "cites". If you also publish on GitHub, add that URL as "is supplemented by".

## Steps

1. Go to https://zenodo.org and click **Log in**. Choose **ORCID** so your ORCID attaches automatically. (1 min)
2. Click **New upload** (top right). (instant)
3. Drag in `tbcu7-stability-screen-v0.1.0.zip`. Optionally, also drag `data/processed/stability_proxy_table.csv` and the four PNG figures separately, so people can preview them. Wait for the green checkmarks. (2 min)
4. **Resource type:** Dataset. **Title**, **Version**, **Description**, **Keywords**: paste from above. (3 min)
5. **Creators:** click **Add creator**, search your ORCID, and set the affiliation exactly as in `AUTHORS.json`. (2 min)
6. **Licenses:** remove the default and add **Creative Commons Attribution 4.0 International**. (1 min)
7. **Related works:** add the identifiers above. (5 min, optional)
8. Click **Preview** and check that the files and author list look right. Then click **Publish**. The screen shows a DOI like `10.5281/zenodo.1234567`. (1 min)
9. Send the DOI to Claude. Claude will put it into `CITATION.cff`, `.zenodo.json` and the README, and rebuild the zip as version 0.1.1. On Zenodo, use **New version** on the same record so both versions share one "concept DOI". (5 min)
10. Record the release in your evidence log the same day. (2 min)

**Tip:** to practice first, do the same steps at https://sandbox.zenodo.org. It's a separate test site, and nothing there is permanent.
