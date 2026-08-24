from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from numbers import Real
from typing import Any


class SkirtGateStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    NEEDS_RULE = "NEEDS_RULE"
    UNSUPPORTED = "UNSUPPORTED"


def _finite_number(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(name: str, value: Any) -> float:
    result = _finite_number(name, value)
    if result <= 0:
        raise ValueError(f"{name} must be > 0")
    return result


def _nonnegative(name: str, value: Any) -> float:
    result = _finite_number(name, value)
    if result < 0:
        raise ValueError(f"{name} must be >= 0")
    return result


@dataclass(frozen=True)
class SkirtBodyMeasurements:
    """Body measurements required by the first A-line skirt pilot.

    All values are millimetres. Garment length deliberately does not live here:
    it is a design/finished-garment target rather than a body measurement.
    """

    waist_mm: float
    hip_mm: float
    waist_to_hip_mm: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "waist_mm", _positive("waist_mm", self.waist_mm))
        object.__setattr__(self, "hip_mm", _positive("hip_mm", self.hip_mm))
        object.__setattr__(self, "waist_to_hip_mm", _positive("waist_to_hip_mm", self.waist_to_hip_mm))


@dataclass(frozen=True)
class SkirtFinishedTargets:
    """Finished-garment targets for the narrow A-line pilot.

    Ease is explicit and may be negative for future stretch-material workflows,
    but the resulting finished circumference must remain positive. Flare is an
    explicit style target per quarter-body allocation; it is not inferred from
    an illustration coordinate or a legacy pattern constant.
    """

    length_mm: float
    waist_ease_mm: float
    hip_ease_mm: float
    flare_per_quarter_mm: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "length_mm", _positive("length_mm", self.length_mm))
        object.__setattr__(self, "waist_ease_mm", _finite_number("waist_ease_mm", self.waist_ease_mm))
        object.__setattr__(self, "hip_ease_mm", _finite_number("hip_ease_mm", self.hip_ease_mm))
        object.__setattr__(
            self,
            "flare_per_quarter_mm",
            _nonnegative("flare_per_quarter_mm", self.flare_per_quarter_mm),
        )


@dataclass(frozen=True)
class ALineSkirtInputs:
    body: SkirtBodyMeasurements
    targets: SkirtFinishedTargets

    def __post_init__(self) -> None:
        if self.finished_waist_mm <= 0:
            raise ValueError("finished waist must be > 0 after ease")
        if self.finished_hip_mm <= 0:
            raise ValueError("finished hip must be > 0 after ease")

    @property
    def finished_waist_mm(self) -> float:
        return self.body.waist_mm + self.targets.waist_ease_mm

    @property
    def finished_hip_mm(self) -> float:
        return self.body.hip_mm + self.targets.hip_ease_mm

    @property
    def quarter_waist_mm(self) -> float:
        return self.finished_waist_mm / 4.0

    @property
    def quarter_hip_mm(self) -> float:
        return self.finished_hip_mm / 4.0

    @property
    def quarter_suppression_mm(self) -> float:
        return self.quarter_hip_mm - self.quarter_waist_mm

    @property
    def quarter_hem_target_mm(self) -> float:
        """Width target at hem for a simple quarter-allocation A-line family.

        This is a style target, not a solved side-seam or hem curve length.
        """
        return self.quarter_hip_mm + self.targets.flare_per_quarter_mm


@dataclass(frozen=True)
class ALineSkirtPolicy:
    """Production policies that must be explicit before geometry may be drafted.

    Values are semantic names only. No policy is implemented merely because it
    is named here; the gate below records whether a validated implementation is
    currently available.
    """

    panel_allocation: str | None = None
    suppression_policy: str | None = None
    side_seam_policy: str | None = None
    hem_policy: str | None = None
    waist_finish: str | None = None
    closure_policy: str | None = None
    material_class: str | None = None
    seam_allowance_policy: str | None = None
    notch_policy: str | None = None
    grain_policy: str | None = None


@dataclass(frozen=True)
class SkirtGateAssessment:
    requirement: str
    value: Any
    status: SkirtGateStatus
    reason: str
    required_inputs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ALineSkirtDraftRequest:
    inputs: ALineSkirtInputs
    policy: ALineSkirtPolicy
    assessments: tuple[SkirtGateAssessment, ...]
    source_contract: str = "a-line-skirt-production-request-v0.1"

    @property
    def blockers(self) -> tuple[SkirtGateAssessment, ...]:
        return tuple(item for item in self.assessments if item.status is not SkirtGateStatus.SUPPORTED)

    @property
    def ready_for_geometry(self) -> bool:
        return not self.blockers

    def assessment(self, requirement: str) -> SkirtGateAssessment:
        matches = [item for item in self.assessments if item.requirement == requirement]
        if len(matches) != 1:
            raise KeyError(requirement)
        return matches[0]


def _supported(requirement: str, value: Any, reason: str) -> SkirtGateAssessment:
    return SkirtGateAssessment(requirement, value, SkirtGateStatus.SUPPORTED, reason)


def _needs_rule(
    requirement: str,
    value: Any,
    reason: str,
    *required_inputs: str,
) -> SkirtGateAssessment:
    return SkirtGateAssessment(
        requirement,
        value,
        SkirtGateStatus.NEEDS_RULE,
        reason,
        tuple(required_inputs),
    )


def _unsupported(requirement: str, value: Any, reason: str) -> SkirtGateAssessment:
    return SkirtGateAssessment(requirement, value, SkirtGateStatus.UNSUPPORTED, reason)


