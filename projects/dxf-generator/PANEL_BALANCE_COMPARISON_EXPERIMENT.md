# Panel Balance Candidate Comparison — Controlled Example

Status: `RESEARCH_COMPARISON` / `NOT_PRODUCTION_RANKING`

This example records the first controlled comparison produced by the panel-balance comparison runner. It does not choose a production policy and does not generate pattern geometry or DXF.

## Shared experiment contract

Synthetic comparison body:

```text
body waist       = 700 mm
body hip         = 900 mm
waist-to-hip     = 200 mm
```

For an apples-to-apples comparison, both candidates use the same finished-garment contract:

```text
finished waist   = 710 mm
finished hip     = 930 mm
waist ease       = 10 mm
hip ease         = 30 mm
quarter suppression = 55 mm
```

Therefore the half-garment suppression requirement is:

```text
2 × 55 = 110 mm
```

## Candidate accounting

| Candidate | Front hip | Back hip | Front waist | Back waist | Front target | Back target | Conservation | Production status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| symmetric baseline | 232.500 | 232.500 | 177.500 | 177.500 | 55.000 | 55.000 | PASS | NOT_APPROVED |
| Aldrich standard | 225.000 | 240.000 | 177.500 | 177.500 | 47.500 | 62.500 | PASS | NOT_PRODUCTION_DEFAULT |

Both candidates account for the same finished waist and hip:

```text
symmetric: 55.0 + 55.0 = 110.0 mm
Aldrich:   47.5 + 62.5 = 110.0 mm
```

The comparison therefore isolates the front/back panel-balance decision instead of confounding it with different ease or finished measurements.

## What differs

The symmetric baseline keeps equal front/back hip spans:

```text
front hip = 232.5 mm
back hip  = 232.5 mm
```

The Aldrich candidate shifts panel balance toward the back:

```text
front hip = 225.0 mm
back hip  = 240.0 mm
```

In this controlled example both systems finish with the same front/back waist spans (`177.5 mm` each), so the hip-span difference appears directly in the suppression targets.

This is a geometry/accounting difference, not evidence that either candidate fits the target wearer better.

## Not instantiated

- `49/51` published method: not instantiated because the current audit does not yet encode a complete same-finished-contract front/back waist allocation. The repo must not guess the missing waist-side rule merely to fill the comparison table.

## Reproducible runner

```text
python tools/compare_skirt_panel_balance.py \
  --waist 700 \
  --hip 900 \
  --waist-to-hip 200 \
  --variant standard
```

Optional Markdown output:

```text
python tools/compare_skirt_panel_balance.py \
  --waist 700 \
  --hip 900 \
  --waist-to-hip 200 \
  --variant standard \
  --output panel-balance-report.md
```

## Interpretation boundary

A conservation `PASS` proves only that a candidate is mathematically compatible with the same finished-waist/finished-hip contract.

It does **not** prove:

- fit quality;
- comfort;
- correct side-seam placement for the target wearer;
- correct dart placement;
- correct dart-versus-side-shaping allocation;
- production suitability;
- factory approval.

No candidate is ranked or selected by this experiment.

## Next experimental step

The next useful comparison requires independent fit evidence rather than another arbitrary numeric candidate:

```text
same body measurements
+ same finished-garment contract
        ↓
research panel-balance candidates
        ↓
CLO toile / physical toile
        +
professional same-family basic skirt block if available
        ↓
compare fit and source geometry
```

Until such evidence exists:

```text
panel_suppression_target_policy = NEEDS_RULE
```
