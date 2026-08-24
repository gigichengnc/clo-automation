# Semantic Vector Drawing — v0.1

A deterministic vector-drawing prototype for clean fashion flats and a controlled semantic front-end for the larger garment-building pipeline.

The AI-facing layer should describe **what exists**. This package owns **how illustration lines are drawn**.

```text
prompt / reference interpretation
        ↓
validated garment spec
        ↓
semantic drawing model
        ↓
front / back technical-flat view
        ↓
deterministic geometry
        ↓
geometry cleanliness validation
        ↓
SVG (authoritative illustration)
DXF (CAD-friendly artwork export)
```

## v0.1 semantic scope

Supported garment semantics:

- garment: `dress`
- front neckline: `round | v`
- sleeve: `sleeveless | short`
- silhouette: `a_line | straight`
- length: `mini | knee | midi | maxi`
- back neckline: `same_as_front | shallow_round`
- back closure: `none | centre_zip`
- front darts: `none | waist_pair` (optional; omitted = unspecified)
- back darts: `none | waist_pair` (optional; omitted = unspecified)
- front pockets: `none | patch_pair` (optional; omitted = unspecified)
- front buttons: `none | centre_row` (optional; omitted = unspecified)
- front princess seams: `none | shoulder_pair` (optional; omitted = unspecified)
- technical-flat view: `front | back`

Back generation requires `back_neckline` and `back_closure`. Optional construction fields distinguish **unknown/unspecified** from explicit `none`.

Stable semantic path IDs now include examples such as:

```text
outline.neckline
detail.dart.front.left
detail.dart.back.left
detail.pocket.front.left
detail.button.front.1
detail.princess.front.left
detail.back_closure.centre_zip
guide.centre_front
guide.centre_back
```

Left/right paired geometry is produced by deterministic mirroring where symmetry is intended.

## Construction-detail boundary

The small v0.1 construction vocabulary is deliberately illustrative:

```text
front_pockets = patch_pair
    -> symbolic paired patch-pocket outlines

front_buttons = centre_row
    -> symbolic centre-front button marks

front_princess_seams = shoulder_pair
    -> symbolic shoulder-to-waist princess seam lines
```

Back views explicitly strip all front-only dart, pocket, button and princess-seam paths. Front details must never leak into the back drawing simply because both views share one `DressSpec`.

As with the existing dart symbols, these coordinates are **technical-flat illustration policy only**. They are not production evidence for pocket dimensions, button spacing, princess-seam placement, dart intake, sewing allowances or pattern geometry.

## Front / back semantic boundary

```text
DressSpec
├── neckline
├── sleeve
├── silhouette
├── length
├── back_neckline
├── back_closure
├── front_darts
├── back_darts
├── front_pockets
├── front_buttons
└── front_princess_seams
```

A back view safe-stops if required back neckline/closure semantics are absent. The engine does not invent a zipper or back neckline.

## Natural-language examples

Front technical flat:

```text
round-neck short-sleeve midi A-line dress front waist darts front patch pockets centre-front buttons front shoulder princess seams
```

Chinese:

```text
圓領 短袖 中長 A字 連衣裙 前腰省 前貼袋 前中鈕扣 前肩公主線
```

Back technical flat:

```text
round-neck short-sleeve midi A-line dress shallow round back neckline centre-back zipper back waist darts
```

Conflicting semantics safe-stop instead of choosing one interpretation, for example `front patch pockets` together with `no front pockets`.

## Geometry cleanliness validation

`vector_drawing.validation.validate_drawing()` currently checks:

- zero-length / collapsed segments;
- duplicate geometry, including reversed duplicates;
- intra-path self-intersection;
- exact left/right mirror symmetry for paired semantic roles;
- expected semantic endpoint joins between neckline, shoulder, armhole/sleeve, side and hem;
- tangent continuity at smooth round-neck cubic joins.

## Important DXF boundary

The v0.1 DXF exporter writes **standard DXF R12 artwork geometry**. It is **not** DXF-AAMA / DXF-ASTM and must not be confused with the repository's factory garment-pattern pipeline.

SVG remains the authoritative illustration output.

## Production request bridge

The semantic front-end now has a strict downstream bridge at:

```text
projects/dxf-generator/garment_request_bridge.py
```

It translates `DressSpec` values into a `ProductionPatternRequest` assessment without copying any illustration coordinates:

```text
DressSpec
   ↓
semantic values only
   ↓
ProductionPatternRequest
   ↓
SUPPORTED / NEEDS_RULE / UNSUPPORTED
```

For example, `front_darts = waist_pair` does **not** reuse the technical-flat dart lines. It becomes a production requirement for a validated suppression policy, dart intake, length and placement. `short` sleeve similarly becomes a requirement for validated armhole and sleeve-cap rules.

The current general dress request is intentionally not production-ready because body measurements, numeric garment targets, material/layer policy and several drafting systems remain unresolved.

## Run

```bash
python -m vector_drawing.cli \
  --prompt "round-neck short-sleeve midi A-line dress front waist darts front patch pockets centre-front buttons front shoulder princess seams" \
  --view front \
  --validate \
  --svg out/dress-front.svg \
  --dxf out/dress-front.dxf
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Milestones

1. **DONE v0.1:** strict semantic prompt parser with safe-stop behavior;
2. **DONE v0.1:** geometry-cleanliness validator and optional CLI gate;
3. **DONE v0.1:** front/back technical-flat views;
4. **DONE v0.1:** explicit back neckline and closure semantics;
5. **DONE v0.1:** explicit front/back waist-dart semantics;
6. **DONE v0.1:** small front construction vocabulary: patch pockets, centre button row and shoulder princess seams;
7. **DONE bridge v0.1:** strict semantic `DressSpec` -> `ProductionPatternRequest` assessment with no illustration-coordinate transfer;
8. **NEXT:** supply validated production inputs/rules to one narrow garment family and make the first request pass selected drafting gates;
9. keep unsupported production semantics as safe-stops;
10. later add semantic raster/image understanding as an input adapter rather than a geometry generator.

The next phase is therefore back in the main garment-building engine: choose one narrow production family, provide real measurements and independently validated drafting rules, then generate pattern geometry only for the semantics that pass those gates.
