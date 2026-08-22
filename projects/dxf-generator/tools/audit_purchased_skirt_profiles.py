"""Reproducible forensic measurements for private purchased 1.dxf / 2.dxf.

The source DXFs are intentionally not committed. Pass paths explicitly.
This script reports mechanical source facts and legacy geometric-corner segments;
it does not assign production sewing semantics automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


def _decode(value: str) -> str:
    try:
        return value.encode("latin1").decode("gbk")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def _groups(path: Path) -> list[tuple[int, str]]:
    lines = path.read_bytes().decode("latin1").splitlines()
    out: list[tuple[int, str]] = []
    for index in range(0, len(lines) - 1, 2):
        try:
            code = int(lines[index].strip())
        except ValueError:
            continue
        out.append((code, lines[index + 1]))
    return out


def _xy(groups: list[tuple[int, str]], start: int) -> tuple[np.ndarray | None, int]:
    x = y = None
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


def parse_all_blocks(path: Path) -> list[dict[str, object]]:
    groups = _groups(path)
    blocks: list[dict[str, object]] = []
    index = 0
    while index < len(groups):
        if groups[index] != (0, "BLOCK"):
            index += 1
            continue
        index += 1
        name = None
        polys: list[dict[str, object]] = []
        texts: list[str] = []
        grainlines: list[np.ndarray] = []
        while index < len(groups) and groups[index] != (0, "ENDBLK"):
            code, value = groups[index]
            if name is None and code == 2:
                name = _decode(value)
                index += 1
                continue
            if (code, value) == (0, "TEXT"):
                index += 1
                text = None
                while index < len(groups) and groups[index][0] != 0:
                    c, v = groups[index]
                    if c == 1:
                        text = _decode(v)
                    index += 1
                if text is not None:
                    texts.append(text)
                continue
            if (code, value) == (0, "LINE"):
                index += 1
                layer = None
                x1 = y1 = x2 = y2 = None
                while index < len(groups) and groups[index][0] != 0:
                    c, v = groups[index]
                    if c == 8:
                        layer = v
                    elif c == 10:
                        x1 = float(v)
                    elif c == 20:
                        y1 = float(v)
                    elif c == 11:
                        x2 = float(v)
                    elif c == 21:
                        y2 = float(v)
                    index += 1
                if layer == "7" and None not in (x1, y1, x2, y2):
                    grainlines.append(np.array([[x1, y1], [x2, y2]], dtype=float))
                continue
            if (code, value) == (0, "POLYLINE"):
                index += 1
                layer = None
                pts: list[np.ndarray] = []
                while index < len(groups):
                    c, v = groups[index]
                    if c == 8 and layer is None:
                        layer = v
                        index += 1
                        continue
                    if (c, v) == (0, "VERTEX"):
                        point, index = _xy(groups, index + 1)
                        if point is not None:
                            pts.append(point)
                        continue
                    if (c, v) == (0, "SEQEND"):
                        index += 1
                        break
                    if c == 0:
                        break
                    index += 1
                polys.append({"layer": layer, "pts": np.asarray(pts, dtype=float)})
                continue
            index += 1
        if name is not None:
            blocks.append({"name": name, "texts": texts, "polys": polys, "grainlines": grainlines})
        index += 1
    return blocks


def material(block: dict[str, object]) -> str | None:
    for text in block["texts"]:
        if isinstance(text, str) and text.startswith("Material:"):
            return text.split(":", 1)[1].strip()
    return None


def first_poly(block: dict[str, object], layer: str) -> np.ndarray:
    for poly in block["polys"]:
        if poly["layer"] == layer:
            return np.asarray(poly["pts"], dtype=float)
    raise ValueError(f"{block['name']} missing layer {layer}")


def upright_net(block: dict[str, object]) -> np.ndarray:
    net = first_poly(block, "14")
    grains = block["grainlines"]
    if not grains:
        raise ValueError(f"{block['name']} missing grainline")
    grain = np.asarray(grains[0], dtype=float)
    direction = grain[1] - grain[0]
    angle = math.pi / 2.0 - math.atan2(direction[1], direction[0])
    c = math.cos(angle)
    s = math.sin(angle)
    rotation = np.array([[c, -s], [s, c]], dtype=float)
    return (net - net.mean(axis=0)) @ rotation.T


def corner_indices(points: np.ndarray, threshold: float = 0.35, minsep: int = 15) -> list[int]:
    candidates: list[int] = []
    for i in range(len(points)):
        v1 = points[i] - points[i - 1]
        v2 = points[(i + 1) % len(points)] - points[i]
        if np.linalg.norm(v1) < 1e-6 or np.linalg.norm(v2) < 1e-6:
            continue
        a1 = math.atan2(v1[1], v1[0])
        a2 = math.atan2(v2[1], v2[0])
        delta = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        if abs(delta) > threshold:
            candidates.append(i)
    out: list[int] = []
    for i in candidates:
        if not out or i - out[-1] > minsep:
            out.append(i)
    return out


def split(points: np.ndarray, indices: list[int]) -> list[np.ndarray]:
    segments: list[np.ndarray] = []
    for k in range(len(indices)):
        a = indices[k]
        b = indices[(k + 1) % len(indices)]
        segment = points[a : b + 1] if b > a else np.vstack([points[a:], points[: b + 1]])
        segments.append(segment)
    return segments


def path_length(points: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum())


def source_entity_summary(path: Path) -> tuple[int, int]:
    groups = _groups(path)
    lwpoly = sum(1 for item in groups if item == (0, "LWPOLYLINE"))
    bulge = sum(1 for code, value in groups if code == 42 and abs(float(value)) > 1e-12)
    return lwpoly, bulge


def audit(path: Path) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    blocks = parse_all_blocks(path)
    by_name: dict[str, list[dict[str, object]]] = defaultdict(list)
    for block in blocks:
        by_name[str(block["name"])].append(block)

    lwpoly, bulge = source_entity_summary(path)
    print(f"\n=== {path.name} ===")
    print(f"sha256(local-only): {digest}")
    print(f"BLOCK definitions: {len(blocks)}; unique names: {len(by_name)}")
    print(f"LWPOLYLINE entities: {lwpoly}; non-zero VERTEX bulges: {bulge}")

    for name, occurrences in by_name.items():
        if "下裙" not in name:
            continue
        print(f"\n{name}")
        for occurrence, block in enumerate(occurrences, start=1):
            net = upright_net(block)
            indices = corner_indices(net)
            lengths = [path_length(segment) for segment in split(net, indices)] if indices else []
            l1 = first_poly(block, "1")
            print(
                f"  occurrence={occurrence} material={material(block)!r} "
                f"layer14_points={len(net)} layer1_points={len(l1)} "
                f"corner_indices={indices}"
            )
            print("    corner_segment_lengths_mm=", [round(value, 6) for value in lengths])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dxf", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.dxf:
        audit(path)


if __name__ == "__main__":
    main()
