# Track A.1 — Persistence Gate Isolated: No Evidence of Boundary-Role Signal

## Status

`RESEARCH_PROTOTYPE` / `NOT_PRODUCTION_OUTPUT`
`SUPERSEDES Finding 3 of REGION_ROLE_TRACK_A_COMPARISON.md`
`PARTIALLY CORRECTED BY REGION_ROLE_TRACK_A1_2_ROBUSTNESS.md`

> **Revision.** This document originally claimed falsification. Robustness
> checks in `REGION_ROLE_TRACK_A1_2_ROBUSTNESS.md` show the statistical
> conclusions were overstated: the interval on persistence cannot exclude a
> useful effect, `sum_area` has not been shown to beat it, and half the 2x2
> failure was a cleanup-parameter artefact. The engineering decision stands;
> the strength of the claims does not. Read that document alongside this one.

## Question

Does coarse-scale persistence contain information beyond *"large or long
boundaries survive coarse segmentation"*?

Both earlier probes scored persistence on boundaries emitted by an
over-segmenting proposer, so its apparent skill was confounded with partition
quality. Track A.1 removes that confound by using the **hand-labelled Track A
boundaries themselves** as the candidate set. Segmentation is perfect by
construction; only role assignment is under test.

## Result 1: on a correct partition, no association is detectable

19 adjacent ground-truth pairs (13 `REGION_BOUNDARY`, 6 `FILL_ONLY`).
Permutation test, 10 000 label shuffles.

```text
score          macroAUC       p   microAUC       p
persist           0.564   0.349      0.614   0.246
length            0.603   0.254      0.343   0.824
min_area          0.654   0.156      0.741   0.090
sum_area          0.769   0.034      0.883   0.016
tortuosity        0.692   0.106      0.851   0.027
```

Persistence is the weakest discriminator tested, and the null of no
association cannot be rejected.

**This is failure to reject, not evidence of equivalence.** A bootstrap
interval (Track A.1.2) puts persistence at 0.564 [0.269, 0.833], which does not
exclude a useful effect.

The trivial control `sum_area` — the summed pixel area of the two adjoining
regions, which uses no image content at all — shows the largest observed
association.

> **Corrected.** Comparing two separate tests against permuted labels does not
> establish that one score beats another. A paired bootstrap on the difference
> (Track A.1.2) gives DeltaAUC 0.205 [-0.128, 0.538]: `sum_area` has **not**
> been shown to outperform persistence.

Matched-budget retention agrees: at every budget from N=2 to N=18, persistence
retains no more true `REGION_BOUNDARY` pairs than `sum_area` or `tortuosity`,
and at several budgets fewer.

## Result 2: the 2x2 counterexample shows why

Fully synthetic fixture, ground truth known by construction:

```text
small structural | large structural
small texture    | large texture
```

```text
group                          GT role           cells   persist
large_structural outline       REGION_BOUNDARY     600     1.000
large_texture interior bands   TEXTURE             900     0.983   FAIL kept-in
large_texture outline          REGION_BOUNDARY     600     0.963
small_structural outline       REGION_BOUNDARY     104     0.000   FAIL kept-out
small_texture interior bands   TEXTURE            1980     0.469
small_texture outline          REGION_BOUNDARY     360     0.983
```

Both off-diagonal cases fail under the default configuration:

- a genuine silhouette that happens to be **small** scores `0.000` and is
  discarded;
- pure texture that happens to be **wide-period** scores `0.983` and is kept.

> **Corrected.** Ablation (Track A.1.2) shows the small-structure failure is
> caused by the coarse-segmentation `min_size` cleanup, not by persistence: at
> `min_size=0` that outline scores 1.000. The wide-texture failure survives
> ablation across `min_size`, `blur`, `downscale` and `k`, and is the one
> genuine scale-prior signature demonstrated here.

## Retraction

`REGION_ROLE_ASSIGNMENT_TRACK_B.md` Finding 2 claimed:

> scale persistence is a cheap proxy for occlusion reasoning ... it recovers a
> large part of what depth estimation or semantic segmentation would provide

`REGION_ROLE_TRACK_A_COMPARISON.md` Finding 3 then reported it as a monotonic
precision gain and called the mechanism claim confirmed.

**Both are withdrawn.** The monotonic gain was real but its cause was
misattributed: persistence was suppressing over-segmentation artefacts, which
are small by definition. Given a correct partition it carries no measurable
signal about whether a boundary should be drawn.

The correct statement is narrower:

> Coarse-scale persistence suppresses small-scale boundaries. On an
> over-segmented partition most spurious boundaries are small, so this
> resembles structure detection. It is not.

## Incidental finding: two controls do carry signal

`sum_area` (macro 0.769 / micro 0.883) and `tortuosity` (micro 0.851) are the
only scores reaching conventional significance.

Both should be treated with suspicion rather than adopted:

- **`sum_area`** may simply encode that this fixture's structural regions
  (towers, sky) are the large ones. On a scene of many small objects the same
  score would invert.
- **`tortuosity`** — straight boundaries are structural, wiggly ones are soft —
  is plausible for *architecture* and likely reverses for organic subjects,
  where real silhouettes are highly curved. It is probably a building-domain
  cue, not a general one.

Neither should enter `region_partition.py` before being tested on a second
domain.

## What this does NOT prove

- n = 19 pairs, 13 positive / 6 negative. Very small. Confidence intervals on
  every AUC above are wide.
- Five scores were tested without multiple-comparison correction. Under a
  Bonferroni threshold (0.05 / 5 = 0.01) **none** of them survives; `sum_area`
  micro at p=0.016 is the closest.
- One image, one crop, one annotator.
- The synthetic fixture is deliberately adversarial. It shows persistence *can*
  fail, not how often it fails on real data.
- Persistence parameters were not tuned here. Ablation in Track A.1.2 later
  showed one of the two 2x2 failure modes **was** parametric.

## Next falsification step

Persistence is retired as a role cue. The remaining evidence says the limiting
factor is the partition, not the role decision, so the next probe should hold
role assignment fixed and vary only the partition source, as set out in
`REGION_ROLE_TRACK_A_COMPARISON.md`.

If a role cue is wanted later, the honest ordering is:

1. re-run this isolation on a second, non-architectural fixture;
2. test `tortuosity` and `sum_area` there — the expectation is that
   `tortuosity` inverts;
3. only a cue that survives both domains deserves implementation.

## Current conclusion

> On this fixture, the current coarse-scale persistence configuration shows no
> detectable boundary-role discrimination once segmentation is held fixed. An
> adversarial synthetic fixture exposes a scale-dependent failure mode that
> survives parameter ablation. This is sufficient to reject the current
> heuristic for implementation, but not to establish that every possible
> persistence formulation is uninformative.

## Reproduce

```bash
python projects/vector-drawing/research/track_a1_isolate.py --image crop.png
python projects/vector-drawing/research/track_a1_synthetic.py
```
