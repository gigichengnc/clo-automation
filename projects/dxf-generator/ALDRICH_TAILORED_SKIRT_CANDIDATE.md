# Aldrich Tailored-Skirt Candidate Experiment

## Status

`RESEARCH_CANDIDATE` / `NOT_PRODUCTION_DEFAULT`

This experiment encodes the Winifred Aldrich tailored-skirt block as a named external drafting-system candidate. It does not change the production gate and it does not generate pattern geometry or DXF.

Primary source checked: University of Manchester reproduction of the Aldrich tailored-skirt block.

Source-native facts used:

- total waist ease: 10 mm;
- total hip ease: 30 mm;
- the side seam is moved forward;
- back hip span: quarter body hip + 15 mm;
- front hip span: the remaining quarter body hip span;
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
canonical average quarter suppression
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

The panel average is:

```text
(47.5 + 62.5) / 2 = 55 mm
```

So whole-garment suppression conservation is consistent with the canonical finished-waist/finished-hip arithmetic.

## Contract mismatch discovered

The current repo `SchoolSkirtSuppressionAllocation` validator expects **each** front and back panel to satisfy:

```text
dart_intake_total + side_shaping = quarter_suppression
```

For the example above it therefore expects both panels to equal `55 mm`.

The Aldrich tailored block instead gives:

```text
front = 47.5 mm
back  = 62.5 mm
mean  = 55.0 mm
```

This is not a failure of suppression conservation. It is a modelling mismatch caused by the Aldrich system deliberately moving the side seam forward and allocating different hip spans to front and back.

Therefore the current equal-quarter front/back suppression contract is too narrow to represent this named drafting system without distortion.

## Safe conclusion

Do not modify the production gate or promote Aldrich values as defaults.

Before any production policy is selected, the project should first decide whether its suppression contract needs to support explicit panel allocation, for example:

```text
total finished hip
        ↓
front/back panel hip allocation
        ↓
front suppression target
back suppression target
        ↓
per-panel dart + side-shaping allocation
```

rather than assuming identical quarter suppression on both panels.

This finding should be treated as an architecture question, not as evidence that Aldrich is the correct production block for the target school skirt.
