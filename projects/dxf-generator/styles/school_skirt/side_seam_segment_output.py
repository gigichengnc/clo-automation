"""Validation and joining for piecewise school-skirt side-seam segment output.

This module validates the generic output contract of explicit side-seam segment
policies and joins already-built waist-to-hip and hip-to-hem paths into one
semantic side seam. It does not choose a curve formula, sampling density, seam
allowance, or DXF representation.

A segment policy may return its path in either direction. The joiner normalizes
point order to each segment's semantic ``start -> end`` direction, verifies the
shared hip boundary, and removes only the duplicated hip point when composing
the full path. Curve coordinates are otherwise preserved unchanged.

All coordinates use millimetres (mm).
"""

import math

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)


_SEGMENT_OUTPUT_TOLERANCE_MM = 1e-6


def _point_errors(name: str, point: Point2D) -> list[str]:
    errors = []
    for axis_name, value in (("x", point.x), ("y", point.y)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{name}.{axis_name} must be numeric")
        elif not math.isfinite(value):
            errors.append(f"{name}.{axis_name} must be a finite number")
    return errors


def _points_close(first: Point2D, second: Point2D) -> bool:
    return math.isclose(
        first.x,
        second.x,
        rel_tol=0.0,
        abs_tol=_SEGMENT_OUTPUT_TOLERANCE_MM,
    ) and math.isclose(
        first.y,
        second.y,
        rel_tol=0.0,
        abs_tol=_SEGMENT_OUTPUT_TOLERANCE_MM,
    )


def validate_side_seam_segment_output(
    geometry_input: SideSeamSegmentGeometryInput,
    path: Path2D,
) -> list[str]:
    """Return generic segment-output errors; empty means the path may be joined."""

    errors = []

    if len(path.points) < 2:
        errors.append("side_seam segment path must contain at least 2 points")

    point_errors = []
    for index, point in enumerate(path.points):
        current_errors = _point_errors(f"side_seam_segment.points[{index}]", point)
        errors.extend(current_errors)
        point_errors.extend(current_errors)

    if len(path.points) < 2 or point_errors:
        return errors

    start = path.points[0]
    end = path.points[-1]
    endpoints_forward = _points_close(start, geometry_input.start) and _points_close(
        end, geometry_input.end
    )
    endpoints_reverse = _points_close(start, geometry_input.end) and _points_close(
        end, geometry_input.start
    )

    if not (endpoints_forward or endpoints_reverse):
        errors.append("side_seam segment endpoints must equal its semantic start and end")

    return errors


def _oriented_points(
    geometry_input: SideSeamSegmentGeometryInput,
    path: Path2D,
) -> tuple[Point2D, ...]:
    """Return validated path points in semantic start-to-end order."""

    if _points_close(path.points[0], geometry_input.start):
        return path.points
    return tuple(reversed(path.points))


def join_side_seam_piecewise_output(
    geometry_input: SideSeamPiecewiseGeometryInput,
    waist_to_hip_path: Path2D,
    hip_to_hem_path: Path2D,
) -> Path2D:
    """Validate, orient, and join two segment paths while keeping one hip point."""

    if not _points_close(geometry_input.waist_to_hip.end, geometry_input.hip_to_hem.start):
        raise ValueError("piecewise side seam segments must share the same hip boundary")

    errors = []
    errors.extend(
        f"waist_to_hip: {error}"
        for error in validate_side_seam_segment_output(
            geometry_input.waist_to_hip,
            waist_to_hip_path,
        )
    )
    errors.extend(
        f"hip_to_hem: {error}"
        for error in validate_side_seam_segment_output(
            geometry_input.hip_to_hem,
            hip_to_hem_path,
        )
    )
    if errors:
        raise ValueError("; ".join(errors))

    upper_points = _oriented_points(geometry_input.waist_to_hip, waist_to_hip_path)
    lower_points = _oriented_points(geometry_input.hip_to_hem, hip_to_hem_path)

    if not _points_close(upper_points[-1], lower_points[0]):
        raise ValueError("resolved side seam segment paths must meet at the hip boundary")

    return Path2D(points=upper_points + lower_points[1:])
