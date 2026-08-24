"""Quarantined Winifred Aldrich tailored-skirt research candidate.

This module encodes a *named external drafting-system candidate* for comparison
only. It is NOT a production default and MUST NOT be selected automatically by
the production gate.

Source checked against the University of Manchester reproduction of the
Aldrich tailored-skirt block. Key source-native rules used here:

- total waist ease: 10 mm;
- total hip ease: 30 mm;
- back hip span: quarter body hip + 15 mm (side seam moved forward);
- front hip span: the remaining half-garment hip span;
- standard darts: two 20 mm back darts, one 20 mm front dart;
- small-waist variant: 25 mm per dart, but the source gives no numeric trigger
  for automatically choosing that variant.

The generalized repo suppression contract permits asymmetric front/back panel
targets as long as the half-garment total is conserved. This module verifies
that the source-native Aldrich allocation fits that generalized contract while
retaining an explicit flag showing that it would not fit the historical equal-
quarter-per-panel assumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from measurements.body import BodyMeasurements
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.suppression import (
    PanelSuppressionAllocation,
    PanelSuppressionTargets,
    SchoolSkirtSuppressionAllocation,
)
from styles.school_skirt.suppression_validation import (
    validate_school_skirt_panel_suppression_targets,
    validate_school_skirt_suppression_allocation,
)


ALDRICH_WAIST_EASE_MM = 10.0
ALDRICH_HIP_EASE_MM = 30.0
ALDRICH_BACK_HIP_EXTRA_MM = 15.0
ALDRICH_STANDARD_DART_INTAKE_MM = 20.0
ALDRICH_SMALL_WAIST_DART_INTAKE_MM = 25.0


class AldrichVariant(str, Enum):
    STANDARD = "standard"
    SMALL_WAIST = "small_waist"


@dataclass(frozen=True)
class AldrichPanelCandidate:
    hip_span: float
    pre_dart_waist_span: float
    dart_intakes: tuple[float, ...]
    dart_intake_total: float
    side_shaping: float
    finished_waist_span: float
    total_suppression: float


@dataclass(frozen=True)
class AldrichTailoredSkirtCandidate:
    """Inspectable source-native candidate plus repo-contract comparison."""

    variant: AldrichVariant
    front: AldrichPanelCandidate
    back: AldrichPanelCandidate
    canonical_quarter_suppression: float
    mean_source_panel_suppression: float
    panel_targets: PanelSuppressionTargets
    mapped_allocation: SchoolSkirtSuppressionAllocation
    panel_target_validation_errors: tuple[str, ...]
    allocation_validation_errors: tuple[str, ...]
    legacy_equal_quarter_mismatch: bool
    status: str = "RESEARCH_CANDIDATE"
    production_status: str = "NOT_PRODUCTION_DEFAULT"
    source_system: str = "Winifred Aldrich tailored-skirt block"

    @property
    def compatible_with_general_panel_target_contract(self) -> bool:
        return not self.panel_target_validation_errors and not self.allocation_validation_errors


def _panel(
    *,
    hip_span: float,
    pre_dart_waist_span: float,
    dart_intakes: tuple[float, ...],
) -> AldrichPanelCandidate:
    dart_total = sum(dart_intakes)
    finished_waist = pre_dart_waist_span - dart_total
    side_shaping = hip_span - pre_dart_waist_span
    total_suppression = dart_total + side_shaping
    return AldrichPanelCandidate(
        hip_span=hip_span,
        pre_dart_waist_span=pre_dart_waist_span,
        dart_intakes=dart_intakes,
        dart_intake_total=dart_total,
        side_shaping=side_shaping,
        finished_waist_span=finished_waist,
        total_suppression=total_suppression,
    )


def build_aldrich_tailored_skirt_candidate(
    body: BodyMeasurements,
    *,
    variant: AldrichVariant,
) -> AldrichTailoredSkirtCandidate:
    """Build a quarantined Aldrich candidate for one supplied body.

    ``variant`` is mandatory because the source says to use wider darts when the
    waist is small relative to the hip but does not provide a numeric threshold.
    The code therefore never guesses which variant applies.
    """

    quarter_waist = body.waist / 4.0
    quarter_hip = body.hip / 4.0

    if variant is AldrichVariant.STANDARD:
        dart = ALDRICH_STANDARD_DART_INTAKE_MM
        back_pre_dart_addition = 42.5
        front_pre_dart_addition = 22.5
    elif variant is AldrichVariant.SMALL_WAIST:
        dart = ALDRICH_SMALL_WAIST_DART_INTAKE_MM
        back_pre_dart_addition = 52.5
        front_pre_dart_addition = 27.5
    else:  # defensive even though Enum typing should prevent this
        raise ValueError(f"unsupported Aldrich variant: {variant!r}")

    # Aldrich moves the side seam forward. Across one front + one back panel
    # family, the extra 15 mm also accounts for the 30 mm total hip ease over
    # the half garment.
    back_hip_span = quarter_hip + ALDRICH_BACK_HIP_EXTRA_MM
    front_hip_span = quarter_hip

    back = _panel(
        hip_span=back_hip_span,
        pre_dart_waist_span=quarter_waist + back_pre_dart_addition,
        dart_intakes=(dart, dart),
    )
    front = _panel(
        hip_span=front_hip_span,
        pre_dart_waist_span=quarter_waist + front_pre_dart_addition,
        dart_intakes=(dart,),
    )

    canonical_quarter_suppression = (
        (body.hip + ALDRICH_HIP_EASE_MM) / 4.0
        - (body.waist + ALDRICH_WAIST_EASE_MM) / 4.0
    )
    mean_source_panel_suppression = (
        front.total_suppression + back.total_suppression
    ) / 2.0

    targets = PanelSuppressionTargets(
        front=front.total_suppression,
        back=back.total_suppression,
    )
    mapped = SchoolSkirtSuppressionAllocation(
        front=PanelSuppressionAllocation(
            dart_intake_total=front.dart_intake_total,
            side_shaping=front.side_shaping,
        ),
        back=PanelSuppressionAllocation(
            dart_intake_total=back.dart_intake_total,
            side_shaping=back.side_shaping,
        ),
    )

    # Dummy vertical values are positive placeholders because the suppression
    # target validator reads only quarter_suppression.
    comparison_draft = SchoolSkirtDraft(
        quarter_waist=(body.waist + ALDRICH_WAIST_EASE_MM) / 4.0,
        quarter_hip=(body.hip + ALDRICH_HIP_EASE_MM) / 4.0,
        quarter_suppression=canonical_quarter_suppression,
        hip_position=1.0,
        hem_position=2.0,
        hem_half_width=1.0,
    )
    target_errors = tuple(
        validate_school_skirt_panel_suppression_targets(comparison_draft, targets)
    )
    allocation_errors = tuple(
        validate_school_skirt_suppression_allocation(targets, mapped)
    )

    legacy_equal_quarter_mismatch = not (
        math.isclose(front.total_suppression, canonical_quarter_suppression, abs_tol=1e-6)
        and math.isclose(back.total_suppression, canonical_quarter_suppression, abs_tol=1e-6)
    )

    return AldrichTailoredSkirtCandidate(
        variant=variant,
        front=front,
        back=back,
        canonical_quarter_suppression=canonical_quarter_suppression,
        mean_source_panel_suppression=mean_source_panel_suppression,
        panel_targets=targets,
        mapped_allocation=mapped,
        panel_target_validation_errors=target_errors,
        allocation_validation_errors=allocation_errors,
        legacy_equal_quarter_mismatch=legacy_equal_quarter_mismatch,
    )
