"""Validation for user-supplied garment requests.

This module validates requested garment dimensions only. It contains no fit,
drafting, geometry, or DXF logic.
"""

from math import isfinite

from garment.request import GarmentRequest


def validate_garment_request(request: GarmentRequest) -> list[str]:
    """Return validation errors; an empty list means the request is valid."""

    errors = []
    if not isfinite(request.requested_length):
        errors.append("requested_length must be a finite number")
    elif request.requested_length <= 0:
        errors.append("requested_length must be greater than 0 mm")
    return errors
