"""Forensic compatibility layer for the lost legacy ``blocks.py`` helper.

This module reconstructs only behavior needed to replay surviving legacy callers
and generated DXFs. It is NOT an authoritative production DXF parser and must
not be used by the new parametric drafting engine.

Compatibility behavior reconstructed here:
- ``parse(path)`` reads ANSI/AAMA BLOCKS and exposes ``polys`` / ``texts``.
- this reconstruction uses *first duplicate BLOCK occurrence wins*. That choice
  reproduces observed Claude-era direct-copy outputs, but the original lost
  implementation is not available and the surviving copied pieces do not
  uniquely rule out every alternative duplicate-selection heuristic.
- ``upright(block)`` takes layer-14 as net geometry and layer-1 as cut geometry,
  centers both using the layer-14 point centroid, and rotates the layer-7
  grainline direction onto +Y.

The third return value of the lost function is not consumed by any surviving
caller. This reconstruction returns the transformed grainline when present.
That choice is useful but is NOT claimed as verified byte-for-byte behavior of
the lost source.
"""

from __future__ import annotations

from pathlib import Path
import math

import numpy as np


def _read_groups(path: str | Path) -> list[tuple[int, str]]:
    data = Path(path).read_bytes()
    try:
        text = data.decode("gb18030")
    except UnicodeDecodeError as exc:
        raise ValueError("legacy DXF must be decodable as GB18030/ASCII") from exc

    lines = text.splitlines()
    groups: list[tuple[int, str]] = []
    index = 0
    while index + 1 < len(lines):
        raw_code = lines[index].strip()
        value = lines[index + 1]
        index += 2
        if not raw_code:
            continue
        try:
            code = int(raw_code)
        except ValueError as exc:
            raise ValueError(f"invalid DXF group code: {raw_code!r}") from exc
        groups.append((code, value))
    return groups


def _read_xy(
    groups: list[tuple[int, str]],
    start: int,
) -> tuple[np.ndarray | None, int]:
    x = None
    y = None
    index = start
    while index < len(groups) and groups[index][0] != 0:
        code, value = groups[index]
        if code == 10:
            x = float(value)
        elif code == 20:
            y = float(value)
        index += 1
    if x is None or y is None:
        return None, index
    return np.array([x, y], dtype=float), index


