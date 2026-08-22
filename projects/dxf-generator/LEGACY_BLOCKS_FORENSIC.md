# Lost `blocks.py` — Forensic Reconstruction

## Status

The original legacy `blocks.py` is missing and is treated as **LOST LEGACY SOURCE**.

`legacy_blocks_compat.py` is a forensic compatibility reconstruction for replaying surviving Claude-era scripts. It is **not** the original file, is **not** production authority, and must not become a dependency of the new parametric drafting engine.

## Observable callers

Surviving scripts import:

```python
from blocks import parse, upright
```

Known callers include `build_set.py`, `build_five.py`, `build_library.py`, `combos.py`, `edges.py`, `fix11.py`, `modules2.py`, `resolve.py`, `validate.py`, plus `parse()`-only callers such as `nest2.py` and `to_clo.py`.

Every surviving `upright()` caller consumes three return values but ignores the third.

## Reconstructed `parse()` contract

Callers establish that `parse(path)` returns a mapping keyed by AAMA BLOCK / piece name and that each value exposes at least:

```text
block["polys"] -> list of {"layer", "pts", ...}
block["texts"] -> list of TEXT strings
```

The compatibility reconstruction also preserves layer-7 grainlines and POINT entities for forensic use.

## Duplicate BLOCK names — corrected confidence statement

Purchased `1.dxf` and `2.dxf` contain repeated BLOCK names for material variants.

The compatibility reconstruction deliberately uses:

```text
first duplicate BLOCK occurrence wins
```

because that rule reproduces the Claude-era direct-copy outputs observed in the surviving generated files.

However the original `blocks.py` source is lost, and the copied pieces available for replay do **not** uniquely rule out every alternative selection heuristic. In several tested body blocks the first occurrence is also the shell and/or has equal or larger point count, so `first occurrence wins` cannot be promoted from compatibility behavior to recovered historical implementation fact.

Use:

```text
COMPATIBILITY_BEHAVIOR: first occurrence wins
ORIGINAL_SELECTION_ALGORITHM: UNVERIFIED
```

The lower-skirt raw order is nevertheless important:

- `1.dxf` lower-skirt lining appears before shell;
- `2.dxf` lower-skirt lining appears before shell.

That makes first-occurrence selection a plausible explanation for why legacy `PROF_A/B` numerics align with lining geometry, but no surviving derivation script proves the causal chain.

## Reconstructed `upright()` contract

The first two outputs are strongly verified for surviving direct-copy callers:

1. select the first layer-14 polyline as net geometry;
2. select the first layer-1 polyline as cut geometry;
3. use the layer-14 point centroid as common transform origin;
4. read the first layer-7 grainline direction;
5. rotate that direction onto positive Y;
6. apply the same rigid transform to net and cut geometry.

The compatibility module returns transformed grainline as the third value. No surviving caller uses that value, so it is useful but **not claimed as verified historical behavior**.

## Direct replay verification

Seven pieces documented by `build_set.py` as direct copies from purchased `2.dxf` were replayed into stored style 4 geometry:

- `2.前中.L` -> `4.前中.L`
- `2.左前侧.L` -> `4.左前侧.L`
- `2.右前侧.L` -> `4.右前侧.L`
- `2.后中.L` -> `4.后中.L`
- `2.后侧.L` -> `4.后侧.L`
- `2.领子.L` -> `4.领子.L`
- `2.领坐.L` -> `4.领坐.L`

The style-4 replay differs by at most about `4.61e-7 mm`, consistent with its DXF write rounding.

A broader replay of 76 direct-copy pieces across stored styles 09-12 and 14-21 reaches approximately `4.10e-12 mm` after placement translation removal.

Following adversarial review, stored generated DXFs were re-parsed from disk again rather than compared to generator RAM. Examples:

```text
09 direct-copy blocks: max error ~3.64e-12 mm
16 direct-copy body blocks: max error ~2.29e-12 mm
```

Therefore the very small replay error is a real stored-DXF round-trip property of these generator outputs, not an in-memory comparison artifact.

## Source-format boundary

Direct re-check of the purchased `1.dxf` / `2.dxf` used here found:

```text
LWPOLYLINE entities: 0
non-zero VERTEX bulges: 0
```

So hidden bulge arcs do not affect these two source files. The compatibility parser is still intentionally narrow and must not be treated as a general AAMA/DXF implementation.

## Safety boundary

Use this compatibility module only for:

- replaying old Claude generation scripts;
- provenance reconstruction;
- comparing generated artifacts to their source pipeline;
- reproducing historical measurement claims.

Do not use it to:

- define production drafting rules;
- silently select shell/lining semantics for the new engine;
- establish universal AAMA layer meaning;
- replace explicit semantic parsing of purchased references;
- support new production geometry.

The new parametric engine remains independent of this compatibility layer.
