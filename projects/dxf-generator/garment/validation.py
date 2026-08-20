"""Validation for user-supplied garment requests.

This module validates requested garment dimensions only. It contains no fit,
drafting, geometry, or DXF logic.
"""

from .request import GarmentRequest


def validate_garment_request(request: GarmentRequest) -> list[str]:
    """Return validation errors; an empty list means the request is valid."""

    errors = []
    if request.requested_length <= 0:
        errors.append("requested_length must be greater than 0 mm")
    return errors
