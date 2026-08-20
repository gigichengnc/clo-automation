# Phase 2 Preparation — CLO API Contract and Topology Safety

**Project period:** Year 2 Summer Project — August 2026

This document defines the next engineering branch. It does not claim the runtime fixes are implemented yet.

## Branch scope

Target branch: `phase2/clo-api-contract`

Primary goal: make the CLO runtime adapter fail closed unless its real API contract and observed garment topology are verified.

## Confirmed blockers to address

1. `GetPatternInputInformation` parsing must handle the documented JSON-string return contract rather than treating the result as `list[str]`.
2. Sewing must be refactored around the actual `AddSeamlinePairGroup(...)` signatures instead of the current empty-group + `AddSeamlinePair(...)` abstraction.
3. InnerShape support must be capability/version gated rather than permanently declared unavailable.
4. `SAFE_CHECKPOINT` must require topology evidence; pattern/sewing counts are sanity checks only.
5. Ambiguous edge matching must stop instead of choosing lowest/highest line index.
6. `metadata_to_style.py` must consume seam identity instead of discarding the DXF side's stable edge/seam semantics.

## Phase 2 work order

### P0.1 — Runtime contract probe

- record installed CLO application/API version
- inspect local `ApiStubFiles`
- add non-destructive method/signature/return-type probe
- fail closed if expected contract is absent

### P0.2 — RealBackend API repair

- normalize pattern-information JSON parsing
- replace obsolete sewing wrapper model
- expose outer/internal line addressing explicitly
- update export/checkpoint verification
- update `CLO_Agent_v0.1/API_AUDIT.md`

### P0.3 — Topology-aware verification

- inspect observed stitch/seam-group data
- map runtime indices back to semantic pattern/edge IDs
- compare expected vs observed seam topology
- require topology verification before `SAFE_CHECKPOINT`

### P1.1 — Strict ambiguity handling

- remove line-index tie-breaking as semantic evidence
- ambiguity → `UNKNOWN` / safe stop
- add regression tests for same-length and near-same-length edges

### P1.2 — DXF → garment-contract compiler

- consume metadata + seams + validation together
- preserve pattern IDs, edge IDs, seam IDs, orientation, and provenance
- treat CLO indices as runtime reconciliation data only

## Definition of done

Phase 2 is not complete until:

- mock tests and real-runtime contract probes agree on semantics
- a wrong seam topology cannot pass by count alone
- ambiguous edge identity cannot silently sew
- InnerShape behavior is capability checked
- API audit matches the installed CLO runtime
- existing human-approved garment fixtures remain unchanged unless explicitly approved
