# Development Roadmap

## Phase 1 — Repository architecture and safety contract

Goal: turn the repository into a multi-project workspace without breaking current scripts.

- add repository architecture
- record known P0/P1 risks
- add AI-agent development rules
- add shared garment-schema draft
- create project placeholders
- keep existing runtime folders in place

Exit condition: contributors can tell which project owns a change and what assumptions are unsafe.

---

## Phase 2 — Verify and stabilize the CLO runtime adapter

Goal: make RealBackend behavior match the installed CLO API contract.

Work:

1. inventory local `ApiStubFiles`
2. add a non-destructive API contract probe
3. verify pattern-information return types
4. verify sewing creation signatures
5. verify internal-line/InnerShape addressing
6. verify project/export methods
7. update mocks to match observed semantics
8. fail closed on unsupported API contracts

Exit condition: adapter contract is reproducible on the actual CLO installation.

---

## Phase 3 — Topology-aware state validation

Goal: remove count-only proof of safety.

Work:

- represent expected seam topology with semantic edge IDs
- inspect observed sewing relationships from CLO
- compare expected versus observed topology
- persist verification evidence
- distinguish API success from semantic verification

Exit condition: `SAFE_CHECKPOINT` cannot be reached solely from pattern/sewing counts.

---

## Phase 4 — DXF → garment-contract compiler

Goal: preserve identity from generated DXF metadata into CLO.

Work:

- compile pattern identities
- compile stable edge identities
- compile seam definitions
- compile mirror relations
- compile validation/tolerances
- remove unnecessary downstream rediscovery

Exit condition: a garment specification can be generated from DXF-side semantic data without manually reconstructing the same seam knowledge in CLO style files.

---

## Phase 5 — Regression garment matrix

Goal: expand styles safely.

Treat garments such as 09–22 as fixtures, not independent scripts.

Each fixture should provide:

- garment/source version
- expected pattern identities
- expected edge identities
- expected seam topology
- mirror relations
- allowed tolerances
- human-approved reference outcome

Exit condition: changes can be checked against all migrated garments.

---

## Phase 6 — CLO simulation and export

Goal: extend the verified state machine beyond sewing.

Potential states:

```text
SAFE_CHECKPOINT
→ ARRANGED
→ SIMULATED
→ EXPORTED
```

Each state requires post-action verification.

Exit condition: a known garment can reach a verified export artifact deterministically.

---

## Phase 7 — Blender Dressing v0.1

Goal: automate one known avatar + one approved CLO garment.

Work:

- import avatar
- import garment mesh/export
- map semantic garment assets
- place/associate garment
- configure minimal cloth/mesh setup
- save `.blend`
- render a verification image

Non-goal: universal automatic fitting.

Exit condition: one known avatar/garment pair produces a repeatable Blender scene and verification render.

---

## Later possibilities

- automatic fitting to multiple avatars
- avatar measurement adapters
- garment rendering/turntables
- animation
- Unity / Unreal export
- pattern recognition from existing DXF
- design parameterization
- batch garment pipelines
