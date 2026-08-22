# Purchased skirt shell vs lining comparison

## Purpose

Compare the purchased `1.dxf` / `2.dxf` lower-skirt shell and lining geometry without promoting any measurement into a production drafting rule.

This document was revised after adversarial review. The earlier pass incorrectly treated source layer-2 points as semantic turn points and therefore misidentified one `2.dxf` shell-back edge as a side seam. The corrected pass uses the surviving Claude-era `edges.py` geometric-corner method where it is effective, together with topology, symmetry, counterpart matching and construction annotations. Semantic labels remain separate from mechanically measured path lengths.

## Evidence boundary

- `RAW_DXF_FACT` — material, quantity, annotation, entity type/order, or stored contour coordinates read directly from the purchased source.
- `DIRECT_GEOMETRY` — length or topology computed from the purchased contour; rigid re-orientation does not change the length.
- `HIGH_CONFIDENCE_SEMANTIC` — edge role is strongly supported by topology/symmetry/counterpart equality but has not yet been proven by a seam map or CLO sewing check.
- `CANDIDATE_SEMANTIC` — edge role remains ambiguous.
- `CONSTRUCTION_MECHANISM_UNRESOLVED` — geometry is established but the way fullness/pleats/gathers/zipper treatment is assembled is not.

No shell/lining ratio below is a production default.

## Source-format check

For the purchased `1.dxf` and `2.dxf` used in this audit:

- there are no `LWPOLYLINE` entities;
- there are no non-zero VERTEX bulges (group 42);
- lower-skirt boundaries are dense classic `POLYLINE` contours.

Therefore the path lengths below are not chordal approximations of hidden DXF bulge arcs.

## `1.dxf`

### Lining (`色丁里`)

The following labels are high-confidence geometric semantics, not an independently supplied seam map.

| Path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 985.530783 mm | 668.939133 mm per piece |
| waist | 425.457520 mm | 196.882202 mm per piece |
| side seam | 568.551237 mm | 568.390462 mm |

Full lining hem = `2323.409049 mm`.

Full lining waist = `819.221924 mm`.

Hem / waist = `2.836116785`.

Front/back lining side difference = `-0.160775 mm` (`back - front`).

The front/back side near-equality strongly supports the side labels. The hem/waist labels are also strongly supported by the four-edge A-line topology, but remain semantic interpretation rather than a source-provided seam map.

### Shell (`弹力面布`)

The front shell is annular-sector-like. The directly measured major path groups are:

- outer curved path: `2298.588663 mm`;
- inner curved path: `1223.241794 mm`;
- radial path: `606.586013 mm`;
- opposite radial path: `606.586021 mm`.

For this sector topology, `HIGH_CONFIDENCE_SEMANTIC` is justified for:

- the two equal radial paths as the two side seams;
- the longer outer arc as hem;
- the shorter inner arc as waist.

The back shell contains a `606.586013 mm` path matching the front side seam to numerical precision. That back side-seam identity is therefore also `HIGH_CONFIDENCE_SEMANTIC`.

Other back paths include approximately:

- `1166.491455 mm` curved lower path;
- `615.947905 mm` upper path group;
- `616.250846 mm` remaining centre/back candidate.

The centre-back zipper annotation supports the existence of a centre-back construction edge, but the `615.95` and `616.25` paths are too similar in length to identify by length alone. Their exact waist-versus-centre assignment remains `CANDIDATE_SEMANTIC`.

If the current back waist/centre assignment is correct, the conditional full-garment totals are:

| Metric | Shell | Lining | Shell / lining |
| --- | ---: | ---: | ---: |
| full waist | 2455.137604 mm | 819.221924 mm | 2.996914 |
| full hem | 4631.571573 mm | 2323.409049 mm | 1.993438 |
| hem / waist | 1.886481 | 2.836117 | — |
| front side seam | 606.586013 mm | 568.551237 mm | — |
| back side seam | 606.586013 mm | 568.390462 mm | — |

Shell minus lining side seam:

- front: `+38.034776 mm`;
- back: `+38.195551 mm`.

The approximately 3× waist observation is evidence of substantial waist-fullness reduction **if** the back waist assignment is correct. It does not identify the construction mechanism. Gathering, pleating, tucks, another controlled-fullness method, or a more complex assembly remain possible. Do not label the mechanism as gathering without construction evidence.

## `2.dxf`

### Lining (`卡其色里`)

| Path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 987.633640 mm | 536.395198 mm per piece |
| waist | 469.395259 mm | 219.296612 mm per piece |
| side seam | 681.172684 mm | 681.657061 mm |

