# CLO API Audit — CLO_Agent v0.1

Every CLO Python API call the agent makes, its verified signature, and the source.
Rule followed: **no invented methods.** Anything not confirmed in the official docs is
marked `verified: PARTIAL` and guarded in code (try candidates + explicit log, never fake success).

Official sources consulted (CLO API 0.1 documentation, developer.clo3d.com):
- API access / editor: <https://developer.clo3d.com/python.html>
- API function list: <https://developer.clo3d.com/list.html>
- API scenario (worked examples): <https://developer.clo3d.com/scenario.html>
- Changelog (module + version per function): <https://developer.clo3d.com/changelog.html>

All calls are isolated in `core/clo_api.py` (`RealBackend`). No other module imports a CLO module.

| # | Call in agent | Official signature | Module (changelog) | Verified | Used for |
|---|---|---|---|---|---|
| 1 | `import_file(path)` | `ImportFile(...)` | Import_API (v4.0.2+) | YES | (optional) load a DXF/zpac before scanning |
| 2 | `pattern_count()` | `GetPatternCount() -> int` | Pattern_API (v3.2.0+) | YES | state machine, scan loop |
| 3 | `pattern_info(idx)` | `GetPatternInputInformation(patternIndex:int) -> list[str]` | Pattern_API (v3.2.0+) | YES (return **format** not documented) | centroid parse for L/R; raw logged |
| 4 | `line_length(idx,line)` | `GetLineLength(patternIndex:int, lineIndex:int) -> float` | Pattern_API (v3.2.0+) | YES | edge-length signatures, seam line lookup |
| 5 | `line_count(idx)` | *(no official count fn)* — probed via #4 until it returns ≤0 | — | DERIVED | number of outer edges per pattern |
| 6 | `symmetry(idx)` | `SymmetryPatternPiece(patternIndex:int) -> bool` | Pattern_API | YES | mirror BACK_CENTER / BACK_SIDE |
| 7 | `add_seam_group()` | `AddSeamlinePairGroup() -> int` (returns group index) | Pattern_API | YES | one group per safe seam |
| 8 | `add_seam_pair(g,p1,l1,p2,l2)` | `AddSeamlinePair(groupIndex:int, patternIndex1:int, lineIndex1:int, patternIndex2:int, lineIndex2:int) -> bool` | Pattern_API | YES | the actual sewing |
| 9 | `seam_group_count()` | `GetSeamlinePairGroupCount() -> int` | Pattern_API | YES | state machine, validation |
| 10 | `export_zprj(path)` | `ExportZPrj(_filePath:str, _bCreateThumbnail:bool) -> str` | **module unconfirmed** (tried `export_api`, then `pattern_api`) | PARTIAL | checkpoints |

## Not used in v0.1 (documented, reserved for later)
- `utility_api.Simulate(intCount)` — drape simulation. **Deliberately not called** (v0.1 stops before simulate).
- `pattern_api.Get/SetArrangement`, `SetArrangementPoint` — arrangement (later).
- `export_api.ExportDXF(_filePath, _exportOption)` — export (later).
- `fabric_api.AddFabric(path)`, `AssignFabricToPattern(fab, pat)` — fabrics (later).
- `pattern_api.CreatePatternWithPoints(points)` — not needed (we import, not draw).

## Two things to verify on YOUR machine (first real run)
1. **`GetPatternInputInformation` return format.** The docs say `list[str]` but not the field
   layout. On the first real run the agent logs the raw output of `pattern_info(0)`. Paste that
   log back and the `scanner._parse_centroid()` parser can be tuned. Until then, if no centroid is
   parseable and an L/R split is required, the agent **SAFE STOPs** rather than guessing.
2. **`ExportZPrj` module.** If checkpoints fail with "ExportZPrj not found", tell me the correct
   module name from your API build; `core/clo_api.py:export_zprj` tries `export_api` then
   `pattern_api`. It never fakes a save — a failed save is logged as `[WARN]`, and you can save
   manually via *File ▸ Save Project As*.

## Yoke / InnerShape safety (from the failed-yoke lesson)
The docs expose **no** InnerShape accessor. `GetLineLength` returns the **outer** boundary edge
(e.g. yoke bottom `378.345`), never the InnerShape children (`189.173 + 189.173`). The agent
therefore can only ever sew outer edges. `core/sewing.py` enforces: if a configured seam length is
not found among a pattern's outer edges (`GetLineLength` results), it **SAFE STOPs**. This is why
the yoke↔back-center seam is **excluded** from v0.1 and would refuse to sew even if added.
