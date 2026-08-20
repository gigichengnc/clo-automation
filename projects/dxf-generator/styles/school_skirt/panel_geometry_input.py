"""Geometry-facing semantic inputs for school-skirt panels.

This module composes already-resolved draft values, suppression allocation, and
semantic dart plans into the scalar inputs that a later coordinate-geometry
layer may consume. It deliberately creates no points, curves, outlines, seam
allowances, or DXF entities.

``target_waist_span`` is the finished panel waist span after dart closure.
``waist_span_before_darts`` is the corresponding waist span before dart intake
is closed. Keeping both values explicit prevents later geometry from having to
reconstruct garment semantics from coordinates.

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
    allocation: PanelSuppressionAllocation,
    dart_plan: PanelDartPlan,
) -> PanelGeometryInput:
    """Compose one validated panel without choosing coordinate geometry."""

    return PanelGeometryInput(
        target_waist_span=draft.quarter_waist,
        waist_span_before_darts=(
            draft.quarter_waist + allocation.dart_intake_total
        ),
        hip_span=draft.quarter_hip,
        hem_span=draft.hem_half_width,
        hip_position=draft.hip_position,
        hem_position=draft.hem_position,
        side_shaping=allocation.side_shaping,
        darts=dart_plan.darts,
    )


def build_school_skirt_panel_geometry_input(
    draft: SchoolSkirtDraft,
    allocation: SchoolSkirtSuppressionAllocation,
    dart_plan: SchoolSkirtDartPlan,
) -> SchoolSkirtPanelGeometryInput:
    """Compose validated school-skirt semantics for a later geometry layer."""

    return SchoolSkirtPanelGeometryInput(
        front=_build_panel_geometry_input(draft, allocation.front, dart_plan.front),
        back=_build_panel_geometry_input(draft, allocation.back, dart_plan.back),
    )
