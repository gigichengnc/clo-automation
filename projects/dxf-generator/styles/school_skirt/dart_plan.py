"""Resolved semantic dart plan for the school-skirt drafting layer.

This module combines already-resolved dart intake, normalized placement, and
panel dart length into the semantic records that later geometry may consume.
It does not choose suppression, distribute intake, place darts, calculate
coordinates, or generate DXF geometry.

The order of a panel's distribution and placement tuples defines dart identity.
Each resolved dart therefore carries an explicit ``dart_index`` so that identity
is preserved when the plan crosses into later geometry and adapter layers.

All dimensional values use millimetres (mm). ``center_fraction`` is
unitless.
"""

from dataclasses import dataclass

from styles.school_skirt.dart_distribution import SchoolSkirtDartDistribution
from styles.school_skirt.dart_placement import SchoolSkirtDartPlacement
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


@dataclass(frozen=True)
class ResolvedDart:
    """One policy-resolved dart before coordinate geometry."""

    dart_index: int
    intake: float
    center_fraction: float
    length: float


@dataclass(frozen=True)
class PanelDartPlan:
    """Resolved semantic darts for one panel."""

    darts: tuple[ResolvedDart, ...]


@dataclass(frozen=True)
class SchoolSkirtDartPlan:
    """Resolved front and back semantic dart plans."""

    front: PanelDartPlan
    back: PanelDartPlan


def _build_panel_dart_plan(
    dart_intakes: tuple[float, ...],
    center_fractions: tuple[float, ...],
    dart_length: float,
) -> PanelDartPlan:
    """Pair validated per-dart semantics without making drafting decisions."""

    if len(dart_intakes) != len(center_fractions):
        raise ValueError(
            "validated dart distribution and placement must contain matching counts"
        )

    return PanelDartPlan(
        darts=tuple(
            ResolvedDart(
                dart_index=index,
                intake=intake,
                center_fraction=center_fraction,
                length=dart_length,
            )
            for index, (intake, center_fraction) in enumerate(
                zip(dart_intakes, center_fractions)
            )
        )
    )


def build_school_skirt_dart_plan(
    distribution: SchoolSkirtDartDistribution,
    placement: SchoolSkirtDartPlacement,
    parameters: SchoolSkirtDraftingParameters,
) -> SchoolSkirtDartPlan:
    """Compose validated dart semantics into a geometry-facing plan."""

    return SchoolSkirtDartPlan(
        front=_build_panel_dart_plan(
            distribution.front.dart_intakes,
            tuple(dart.center_fraction for dart in placement.front.darts),
            parameters.front_dart_length,
        ),
        back=_build_panel_dart_plan(
            distribution.back.dart_intakes,
            tuple(dart.center_fraction for dart in placement.back.darts),
            parameters.back_dart_length,
        ),
    )
