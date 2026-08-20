# Existing DXF Work Inventory

This file records useful work that already exists in the private working folder so future contributors do not rebuild the same ideas from scratch.

## Public / private boundary

The public repository should contain reusable code, architecture, schemas, synthetic examples, and documentation.

Keep these outside the public repository unless there is a clear right to publish them:

- original or reference DXF files
- source/reference images
- external measurement/specification tables
- personal body measurements
- private Drive links, file IDs, or local paths
- generated garment files that contain private or source-derived pattern data

The private working folder remains the reference workspace for those materials.

## Reusable or promising code already created

### `skirt_gen.py`

Parametric skirt/DXF generator. Existing capabilities include:

- ANSI/AAMA-style DXF output
- pattern net + cut-line generation
- seam allowance offsets
- turn/curve point layers
- notches and grain lines
- parametric panel construction
- `make_skirt_dxf(...)`
- `make_size_set(...)`
- per-size geometry solving instead of globally scaling a finished DXF

This is the strongest starting point for the future DXF Generator core.

### `school_skirt.py`

Prototype generator for the No.22 student A-line skirt.

Already models:

- waist + ease
- front/back panels
- darts
- waist-to-hip transition
- flare
- waistband
- hem allowance
- multiple waist sizes

Current limitation: some body dimensions are derived from fixed assumptions (for example hip addition, hip depth, and skirt length) rather than being supplied as individual body measurements.

This is the best first fixture for personalised body-size input.

### `run_sizeset.py`

Small example that calls `make_size_set(...)` to generate a multi-size skirt set from a base size and grading increments.

Useful as a regression/example script, but grading by named sizes is different from true personalised body measurement input.

### `to_clo.py`

Prototype DXF-to-CLO-clean conversion utility.

Existing idea:

- read the net/seam-line layer
- preserve internal lines
- create a cleaner CLO-oriented DXF

This should eventually become an adapter rather than part of the garment drafting logic.

### `validate.py`

Garment-specific edge/seam-length investigation script.

Useful ideas can later be extracted into generic validation, but the current script contains garment-specific assumptions and unresolved relationships, so it should not be treated as a universal validator.

### Other prototype builders

Existing private scripts include garment/build experiments such as:

- `build_set.py`
- `build_five.py`
- `build_two.py`
- `build_library.py`
- `combos.py`
- `nest2.py`
- `resolve.py`
- `run_gen.py`

These are reference material. Review them before reimplementing similar geometry or workflow logic, but do not migrate them blindly into the public architecture.

## Existing CLO inspection work

### `CLO_no11_compact_dump.py`

A read-only No.11 CLO inspection prototype that examines pattern/sewing API availability and pattern/edge information.

It is a useful predecessor/reference for the newer generic runtime contract probe in `CLO_Agent_v0.1/tools/contract_probe.py`.

### `CLO_no11_api_probe.py`

The copy found in the private working folder is effectively empty and should not be treated as an implemented probe.

## Private DXF reference coverage

The private workspace already contains useful reference families, including:

- single-size garment DXFs
- CLO-clean variants
- multi-size / M–4XL sets
- a skirt size-set example
- No.22 student A-line skirt W60–76
- block/module-library DXFs

These should be used later for regression and comparison without publishing the raw files.

## What this means for personalised sizing

We are not starting from zero.

Current capability is roughly:

```text
base dimensions / size grading
        ↓
parametric geometry
        ↓
DXF
```

Target capability is:

```text
body measurements
        ↓
fit + ease rules
        ↓
garment dimensions
        ↓
parametric geometry
        ↓
validated DXF
```

The first target should be the student A-line skirt because an existing parametric prototype and multiple waist-size outputs already exist.

## Small-task workflow

Use these labels when planning follow-up work:

- `[NOW]` — pure code/documentation task; no real garment file required
- `[NEEDS_DXF]` — requires private/reference DXF comparison
- `[NEEDS_CLO]` — requires running inside CLO
- `[HUMAN]` — requires visual/design judgment by the garment operator

Initial follow-up tasks:

```text
[NOW] Define a BodyMeasurements model: waist, hip, waist_to_hip, garment_length.
[NOW] Separate body measurements from fit/ease rules.
[NOW] Adapt the student-skirt prototype to accept explicit hip, waist-to-hip, and length values.
[NOW] Add input validation and synthetic test measurements.

[NEEDS_DXF] Compare a generated personalised skirt against approved/reference skirt geometry.
[NEEDS_DXF] Compare generator behaviour with existing multi-size reference sets.

[NEEDS_CLO] Import a generated personalised DXF and verify scale/pattern count.
[NEEDS_CLO] Verify darts/internal lines survive import correctly.
[NEEDS_CLO] Test semantic-edge auto-sewing after the CLO API contract work is stable.

[HUMAN] Confirm proportions and fit intent visually.
[HUMAN] Approve changes to ease, dart placement, or source garment geometry.
```
