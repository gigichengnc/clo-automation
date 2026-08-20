# clo-automation

Two connected tools for turning garment patterns into a **machine-readable, CLO3D-automatable**
pipeline. Prototype garment: **No.11 fitted dress**; designed to extend to more styles.

> **Measurement-free template.** This repo ships the framework only — code, schemas, docs, and a
> **synthetic demo** (`styles/demo.json`, obviously-fake round numbers). No real garment data:
> pattern binaries (`*.dxf`, `*.zprj`), preview images, and the real style/metadata files are
> git-ignored / kept local and not published. Everything runs on the demo out of the box; to use it
> for a real garment, add your own `styles/<id>.json` and `state/mock_fresh_<id>.json` locally.

## `DXF_AUTOMATION_V2/`
Upgrades a pattern DXF into machine-readable form **without changing the garment geometry**
(perimeter preserved to 0.000 mm). Emits stable ASCII pattern/edge IDs, a metadata sidecar
(edges identified by corner endpoints, not length), a seam map, notches/grainlines, validation, and
a CLO-clean DXF. See `DXF_AUTOMATION_V2/README.md`.

```bash
cd DXF_AUTOMATION_V2 && python gen_example.py     # synthetic demo of the retag/segment/split moves
```
(The real No.11 generator `gen11.py` + its measurement templates are kept local, not published.)

## `CLO_Agent_v0.1/`
One reusable in-CLO automation controller (a state machine): scan → identify (by edge-length
signature, no hardcoded indices) → validate → mirror → auto-sew 9 verified seams → validate →
checkpoint → **STOP before simulate**. Runs inside CLO's Python Editor; also runs off-CLO on a mock
backend for testing. Every CLO API call is verified in `CLO_Agent_v0.1/API_AUDIT.md`. See
`CLO_Agent_v0.1/README.md`.

```bash
cd CLO_Agent_v0.1 && python CLO_Agent.py && python selftest.py   # runs the synthetic demo + safety tests
```
The bundled demo goes `FRESH 4/0 → MIRRORED 5/0 → SAFE_CHECKPOINT 5/3`.

## Milestone (real No.11, local data)
With the local `styles/11.json`: `FRESH 11/0` → `MIRRORED 13/0` → `SAFE_CHECKPOINT 13/9`,
no simulation, no duplicate seams, no yoke/InnerShape error.
