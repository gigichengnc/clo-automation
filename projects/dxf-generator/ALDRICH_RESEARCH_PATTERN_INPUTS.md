# Aldrich Tailored-Skirt Research Pattern Inputs

## Status

`RESEARCH_PATTERN_INPUTS` / `NOT_FACTORY_READY`

This experiment carries the named Winifred Aldrich tailored-skirt candidate from suppression accounting into source-faithful semantic pattern inputs. It intentionally stops before coordinate curve generation and does not export DXF.

Primary source checked: University of Manchester reproduction of the Aldrich tailored-skirt block.

## Why this step was necessary

The generalized suppression contract already permits asymmetric front/back targets, but the older `panel_geometry_input.py` builder still copied the same `draft.quarter_waist` and `draft.quarter_hip` into both panels.

That would silently flatten a source-native Aldrich balance such as:

```text
front hip = 225 mm
back hip  = 240 mm
```

back into equal quarter widths.

The geometry-input layer now has an explicit-span builder:

```text
build_school_skirt_panel_geometry_input_from_spans(...)
```

which requires resolved front/back spans and provides no implicit symmetric fallback. The historical builder remains only as a compatibility path for earlier symmetric tests/experiments.

## Controlled example

Synthetic body:

```text
waist         = 700 mm
hip           = 900 mm
waist-to-hip  = 200 mm
skirt length  = 600 mm
```

Aldrich stated ease:

```text
finished waist = 710 mm
finished hip   = 930 mm
```

Standard source-native panel semantics:

| Semantic value | Front | Back |
| --- | ---: | ---: |
| finished waist span | 177.5 mm | 177.5 mm |
| hip span | 225.0 mm | 240.0 mm |
| dart intake total | 20.0 mm | 40.0 mm |
| side shaping | 27.5 mm | 22.5 mm |
| waist span before darts | 197.5 mm | 217.5 mm |
| suppression target | 47.5 mm | 62.5 mm |

The explicit panel geometry input preserves these asymmetric values rather than reconstructing them from a single quarter-width scalar.

## Source-faithful dart semantics

The source provides more detail than the repo's generic prototype parameters can represent.

### Front

```text
count = 1
intake = 20 mm standard / 25 mm small-waist variant
centre = 1/3 along the centre-to-side waist line
length = 100 mm
```

### Back

```text
count = 2
centres = 1/3 and 2/3 along the centre-to-side waist line
standard intakes = 20 mm + 20 mm
small-waist intakes = 25 mm + 25 mm
lengths = 140 mm and 125 mm
```

The unequal back-dart lengths are significant. The historical generic `SchoolSkirtDraftingParameters.back_dart_length` stores only one back length, so the research adapter bypasses that lossy abstraction and creates per-dart `ResolvedDart` records directly.

This is a research-path preservation decision, not a production-policy promotion.

## Straight-block boundary

This Aldrich source is a tailored **straight-skirt block**, not the final A-line style transformation.

The source squares the hip-side construction down to the hemline. Therefore the research semantic inputs preserve the same horizontal hip/hem endpoint spans before the unresolved side-seam curve is applied.

No A-line flare is added here.

## What is still unresolved

The source gives qualitative construction instructions that are not yet a unique deterministic curve algorithm in this repo:

```text
WAIST_CURVE_UNRESOLVED
- draw the waistline with a slight curve

SIDE_SEAM_CURVE_UNRESOLVED
- draw the side seam curving it outward by 5 mm
```

Those statements establish construction intent, but not a unique Bézier/control-point/radius representation. The engine therefore does not guess a curve.

Additional blockers remain:

```text
A_LINE_FLARE_NOT_APPLIED
PRODUCTION_TRANSFORMS_UNRESOLVED
```

The latter includes seam allowance, notches, grain, closure, material-layer rules and factory DXF serialization.

## Current pipeline

```text
body measurements
+ explicit skirt length
+ explicit Aldrich variant
        ↓
Aldrich named panel balance
        ↓
front/back suppression targets
        ↓
source-native dart + side allocation
        ↓
source-native per-dart positions/lengths
        ↓
explicit asymmetric PanelGeometryInput
        ↓
STOP: unresolved coordinate curve policies
```

## What a PASS means

`semantic_inputs_valid = True` means only:

- the named candidate satisfies the generalized suppression contract;
- panel spans preserve the candidate's front/back balance;
- dart intake and side shaping reconcile with those spans;
- per-dart semantics are internally consistent.

It does **not** mean:

- the skirt fits the target wearer;
- Aldrich is the project's production drafting system;
- the side-seam/waist curves are solved;
- the pattern is A-line;
- the pattern is ready for CLO sewing;
- the pattern is factory-ready.

## Safest next experiment

Do not choose an arbitrary final curve.

Use the existing side-seam candidate infrastructure to create multiple explicitly named **research curve realizations** that all respect the source's 5 mm outward-curving instruction, then compare their geometric consequences without ranking one as production-correct.

For example:

```text
same Aldrich semantic inputs
        ↓
linear / quadratic / piecewise named research candidates
        ↓
curve measurements + continuity checks
        ↓
controlled CLO toile candidates
```

The waist curve should remain a separate candidate family rather than being bundled invisibly into the side-seam experiment.
