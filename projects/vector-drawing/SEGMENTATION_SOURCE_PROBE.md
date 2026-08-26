# Segmentation Source Probe — SAM 2.1 AMG vs RGB k-means

## Status

`RESEARCH_PROTOTYPE` / `NOT_PRODUCTION_OUTPUT`
`DEVELOPMENT FIXTURE — see Fixture status`

Answers exactly one question:

> Does replacing RGB colour quantization with SAM 2.1 automatic mask generation
> materially improve the region partition **before** cleanup?

Nothing here is attached to `region_partition.py`, role prediction, curve
fitting or SVG output.

The measurement protocol was fixed in advance by
`REGION_ROLE_TRACK_A_COMPARISON.md`: measure raw proposals **before**
normalization, then again after, so that cleanup cannot silently rescue a weak
proposal source.

## Environment

```text
Python            3.13.9   Windows-11-10.0.26200
PyTorch (venv)    2.13.0+cpu
CUDA available    False
GPU               none (Intel integrated graphics only; nvidia-smi absent)
free disk         53.1 GB
sam2              1.1.0 (PyPI), isolated venv, project dependencies untouched
checkpoint        sam2.1_hiera_tiny.pt  156.0 MB
                  sha256 7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69
```

SAM 1 (`segment-anything`) was deliberately not installed.

Wall-clock timings are **not reported as measurements**: the host slept during
runs, so elapsed figures are unreliable. The only timing claim made is
qualitative — CPU inference is too slow for iteration.

## Metric definitions

Let the image domain be a grid of cells with `|W| = H x W`.
Let `P = {p_1 ... p_n}` be the proposal set: masks, which may overlap and may
leave cells uncovered. Let `R` be a partition: disjoint and covering.
Let `G = {g_1 ... g_k}` be the ground-truth partition.
`B_X` denotes the boundary cell set of `X`; `dil(S, t)` is binary dilation of
`S` by `t` cells. All boundary metrics use `t = 4`.

```text
count                 n                                    integer >= 0

pixel coverage        |union_i p_i| / |W|                  [0, 1]

unassigned fraction   1 - coverage                         [0, 1]

overlap multiplicity  (sum_i |p_i|) / |W|                  [0, n]
  (mean)              = mean number of masks covering a
                        cell. Equals 1 for a covering
                        partition. NOT bounded by 1.

overlap ratio         |{x : #{i : x in p_i} >= 2}| / |W|   [0, 1]

boundary recall       |B_G ∩ dil(B_P, t)| / |B_G|          [0, 1]

boundary precision    |B_P ∩ dil(B_G, t)| / |B_P|          [0, 1]

boundary F1           2 * precision * recall               [0, 1]
                      / (precision + recall)

fragmentation(g)      #{p : |p ∩ g| >= 0.5|p|              integer >= 0
                           and |p ∩ g| >= 0.01|g|}
  reported as mean and max over g in G.
```

### under-segmentation bleed

```text
UE = (1/|W|) * sum_{g in G} sum_{p : p ∩ g != {}} min(|p ∩ g|, |p \ g|)
```

**This is not a percentage and not a rate.** Its denominator is the image area,
but the numerator may count the same cell once per ground-truth region a mask
crosses, so overlapping or region-crossing proposals accumulate.

Valid range:

```text
0 <= UE <= overlap multiplicity (mean)
```

because `min(|p ∩ g|, |p \ g|) <= |p ∩ g|` and `sum_g |p ∩ g| = |p|` when `G`
partitions the domain. For a covering partition the multiplicity is 1, so
`UE` lies in `[0, 1]` there; for raw overlapping masks it may exceed 1.

Observed values satisfy the bound:

```text
RAW SAM default     UE 0.356   multiplicity 0.495
RAW SAM relaxed     UE 1.303   multiplicity 1.811
NORM default        UE 0.870   multiplicity 1.000
NORM relaxed        UE 0.522   multiplicity 1.000
```

Read `UE` as *normalized bleed*, comparable only between rows of similar
multiplicity. Comparing `1.303` against `0.345` without also comparing
multiplicity would be misleading.

---

## Primary result — pre-specified AMG defaults

`SAM2AutomaticMaskGenerator`, `points_per_side=32`,
`pred_iou_thresh=0.80`, `stability_score_thresh=0.95`, `crop_n_layers=0`.
These are the documented defaults and were fixed before looking at any output.

