"""Collection contract for named school-skirt side-seam candidate results.

This module groups already-named side-seam candidate measurement results while
preserving their supplied order and enforcing unique candidate identifiers. The
stored order is not a ranking and carries no preference or production meaning.

It deliberately performs no sorting, scoring, tolerance check, pass/fail
judgement, winner selection, or production-policy choice. Empty collections are
allowed; minimum comparison-set size belongs to a later explicit workflow, not
this storage contract.
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_candidate_result import (
    NamedSideSeamCandidateResult,
)


@dataclass(frozen=True)
class SideSeamCandidateCollection:
    """An ordered, identity-unique set of named measurement-only candidates."""

    candidates: tuple[NamedSideSeamCandidateResult, ...]

    def __post_init__(self) -> None:
        seen = set()
        for candidate in self.candidates:
            if candidate.candidate_id in seen:
                raise ValueError(
                    f"duplicate side-seam candidate_id: {candidate.candidate_id}"
                )
            seen.add(candidate.candidate_id)
