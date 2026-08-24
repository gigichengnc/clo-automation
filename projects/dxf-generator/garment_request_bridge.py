from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class BridgeStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    NEEDS_RULE = "NEEDS_RULE"
    UNSUPPORTED = "UNSUPPORTED"


class DressSemanticSpec(Protocol):
    """Structural contract accepted from the illustration layer.

    The bridge deliberately depends on named semantics only. It never reads
    SVG/DXF coordinates, Bézier control points, drawing dimensions, or path
    geometry from the technical-flat renderer.
    """

    neckline: str
    sleeve: str
    silhouette: str
    length: str
    back_neckline: str | None
    back_closure: str | None
    front_darts: str | None
    back_darts: str | None
    front_pockets: str | None
    front_buttons: str | None
    front_princess_seams: str | None


@dataclass(frozen=True)
class FeatureAssessment:
    feature: str
    value: Any
    status: BridgeStatus
    reason: str
    required_inputs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProductionPatternRequest:
    garment_type: str
    source_contract: str
    features: tuple[FeatureAssessment, ...]

    @property
    def blockers(self) -> tuple[FeatureAssessment, ...]:
        return tuple(feature for feature in self.features if feature.status is not BridgeStatus.SUPPORTED)

    @property
    def ready_for_drafting(self) -> bool:
        return not self.blockers

    def assessment(self, feature: str) -> FeatureAssessment:
        matches = [item for item in self.features if item.feature == feature]
        if len(matches) != 1:
            raise KeyError(feature)
        return matches[0]


def _supported(feature: str, value: Any, reason: str) -> FeatureAssessment:
    return FeatureAssessment(feature, value, BridgeStatus.SUPPORTED, reason)


def _needs_rule(
    feature: str,
    value: Any,
    reason: str,
    *required_inputs: str,
) -> FeatureAssessment:
    return FeatureAssessment(
        feature,
        value,
        BridgeStatus.NEEDS_RULE,
        reason,
        tuple(required_inputs),
    )


def _unsupported(feature: str, value: Any, reason: str) -> FeatureAssessment:
    return FeatureAssessment(feature, value, BridgeStatus.UNSUPPORTED, reason)


def _optional_absence_or_rule(
    *,
    feature: str,
    value: str | None,
    supported_values: set[str],
    rule_inputs: tuple[str, ...],
    rule_reason: str,
) -> FeatureAssessment:
    if value is None:
        return _needs_rule(
            feature,
            value,
            "semantic decision is unspecified; production generation must not infer it",
            f"explicit_{feature}",
        )
    if value == "none":
        return _supported(feature, value, "explicit absence can pass through without illustration geometry")
    if value in supported_values:
        return _needs_rule(feature, value, rule_reason, *rule_inputs)
    return _unsupported(feature, value, "value is outside the current production bridge contract")


