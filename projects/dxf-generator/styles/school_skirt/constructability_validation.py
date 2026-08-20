"""Constructability validation for school-skirt dart lengths.

This layer checks only cross-layer relationships needed before dart placement
or coordinate geometry. It assumes the draft and drafting parameters have
already passed their own validators.

It does not choose dart intake, distribute suppression, place darts, clamp
values, or generate DXF geometry.

All values use millimetres (mm).
"""

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


def validate_school_skirt_constructability(
    draft: SchoolSkirtDraft,
    parameters: SchoolSkirtDraftingParameters,
) -> list[str]:
    """Return constructability errors; empty means dart lengths can continue."""

    errors = []

    for panel_name, dart_count, dart_length in (
        ("front", parameters.front_dart_count, parameters.front_dart_length),
        ("back", parameters.back_dart_count, parameters.back_dart_length),
    ):
        if dart_count <= 0:
            continue

        if dart_length > draft.hip_position:
            errors.append(
                f"{panel_name}_dart_length must be less than or equal to "
                f"hip_position ({draft.hip_position} mm)"
            )

    return errors
