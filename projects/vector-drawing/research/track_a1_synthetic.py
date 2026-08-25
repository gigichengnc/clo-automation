"""Track A.1 counterexample: 2x2 scale/role fixture.

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT

    small structural | large structural
    small texture    | large texture

A genuine structural cue should keep both structural outlines and reject
both texture interiors. A pure scale prior will instead fail on the two
off-diagonal cases: the small structural outline and the wide-period
texture interior.

Fully synthetic: ground truth is known by construction, no image needed.

    python track_a1_synthetic.py
"""
from __future__ import annotations

import numpy as np

from region_role_track_b import structure_mask

QUAD = 200


def build():
    size = 2 * QUAD
    img = np.ones((size, size, 3)) * 0.92
    labels = np.ones((size, size), np.int32)
    names = {1: "background"}
    roles: dict[tuple[int, int], str] = {}
    nxt = 2

    def solid(cx, cy, side, name):
        nonlocal nxt
        y0, x0 = cy - side // 2, cx - side // 2
        img[y0:y0 + side, x0:x0 + side] = 0.18
        labels[y0:y0 + side, x0:x0 + side] = nxt
        names[nxt] = name
        roles[(1, nxt)] = "REGION_BOUNDARY"
        nxt += 1

    def striped(cx, cy, side, period, name):
        nonlocal nxt
        y0, x0 = cy - side // 2, cx - side // 2
        ids = []
        for i, y in enumerate(range(y0, y0 + side, period)):
            y1 = min(y + period, y0 + side)
            img[y:y1, x0:x0 + side] = 0.22 if i % 2 == 0 else 0.80
            labels[y:y1, x0:x0 + side] = nxt
            names[nxt] = f"{name}_{i}"
            ids.append(nxt)
            nxt += 1
        for band in ids:
            roles[(1, band)] = "REGION_BOUNDARY"          # outer frame
        for a, b in zip(ids, ids[1:]):
            roles[(a, b)] = "TEXTURE"                     # interior bands

    solid(QUAD // 2, QUAD // 2, 26, "small_structural")
    solid(QUAD + QUAD // 2, QUAD // 2, 150, "large_structural")
    striped(QUAD // 2, QUAD + QUAD // 2, 90, 4, "small_texture")
    striped(QUAD + QUAD // 2, QUAD + QUAD // 2, 150, 22, "large_texture")
    return img, labels, names, roles


def group_of(a, b, role):
    if role == "TEXTURE":
        return f"{a.rsplit('_', 1)[0]} interior bands"
    for kind in ("small_structural", "large_structural", "small_texture", "large_texture"):
        if kind in a or kind in b:
            return f"{kind} outline"
    return "?"


def evaluate(**mask_kwargs):
    """Return {group: (role, cells, persistence)} for one structure_mask config."""
    img, labels, names, roles = build()
    sm = structure_mask(img, labels.shape, **mask_kwargs)
    cells = {}
    for arr, dy, dx in ((labels != np.roll(labels, -1, 1), 0, 1),
                        (labels != np.roll(labels, -1, 0), 1, 0)):
        arr = arr.copy()
        if dx:
            arr[:, -1] = False
        else:
            arr[-1, :] = False
        for y, x in zip(*np.nonzero(arr)):
            cells.setdefault(tuple(sorted((labels[y, x], labels[y + dy, x + dx]))), []).append((y, x))
    groups = {}
    for key, cs in cells.items():
        role = roles.get(key) or roles.get((key[1], key[0]))
        if role is None:
            continue
        groups.setdefault((group_of(names[key[0]], names[key[1]], role), role), []).extend(cs)
    return {g: (r, len(cs), float(np.mean([sm[y, x] for y, x in cs])))
            for (g, r), cs in groups.items()}


def main():
    img, labels, names, roles = build()
    sm = structure_mask(img, labels.shape)

    cells: dict[tuple[int, int], list] = {}
    for arr, dy, dx in ((labels != np.roll(labels, -1, 1), 0, 1),
                        (labels != np.roll(labels, -1, 0), 1, 0)):
        arr = arr.copy()
        if dx:
            arr[:, -1] = False
        else:
            arr[-1, :] = False
        for y, x in zip(*np.nonzero(arr)):
            cells.setdefault(tuple(sorted((labels[y, x], labels[y + dy, x + dx]))), []).append((y, x))

    groups: dict[tuple[str, str], list] = {}
    for key, cs in cells.items():
        role = roles.get(key) or roles.get((key[1], key[0]))
        if role is None:
            continue
        groups.setdefault((group_of(names[key[0]], names[key[1]], role), role), []).extend(cs)

    print(f"{'group':<34} {'GT role':<16} {'cells':>7} {'persist':>9}")
    for (group, role), cs in sorted(groups.items()):
        score = float(np.mean([sm[y, x] for y, x in cs]))
        flag = ""
        if role == "REGION_BOUNDARY" and score < 0.5:
            flag = "   FAIL kept-out"
        if role == "TEXTURE" and score > 0.5:
            flag = "   FAIL kept-in"
        print(f"{group:<34} {role:<16} {len(cs):>7} {score:>9.3f}{flag}")


if __name__ == "__main__":
    main()
