from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dxf import render_dxf
from .fashion_flat import DressSpec, build_dress_flat
from .prompt import PromptParseError, parse_prompt
from .svg import render_svg


def _load_spec(spec_path: Path | None, prompt: str | None) -> DressSpec:
    if (spec_path is None) == (prompt is None):
        raise SystemExit("provide exactly one of a JSON spec path or --prompt")

    if prompt is not None:
        try:
            return parse_prompt(prompt).spec
        except PromptParseError as exc:
            raise SystemExit(f"prompt rejected: {exc}") from exc

    assert spec_path is not None
    raw = json.loads(spec_path.read_text(encoding="utf-8"))
    if raw.get("garment") != "dress":
        raise SystemExit("v0.1 supports garment='dress' only")
    return DressSpec(
        neckline=raw.get("neckline", "round"),
        sleeve=raw.get("sleeve", "sleeveless"),
        silhouette=raw.get("silhouette", "a_line"),
        length=raw.get("length", "midi"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic vector fashion flats")
    parser.add_argument("spec", type=Path, nargs="?", help="JSON garment specification")
    parser.add_argument("--prompt", help="strict natural-language garment description")
    parser.add_argument("--svg", type=Path, required=True, help="SVG output path")
    parser.add_argument("--dxf", type=Path, help="optional standard DXF artwork output")
    args = parser.parse_args()

    spec = _load_spec(args.spec, args.prompt)
    drawing = build_dress_flat(spec)
    args.svg.parent.mkdir(parents=True, exist_ok=True)
    args.svg.write_text(render_svg(drawing), encoding="utf-8")
    if args.dxf:
        args.dxf.parent.mkdir(parents=True, exist_ok=True)
        args.dxf.write_text(render_dxf(drawing), encoding="ascii")


if __name__ == "__main__":
    main()
