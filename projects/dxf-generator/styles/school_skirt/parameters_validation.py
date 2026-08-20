"""Validation for school-skirt drafting parameters.

This layer checks parameter types and non-degenerate numeric values only. It
does not choose dart intake, allocate suppression, constrain flare direction,
or generate pattern geometry.

All dimensional values use millimetres (mm).
"""

import math

from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


_COUNT_FIELDS = (
    "front_dart_count",
    "back_dart_count",
)

_LENGTH_FIELDS = (
    "front_dart_length",
    "back_dart_length",
)


def _validate_finite_numeric(name: str, value: object) -> list[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{name} must be numeric"]
    if not math.isfinite(value):
        return [f"{name} must be a finite number"]
    return []


def validate_school_skirt_parameters(
    parameters: SchoolSkirtDraftingParameters,
) -> list[str]:
    """Return parameter errors; an empty list means the parameters are valid."""

    errors = []

    for field_name in _COUNT_FIELDS:
        value = getattr(parameters, field_name)
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{field_name} must be an integer")
        elif value < 0:
            errors.append(f"{field_name} must be greater than or equal to 0")

    for field_name in ("flare", *_LENGTH_FIELDS, "waistband_height"):
        value = getattr(parameters, field_name)
        field_errors = _validate_finite_numeric(field_name, value)
        if field_errors:
            errors.extend(field_errors)
            continue

        if field_name == "waistband_height" and value <= 0:
            errors.append("waistband_height must be greater than 0 mm")

    for count_field, length_field in (
        ("front_dart_count", "front_dart_length"),
        ("back_dart_count", "back_dart_length"),
    ):
        count = getattr(parameters, count_field)
        length = getattr(parameters, length_field)
        if (
            isinstance(count, int)
            and not isinstance(count, bool)
            and count > 0
            and isinstance(length, (int, float))
            and not isinstance(length, bool)
            and math.isfinite(length)
            and length <= 0
        ):
            errors.append(f"{length_field} must be greater than 0 mm when {count_field} is greater than 0")

    return errors
