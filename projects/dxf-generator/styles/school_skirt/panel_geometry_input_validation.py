"""Consistency validation for school-skirt panel geometry inputs.

This layer validates semantic conservation after the draft, suppression,
dart-distribution, placement, and dart-plan layers have already been validated.
It deliberately creates no coordinates and does not choose any drafting policy.

For each panel:
- pre-dart waist minus target waist must equal total resolved dart intake;
- hip span minus pre-dart waist must equal resolved side shaping.

All dimensional values use millimetres (mm).
"""

import math

from styles.school_skirt.panel_geometry_input import SchoolSkirtPanelGeometryInput


_GEOMETRY_INPUT_TOLERANCE_MM = 1e-6


def validate_school_skirt_panel_geometry_input(
    geometry_input: SchoolSkirtPanelGeometryInput,
) -> list[str]:
    """Return semantic consistency errors; empty means geometry may continue."""

    errors = []

    for panel_name, panel in (
        ("front", geometry_input.front),
        ("back", geometry_input.back),
    ):
        resolved_dart_total = math.fsum(dart.intake for dart in panel.darts)
        represented_dart_total = panel.waist_span_before_darts - panel.target_waist_span

        if not math.isclose(
            represented_dart_total,
            resolved_dart_total,
            rel_tol=0.0,
            abs_tol=_GEOMETRY_INPUT_TOLERANCE_MM,
        ):
            errors.append(
                f"{panel_name} pre-dart waist expansion must equal resolved dart intake total "
                f"({resolved_dart_total} mm)"
            )

        represented_side_shaping = panel.hip_span - panel.waist_span_before_darts
        if not math.isclose(
            represented_side_shaping,
            panel.side_shaping,
            rel_tol=0.0,
            abs_tol=_GEOMETRY_INPUT_TOLERANCE_MM,
        ):
            errors.append(
                f"{panel_name} hip-to-pre-dart-waist difference must equal side_shaping "
                f"({panel.side_shaping} mm)"
            )

    return errors
