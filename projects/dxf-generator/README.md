# DXF Generator

Status: production-pattern architecture under validation; legacy implementation remains in `DXF_AUTOMATION_V2/` during migration.

## Mission

Generate garment pattern geometry and stable semantic identities from explicit body, garment, drafting and production inputs.

## Owns

- garment/pattern geometry generation
- production-request validation
- drafting-rule gates
- DXF creation
- stable pattern IDs
- stable edge IDs
- geometric validation
- source measurement provenance

## Does not own

- technical-flat illustration coordinates
- CLO sewing calls
- CLO runtime indices
- Blender scene operations

## Semantic garment bridge

`garment_request_bridge.py` is the strict boundary between the illustration-facing `DressSpec` and production drafting.

```text
DressSpec semantics
        ↓
garment_request_bridge.py
        ↓
ProductionPatternRequest
        ↓
SUPPORTED / NEEDS_RULE / UNSUPPORTED
        ↓
validated drafting rules only
        ↓
pattern geometry
```

The bridge copies **semantic decisions only**. It never copies SVG/DXF artwork coordinates, technical-flat Bézier control points, drawing dimensions or symbolic construction-detail placement into production.

Examples:

```text
front_darts = none
    -> SUPPORTED as explicit absence

front_darts = waist_pair
    -> NEEDS_RULE
       suppression policy
       dart intake
       dart length
       dart placement

sleeve = short
    -> NEEDS_RULE
       armhole drafting policy
       sleeve-cap policy
       sleeve length
       biceps ease
```

The current general dress request is therefore expected to safe-stop before drafting until the missing body measurements and production rules are supplied and independently validated.

## First production family: A-line school skirt

`styles/school_skirt/production_gate.py` is the first narrow production-readiness gate.
It deliberately reuses the existing canonical pipeline instead of defining a second measurement model:

```text
BodyMeasurements
+ GarmentRequest
+ explicit waist/hip ease
+ explicit SchoolSkirtDraftingParameters
        ↓
existing validators
        ↓
SchoolSkirtSpec
        ↓
SchoolSkirtDraft
        ↓
production_gate.py
        ↓
SUPPORTED arithmetic
+ explicit production blockers
```

The gate requires ease and drafting parameters to be passed explicitly. It does not silently inherit prototype defaults for a production request.

Currently supported/checkable before geometry:

- canonical waist / hip / waist-to-hip input validation;
- explicit requested skirt length;
- explicit waist and hip ease;
- finished waist and hip resolution;
- quarter waist / hip arithmetic;
- quarter suppression arithmetic;
- hip and hem positions;
- explicit flare target from the supplied drafting parameters;
- basic dart-length versus hip-depth constructability checks.

These are **not** yet production-approved simply because they are numeric. The gate still blocks on:

```text
drafting parameter provenance
suppression allocation policy
dart-intake distribution policy
dart placement policy
side-seam geometry policy
hem policy
waist finish / waistband policy
closure / zipper policy
material + shell/lining policy
edge-specific seam allowance
semantic notches
grain / cut-on-fold constraints
```

Candidate or experimental implementations already present in the repository do not pass the gate merely by existing. They must be explicitly validated against production evidence or approved by the garment operator before promotion.

The gate stops before coordinate geometry and before DXF generation.

## Target output

```text
garment.dxf
garment.json
seams.json
validation.json
```
