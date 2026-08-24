from __future__ import annotations

from html import escape

from .model import Cubic, Drawing, Line, Move, SemanticPath


def _fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def path_data(path: SemanticPath) -> str:
    parts: list[str] = []
    for command in path.commands:
        if isinstance(command, Move):
            parts.append(f"M {_fmt(command.to.x)} {_fmt(command.to.y)}")
        elif isinstance(command, Line):
            parts.append(f"L {_fmt(command.to.x)} {_fmt(command.to.y)}")
        elif isinstance(command, Cubic):
            parts.append(
                "C "
                f"{_fmt(command.control1.x)} {_fmt(command.control1.y)} "
                f"{_fmt(command.control2.x)} {_fmt(command.control2.y)} "
                f"{_fmt(command.to.x)} {_fmt(command.to.y)}"
            )
    return " ".join(parts)


def render_svg(drawing: Drawing) -> str:
    min_x = -drawing.width / 2.0
    classes = {
        "outline": 'stroke="black" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"',
        "detail": 'stroke="black" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-linejoin="round"',
        "guide": 'stroke="black" stroke-width="0.8" fill="none" stroke-dasharray="5 5" opacity="0.45"',
    }
    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{_fmt(min_x)} 0 {_fmt(drawing.width)} {_fmt(drawing.height)}">',
        f'  <g id="{escape(drawing.drawing_id)}">',
    ]
    for path in drawing.paths:
        style = classes.get(path.layer, classes["outline"])
        rows.append(
            f'    <path id="{escape(path.path_id)}" data-role="{escape(path.role)}" d="{path_data(path)}" {style}/>'
        )
    rows.extend(["  </g>", "</svg>", ""])
    return "\n".join(rows)
