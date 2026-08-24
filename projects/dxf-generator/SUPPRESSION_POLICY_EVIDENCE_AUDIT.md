# School-Skirt Suppression Policy — Evidence Audit

## Purpose

This audit asks one narrow production question:

> Given the already-computed quarter suppression, do we have enough evidence to decide how much must be assigned to darts versus side-seam shaping for the first A-line skirt production pilot?

It does **not** choose a production policy. It classifies current evidence and identifies what would be required before a policy can be promoted.

## Mathematical invariant already supported

The current production pipeline already computes:

```text
quarter_suppression = quarter_hip - quarter_waist
```

and the suppression contract requires, for each panel:

```text
dart_intake_total + side_shaping = quarter_suppression
```

This is a conservation constraint. It says how much shaping must be accounted for; it does not say how to distribute that shaping.

## Internal repository evidence

### 1. Suppression validation tests are fixtures, not drafting rules

`tests/test_school_skirt_suppression.py` uses allocations such as:

```text
front: dart 20 mm + side 25 mm = 45 mm
back:  dart 30 mm + side 15 mm = 45 mm
```

Those numbers exist only to verify the validator's conservation, range and finite-number rules. They are synthetic examples and have no production provenance.

**Classification:** `SYNTHETIC_TEST_FIXTURE`

**Promotion status:** not eligible.

### 2. Dart-distribution tests are fixtures, not production evidence

`tests/test_school_skirt_dart_distribution.py` uses examples such as one 15 mm front dart and unequal 10/20 mm back darts. The purpose is to prove that the validator accepts unequal distributions when totals match and rejects invalid counts/totals.

The tests intentionally demonstrate that equal splitting is **not** a required invariant.

**Classification:** `SYNTHETIC_TEST_FIXTURE`

**Promotion status:** not eligible.

### 3. Dart-plan tests are semantic plumbing tests

`tests/test_school_skirt_dart_plan.py` carries sample values such as centre fractions `0.42`, `0.28`, `0.73` and lengths `100/120 mm` through the resolved semantic plan.

These values prove identity preservation and count matching only. They do not establish production placement or intake rules.

**Classification:** `SYNTHETIC_TEST_FIXTURE`

**Promotion status:** not eligible.

### 4. Historical `school_skirt.py` values remain generated assumptions

The legacy prototype used fixed assumptions including:

```text
front dart count  = 1
back dart count   = 2
fixed dart intake = 25 mm in legacy construction logic
front dart length = 100 mm
back dart length  = 120 mm
```

The historical generator was Claude-generated / assumption-driven and is not an independent production reference. Those values may be useful for regression but may not be promoted merely because the old generator produced a plausible skirt.

**Classification:** `GENERATED_ARTIFACT` / `PARAMETRIC_ASSUMPTION`

**Promotion status:** quarantined.

### 5. Purchased `1/2` patterns do not establish the target basic-skirt suppression policy

The purchased/custom-made `1.dxf` and `2.dxf` (with corresponding native maker PRJ sources) are independent production references, but their lower skirts are parts of styled dresses with shell/lining differences, controlled fullness and construction details that are not equivalent to the current simple fitted A-line school-skirt family.

They can validate general production concepts such as semantic piece identity, side-seam pairing, interface lengths and material layers. They do **not** currently provide a clean, independently resolved mapping from body waist/hip suppression to basic-skirt dart versus side-seam allocation.

**Classification:** `HUMAN_CONFIRMED` production references, but `OUT_OF_FAMILY_FOR_THIS_RULE`.

**Promotion status:** insufficient for this suppression policy.

## External drafting-system candidate

A useful named reference is Winifred Aldrich's *Metric Pattern Cutting for Women's Wear* tailored-skirt block, available through the University of Manchester.

Source:

- University of Manchester PDF: `https://www.sites.se.manchester.ac.uk/ademanchester/wp-content/uploads/sites/44/2025/04/Aldrich_2008_Skirt.pdf`

The tailored-skirt block specifies, for its own drafting system:

- one front dart of 2 cm;
- two back darts of 2 cm each;
- special handling for figures whose waist is small relative to hip, increasing dart width to 2.5 cm;
- explicit side-seam and waistline construction steps.

This is valuable because it proves that a complete, named drafting system can define concrete suppression-related decisions. It also shows that those decisions can vary with body proportion.

However, this does **not** establish a universal law such as:

```text
front dart = 20 mm
back darts = 20 mm each
```

for every person, fabric, style or production block.

**Classification:** `EXTERNAL_NAMED_DRAFTING_SYSTEM_CANDIDATE`

**Promotion status:** research candidate only.

## Important distinction

The repo must keep these three concepts separate:

```text
MATHEMATICAL INVARIANT
quarter suppression must be conserved

DRAFTING-SYSTEM RULE
how a named block distributes that suppression

PRODUCTION-APPROVED POLICY
what this project is authorised to use for the target garment family
```

A published drafting system can satisfy the second category without automatically satisfying the third.

## Current evidence decision

There is **not yet enough evidence** to promote a production `SchoolSkirtSuppressionPolicy` implementation.

Current state:

| Requirement | Status | Reason |
| --- | --- | --- |
| suppression conservation | `SUPPORTED` | mathematical invariant + validator |
| non-negative allocation | `SUPPORTED` | validation rule |
| front/back allocation ratio | `NEEDS_RULE` | no production-family evidence |
| dart-vs-side allocation | `NEEDS_RULE` | no production-family evidence |
| individual dart intake | `NEEDS_RULE` | synthetic fixtures only |
| dart count | `NEEDS_RULE` | legacy value not production-approved |
| body-proportion adaptation | `NEEDS_RULE` | external systems show it matters |

Therefore the production gate should continue to report:

```text
suppression_policy = NEEDS_RULE
```

## Safest next experiment

Do **not** implement the Aldrich values as defaults.

Instead create a quarantined, explicitly named research candidate only after the target measurements are fixed, for example:

```text
AldrichTailoredSkirtCandidate
```

Then compare candidate outputs against:

1. the same supplied body measurements;
2. the current semantic/geometry validators;
3. a CLO toile / physical muslin;
4. if possible, a commissioned basic A-line skirt block made for the same measurements.

The commissioned same-family block would be the strongest new evidence because its darts and side shaping could be measured directly and compared with the candidate system.

## Promotion gate

A suppression policy may be promoted only when all of the following are explicit:

```text
named garment family
+ body measurement contract
+ ease contract
+ dart count
+ total dart intake per panel
+ side-shaping intake per panel
+ per-dart distribution
+ dart placement/length policy
+ fit validation on sample/toile
+ provenance for the chosen rule
```

Until then, the current safe-stop is intentional and correct.
