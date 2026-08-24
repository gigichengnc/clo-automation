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

## Target output

```text
garment.dxf
garment.json
seams.json
validation.json
```
