# CLO AutoSewing

Status: architecture placeholder; current implementation remains in `CLO_Agent_v0.1/` during migration.

## Mission

Apply a verified garment specification to CLO without guessing garment semantics.

## Owns

- CLO state scanning
- semantic pattern/edge reconciliation
- verified seam creation
- checkpoint/state machine
- CLO simulation/export orchestration
- runtime evidence

## Does not own

- source garment measurements
- DXF construction rules
- Blender dressing logic

## Safety principle

```text
ambiguous → stop
missing   → stop
mismatch  → stop
verified  → continue
```
