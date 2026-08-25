"""Track B research probe: automatic region-boundary role proposal.

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT

This script does NOT produce illustration output for the pipeline. It exists to
test one narrow claim described in REGION_ROLE_ASSIGNMENT_TRACK_B.md:

    scale persistence can separate structural boundaries from texture
    boundaries without depth estimation, semantics, or a learned model.

It deliberately stays in raster space. No Bezier fitting, no closed-loop
vectorization, no DXF. Those belong to region_partition.py once a role
assignment method is trusted.

Input images are not committed to this repository. Pass one explicitly:

    python region_role_track_b.py --image path/to/photo.jpg --out out/

Dependencies: numpy, scipy, pillow, matplotlib.
"""
from __future__ import annotations

import argparse
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2


def segment(img, k, min_size, median=7, seed=0):
    """Quantize then label. Returns a normalized partition: every cell has exactly one id."""
    smoothed = np.stack([ndi.median_filter(img[..., c], size=median) for c in range(3)], -1)
    flat = smoothed.reshape(-1, 3)
    sample = flat[np.random.default_rng(seed).choice(len(flat), min(40000, len(flat)), replace=False)]
    centroids, _ = kmeans2(sample, k, minit="++", seed=seed)
    quantized = ((flat[:, None, :] - centroids[None, :, :]) ** 2).sum(-1).argmin(1).reshape(img.shape[:2])

    labels = np.zeros(img.shape[:2], np.int32)
    nxt = 1
    for cluster in range(k):
        comp, n = ndi.label(quantized == cluster)
        mask = comp > 0
        labels[mask] = comp[mask] + nxt
        nxt += n + 1

    # Normalization: absorb sub-threshold fragments into the nearest surviving region
    # so that the result is a true partition with no unassigned cells.
    sizes = np.bincount(labels.ravel())
    labels[np.isin(labels, np.where(sizes < min_size)[0])] = 0
    _, (iy, ix) = ndi.distance_transform_edt(labels == 0, return_indices=True)
    return labels[iy, ix], smoothed


def boundary_pairs(labels):
    """Group boundary cells by the unordered pair of regions they separate."""
    pairs: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for axis, (dy, dx) in enumerate([(0, 1), (1, 0)]):
        diff = labels != np.roll(labels, -1, axis=1 - axis if axis == 0 else 0)
        if axis == 0:
            diff[:, -1] = False
        else:
            diff[-1, :] = False
        for y, x in zip(*np.nonzero(diff)):
            key = (min(labels[y, x], labels[y + dy, x + dx]),
                   max(labels[y, x], labels[y + dy, x + dx]))
            pairs.setdefault(key, []).append((y, x))
    return pairs


def structure_mask(rgb, shape, blur=5, downscale=4, k=6, dilate=3, min_size=120):
    """Coarse-scale partition boundaries, upsampled. Survives blur => structural.

    NOTE: min_size is a cleanup gate on the COARSE raster. Components smaller
    than it are absorbed before boundaries are traced, so it independently
    removes small features regardless of scale persistence. Exposed as a
    parameter so the two effects can be separated; the default preserves the
    behaviour used in the Track B and Track A probes.
    """
    h, w = shape
    small = np.stack(
        [ndi.zoom(ndi.gaussian_filter(rgb[..., c], blur), 1 / downscale, order=1) for c in range(3)], -1
    )
    coarse, _ = segment(small, k, min_size, median=5)
    right = coarse != np.roll(coarse, -1, axis=1)
    right[:, -1] = False
    down = coarse != np.roll(coarse, -1, axis=0)
    down[-1, :] = False
    big = np.asarray(
        Image.fromarray(((right | down) * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)
    ) > 127
    return ndi.binary_dilation(big, iterations=dilate)


def propose_roles(rgb, labels, pairs, smoothed, use_persistence):
    """Propose which boundaries are visible lines.

    Baseline features (gradient, colour contrast, length) cannot separate a
    facade window band from a building silhouette: both score high on all three.
    The persistence gate adds the missing axis.
    """
    grey = rgb @ np.array([0.299, 0.587, 0.114])
    gmag = np.hypot(ndi.sobel(grey, axis=1), ndi.sobel(grey, axis=0))
    mean_colour = {l: smoothed[labels == l].mean(0) for l in np.unique(labels)}
    persist_mask = structure_mask(rgb, labels.shape) if use_persistence else None

    visible = set()
    for key, cells in pairs.items():
        a, b = key
        gradient = np.mean([gmag[y, x] for y, x in cells])
        contrast = float(np.linalg.norm(mean_colour[a] - mean_colour[b]))
        length = len(cells)
        ok = gradient > 0.22 and contrast > 0.10 and length > 45
        if ok and persist_mask is not None:
            ok = np.mean([persist_mask[y, x] for y, x in cells]) > 0.55
        if ok:
            visible.add(key)
    return visible


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--width", type=int, default=1100)
    ap.add_argument("--colours", type=int, default=14)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    im = Image.open(args.image).convert("RGB")
    height = int(im.height * args.width / im.width)
    rgb = np.asarray(im.resize((args.width, height), Image.LANCZOS), dtype=np.float64) / 255.0

    labels, smoothed = segment(rgb, args.colours, 180)
    pairs = boundary_pairs(labels)
    baseline = propose_roles(rgb, labels, pairs, smoothed, use_persistence=False)
    persistent = propose_roles(rgb, labels, pairs, smoothed, use_persistence=True)

    print(f"regions                     {len(np.unique(labels))}")
    print(f"adjacent region pairs       {len(pairs)}")
    print(f"visible pairs (baseline)    {len(baseline)}")
    print(f"visible pairs (persistence) {len(persistent)}")

    def render(keys, name):
        mask = np.zeros(labels.shape, bool)
        for key in keys:
            for y, x in pairs[key]:
                mask[y, x] = True
        mask = ndi.binary_dilation(mask, iterations=1)
        Image.fromarray(((1 - mask) * 255).astype(np.uint8)).save(os.path.join(args.out, name))
        return int(mask.sum())

    print(f"line cells (baseline)       {render(baseline, 'lines_baseline.png')}")
    print(f"line cells (persistence)    {render(persistent, 'lines_persistence.png')}")

    fill = np.zeros_like(rgb)
    mean_colour = {l: smoothed[labels == l].mean(0) for l in np.unique(labels)}
    for l, c in mean_colour.items():
        fill[labels == l] = c
    Image.fromarray((np.clip(fill, 0, 1) * 255).astype(np.uint8)).save(
        os.path.join(args.out, "regions_flat.png")
    )


if __name__ == "__main__":
    main()
