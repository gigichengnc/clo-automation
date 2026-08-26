# -*- coding: utf-8 -*-
"""Segmentation-source probe: SAM 2.1 AMG vs RGB k-means, before AND after normalization.

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT.  See SEGMENTATION_SOURCE_PROBE.md
for metric definitions and the development-fixture freeze protocol.

Input images and checkpoints are not committed. Set CROP and PROBE_DIR.

Answers only: does replacing RGB quantization with SAM 2.1 materially improve
the region partition BEFORE cleanup?

Not connected to region_partition.py, role prediction, Bezier fitting or SVG.
"""
import sys, os, json, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.environ.get('PROBE_DIR', os.path.dirname(os.path.abspath(__file__)))
RES = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RES)
from track_a_fixture import load_fixture, rasterize, role_masks   # noqa: E402
from region_role_track_b import segment                            # noqa: E402

TOL = 4
CROP = os.environ.get('CROP', os.path.join(HERE, 'trackA_crop.png'))

# ---------------- ground truth ----------------
meta, roles = load_fixture(os.path.join(RES, 'track_a_fixture.json'))
gt = rasterize(meta)
gt_line, gt_fill = role_masks(gt, meta, roles)
H, W = gt.shape
img = np.asarray(Image.open(CROP).convert('RGB').resize((W, H)), dtype=np.uint8)
rgb = img.astype(np.float64) / 255.0
print("image %dx%d   GT regions %d" % (W, H, len(np.unique(gt))))

# ---------------- SAM 2.1 AMG ----------------
t0 = time.time()
import torch
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

torch.set_num_threads(os.cpu_count() or 4)
model = build_sam2("configs/sam2.1/sam2.1_hiera_t.yaml",
                   os.path.join(HERE, 'ckpt', 'sam2.1_hiera_tiny.pt'),
                   device="cpu", apply_postprocessing=False)
IOU=float(os.environ.get('IOU',0.8)); STAB=float(os.environ.get('STAB',0.95))
TAG=os.environ.get('TAG','default')
amg = SAM2AutomaticMaskGenerator(model, points_per_side=int(os.environ.get('PPS',32)),
                                 pred_iou_thresh=IOU, stability_score_thresh=STAB,
                                 min_mask_region_area=0)
print("AMG config: pps=%s iou>=%.2f stab>=%.2f  tag=%s"%(os.environ.get('PPS',32),IOU,STAB,TAG),flush=True)
print("model loaded  %.1fs" % (time.time() - t0))

t1 = time.time()
anns = amg.generate(img)
print("AMG generate  %.1fs   -> %d raw masks" % (time.time() - t1, len(anns)),flush=True)
masks = [a['segmentation'].astype(bool) for a in anns]
np.save(os.path.join(HERE, 'sam_masks_%s.npy'%TAG), np.array(masks))
json.dump([{k: (float(v) if isinstance(v, (int, float, np.floating)) else None)
            for k, v in a.items() if k in ('area', 'predicted_iou', 'stability_score')}
           for a in anns], open(os.path.join(HERE, 'sam_meta_%s.json'%TAG), 'w'), indent=1)

# ---------------- metrics ----------------
def boundary_of(labels):
    r = labels != np.roll(labels, -1, 1); r[:, -1] = False
    d = labels != np.roll(labels, -1, 0); d[-1, :] = False
    return r | d

def mask_boundaries(ms):
    b = np.zeros((H, W), bool)
    for m in ms:
        b |= m ^ ndi.binary_erosion(m)
    return b

def boundary_recall(prop_b, tol=TOL):
    return float((gt_line & ndi.binary_dilation(prop_b, iterations=tol)).sum() / max(gt_line.sum(), 1))