def _named_policy(
    requirement: str,
    value: str | None,
    *,
    reason: str,
    required_inputs: tuple[str, ...],
) -> SkirtGateAssessment:
    if value is None:
        return _needs_rule(
            requirement,
            None,
            "production policy is unspecified; geometry generation must not infer one",
            f"explicit_{requirement}",
        )
    return _needs_rule(requirement, value, reason, *required_inputs)


def build_a_line_skirt_draft_request(
    inputs: ALineSkirtInputs,
    policy: ALineSkirtPolicy | None = None,
) -> ALineSkirtDraftRequest:
    """Create the first production-safe A-line skirt drafting request.

    The function deliberately stops before pattern geometry. It proves the
    measurement/ease arithmetic that is already well-defined, then exposes all
    unresolved drafting and production policies as blockers.

    It contains no legacy fixed hip-add, hip-depth, skirt-length, dart-intake,
    hem-dip or waistband constants.
    """

    policy = policy or ALineSkirtPolicy()
    assessments: list[SkirtGateAssessment] = []

    assessments.append(
        _supported(
            "body_measurements",
            inputs.body,
            "waist, hip and waist-to-hip are explicit validated body inputs",
        )
    )
    assessments.append(
        _supported(
            "finished_waist",
            inputs.finished_waist_mm,
            "finished waist is derived exactly once as body waist + explicit waist ease",
        )
    )
    assessments.append(
        _supported(
            "finished_hip",
            inputs.finished_hip_mm,
            "finished hip is derived exactly once as body hip + explicit hip ease",
        )
    )
    assessments.append(
        _supported(
            "garment_length",
            inputs.targets.length_mm,
            "garment length is an explicit finished target rather than a body-derived legacy assumption",
        )
    )
    assessments.append(
        _supported(
            "flare_target",
            inputs.targets.flare_per_quarter_mm,
            "flare is an explicit style target; no illustration coordinate or legacy constant is reused",
        )
    )

    if inputs.quarter_suppression_mm < 0:
        assessments.append(
            _unsupported(
                "suppression_domain",
                inputs.quarter_suppression_mm,
                "current fitted A-line suppression model does not support finished waist larger than finished hip",
            )
        )
    else:
        assessments.append(
            _supported(
                "quarter_suppression",
                inputs.quarter_suppression_mm,
                "quarter suppression is the mathematical difference quarter_hip - quarter_waist",
            )
        )

    assessments.append(
        _named_policy(
            "panel_allocation",
            policy.panel_allocation,
            reason="panel allocation is a drafting policy; the current repo has not validated a production implementation for this pilot",
            required_inputs=("panel_count", "front_back_allocation", "cut_on_fold_policy"),
        )
    )
    assessments.append(
        _named_policy(
            "suppression_policy",
            policy.suppression_policy,
            reason="suppression must be allocated between darts, side shaping and any other shaping using a validated policy",
            required_inputs=("dart_count", "dart_intakes", "dart_lengths", "dart_positions", "side_shaping_allocation"),
        )
    )
    assessments.append(
        _named_policy(
            "side_seam_policy",
            policy.side_seam_policy,
            reason="side-seam curve construction and front/back balance remain unresolved production rules",
            required_inputs=("side_curve_family", "front_back_balance", "seam_length_tolerance"),
        )
    )
    assessments.append(
        _named_policy(
            "hem_policy",
            policy.hem_policy,
            reason="hem curve/level policy is unresolved; the engine must not reuse the historical 12 mm dip assumption",
            required_inputs=("hem_curve_family", "hem_level_reference", "hem_allowance_policy"),
        )
    )
    assessments.append(
        _named_policy(
            "waist_finish",
            policy.waist_finish,
            reason="waistband/facing geometry and overlap are unresolved production rules",
            required_inputs=("waist_finish_type", "finished_height", "overlap_or_extension", "interface_length_policy"),
        )
    )
    assessments.append(
        _named_policy(
            "closure_policy",
            policy.closure_policy,
            reason="zipper/opening location, length and seam treatment require explicit validated construction rules",
            required_inputs=("closure_type", "closure_location", "opening_length_mm", "zipper_seam_allowance_policy"),
        )
    )
    assessments.append(
        _named_policy(
            "material_class",
            policy.material_class,
            reason="material behavior is needed before ease, lining, grain and construction choices can be production-approved",
            required_inputs=("woven_or_knit", "stretch_behavior", "shell_lining_requirement"),
        )
    )
    assessments.append(
        _named_policy(
            "seam_allowance_policy",
            policy.seam_allowance_policy,
            reason="production seam allowance must be edge-specific and validated, not a whole-piece legacy constant",
            required_inputs=("edge_specific_allowances", "corner_join_policy", "hem_allowance"),
        )
    )
    assessments.append(
        _named_policy(
            "notch_policy",
            policy.notch_policy,
            reason="notches must be tied to semantic sewing interfaces and construction needs",
            required_inputs=("semantic_notch_locations", "notch_type_policy"),
        )
    )
    assessments.append(
        _named_policy(
            "grain_policy",
            policy.grain_policy,
            reason="grain direction and allowed rotation are production constraints and remain explicit policy inputs",
            required_inputs=("grain_direction", "cut_on_fold", "nap_or_directional_constraint"),
        )
    )

    return ALineSkirtDraftRequest(
        inputs=inputs,
        policy=policy,
        assessments=tuple(assessments),
    )
