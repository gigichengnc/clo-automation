"""Track A.1 — isolate the persistence gate from segmentation.

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT

The Track B probe scored persistence on boundaries produced by an
over-segmenting proposer, so its apparent skill was confounded with
partition quality. Here the candidate set is the hand-labelled Track A
boundaries themselves, so segmentation is held perfect by construction.

Question: does scale persistence carry information beyond "large or long
boundaries survive coarse segmentation"?

Controls are matched-budget: same number of retained boundaries.

    python track_a1_isolate.py --image crop.png
"""
from __future__ import annotations

import argparse
import itertools

import numpy as np
from PIL import Image

from region_role_track_b import structure_mask
from track_a_fixture import load_fixture, rasterize

SCORES = (("persist", 1), ("length", 1), ("min_area", 1), ("sum_area", 1), ("tortuosity", -1))


def collect(gt, meta, roles, rgb):
    names = {l["id"]: l["name"] for l in meta["layers"]}
    area = {l["name"]: int((gt == l["id"]).sum()) for l in meta["layers"]}
    cells: dict[tuple[str, str], list] = {}
    for arr, dy, dx in ((gt != np.roll(gt, -1, 1), 0, 1), (gt != np.roll(gt, -1, 0), 1, 0)):
        arr = arr.copy()
        if dx:
            arr[:, -1] = False
        else:
            arr[-1, :] = False
        for y, x in zip(*np.nonzero(arr)):
            cells.setdefault(tuple(sorted((names[gt[y, x]], names[gt[y + dy, x + dx]]))), []).append((y, x))

    sm = structure_mask(rgb, gt.shape)
    rows = []
    for key, cs in cells.items():
        role = roles.get(key) or roles.get((key[1], key[0]))
        ys = np.array([c[0] for c in cs])
        xs = np.array([c[1] for c in cs])
        diag = max(float(np.hypot(np.ptp(ys), np.ptp(xs))), 1.0)
        rows.append(dict(
            pair="|".join(key), role=role, n=len(cs),
            persist=float(np.mean([sm[y, x] for y, x in cs])),
            length=float(len(cs)),
            min_area=float(min(area[key[0]], area[key[1]])),
            sum_area=float(area[key[0]] + area[key[1]]),
            tortuosity=len(cs) / diag,
        ))
    return rows


def auc_macro(score, label):
    pos, neg = score[label == 1], score[label == 0]
    return float(np.mean([(1.0 if p > n else 0.5 if p == n else 0.0) for p in pos for n in neg]))


def auc_micro(score, label, weight):
    pos = [(s, w) for s, l, w in zip(score, label, weight) if l == 1]
    neg = [(s, w) for s, l, w in zip(score, label, weight) if l == 0]
    num = den = 0.0
    for (p, wp), (n, wn) in itertools.product(pos, neg):
        w = wp * wn
        den += w
        num += w * (1.0 if p > n else 0.5 if p == n else 0.0)
    return num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--permutations", type=int, default=10000)
    args = ap.parse_args()

    meta, roles = load_fixture()
    gt = rasterize(meta)
    h, w = gt.shape
    rgb = np.asarray(Image.open(args.image).convert("RGB").resize((w, h)), dtype=np.float64) / 255.0

    rows = collect(gt, meta, roles, rgb)
    label = np.array([1 if r["role"] == "REGION_BOUNDARY" else 0 for r in rows])
    weight = np.array([r["n"] for r in rows], dtype=float)
    rng = np.random.default_rng(0)

    print(f"adjacent GT pairs {len(rows)}  (REGION_BOUNDARY {label.sum()} / FILL_ONLY {(1-label).sum()})\n")
    print(f"{'score':<12} {'macroAUC':>9} {'p':>7} {'microAUC':>9} {'p':>7}")
    for name, sign in SCORES:
        score = np.array([sign * r[name] for r in rows], dtype=float)
        a_ma, a_mi = auc_macro(score, label), auc_micro(score, label, weight)
        nm = nu = 0
        for _ in range(args.permutations):
            perm = rng.permutation(label)
            nm += auc_macro(score, perm) >= a_ma
            nu += auc_micro(score, perm, weight) >= a_mi
        print(f"{name:<12} {a_ma:>9.3f} {(nm+1)/(args.permutations+1):>7.3f}"
              f" {a_mi:>9.3f} {(nu+1)/(args.permutations+1):>7.3f}")

    print("\nmatched budget: REGION_BOUNDARY retained when keeping top N")
    budgets = list(range(2, len(rows) + 1, 2))
    print(f"{'N':<12}" + "".join(f"{n:>5}" for n in budgets))
    for name, sign in SCORES:
        hits = [sum(1 for r in sorted(rows, key=lambda r: -sign * r[name])[:n]
                    if r["role"] == "REGION_BOUNDARY") for n in budgets]
        print(f"{name:<12}" + "".join(f"{h:>5}" for h in hits))
    print(f"{'ceiling':<12}" + "".join(f"{min(n, int(label.sum())):>5}" for n in budgets))


if __name__ == "__main__":
    main()
