"""School-skirt garment specification derived from validated inputs.

This module separates body measurements, garment requests, and resolved garment
measurements. It contains no pattern geometry and does not generate or modify
DXF files.

All values use millimetres (mm).
"""

from dataclasses import dataclass

from garment.request import GarmentRequest
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
    request: GarmentRequest,
    *,
    waist_ease: float = DEFAULT_WAIST_EASE_MM,
    hip_ease: float = DEFAULT_HIP_EASE_MM,
) -> SchoolSkirtSpec:
    """Resolve validated inputs into school-skirt garment measurements.

    Call the layer validators before this builder. Ease remains explicit so
    downstream drafting code never needs to guess whether an input describes
    the body or the finished garment.
    """

    return SchoolSkirtSpec(
        body_waist=body.waist,
        body_hip=body.hip,
        garment_waist=body.waist + waist_ease,
        garment_hip=body.hip + hip_ease,
        waist_to_hip=body.waist_to_hip,
        skirt_length=request.requested_length,
        waist_ease=waist_ease,
        hip_ease=hip_ease,
    )
