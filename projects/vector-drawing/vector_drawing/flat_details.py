from __future__ import annotations

from .model import Line, Move, Point, SemanticPath


_SUPPORTED_VIEWS = {"front", "back"}


def _dart_path(*, view: str, side: str, waist_y: float, apex_y: float, centre_x: float, half_width: float) -> SemanticPath:
    if view not in _SUPPORTED_VIEWS:
        raise ValueError(f"unsupported dart view: {view}")
    if side not in {"left", "right"}:
        raise ValueError(f"unsupported dart side: {side}")

    sign = -1.0 if side == "left" else 1.0
    inner_x = sign * (centre_x - half_width)
    outer_x = sign * (centre_x + half_width)
    apex_x = sign * centre_x

    # Keep path direction mirrored as well as geometry: left runs outer->apex->inner,
    # right runs the exact x-reflection outer->apex->inner.
    return SemanticPath(
        path_id=f"detail.dart.{view}.{side}",
        role=f"dart.{view}.{side}",
        commands=(
            Move(Point(outer_x, waist_y)),
            Line(Point(apex_x, apex_y)),
            Line(Point(inner_x, waist_y)),
        ),
        layer="detail",
    )


def build_waist_dart_pair(*, view: str, waist_y: float = 125.0) -> tuple[SemanticPath, SemanticPath]:
    """Build a symbolic technical-flat waist-dart pair.

    These coordinates are illustration policy only. They communicate that a
    waist-dart construction feature exists; they are NOT production-pattern
    dart intake, length or placement measurements.
    """
    if view == "front":
        centre_x = 25.0
        half_width = 4.0
        apex_y = 103.0
    elif view == "back":
        centre_x = 26.0
        half_width = 5.0
        apex_y = 96.0
    else:
        raise ValueError(f"unsupported dart view: {view}")

    left = _dart_path(
        view=view,
        side="left",
        waist_y=waist_y,
        apex_y=apex_y,
        centre_x=centre_x,
        half_width=half_width,
    )
    right = left.mirror_x(
        path_id=f"detail.dart.{view}.right",
        role=f"dart.{view}.right",
    )
    return left, right
