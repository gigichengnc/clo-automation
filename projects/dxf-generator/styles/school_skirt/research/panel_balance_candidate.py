"""Research-only panel-balance candidate contract.

A panel-target research candidate must expose the front/back finished hip spans
and finished waist spans from a named drafting method or explicit experiment.
The engine derives suppression targets from those spans and checks them against
the generalized school-skirt conservation contract.

This module chooses no production policy, contains no ratio defaults and creates
no pattern geometry or DXF.
"""

from __future__ import annotations

from dataclasses import dataclass

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.suppression import PanelSuppressionTargets
from styles.school_skirt.suppression_validation import (
    validate_school_skirt_panel_suppression_targets,
)


@dataclass(frozen=True)
class PanelBalanceEvidence:
    """Explicit front/back spans supplied by a named research candidate."""

    front_hip_span: float
    back_hip_span: float
    front_finished_waist_span: float
    back_finished_waist_span: float
    provenance: str
    status: str = "RESEARCH_CANDIDATE"
    production_status: str = "NOT_PRODUCTION_DEFAULT"

    @property
    def targets(self) -> PanelSuppressionTargets:
        return PanelSuppressionTargets(
            front=self.front_hip_span - self.front_finished_waist_span,
            back=self.back_hip_span - self.back_finished_waist_span,
        )

    @property
    def half_garment_hip_span(self) -> float:
        return self.front_hip_span + self.back_hip_span

    @property
    def half_garment_waist_span(self) -> float:
        return self.front_finished_waist_span + self.back_finished_waist_span

    @property
    def half_garment_suppression(self) -> float:
        return self.half_garment_hip_span - self.half_garment_waist_span


@dataclass(frozen=True)
class PanelBalanceCandidateEvaluation:
    candidate: PanelBalanceEvidence
    validation_errors: tuple[str, ...]

    @property
    def compatible_with_global_suppression(self) -> bool:
        return not self.validation_errors


def evaluate_panel_balance_candidate(
    draft: SchoolSkirtDraft,
    candidate: PanelBalanceEvidence,
) -> PanelBalanceCandidateEvaluation:
    """Validate one explicit research candidate against global suppression.

    The validator checks conservation only. Passing this evaluation does not
    establish fit quality or production authority.
    """

    errors = tuple(
        validate_school_skirt_panel_suppression_targets(draft, candidate.targets)
    )
    return PanelBalanceCandidateEvaluation(
        candidate=candidate,
        validation_errors=errors,
    )