Full lining hem = `2060.424036 mm`.

Full lining waist = `907.988483 mm`.

Hem / waist = `2.269218250`.

Front/back lining side difference = `+0.484377 mm` (`back - front`).

Again, the near-equal side lengths strongly support the side labels while the complete waist/hem semantics remain high-confidence inference rather than an explicit seam map.

### Shell (`卡其色面`) — corrected geometric-corner split

Using the surviving `edges.py` corner algorithm on layer-14 gives the following mechanical segments.

Front shell:

1. lower curved path: `1376.647543 mm`;
2. left side lower segment: `533.400272 mm`;
3. left side upper segment: `177.799961 mm`;
4. upper shaped path: `622.009747 mm`;
5. right side: `711.200183 mm`.

The two left-side segments sum to:

```text
533.400272 + 177.799961 = 711.200233 mm
```

which matches the right side (`711.200183`) within `0.000050 mm`. The split on the left is therefore a geometric subdivision of one semantic side interface, not evidence of a shorter side seam.

Back shell:

1. lower curved path: `735.276778 mm`;
2. side seam: `711.199804 mm`;
3. upper segment A: `126.900239 mm`;
4. upper segment B: `168.606055 mm`;
5. remaining long centre/back construction edge: `723.900048 mm`.

The back side (`711.199804`) matches the front side (`711.200183`) within:

```text
-0.000379 mm  (back - front)
```

Therefore the previous claim that `2.dxf` shell front/back side seams differ by about `12.7 mm` is **withdrawn**. It came from incorrectly assigning the `723.900048 mm` centre/back construction edge as the side seam.

`HIGH_CONFIDENCE_SEMANTIC` assignments are now:

- front and back `~711.200 mm` paths = side seams;
- lower curved paths = hems;
- front `622.009747 mm` upper path = front waist interface;
- back `126.900239 + 168.606055 = 295.506294 mm` upper path group = back waist interface;
- back `723.900048 mm` remaining long edge = centre/back construction edge candidate, consistent with the lower-skirt construction topology.

Under those assignments:

| Metric | Shell | Lining | Shell / lining |
| --- | ---: | ---: | ---: |
| full waist | 1213.022335 mm | 907.988483 mm | 1.335945 |
| full hem | 2847.201099 mm | 2060.424036 mm | 1.381852 |
| hem / waist | 2.347196 | 2.269218 | — |
| front side seam | 711.200183 mm | 681.172684 mm | — |
| back side seam | 711.199804 mm | 681.657061 mm | — |

Shell minus lining side seam:

- front: `+30.027499 mm`;
- back: `+29.542743 mm`.

The shell side length is still approximately `12.7 mm` longer than the maker's `27.5 in = 698.5 mm` annotation. That is now treated as a **separate length-semantics question**, not a front/back sewing mismatch. The annotation may refer to finished length, a centre path, seam-line convention, or another house measurement.

## Why source layer-2 points are not semantic edges

The adversarial review correctly challenged the earlier splitter. In the shell blocks there are many layer-2 points, and many do not lie exactly on a semantic corner. For example, `2.dxf` shell front contains 65 layer-2 points while the geometric corner method produces only five contour corners. Several layer-2 points are around `12.7 mm`, `50.8 mm` or other construction offsets away from the layer-14 boundary.

Therefore layer-2 points must not be treated as an automatic edge partition. They may encode grading/construction reference points and require separate semantic interpretation.

## What this comparison now establishes

1. The historical `PROF_A/B` numeric values align with lining-profile geometry, not shell geometry.
2. Shell and lining are distinct pattern instances and are not related by one global scale factor.
3. `1.dxf` shell side-seam identity is strong; its fullness-reduction mechanism remains unresolved.
4. `2.dxf` shell front/back side seams match essentially exactly when split by geometric corners.
5. The old `12.7 mm` front/back mismatch was an edge-identity error and must not influence production policy.
6. New-engine shell and lining must remain explicit semantic objects; duplicate names must never silently choose one material instance.

## Still unresolved

Before converting these observations into drafting rules, verify:

- exact `1.dxf` back waist-versus-centre assignment from zipper/notch/sewing evidence;
- whether `1.dxf` shell fullness is gathered, pleated, tucked or controlled another way;
- what the shell maker length annotations (`23.5 in`, `27.5 in`) measure;
- edge-by-edge layer-1 versus layer-14 seam-allowance behavior;
- whether the `2.dxf` upper waist subdivisions encode darts, zipper treatment, shaping, or another construction feature.

Until those are resolved, geometry observations remain evidence, not production defaults.
