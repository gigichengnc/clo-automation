from __future__ import annotations

import argparse
from pathlib import Path

from .loader import load_dxf_scene
from .svg import write_svg


def _parse_layers(raw: str | None) -> set[str] | None:
    if raw is None:
        return None
    values = {item.strip() for item in raw.split(",") if item.strip()}
    return values or None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render deterministic clean SVG outlines from DXF geometry"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--layers", help="comma-separated DXF layers to include")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.25,
        help="curve flattening tolerance in DXF units",
    )
    parser.add_argument(
        "--stroke-width",
        type=float,
        default=0.8,
        help="SVG stroke width",
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=10.0,
        help="SVG viewBox padding",
    )
    args = parser.parse_args()

    scene = load_dxf_scene(
        args.input,
        layers=_parse_layers(args.layers),
        tolerance=args.tolerance,
    )
    if not scene.paths:
        raise SystemExit("No renderable paths found for the requested layers")

    write_svg(
        scene,
        args.output,
        stroke_width=args.stroke_width,
        padding=args.padding,
    )
    print(f"rendered {len(scene.paths)} paths -> {args.output}")


if __name__ == "__main__":
    main()
