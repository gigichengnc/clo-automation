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

Every surviving `upright()` caller consumes three return values but ignores the third one.

## Reconstructed `parse()` contract

The callers establish that `parse(path)` returns a mapping keyed by AAMA BLOCK / piece name and that each value exposes at least:

```text
block["polys"] -> list of {"layer", "pts", ...}
block["texts"] -> list of TEXT strings
```

The reconstruction also preserves layer-7 grainlines and POINT entities for forensic use.

### Duplicate BLOCK names

Purchased `1.dxf` and `2.dxf` contain repeated BLOCK names for material variants. The replay evidence establishes **first occurrence wins** for the legacy behavior needed by the surviving pipeline.

Key proof: purchased `2.dxf` contains two `2.前中.L` BLOCKs. The first is the shell (`Material: 米白色面`) with 680 layer-14 points; the second is lining with 673. Claude's generated `4.前中.L`, created by `build_set.py` through `upright(SRC['2.前中.L'])`, contains 680 layer-14 points and reproduces the first occurrence geometry.

## Reconstructed `upright()` contract

Verified first two outputs:

1. select the first layer-14 polyline as net geometry
2. select the first layer-1 polyline as cut geometry
3. use the layer-14 point centroid as the common transform origin
4. read the first layer-7 grainline direction
5. rotate that direction onto positive Y
6. apply the same rigid transform to net and cut geometry

The reconstruction returns the transformed grainline as the third value. No surviving caller uses this value, so this third-value choice is useful but **not claimed as verified behavior of the lost source**.

## Direct replay verification

The reconstruction was checked against the purchased `2.dxf` and Claude-generated `4.恤衫連衣裙.L.dxf` produced by the surviving `build_set.py` logic.

Seven pieces documented by `build_set.py` as direct copies from `2.dxf` were replayed:

- `2.前中.L` → `4.前中.L`
- `2.左前侧.L` → `4.左前侧.L`
- `2.右前侧.L` → `4.右前侧.L`
- `2.后中.L` → `4.后中.L`
- `2.后侧.L` → `4.后侧.L`
- `2.领子.L` → `4.领子.L`
- `2.领坐.L` → `4.领坐.L`

After applying the documented `build_set.py` X origins, the maximum pointwise difference across layer-14 net and layer-1 cut contours was:

```text
4.61e-7 mm
```

This is consistent with DXF decimal write rounding and strongly verifies the reconstructed first-two-output behavior.

The same parser reports the purchased source inventories already established by direct audit:

```text
1.dxf -> 14 unique piece names
2.dxf -> 21 unique piece names
```

Using the surviving `edges.py` corner/split/length algorithm on reconstructed `upright(2.dxf)` also reproduces legacy measurements including:

```text
2.前中.L    ... 197.8, ... 101.3, ...
2.左前侧.L  135.8, 279.8, 129.3, 146.1
2.右前侧.L  135.8, 146.1, 129.3, 279.8
```

These results explain the handover's front-waist / princess / armhole / side-seam values without promoting those legacy edge interpretations to production truth.

## Safety boundary

Use this compatibility module only for:

- replaying old Claude generation scripts
- provenance reconstruction
- comparing generated artifacts to their source pipeline
- reproducing historical measurement claims

Do not use it to:

- define production drafting rules
- silently select shell/lining semantics for the new engine
- establish AAMA layer meaning for the new architecture
- replace direct semantic parsing of purchased references
- support new production geometry

The new parametric engine remains independent of this compatibility layer.
