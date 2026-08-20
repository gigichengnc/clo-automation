# DXF Generator

Status: architecture placeholder; current implementation remains in `DXF_AUTOMATION_V2/` during migration.

## Mission

Generate garment pattern geometry and stable semantic identities.

## Owns

- garment/pattern geometry generation
- DXF creation
- stable pattern IDs
- stable edge IDs
- geometric validation
- source measurement provenance

## Does not own

- CLO sewing calls
- CLO runtime indices
- Blender scene operations

## Target output

```text
garment.dxf
garment.json
seams.json
validation.json
```
