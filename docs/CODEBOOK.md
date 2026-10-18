# Codebook

*Plain-language note: what every column means. Open this when a column name is unclear.*

## data/curated/observations.csv (one row per lab observation)
| Column | Meaning |
|---|---|
| obs_id | Stable ID (O01...) |
| system | Elements present, e.g. Sm-Fe-Ti |
| M | Third element (blank for binary) |
| sample_composition | Nominal alloy composition as reported (semicolons replace commas) |
| process / state | Synthesis route (melt spinning, mechanical alloying, ...) and whether as-quenched, as-milled or annealed |
| observed_phases | Phases reported in the source |
| test_family | Crystal family tested against the databases (TbCu7, ThMn12, Th2Zn17, Th2Ni17, CaCu5, Sm5Fe17, omega, ...) |
| test_outcome | formed / not_formed |
| phase_x_TM_per_R | Transition-metal-site atoms per Sm-site atom in the tested phase |
| phase_frac_Sm, phase_frac_M | Atomic fractions of Sm and M in the tested phase |
| phase_comp_basis | Whether the phase composition is reported, nominal or assumed (assumptions labelled "assumed") |
| minor_additions | Other elements present (Co, B, C, N) |
| Js_T, Js_temp_K | Saturation polarization (tesla) and the temperature it was measured at |
| Tc_K | Curie temperature (kelvin) |
| m_Fe_muB, m_Fe_temp | Reported Fe moment (Bohr magnetons) and temperature |
| lattice_a_A, lattice_c_A | Hexagonal lattice parameters (Å) when reported |
| scored | yes = used in the validation; no = context only |
| doi, first_author, year | Source |
| evidence | abstract / title / title+abstract: how much of the source was readable in open metadata |
| notes | Short paraphrase, never copied text |

## data/processed/computed_entries.csv (one row per database entry)
| Column | Meaning |
|---|---|
| database | MP, JARVIS, NOMAD-Alexandria, OQMD, GNoME (AFLOW returned none) |
| entry_id | The database's own ID |
| formula, system, M | Reduced formula, element set, third element |
| frac_Sm, frac_Fe, frac_M | Atomic fractions |
| nsites, sg_number | Atoms in the stored cell; space-group number when provided |
| family | Stoichiometry class (see LIMITATIONS 2) |
| x_TM_per_R, R_site | Ratio used for the family, and which elements were placed on the Sm site |
| ehull_eV_atom | The database's own energy above its hull (GNoME: decomposition energy clipped at 0) |
| ehull_kind | Functional / scheme behind it |
| eform_eV_atom | Formation energy per atom |
| m_Fe_muB | Mean Fe moment (Alexandria: per-site average; JARVIS: cell moment / N_Fe) |
| magnetization_muB_cell | Total cell moment as served |
| note, source_url | Extra values (e.g. MP r2SCAN hull) and a link to the entry |

## data/processed/stability_proxy_table.csv (the deliverable table)
One row per system × family × database with the lowest-energy entry: n_entries, best_entry_id, best_formula, x_TM_per_R, R_site, frac_M, ehull_eV_atom, eform_eV_atom, m_Fe_muB, within_50meV, on_hull_10meV, source_url. The last rows ("TbCu7 proxy (x=9, ordered-parent envelope)") give the TbCu7 SmFe9 estimate per database.

## data/processed/tbcu7_binary_path.csv
x_TM_per_R, delta_dumbbell (fraction of Sm sites replaced by Fe pairs), frac_Fe, E_envelope (lower envelope of ordered parents), E_hull, dE_proxy (= envelope − hull), TS_conf (ideal mixing entropy × T), dG_proxy (= dE − TS), T_K, bracket_frac_Fe (parents used).

## data/processed/validation_matrix.csv
obs_id × database: metric_eV_atom (value compared to the window), coverage (binary entry / ternary entry / ternary approximant / binary-path model / binary entry (M ignored) / none), matched (entry used), comp_distance, metric_minus_TS_conf (TbCu7 only), verdict_25meV / verdict_50meV / verdict_100meV (hit, miss, false alarm, correct reject, no data).

## Other outputs
- db_scorecard.csv / sensitivity.csv: counts per database (and per window).
- hull_fidelity.csv: Sm2Fe17, SmFe3, SmFe2 (equilibrium phases) versus each database; pass if ≤ 0.010 eV/atom.
- hull_recheck.csv: our recomputed Sm-Fe hull distance against each database's own value.
- magnetization_comparison.csv: computed and measured Fe moments.
- report/stats.json: every number quoted in README and the report.
