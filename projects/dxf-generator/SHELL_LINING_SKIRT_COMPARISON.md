# Purchased skirt shell vs lining comparison

## Purpose

Compare the purchased `1.dxf` / `2.dxf` lower-skirt shell and lining geometry without promoting any measurement into a production drafting rule.

This pass uses the original purchased DXFs directly. Layer-14 contours are measured after the forensically verified legacy upright transform. Source layer-2 turn points are used to segment contour paths. Where sewing semantics are not independently proven, the result is explicitly marked as a **candidate semantic interpretation** rather than fact.

## Evidence boundary

- `DIRECT_PATH` — exact path length from the purchased layer-14 contour between source turn points.
- `CANDIDATE_SEMANTIC` — a path whose likely role (waist / hem / side / centre) is inferred from topology, symmetry and matching counterpart lengths, but is not yet verified by an explicit seam map or CLO sewing check.
- No shell/lining ratio below is a production default.

## `1.dxf`

### Lining — resolved semantic paths

Material: `色丁里`.

| Path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 985.530783 mm | 668.939133 mm per piece |
| waist | 425.457520 mm | 196.882202 mm per piece |
| side seam | 568.551237 mm | 568.390462 mm |

Full lining hem = `2323.409049 mm`.

Full lining waist = `819.221924 mm`.

Hem / waist = `2.836116785`.

Front/back lining side-seam mismatch = `-0.160775 mm` (`back - front`).

### Shell — direct paths and candidate semantics

Material: `弹力面布`.

The front shell is an annular-sector-like contour rather than a simple A-line counterpart to the lining. Direct path groups are:

- outer curved path: `2298.588663 mm`
- inner curved path: `1223.241794 mm`
- two equal radial paths: `606.586013 mm` and `606.586021 mm`

The back shell contains:

- path A: `1166.491455 mm`
- path B: `606.586013 mm`
- upper split path total: `615.947905 mm`
- remaining curved/centre candidate path: `616.250846 mm`

`CANDIDATE_SEMANTIC` interpretation:

- front radial paths are side seams;
- back path B (`606.586013`) is the matching side seam because it matches the front to numerical precision;
- front outer curved path is hem and inner curved path is waist;
- back path A is hem and upper split path is waist;
- remaining `616.250846` path is a centre/back construction edge.

Under that interpretation:

| Metric | Shell | Lining | Shell / lining |
| --- | ---: | ---: | ---: |
| full waist | 2455.137604 mm | 819.221924 mm | 2.996914 |
| full hem | 4631.571573 mm | 2323.409049 mm | 1.993438 |
| hem / waist | 1.886481 | 2.836117 | — |
| front side seam | 606.586013 mm | 568.551237 mm | — |
| back side seam | 606.586013 mm | 568.390462 mm | — |

Shell minus lining side seam:

- front: `+38.034776 mm`
- back: `+38.195551 mm`

This strongly suggests the `1.dxf` shell and lining are **not the same silhouette with a simple uniform shortening/scaling operation**. The candidate shell waist is almost exactly 3× the lining waist while the candidate shell hem is about 2× the lining hem, consistent with substantial shell fullness/gathering, but that construction interpretation still requires explicit seam/notch verification before becoming a rule.

## `2.dxf`

### Lining — resolved semantic paths

Material: `卡其色里`.

| Path | Front lining, qty 1 | Back lining, qty 2 |
| --- | ---: | ---: |
| hem | 987.633640 mm | 536.395198 mm per piece |
| waist | 469.395259 mm | 219.296612 mm per piece |
| side seam | 681.172684 mm | 681.657061 mm |

Full lining hem = `2060.424036 mm`.

Full lining waist = `907.988483 mm`.

Hem / waist = `2.269218250`.

Front/back lining side-seam mismatch = `+0.484377 mm` (`back - front`).

### Shell — direct paths and candidate semantics

Material: `卡其色面`.

Front shell is symmetric in the source contour:

- bottom curved path: `1376.647543 mm`
- left side candidate: `711.200232 mm`
- right side candidate: `711.200183 mm`
- upper shaped path: `622.009747 mm`

Back shell direct path groups:

- bottom curved path: `735.276778 mm`
- path A: `533.399571 mm`
- upper shaped path: `473.306528 mm`
- path B: `723.900048 mm`

`CANDIDATE_SEMANTIC` interpretation:

- front `711.2002` paths are the two side seams;
- back path B (`723.900048`) is the side-seam candidate because it is the only back edge close to the front side-seam length;
- back path A (`533.399571`) is the centre/back construction edge;
- upper shaped paths are waist interfaces;
- bottom curved paths are hems.

Under that interpretation:

| Metric | Shell | Lining | Shell / lining |
| --- | ---: | ---: | ---: |
| full waist | 1568.622803 mm | 907.988483 mm | 1.727580 |
| full hem | 2847.201099 mm | 2060.424036 mm | 1.381852 |
| hem / waist | 1.815096 | 2.269218 | — |
| front side seam | 711.200232 mm | 681.172684 mm | — |
| back side seam candidate | 723.900048 mm | 681.657061 mm | — |

Shell minus lining side seam:

- front: `+30.027548 mm`
- back candidate: `+42.242987 mm`

Shell front/back candidate side mismatch = `+12.699816 mm` (`back - front`).

Unlike the lining, the shell therefore does **not** currently support an assumption of equal front/back side-seam length. The `12.699816 mm` difference is suspiciously close to `12.7 mm` (1/2 inch), but no causal interpretation is promoted here.

## What this comparison establishes

1. The historical `PROF_A/B` constants are lining-profile measurements only.
2. Purchased shell geometry differs materially from lining geometry in both references.
3. Shell-to-lining transformation is not a single global scale factor.
4. `1.dxf` shows especially large fullness differences between shell and lining.
5. `2.dxf` lining side seams nearly match, whereas the current shell side-seam candidate pair differs by about 12.7 mm.
6. New-engine shell and lining must therefore be separate semantic objects; one must never be silently substituted for the other.

## Still unresolved

Before converting shell observations into drafting rules, verify:

- exact shell waist/hem/side/centre seam identity from notches, construction annotations or CLO sewing;
- whether `1.dxf` shell fullness is gathered, pleated, draped or otherwise controlled at assembly;
- why `2.dxf` shell front/back side candidate lengths differ by about 12.7 mm;
- whether shell maker annotations (`23.5 in`, `27.5 in`) refer to centre length, side length, finished length or another house convention;
- edge-by-edge layer-1 versus layer-14 seam allowance behavior.

Until those are resolved, the shell totals above remain evidence for geometry comparison, not production defaults.
