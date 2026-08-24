"""Validation for school-skirt suppression targets and allocations.

The policy-independent draft provides the canonical quarter-suppression basis.
Validation derives the corresponding half-garment requirement as twice that
value. An explicit panel-target policy must first divide the half-garment
requirement between front and back. A later allocation policy then divides each
panel target between dart intake and side shaping.

This validator chooses neither policy and provides no equal-quarter fallback.
All values use millimetres (mm).
"""

import math

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.suppression import (
    PanelSuppressionTargets,
    SchoolSkirtSuppressionAllocation,
)


_SUPPRESSION_TOLERANCE_MM = 1e-6


def _validate_component(name: str, value: object) -> list[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{name} must be numeric"]
    if not math.isfinite(value):
        return [f"{name} must be a finite number"]
    if value < 0:
        return [f"{name} must be greater than or equal to 0 mm"]
    return []


def validate_school_skirt_panel_suppression_targets(
    draft: SchoolSkirtDraft,
    targets: PanelSuppressionTargets,
) -> list[str]:
    """Validate front/back targets against whole half-garment conservation."""

    expected_quarter = draft.quarter_suppression
    if isinstance(expected_quarter, bool) or not isinstance(expected_quarter, (int, float)):
        return ["quarter_suppression must be numeric"]
    if not math.isfinite(expected_quarter):
        return ["quarter_suppression must be a finite number"]
    if expected_quarter < 0:
        return [
            "quarter_suppression must be greater than or equal to 0 mm "
            "for suppression allocation"
        ]

    errors = []
    errors.extend(_validate_component("targets.front", targets.front))
    errors.extend(_validate_component("targets.back", targets.back))
    if errors:
        return errors

    expected_half_garment_total = 2.0 * expected_quarter
    if not math.isclose(
        targets.total,
        expected_half_garment_total,
        rel_tol=0.0,
        abs_tol=_SUPPRESSION_TOLERANCE_MM,
    ):
        errors.append(
            "front + back suppression targets must equal twice quarter_suppression "
            f"({expected_half_garment_total} mm)"
        )

    return errors


def validate_school_skirt_suppression_allocation(
    targets: PanelSuppressionTargets,
    allocation: SchoolSkirtSuppressionAllocation,
) -> list[str]:
    """Validate dart/side allocations against explicit per-panel targets."""

    errors = []

    for panel_name, expected, panel in (
        ("front", targets.front, allocation.front),
        ("back", targets.back, allocation.back),
    ):
        target_errors = _validate_component(f"targets.{panel_name}", expected)
        dart_errors = _validate_component(
            f"{panel_name}.dart_intake_total", panel.dart_intake_total
        )
        side_errors = _validate_component(
            f"{panel_name}.side_shaping", panel.side_shaping
        )
        errors.extend(target_errors)
        errors.extend(dart_errors)
        errors.extend(side_errors)

        if target_errors or dart_errors or side_errors:
            continue

        if not math.isclose(
            panel.total,
            expected,
            rel_tol=0.0,
            abs_tol=_SUPPRESSION_TOLERANCE_MM,
        ):
            errors.append(
                f"{panel_name} suppression allocation must equal its explicit "
                f"panel target ({expected} mm)"
            )

    return errors
