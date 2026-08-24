# Aldrich Tailored-Skirt Candidate Experiment

## Status

`RESEARCH_CANDIDATE` / `NOT_PRODUCTION_DEFAULT`

This experiment encodes the Winifred Aldrich tailored-skirt block as a named external drafting-system candidate. It does not select a production policy and it does not generate pattern geometry or DXF.

Primary source checked: University of Manchester reproduction of the Aldrich tailored-skirt block.

Source-native facts used:

- total waist ease: 10 mm;
- total hip ease: 30 mm;
- the side seam is moved forward;
- back hip span: quarter body hip + 15 mm;
- front hip span: the remaining half-garment hip span;
- standard variant: one 20 mm front dart and two 20 mm back darts;
- small-waist variant: 25 mm per dart, with no numeric source threshold for automatic selection.

The code is isolated at:

```text
styles/school_skirt/research/aldrich_tailored_candidate.py
```

## Example comparison

For a synthetic comparison body:

```text
waist = 700 mm
hip   = 900 mm
```

Aldrich's stated ease gives:

```text
finished waist = 710 mm
finished hip   = 930 mm
canonical quarter suppression
= 930/4 - 710/4
= 55 mm
```

The standard Aldrich source-native panel construction gives:

```text
FRONT
hip span             = 225.0 mm
pre-dart waist span  = 197.5 mm
front dart           = 20.0 mm
side shaping         = 27.5 mm
total suppression    = 47.5 mm
finished waist span  = 177.5 mm

BACK
hip span             = 240.0 mm
pre-dart waist span  = 217.5 mm
back darts            = 20.0 + 20.0 mm
side shaping         = 22.5 mm
total suppression    = 62.5 mm
finished waist span  = 177.5 mm
```

The half-garment total is:

```text
47.5 + 62.5 = 110 mm
2 × canonical quarter suppression = 2 × 55 = 110 mm
```

So whole half-garment suppression conservation is consistent with the canonical finished-waist/finished-hip arithmetic even though the front/back panel targets are asymmetric.

## Architecture finding resolved

The previous repo suppression validator required **each** front and back panel to equal the same `quarter_suppression`. That historical equal-quarter assumption could not represent a drafting system that deliberately shifts the side seam and allocates different front/back hip spans.

The core contract has now been generalized into two explicit decisions:

```text
global suppression requirement
        ↓
PanelSuppressionTargets(front, back)
        ↓
per-panel dart + side-shaping allocation
```

Validation now requires:

```text
front_target + back_target
= 2 × quarter_suppression
```

and then independently:

```text
front dart + front side shaping = front_target
back darts + back side shaping  = back_target
```

Under this generalized contract the source-native Aldrich example is mathematically compatible:

```text
front target = 47.5 mm
back target  = 62.5 mm
allocation validation = PASS
```

The research candidate still records `legacy_equal_quarter_mismatch = True` so the historical modelling limitation remains visible rather than being erased.

## What this does NOT prove

Passing the generalized contract does not promote Aldrich into a production rule. It proves only that the contract can faithfully represent an asymmetric named drafting system without distorting it.

The production gate therefore still safe-stops on two separate decisions:

```text
panel_suppression_target_policy = NEEDS_RULE
suppression_allocation_policy   = NEEDS_RULE
```

A production-approved school-skirt policy still requires same-family evidence or explicit human approval, plus fit/toile validation.
