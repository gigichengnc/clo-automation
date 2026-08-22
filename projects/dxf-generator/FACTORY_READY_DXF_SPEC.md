# Factory-Ready DXF Acceptance Contract

## Purpose

Define the minimum acceptance gate for a garment pattern package that may be sent to a sample room or factory for production review.

A file being syntactically valid DXF is **not** sufficient. A factory-ready package must preserve pattern geometry, construction semantics, production metadata, grading intent and enough accompanying specification for another CAD/sample-room workflow to reproduce the intended garment without guessing.

This document is an internal acceptance contract for the `clo-automation` project. It does not replace a factory's own CAD or tech-pack requirements.

---

## 1. Preferred interchange formats

Primary deliverables:

- `DXF-AAMA` and/or `DXF-ASTM` according to the receiving factory's CAD workflow;
- metric units unless the factory explicitly requests otherwise;
- one clearly named style/version per package;
- grading embedded in the DXF or supplied in the rule format expected by the factory.

A separate Standard DXF may be supplied for visual CAD compatibility, but it must not be treated as the authoritative production representation when AAMA/ASTM semantics are required.

---

## 2. Pattern-piece geometry gate

Every production piece must pass all of the following before release:

- closed outer boundary;
- no self-intersection;
- no accidental overlapping/duplicated boundary segment;
- no zero-length segment;
- no disconnected boundary fragment;
- valid curve continuity at intended smooth joins;
- all dimensions expressed in the declared unit;
- geometry remains invariant under export -> re-import round trip within an explicit numeric tolerance;
- cutting line and sewing/net line are not silently swapped.

Round-trip validation must compare semantic edges or resampled contours rather than only bounding boxes.

---

## 3. Stable piece identity

Each pattern piece must carry a stable machine-readable ID independent of screen position or runtime CAD index.

Example:

```text
style_id: PILOT-001
piece_id: shell.front
piece_name: Front
material_role: shell
size: M
quantity: 1
mirror: false
```

A shell and lining piece must never share identity merely because their visible Chinese/English names are similar.

Required identity fields should include, where applicable:

- style/version;
- piece ID;
- human-readable name;
- material role (`shell`, `lining`, `interfacing`, etc.);
- cut quantity;
- pair/mirror requirement;
- size/grade identity;
- source/provenance class.

---

## 4. Semantic edge contract

A factory-ready piece cannot be only an anonymous polygon.

Important edges must be explicitly identified, for example:

```text
front.side
back.side
front.waist
back.waist
front.armhole
back.armhole
sleeve.cap.front
sleeve.cap.back
neckline.front
neckline.back
collar_stand.lower
collar_stand.upper
hem
zipper.edge
```

Each sewing relationship must be represented separately from geometric proximity.

Example:

```text
seam_id: shell.side.left
A: shell.front.side
B: shell.back.side
relationship: one_to_one
```

No automatic sewing decision may be based on similar edge length alone.

---

## 5. Sewing-interface validation

Before release, each intended sewing pair must report:

- edge A length;
- edge B length;
- absolute difference;
- relative difference;
- intended relationship (`one_to_one`, `ease`, `gather`, `pleat`, `stretch`, etc.);
- allowed tolerance or required ease/fullness target;
- evidence/source for that tolerance or target.

For a one-to-one seam:

```text
abs(A - B) <= approved_tolerance
```

If no tolerance has been approved, ambiguity must safe-stop rather than inventing one.

Examples that must remain semantically separate:

- bodice armhole vs sleeve-cap length;
- bodice neckline vs collar-stand lower edge;
- collar-stand upper edge vs collar-face lower edge;
- shell waist vs lining waist;
- lining waist vs bodice/skirt join.

---

## 6. Grainlines and orientation

Every fabric-dependent piece must have an explicit grainline or approved directional rule.

Validate:

- grainline exists where required;
- grainline direction is non-zero;
- intended fold/centre line is not mistaken for grain;
- directional print / nap restrictions are recorded when relevant;
- mirror/pair cutting requirements remain explicit.

Marker placement may rotate/translate a pattern only according to its material and grain policy.

---

## 7. Notches and match points

Required match information must be encoded and survive round-trip:

- side-seam balance points;
- armhole/sleeve front-back notches;
- waist panel match points;
- collar/neckline centre and shoulder match points;
- zipper start/end/reference points;
- pleat/gather boundaries;
- pocket-placement references where required.

Notches are semantic construction data. They must not be inferred solely from layer-number conventions without verification.

---

## 8. Seam allowance and hem allowance

Seam/net geometry and cut geometry must remain distinct.

For every edge, the production package should know whether allowance is:

- zero;
- standard seam allowance;
- edge-specific seam allowance;
- zipper allowance;
- hem allowance;
- fold/turn allowance;
- binding/finish-specific allowance.

