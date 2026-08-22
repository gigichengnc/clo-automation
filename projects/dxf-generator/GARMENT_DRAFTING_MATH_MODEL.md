# Garment Drafting Mathematics Model

## Purpose

This document defines the mathematical layer between body/style inputs and production pattern geometry.

The DXF generator must not be a coordinate copier. It should solve a constrained garment model and only then serialize the resulting semantic pattern pieces to DXF.

```text
body measurements
+ garment request
+ drafting policy
+ construction policy
+ calibrated production evidence
        ↓
mathematical garment model
        ↓
semantic pattern geometry
        ↓
constraint validation
        ↓
production transforms
        ↓
DXF / garment metadata / seam contract
```

The model deliberately separates four kinds of knowledge:

1. **mathematical invariants** — geometry and conservation relationships that should always hold;
2. **drafting policy** — how a drafting system distributes shape and ease;
3. **style policy** — design choices such as flare, drop shoulder, gathering or collar type;
4. **production policy** — seam allowance, notches, zipper treatment, grading, shell/lining behavior and manufacturing conventions.

A value observed in a purchased pattern is evidence for calibration. It is not automatically a universal rule.

---

## 1. Coordinate and unit contract

All internal drafting geometry uses millimetres.

Each piece has a canonical local frame before placement in a marker or DXF sheet. A typical convention is:

```text
+x = from centre toward side
+y = upward
```

or, where existing code requires it:

```text
+x = from centre toward side
-y = downward from waist/reference line
```

The exact sign convention is less important than making it explicit and stable.

Rigid translation/rotation used for display, nesting or DXF placement must not change semantic measurements.

---

## 2. Input model

The engine should distinguish body measurements from finished-garment targets.

```text
BodyMeasurements
  waist
  hip
  bust/chest
  high_bust
  neck
  shoulder_width
  shoulder_slope
  arm_length
  biceps
  wrist
  waist_to_hip
  torso lengths
  ...

GarmentRequest
  garment_type
  requested_length
  fit/ease targets
  silhouette
  design options
  material class
  shell / lining requirement
  closure type
  ...
```

A garment measurement should normally be derived explicitly:

\[
G = B + E
\]

where:

- \(B\) = body measurement;
- \(E\) = ease or design allowance;
- \(G\) = finished garment target.

For stretch garments, \(E\) may be negative.

No downstream geometry function should silently add a second ease allowance.

---

## 3. Circumference allocation

For symmetric garments, circumference targets may be partitioned into front/back or quarter-body spans.

Example:

\[
W_q = \frac{W_g}{4}
\]

\[
H_q = \frac{H_g}{4}
\]

These are mathematical conveniences, not assumptions that every style must use four equal panels.

A more general interface allocation is:

\[
C = \sum_i L_i
\]

where \(L_i\) are the sewn edge lengths contributing to a finished circumference.

The engine should therefore model circumference as a set of named semantic interfaces rather than one anonymous number.

---

## 4. Suppression and dart conservation

For a fitted skirt or bodice, the difference between a larger reference level and a smaller level must be absorbed by shaping.

For a quarter skirt:

\[
S = H_q - W_q
\]

where \(S\) is total suppression.

The fundamental conservation constraint is:

\[
S = S_{side} + \sum_{j=1}^{n} D_j + S_{other}
\]

where:

- \(S_{side}\) = side-seam shaping;
- \(D_j\) = dart intake;
- \(S_{other}\) = princess seams, gathers, pleats or other shaping mechanisms.

The mathematics determines that the allocations must sum correctly. It does **not** determine the production drafting policy for how much goes to each component.

Therefore the engine needs an explicit policy object, for example:

```text
SuppressionPolicy
  allocate(total_suppression, body, style) ->
    front_darts
    back_darts
    side_shaping
    other_shaping
```

If no supported allocation policy exists, safe-stop rather than inventing one.

---

## 5. Dart geometry

A dart has at least:

```text
position
intake
length
orientation
apex / termination policy
```

If a dart intake is \(D\), closing the dart must reduce the open waist path by exactly \(D\), within numerical tolerance.

For multiple darts:

\[
W_{open} - W_{closed} = \sum_j D_j
\]

Dart positions should be represented by explicit fractions or reference points rather than assumed equal spacing.

Dart counts, positions, intakes and lengths are drafting-policy parameters unless independently established by production evidence.

---

## 6. A-line and flared skirt geometry

A simple A-line model may use:

\[
H_{hem} = H_{hip} + F
\]

where \(F\) is flare per semantic half/quarter panel.

That is only one drafting family. A production pattern may instead use curved side seams, multiple panels, godets, pleats, gathers or circular sectors.

The new engine must identify which silhouette model is active rather than applying one formula to every skirt.

---

## 7. Circular and sector skirts

For a full circle with waist circumference \(C\):

\[
r = \frac{C}{2\pi}
\]

For a half circle:

\[
r = \frac{C}{\pi}
\]

