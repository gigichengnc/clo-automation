"""Geometry-facing semantic inputs for school-skirt panels.

This module composes already-resolved panel spans, suppression allocation, and
semantic dart plans into scalar inputs that a later coordinate-geometry layer
may consume. It deliberately creates no points, curves, outlines, seam
allowances, or DXF entities.

``target_waist_span`` is the finished panel waist span after dart closure.
``waist_span_before_darts`` is the corresponding waist span before dart intake
is closed. Keeping both values explicit prevents later geometry from having to
reconstruct garment semantics from coordinates.

The newer explicit-span builder supports asymmetric front/back panel balance.
The historical builder remains only as a symmetric architectural compatibility
path and must not be mistaken for a production panel-balance policy.

All dimensional values use millimetres (mm).
"""

from dataclasses import dataclass

from styles.school_skirt.dart_plan import PanelDartPlan, ResolvedDart, SchoolSkirtDartPlan
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.suppression import (
    PanelSuppressionAllocation,
    SchoolSkirtSuppressionAllocation,
)


@dataclass(frozen=True)
class PanelFinishedSpans:
    """Explicit finished spans for one panel family before coordinate geometry."""

    target_waist_span: float
    hip_span: float
    hem_span: float


@dataclass(frozen=True)
class SchoolSkirtPanelFinishedSpans:
    """Explicit front/back finished spans supplied by a resolved balance method."""

    front: PanelFinishedSpans
    back: PanelFinishedSpans


@dataclass(frozen=True)
class PanelGeometryInput:
    """Resolved semantic dimensions for one panel before coordinate geometry."""

    target_waist_span: float
    waist_span_before_darts: float
    hip_span: float
    hem_span: float
    hip_position: float
    hem_position: float
    side_shaping: float
    darts: tuple[ResolvedDart, ...]


@dataclass(frozen=True)
class SchoolSkirtPanelGeometryInput:
    """Resolved front and back panel inputs for the geometry layer."""

    front: PanelGeometryInput
    back: PanelGeometryInput


def _build_panel_geometry_input(
    draft: SchoolSkirtDraft,
    spans: PanelFinishedSpans,
    allocation: PanelSuppressionAllocation,
    dart_plan: PanelDartPlan,
) -> PanelGeometryInput:
    """Compose one resolved panel without choosing coordinate geometry."""

    return PanelGeometryInput(
        target_waist_span=spans.target_waist_span,
        waist_span_before_darts=(
            spans.target_waist_span + allocation.dart_intake_total
        ),
        hip_span=spans.hip_span,
        hem_span=spans.hem_span,
        hip_position=draft.hip_position,
        hem_position=draft.hem_position,
        side_shaping=allocation.side_shaping,
        darts=dart_plan.darts,
    )


def build_school_skirt_panel_geometry_input_from_spans(
    draft: SchoolSkirtDraft,
    spans: SchoolSkirtPanelFinishedSpans,
    allocation: SchoolSkirtSuppressionAllocation,
    dart_plan: SchoolSkirtDartPlan,
) -> SchoolSkirtPanelGeometryInput:
    """Compose explicit, possibly asymmetric panel spans for later geometry.

    ``spans`` must come from an explicit balance method or experiment. This
    builder provides no equal-front/back fallback and chooses no drafting rule.
    """

    return SchoolSkirtPanelGeometryInput(
        front=_build_panel_geometry_input(
            draft, spans.front, allocation.front, dart_plan.front
        ),
        back=_build_panel_geometry_input(
            draft, spans.back, allocation.back, dart_plan.back
        ),
    )


def build_school_skirt_panel_geometry_input(
    draft: SchoolSkirtDraft,
    allocation: SchoolSkirtSuppressionAllocation,
    dart_plan: SchoolSkirtDartPlan,
) -> SchoolSkirtPanelGeometryInput:
    """Historical symmetric compatibility builder.

    This preserves the repo's earlier quarter-width geometry behavior for
    existing tests and experiments. New research/production work that permits
    asymmetric front/back balance must use
    ``build_school_skirt_panel_geometry_input_from_spans`` instead.
    """

    symmetric_spans = SchoolSkirtPanelFinishedSpans(
        front=PanelFinishedSpans(
            target_waist_span=draft.quarter_waist,
            hip_span=draft.quarter_hip,
            hem_span=draft.hem_half_width,
        ),
        back=PanelFinishedSpans(
            target_waist_span=draft.quarter_waist,
            hip_span=draft.quarter_hip,
            hem_span=draft.hem_half_width,
        ),
    )
    return build_school_skirt_panel_geometry_input_from_spans(
        draft,
        symmetric_spans,
        allocation,
        dart_plan,
    )
