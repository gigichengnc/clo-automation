# Garment Automation Lab

> DXF generation · CLO automatic sewing · Blender garment workflows

This repository is evolving from two garment-automation prototypes into a multi-project workspace built around a shared digital garment contract.

## Projects

| Project | Purpose | Status |
|---|---|---|
| DXF Generator | Generate garment patterns, DXF, stable pattern/edge IDs, and validation metadata | Existing prototype in `DXF_AUTOMATION_V2/`; migration planned |
| CLO AutoSewing | Reconcile garment semantics with CLO, sew verified topology, simulate/export | Existing prototype in `CLO_Agent_v0.1/`; stabilization in progress |
| Blender Dressing | Import approved CLO garment + avatar and automate dressing/render setup | Planned |

## Design principles

1. **Preserve semantic identity.** Pattern IDs, edge IDs, and seam IDs should survive the full pipeline.
2. **Do not guess garment geometry.** Ambiguity is a safe-stop condition.
3. **Validate topology, not only counts.** The expected number of seams is not proof that the correct seams exist.
4. **Separate garment data from application adapters.** CLO and Blender should consume the garment contract rather than redefine it.
5. **Treat installed application API stubs as runtime truth.** Mock success is not proof of real-runtime compatibility.

Read:

- `ARCHITECTURE.md`
- `KNOWN_ISSUES.md`
- `AGENTS.md`
- `docs/development-roadmap.md`
- `docs/migration-plan.md`

## Target pipeline

```text
garment parameters
        ↓
DXF Generator
        ↓
shared garment contract
        ↓
CLO AutoSewing
        ↓
simulation / export
        ↓
Blender Dressing
        ↓
render / animation / engine export
```

Existing folders remain in place during the first migration phase so current scripts are not broken by a documentation/architecture change.
