"""Explicit policy runner for one school-skirt side-seam candidate.

This module runs one supplied piecewise side-seam strategy against already-built
front and back piecewise geometry inputs, validates the generated segment paths
through the existing join contract, then sends the four validated segment paths
through the existing candidate evaluation pipeline.

No strategy is selected implicitly. The caller must supply an explicit
``SchoolSkirtSideSeamPiecewiseStrategy``. This module performs no fallback,
sorting, ranking, scoring, tolerance check, pass/fail judgement, winner
selection, or production-policy choice.
"""

from styles.school_skirt.geometry_output import Path2D
from styles.school_skirt.side_seam_candidate_evaluator import (
    evaluate_side_seam_candidate,
)
from styles.school_skirt.side_seam_candidate_result import (
    NamedSideSeamCandidateResult,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SchoolSkirtSideSeamPiecewiseStrategy,
    SideSeamPiecewiseGeometryInput,
)
from styles.school_skirt.side_seam_segment_output import (
    join_side_seam_piecewise_output,
)


def _build_validated_piecewise_paths(
    geometry_input: SideSeamPiecewiseGeometryInput,
    strategy: SchoolSkirtSideSeamPiecewiseStrategy,
) -> tuple[Path2D, Path2D]:
    """Build both semantic segments and validate them as one connected side seam."""

    waist_to_hip = strategy.waist_to_hip_policy.build(
        geometry_input.waist_to_hip
    )
    hip_to_hem = strategy.hip_to_hem_policy.build(
        geometry_input.hip_to_hem
    )

    # The joined path is intentionally discarded here. Calling the existing
    # join contract verifies both segment outputs, their semantic endpoints,
    # and the shared hip boundary before measurement begins.
    join_side_seam_piecewise_output(
        geometry_input,
        waist_to_hip,
        hip_to_hem,
    )

    return waist_to_hip, hip_to_hem


def run_side_seam_policy_candidate(
    *,
    candidate_id: str,
    front_input: SideSeamPiecewiseGeometryInput,
    back_input: SideSeamPiecewiseGeometryInput,
    strategy: SchoolSkirtSideSeamPiecewiseStrategy,
) -> NamedSideSeamCandidateResult:
    """Generate, validate, and measure one explicitly supplied policy candidate."""

    front_waist_to_hip, front_hip_to_hem = _build_validated_piecewise_paths(
        front_input,
        strategy,
    )
    back_waist_to_hip, back_hip_to_hem = _build_validated_piecewise_paths(
        back_input,
        strategy,
    )

    return evaluate_side_seam_candidate(
        candidate_id=candidate_id,
        front_waist_to_hip=front_waist_to_hip,
        front_hip_to_hem=front_hip_to_hem,
        back_waist_to_hip=back_waist_to_hip,
        back_hip_to_hem=back_hip_to_hem,
    )
