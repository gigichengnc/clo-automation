"""School-skirt garment specification derived from body measurements.

This module separates body measurements from garment measurements. It contains
no pattern geometry and does not generate or modify DXF files.

All values use millimetres (mm).
"""

from dataclasses import dataclass

from measurements.body import BodyMeasurements


DEFAULT_WAIST_EASE_MM = 20.0
DEFAULT_HIP_EASE_MM = 0.0


@dataclass(frozen=True)
class SchoolSkirtSpec:
    """Resolved measurements for the school-skirt drafting layer."""

    body_waist: float
    body_hip: float
    garment_waist: float
    garment_hip: float
    waist_to_hip: float
    skirt_length: float
    waist_ease: float
    hip_ease: float


def build_school_skirt_spec(
    body: BodyMeasurements,
    *,
    waist_ease: float = DEFAULT_WAIST_EASE_MM,
    hip_ease: float = DEFAULT_HIP_EASE_MM,
) -> SchoolSkirtSpec:
    """Resolve body measurements into school-skirt garment measurements.

    Ease is explicit and separate from body measurements so later drafting code
    does not need to guess whether an input value describes the body or garment.
    """

    if waist_ease < 0:
        raise ValueError("waist_ease must be greater than or equal to 0 mm")
    if hip_ease < 0:
        raise ValueError("hip_ease must be greater than or equal to 0 mm")

    return SchoolSkirtSpec(
        body_waist=body.waist,
        body_hip=body.hip,
        garment_waist=body.waist + waist_ease,
        garment_hip=body.hip + hip_ease,
        waist_to_hip=body.waist_to_hip,
        skirt_length=body.garment_length,
        waist_ease=waist_ease,
        hip_ease=hip_ease,
    )
