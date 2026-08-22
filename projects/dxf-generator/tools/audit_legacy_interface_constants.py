"""Reproduce legacy interface-constant candidates from private purchased 2.dxf.

The source DXF is intentionally not committed. Pass its path explicitly.
This tool reports geometry and numeric matches; it does not promote semantic
labels or drafting constants automatically.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from audit_purchased_skirt_profiles import (
    corner_indices,
    material,
    parse_all_blocks,
    path_length,
    split,
    upright_net,
)


def occurrences(blocks, name: str):
    return [block for block in blocks if block["name"] == name]


def lengths(block) -> list[float]:
    net = upright_net(block)
    idx = corner_indices(net)
    return [path_length(segment) for segment in split(net, idx)]


def nearest(values: list[float], target: float) -> tuple[float, float]:
    value = min(values, key=lambda item: abs(item - target))
    return value, value - target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dxf", type=Path, help="private purchased 2.dxf")
    args = parser.parse_args()

    blocks = parse_all_blocks(args.dxf)

    print("=== duplicate/material order ===")
    for name in ["2.前下裙.L", "2.后下裙.L", "2.前中.L"]:
        xs = occurrences(blocks, name)
        print(name, [(i + 1, material(block)) for i, block in enumerate(xs)])

    print("\n=== WAIST = 907 candidate lineage ===")
    front = occurrences(blocks, "2.前下裙.L")[0]  # raw first occurrence: lining
    back = occurrences(blocks, "2.后下裙.L")[0]   # raw first occurrence: lining
    front_lengths = lengths(front)
    back_lengths = lengths(back)
    print("front lining corner segments mm:", [round(v, 6) for v in front_lengths])
    print("back lining corner segments mm:", [round(v, 6) for v in back_lengths])

    # For the simple lining topology, one front semantic side is isolated while
    # the opposite side and waist are merged by the legacy corner threshold.
    # The back waist is the short upper segment. Keep this derivation explicit.
    front_side = min(front_lengths, key=lambda v: abs(v - 681.0))
    front_combined = max(front_lengths)
    front_waist = front_combined - front_side
    back_waist = min(back_lengths)
    full_lining_waist = front_waist + 2.0 * back_waist
    front_hem = sorted(front_lengths)[1]
    back_hem = sorted(back_lengths)[1]
    full_lining_hem = front_hem + 2.0 * back_hem
    print(f"derived front lining waist mm: {front_waist:.6f}")
    print(f"derived back lining waist mm:  {back_waist:.6f}")
    print(f"full lining waist mm:          {full_lining_waist:.6f}")
    print(f"legacy 907 difference mm:      {907.0 - full_lining_waist:.6f}")
    print(f"907 * 2.27 mm:                 {907.0 * 2.27:.6f}")
    print(f"actual lining hem difference:  {full_lining_hem - 907.0 * 2.27:.6f}")

    print("\n=== NECK = 455 numeric lineage ===")
    stand = occurrences(blocks, "2.领坐.L")[0]
    collar = occurrences(blocks, "2.领子.L")[0]
    stand_lengths = lengths(stand)
    collar_lengths = lengths(collar)
    print("collar-stand layer14 segments mm:", [round(v, 6) for v in stand_lengths])
    print("collar layer14 segments mm:      ", [round(v, 6) for v in collar_lengths])
    stand_455, delta_455 = nearest(stand_lengths, 455.0)
    pair = min(
        ((a, b, abs(a - b)) for a in stand_lengths for b in collar_lengths),
        key=lambda row: row[2],
    )
    print(f"nearest stand edge to 455: {stand_455:.6f} (delta {delta_455:+.6f})")
    print(f"closest stand/collar pair: {pair[0]:.6f} / {pair[1]:.6f} (diff {pair[2]:.6f})")

    print("\n=== ARMH = 526 / 520 lineage ===")
    sleeve = occurrences(blocks, "2.袖子.L")[0]
    sleeve_lengths = lengths(sleeve)
    print("sleeve layer14 segments mm:", [round(v, 6) for v in sleeve_lengths])
    cap_526, delta_526 = nearest(sleeve_lengths, 526.0)
    print(f"nearest sleeve edge to 526: {cap_526:.6f} (delta {delta_526:+.6f})")

    front_center = lengths(occurrences(blocks, "2.前中.L")[0])
    front_side = lengths(occurrences(blocks, "2.左前侧.L")[0])
    back_side = lengths(occurrences(blocks, "2.后侧.L")[0])
    fc_arm, _ = nearest(front_center, 101.3)
    fs_arm, _ = nearest(front_side, 129.3)
    bs_arm, _ = nearest(back_side, 265.0)
    bodice_candidate = fc_arm + fs_arm + bs_arm
    print(f"front armhole candidate: {fc_arm:.6f} + {fs_arm:.6f} = {fc_arm + fs_arm:.6f}")
    print(f"back armhole candidate:  {bs_arm:.6f}")
    print(f"one-side bodice total:    {bodice_candidate:.6f}")
    print(f"difference from 520:      {bodice_candidate - 520.0:+.6f}")
    print(f"sleeve cap - bodice:      {cap_526 - bodice_candidate:+.6f}")


if __name__ == "__main__":
    main()
