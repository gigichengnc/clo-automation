"""Comparison snapshots for school-skirt side-seam candidate collections.

This module projects an ordered ``SideSeamCandidateCollection`` into compact,
measurement-only rows suitable for side-by-side inspection. Each semantic region
keeps both the signed ``back_minus_front`` value and its absolute difference.

The supplied candidate order is preserved exactly. This module deliberately
performs no sorting, ranking, scoring, tolerance check, pass/fail judgement,
winner selection, or production-policy choice.

All returned differences use millimetres (mm).
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_candidate_collection import (
    SideSeamCandidateCollection,
)
from styles.school_skirt.side_seam_measurement import SideSeamLengthComparison


@dataclass(frozen=True)
class SideSeamMismatchSnapshot:
    """Signed and absolute front/back mismatch for one semantic region."""

    back_minus_front: float
    absolute_difference: float


@dataclass(frozen=True)
class SideSeamCandidateComparisonRow:
    """One candidate's upper, lower, and total mismatch measurements."""

    candidate_id: str
    waist_to_hip: SideSeamMismatchSnapshot
    hip_to_hem: SideSeamMismatchSnapshot
    total: SideSeamMismatchSnapshot


@dataclass(frozen=True)
class SideSeamCandidateComparisonSnapshot:
    """Ordered measurement-only comparison rows for a candidate collection."""

    rows: tuple[SideSeamCandidateComparisonRow, ...]


def _mismatch_snapshot(
    comparison: SideSeamLengthComparison,
) -> SideSeamMismatchSnapshot:
    return SideSeamMismatchSnapshot(
        back_minus_front=comparison.back_minus_front,
        absolute_difference=comparison.absolute_difference,
    )


def build_side_seam_candidate_comparison_snapshot(
    collection: SideSeamCandidateCollection,
) -> SideSeamCandidateComparisonSnapshot:
    """Project named candidate reports into ordered, non-ranked comparison rows."""

    return SideSeamCandidateComparisonSnapshot(
        rows=tuple(
            SideSeamCandidateComparisonRow(
                candidate_id=candidate.candidate_id,
                waist_to_hip=_mismatch_snapshot(candidate.report.waist_to_hip),
                hip_to_hem=_mismatch_snapshot(candidate.report.hip_to_hem),
                total=_mismatch_snapshot(candidate.report.total),
            )
            for candidate in collection.candidates
        )
    )
