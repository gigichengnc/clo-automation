# DXF 1 / DXF 2 — Production Reference Audit

## Purpose

`1.dxf` and `2.dxf` are not synthetic examples. The garment owner has confirmed that both files are patterns for garments actually ordered from a custom clothes maker and made into real clothes.

They therefore serve as **production reference patterns** for the parametric DXF rebuild.

This document deliberately separates direct production evidence from measurements that survive only through old parser scripts or derived notes. No derived value is promoted to a universal drafting rule without direct re-measurement from the original DXF and comparison across references.

## Evidence levels

- **HUMAN_CONFIRMED** — garment provenance or intent confirmed by the garment owner.
- **DIRECT_DXF** — measured directly from the original `1.dxf` or `2.dxf` file in the current audit.
- **DERIVED_LEGACY** — a value recorded by an older parser/script that previously consumed the original DXF, but not yet re-measured from the source file in this audit.
- **UNVERIFIED** — required production fact that has not yet been established.

A `DERIVED_LEGACY` value may guide the next measurement pass but must not become a production constant by itself.

## Source status

| Reference | Status | Meaning |
| --- | --- | --- |
| `1.dxf` | HUMAN_CONFIRMED | custom-made garment pattern; real garment was produced |
| `2.dxf` | HUMAN_CONFIRMED | custom-made garment pattern; real garment was produced |

The original DXF bytes are not currently available to this audit session, so no geometry fact below is marked `DIRECT_DXF` yet.

## Current surviving measurements

### `1.dxf`

| Observation | Value | Evidence | Notes |
| --- | ---: | --- | --- |
| skirt profile classification | circular / fuller skirt | DERIVED_LEGACY | old generator annotation only; direct outline still required |
| skirt length | 569 mm | DERIVED_LEGACY | recorded as `PROF_A.length` |
| hem-to-waist ratio | 2.84 | DERIVED_LEGACY | recorded as `PROF_A.ratio`; exact measurement method must be reconstructed |

### `2.dxf`

| Observation | Value | Evidence | Notes |
| --- | ---: | --- | --- |
| skirt profile classification | A-line | DERIVED_LEGACY | old generator annotation only; direct outline still required |
| skirt length | 681 mm | DERIVED_LEGACY | recorded as `PROF_B.length` |
| hem-to-waist ratio | 2.27 | DERIVED_LEGACY | recorded as `PROF_B.ratio`; exact measurement method must be reconstructed |
| bodice/block lower opening | 907 mm | DERIVED_LEGACY | old script labels this as measured `2.dxf` waist/block lower opening; semantic meaning must be checked against original pieces |
| neckline / collar-seat reference | 455 mm | DERIVED_LEGACY | old derivative scripts use this with the `2.dxf` block; source path must be re-measured |
| armhole reference | 520–526 mm | DERIVED_LEGACY | two surviving scripts disagree, so this remains inconsistent and cannot be promoted |

## Surviving structural evidence from `2.dxf`

Legacy scripts previously parsed named pieces from `2.dxf`, including identifiers corresponding to:

- front centre
- left front side
- right front side
- back centre
- back side
- back yoke
- sleeve
- collar
- collar stand
- cuff

This is evidence that `2.dxf` was used as a multi-piece upper-body production reference, not merely as a skirt-ratio source. Exact piece count, geometry, mirror relations, edge identities and seam topology remain `UNVERIFIED` until the original DXF is directly inspected.

## House-format observations

A legacy DXF writer states that it was designed to follow the `1.dxf / 2.dxf` house convention:

- units: mm
- layer 1: cut line / annotation
- layer 2: turn points
- layer 3: curve points
- layer 4: notches
- layer 7: grainline
- layer 14: seam / net line
- common seam allowance recorded by the generator: 9.5 mm

These are **DERIVED_LEGACY**, not yet `DIRECT_DXF`. In particular, seam allowance must be measured from source cut/seam geometry rather than accepted from the legacy writer comment.

## Direct measurement checklist

When the original files are available, measure facts first and interpret later.

For each DXF:

1. file units, encoding, AAMA/ASTM structure and layer map
2. pattern-piece inventory and quantity/mirror information
3. cut-line and net/seam-line outlines separately
4. piece bounding dimensions and closed/open contour status
5. waist seam lengths
6. hip level / waist-to-hip depth where geometrically identifiable
7. hem lengths / circumferences
8. centre-front / centre-back lengths
9. side-seam lengths, separately front/back
10. side-seam coordinates and curvature samples
11. dart count, intake, apex, length and placement
12. waistband piece count, dimensions and overlap
13. centre-back / zipper construction geometry
14. seam allowance by semantic edge, including hem allowance
15. notches, drill marks, grainlines and internal lines

## Promotion rule

No production rule should be inferred from a single surviving number.

Use this progression:

```text
HUMAN_CONFIRMED reference
        ↓
DIRECT_DXF measurement
        ↓
cross-reference comparison
        ↓
explicit hypothesis
        ↓
parametric rule only if supported
```

Examples:

- matching 25 mm dart intakes in two files do **not** automatically mean `dart_intake = 25 mm` universally;
- matching seam allowance values do not establish that every edge uses the same allowance;
- a front/back side-seam mismatch must be preserved and reported before deciding whether it is intentional, grading-related, construction-related or erroneous.

## Current safe conclusion

`1.dxf` and `2.dxf` are valid **production reference sources**, but the currently recoverable numerical observations are still mostly `DERIVED_LEGACY`. They can be used to design the measurement pass and regression fixtures, but not yet as final production constants for the new engine.