def seg_stats(regions_or_masks, is_partition, name):
    """Common metric block. For raw masks, overlap/coverage are meaningful."""
    out = {'name': name}
    if is_partition:
        lab = regions_or_masks
        ids = np.unique(lab)
        ids = ids[ids != 0]
        out['count'] = int(len(ids))
        cov = (lab != 0)
        out['coverage'] = float(cov.mean())
        out['unassigned'] = float(1 - cov.mean())
        out['overlap_mean'] = 1.0
        out['overlap_ratio'] = 0.0
        areas = np.array([int((lab == i).sum()) for i in ids])
        prop_b = boundary_of(lab)
        comps = [(lab == i) for i in ids]
    else:
        ms = regions_or_masks
        out['count'] = len(ms)
        stack = np.zeros((H, W), np.int32)
        for m in ms:
            stack += m
        out['coverage'] = float((stack > 0).mean())
        out['unassigned'] = float((stack == 0).mean())
        out['overlap_mean'] = float(stack.mean())
        out['overlap_ratio'] = float((stack >= 2).mean())
        areas = np.array([int(m.sum()) for m in ms]) if ms else np.array([0])
        prop_b = mask_boundaries(ms)
        comps = ms

    out['boundary_recall'] = boundary_recall(prop_b)
    q = np.percentile(areas, [0, 25, 50, 75, 100]).astype(int).tolist() if len(areas) else [0]*5
    out['area_min_q1_med_q3_max'] = q
    out['area_frac_lt_1pct'] = float(np.mean(areas < 0.01 * H * W)) if len(areas) else 0.0

    # over-segmentation: proposals substantially inside each GT region
    frag = []
    for g in np.unique(gt):
        gm = (gt == g); ga = gm.sum()
        n = sum(1 for c in comps if c.sum() > 0 and (c & gm).sum() >= 0.5 * c.sum()
                and (c & gm).sum() >= 0.01 * ga)
        frag.append(n)
    out['fragmentation_mean'] = float(np.mean(frag))
    out['fragmentation_max'] = int(np.max(frag))

    # under-segmentation error (Achanta-style, symmetric min form)
    ue = 0.0
    for g in np.unique(gt):
        gm = (gt == g)
        for c in comps:
            inter = (c & gm).sum()
            if inter > 0:
                ue += min(inter, c.sum() - inter)
    out['under_seg_error'] = float(ue / (H * W))
    return out

# ---------------- normalization (same philosophy as existing code) ----------------
def normalize(ms, min_size=55):
    """smaller masks painted last -> one label per cell; gaps filled by nearest; small absorbed."""
    order = np.argsort([-m.sum() for m in ms])
    lab = np.zeros((H, W), np.int32)
    for rank, i in enumerate(order, start=1):
        lab[ms[i]] = rank
    if (lab == 0).any() and (lab != 0).any():
        _, (iy, ix) = ndi.distance_transform_edt(lab == 0, return_indices=True)
        lab = lab[iy, ix]
    out = np.zeros((H, W), np.int32); nxt = 1
    for i in np.unique(lab):
        cc, n = ndi.label(lab == i)
        m = cc > 0; out[m] = cc[m] + nxt; nxt += n + 1
    sizes = np.bincount(out.ravel())
    out[np.isin(out, np.where(sizes < min_size)[0])] = 0
    if (out == 0).any():
        _, (iy, ix) = ndi.distance_transform_edt(out == 0, return_indices=True)
        out = out[iy, ix]
    return out

sam_norm = normalize(masks)
kmeans, _ = segment(rgb, 14, 55)

rows = [
    seg_stats(masks,    False, 'RAW SAM 2.1 masks'),
    seg_stats(sam_norm, True,  'NORMALIZED SAM partition'),
    seg_stats(kmeans,   True,  'RGB k-means partition'),
    seg_stats(gt,       True,  'Track A ground truth'),
]
json.dump(rows, open(os.path.join(HERE, 'sam_metrics_%s.json'%TAG), 'w'), indent=1)

K = [('count','regions/masks'),('coverage','coverage'),('unassigned','unassigned'),
     ('overlap_mean','overlap mean'),('overlap_ratio','overlap >=2'),
     ('boundary_recall','GT bnd recall'),('fragmentation_mean','frag mean'),
     ('fragmentation_max','frag max'),('under_seg_error','under-seg err')]
print("\n%-22s" % "metric", *["%-24s" % r['name'] for r in rows], sep="")
for k, lbl in K:
    print("%-22s" % lbl, *["%-24s" % (("%.3f" % r[k]) if isinstance(r[k], float) else str(r[k])) for r in rows], sep="")
print("%-22s" % "area min/q1/med/q3/max", *["%-24s" % str(r['area_min_q1_med_q3_max']) for r in rows], sep="")
print("%-22s" % "frac area <1% img", *["%-24s" % ("%.3f" % r['area_frac_lt_1pct']) for r in rows], sep="")
np.save(os.path.join(HERE, 'sam_norm_%s.npy'%TAG), sam_norm)
print("\nsaved sam_masks.npy / sam_norm.npy / sam_metrics.json")

print('PROBE_DONE',flush=True)
