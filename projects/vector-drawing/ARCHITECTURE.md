# Semantic Vector Drawing Architecture

## Core rule

AI interprets intent; deterministic geometry draws the line.

```text
natural-language prompt / image
        ↓
INTERPRETER (probabilistic)
        ↓
validated semantic spec
        ↓
GEOMETRY ENGINE (deterministic)
        ↓
semantic paths + constraints
        ↓
renderers
  ├─ SVG — illustration master
  ├─ DXF — CAD-friendly artwork
  ├─ PDF — future print renderer
  └─ PNG — future raster preview
```

The renderer must never ask a model to invent intermediate pixels.

## Separation from factory patterns

Fashion-flat geometry and production-pattern geometry may share low-level primitives (`Point`, curve evaluation, mirroring, offsets, intersections), but they do not share semantic meaning automatically.

Examples:

```text
fashion flat: outline.armhole.left
production:   shell.front.armhole
```

Similar names do not imply that the illustrated curve is a cut/sew pattern edge.

The vector project therefore cannot silently feed illustration geometry into mass-production DXF.

## v0.1 contracts

### Interpreter contract

Input may be free-form later, but the deterministic engine receives only a validated structure, e.g.

```json
{
  "garment": "dress",
  "neckline": "round",
  "sleeve": "short",
  "silhouette": "a_line",
  "length": "midi"
}
```

Unknown values safe-stop.

### Semantic geometry contract

Every path has:

- stable `path_id`;
- semantic `role`;
- display `layer`;
- deterministic vector commands.

Symmetric components are mirrored mathematically, not redrawn independently.

### Renderer contract

SVG preserves cubic curves directly.

DXF v0.1 is an artwork/export adapter only. Curves are sampled at a deterministic resolution into standard R12 polylines. It is not a production garment interchange file.

## Shared-kernel candidates with `dxf-generator`

Good candidates to share later:

- finite-point validation;
- rigid transforms;
- exact mirroring;
- cubic/spline evaluation;
- polyline/path length;
- intersections;
- offset geometry;
- continuity tests;
- semantic IDs.

Do **not** share without translation:

- seam identity;
- seam allowance policy;
- cut quantity;
- grading;
- fabric/material role;
- CLO sewing relationships;
- factory release states.

## Evidence boundary

A clean fashion flat proves only that the vector renderer obeys its semantic spec. It does not prove garment fit or manufacturability.