def parse(path: str | Path) -> dict[str, dict[str, object]]:
    """Parse the first occurrence of each ANSI/AAMA BLOCK used by legacy tools."""

    groups = _read_groups(path)
    result: dict[str, dict[str, object]] = {}
    index = 0

    while index < len(groups):
        code, value = groups[index]
        if code != 0 or value != "BLOCK":
            index += 1
            continue

        index += 1
        name: str | None = None
        polys: list[dict[str, object]] = []
        texts: list[str] = []
        points: list[dict[str, object]] = []
        grainlines: list[np.ndarray] = []

        while index < len(groups):
            code, value = groups[index]
            if code == 0 and value == "ENDBLK":
                break

            if name is None and code == 2:
                name = value
                index += 1
                continue

            if code == 0 and value == "POLYLINE":
                index += 1
                layer: str | None = None
                closed = False
                poly_points: list[np.ndarray] = []

                while index < len(groups):
                    entity_code, entity_value = groups[index]
                    if entity_code == 8 and layer is None:
                        layer = entity_value
                        index += 1
                        continue
                    if entity_code == 70:
                        closed = bool(int(entity_value) & 1)
                        index += 1
                        continue
                    if entity_code == 0 and entity_value == "VERTEX":
                        point, index = _read_xy(groups, index + 1)
                        if point is not None:
                            poly_points.append(point)
                        continue
                    if entity_code == 0 and entity_value == "SEQEND":
                        index += 1
                        break
                    if entity_code == 0:
                        break
                    index += 1

                polys.append(
                    {
                        "layer": layer,
                        "pts": np.asarray(poly_points, dtype=float),
                        "closed": closed,
                    }
                )
                continue

            if code == 0 and value == "TEXT":
                index += 1
                text_value: str | None = None
                while index < len(groups) and groups[index][0] != 0:
                    text_code, text_item = groups[index]
                    if text_code == 1:
                        text_value = text_item
                    index += 1
                if text_value is not None:
                    texts.append(text_value)
                continue

            if code == 0 and value == "POINT":
                index += 1
                layer: str | None = None
                x = None
                y = None
                while index < len(groups) and groups[index][0] != 0:
                    point_code, point_value = groups[index]
                    if point_code == 8:
                        layer = point_value
                    elif point_code == 10:
                        x = float(point_value)
                    elif point_code == 20:
                        y = float(point_value)
                    index += 1
                if x is not None and y is not None:
                    points.append(
                        {"layer": layer, "pt": np.array([x, y], dtype=float)}
                    )
                continue

            if code == 0 and value == "LINE":
                index += 1
                layer: str | None = None
                x1 = y1 = x2 = y2 = None
                while index < len(groups) and groups[index][0] != 0:
                    line_code, line_value = groups[index]
                    if line_code == 8:
                        layer = line_value
                    elif line_code == 10:
                        x1 = float(line_value)
                    elif line_code == 20:
                        y1 = float(line_value)
                    elif line_code == 11:
                        x2 = float(line_value)
                    elif line_code == 21:
                        y2 = float(line_value)
                    index += 1
                if (
                    layer == "7"
                    and x1 is not None
                    and y1 is not None
                    and x2 is not None
                    and y2 is not None
                ):
                    grainlines.append(
                        np.array([[x1, y1], [x2, y2]], dtype=float)
                    )
                continue

            index += 1

        if name is not None and name not in result:
            result[name] = {
                "polys": polys,
                "texts": texts,
                "points": points,
                "grainlines": grainlines,
            }

        index += 1

    return result


def _first_poly(block: dict[str, object], layer: str) -> np.ndarray:
    polys = block.get("polys")
    if not isinstance(polys, list):
        raise ValueError("legacy block must contain a polys list")
    for poly in polys:
        if isinstance(poly, dict) and poly.get("layer") == layer:
            pts = np.asarray(poly.get("pts"), dtype=float)
            if pts.ndim != 2 or pts.shape[1:] != (2,) or len(pts) < 2:
                raise ValueError(f"legacy layer {layer} contour is invalid")
            if not np.isfinite(pts).all():
                raise ValueError(
                    f"legacy layer {layer} contour contains non-finite points"
                )
            return pts
    raise ValueError(f"legacy block is missing layer {layer} contour")


def _first_grainline(block: dict[str, object]) -> np.ndarray:
    grainlines = block.get("grainlines")
    if not isinstance(grainlines, list) or not grainlines:
        raise ValueError("legacy block is missing layer-7 grainline")
    grainline = np.asarray(grainlines[0], dtype=float)
    if grainline.shape != (2, 2) or not np.isfinite(grainline).all():
        raise ValueError("legacy layer-7 grainline is invalid")
    if np.linalg.norm(grainline[1] - grainline[0]) <= 1e-9:
        raise ValueError("legacy layer-7 grainline must have non-zero length")
    return grainline


def upright(
    block: dict[str, object],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return net/cut geometry centered and grainline-oriented to legacy +Y."""

    net = _first_poly(block, "14")
    cut = _first_poly(block, "1")
    grainline = _first_grainline(block)

    center = net.mean(axis=0)
    direction = grainline[1] - grainline[0]
    source_angle = math.atan2(direction[1], direction[0])
    rotation = math.pi / 2.0 - source_angle
    cosine = math.cos(rotation)
    sine = math.sin(rotation)
    matrix = np.array([[cosine, -sine], [sine, cosine]], dtype=float)

    def transform(points: np.ndarray) -> np.ndarray:
        return (np.asarray(points, dtype=float) - center) @ matrix.T

    return transform(net), transform(cut), transform(grainline)
