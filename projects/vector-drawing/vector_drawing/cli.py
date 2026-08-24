from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dxf import render_dxf
from .fashion_flat import DressSpec, build_dress_flat
from .svg import render_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic vector fashion flats")
    parser.add_argument("spec", type=Path, help="JSON garment specification")
    parser.add_argument("--svg", type=Path, required=True, help="SVG output path")
    parser.add_argument("--dxf", type=Path, help="optional standard DXF artwork output")
    args = parser.parse_args()

    raw = json.loads(args.spec.read_text(encoding="utf-8"))
    if raw.get("garment") != "dress":
        raise SystemExit("v0.1 supports garment='dress' only")
    spec = DressSpec(
        neckline=raw.get("neckline", "round"),
        sleeve=raw.get("sleeve", "sleeveless"),
        silhouette=raw.get("silhouette", "a_line"),
        length=raw.get("length", "midi"),
    )
    drawing = build_dress_flat(spec)
    args.svg.parent.mkdir(parents=True, exist_ok=True)
    args.svg.write_text(render_svg(drawing), encoding="utf-8")
    if args.dxf:
        args.dxf.parent.mkdir(parents=True, exist_ok=True)
        args.dxf.write_text(render_dxf(drawing), encoding="ascii")


if __name__ == "__main__":
    main()
