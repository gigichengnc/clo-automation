"""User garment requests that are not body measurements.

This module keeps requested garment dimensions separate from measurements taken
from the body. It contains no fit, drafting, geometry, or DXF logic.

All values use millimetres (mm).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GarmentRequest:
    """Minimal garment request for the first school-skirt sizing prototype."""

    requested_length: float