For a sector of angle \(\theta\) radians:

\[
C = r\theta
\]

thus:

\[
r = \frac{C}{\theta}
\]

If skirt length is \(L\):

\[
R = r + L
\]

and the outer hem arc is:

\[
C_{hem} = R\theta
\]

This family is relevant when a production piece is annular-sector-like. It should be fitted/calibrated from semantic waist/hem/radial paths, not from file bounding boxes.

---

## 8. Curve representation

Garment curves should be semantic geometry, not dense anonymous coordinate clouds.

Supported mathematical representations may include:

- circular arcs;
- cubic Bézier curves;
- splines/B-splines;
- piecewise polynomial curves;
- sampled production contours when a faithful direct-copy mode is required.

For a cubic Bézier:

\[
B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3
\]

where \(P_0\) and \(P_3\) are semantic endpoints and \(P_1,P_2\) control shape.

Curve policy should expose parameters that have drafting meaning, for example armhole depth, tangent direction or control-point offsets.

---

## 9. Path length

For a smooth parametric curve \(C(t)\), seam length is:

\[
L = \int_a^b \|C'(t)\|\,dt
\]

For sampled production polylines, length is:

\[
L = \sum_i \|P_{i+1}-P_i\|
\]

The engine must compare **semantic sewing paths**, not overall piece perimeter or bounding boxes.

---

## 10. Sewing-interface constraints

Every sewing relationship should be represented explicitly.

Examples:

```text
front_side_seam ↔ back_side_seam
front_princess ↔ side_front_princess
collar_stand_lower ↔ bodice_neckline
collar_face_lower ↔ collar_stand_upper
sleeve_cap ↔ bodice_armhole
skirt_waist ↔ bodice_lower_opening
waistband_inner ↔ skirt_waist
```

For a nominal 1:1 seam:

\[
|L_A-L_B| \leq T
\]

where \(T\) is an explicit construction tolerance.

The engine must not infer sewing partners from similar length alone.

---

## 11. Ease at sewing interfaces

Some interfaces intentionally do not have equal lengths.

For a sleeve cap:

\[
E_{cap}=L_{cap}-L_{armhole}
\]

and ease percentage:

\[
E_{cap\%}=\frac{L_{cap}-L_{armhole}}{L_{armhole}}\times100
\]

This relationship should be represented as an explicit allowed-ease constraint, not disguised as a mismatch tolerance.

The same principle applies to gathering, pleating, elastic, shrinkage or eased collars.

A seam relationship should therefore specify a mode:

```text
EXACT_1_TO_1
EASED
GATHERED
PLEATED
ELASTIC
OPEN_EDGE
FOLD
ZIPPER
OTHER_EXPLICIT
```

Unknown mode => safe-stop.

---

## 12. Neckline and collar system

The collar system contains at least two distinct interfaces:

```text
bodice neckline
      ↕
collar stand lower edge

collar stand upper edge
      ↕
collar face lower edge
```

These must never be collapsed into one generic `NECK` measurement.

If stand ends contain overlap or extension:

\[
L_{effective}=L_{raw}-L_{left\_extension}-L_{right\_extension}
\]

The sewing validator should compare the effective sewing span, not necessarily the raw geometric edge from tip to tip.

---

## 13. Armhole and sleeve system

The bodice armhole should be decomposed by semantic pieces:

\[
L_{armhole}=L_{front}+L_{back}
\]

or, for multi-panel bodices:

\[
L_{front}=\sum_i L_{front,i}
\]

\[
L_{back}=\sum_j L_{back,j}
\]

The sleeve cap is a separate semantic path.

The drafting solver may use armhole depth, cap height, biceps width and control rules to generate the sleeve, but the final cap/armhole relationship must be validated independently.

An edge detector that merges a true sleeve-underarm segment into the cap is a semantic failure even if the resulting number happens to match a legacy constant.

---

## 14. Shell and lining as separate systems

Shell and lining are different pattern instances.

They may have different:

- hem circumference;
- waist circumference;
- length;
- ease/fullness;
- seam placement;
- zipper treatment;
- facing interaction;
- seam allowance;
- construction paths.

Therefore:

```text
ShellPattern != LiningPattern
```

A duplicate DXF block name must never silently choose a material instance in the new architecture.

If a lining is derived from shell, the derivation must be an explicit policy with measurable transforms, not a global scale factor unless production evidence supports that specific rule.

---

## 15. Seam allowance as offset geometry

For seam-line curve \(C(t)\) and allowance \(d\):

\[
C_d(t)=C(t)+dN(t)
\]

where \(N(t)\) is the local normal.

Real production offsets require corner policies:

```text
miter
round
bevel
special hem corner
zipper allowance
fold allowance
zero-SA edge
```

Seam allowance therefore belongs to an edge-semantic production policy, not a single whole-piece constant.

Example:

```text
SemanticEdge
  id
  path
  sewing_role
  seam_allowance_rule
  notch_rule
  partner_id
```

---

