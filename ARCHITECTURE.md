# Garment Automation Lab — Architecture

## 1. Purpose

This repository is a multi-project workspace for automating digital garment workflows.

The repository should not be centered on one application. CLO, Blender, and future tools are runtimes that consume the same garment information.

The architectural center is the **digital garment specification**:

- pattern identity
- edge identity
- seam topology
- geometry metadata
- validation state
- asset provenance

The same semantic identity should survive from DXF generation through sewing, simulation, export, dressing, and rendering.

---

## 2. Core principle

> Geometry is generated once. Identity is preserved throughout the pipeline. Applications consume the same garment specification instead of rediscovering garment structure independently.

A downstream tool must not throw away known identities and then infer them again from weak signals such as edge length or line index unless the specification explicitly allows it.

---

## 3. Project layout

```text
clo-automation/
├── README.md
├── ARCHITECTURE.md
├── KNOWN_ISSUES.md
├── AGENTS.md
│
├── projects/
│   ├── dxf-generator/
│   ├── clo-autosewing/
│   └── blender-dressing/
│
├── shared/
│   ├── garment-schema/
│   ├── geometry/
│   └── validation/
│
├── docs/
│   ├── development-roadmap.md
│   ├── migration-plan.md
│   └── clo-api-verification.md
│
├── DXF_AUTOMATION_V2/       # existing implementation; migrate gradually
└── CLO_Agent_v0.1/          # existing implementation; migrate gradually
```

Existing runtime folders stay in place during Phase 1. They should be migrated only after import paths, tests, and fixtures are stable.

---

## 4. Project boundaries

### 4.1 DXF Generator

Responsibility:

```text
measurements / garment parameters
              ↓
      pattern geometry
              ↓
       DXF + metadata
```

The DXF generator owns geometric construction and stable semantic IDs.

Expected outputs may include:

```text
garment.dxf
garment.json
seams.json
validation.json
```

It should not contain CLO-specific sewing calls or Blender-specific dressing logic.

### 4.2 CLO AutoSewing

Responsibility:

```text
garment specification
        +
current CLO state
        ↓
pattern reconciliation
        ↓
edge reconciliation
        ↓
topology validation
        ↓
sewing / simulation / export
```

The CLO project should act as an application adapter and state machine. It should consume semantic garment data rather than encode garment-specific knowledge inside the engine.

### 4.3 Blender Dressing

Planned responsibility:

```text
CLO / mesh export
       +
avatar / body
       ↓
import + garment association
       ↓
fit / attach / simulation setup
       ↓
rig / animation / render pipeline
```

The Blender project should reuse garment IDs and exported metadata where possible.

It should not redefine the garment's seam topology independently.

---

## 5. Shared garment contract

All projects should converge on one versioned garment contract.

Example conceptual structure:

```json
{
  "schema_version": "0.1.0",
  "garment_id": "school_skirt_01",
  "patterns": [
    {
      "id": "front_left",
      "edges": [
        {
          "id": "front_left.side",
          "length_mm": 327.4
        }
      ]
    }
  ],
  "seams": [
    {
      "id": "left_side_seam",
      "a": "front_left.side",
      "b": "back_left.side"
    }
  ]
}
```

IDs are semantic references, not transient array indices.

Tool-specific indices may be stored as runtime reconciliation data, but they must not replace semantic IDs.

---

## 6. Identity preservation

Preferred flow:

```text
DXF
 ↓
pattern ID + stable edge ID
 ↓
garment specification
 ↓
CLO pattern/edge reconciliation
 ↓
verified seam topology
 ↓
CLO simulation/export
 ↓
Blender import/dressing
```

Avoid this flow:

```text
DXF knows exact edge
 ↓
identity discarded
 ↓
CLO guesses edge from length/index
```

Length, centroid, index, and orientation may be useful reconciliation signals, but they are not the semantic source of truth.

---

## 7. Validation philosophy

Automation should be conservative.

```text
known + verified       → continue
known but inconsistent → stop
ambiguous              → stop
missing                → stop
API mismatch           → stop
```

A safe stop is preferable to a plausible but incorrect garment.

Counts such as `pattern_count` or `sewing_group_count` are sanity checks only. They are not proof of correct topology.

---

## 8. Runtime adapters

Each external application should be isolated behind an adapter boundary.

Examples:

```text
Garment core
   ├── DXF adapter
   ├── CLO adapter
   └── Blender adapter
```

This prevents CLO API changes from changing garment semantics and prevents Blender implementation choices from leaking into the DXF generator.

---

## 9. Human ground truth

Some decisions remain human-authoritative:

- whether the garment visually matches the intended design
- whether a pattern piece has the intended semantic role
- whether a seam is physically/design-wise correct when source data is incomplete
- whether source measurements may be changed
- whether a failed/ambiguous automated match may be overridden

The automation may report uncertainty. It must not silently replace missing garment knowledge with a guess.

---

## 10. Long-term pipeline

```text
Garment parameters
        ↓
DXF Generator
        ↓
Garment Contract
        ↓
CLO AutoSewing
        ↓
CLO simulation / export
        ↓
Blender Dressing
        ↓
render / animation / engine export
```

Future projects can attach to the garment contract without turning the CLO agent into a monolith.
