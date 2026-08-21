"""Runner for reproducible named quadratic Bezier side-seam research candidates.

This module accepts ordered ``NamedQuadraticCandidateSpec`` values, adapts each
one through the existing quadratic candidate adapter, then delegates execution
to the existing multi-policy runner. The resulting candidate collection and
comparison snapshot therefore keep the same validation and measurement
contracts as all other explicit side-seam policy candidates.

The supplied order is preserved exactly. This module defines no candidate
defaults, sorting, ranking, scoring, tolerance, pass/fail judgement, winner
selection, production policy, seam allowance, or DXF behavior.
"""

from styles.school_skirt.side_seam_candidate_collection_evaluator import (
    SideSeamCandidateCollectionEvaluation,
)
from styles.school_skirt.side_seam_multi_policy_runner import (
    run_side_seam_policy_candidates,
)
from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
    build_quadratic_policy_candidate_spec,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
)


def run_named_quadratic_candidates(
    *,
    front_input: SideSeamPiecewiseGeometryInput,
    back_input: SideSeamPiecewiseGeometryInput,
    candidates: tuple[NamedQuadraticCandidateSpec, ...],
) -> SideSeamCandidateCollectionEvaluation:
    """Run ordered named quadratic research configs through the shared pipeline."""

    return run_side_seam_policy_candidates(
        front_input=front_input,
        back_input=back_input,
        candidates=tuple(
            build_quadratic_policy_candidate_spec(candidate)
            for candidate in candidates
        ),
    )