def build_production_pattern_request(spec: DressSemanticSpec) -> ProductionPatternRequest:
    """Translate illustration semantics into a strict production request.

    This function is intentionally *not* a pattern generator. It records what
    the production engine may safely accept and where validated drafting rules
    or numeric production inputs are still missing.

    No illustration coordinates are copied into this request.
    """

    features: list[FeatureAssessment] = []

    # The production architecture can represent a dress request, but a complete
    # general dress drafting implementation does not yet exist.
    features.append(
        _supported(
            "garment_type",
            "dress",
            "dress is a recognized production request envelope; this does not imply a complete dress drafter exists",
        )
    )

    # Illustration length words are categorical. Production requires a numeric
    # finished target and body/reference landmarks; SVG y-coordinates are forbidden.
    if spec.length in {"mini", "knee", "midi", "maxi"}:
        features.append(
            _needs_rule(
                "length",
                spec.length,
                "illustration length category must be resolved to a numeric finished-garment target",
                "requested_length_mm",
                "body_or_design_reference_for_length",
            )
        )
    else:
        features.append(_unsupported("length", spec.length, "unsupported production length semantic"))

    if spec.silhouette in {"a_line", "straight"}:
        features.append(
            _needs_rule(
                "silhouette",
                spec.silhouette,
                "silhouette is recognized but requires a validated production drafting family and numeric ease/flare policy",
                "body_measurements",
                "finished_ease_targets",
                "silhouette_drafting_policy",
            )
        )
    else:
        features.append(_unsupported("silhouette", spec.silhouette, "unsupported production silhouette semantic"))

    if spec.neckline in {"round", "v"}:
        features.append(
            _needs_rule(
                "front_neckline",
                spec.neckline,
                "front neckline is recognized, but general bodice neckline drafting is not yet production-validated",
                "bodice_measurements",
                "neckline_depth_width_or_policy",
            )
        )
    else:
        features.append(_unsupported("front_neckline", spec.neckline, "unsupported production neckline semantic"))

    if spec.sleeve == "sleeveless":
        features.append(
            _needs_rule(
                "sleeve",
                spec.sleeve,
                "sleeveless still requires a validated bodice armhole and finishing policy",
                "bodice_measurements",
                "armhole_drafting_policy",
                "armhole_finish_policy",
            )
        )
    elif spec.sleeve == "short":
        features.append(
            _needs_rule(
                "sleeve",
                spec.sleeve,
                "short sleeve requires validated armhole, sleeve-cap, biceps/ease and sleeve-length rules",
                "bodice_measurements",
                "armhole_drafting_policy",
                "sleeve_cap_policy",
                "sleeve_length_mm",
                "biceps_ease_target",
            )
        )
    else:
        features.append(_unsupported("sleeve", spec.sleeve, "unsupported production sleeve semantic"))

    if spec.back_neckline is None:
        features.append(
            _needs_rule(
                "back_neckline",
                None,
                "back neckline is unspecified; production generation must not copy or infer the front neckline",
                "explicit_back_neckline",
            )
        )
    elif spec.back_neckline in {"same_as_front", "shallow_round"}:
        features.append(
            _needs_rule(
                "back_neckline",
                spec.back_neckline,
                "back neckline semantic is recognized but needs validated bodice drafting dimensions/policy",
                "back_neckline_depth_width_or_policy",
            )
        )
    else:
        features.append(_unsupported("back_neckline", spec.back_neckline, "unsupported production back-neckline semantic"))

    features.append(
        _optional_absence_or_rule(
            feature="back_closure",
            value=spec.back_closure,
            supported_values={"centre_zip"},
            rule_inputs=("zipper_length_mm", "zipper_seam_allowance_policy", "closure_construction_policy"),
            rule_reason="centre-back zipper is recognized but requires validated opening length and production construction policy",
        )
    )

    features.append(
        _optional_absence_or_rule(
            feature="front_darts",
            value=spec.front_darts,
            supported_values={"waist_pair"},
            rule_inputs=("suppression_policy", "front_dart_intake", "front_dart_length", "front_dart_placement"),
            rule_reason="front waist darts require validated suppression allocation, intake, length and placement rules",
        )
    )
    features.append(
        _optional_absence_or_rule(
            feature="back_darts",
            value=spec.back_darts,
            supported_values={"waist_pair"},
            rule_inputs=("suppression_policy", "back_dart_intake", "back_dart_length", "back_dart_placement"),
            rule_reason="back waist darts require validated suppression allocation, intake, length and placement rules",
        )
    )

    features.append(
        _optional_absence_or_rule(
            feature="front_pockets",
            value=spec.front_pockets,
            supported_values={"patch_pair"},
            rule_inputs=("pocket_dimensions", "pocket_placement", "pocket_seam_allowance_policy"),
            rule_reason="patch-pocket semantics need production dimensions, placement and construction policy",
        )
    )
    features.append(
        _optional_absence_or_rule(
            feature="front_buttons",
            value=spec.front_buttons,
            supported_values={"centre_row"},
            rule_inputs=("button_count", "button_spacing", "button_size", "placket_or_overlap_policy"),
            rule_reason="centre-front buttons need count, spacing and closure/placket production rules",
        )
    )
    features.append(
        _optional_absence_or_rule(
            feature="front_princess_seams",
            value=spec.front_princess_seams,
            supported_values={"shoulder_pair"},
            rule_inputs=("bodice_measurements", "princess_shaping_policy", "seam_balance_policy"),
            rule_reason="princess seams require validated bodice shaping and paired sewing-interface rules",
        )
    )

    # Global inputs absent from the illustration contract are explicit blockers.
    features.append(
        _needs_rule(
            "body_measurements",
            None,
            "technical-flat semantics do not contain the body measurements required for production drafting",
            "waist",
            "hip",
            "bust_or_chest",
            "high_bust_if_required",
            "neck",
            "shoulder_width",
            "shoulder_slope",
            "torso_lengths",
            "waist_to_hip",
            "arm_measurements_if_sleeved",
        )
    )
    features.append(
        _needs_rule(
            "material_and_layer_system",
            None,
            "illustration semantics do not establish shell/lining/material behavior or production transforms",
            "material_class",
            "shell_lining_requirement",
            "grain_policy",
            "seam_allowance_policy",
            "notch_policy",
        )
    )

    return ProductionPatternRequest(
        garment_type="dress",
        source_contract="semantic-dress-spec-v0.1",
        features=tuple(features),
    )
