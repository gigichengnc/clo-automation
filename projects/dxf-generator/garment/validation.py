"""Validation for user-supplied garment requests.

This module validates requested garment dimensions only. It contains no fit,
drafting, geometry, or DXF logic.
"""

from math import isfinite

from garment.request import GarmentRequest


def validate_garment_request(request: GarmentRequest) -> list[str]:
    """Return validation errors; an empty list means the request is valid."""

    errors = []
    value = request.requested_length
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append("requested_length must be numeric")
    elif not isfinite(value):
        errors.append("requested_length must be a finite number")
    elif value <= 0:
        errors.append("requested_length must be greater than 0 mm")
    return errors
