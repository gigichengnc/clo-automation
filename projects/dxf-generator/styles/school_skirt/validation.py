"""Validation for school-skirt specification inputs.

This layer validates style-specific fit inputs used to resolve a garment
specification. Drafting, constructability, geometry, and DXF rules belong to
later layers.

All values use millimetres (mm).
"""


def validate_school_skirt_spec_inputs(
    *,
    waist_ease: float,
    hip_ease: float,
) -> list[str]:
    """Return school-skirt specification errors; empty means valid."""

    errors = []
    if waist_ease < 0:
        errors.append("waist_ease must be greater than or equal to 0 mm")
    if hip_ease < 0:
        errors.append("hip_ease must be greater than or equal to 0 mm")
    return errors
