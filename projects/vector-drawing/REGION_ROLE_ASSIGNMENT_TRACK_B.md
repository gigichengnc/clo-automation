# Region Role Assignment — Track B Probe

## Status

`RESEARCH_PROTOTYPE` / `NOT_PRODUCTION_OUTPUT`

This continues the **Track B — automatic proposal** experiment named at the end
of `REGION_TO_LAYERED_VECTOR_STEP0.md`.

Step 0 established that a normalized partition yields closed loops and
independent recolouring. It explicitly deferred the harder question:

```text
Where does one fill region end?
                ≠
Should that boundary be drawn as a line?
```

This probe attacks only the second question, and only far enough to falsify one
candidate method.

It stays in raster space on purpose. No Bezier fitting, no closed-loop
vectorization, no DXF. Those remain in `region_partition.py` and must not
consume this output.

## Probe subject

One photograph, open domain, not garment: a dense city skyline at dusk.

The subject was chosen because it contains five boundary situations whose
correct visible-line answers differ:

```text
building silhouette vs sky      -> should be a line
facade window bands             -> should NOT be ~30 lines
cloud edges                     -> soft, should not be a line
distant ridge in haze           -> marginal
shading break on one facade     -> should not be a line
```

The input image is not committed. The script takes an explicit `--image` path.

## Method

```text
median filter
        ↓
colour quantization (k = 14)
        ↓
connected-component labelling
        ↓
NORMALIZE  (sub-threshold fragments absorbed into nearest region;
            every cell ends with exactly one region id)
        ↓
RegionPartition
        ↓
group boundary cells by unordered region pair
        ↓
propose visible-line role per pair
```

Two role proposers were compared.

**Baseline** — three features per boundary pair:

```text
mean gradient magnitude in the ORIGINAL raster
mean colour distance between the two regions
boundary length
```

**Persistence** — baseline, plus one gate:

```text
segment the image again at a coarse scale
(gaussian blur -> 1/4 downscale -> k = 6)
        ↓
a boundary is structural only if it still exists there
```

## Result

```text
regions                       408
adjacent region pairs         868
visible pairs (baseline)      233      line cells  61434
visible pairs (persistence)    70      line cells  17468
```

The persistence gate removed **72%** of remaining line cells.

Visually: the facade window bands are eliminated and the building silhouettes
survive.

## Finding 1: the baseline features cannot work, in principle

The baseline did not merely perform badly. It fails for a structural reason
worth recording:

> A facade window band scores **high on all three baseline features**. It is a
> real, high-contrast, long edge — exactly like a building silhouette.
>
> Gradient, contrast and length therefore cannot separate `texture` from
> `structure`. No threshold tuning fixes this.

Any future role proposer must introduce an axis that is not local edge
strength.

## Finding 2: scale persistence is a cheap proxy for occlusion reasoning

Structure survives blur. Texture does not.

This recovers a large part of what depth estimation or semantic segmentation
would provide, with no learned model, no depth map, and full determinism.

It is a heuristic, not a theory. It is recorded here as a candidate, not as a
resolved policy.

## Finding 3: the role vocabulary is missing a case

The Step 0 vocabulary is:

```text
REGION_BOUNDARY
INTERNAL_DETAIL
CONSTRUCTION
OCCLUSION
FILL_ONLY
```

The window band fits none of them correctly:

- it is not `FILL_ONLY` — it is a genuine high-contrast edge;
- it is not `INTERNAL_DETAIL` — emitting ~30 parallel lines is the wrong
  drawing, not a detailed one;
- suppressing it entirely also loses real information about the surface.

The correct output is neither a line nor nothing. It is a **property of the
region**:

```text
{ region: facade, texture: horizontal_bands, period: 12 cells }
```

This suggests the drawing model needs three output kinds, not two:

```text
LINE      explicit stroked path
FILL      flat colour region
TEXTURE   repeated pattern attached to a region
```

A `TEXTURE` role would let the same partition drive a stroked silhouette and a
patterned facade without inventing thirty separate paths.

This mirrors how a phone ISP performs semantic rendering: sky, skin and
foliage regions receive different local treatment rather than one global
operator.

## What this does NOT prove

- One image. One domain. Not garment.
- Thresholds were hand-tuned against this single image and are not calibrated.
- The persistence gate **over-prunes**: silhouettes acquire gaps and cloud
  boundaries disappear entirely. The usable operating point lies between the
  two proposers and has not been characterized.
- Output is still raster. Closed-loop vectorization and smoothing were not run,
  so nothing here demonstrates clean vector line quality.
- No comparison against Track A. Without a manually verified partition for the
  same image, this probe cannot attribute failure to segmentation versus role
  assignment.
- Colour quantization in RGB, not a perceptual space.

## Next falsification step

1. Build the Track A fixture: the same raster with a manually verified region
   partition and hand-assigned boundary roles.
2. Run this proposer against those labels and report per-role agreement,
   separating segmentation error from role-assignment error.
3. Characterize the operating curve between baseline and persistence rather
   than reporting two points.
4. Only then attach the proposer to `region_partition.py` and produce vectors.

## Current conclusion

> Scale persistence separates structural boundaries from texture boundaries on
> one open-domain image without any learned model, and does so far better than
> local edge strength. It also over-prunes, and it exposes that the role
> vocabulary needs a `TEXTURE` case which is neither a line nor a plain fill.

## Reproduce

```bash
python projects/vector-drawing/research/region_role_track_b.py \
  --image path/to/image.jpg \
  --out out/track-b
```

## Follow-up

See `REGION_ROLE_TRACK_A_COMPARISON.md`. The Track A comparison corrects the
significance claim made here: most of the 72% reduction was over-segmentation
artefact rather than reclassified texture, and segmentation — not role
assignment — is the measured bottleneck.
