from __future__ import annotations

from .model import Cubic, Line, Move, Point, SemanticPath


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


def build_patch_pocket_pair() -> tuple[SemanticPath, SemanticPath]:
    """Build a symbolic front patch-pocket pair for technical illustration."""
    left = SemanticPath(
        path_id="detail.pocket.front.left",
        role="pocket.front.left",
        commands=(
            Move(Point(-55.0, 150.0)),
            Line(Point(-28.0, 150.0)),
            Line(Point(-28.0, 184.0)),
            Cubic(Point(-35.0, 190.0), Point(-48.0, 190.0), Point(-55.0, 184.0)),
            Line(Point(-55.0, 150.0)),
        ),
        layer="detail",
    )
    right = left.mirror_x(
        path_id="detail.pocket.front.right",
        role="pocket.front.right",
    )
    return left, right


def build_centre_button_row() -> tuple[SemanticPath, ...]:
    """Build symbolic centre-front button marks without duplicating the centre guide."""
    paths: list[SemanticPath] = []
    for index, y in enumerate((94.0, 106.0, 118.0), start=1):
        paths.append(
            SemanticPath(
                path_id=f"detail.button.front.{index}",
                role=f"button.front.{index}",
                commands=(Move(Point(-2.5, y)), Line(Point(2.5, y))),
                layer="detail",
            )
        )
    return tuple(paths)


def build_shoulder_princess_seam_pair() -> tuple[SemanticPath, SemanticPath]:
    """Build symbolic shoulder-to-waist princess seams for a front technical flat.

    Geometry is an illustration convention only and is not a production seam
    placement or shaping rule.
    """
    left = SemanticPath(
        path_id="detail.princess.front.left",
        role="princess.front.left",
        commands=(
            Move(Point(-40.0, 43.0)),
            Cubic(Point(-38.0, 68.0), Point(-33.0, 95.0), Point(-29.0, 124.0)),
        ),
        layer="detail",
    )
    right = left.mirror_x(
        path_id="detail.princess.front.right",
        role="princess.front.right",
    )
    return left, right
