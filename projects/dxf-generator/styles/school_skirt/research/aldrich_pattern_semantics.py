"""Source-faithful Aldrich tailored-skirt research pattern semantics.

This module carries the quarantined Aldrich tailored-skirt candidate one layer
closer to coordinate geometry without promoting it to a production policy.
It preserves source-native panel balance, dart intake, dart positions and
per-dart lengths, then builds explicit asymmetric ``PanelGeometryInput`` values.

It deliberately stops before coordinate curves. The source says to draw a
slightly curved waistline and to curve the side seam outward by 5 mm, but that
instruction is not a uniquely specified mathematical curve family. This module
therefore records those items as blockers instead of guessing geometry.

No seam allowance, notches, grain, closure, material rules or DXF are produced.
All dimensional values use millimetres (mm).
"""

from __future__ import annotations

from dataclasses import dataclass

from measurements.body import BodyMeasurements
from styles.school_skirt.dart_distribution import (
    PanelDartDistribution,
    SchoolSkirtDartDistribution,
)
from styles.school_skirt.dart_placement import (
    DartPlacement,
    PanelDartPlacement,
    SchoolSkirtDartPlacement,
)
from styles.school_skirt.dart_plan import (
    PanelDartPlan,
    ResolvedDart,
    SchoolSkirtDartPlan,
)
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.panel_geometry_input import (
    PanelFinishedSpans,
    SchoolSkirtPanelFinishedSpans,
    SchoolSkirtPanelGeometryInput,
    build_school_skirt_panel_geometry_input_from_spans,
)
from styles.school_skirt.panel_geometry_input_validation import (
    validate_school_skirt_panel_geometry_input,
)
from styles.school_skirt.research.aldrich_tailored_candidate import (
    ALDRICH_HIP_EASE_MM,
    ALDRICH_WAIST_EASE_MM,
    AldrichTailoredSkirtCandidate,
    AldrichVariant,
    build_aldrich_tailored_skirt_candidate,
)


ALDRICH_FRONT_DART_CENTER_FRACTIONS = (1.0 / 3.0,)
ALDRICH_BACK_DART_CENTER_FRACTIONS = (1.0 / 3.0, 2.0 / 3.0)
ALDRICH_FRONT_DART_LENGTHS_MM = (100.0,)
ALDRICH_BACK_DART_LENGTHS_MM = (140.0, 125.0)


@dataclass(frozen=True)
class ResearchPatternBlocker:
    code: str
    detail: str


@dataclass(frozen=True)
class AldrichResearchPatternSemantics:
    """Inspectable source-native semantics before coordinate curve generation."""

    source_candidate: AldrichTailoredSkirtCandidate
    skirt_length: float
    draft: SchoolSkirtDraft
    panel_spans: SchoolSkirtPanelFinishedSpans
    dart_distribution: SchoolSkirtDartDistribution
    dart_placement: SchoolSkirtDartPlacement
    dart_plan: SchoolSkirtDartPlan
    geometry_input: SchoolSkirtPanelGeometryInput
    geometry_input_validation_errors: tuple[str, ...]
    blockers: tuple[ResearchPatternBlocker, ...]
    status: str = "RESEARCH_PATTERN_INPUTS"
    production_status: str = "NOT_FACTORY_READY"

    @property
    def semantic_inputs_valid(self) -> bool:
        return (
            self.source_candidate.compatible_with_general_panel_target_contract
            and not self.geometry_input_validation_errors
        )


def _build_dart_semantics(
    candidate: AldrichTailoredSkirtCandidate,
) -> tuple[SchoolSkirtDartDistribution, SchoolSkirtDartPlacement, SchoolSkirtDartPlan]:
    front_intakes = candidate.front.dart_intakes
    back_intakes = candidate.back.dart_intakes

    distribution = SchoolSkirtDartDistribution(
        front=PanelDartDistribution(dart_intakes=front_intakes),
        back=PanelDartDistribution(dart_intakes=back_intakes),
    )
    placement = SchoolSkirtDartPlacement(
        front=PanelDartPlacement(
            darts=tuple(
                DartPlacement(center_fraction=value)
                for value in ALDRICH_FRONT_DART_CENTER_FRACTIONS
            )
        ),
        back=PanelDartPlacement(
            darts=tuple(
                DartPlacement(center_fraction=value)
                for value in ALDRICH_BACK_DART_CENTER_FRACTIONS
            )
        ),
    )

    if len(front_intakes) != len(ALDRICH_FRONT_DART_LENGTHS_MM):
        raise ValueError("Aldrich front dart intake/length count mismatch")
    if len(back_intakes) != len(ALDRICH_BACK_DART_LENGTHS_MM):
        raise ValueError("Aldrich back dart intake/length count mismatch")

    dart_plan = SchoolSkirtDartPlan(
        front=PanelDartPlan(
            darts=tuple(
                ResolvedDart(
                    dart_index=index,
                    intake=intake,
                    center_fraction=center,
                    length=length,
                )
                for index, (intake, center, length) in enumerate(
                    zip(
                        front_intakes,
                        ALDRICH_FRONT_DART_CENTER_FRACTIONS,
                        ALDRICH_FRONT_DART_LENGTHS_MM,
                    )
                )
            )
        ),
        back=PanelDartPlan(
            darts=tuple(
                ResolvedDart(
                    dart_index=index,
                    intake=intake,
                    center_fraction=center,
                    length=length,
                )
                for index, (intake, center, length) in enumerate(
                    zip(
                        back_intakes,
                        ALDRICH_BACK_DART_CENTER_FRACTIONS,
                        ALDRICH_BACK_DART_LENGTHS_MM,
                    )
                )
            )
        ),
    )
    return distribution, placement, dart_plan


