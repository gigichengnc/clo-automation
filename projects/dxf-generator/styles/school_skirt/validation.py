"""Validation for school-skirt specification inputs.

This layer validates style-specific fit inputs used to resolve a garment
specification. Drafting, constructability, geometry, and DXF rules belong to
later layers.

All values use millimetres (mm).
"""

from math import isfinite


def _validate_ease(name: str, value) -> list[str]:
    """Return validation errors for one explicit ease value."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{name} must be numeric"]
    if not isfinite(value):
        return [f"{name} must be a finite number"]
    if value < 0:
        return [f"{name} must be greater than or equal to 0 mm"]
    return []


def validate_school_skirt_spec_inputs(
    *,
    waist_ease: float,
    hip_ease: float,
) -> list[str]:
    """Return school-skirt specification errors; empty means valid."""

    errors = []
    errors.extend(_validate_ease("waist_ease", waist_ease))
    errors.extend(_validate_ease("hip_ease", hip_ease))
    return errors
