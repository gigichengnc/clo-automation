"""Composition helper for evaluating one school-skirt side-seam candidate.

This module wires one stable candidate identifier and four already-resolved
front/back semantic side-seam segment paths through the existing measurement
and naming contracts. It deliberately performs no curve generation, sorting,
ranking, scoring, tolerance check, pass/fail judgement, winner selection, or
production-policy choice.

Path validation remains owned by the measurement layer. Candidate-identifier
validation remains owned by ``NamedSideSeamCandidateResult``.
"""

from styles.school_skirt.geometry_output import Path2D
from styles.school_skirt.side_seam_candidate_report import (
    build_side_seam_candidate_measurement_report,
)
from styles.school_skirt.side_seam_candidate_result import (
    NamedSideSeamCandidateResult,
)


def evaluate_side_seam_candidate(
    *,
    candidate_id: str,
    front_waist_to_hip: Path2D,
    front_hip_to_hem: Path2D,
    back_waist_to_hip: Path2D,
    back_hip_to_hem: Path2D,
) -> NamedSideSeamCandidateResult:
    """Measure one candidate's four semantic segment paths and bind its identity."""

    report = build_side_seam_candidate_measurement_report(
        front_waist_to_hip=front_waist_to_hip,
        front_hip_to_hem=front_hip_to_hem,
        back_waist_to_hip=back_waist_to_hip,
        back_hip_to_hem=back_hip_to_hem,
    )

    return NamedSideSeamCandidateResult(
        candidate_id=candidate_id,
        report=report,
    )