Do not apply one global polygon offset if the production construction requires edge-specific treatment.

Corner joins and concave/convex offsets must be validated explicitly.

---

## 9. Internal construction geometry

Internal lines/marks must be classified, not merely stored as anonymous polylines.

Examples:

- dart legs / dart centre;
- pleat/fold lines;
- pocket placement;
- button/buttonhole positions;
- zipper placement;
- stitch/topstitch guides;
- drill/mark points;
- fold lines;
- gathering limits.

Unknown internal geometry must be reported instead of silently discarded.

---

## 10. Quantity, material and cut instructions

For each piece, record at minimum:

- material/fabric role;
- quantity;
- pair/mirror status;
- cut on fold where applicable;
- interfacing requirement if applicable;
- size;
- orientation restrictions.

The pattern package must distinguish pattern-piece quantity from total garment cut quantity.

---

## 11. Grading / size-set gate

A multi-size production release must state which method produced each size:

### Traditional grading

```text
base pattern
+ grade-rule deltas
-> other sizes
```

### Parametric re-solve

```text
size-specific body/garment targets
+ same drafting policy
-> independently solved geometry
```

Do not describe coordinate grading as independent parametric solving.

For every released size validate:

- required measurements;
- sewing partner compatibility;
- dart/suppression constraints;
- minimum feature spacing;
- seam allowance integrity;
- notch correspondence;
- piece count and quantity.

---

## 12. DXF round-trip acceptance

Before factory release, the authoritative DXF must be imported into at least one independent garment CAD/CLO workflow and checked for:

- scale/unit correctness;
- piece count;
- piece names/IDs where supported;
- closed boundaries;
- sewing/net vs cutting line identity;
- seam allowances;
- notches;
- grainlines;
- internal lines;
- grading/size group;
- measurement invariance.

A successful file-open is not a pass.

---

## 13. Factory package — DXF is not enough

The DXF pattern package should normally be accompanied by a concise production specification / tech pack containing at least:

- style/version ID;
- flat/sketch or reference image;
- finished garment measurements and tolerances;
- size chart;
- BOM / material specification;
- construction/seam notes;
- stitch type or critical sewing instructions where needed;
- closure details;
- placement dimensions for pockets/trims/buttons/zipper;
- seam/hem allowance policy;
- graded-size method/status;
- revision log;
- known unresolved items / explicit factory questions.

DXF-AAMA/ASTM is a pattern-data interchange format; it is not a complete product specification, marker, spreading or cutter-instruction package.

---

## 14. Sample-room gate before mass production

No newly generated pattern should go directly from code to bulk cutting.

Release sequence:

```text
mathematical/semantic validation
        ↓
DXF round-trip validation
        ↓
first sample / toile / prototype
        ↓
fit + construction review
        ↓
pattern corrections
        ↓
pre-production sample
        ↓
factory approval
        ↓
bulk production
```

A successful CLO simulation is useful evidence but does not replace a physical sample for production approval.

---

## 15. Pilot strategy for this repository

### Pilot A — factory interchange proof

Use a purchased pattern already known to have produced a real garment, without changing its geometry.

Goal:

- prove parser -> semantic representation -> export preserves production geometry and metadata;
- produce clean `DXF-AAMA` / `DXF-ASTM` outputs;
- re-import and compare against the purchased source;
- validate piece identity, grain, cut/sew lines, notches, quantities and materials;
- do **not** claim new drafting capability from this pilot.

Recommended source: purchased `2.dxf`, because the repository already has the deepest direct interface audit for it.

### Pilot B — first newly generated production pattern

Only after Pilot A passes, create a deliberately simple garment from the new mathematical engine.

Recommended scope:

- simple skirt or similarly low-piece-count garment;
- one base size first;
- explicit shell/lining choice;
- no unresolved legacy constants;
- all seam partners validated;
- physical sample required before grading/bulk release.

Do not use historical style `22.學生A字裙.W60-76.dxf` as production ground truth; it remains an assumption-driven regression artifact.

---

## 16. Release states

Every output should carry one of these states:

```text
EXPERIMENTAL
GEOMETRY_VALIDATED
ROUNDTRIP_VALIDATED
SAMPLE_VALIDATED
PREPRODUCTION_APPROVED
FACTORY_RELEASED
```

`FACTORY_RELEASED` is allowed only after both digital validation and sample/factory approval.

---

## Current project decision

The immediate objective is **not** arbitrary AI garment generation.

The immediate objective is:

```text
produce one auditable, factory-interchange-ready pilot package
        ↓
prove the pipeline preserves real production pattern semantics
        ↓
then release the first newly generated garment through the same gate
```