def build_aldrich_research_pattern_semantics(
    body: BodyMeasurements,
    *,
    skirt_length: float,
    variant: AldrichVariant,
) -> AldrichResearchPatternSemantics:
    """Build source-native semantic pattern inputs for a controlled experiment.

    ``skirt_length`` and ``variant`` are mandatory. The source does not provide a
    numeric trigger for selecting its small-waist variant, so this adapter never
    auto-selects it.
    """

    if isinstance(skirt_length, bool) or not isinstance(skirt_length, (int, float)):
        raise ValueError("skirt_length must be numeric")
    if skirt_length <= 0:
        raise ValueError("skirt_length must be greater than 0 mm")

    candidate = build_aldrich_tailored_skirt_candidate(body, variant=variant)
    finished_waist = body.waist + ALDRICH_WAIST_EASE_MM
    finished_hip = body.hip + ALDRICH_HIP_EASE_MM

    draft = SchoolSkirtDraft(
        quarter_waist=finished_waist / 4.0,
        quarter_hip=finished_hip / 4.0,
        quarter_suppression=finished_hip / 4.0 - finished_waist / 4.0,
        hip_position=body.waist_to_hip,
        hem_position=float(skirt_length),
        # This global scalar is not consumed by the explicit-span builder. It is
        # retained only because SchoolSkirtDraft is the canonical arithmetic
        # carrier and requires the field.
        hem_half_width=finished_hip / 4.0,
    )

    # In this tailored straight-skirt block the hip-side construction is squared
    # down to the hemline, so the panel hem endpoints retain the same horizontal
    # spans as the hip endpoints before the unresolved side-seam curve is drawn.
    spans = SchoolSkirtPanelFinishedSpans(
        front=PanelFinishedSpans(
            target_waist_span=candidate.front.finished_waist_span,
            hip_span=candidate.front.hip_span,
            hem_span=candidate.front.hip_span,
        ),
        back=PanelFinishedSpans(
            target_waist_span=candidate.back.finished_waist_span,
            hip_span=candidate.back.hip_span,
            hem_span=candidate.back.hip_span,
        ),
    )

    distribution, placement, dart_plan = _build_dart_semantics(candidate)
    geometry_input = build_school_skirt_panel_geometry_input_from_spans(
        draft,
        spans,
        candidate.mapped_allocation,
        dart_plan,
    )
    geometry_errors = tuple(
        validate_school_skirt_panel_geometry_input(geometry_input)
    )

    blockers = (
        ResearchPatternBlocker(
            code="WAIST_CURVE_UNRESOLVED",
            detail=(
                "source instructs a slight waist curve but this adapter has no "
                "source-defined deterministic curve family"
            ),
        ),
        ResearchPatternBlocker(
            code="SIDE_SEAM_CURVE_UNRESOLVED",
            detail=(
                "source instructs the side seam to curve outward by 5 mm but "
                "does not uniquely specify the curve construction used here"
            ),
        ),
        ResearchPatternBlocker(
            code="A_LINE_FLARE_NOT_APPLIED",
            detail=(
                "this is the Aldrich tailored straight-skirt block; an A-line "
                "flare transform is a separate unresolved style policy"
            ),
        ),
        ResearchPatternBlocker(
            code="PRODUCTION_TRANSFORMS_UNRESOLVED",
            detail=(
                "seam allowance, notches, grain, closure, material layers and "
                "factory DXF serialization are intentionally absent"
            ),
        ),
    )

    return AldrichResearchPatternSemantics(
        source_candidate=candidate,
        skirt_length=float(skirt_length),
        draft=draft,
        panel_spans=spans,
        dart_distribution=distribution,
        dart_placement=placement,
        dart_plan=dart_plan,
        geometry_input=geometry_input,
        geometry_input_validation_errors=geometry_errors,
        blockers=blockers,
    )
