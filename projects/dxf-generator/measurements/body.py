"""Body measurement data for parametric garment drafting.

All measurements are stored in millimetres (mm) to match the DXF generator.
Validation rules intentionally live elsewhere so this model stays a simple
container for user-supplied body measurements.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BodyMeasurements:
    """Minimal body measurements used by the first auto-sizing prototype."""

    waist: float
    hip: float
    waist_to_hip: float
    garment_length: float
