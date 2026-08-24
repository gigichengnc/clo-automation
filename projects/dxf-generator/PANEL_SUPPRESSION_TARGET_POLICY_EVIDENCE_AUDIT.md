# School-Skirt Panel Suppression Target Policy — Evidence Audit

## Purpose

This audit asks one production question only:

> Once global waist-to-hip suppression is known, how should the required suppression be assigned between the front and back panel families?

It does **not** choose a production default. It records the evidence needed by the new generalized contract:

```text
global suppression requirement
        ↓
PanelSuppressionTargets(front, back)
        ↓
per-panel dart + side-shaping allocation
```

## Current mathematical contract

The policy-independent draft still computes:

```text
quarter_suppression = quarter_hip - quarter_waist
```

The generalized suppression validator now requires only whole half-garment conservation:

```text
front_target + back_target = 2 × quarter_suppression
```

Each target is later resolved independently:

```text
front darts + front side shaping = front_target
back darts  + back side shaping  = back_target
```

There is deliberately no implicit `front == back` rule.

## Why panel targets are a separate drafting decision

A front/back target is not determined by waist and hip circumference alone. It also depends on how a drafting system allocates the half-garment hip and waist spans between the front and back pattern families.

Two systems can conserve the same finished waist and hip while placing the side seam differently and therefore requiring different front/back suppression targets.

## Candidate A — symmetric architectural baseline

A neutral mathematical baseline is:

```text
front_target = quarter_suppression
back_target  = quarter_suppression
```

This is useful as an architectural baseline and reproduces the repo's historical equal-quarter contract.

It is **not** independent production evidence and must not be described as a universal fit rule.

**Classification:** `ARCHITECTURAL_BASELINE`

**Production status:** `NOT_APPROVED`.

## Candidate B — Winifred Aldrich tailored-skirt block

The University of Manchester reproduction of Winifred Aldrich's tailored-skirt block provides a named external drafting system in which the side seam is moved forward and the back receives more hip width than the front.

The existing quarantined research module records:

```text
back hip span = quarter body hip + 15 mm
front hip span = remaining front span
```

For the synthetic comparison body used in the repo:

```text
body waist = 700 mm
body hip   = 900 mm
Aldrich finished waist = 710 mm
Aldrich finished hip   = 930 mm
quarter suppression    = 55 mm
```

The source-native standard block gives:

```text
front target = 47.5 mm
back target  = 62.5 mm

47.5 + 62.5 = 110 mm = 2 × 55 mm
```

So it conserves the same whole half-garment suppression while using an asymmetric front/back balance.

**Classification:** `EXTERNAL_NAMED_DRAFTING_SYSTEM_CANDIDATE`

**Production status:** `RESEARCH_CANDIDATE / NOT_PRODUCTION_DEFAULT`.

## Candidate C — explicit 49/51 front/back hip split

A published basic-skirt drafting tutorial by Anicka Design explicitly splits the half-hip width as:

```text
front hip span = 49% of half finished hip
back hip span  = 51% of half finished hip
```

and separately calculates front/back dart widths from the waist-to-hip difference.

This is useful evidence for one architectural point: asymmetric panel balance is not unique to Aldrich, and a drafting system may encode the front/back hip split explicitly rather than inheriting a 50/50 split.

The tutorial is not treated as equivalent in authority to a production block or the Aldrich text, and this repo does not promote its exact 49/51 numbers.

**Classification:** `EXTERNAL_DRAFTING_METHOD_CANDIDATE`

**Production status:** `RESEARCH_ONLY`.

## Cross-system finding

The useful common structure is not a universal numeric ratio. It is this dependency:

```text
finished garment waist + hip
        ↓
front/back panel balance policy
        ↓
front hip span / back hip span
front waist span / back waist span
        ↓
front suppression target
back suppression target
```

Therefore the production-level panel-target policy should eventually be based on explicit panel-balance semantics, not a hidden suppression ratio.

A future policy result should be inspectable enough to expose at least:

```text
front_hip_span
back_hip_span
front_finished_waist_span
back_finished_waist_span
front_suppression_target
back_suppression_target
provenance
```

## What current purchased references can and cannot prove

The purchased/custom-made PRJ/DXF sources remain strong production references for semantic piece identity, sewing interfaces, material layers and finished geometry.

However, the current purchased garments are styled dresses rather than a clean basic A-line skirt block. Their lower-skirt construction does not independently reveal the body-measurement-to-panel-balance rule used by the maker.

Therefore they cannot yet choose between a 50/50, Aldrich-like, 49/51, or another front/back balance policy for the school-skirt family.

**Classification:** `HUMAN_CONFIRMED` but `OUT_OF_FAMILY_FOR_POLICY_SELECTION`.

## Current production decision

The generalized contract is now broad enough, but the policy remains unresolved:

| Requirement | Status | Reason |
| --- | --- | --- |
| whole half-garment suppression conservation | `SUPPORTED` | mathematical invariant + generalized validator |
| asymmetric front/back targets | `SUPPORTED` | data model + validator |
| symmetric 50/50 target split | `RESEARCH_BASELINE` | architectural baseline only |
| Aldrich asymmetric split | `RESEARCH_CANDIDATE` | named external system |
| 49/51 hip balance | `RESEARCH_CANDIDATE` | published drafting method |
| production panel-balance rule | `NEEDS_RULE` | no same-family production validation |

The production gate should therefore continue to report:

```text
panel_suppression_target_policy = NEEDS_RULE
```

## Strongest next validation step

The most useful new evidence would be a same-family basic A-line / straight-skirt block drafted for a known body-measurement set by a professional pattern maker, together with the measurement/ease contract used.

Then the project can measure directly:

```text
front hip span
back hip span
front finished waist span
back finished waist span
front dart/side shaping
back dart/side shaping
```

and compare those values against the named research candidates.

A CLO toile can test fit behavior, but simulation alone should not promote a policy to production authority.

## Safe conclusion

The architecture question is resolved: front/back panel suppression targets must be explicit and may be asymmetric.

The production-rule question is **not** resolved. No 50/50, Aldrich, 49/51 or other split is a default yet.