## 16. Grainline and orientation

Grain is a production constraint, not merely a visual arrow.

The pattern model should preserve:

```text
grain direction
allowed bias / rotation range
cut-on-fold semantics
nap/directional-fabric constraint
```

Rigid nesting rotations must respect those constraints.

---

## 17. Grading versus re-solving

Two fundamentally different systems must remain distinct.

### Coordinate grading

A grade point follows:

\[
P_i(s)=P_i(base)+(\Delta x_i(s),\Delta y_i(s))
\]

This preserves a base pattern and applies rule-table movements.

### Parametric re-solving

Each size has its own body/garment measurements:

```text
measurements(size)
        ↓
same drafting model
        ↓
new solved geometry(size)
```

This can produce non-linear size changes and should not be described as traditional linear grading.

The engine may eventually support both, but provenance must record which method created a size.

---

## 18. Constraint classes

### Hard mathematical constraints

Must pass or safe-stop:

- finite coordinates;
- non-degenerate paths;
- positive required dimensions;
- suppression conservation;
- closed outline validity;
- declared 1:1 sewing partners within tolerance;
- no contradictory duplicate semantic IDs;
- shell/lining identity preserved;
- grading/re-solve provenance known.

### Construction constraints

Require explicit policy:

- sleeve-cap ease range;
- gathering/pleat ratio;
- zipper opening length;
- collar overlap/extension;
- hem turn-up;
- seam allowance by edge;
- notch correspondence.

### Style constraints

Design-specific:

- flare;
- dart count and distribution;
- neckline shape;
- collar type;
- sleeve silhouette;
- skirt fullness;
- asymmetric design.

---

## 19. Evidence and calibration model

Rules should carry provenance.

```text
MATHEMATICAL_INVARIANT
INDUSTRY_DRAFTING_METHOD
HUMAN_CONFIRMED
DIRECT_PRODUCTION_GEOMETRY
HIGH_CONFIDENCE_SEMANTIC
CALIBRATED_FROM_REFERENCE
STYLE_CHOICE
ASSUMPTION
UNVERIFIED
```

A production reference can calibrate a parameter, but one purchased garment normally cannot establish a universal drafting constant.

Generated artifacts may test replay/regression but provide no independent vote for production-rule inference.

---

## 20. Safe-stop rule

```text
known + verified        -> continue
known but inconsistent  -> stop
ambiguous               -> stop
missing                 -> stop
API mismatch            -> stop
```

The solver must never silently repair a semantic ambiguity merely to produce a DXF.

---

## 21. Target semantic data model

A future shared contract should resemble:

```text
GarmentModel
  body_measurements
  garment_targets
  drafting_policy
  construction_policy
  pieces[]
  interfaces[]
  provenance[]

PatternPiece
  id
  material_role       # shell / lining / facing / binding ...
  quantity
  grainline
  outline
  internal_features[]
  semantic_edges[]

SemanticEdge
  id
  geometry
  role
  sewing_partner
  relation_mode
  expected_ease
  seam_allowance_rule
  notch_rule
  evidence
```

DXF, CLO and Blender adapters should consume this contract rather than inventing semantics from coordinates independently.

---

## 22. School-skirt engine mapping

The current school-skirt work already contains several pieces of this architecture:

```text
BodyMeasurements
GarmentRequest
SchoolSkirtSpec
SchoolSkirtDraftingParameters
SchoolSkirtSuppressionPolicy
SchoolSkirtDraft
PanelGeometryInput
semantic panel geometry
```

The next development work should use this mathematics document to classify every existing parameter as one of:

```text
invariant
calibrated policy
style choice
manufacturing rule
legacy assumption
unresolved
```

Examples:

- `quarter_waist = garment_waist / 4` -> mathematical model for the current symmetric topology;
- suppression conservation -> invariant;
- front/back dart allocation -> unresolved drafting policy;
- fixed 80 mm flare -> style/legacy assumption until calibrated;
- fixed dart lengths -> policy/legacy assumption;
- hem shape -> unresolved style/drafting policy;
- seam allowance -> production policy, not panel geometry.

---

## 23. What the engine is not

It is not:

- an AI system that guesses production patterns from appearance alone;
- a library of copied DXF coordinates;
- a universal claim that one drafting school is correct;
- a whole-piece uniform-offset script;
- a length-matching sewing heuristic;
- a substitute for human/CLO verification when production semantics remain unknown.

---

## 24. Development order

Recommended order:

```text
1. semantic measurement / interface model
2. mathematical invariants
3. skirt drafting policies
4. bodice drafting policies
5. armhole/sleeve coupled solver
6. neckline/collar coupled solver
7. shell/lining derivation policies
8. seam allowance + notch policies
9. grading and parametric size re-solving
10. DXF serialization
11. CLO sewing/simulation adapter
12. production-reference calibration loop
```

The goal is not merely to generate a pattern. The goal is to generate a pattern whose geometry, sewing relationships and provenance can be explained and mechanically validated.
