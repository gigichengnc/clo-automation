"""Validation for school-skirt side-seam policy output.

This layer validates only the semantic contract of a resolved side-seam path.
It does not choose a curve formula, interpolation method, sampling density,
seam allowance, or DXF representation.

The path may run in either direction, but its endpoints must be the supplied
side-waist and hem-side anchors, and the supplied hip-side anchor must remain an
explicit point on the path. Keeping the hip anchor explicit preserves semantic
identity for later diagnostics and production layers.

All coordinates use millimetres (mm).
"""

import math

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_policy import SideSeamGeometryInput


_SIDE_SEAM_TOLERANCE_MM = 1e-6


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
        abs_tol=_SIDE_SEAM_TOLERANCE_MM,
    ) and math.isclose(
        first.y,
        second.y,
        rel_tol=0.0,
        abs_tol=_SIDE_SEAM_TOLERANCE_MM,
    )


def validate_school_skirt_side_seam(
    geometry_input: SideSeamGeometryInput,
    path: Path2D,
) -> list[str]:
    """Return side-seam contract errors; empty means the path may continue."""

    errors = []

    if len(path.points) < 3:
        errors.append(
            "side_seam path must contain at least 3 points so all semantic anchors remain explicit"
        )

    point_errors = []
    for index, point in enumerate(path.points):
        current_errors = _point_errors(f"side_seam.points[{index}]", point)
        errors.extend(current_errors)
        point_errors.extend(current_errors)

    if len(path.points) < 2 or point_errors:
        return errors

    start = path.points[0]
    end = path.points[-1]
    endpoints_forward = _points_close(start, geometry_input.side_waist) and _points_close(
        end, geometry_input.hem_side
    )
    endpoints_reverse = _points_close(start, geometry_input.hem_side) and _points_close(
        end, geometry_input.side_waist
    )

    if not (endpoints_forward or endpoints_reverse):
        errors.append(
            "side_seam endpoints must be side_waist and hem_side in either direction"
        )

    if not any(
        _points_close(point, geometry_input.hip_side) for point in path.points
    ):
        errors.append("side_seam path must contain hip_side as an explicit point")

    return errors
