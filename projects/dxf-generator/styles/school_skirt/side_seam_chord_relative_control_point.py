"""Chord-relative quadratic Bezier control-point research rule.

This module provides a reproducible caller-parameterized way to place one
quadratic Bezier control point relative to a semantic side-seam segment chord.
It is a research helper only: it defines no preferred skirt curve, no default
parameters, no production policy, and no DXF behavior.

``along_fraction`` places the base point along the directed chord from start to
end. It is intentionally not restricted to the interval [0, 1], so research
candidates may explicitly explore extrapolated control points.

``normal_offset`` is a signed distance in millimetres along the chord's
left-hand unit normal. Positive values move left of the directed start-to-end
chord; negative values move right.
"""

from dataclasses import dataclass
import math

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamSegmentGeometryInput,
)


def _validate_parameter(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")


def _validate_point(name: str, point: Point2D) -> None:
    for axis_name, value in (("x", point.x), ("y", point.y)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name}.{axis_name} must be numeric")
        if not math.isfinite(value):
            raise ValueError(f"{name}.{axis_name} must be a finite number")


@dataclass(frozen=True)
class ChordRelativeBezierControlPointRule:
    """Resolve a control point from explicit chord-relative parameters."""

    along_fraction: float
    normal_offset: float

    def __post_init__(self) -> None:
        _validate_parameter("along_fraction", self.along_fraction)
        _validate_parameter("normal_offset", self.normal_offset)

    def resolve(self, geometry_input: SideSeamSegmentGeometryInput) -> Point2D:
        """Return the explicit chord-relative control point for one segment."""

        _validate_point("side_seam_segment.start", geometry_input.start)
        _validate_point("side_seam_segment.end", geometry_input.end)

        dx = geometry_input.end.x - geometry_input.start.x
        dy = geometry_input.end.y - geometry_input.start.y
        chord_length = math.hypot(dx, dy)
        if chord_length == 0.0:
            raise ValueError("side-seam segment chord must have non-zero length")

        base_x = geometry_input.start.x + (self.along_fraction * dx)
        base_y = geometry_input.start.y + (self.along_fraction * dy)

        left_normal_x = -dy / chord_length
        left_normal_y = dx / chord_length

        return Point2D(
            x=base_x + (self.normal_offset * left_normal_x),
            y=base_y + (self.normal_offset * left_normal_y),
        )
