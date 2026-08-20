"""Validation for resolved school-skirt dart placements.

This layer validates the output of a future explicit dart-placement policy.
It does not choose dart positions, require equal spacing, map positions to
coordinates, or generate pattern geometry.

Each ``center_fraction`` is dimensionless: 0.0 is the centre edge and 1.0 is
the side-seam edge. Boundary positions remain allowed here; any stronger
edge-clearance rule belongs to a later explicit constructability decision.
"""

import math

from styles.school_skirt.dart_placement import SchoolSkirtDartPlacement
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


_PLACEMENT_TOLERANCE = 1e-6


def _validate_center_fraction(name: str, value: object) -> list[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{name} must be numeric"]
    if not math.isfinite(value):
        return [f"{name} must be a finite number"]
    if value < 0.0 or value > 1.0:
        return [f"{name} must be between 0.0 and 1.0 inclusive"]
    return []


def validate_school_skirt_dart_placement(
    parameters: SchoolSkirtDraftingParameters,
    placement: SchoolSkirtDartPlacement,
) -> list[str]:
    """Return placement errors; an empty list means placement can continue."""

    errors = []

    for panel_name, panel_placement, expected_count in (
        ("front", placement.front, parameters.front_dart_count),
        ("back", placement.back, parameters.back_dart_count),
    ):
        if (
            isinstance(expected_count, bool)
            or not isinstance(expected_count, int)
            or expected_count < 0
        ):
            errors.append(
                f"{panel_name}_dart_count must be a non-negative integer for dart placement"
            )
            continue

        if len(panel_placement.darts) != expected_count:
            errors.append(
                f"{panel_name} dart placement must contain exactly "
                f"{expected_count} dart(s)"
            )

        valid_positions = []
        for index, dart in enumerate(panel_placement.darts):
            name = f"{panel_name}.darts[{index}].center_fraction"
            current_errors = _validate_center_fraction(name, dart.center_fraction)
            errors.extend(current_errors)
            if not current_errors:
                valid_positions.append(dart.center_fraction)

        duplicate_found = False
        for index, position in enumerate(valid_positions):
            for earlier in valid_positions[:index]:
                if math.isclose(
                    position,
                    earlier,
                    rel_tol=0.0,
                    abs_tol=_PLACEMENT_TOLERANCE,
                ):
                    duplicate_found = True
                    break
            if duplicate_found:
                break

        if duplicate_found:
            errors.append(
                f"{panel_name} dart placements must not overlap within "
                f"{_PLACEMENT_TOLERANCE} normalized fraction"
            )

    return errors
