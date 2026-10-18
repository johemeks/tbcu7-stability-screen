# Transcription check (2026-10-13)

Plain-language note: the raw files were copied out of the browser by hand-off (not a direct download), so they were checked against a fresh, independent pull from each database. Same fingerprint means not a single value differs.

| File | Re-pulled values compared | Rows | Result |
|---|---|---|---|
| mp_optimade.json | id, ehull (GGA/GGA+U), formation energy - fresh OPTIMADE query | 61 | identical (0 mismatches) |
| nomad_alexandria.json | id, hull distance, formation energy, magnetization - fresh OPTIMADE query, SHA-256 of sorted rows | 354 | identical (0d04d656...e9ee067a) |
| oqmd_*.json | id, formula, delta_e, stability - SHA-256 against in-browser responses | 191 | identical (3a0015c9...e1fb4a34) |
| gnome.json | id, formation energy, decomposition energy - SHA-256 against in-browser parse of the CSV | 18 | identical (7fb8bb71...e2a2467aa42) |
| jarvis_optimade.json | 14 rows; checked by eye against the response | 14 | identical |
