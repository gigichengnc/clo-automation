# Track A.1.2 — Robustness Checks on the Track A.1 Conclusions

## Status

`RESEARCH_PROTOTYPE` / `NOT_PRODUCTION_OUTPUT`
`CORRECTS REGION_ROLE_TRACK_A1_ISOLATION.md`

Track A.1 reached the right engineering decision by an overstated statistical
route. This document supplies the four checks required to state the conclusion
correctly, and corrects two claims that do not survive them.

## Terminology change

What Track A.1 called `microAUC` is renamed **length-weighted AUC**. It weights
each pair by boundary cell count, and cells along one boundary are not
independent observations, so an 800-cell boundary is not 800 observations. The
macro figure is the more meaningful one and is used for all inference below.

---

## Check 1: the AUC interval cannot exclude a useful effect

Pre-declared minimum effect worth implementing: **AUC >= 0.70**.
Stratified bootstrap, 3000 replicates, 13 positive / 6 negative.

```text
score         macroAUC             95% CI  excludes >=0.70?   len-weighted
persist          0.564 [ 0.269, 0.833]                 NO          0.614
length           0.603 [ 0.256, 0.923]                 NO          0.343
min_area         0.654 [ 0.410, 0.865]                 NO          0.741
sum_area         0.769 [ 0.538, 0.949]                 NO          0.883
tortuosity       0.692 [ 0.372, 0.962]                 NO          0.851
```

**No score can exclude a useful effect, including persistence.**

The Track A.1 permutation result (p = 0.349) was a *failure to reject* the null
of no association. It is not evidence that AUC = 0.5. With this sample the
interval on persistence spans 0.27 to 0.83 and is entirely uninformative about
whether a useful effect exists.

## Check 2: `sum_area` has not been shown to beat persistence

Track A.1 tested each score separately against permuted labels and then
compared the resulting p-values. That is an invalid inference. The paired
quantity must be tested directly.

Paired bootstrap on `DeltaAUC = AUC(other) - AUC(persist)`:

```text
comparison                    Delta             95% CI  P(Delta<=0)
length vs persist             0.038 [-0.372, 0.462]        0.456
min_area vs persist           0.090 [-0.225, 0.423]        0.318
sum_area vs persist           0.205 [-0.128, 0.538]        0.115
tortuosity vs persist         0.128 [-0.231, 0.488]        0.250
```

**Every interval contains zero.** No control has been shown to outperform
persistence.

The Track A.1 sentence "a control using only region area ... outperforms it
significantly" is **withdrawn**. The correct statement is that `sum_area`
showed the largest observed association in this fixture, that the result does
not survive multiple-comparison correction, and that it has not been shown to
beat persistence.

Counting both macro and length-weighted figures as inferential tests gives
roughly ten comparisons, not five, so the Bonferroni threshold quoted in
Track A.1 was already generous.

## Check 3: the 19 pairs are not 19 independent observations

Ten regions generate the 19 pairs, so regions recur across them. Macro AUC
recomputed with all pairs touching one region removed:

```text
score           full  sky_brigh  cloud_dar  cloud_mid  sky_haze_      ridge  tower_rig  bldg_righ  tower_mid  tower_lef  foregroun
persist        0.564      0.700      0.577      0.564      0.389      0.694      0.500      0.597      0.574      0.542      0.636
length         0.603      0.650      0.731      0.745      0.389      0.500      0.574      0.583      0.611      0.583      0.621
min_area       0.654      0.675      0.721      0.655      0.611      0.806      0.620      0.625      0.620      0.625      0.682
sum_area       0.769      0.900      0.808      0.800      0.667      0.889      0.815      0.750      0.741      0.646      0.803
tortuosity     0.692      0.550      0.635      0.655      0.667      0.861      0.685      0.708      0.667      0.729      0.697
```

`persist` swings 0.389 to 0.700 — dropping below chance on removal of a single
region. `tortuosity` swings 0.550 to 0.861. Both are unstable at this sample
size.

`sum_area` is the most stable (0.646 to 0.900), but the specific worry that one
huge region props it up is **not supported**: removing `sky_bright` *raises* its
AUC to 0.900 rather than collapsing it. The largest single drop is from removing
`tower_left` (0.769 to 0.646).

