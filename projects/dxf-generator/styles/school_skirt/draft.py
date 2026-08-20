"""Policy-independent derived values for school-skirt drafting.

This layer converts resolved garment measurements and style parameters into
simple numeric drafting values that do not depend on a dart-allocation policy.
It contains no coordinates, pattern geometry, or DXF logic.

Constructability and dart-allocation rules intentionally live in later steps.
All values use millimetres (mm).
"""

from dataclasses import dataclass

from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.spec import SchoolSkirtSpec


@dataclass(frozen=True)
class SchoolSkirtDraft:
    """Policy-independent numeric values used by later drafting layers."""

    quarter_waist: float
    quarter_hip: float
    quarter_suppression: float
    hip_position: float
    hem_position: float
    hem_half_width: float


def build_school_skirt_draft(
    spec: SchoolSkirtSpec,
    parameters: SchoolSkirtDraftingParameters,
) -> SchoolSkirtDraft:
    """Derive policy-independent drafting values from validated inputs.

    This builder performs arithmetic only. It does not choose dart intake,
    allocate suppression, validate constructability, or generate coordinates.
    """

    quarter_waist = spec.garment_waist / 4.0
    quarter_hip = spec.garment_hip / 4.0

    return SchoolSkirtDraft(
        quarter_waist=quarter_waist,
        quarter_hip=quarter_hip,
        quarter_suppression=quarter_hip - quarter_waist,
        hip_position=spec.waist_to_hip,
        hem_position=spec.skirt_length,
        hem_half_width=quarter_hip + parameters.flare,
    )
