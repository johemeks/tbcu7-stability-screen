# Next steps (what v0.2 would add)

1. **Fill the M gaps.** Look for Cr, Mn and Hf rapid-solidification or milling data in non-open full texts, Japanese conference proceedings, and the Teresiak 1998/1999 and Schultz 1991 full papers.
2. **Compute TbCu7 directly.** Run special-quasirandom-structure (SQS) or cluster-expansion DFT for SmFe9 and (Sm,Zr)Fe10 with the MP-compatible settings, and compare with the proxy. This is the single most valuable addition.
3. **Fix the binary hull.** Recompute Sm-Fe with 4f-in-valence plus Hubbard U or with r2SCAN (MP already serves r2SCAN values for some entries, kept in `computed_entries.csv` notes). Check whether Sm2Fe17 returns to the hull.
4. **Materials Project moments.** Add an `MP_API_KEY` run of `01_fetch.py` for total magnetization.
5. **Structure matching.** Replace stoichiometry-based family labels with pymatgen StructureMatcher against the CaCu5, Th2Zn17, Th2Ni17, Sm3Fe29 and ThMn12 prototypes.
6. **Second "not formed" set.** Add compositions where melt spinning gives only amorphous or alpha-Fe plus 2:17, to test specificity more than once.
