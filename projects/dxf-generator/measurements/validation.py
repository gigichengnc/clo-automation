"""Validation for user-supplied body measurements.

This first version intentionally keeps the rules minimal. It only verifies that
all required body measurements are greater than zero. Garment-specific fit
rules, body-range assumptions, ease, and drafting constraints belong in later
layers.
"""

from measurements.body import BodyMeasurements


_REQUIRED_FIELDS = (
    "waist",
    "hip",
    "waist_to_hip",
)


def validate_body_measurements(measurements: BodyMeasurements) -> list[str]:
    """Return validation errors; an empty list means the input is valid."""

    errors = []
    for field_name in _REQUIRED_FIELDS:
        value = getattr(measurements, field_name)
        if value <= 0:
            errors.append(f"{field_name} must be greater than 0 mm")
    return errors
