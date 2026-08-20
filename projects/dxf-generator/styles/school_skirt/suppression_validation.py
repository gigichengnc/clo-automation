"""Validation for resolved school-skirt suppression allocations.

This layer validates the output of a future explicit suppression-allocation
policy. It does not choose a policy, distribute intake across individual darts,
clamp values, or generate pattern geometry.

All values use millimetres (mm).
"""

import math

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.suppression import SchoolSkirtSuppressionAllocation


_SUPPRESSION_TOLERANCE_MM = 1e-6


def _validate_component(name: str, value: object) -> list[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{name} must be numeric"]
    if not math.isfinite(value):
        return [f"{name} must be a finite number"]
    if value < 0:
        return [f"{name} must be greater than or equal to 0 mm"]
    return []


def validate_school_skirt_suppression_allocation(
    draft: SchoolSkirtDraft,
    allocation: SchoolSkirtSuppressionAllocation,
) -> list[str]:
    """Return allocation errors; an empty list means the allocation is valid."""

    errors = []

    expected = draft.quarter_suppression
    if isinstance(expected, bool) or not isinstance(expected, (int, float)):
        return ["quarter_suppression must be numeric"]
    if not math.isfinite(expected):
        return ["quarter_suppression must be a finite number"]
    if expected < 0:
        return ["quarter_suppression must be greater than or equal to 0 mm for suppression allocation"]

    for panel_name, panel in (
        ("front", allocation.front),
        ("back", allocation.back),
    ):
        dart_name = f"{panel_name}.dart_intake_total"
        side_name = f"{panel_name}.side_shaping"

        dart_errors = _validate_component(dart_name, panel.dart_intake_total)
        side_errors = _validate_component(side_name, panel.side_shaping)
        errors.extend(dart_errors)
        errors.extend(side_errors)

        if dart_errors or side_errors:
            continue

        total = panel.dart_intake_total + panel.side_shaping
        if not math.isclose(
            total,
            expected,
            rel_tol=0.0,
            abs_tol=_SUPPRESSION_TOLERANCE_MM,
        ):
            errors.append(
                f"{panel_name} suppression allocation must equal quarter_suppression "
                f"({expected} mm)"
            )

    return errors
