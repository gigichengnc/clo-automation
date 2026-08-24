from __future__ import annotations

from .model import Drawing, Point, SemanticPath, sample_path


def _pair(code: int, value: str | int | float) -> list[str]:
    return [str(code), str(value)]


def _safe_layer(layer: str) -> str:
    return {"outline": "ART_OUTLINE", "detail": "ART_DETAIL", "guide": "ART_GUIDE"}.get(layer, "ART_OUTLINE")


def _polyline(path: SemanticPath, points: list[Point]) -> list[str]:
    out: list[str] = []
    out += _pair(0, "POLYLINE")
    out += _pair(8, _safe_layer(path.layer))
    out += _pair(66, 1)
    out += _pair(70, 0)
    for point in points:
        out += _pair(0, "VERTEX")
        out += _pair(8, _safe_layer(path.layer))
        out += _pair(10, f"{point.x:.6f}")
        out += _pair(20, f"{-point.y:.6f}")
        out += _pair(30, "0.0")
    out += _pair(0, "SEQEND")
    out += _pair(8, _safe_layer(path.layer))
    return out


def render_dxf(drawing: Drawing, *, cubic_steps: int = 24) -> str:
    """Render a simple standard DXF R12 artwork export.

    This is intentionally NOT DXF-AAMA/ASTM garment-pattern output. Cubic curves
    are deterministically sampled into open polylines for CAD/editing use.
    """
    lines: list[str] = []
    lines += _pair(0, "SECTION") + _pair(2, "HEADER")
    lines += _pair(9, "$ACADVER") + _pair(1, "AC1009")
    lines += _pair(0, "ENDSEC")
    lines += _pair(0, "SECTION") + _pair(2, "ENTITIES")
    for path in drawing.paths:
        lines += _polyline(path, sample_path(path, cubic_steps=cubic_steps))
    lines += _pair(0, "ENDSEC") + _pair(0, "EOF")
    return "\n".join(lines) + "\n"
