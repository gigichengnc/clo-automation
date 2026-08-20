"""Segment-level measurement reports for school-skirt side-seam candidates.

This module measures already-resolved front/back side-seam candidate segments and
reports where their length difference occurs: waist-to-hip, hip-to-hem, and the
combined total. It deliberately sets no mismatch tolerance and performs no
pass/fail judgement.

The total length is the sum of the two measured semantic segment lengths for
each panel. This keeps upper and lower contributions visible instead of hiding
them inside one total number.

All coordinates and returned lengths use millimetres (mm).
"""

from dataclasses import dataclass

from styles.school_skirt.geometry_output import Path2D
from styles.school_skirt.side_seam_measurement import (
    SideSeamLengthComparison,
    compare_side_seam_lengths,
)


@dataclass(frozen=True)
class SideSeamCandidateMeasurementReport:
    """Front/back length comparisons for both semantic segments and their total."""

    waist_to_hip: SideSeamLengthComparison
    hip_to_hem: SideSeamLengthComparison
    total: SideSeamLengthComparison


def _combine_comparisons(
    waist_to_hip: SideSeamLengthComparison,
    hip_to_hem: SideSeamLengthComparison,
) -> SideSeamLengthComparison:
    """Combine two measured semantic segments without applying a judgement."""

    front_length = waist_to_hip.front_length + hip_to_hem.front_length
    back_length = waist_to_hip.back_length + hip_to_hem.back_length
    back_minus_front = back_length - front_length

    return SideSeamLengthComparison(
        front_length=front_length,
        back_length=back_length,
        back_minus_front=back_minus_front,
        absolute_difference=abs(back_minus_front),
    )


def build_side_seam_candidate_measurement_report(
    *,
    front_waist_to_hip: Path2D,
    front_hip_to_hem: Path2D,
    back_waist_to_hip: Path2D,
    back_hip_to_hem: Path2D,
) -> SideSeamCandidateMeasurementReport:
    """Measure front/back candidate segments and expose localized differences."""

    waist_to_hip = compare_side_seam_lengths(
        front_waist_to_hip,
        back_waist_to_hip,
    )
    hip_to_hem = compare_side_seam_lengths(
        front_hip_to_hem,
        back_hip_to_hem,
    )

    return SideSeamCandidateMeasurementReport(
        waist_to_hip=waist_to_hip,
        hip_to_hem=hip_to_hem,
        total=_combine_comparisons(waist_to_hip, hip_to_hem),
    )
