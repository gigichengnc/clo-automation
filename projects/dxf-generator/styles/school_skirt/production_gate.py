"""Production-readiness gate for the first A-line school-skirt pilot.

This module reuses the canonical measurement, garment-request, school-skirt
specification and policy-independent draft layers already present in the repo.
It does not define a second body-measurement model and it does not generate
coordinates or DXF.

The gate distinguishes:

- arithmetic / validation that is already implemented and testable;
- drafting decisions that still require a validated production rule;
- invalid inputs that must stop immediately.

All dimensional values use millimetres (mm).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from garment.request import GarmentRequest
from garment.validation import validate_garment_request
from measurements.body import BodyMeasurements
from measurements.validation import validate_body_measurements
from styles.school_skirt.constructability_validation import (
    validate_school_skirt_constructability,
)
from styles.school_skirt.draft import SchoolSkirtDraft, build_school_skirt_draft
from styles.school_skirt.draft_validation import validate_school_skirt_draft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.parameters_validation import validate_school_skirt_parameters
from styles.school_skirt.spec import SchoolSkirtSpec, build_school_skirt_spec
from styles.school_skirt.validation import validate_school_skirt_spec_inputs


class ProductionGateStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    NEEDS_RULE = "NEEDS_RULE"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class ProductionGateAssessment:
    requirement: str
    status: ProductionGateStatus
    value: Any
    reason: str
    required_evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class SchoolSkirtProductionGate:
    """Inspectable readiness result before any production pattern geometry."""

    body: BodyMeasurements
    request: GarmentRequest
    waist_ease: float
    hip_ease: float
    parameters: SchoolSkirtDraftingParameters
    spec: SchoolSkirtSpec | None
    draft: SchoolSkirtDraft | None
    assessments: tuple[ProductionGateAssessment, ...]
    source_contract: str = "school-skirt-production-gate-v0.1"

    @property
    def blockers(self) -> tuple[ProductionGateAssessment, ...]:
        return tuple(
            item
            for item in self.assessments
            if item.status is not ProductionGateStatus.SUPPORTED
        )

    @property
    def ready_for_pattern_geometry(self) -> bool:
        return not self.blockers

    def assessment(self, requirement: str) -> ProductionGateAssessment:
        matches = [item for item in self.assessments if item.requirement == requirement]
        if len(matches) != 1:
            raise KeyError(requirement)
        return matches[0]


def _supported(requirement: str, value: Any, reason: str) -> ProductionGateAssessment:
    return ProductionGateAssessment(
        requirement=requirement,
        status=ProductionGateStatus.SUPPORTED,
        value=value,
        reason=reason,
    )


def _needs_rule(
    requirement: str,
    value: Any,
    reason: str,
    *required_evidence: str,
) -> ProductionGateAssessment:
    return ProductionGateAssessment(
        requirement=requirement,
        status=ProductionGateStatus.NEEDS_RULE,
        value=value,
        reason=reason,
        required_evidence=tuple(required_evidence),
    )


def _unsupported(
    requirement: str,
    value: Any,
    reason: str,
) -> ProductionGateAssessment:
    return ProductionGateAssessment(
        requirement=requirement,
        status=ProductionGateStatus.UNSUPPORTED,
        value=value,
        reason=reason,
    )


def _error_assessment(requirement: str, errors: list[str]) -> ProductionGateAssessment:
    return _unsupported(
        requirement,
        tuple(errors),
        "; ".join(errors),
    )


def build_school_skirt_production_gate(
    body: BodyMeasurements,
    request: GarmentRequest,
    *,
    waist_ease: float,
    hip_ease: float,
    parameters: SchoolSkirtDraftingParameters,
) -> SchoolSkirtProductionGate:
    """Evaluate how far an A-line school-skirt request may safely proceed.

    Ease and drafting parameters are keyword-only and have no defaults here.
    Production callers therefore cannot accidentally inherit prototype defaults
    merely by omitting them.

    The function stops at readiness assessment. It never chooses front/back
    suppression targets, dart-versus-side allocation, dart distribution, dart
    placement, side-seam shape, hem shape, waistband, closure, seam allowance,
    notches, grain, or DXF serialization.
    """

    assessments: list[ProductionGateAssessment] = []

    body_errors = validate_body_measurements(body)
    request_errors = validate_garment_request(request)
    ease_errors = validate_school_skirt_spec_inputs(
        waist_ease=waist_ease,
        hip_ease=hip_ease,
    )
    parameter_errors = validate_school_skirt_parameters(parameters)

    assessments.append(
        _error_assessment("body_inputs", body_errors)
        if body_errors
        else _supported(
            "body_inputs",
            body,
            "canonical body measurements passed the existing numeric validator",
        )
    )
    assessments.append(
        _error_assessment("garment_request", request_errors)
        if request_errors
        else _supported(
            "garment_request",
            request,
            "requested skirt length passed the existing garment-request validator",
        )
    )
    assessments.append(
        _error_assessment("ease_inputs", ease_errors)
        if ease_errors
        else _supported(
            "ease_inputs",
            (waist_ease, hip_ease),
            "waist and hip ease are explicit numeric inputs and passed the style validator",
        )
    )
    assessments.append(
        _error_assessment("drafting_parameter_inputs", parameter_errors)
        if parameter_errors
        else _supported(
            "drafting_parameter_inputs",
            parameters,
            "drafting parameter values are numerically valid; this is not production provenance approval",
        )
    )

    if body_errors or request_errors or ease_errors or parameter_errors:
        return SchoolSkirtProductionGate(
            body=body,
            request=request,
            waist_ease=waist_ease,
            hip_ease=hip_ease,
            parameters=parameters,
            spec=None,
            draft=None,
            assessments=tuple(assessments),
        )

    spec = build_school_skirt_spec(
        body,
        request,
        waist_ease=waist_ease,
        hip_ease=hip_ease,
    )
    draft = build_school_skirt_draft(spec, parameters)

    draft_errors = validate_school_skirt_draft(draft)
    if draft_errors:
        assessments.append(_error_assessment("policy_independent_draft", draft_errors))
    else:
        assessments.append(
            _supported(
                "policy_independent_draft",
                draft,
                "quarter waist/hip, suppression, hip position, hem position and flare target are derived without choosing downstream geometry",
            )
        )

    constructability_errors = (
        validate_school_skirt_constructability(draft, parameters)
        if not draft_errors
        else []
    )
    if constructability_errors:
        assessments.append(
            _error_assessment("basic_constructability", constructability_errors)
        )
    elif not draft_errors:
        assessments.append(
            _supported(
                "basic_constructability",
                True,
                "current cross-layer dart-length/hip-position checks passed",
            )
        )

    # The following are deliberate blockers. Existing code contains contracts,
    # experiments and candidate geometry infrastructure, but no production-
    # approved rule should be selected merely because a candidate implementation
    # exists or a prototype parameter has a numeric value.
    assessments.extend(
        [
            _needs_rule(
                "drafting_parameter_provenance",
                parameters,
                "flare, dart counts/lengths and waistband height are explicit prototype/style parameters but are not yet approved production defaults",
                "human_or_reference_approved_flare",
                "human_or_reference_approved_dart_counts_and_lengths",
                "human_or_reference_approved_waist_finish_dimensions",
            ),
            _needs_rule(
                "panel_suppression_target_policy",
                None,
                "the global suppression requirement is known, but the production rule assigning explicit front/back panel targets is unresolved",
                "validated_front_back_panel_targets",
                "front_back_balance_provenance",
                "production_evidence_or_human_approval",
            ),
            _needs_rule(
                "suppression_allocation_policy",
                None,
                "each explicit panel target still requires an approved rule dividing it between dart intake and side shaping",
                "validated_panel_dart_vs_side_allocation",
                "production_evidence_or_human_approval",
            ),
            _needs_rule(
                "dart_distribution_policy",
                None,
                "individual dart-intake distribution has a contract but no approved equal-split or legacy fallback",
                "validated_per_dart_intakes",
            ),
            _needs_rule(
                "dart_placement_policy",
                None,
                "dart placement is intentionally semantic and has no approved equal-spacing fallback",
                "validated_normalized_dart_positions",
            ),
            _needs_rule(
                "side_seam_policy",
                None,
                "side-seam candidate infrastructure exists, but no candidate has been promoted to a production drafting rule",
                "approved_side_seam_curve_family",
                "front_back_seam_balance_rule",
                "seam_length_tolerance",
            ),
            _needs_rule(
                "hem_policy",
                None,
                "hem curvature/level remains unresolved and the historical fixed hem-dip assumption must not be reused",
                "approved_hem_curve_or_level_rule",
                "hem_allowance_rule",
            ),
            _needs_rule(
                "waist_finish_policy",
                None,
                "waistband/facing geometry, overlap and interface treatment are not production-resolved",
                "waist_finish_type",
                "finished_height",
                "overlap_or_extension",
                "waist_interface_rule",
            ),
            _needs_rule(
                "closure_policy",
                None,
                "zipper/opening location, opening length and seam treatment are unresolved",
                "closure_type",
                "closure_location",
                "opening_length_mm",
                "closure_seam_allowance_rule",
            ),
            _needs_rule(
                "material_layer_policy",
                None,
                "shell/lining/material behavior is not part of the current school-skirt arithmetic layer",
                "material_class",
                "shell_lining_requirement",
                "stretch_or_stability_assumption",
            ),
            _needs_rule(
                "production_transforms",
                None,
                "edge-specific seam allowance, semantic notches and grain constraints must be approved before factory DXF export",
                "edge_specific_seam_allowances",
                "semantic_notch_rules",
                "grain_and_cut_on_fold_rules",
            ),
        ]
    )

    return SchoolSkirtProductionGate(
        body=body,
        request=request,
        waist_ease=waist_ease,
        hip_ease=hip_ease,
        parameters=parameters,
        spec=spec,
        draft=draft,
        assessments=tuple(assessments),
    )
