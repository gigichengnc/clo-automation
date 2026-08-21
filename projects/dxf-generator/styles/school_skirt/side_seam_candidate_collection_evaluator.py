"""Composition helper for evaluating collections of school-skirt side-seam candidates.

This module accepts ordered candidate path sets, evaluates each one through the
existing single-candidate measurement pipeline, then builds both an identity-
unique ``SideSeamCandidateCollection`` and its measurement-only comparison
snapshot.

The supplied order is preserved exactly. This module deliberately performs no
sorting, ranking, scoring, tolerance check, pass/fail judgement, winner
selection, or production-policy choice.

Validation ownership remains downstream: path validation belongs to the
measurement layer, candidate-identifier validation belongs to
``NamedSideSeamCandidateResult``, and duplicate-identifier validation belongs
to ``SideSeamCandidateCollection``.
"""

from dataclasses import dataclass

from styles.school_skirt.geometry_output import Path2D
from styles.school_skirt.side_seam_candidate_collection import (
    SideSeamCandidateCollection,
)
from styles.school_skirt.side_seam_candidate_evaluator import (
    evaluate_side_seam_candidate,
)
from styles.school_skirt.side_seam_candidate_snapshot import (
    SideSeamCandidateComparisonSnapshot,
    build_side_seam_candidate_comparison_snapshot,
)


@dataclass(frozen=True)
class SideSeamCandidatePathSet:
    """One named candidate's four already-resolved semantic segment paths."""

    candidate_id: str
    front_waist_to_hip: Path2D
    front_hip_to_hem: Path2D
    back_waist_to_hip: Path2D
    back_hip_to_hem: Path2D


@dataclass(frozen=True)
class SideSeamCandidateCollectionEvaluation:
    """Evaluated candidate collection together with its non-ranked snapshot."""

    collection: SideSeamCandidateCollection
    snapshot: SideSeamCandidateComparisonSnapshot


def evaluate_side_seam_candidate_collection(
    candidates: tuple[SideSeamCandidatePathSet, ...],
) -> SideSeamCandidateCollectionEvaluation:
    """Evaluate ordered candidate path sets and build collection plus snapshot."""

    collection = SideSeamCandidateCollection(
        candidates=tuple(
            evaluate_side_seam_candidate(
                candidate_id=candidate.candidate_id,
                front_waist_to_hip=candidate.front_waist_to_hip,
                front_hip_to_hem=candidate.front_hip_to_hem,
                back_waist_to_hip=candidate.back_waist_to_hip,
                back_hip_to_hem=candidate.back_hip_to_hem,
            )
            for candidate in candidates
        )
    )

    return SideSeamCandidateCollectionEvaluation(
        collection=collection,
        snapshot=build_side_seam_candidate_comparison_snapshot(collection),
    )
