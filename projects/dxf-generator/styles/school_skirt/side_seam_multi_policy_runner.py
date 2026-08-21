"""Explicit multi-policy runner for school-skirt side-seam candidates.

This module runs multiple explicitly named piecewise side-seam strategies against
the same already-built front and back piecewise geometry inputs. Each strategy
is evaluated through the existing single-policy runner, then all named results
are assembled into the existing identity-unique candidate collection and its
measurement-only comparison snapshot.

The supplied candidate order is preserved exactly. No strategy is selected
implicitly, and this module performs no fallback, sorting, ranking, scoring,
tolerance check, pass/fail judgement, winner selection, or production-policy
choice.
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_candidate_collection import (
    SideSeamCandidateCollection,
)
from styles.school_skirt.side_seam_candidate_collection_evaluator import (
    SideSeamCandidateCollectionEvaluation,
)
from styles.school_skirt.side_seam_candidate_snapshot import (
    build_side_seam_candidate_comparison_snapshot,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SchoolSkirtSideSeamPiecewiseStrategy,
    SideSeamPiecewiseGeometryInput,
)
from styles.school_skirt.side_seam_policy_candidate_runner import (
    run_side_seam_policy_candidate,
)


@dataclass(frozen=True)
class SideSeamPolicyCandidateSpec:
    """One stable candidate identifier paired with one explicit strategy."""

    candidate_id: str
    strategy: SchoolSkirtSideSeamPiecewiseStrategy


def run_side_seam_policy_candidates(
    *,
    front_input: SideSeamPiecewiseGeometryInput,
    back_input: SideSeamPiecewiseGeometryInput,
    candidates: tuple[SideSeamPolicyCandidateSpec, ...],
) -> SideSeamCandidateCollectionEvaluation:
    """Run explicit strategies on shared geometry inputs and build one snapshot."""

    collection = SideSeamCandidateCollection(
        candidates=tuple(
            run_side_seam_policy_candidate(
                candidate_id=candidate.candidate_id,
                front_input=front_input,
                back_input=back_input,
                strategy=candidate.strategy,
            )
            for candidate in candidates
        )
    )

    return SideSeamCandidateCollectionEvaluation(
        collection=collection,
        snapshot=build_side_seam_candidate_comparison_snapshot(collection),
    )
