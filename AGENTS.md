# AI Agent Development Rules

This repository is developed collaboratively by a human garment operator and coding agents such as Codex, Claude Code, and ChatGPT.

The purpose of this file is to keep agents from making plausible but unsafe assumptions about garment geometry or application APIs.

---

## 1. Sources of truth

Use the following precedence.

### Garment intent / appearance

**Human-approved garment source and visual verification** are authoritative.

### Pattern and seam semantics

The versioned garment specification and human-approved DXF/seam data are authoritative.

### CLO runtime API

The API/stub files shipped with the installed CLO version are the runtime source of truth.

Public online documentation is useful for comparison and upgrade review, but the installed runtime must be verified before changing the real adapter.

### Blender runtime API

The Blender version used by the project and its corresponding Python API documentation are authoritative.

---

## 2. Never guess garment semantics

Agents must not silently infer:

- which pattern is front/back from array position
- left/right from line index
- sewing partners from similar edge length alone
- mirror relationships from naming coincidence alone
- garment measurements not present in approved source data
- a safe checkpoint from counts alone

If semantic identity is missing or ambiguous, stop and surface the ambiguity.

---

## 3. Safe-stop rule

Use this default:

```text
verified     → continue
inconsistent → stop
ambiguous    → stop
missing      → stop
API mismatch → stop
```

Do not introduce a fallback merely to keep automation moving.

---

## 4. Preserve semantic IDs

Pattern IDs, edge IDs, and seam IDs must survive across stages.

Do not replace semantic IDs with tool-local indices.

Tool-local values such as:

- CLO pattern index
- CLO line index
- Blender object name/index

are reconciliation data only.

Preferred model:

```text
semantic ID → runtime locator → observed result → verification
```

---

## 5. Do not modify source measurements casually

If a pattern edge mismatch appears, do not automatically change dimensions to make sewing pass.

Instead:

1. report the mismatch
2. identify whether it is source geometry, scale, mirror, import, or seam-selection related
3. preserve original measurements
4. require explicit approval before changing garment geometry

---

## 6. CLO API changes

Before editing the real CLO backend:

1. identify installed CLO/API version
2. inspect the matching shipped API stubs
3. verify function names, signatures, return types, and index models
4. add/update a test or non-destructive contract probe
5. keep mock and real backend behavior semantically aligned

Never update the real backend from memory alone.

---

## 7. Blender changes

Blender automation belongs under `projects/blender-dressing/` unless it is genuinely shared logic.

Do not place Blender-specific scene/object operations into the garment schema.

The schema may describe semantic assets and desired relationships; the Blender adapter decides how to implement them.

---

## 8. Project ownership boundaries

### `projects/dxf-generator`

Owns:

- pattern geometry generation
- DXF writing
- stable pattern/edge identity
- geometric validation

Does not own CLO sewing or Blender scene logic.

### `projects/clo-autosewing`

Owns:

- CLO scanning/reconciliation
- verified seam creation
- CLO state machine
- simulation/export orchestration

Does not redefine source garment geometry.

### `projects/blender-dressing`

Owns:

- garment/avatar import
- Blender object reconciliation
- fitting/attachment setup
- cloth/rig/render workflow

Does not redefine source seam topology.

### `shared/`

Contains only application-neutral contracts/utilities.

If code imports CLO or `bpy`, it normally does not belong in `shared/`.

---

## 9. Agent collaboration model

Recommended roles:

### Human operator

- garment ground truth
- CLO/Blender visual verification
- approves semantic corrections and measurement changes

### Primary implementer (for example Codex)

- implements one scoped issue/feature
- adds tests
- avoids unrelated refactors

### Adversarial reviewer (for example Claude Code)

- reviews diff rather than independently rewriting the same feature
- searches for unsafe assumptions, ambiguity, regression risk, API mismatch

### Architecture/API reviewer (for example ChatGPT)

- checks cross-project contracts
- verifies architecture against current external APIs/docs when needed
- identifies missing validation and unsafe coupling

Roles are suggestions, not vendor requirements. The important rule is to avoid two agents making uncoordinated edits to the same feature simultaneously.

---

## 10. Required change discipline

For each non-trivial change, state:

- project affected
- garment fixtures affected
- semantic contract changed? yes/no
- external API contract changed? yes/no
- tests added/updated
- new ambiguity/fallback introduced? yes/no

Any new fallback must be documented explicitly.

---

## 11. Definition of "safe"

An automation step is not safe merely because it completed without an exception.

A safe checkpoint requires evidence that the observed garment state matches the expected semantic state.
