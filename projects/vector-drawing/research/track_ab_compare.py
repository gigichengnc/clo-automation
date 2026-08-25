"""Compare Track A (hand-labelled) against Track B (automatic proposal).

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT

Purpose, per REGION_TO_LAYERED_VECTOR_STEP0.md: determine whether failure
comes from segmentation or from role assignment.

Every proposed line cell is classified against the hand-labelled fixture:

    on a REGION_BOUNDARY   -> correct
    on a FILL_ONLY edge    -> role-assignment error
    inside a GT region     -> segmentation error (over-segmentation / texture)

The fixture polygons are approximate, so a tolerance sweep is reported
rather than a single number. Only the relative comparison between proposers
should be trusted.

    python track_ab_compare.py --image cropped.png
"""
from __future__ import annotations

import argparse

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from region_role_track_b import boundary_pairs, propose_roles, segment
from track_a_fixture import load_fixture, rasterize, role_masks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="photograph cropped to the fixture size")
    ap.add_argument("--colours", type=int, default=14)
    ap.add_argument("--min-size", type=int, default=55)
    args = ap.parse_args()

    meta, roles = load_fixture()
    gt = rasterize(meta)
    gt_line, gt_fill = role_masks(gt, meta, roles)
    h, w = gt.shape

    im = Image.open(args.image).convert("RGB")
    if im.size != (w, h):
        im = im.resize((w, h), Image.LANCZOS)
    rgb = np.asarray(im, dtype=np.float64) / 255.0

    d_line = ndi.distance_transform_edt(~gt_line)
    d_fill = ndi.distance_transform_edt(~gt_fill)

    labels, smoothed = segment(rgb, args.colours, args.min_size)
    pairs = boundary_pairs(labels)

    print(f"GT regions {len(np.unique(gt))}   proposed regions {len(np.unique(labels))}"
          f"   over-segmentation {len(np.unique(labels)) / len(np.unique(gt)):.1f}x")
    print()
    print(f"{'tol':>4} {'proposer':<12} {'precision':>10} {'recall':>8} {'interior':>9} {'role-err':>9}")

    proposals = {
        "baseline": propose_roles(rgb, labels, pairs, smoothed, use_persistence=False),
        "persistence": propose_roles(rgb, labels, pairs, smoothed, use_persistence=True),
    }
    for tol in (2, 4, 8, 12, 20):
        for name, keys in proposals.items():
            mask = np.zeros(labels.shape, bool)
            for key in keys:
                for y, x in pairs[key]:
                    mask[y, x] = True
            total = max(int(mask.sum()), 1)
            hit = int((mask & (d_line <= tol)).sum())
            role_err = int((mask & (d_line > tol) & (d_fill <= tol)).sum())
            interior = total - hit - role_err
            recall = (gt_line & ndi.binary_dilation(mask, iterations=tol)).sum() / max(gt_line.sum(), 1)
            print(f"{tol:>4} {name:<12} {100*hit/total:>9.1f}% {100*recall:>7.1f}%"
                  f" {100*interior/total:>8.1f}% {100*role_err/total:>8.1f}%")


if __name__ == "__main__":
    main()
