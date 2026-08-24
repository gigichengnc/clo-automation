# Aldrich Side-Seam Curve Candidate Comparison

## Status

`RESEARCH_CURVE_COMPARISON` / `NO_PRODUCTION_SELECTION`

This experiment carries the source-faithful Aldrich tailored-skirt semantics into sampled coordinate side-seam curves without promoting any curve family to production use.

The source instruction under study says to curve the side seam outward by 5 mm, but it does not uniquely specify a mathematical curve family. The repo therefore compares explicit named interpretations rather than hiding one arbitrary curve as a default.

## Controlled example

Synthetic body and experiment inputs:

```text
body waist       = 700 mm
body hip         = 900 mm
waist-to-hip     = 200 mm
skirt length     = 600 mm
Aldrich variant  = standard
```

Source-faithful semantic panel anchors before the unresolved side-seam curve:

```text
FRONT
side waist = (197.5,   0.0)
hip side   = (225.0, -200.0)
hem side   = (225.0, -600.0)

BACK
side waist = (217.5,   0.0)
hip side   = (240.0, -200.0)
hem side   = (240.0, -600.0)
```

## Three research interpretations

### 1. `linear_reference`

Two straight segments:

```text
side waist → hip side → hem side
```

This is a geometry baseline only. It preserves the semantic hip anchor exactly but contains a direction change at the hip.

### 2. `single_quadratic_5mm`

One quadratic Bezier from side waist directly to hem side. Its midpoint control construction creates a maximum 5 mm chord-normal outward deviation.

This produces one continuous curve but deliberately does **not** constrain the curve to pass through the semantic hip anchor.

### 3. `piecewise_quadratic_5mm`

```text
side waist → quadratic → hip side → linear → hem side
```

The upper waist-to-hip quadratic has a maximum 5 mm chord-normal outward deviation. The lower hip-to-hem segment remains linear, so the source-native hip anchor is retained explicitly.

## Controlled geometric snapshot

For the inputs above, the deterministic candidate definitions give approximately:

| Candidate | Panel | Length mm | Max outward deviation mm | Hip anchor error mm | Hip preserved | Hip tangent angle deg |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| linear reference | front | 601.882 | 0.000 | 0.000 | yes | 7.829 |
| linear reference | back | 601.262 | 0.000 | 0.000 | yes | 6.419 |
| single quadratic 5 mm | front | 600.741 | 5.000 | 14.180 | no | n/a |
| single quadratic 5 mm | back | 600.533 | 5.000 | 10.874 | no | n/a |
| piecewise quadratic 5 mm | front | 602.211 | 5.000 | 0.000 | yes | 2.228 |
| piecewise quadratic 5 mm | back | 601.592 | 5.000 | 0.000 | yes | 0.800 |

Front/back sampled side-seam length differences are approximately:

```text
linear reference          back - front = -0.620 mm
single quadratic 5 mm     back - front = -0.208 mm
piecewise quadratic 5 mm  back - front = -0.619 mm
```

These values are measurements, not acceptance thresholds.

## What the experiment tells us

The candidates expose different modelling consequences:

- the linear reference preserves all semantic anchors but has a visible tangent change at the hip;
- the single quadratic removes the explicit hip join but misses the semantic hip anchor by roughly 11–14 mm in this example;
- the piecewise quadratic preserves the hip anchor and reduces the sampled tangent-angle discontinuity relative to the straight reference, while still leaving a non-zero join angle.

This does **not** establish that the piecewise candidate is the correct production curve. It only shows why preserving semantic construction points and measuring continuity separately are useful.

## Reproducible CLI

```text
python tools/compare_aldrich_side_seam_curves.py \
  --waist 700 \
  --hip 900 \
  --waist-to-hip 200 \
  --skirt-length 600 \
  --variant standard
```

Optional Markdown output:

```text
python tools/compare_aldrich_side_seam_curves.py \
  --waist 700 \
  --hip 900 \
  --waist-to-hip 200 \
  --skirt-length 600 \
  --variant standard \
  --output side-seam-report.md
```

## Interpretation boundary

No candidate is ranked or selected.

A smaller front/back length difference, a smaller tangent angle, or exact hip-anchor passage does not by itself prove better fit, comfort, or production correctness.

The following remain unresolved:

```text
WAIST_CURVE_UNRESOLVED
SIDE_SEAM_CURVE_PRODUCTION_RULE_UNRESOLVED
A_LINE_FLARE_NOT_APPLIED
PRODUCTION_TRANSFORMS_UNRESOLVED
```

No seam allowance, notches, grain, closure, material-layer policy, AAMA/ASTM export, or factory DXF is created by this experiment.

## Next useful step

The next step should not be to pick the numerically smallest curve metric as a winner. The useful next experiment is to build **research-only full panel coordinate outlines** by combining:

```text
centre edge
+ source-faithful dart geometry
+ one named side-seam candidate
+ an explicitly quarantined waist-curve candidate
+ straight research hem
```

Those complete research outlines can then be exported to a non-production SVG or diagnostic DXF for CLO/toile comparison while retaining `NOT_FACTORY_READY` status.
