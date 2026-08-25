"""Track A fixture: hand-authored ground-truth region partition.

RESEARCH_PROTOTYPE / NOT_PRODUCTION_OUTPUT

Regions are authored as polygons and rasterized in painter's order, so
"every cell has exactly one region id" is guaranteed by construction rather
than by post-hoc cleanup. Boundary roles are assigned by hand.

The fixture is stored as polygon coordinates only (track_a_fixture.json).
No image pixels are committed. The source photograph must be supplied
separately and cropped to the fixture's declared size.
"""
from __future__ import annotations

import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "track_a_fixture.json")


def load_fixture(path: str = FIXTURE):
    with open(path, encoding="utf-8") as fh:
        meta = json.load(fh)
    roles = {tuple(k.split("|")): v for k, v in meta["roles"].items()}
    return meta, roles


def rasterize(meta):
    """Painter's order rasterization -> a partition with no unassigned cells."""
    w, h = meta["size"]
    ids = {layer["name"]: layer["id"] for layer in meta["layers"]}
    img = Image.new("I", (w, h), meta["layers"][0]["id"])
    draw = ImageDraw.Draw(img)
    for layer in meta["layers"]:
        draw.polygon([tuple(p) for p in layer["polygon"]], fill=ids[layer["name"]])
    labels = np.array(img, dtype=np.int32)
    if not (labels > 0).all():
        raise ValueError("unassigned cells in fixture raster")
    return labels


def adjacent_pairs(labels, names):
    pairs = set()
    for arr, dy, dx in (
        (labels != np.roll(labels, -1, 1), 0, 1),
        (labels != np.roll(labels, -1, 0), 1, 0),
    ):
        arr = arr.copy()
        if dx:
            arr[:, -1] = False
        else:
            arr[-1, :] = False
        for y, x in zip(*np.nonzero(arr)):
            pairs.add((names[labels[y, x]], names[labels[y + dy, x + dx]]))
    return pairs


def role_masks(labels, meta, roles):
    """Split ground-truth boundaries into visible-line and fill-only masks.

    Safe-stops if any genuinely adjacent pair has no hand-assigned role.
    """
    names = {layer["id"]: layer["name"] for layer in meta["layers"]}
    missing = [
        p for p in adjacent_pairs(labels, names)
        if p not in roles and (p[1], p[0]) not in roles
    ]
    if missing:
        raise ValueError(f"SAFE-STOP: unlabelled adjacent pairs {sorted(set(missing))}")

    line = np.zeros(labels.shape, bool)
    fill = np.zeros(labels.shape, bool)
    for arr, dy, dx in (
        (labels != np.roll(labels, -1, 1), 0, 1),
        (labels != np.roll(labels, -1, 0), 1, 0),
    ):
        arr = arr.copy()
        if dx:
            arr[:, -1] = False
        else:
            arr[-1, :] = False
        for y, x in zip(*np.nonzero(arr)):
            a, b = names[labels[y, x]], names[labels[y + dy, x + dx]]
            role = roles.get((a, b)) or roles.get((b, a))
            (line if role == "REGION_BOUNDARY" else fill)[y, x] = True
    return line, fill


if __name__ == "__main__":
    meta, roles = load_fixture()
    labels = rasterize(meta)
    line, fill = role_masks(labels, meta, roles)
    print(f"regions          {len(np.unique(labels))}")
    print(f"roles assigned   {len(roles)}")
    print(f"line cells       {int(line.sum())}")
    print(f"fill-only cells  {int(fill.sum())}")
