"""Explicit sampled quadratic Bezier side-seam segment research policy.

This module provides a generic quadratic Bezier implementation for research and
candidate comparison. It deliberately does not choose a control-point rule,
sampling count, production default, or garment-specific drafting recommendation.
The caller must supply both an explicit ``control_point_rule`` and
``sample_count``.

``sample_count`` means the total number of returned path points, including the
semantic start and end anchors, and must be at least 3 so the sampled path
contains at least one interior point. The first and last returned points are the
exact supplied semantic anchor objects; only interior Bezier points are
calculated.

This policy performs no seam allowance or DXF behavior. All coordinates use
millimetres (mm).
"""

from dataclasses import dataclass
import math
from typing import Protocol

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamSegmentGeometryInput,
)


class QuadraticBezierControlPointRule(Protocol):
    """Explicit caller-supplied rule for resolving one Bezier control point."""

    def resolve(self, geometry_input: SideSeamSegmentGeometryInput) -> Point2D:
        """Return the control point for the supplied semantic segment."""
        ...


def _validate_point(name: str, point: Point2D) -> None:
    for axis_name, value in (("x", point.x), ("y", point.y)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name}.{axis_name} must be numeric")
        if not math.isfinite(value):
            raise ValueError(f"{name}.{axis_name} must be a finite number")


def _quadratic_bezier_point(
    start: Point2D,
    control: Point2D,
    end: Point2D,
    t: float,
) -> Point2D:
    one_minus_t = 1.0 - t
    return Point2D(
        x=(one_minus_t * one_minus_t * start.x)
        + (2.0 * one_minus_t * t * control.x)
        + (t * t * end.x),
        y=(one_minus_t * one_minus_t * start.y)
        + (2.0 * one_minus_t * t * control.y)
        + (t * t * end.y),
    )


@dataclass(frozen=True)
class QuadraticBezierSideSeamSegmentPolicy:
    """Sample one explicit quadratic Bezier segment for research comparison."""

    control_point_rule: QuadraticBezierControlPointRule
    sample_count: int

    def __post_init__(self) -> None:
        if isinstance(self.sample_count, bool) or not isinstance(self.sample_count, int):
            raise ValueError("sample_count must be an integer")
        if self.sample_count < 3:
            raise ValueError("sample_count must be at least 3")

    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        """Resolve the explicit control point and sample the quadratic curve."""

        control = self.control_point_rule.resolve(geometry_input)
        _validate_point("side_seam_segment.start", geometry_input.start)
        _validate_point("side_seam_segment.end", geometry_input.end)
        _validate_point("quadratic_bezier.control", control)

        denominator = self.sample_count - 1
        interior_points = tuple(
            _quadratic_bezier_point(
                geometry_input.start,
                control,
                geometry_input.end,
                index / denominator,
            )
            for index in range(1, self.sample_count - 1)
        )

        return Path2D(
            points=(
                geometry_input.start,
                *interior_points,
                geometry_input.end,
            )
        )
