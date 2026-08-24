# School-Skirt Suppression Policy — Evidence Audit

## Purpose

This audit asks one narrow production question:

> Given the already-computed global suppression requirement, do we have enough evidence to decide (1) how much belongs to front versus back and then (2) how each panel target is divided between darts and side-seam shaping?

It does **not** choose either production policy.

## Mathematical invariant already supported

The current draft computes:

```text
quarter_suppression = quarter_hip - quarter_waist
```

For one front + one back panel family, the global half-garment requirement is:

```text
half_garment_suppression = 2 × quarter_suppression
```

The generalized contract now separates two decisions:

```text
global suppression requirement
        ↓
PanelSuppressionTargets(front, back)
        ↓
per-panel dart + side-shaping allocation
```

Validation requires:

```text
front_target + back_target = 2 × quarter_suppression
```

followed by:

```text
front dart intake + front side shaping = front_target
back dart intake  + back side shaping  = back_target
```

These are conservation constraints. They do not choose the front/back ratio or the dart/side ratio.

## Internal repository evidence

### Suppression tests are fixtures, not drafting rules

Examples such as:

```text
front: dart 20 mm + side 25 mm
back:  dart 30 mm + side 15 mm
```

exist only to validate arithmetic, ranges and conservation. They have no production provenance.

**Classification:** `SYNTHETIC_TEST_FIXTURE`

### Dart-distribution and dart-plan values are plumbing fixtures

Values such as one 15 mm front dart, unequal 10/20 mm back darts, centre fractions `0.42 / 0.28 / 0.73`, and lengths `100/120 mm` prove validator and semantic-plumbing behavior only.

**Classification:** `SYNTHETIC_TEST_FIXTURE`

### Historical `school_skirt.py` values remain assumptions

The legacy prototype used one front dart, two back darts, a fixed 25 mm intake in legacy construction logic, and 100/120 mm dart lengths. The generator was Claude-generated / assumption-driven and is not independent production evidence.

**Classification:** `GENERATED_ARTIFACT` / `PARAMETRIC_ASSUMPTION`

### Purchased `1/2` patterns are out-of-family for this rule

The purchased/custom-made `1.dxf` and `2.dxf` plus native maker PRJ sources are independent production references, but their lower skirts belong to styled dresses with shell/lining differences and controlled fullness. They do not currently establish a basic-school-skirt body-suppression rule.

**Classification:** `HUMAN_CONFIRMED`, but `OUT_OF_FAMILY_FOR_THIS_RULE`.

## External drafting-system candidate

Winifred Aldrich's *Metric Pattern Cutting for Women's Wear* tailored-skirt block is retained as a named research candidate. The University of Manchester reproduction specifies, for that drafting system:

- one 20 mm front dart;
- two 20 mm back darts;
- a 25 mm-per-dart small-waist variant;
- an explicit forward side-seam placement;
- source-native waist/hip ease and waistline construction.

This proves that a complete named drafting system may define **asymmetric front/back panel suppression**, not that Aldrich is a universal production rule.

**Classification:** `EXTERNAL_NAMED_DRAFTING_SYSTEM_CANDIDATE`

**Promotion status:** research candidate only.

## Architecture finding from the Aldrich experiment

For the synthetic comparison body `waist=700 mm`, `hip=900 mm`, Aldrich's own ease produces canonical quarter suppression `55 mm`, while its source-native panel construction yields:

```text
front target = 47.5 mm
back target  = 62.5 mm
sum          = 110.0 mm
2 × 55       = 110.0 mm
```

The previous equal-quarter-per-panel validator rejected this even though global conservation was correct. The contract has therefore been generalized to support explicit `PanelSuppressionTargets`.

This architecture correction is now complete. It does **not** resolve the production policy.

## Current evidence decision

| Requirement | Status | Reason |
| --- | --- | --- |
| global suppression conservation | `SUPPORTED` | mathematical invariant + validator |
| non-negative panel targets | `SUPPORTED` | validation rule |
| front + back target total | `SUPPORTED` | must equal global half-garment requirement |
| front/back target ratio | `NEEDS_RULE` | no same-family production evidence |
| dart-vs-side allocation per panel | `NEEDS_RULE` | no same-family production evidence |
| individual dart intake | `NEEDS_RULE` | synthetic fixtures / external candidate only |
| dart count | `NEEDS_RULE` | legacy value not production-approved |
| body-proportion adaptation | `NEEDS_RULE` | external systems show it matters |

The production gate therefore correctly reports two separate blockers:

```text
panel_suppression_target_policy = NEEDS_RULE
suppression_allocation_policy   = NEEDS_RULE
```

## Promotion gate

A production suppression policy may be promoted only when all of the following are explicit:

```text
named garment family
+ body measurement contract
+ ease contract
+ front/back panel target policy
+ dart count
+ total dart intake per panel
+ side-shaping intake per panel
+ per-dart distribution
+ dart placement/length policy
+ fit validation on sample/toile
+ provenance for the chosen rules
```

Until then, safe-stop remains intentional.
