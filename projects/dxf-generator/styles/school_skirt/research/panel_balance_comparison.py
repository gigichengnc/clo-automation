"""Research-only comparison runner for school-skirt panel-balance candidates.

The runner compares multiple explicit ``PanelBalanceEvidence`` candidates against
one shared finished-garment contract. It performs accounting/conservation checks
only; it does not rank candidates, choose a production policy, generate pattern
geometry, or export DXF.

All values use millimetres (mm).
"""

from __future__ import annotations

from dataclasses import dataclass

from measurements.body import BodyMeasurements
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.research.panel_balance_candidate import (
    PanelBalanceCandidateEvaluation,
    PanelBalanceEvidence,
    evaluate_panel_balance_candidate,
)


@dataclass(frozen=True)
class PanelBalanceComparisonContext:
    """One body plus one fixed finished-waist/finished-hip experiment contract."""

    body: BodyMeasurements
    finished_waist: float
    finished_hip: float

    @property
    def waist_ease(self) -> float:
        return self.finished_waist - self.body.waist

    @property
    def hip_ease(self) -> float:
        return self.finished_hip - self.body.hip

    @property
    def quarter_suppression(self) -> float:
        return self.finished_hip / 4.0 - self.finished_waist / 4.0

    def comparison_draft(self) -> SchoolSkirtDraft:
        """Return the minimal policy-independent draft needed for conservation."""

        return SchoolSkirtDraft(
            quarter_waist=self.finished_waist / 4.0,
            quarter_hip=self.finished_hip / 4.0,
            quarter_suppression=self.quarter_suppression,
            hip_position=1.0,
            hem_position=2.0,
            hem_half_width=1.0,
        )


@dataclass(frozen=True)
class PanelBalanceComparisonRow:
    name: str
    provenance: str
    front_hip_span: float
    back_hip_span: float
    front_finished_waist_span: float
    back_finished_waist_span: float
    front_target: float
    back_target: float
    conservation_pass: bool
    validation_errors: tuple[str, ...]
    production_status: str


@dataclass(frozen=True)
class PanelBalanceComparisonReport:
    context: PanelBalanceComparisonContext
    rows: tuple[PanelBalanceComparisonRow, ...]
    excluded_candidates: tuple[str, ...] = ()
    status: str = "RESEARCH_COMPARISON"
    production_status: str = "NOT_PRODUCTION_RANKING"


def build_symmetric_panel_balance_baseline(
    context: PanelBalanceComparisonContext,
) -> PanelBalanceEvidence:
    """Build a neutral 50/50 architectural baseline for the same finished garment.

    This helper is deliberately labelled as a baseline rather than a production
    policy. It splits both the half-garment hip and waist spans equally.
    """

    return PanelBalanceEvidence(
        front_hip_span=context.finished_hip / 4.0,
        back_hip_span=context.finished_hip / 4.0,
        front_finished_waist_span=context.finished_waist / 4.0,
        back_finished_waist_span=context.finished_waist / 4.0,
        provenance="ARCHITECTURAL_BASELINE: symmetric 50/50 finished spans",
        status="RESEARCH_BASELINE",
        production_status="NOT_APPROVED",
    )


def _row(
    name: str,
    evaluation: PanelBalanceCandidateEvaluation,
) -> PanelBalanceComparisonRow:
    candidate = evaluation.candidate
    targets = candidate.targets
    return PanelBalanceComparisonRow(
        name=name,
        provenance=candidate.provenance,
        front_hip_span=candidate.front_hip_span,
        back_hip_span=candidate.back_hip_span,
        front_finished_waist_span=candidate.front_finished_waist_span,
        back_finished_waist_span=candidate.back_finished_waist_span,
        front_target=targets.front,
        back_target=targets.back,
        conservation_pass=evaluation.compatible_with_global_suppression,
        validation_errors=evaluation.validation_errors,
        production_status=candidate.production_status,
    )


def compare_panel_balance_candidates(
    context: PanelBalanceComparisonContext,
    candidates: tuple[tuple[str, PanelBalanceEvidence], ...],
    *,
    excluded_candidates: tuple[str, ...] = (),
) -> PanelBalanceComparisonReport:
    """Evaluate candidates under one shared finished-garment contract.

    Passing conservation means only that the candidate accounts for the same
    finished waist/hip relationship. It does not establish fit quality,
    drafting-system correctness, or production authority.
    """

    draft = context.comparison_draft()
    rows = tuple(
        _row(name, evaluate_panel_balance_candidate(draft, candidate))
        for name, candidate in candidates
    )
    return PanelBalanceComparisonReport(
        context=context,
        rows=rows,
        excluded_candidates=excluded_candidates,
    )


def render_panel_balance_comparison_markdown(
    report: PanelBalanceComparisonReport,
) -> str:
    """Render an inspectable Markdown comparison with no winner/ranking."""

    context = report.context
    lines = [
        "# Panel Balance Candidate Comparison",
        "",
        f"Status: `{report.status}` / `{report.production_status}`",
        "",
        "## Shared experiment contract",
        "",
        f"- body waist: {context.body.waist:.3f} mm",
        f"- body hip: {context.body.hip:.3f} mm",
        f"- finished waist: {context.finished_waist:.3f} mm",
        f"- finished hip: {context.finished_hip:.3f} mm",
        f"- waist ease: {context.waist_ease:.3f} mm",
        f"- hip ease: {context.hip_ease:.3f} mm",
        f"- quarter suppression: {context.quarter_suppression:.3f} mm",
        "",
        "## Candidate accounting",
        "",
        "| Candidate | Front hip | Back hip | Front waist | Back waist | Front target | Back target | Conservation | Production status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]

    for row in report.rows:
        lines.append(
            "| "
            f"{row.name} | {row.front_hip_span:.3f} | {row.back_hip_span:.3f} | "
            f"{row.front_finished_waist_span:.3f} | {row.back_finished_waist_span:.3f} | "
            f"{row.front_target:.3f} | {row.back_target:.3f} | "
            f"{'PASS' if row.conservation_pass else 'FAIL'} | {row.production_status} |"
        )

    lines.extend(
        [
            "",
            "No candidate is ranked or selected by this report.",
        ]
    )

    if report.excluded_candidates:
        lines.extend(["", "## Not instantiated", ""])
        lines.extend(f"- {item}" for item in report.excluded_candidates)

    failures = [row for row in report.rows if row.validation_errors]
    if failures:
        lines.extend(["", "## Validation errors", ""])
        for row in failures:
            lines.append(f"### {row.name}")
            lines.extend(f"- {error}" for error in row.validation_errors)

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "A conservation PASS proves accounting compatibility with the shared finished-waist/finished-hip contract only. It does not prove fit, comfort, manufacturing suitability, or production approval.",
            "",
        ]
    )
    return "\n".join(lines)
