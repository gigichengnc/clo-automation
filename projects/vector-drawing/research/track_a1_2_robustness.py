"""Track A.1.2 — robustness checks on the Track A.1 conclusions.

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT

Track A.1 overstated its statistical conclusions. This script adds the four
checks needed to state them correctly:

1. bootstrap confidence intervals, and an explicit equivalence question:
   can AUC >= 0.70 be excluded, or is this only failure-to-reject?
2. paired bootstrap on the DIFFERENCE in AUC, since two separate tests
   against random labels cannot establish that one score beats another;
3. leave-one-region-out sensitivity, because 19 boundary pairs drawn from
   10 regions are not 19 independent observations;
4. an ablation over the coarse-scale parameters of the synthetic 2x2
   fixture, because structure_mask applies a min_size cleanup that removes
   small components independently of scale persistence.

"microAUC" from Track A.1 is renamed "length-weighted AUC" here. Cells along
one boundary are not independent observations, so the macro figure is the
more meaningful one.

    python track_a1_2_robustness.py --image crop.png
"""
from __future__ import annotations

import argparse
import itertools

import numpy as np
from PIL import Image

from track_a1_isolate import SCORES, collect
from track_a1_synthetic import evaluate
from track_a_fixture import load_fixture, rasterize

USEFUL_AUC = 0.70          # pre-declared minimum effect worth implementing


def auc_macro(score, label):
    pos, neg = score[label == 1], score[label == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    return float(np.mean([(1.0 if p > n else 0.5 if p == n else 0.0) for p in pos for n in neg]))


def auc_weighted(score, label, weight):
    pos = [(s, w) for s, l, w in zip(score, label, weight) if l == 1]
    neg = [(s, w) for s, l, w in zip(score, label, weight) if l == 0]
    num = den = 0.0
    for (p, wp), (n, wn) in itertools.product(pos, neg):
        w = wp * wn
        den += w
        num += w * (1.0 if p > n else 0.5 if p == n else 0.0)
    return num / den if den else float("nan")


def strat_boot_idx(label, rng):
    pos = np.nonzero(label == 1)[0]
    neg = np.nonzero(label == 0)[0]
    return np.concatenate([rng.choice(pos, len(pos), True), rng.choice(neg, len(neg), True)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--boot", type=int, default=4000)
    args = ap.parse_args()

    meta, roles = load_fixture()
    gt = rasterize(meta)
    h, w = gt.shape
    rgb = np.asarray(Image.open(args.image).convert("RGB").resize((w, h)), dtype=np.float64) / 255.0
    rows = collect(gt, meta, roles, rgb)
    label = np.array([1 if r["role"] == "REGION_BOUNDARY" else 0 for r in rows])
    weight = np.array([r["n"] for r in rows], dtype=float)
    scores = {n: np.array([s * r[n] for r in rows], dtype=float) for n, s in SCORES}
    rng = np.random.default_rng(0)

    # ---- 1. bootstrap CI + equivalence -------------------------------------
    print("1. Bootstrap CI on AUC  (stratified, %d replicates)\n" % args.boot)
    print(f"{'score':<12} {'macroAUC':>9} {'95% CI':>18} {'excl >=0.70?':>13} {'len-wtd':>9}")
    boots = {}
    for name in scores:
        vals = []
        for _ in range(args.boot):
            idx = strat_boot_idx(label, rng)
            vals.append(auc_macro(scores[name][idx], label[idx]))
        vals = np.array(vals)
        boots[name] = vals
        lo, hi = np.percentile(vals, [2.5, 97.5])
        excl = "yes" if hi < USEFUL_AUC else "NO"
        print(f"{name:<12} {auc_macro(scores[name], label):>9.3f} "
              f"[{lo:>6.3f},{hi:>6.3f}] {excl:>13} "
              f"{auc_weighted(scores[name], label, weight):>9.3f}")
    print(f"\n   pre-declared useful effect: AUC >= {USEFUL_AUC}")
    print("   'NO' means the data cannot exclude a useful effect: failure to")
    print("   reject, not evidence of equivalence.")

    # ---- 2. paired DeltaAUC -------------------------------------------------
    print("\n2. Paired bootstrap on DeltaAUC = AUC(other) - AUC(persist)\n")
    print(f"{'comparison':<26} {'Delta':>8} {'95% CI':>18} {'P(Delta<=0)':>12}")
    rng = np.random.default_rng(1)
    idxs = [strat_boot_idx(label, rng) for _ in range(args.boot)]
    for name in scores:
        if name == "persist":
            continue
        d = np.array([auc_macro(scores[name][i], label[i]) - auc_macro(scores["persist"][i], label[i])
                      for i in idxs])
        lo, hi = np.percentile(d, [2.5, 97.5])
        obs = auc_macro(scores[name], label) - auc_macro(scores["persist"], label)
        print(f"{name + ' vs persist':<26} {obs:>8.3f} [{lo:>6.3f},{hi:>6.3f}] "
              f"{float(np.mean(d <= 0)):>12.3f}")

    # ---- 3. leave-one-region-out -------------------------------------------
    print("\n3. Leave-one-region-out (macro AUC; pairs touching the region removed)\n")
    regions = [l["name"] for l in meta["layers"]]
    header = f"{'score':<12} {'full':>7}"
    for r in regions:
        header += f" {r[:9]:>10}"
    print(header)
    for name in scores:
        line = f"{name:<12} {auc_macro(scores[name], label):>7.3f}"
        for reg in regions:
            keep = np.array([reg not in r["pair"].split("|") for r in rows])
            if label[keep].sum() == 0 or (1 - label[keep]).sum() == 0:
                line += f" {'n/a':>10}"
            else:
                line += f" {auc_macro(scores[name][keep], label[keep]):>10.3f}"
        print(line)

    # ---- 4. synthetic ablation ---------------------------------------------
    print("\n4. Synthetic 2x2 ablation over coarse-scale parameters\n")
    print("   FAIL-out = small structural outline dropped (persist < 0.5)")
    print("   FAIL-in  = large texture interior kept    (persist > 0.5)\n")
    print(f"{'config':<40} {'sm.struct':>10} {'lg.texture':>11} {'verdict':>18}")
    grid = []
    for ms in (0, 20, 60, 120, 240):
        grid.append(dict(min_size=ms))
    for bl in (1, 3, 8):
        grid.append(dict(blur=bl))
    for ds in (2, 8):
        grid.append(dict(downscale=ds))
    for k in (4, 10):
        grid.append(dict(k=k))
    grid.append(dict(min_size=0, blur=1, downscale=2))
    for cfg in grid:
        res = evaluate(**cfg)
        s_small = res["small_structural outline"][2]
        s_tex = res["large_texture interior bands"][2]
        v = []
        if s_small < 0.5:
            v.append("FAIL-out")
        if s_tex > 0.5:
            v.append("FAIL-in")
        label_cfg = ", ".join(f"{k}={v2}" for k, v2 in cfg.items())
        print(f"{label_cfg:<40} {s_small:>10.3f} {s_tex:>11.3f} {'+'.join(v) or 'ok':>18}")


if __name__ == "__main__":
    main()
