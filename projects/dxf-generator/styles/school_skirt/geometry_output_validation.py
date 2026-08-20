"""Validation for school-skirt coordinate-geometry output.

This layer checks generic geometric integrity only. It does not choose a
side-seam curve, hem shape, dart placement policy, sampling density, seam
allowance, or DXF representation.

Panel edge connectivity is checked semantically without imposing path direction:
centre edge must meet waist and hem, waist must meet side seam, and side seam
must meet hem.

All coordinates use millimetres (mm).
"""

import math

from styles.school_skirt.geometry_output import (
    DartGeometry,
    PanelGeometry,
    Path2D,
    Point2D,
    SchoolSkirtGeometry,
)


_GEOMETRY_TOLERANCE_MM = 1e-6


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
        abs_tol=_GEOMETRY_TOLERANCE_MM,
    ) and math.isclose(
        first.y,
        second.y,
        rel_tol=0.0,
        abs_tol=_GEOMETRY_TOLERANCE_MM,
    )


def _path_errors(name: str, path: Path2D) -> list[str]:
    errors = []
    if len(path.points) < 2:
        errors.append(f"{name} must contain at least 2 points")

    for index, point in enumerate(path.points):
        errors.extend(_point_errors(f"{name}.points[{index}]", point))

    return errors


def _paths_meet(first: Path2D, second: Path2D) -> bool:
    if len(first.points) < 2 or len(second.points) < 2:
        return False

    first_endpoints = (first.points[0], first.points[-1])
    second_endpoints = (second.points[0], second.points[-1])
    return any(
        _points_close(first_point, second_point)
        for first_point in first_endpoints
        for second_point in second_endpoints
    )


def _dart_errors(name: str, dart: DartGeometry) -> list[str]:
    errors = []

    if (
        isinstance(dart.dart_index, bool)
        or not isinstance(dart.dart_index, int)
        or dart.dart_index < 0
    ):
        errors.append(f"{name}.dart_index must be a non-negative integer")

    for point_name, point in (
        ("left_waist", dart.left_waist),
        ("apex", dart.apex),
        ("right_waist", dart.right_waist),
    ):
        errors.extend(_point_errors(f"{name}.{point_name}", point))

    if not errors:
        if _points_close(dart.left_waist, dart.right_waist):
            errors.append(f"{name} waist legs must not overlap")
        if _points_close(dart.apex, dart.left_waist) or _points_close(
            dart.apex, dart.right_waist
        ):
            errors.append(f"{name} apex must be distinct from both waist legs")

    return errors


def _panel_errors(panel_name: str, panel: PanelGeometry) -> list[str]:
    errors = []

    paths = (
        ("centre_edge", panel.outline.centre_edge),
        ("waist", panel.outline.waist),
        ("side_seam", panel.outline.side_seam),
        ("hem", panel.outline.hem),
    )

    path_errors = {}
    for edge_name, path in paths:
        current_errors = _path_errors(f"{panel_name}.outline.{edge_name}", path)
        path_errors[edge_name] = current_errors
        errors.extend(current_errors)

    for first_name, second_name in (
        ("centre_edge", "waist"),
        ("waist", "side_seam"),
        ("side_seam", "hem"),
        ("hem", "centre_edge"),
    ):
        if path_errors[first_name] or path_errors[second_name]:
            continue

        first_path = getattr(panel.outline, first_name)
        second_path = getattr(panel.outline, second_name)
        if not _paths_meet(first_path, second_path):
            errors.append(
                f"{panel_name} {first_name} and {second_name} must share an endpoint"
            )

    seen_indices = set()
    for index, dart in enumerate(panel.darts):
        dart_name = f"{panel_name}.darts[{index}]"
        errors.extend(_dart_errors(dart_name, dart))

        if isinstance(dart.dart_index, int) and not isinstance(dart.dart_index, bool):
            if dart.dart_index in seen_indices:
                errors.append(
                    f"{panel_name} dart_index values must be unique within the panel"
                )
                break
            seen_indices.add(dart.dart_index)

    return errors


def validate_school_skirt_geometry(geometry: SchoolSkirtGeometry) -> list[str]:
    """Return generic geometry errors; empty means output may continue."""

    errors = []
    errors.extend(_panel_errors("front", geometry.front))
    errors.extend(_panel_errors("back", geometry.back))
    return errors
