"""Policy-independent validation for school-skirt draft values.

This layer checks only relationships that must hold before any dart-allocation
policy or coordinate geometry is applied. It does not choose dart intake,
allocate suppression, clamp values, or generate DXF geometry.

All values use millimetres (mm).
"""

from styles.school_skirt.draft import SchoolSkirtDraft


def validate_school_skirt_draft(draft: SchoolSkirtDraft) -> list[str]:
    """Return draft errors; an empty list means the draft can continue."""

    errors = []

    if draft.quarter_waist <= 0:
        errors.append("quarter_waist must be greater than 0 mm")

    if draft.quarter_hip <= 0:
        errors.append("quarter_hip must be greater than 0 mm")

    if draft.hem_position <= draft.hip_position:
        errors.append("hem_position must be greater than hip_position")

    return errors
