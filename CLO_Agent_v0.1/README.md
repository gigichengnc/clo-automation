# CLO_Agent v0.1

> **Published as a measurement-free template.** The runnable bundle here uses the **synthetic demo**
> style (`styles/demo.json`, fake numbers) → `4/0 → 5/0 → 5/3`. The real No.11 config
> (`styles/11.json`, `state/mock_fresh_11.json`) is kept local/unpublished; with it the same code
> gives the `11/0 → 13/0 → 13/9` milestone described below. Everything else is identical.

One reusable CLO3D automation controller (a state machine), not a pile of `StageN.py`.
Prototype target: **No.11 收腰小洋裝**. Designed to extend to 09–22 by adding `styles/<id>.json`.

```
scan → identify → validate → mirror → validate → auto-sew safe seams → validate → checkpoint → STOP
```

v0.1 deliberately **stops before arrange / simulate / export**.

## What one run does (No.11)

| State | patterns | sewing groups |
|---|---|---|
| FRESH | 11 | 0 |
| MIRRORED (after mirroring BACK_CENTER + BACK_SIDE) | 13 | 0 |
| SAFE_CHECKPOINT (after 9 verified seams) | 13 | 9 |

The 9 safe seams: front princess L/R, skirt side A/B, center-back, back princess L/R, side seam L/R.
**Not touched in v0.1** (config `do_not_touch_v01`): yoke↔back-center, collar↔neckline,
armhole facing, waist M:N, shoulder — until their CLO behaviour is verified.

## Install / run inside CLO3D 2026

1. Copy the whole `CLO_Agent_v0.1/` folder somewhere stable, e.g. `C:\CLO_Agent_v0.1`.
2. Open your **fresh No.11** project in CLO (patterns = 11, sewing groups = 0).
   - Either import the DXF first, or let the agent import it (put the path in `command.json` later; v0.1 assumes it's already open).
3. CLO ▸ Main Menu ▸ **Edit ▸ Python Script**. In the editor, open `CLO_Agent.py` and press **Run**
   (or drag `CLO_Agent.py` into the 3D window).
4. Read the **Log Console**. Expected tail:

```
Patterns = 13
Sewing groups = 9
STATUS = SAFE CHECKPOINT
```

5. Outputs written next to the script:
   - `logs/run_*.log` — full readable log (paste into ChatGPT/Claude to debug).
   - `state/current_state.json` — machine state for a Codex/Claude bridge.
   - `checkpoints/11_00_fresh.zprj`, `11_01_mirrored.zprj`, `11_02_safe_sewn.zprj` — if `ExportZPrj` is available (see API_AUDIT.md).

### Run it again
- If the project is already `13 / 9`, the agent reports **SAFE CHECKPOINT already reached** and does nothing (no duplicate seams).
- If the state is anything unexpected, it **STOPs** and refuses to continue.

## Test it WITHOUT CLO (this is how it was validated)

```bash
python CLO_Agent.py     # runs on a MOCK backend (state/mock_fresh_11.json) -> 13 / 9
python selftest.py      # asserts safety branches: closest-edge match, InnerShape guard, state detection
```

The MOCK backend is a **test double**, clearly labelled in every output; it never fakes a real CLO
result. The exact same module code drives the REAL CLO API when run inside CLO.

## Semantic identification (no hardcoded indices)

Pieces are identified by **edge-length signature** (order-independent multiset match, tolerance
`tolerance_mm`), then L/R split by **centroid.x** from `GetPatternInputInformation`. If a required
L/R split can't be resolved (no centroid), the agent **SAFE STOPs** — rule: *never silently guess*.
Seam edges are then located by **closest** matching length (not first-within-tolerance), so
near-but-different edges (e.g. a center-back edge a few mm from a princess edge) don't get confused;
only genuinely near-equal edges (e.g. the two symmetric front princess edges) are treated as
ambiguous and resolved by the config's `pick: left|right`, always logged.

## Architecture

```
CLO_Agent.py            state machine / orchestrator; reads command.json, writes current_state.json
core/clo_api.py         ONLY file that imports CLO modules. REAL + MOCK backends, one verified call each
core/scanner.py         scan all patterns -> edge lengths + centroid
core/matcher.py         signature -> semantic ID; closest-edge line lookup; L/R by centroid
core/mirror.py          SymmetryPatternPiece for BACK_CENTER / BACK_SIDE, re-scan between
core/sewing.py          the 9 safe seams; outer-edge (InnerShape) guard; atomic plan-then-sew
core/validator.py       count checks, piece-present checks, duplicate-seam checks, state detection
core/checkpoint.py      ExportZPrj (guarded; reports honestly if unavailable)
core/logger.py          [PASS]/[FAIL]/[WARN]/[STOP] readable log
styles/11.json          No.11 signatures + 9 safe seams + state machine
state/command.json      {style, action}  (input)   action: "build_safe"
state/current_state.json                  (output, for Codex/Claude bridge)
state/mock_fresh_11.json                  MOCK fixture (off-CLO only)
```

## Codex / Claude bridge (already wired, no AI calls inside)

- Input: `state/command.json` — `{ "style": "11", "action": "build_safe" }`.
- Output: `state/current_state.json`:

```json
{ "style": "11", "status": "SAFE_CHECKPOINT", "pattern_count": 13,
  "sewing_groups": 9, "backend": "REAL_CLO", "warnings": [], "errors": [] }
```

v0.1 is deterministic and local — no OpenAI/Anthropic calls (per spec).

## Adding another style (09–22)

Add `styles/<id>.json` with the same shape: CLO-probed edge signatures, `state_machine`,
`mirror_sources`, and `safe_seams`. If you generate the DXF with `DXF_AUTOMATION_V2/gen<id>.py`,
use `tools/metadata_to_style.py` to seed the signatures from `<id>.metadata.json`, then re-probe
inside CLO once to lock the exact numbers (CLO re-segments curves on import).

## Known limits / honesty notes
- The existing `Stage1/Stage2A/probe` scripts were **not present in this project folder**; the agent
  reconstructs their proven logic from your written spec + the verified API docs. If you paste those
  scripts, the line-index choices can be cross-checked against your working run.
- `GetPatternInputInformation` format and `ExportZPrj` module need one confirmation on your machine
  (see **API_AUDIT.md**). Both are guarded: unknowns SAFE STOP or WARN, never fake success.
- FRONT_SKIRT vs BACK_SKIRT share an identical signature; v0.1 tells them apart by centroid only.
  Harmless for the symmetric skirt-side seams, but flagged.
