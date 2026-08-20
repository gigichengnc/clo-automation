"""Named measurement results for school-skirt side-seam curve candidates.

This module binds a stable candidate identifier to an already-built
``SideSeamCandidateMeasurementReport``. It deliberately performs no ranking,
scoring, tolerance check, pass/fail judgement, or production-policy selection.

Candidate identifiers must be non-empty strings without leading or trailing
whitespace. No stronger naming convention is imposed here.
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_candidate_report import (
    SideSeamCandidateMeasurementReport,
)


@dataclass(frozen=True)
class NamedSideSeamCandidateResult:
    """One identified side-seam candidate and its measurement-only report."""

    candidate_id: str
    report: SideSeamCandidateMeasurementReport

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_id, str):
            raise ValueError("candidate_id must be a string")
        if not self.candidate_id:
            raise ValueError("candidate_id must not be empty")
        if self.candidate_id != self.candidate_id.strip():
            raise ValueError("candidate_id must not contain leading or trailing whitespace")
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must not be blank")
