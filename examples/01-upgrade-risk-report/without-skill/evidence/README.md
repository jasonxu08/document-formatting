# Evidence for the v8 → v10 upgrade assessment

Supporting data for [`../report.md`](../report.md). Keep it with the report: the report cites these files and the decision record refers to them.

| Path | Contents |
|---|---|
| `source/` | The three inputs exactly as received on 2026-10-17: the Platform team's notes (dated 2026-10-14), the service inventory and the Q3 incident log. The inventory and the log carry no as-of date. Do not edit; put corrections in a new, dated file. |
| `SHA256SUMS.txt` | SHA-256 of each file in `source/`, as received. |
| `derived/` | Numbers calculated from `source/`. `key-figures.csv` gives the calculation behind every figure cited in the report. |
| `analysis.py` | Regenerates `derived/` and `../figures/`. Run `python evidence/analysis.py` from the folder that holds `report.md`. Standard library only; Graphviz is needed only for the PNG. |

To check that the inputs are unchanged without Python, compare `Get-FileHash source\* -Algorithm SHA256` (PowerShell) with `SHA256SUMS.txt`. A mismatch right after a git checkout usually means line-ending conversion.
