"""Validation for resolved school-skirt individual dart distributions.

This layer validates the output of a future explicit dart-distribution policy.
It does not choose how dart intake is split, place darts, choose dart lengths,
or generate pattern geometry.

All values use millimetres (mm).
"""

import math

from styles.school_skirt.dart_distribution import SchoolSkirtDartDistribution
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.suppression import SchoolSkirtSuppressionAllocation


_DART_TOTAL_TOLERANCE_MM = 1e-6


def _validate_intake(name: str, value: object) -> list[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{name} must be numeric"]
    if not math.isfinite(value):
        return [f"{name} must be a finite number"]
    if value < 0:
        return [f"{name} must be greater than or equal to 0 mm"]
    return []


def validate_school_skirt_dart_distribution(
    allocation: SchoolSkirtSuppressionAllocation,
    parameters: SchoolSkirtDraftingParameters,
    distribution: SchoolSkirtDartDistribution,
) -> list[str]:
    """Return distribution errors; an empty list means the distribution is valid."""

    errors = []

    for panel_name, panel_distribution, panel_allocation, expected_count in (
        (
            "front",
            distribution.front,
            allocation.front,
            parameters.front_dart_count,
        ),
        (
            "back",
            distribution.back,
            allocation.back,
            parameters.back_dart_count,
        ),
    ):
        if (
            isinstance(expected_count, bool)
            or not isinstance(expected_count, int)
            or expected_count < 0
        ):
            errors.append(
                f"{panel_name}_dart_count must be a non-negative integer for dart distribution"
            )
            continue

        if len(panel_distribution.dart_intakes) != expected_count:
            errors.append(
                f"{panel_name} dart distribution must contain exactly "
                f"{expected_count} intake value(s)"
            )

        total_name = f"{panel_name}.dart_intake_total"
        total_errors = _validate_intake(total_name, panel_allocation.dart_intake_total)
        errors.extend(total_errors)

        intake_errors = []
        for index, intake in enumerate(panel_distribution.dart_intakes):
            name = f"{panel_name}.dart_intakes[{index}]"
            current_errors = _validate_intake(name, intake)
            errors.extend(current_errors)
            intake_errors.extend(current_errors)

        if total_errors or intake_errors:
            continue

        distributed_total = sum(panel_distribution.dart_intakes)
        if not math.isclose(
            distributed_total,
            panel_allocation.dart_intake_total,
            rel_tol=0.0,
            abs_tol=_DART_TOTAL_TOLERANCE_MM,
        ):
            errors.append(
                f"{panel_name} dart intake sum must equal {total_name} "
                f"({panel_allocation.dart_intake_total} mm)"
            )

    return errors
