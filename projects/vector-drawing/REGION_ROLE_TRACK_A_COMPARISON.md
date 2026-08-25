# Region Role Assignment — Track A vs Track B

## Status

`RESEARCH_PROTOTYPE` / `NOT_PRODUCTION_OUTPUT`

This completes the comparison named at the end of
`REGION_TO_LAYERED_VECTOR_STEP0.md`:

```text
Track A — raster + manually verified region partition
Track B — same raster + automatic segmentation proposal

Comparing A and B tells us whether failure comes from segmentation
or from the vector/layer backend.
```

It also **corrects an overstatement** in
`REGION_ROLE_ASSIGNMENT_TRACK_B.md`. See "Correction" below.

## Track A fixture

One crop of the Track B photograph, hand-authored as ten polygon regions
rasterized in painter's order:

```text
sky_bright  cloud_dark  cloud_mid  sky_haze_left  ridge
tower_right bldg_right_low  tower_mid  tower_left  foreground
```

Painter's order means "every cell has exactly one region id" is guaranteed by
construction, not by cleanup. 27 boundary roles were hand-assigned:
19 `REGION_BOUNDARY`, 8 `FILL_ONLY`.

The fixture stores polygon coordinates only. No image pixels are committed.

**Facade window bands are deliberately not regions.** A tower facade is one
region. If Track B splits a facade into thirty bands, that is a segmentation
error, not a role error. This is what makes the two error sources separable.

An unlabelled adjacent pair raises `SAFE-STOP` rather than defaulting. The
first fixture run did exactly this, catching a missing `tower_left / sky_bright`
pair.

## Method

Every Track B line cell is classified against the fixture:

```text
within tol of a REGION_BOUNDARY  -> correct
within tol of a FILL_ONLY edge   -> ROLE ERROR
inside a GT region               -> SEGMENTATION ERROR
```

Fixture polygons are approximate, so a tolerance sweep is reported instead of a
single figure.

## Result

```text
GT regions 10   proposed regions 211   over-segmentation 21.1x

 tol proposer      precision   recall  interior  role-err
   2 baseline          13.1%    13.7%     86.5%      0.4%
   2 persistence       15.4%    11.3%     84.0%      0.6%
   4 baseline          24.3%    22.2%     75.3%      0.5%
   4 persistence       28.6%    19.8%     70.6%      0.7%
   8 baseline          43.5%    39.0%     55.9%      0.7%
   8 persistence       55.2%    35.4%     43.7%      1.1%
  12 baseline          55.1%    52.7%     44.2%      0.8%
  12 persistence       72.4%    48.5%     26.4%      1.2%
  20 baseline          69.2%    66.4%     29.9%      0.9%
  20 persistence       89.8%    63.0%      8.9%      1.4%
```

## Finding 1: role assignment is not the bottleneck

Role error stays **below 1.5% at every tolerance**. Soft cloud and haze
boundaries are almost never drawn as lines.

The `FILL_ONLY` half of the Step 0 vocabulary is, for this image, already
handled by gradient and colour contrast. It does not need more work yet.

## Finding 2: segmentation is the bottleneck, in two directions

**Over-segmentation.** 211 proposed regions against 10 real ones. At tol 8,
44–56% of proposed line cells lie inside a ground-truth region — they are
facade texture promoted to geometry.

**Under-detection.** Recall is only 35–39% at tol 8. More than half of the real
structural silhouette is never proposed at all. This is the larger problem and
was invisible in the Track B probe, which only counted cells removed.

Colour quantization plus connected components is not an adequate partition
source for this domain.

## Finding 3: the persistence gate survives, and is now measured

Persistence improves precision at every tolerance and specifically reduces
interior cells:

```text
tol 8    precision 43.5% -> 55.2%    interior 55.9% -> 43.7%
tol 12   precision 55.1% -> 72.4%    interior 44.2% -> 26.4%
tol 20   precision 69.2% -> 89.8%    interior 29.9% ->  8.9%
```

The monotonic pattern across tolerances means the effect is not an artefact of
one threshold. It costs recall (39.0% -> 35.4% at tol 8), so it is a genuine
precision/recall trade rather than a free improvement.

## Correction to the Track B probe

`REGION_ROLE_ASSIGNMENT_TRACK_B.md` reported that persistence removed 72% of
line cells and framed this as progress on the role-assignment problem.

Track A shows that framing was too strong:

> Most of the removed cells were **over-segmentation artefacts**, not correctly
> reclassified texture boundaries. The persistence gate was largely
> compensating for a bad partition rather than answering "should this boundary
> be drawn".
>
> The mechanism claim (structure survives blur, texture does not) holds and is
> now measured against ground truth. The significance claim was overstated.

The Track B document should be read together with this one.

## What this does NOT prove

- One crop of one image. One domain. Not garment.
- Fixture polygons are accurate to roughly 10–20 px. Absolute precision and
  recall are therefore unreliable; only the relative comparison between
  proposers is trustworthy.
- Roles were assigned by one author with no second opinion. `ridge` was called
  `FILL_ONLY` by judgement, not by rule.
- Still raster. No closed-loop vectorization, smoothing or DXF.
- Colour quantization in RGB, not a perceptual space.

## Next falsification step

Segmentation is now the measured bottleneck, so the next probe should hold the
role proposer fixed and vary only the partition source:

1. replace colour quantization with a stronger proposal (for example SAM masks
   plus the existing normalization step);
2. re-run this comparison unchanged;
3. if recall rises substantially while role error stays under a few percent,
   the partition source was the limiting factor and role assignment can be
   revisited on a sound partition;
4. a second author should re-label the fixture independently to estimate how
   much of the disagreement is annotation noise.

Do not attach the proposer to `region_partition.py` until recall is credible.

## Current conclusion

> On this image the visible-line role problem is not the limiting factor.
> Distinguishing soft boundaries from structural ones already works. What fails
> is obtaining the partition: the segmenter over-segments facades by an order
> of magnitude and misses more than half of the real silhouette. Scale
> persistence is a real, monotonic precision improvement, but it is treating a
> symptom of the partition rather than solving boundary roles.

## Reproduce

```bash
python projects/vector-drawing/research/track_a_fixture.py
python projects/vector-drawing/research/track_ab_compare.py --image crop.png
```

> **Finding 3 RETRACTED.** See `REGION_ROLE_TRACK_A1_FALSIFICATION.md`. The
> monotonic precision gain was real but misattributed: persistence suppresses
> small-scale boundaries, and on an over-segmented partition most spurious
> boundaries are small. Findings 1 and 2 stand.