## Check 4: the 2x2 fixture had a hidden minimum-size gate

`structure_mask()` runs a coarse segmentation whose cleanup absorbs components
below `min_size`. At the default 120, the 26x26 structural square becomes about
42 coarse cells and is removed **by the cleanup rule**, not by scale
persistence. `min_size` is now an explicit parameter (default unchanged) so the
two effects can be separated.

```text
config                                    sm.struct  lg.texture            verdict
min_size=0                                    1.000       1.000            FAIL-in
min_size=20                                   0.000       1.000   FAIL-out+FAIL-in
min_size=60                                   0.000       0.987   FAIL-out+FAIL-in
min_size=120                                  0.000       0.983   FAIL-out+FAIL-in
min_size=240                                  0.000       0.048           FAIL-out
blur=1                                        0.000       0.997   FAIL-out+FAIL-in
blur=3                                        0.000       0.828   FAIL-out+FAIL-in
blur=8                                        0.000       0.859   FAIL-out+FAIL-in
downscale=2                                   0.000       1.000   FAIL-out+FAIL-in
downscale=8                                   0.000       0.000           FAIL-out
k=4                                           0.000       1.000   FAIL-out+FAIL-in
k=10                                          0.000       0.126           FAIL-out
min_size=0, blur=1, downscale=2               1.000       1.000            FAIL-in
```

Two different verdicts:

**FAIL-out is withdrawn as a persistence failure.** At `min_size=0` the small
structural outline scores 1.000. Losing it was the cleanup gate, exactly as
suspected. Track A.1's sentence "the 2x2 failure mode is structural rather than
parametric" was wrong for this half.

**FAIL-in survives ablation.** Wide-period texture is retained at `min_size`
0, 20, 60 and 120, at `blur` 1, 3 and 8, at `downscale` 2, and at `k=4`,
including under the most permissive combination tested. It is suppressed only
by settings extreme enough to erase real structure too (`downscale=8` also
drives the structural case to 0.000).

So one genuine, parameter-robust failure mode remains:

> Coarse-scale persistence cannot distinguish wide-period texture from
> structure. This is a scale-prior signature and is not an artefact of the
> cleanup configuration.

## Corrected position

```text
claim                                                    verdict
current persistence config shows no role signal here     supported
stop feeding this gate into the pipeline                 supported
persistence is generally equivalent to random guessing   NOT established
persistence is intrinsically only a scale prior          strong hypothesis
sum_area statistically beats persistence                 NOT established
2x2 exposes a scale-dependent failure in this config     supported (FAIL-in only)
2x2 shows small structures are intrinsically lost        withdrawn (min_size)
```

## What this does NOT prove

- Still one image, one crop, one annotator, 19 pairs.
- Bootstrap intervals at n=19 are themselves unreliable; percentile intervals
  on an AUC with 6 negatives are coarse.
- The ablation is one-factor-at-a-time apart from a single combined cell. No
  interaction effects were explored.
- `USEFUL_AUC = 0.70` is a judgement call, declared before the checks were run
  but not derived from any downstream requirement.

## Decision

Persistence research stops here. The engineering standard needed is not "proven
useless in all formulations" but:

```text
candidate rule -> fails to demonstrate sufficient reliability -> NOT ADOPTED
```

That standard is met. The gate is not adopted, and no further effort is spent
falsifying it.

## Next step: partition source, measured before and after normalization

The next probe replaces colour quantization with a stronger mask proposal. To
avoid the same confound recurring, raw proposals must be measured **before**
cleanup, so that normalization cannot silently rescue a weak segmenter:

```text
raw masks
   -> measure coverage, overlap, boundary recall,
      over-segmentation, under-segmentation
   -> normalization
   -> measure the same quantities again
```

Reporting only the post-normalization score would leave it impossible to tell
whether segmentation or cleanup produced the result — the identical error this
document was written to correct.

## Reproduce

```bash
python projects/vector-drawing/research/track_a1_2_robustness.py --image crop.png
```