```text
                              GT       RGB k-means   RAW SAM default   NORM SAM default
mask / region count           10       211           8                 8
pixel coverage                1.000    1.000         0.492             1.000
unassigned fraction           0.000    0.000         0.508             0.000
overlap multiplicity (mean)   1.000    1.000         0.495             1.000
overlap ratio (>=2)           0.000    0.000         0.002             0.000
boundary recall               1.000    0.614         0.179             0.076
fragmentation mean            1.00     7.90          0.60              0.70
fragmentation max             1        17            4                 5
under-segmentation bleed      0.000    0.345         0.356             0.870
frac of parts < 1% of image   0.000    0.886         0.625             0.125
area min/q1/med/q3/max        6412/    55/101/       296/517/          547/4965/
                              15974/   218/658/      1123/11860/       9935/28469/
                              28676/   24456         95712             159072
                              34478/
                              52678
```

### Recall alone is unfair to a sparse proposer

`RGB k-means` emits 27 366 boundary cells; `RAW SAM default` emits 4 082, a
6.7x difference. Recall rewards proposing more boundaries, so precision must be
reported alongside it:

```text
vs all GT boundaries (t=4)   precision   recall      F1   boundary cells
GT                               1.000    1.000   1.000            3459
RGB k-means                      0.125    0.560   0.204           27366
RAW SAM default                  0.131    0.148   0.139            4082
NORM SAM default                 0.114    0.058   0.077            1974
```

Precision is depressed for every row because the fixture polygons are accurate
only to roughly 10-20 cells while `t = 4`. Only the relative ordering is
meaningful.

**SAM's precision matches k-means (0.131 vs 0.125). The entire gap is recall.**
The failure is not wrong boundaries; it is too few of them.

### Answer

**No.** At the pre-specified configuration SAM 2.1 Tiny does not materially
improve the partition: F1 0.139 against 0.204 for RGB k-means, with 50.8% of
the image left unassigned.

## Secondary result — post-hoc, development-only

`pred_iou_thresh=0.50`, `stability_score_thresh=0.80`.

> **These thresholds were chosen after inspecting coverage on this same crop and
> observing which structures were missing.** They are contaminated by the
> fixture and are recorded as a sensitivity probe only. They are not evidence
> of improvement and must not be quoted as a result.

```text
                              [post-hoc] RAW relax   [post-hoc] NORM relax
mask / region count           44                     46
pixel coverage                0.982                  1.000
overlap ratio (>=2)           0.468                  0.000
boundary recall               0.521                  0.364
under-segmentation bleed      1.303                  0.522
boundary F1                   0.226                  0.228
```

Even tuned on the fixture it reaches F1 0.226-0.228 against k-means 0.204 —
roughly parity, on the image it was tuned against. Raw overlap ratio 0.468
means nearly half the image is claimed by two or more masks.

## Finding: forcing a complete partition made the result worse

```text
RAW SAM default          coverage 0.492   F1 0.139   bleed 0.356
        |
        |  nearest-region normalization
        v
NORMALIZED SAM default   coverage 1.000   F1 0.077   bleed 0.870
```

Coverage improved to 100% while every quality measure degraded. Filling 50.8%
unassigned area by nearest-region assignment smears eight masks across the
whole frame.

**A complete partition is not by itself a quality property.** If the front end
only understands half the image, forcing it to 100% manufactures false
certainty.

### Architecture implication (recorded only — no code change)

The normalization interface may eventually want an admission gate:

```text
raw proposal
    |
    +-- coverage sufficient?
    +-- overlap acceptable?
    +-- boundary evidence sufficient?
            |
            +-- NO  -> SAFE-STOP
            +-- YES -> normalize
```

rather than the current implicit contract of "normalize whatever arrives to
100%". This is not implemented and `region_partition.py` is untouched.

## Fixture status

This city crop is now a **development fixture**.

```text
any SAM threshold or parameter chosen after looking at this image
    -> must be frozen
    -> then tested once on a second unseen holdout image
    -> with no retuning
```

`0.50 / 0.80` is already contaminated by this fixture and carries that
condition.

## What this does NOT establish

- One crop, one image, one annotator, one model size.
- Fixture polygons are accurate to roughly 10-20 cells, so absolute precision
  and F1 are depressed for all rows.
- Only `points_per_side=32` was tested at each threshold setting.
- No holdout image has been used.
- Nothing here says SAM 2.1 is unsuitable in general; it says this
  configuration, on this fixture, did not improve the partition.

## Next step

The towers on the left and right are absent from the proposal set. Before
changing model size, locate which stage loses them:

```text
point-grid multimask predictions
    -> predicted-IoU filter
    -> stability filter
    -> crop-edge filter
    -> box NMS
    -> final masks
```

and separately ask `SAM2ImagePredictor`, with explicit positive points inside
each missing tower, whether a good mask exists at all and what scores it
receives.

```text
good prompted mask + low quality score   -> threshold / calibration problem
good prompted mask + high score, absent  -> point-grid / NMS / proposal path
no good prompted mask                    -> model or representation limit
```

Increasing model size before this is answered would spend compute to hide the
question.

## Reproduce

```bash
python sam_probe.py            # IOU / STAB / PPS / TAG via environment
```
