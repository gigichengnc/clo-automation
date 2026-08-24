from __future__ import annotations

from html import escape
from pathlib import Path

from .model import VectorScene


def _fmt(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def scene_to_svg(
    scene: VectorScene,
    *,
    stroke_width: float = 0.8,
    padding: float = 10.0,
) -> str:
    if stroke_width <= 0:
        raise ValueError("stroke_width must be positive")
    if padding < 0:
        raise ValueError("padding cannot be negative")

    min_x, min_y, max_x, max_y = scene.bounds()
    width = (max_x - min_x) + 2 * padding
    height = (max_y - min_y) + 2 * padding

    def transform(x: float, y: float) -> tuple[float, float]:
        return x - min_x + padding, max_y - y + padding

    body: list[str] = []
    for index, path in enumerate(scene.paths):
        transformed = [transform(point.x, point.y) for point in path.points]
        commands = [f"M {_fmt(transformed[0][0])} {_fmt(transformed[0][1])}"]
        commands.extend(f"L {_fmt(x)} {_fmt(y)}" for x, y in transformed[1:])
        if path.closed:
            commands.append("Z")

        attrs = {
            "data-index": str(index),
            "data-layer": path.layer,
            "data-source": path.source or "",
            "data-entity": path.entity_type or "",
        }
        data = " ".join(
            f'{key}="{escape(value, quote=True)}"' for key, value in attrs.items()
        )
        body.append(
            f'<path d="{" ".join(commands)}" fill="none" stroke="black" '
            f'stroke-width="{_fmt(stroke_width)}" vector-effect="non-scaling-stroke" {data}/>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_fmt(width)} {_fmt(height)}" '
        f'width="{_fmt(width)}mm" height="{_fmt(height)}mm">\n'
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>\n'
        '<g id="outline-pass">\n'
        + "\n".join(body)
        + "\n</g>\n</svg>\n"
    )


def write_svg(scene: VectorScene, output: str | Path, **kwargs: float) -> Path:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(scene_to_svg(scene, **kwargs), encoding="utf-8")
    return target
