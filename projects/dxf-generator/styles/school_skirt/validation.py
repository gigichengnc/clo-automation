"""Validation for school-skirt specification inputs.

This layer validates style-specific fit inputs used to resolve a garment
specification. Drafting, constructability, geometry, and DXF rules belong to
later layers.

All values use millimetres (mm).
"""

from math import isfinite


def validate_school_skirt_spec_inputs(
    *,
    waist_ease: float,
    hip_ease: float,
) -> list[str]:
    """Return school-skirt specification errors; empty means valid."""

    errors = []
    if not isfinite(waist_ease):
        errors.append("waist_ease must be a finite number")
    elif waist_ease < 0:
        errors.append("waist_ease must be greater than or equal to 0 mm")

    if not isfinite(hip_ease):
        errors.append("hip_ease must be a finite number")
    elif hip_ease < 0:
        errors.append("hip_ease must be greater than or equal to 0 mm")

    return errors
