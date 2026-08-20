"""Canonical anchor points for school-skirt panel coordinate geometry.

This module maps validated ``PanelGeometryInput`` scalars into a small set of
policy-independent Cartesian anchors. It does not create side-seam curves, hem
curves, dart geometry, sampled paths, seam allowances, or DXF entities.

The canonical drafting frame is:
- centre waist is the origin ``(0, 0)``;
- positive x runs from the centre edge toward the side seam;
- negative y runs from the waist toward the hem.

``side_waist`` uses the pre-dart waist span because dart openings are resolved
later within the waist path. All coordinates use millimetres (mm).
"""

from dataclasses import dataclass

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.panel_geometry_input import (
    PanelGeometryInput,
    SchoolSkirtPanelGeometryInput,
)


@dataclass(frozen=True)
class PanelAnchorPoints:
    """Five semantic anchors for one panel before curve construction."""

    centre_waist: Point2D
    centre_hem: Point2D
    side_waist: Point2D
    hip_side: Point2D
    hem_side: Point2D


@dataclass(frozen=True)
class SchoolSkirtPanelAnchors:
    """Canonical front and back panel anchors."""

    front: PanelAnchorPoints
    back: PanelAnchorPoints


def _build_panel_anchors(panel: PanelGeometryInput) -> PanelAnchorPoints:
    """Map one validated semantic panel input into canonical anchors."""

    return PanelAnchorPoints(
        centre_waist=Point2D(0.0, 0.0),
        centre_hem=Point2D(0.0, -panel.hem_position),
        side_waist=Point2D(panel.waist_span_before_darts, 0.0),
        hip_side=Point2D(panel.hip_span, -panel.hip_position),
        hem_side=Point2D(panel.hem_span, -panel.hem_position),
    )


def build_school_skirt_panel_anchors(
    geometry_input: SchoolSkirtPanelGeometryInput,
) -> SchoolSkirtPanelAnchors:
    """Build canonical anchors without choosing any curve or dart geometry."""

    return SchoolSkirtPanelAnchors(
        front=_build_panel_anchors(geometry_input.front),
        back=_build_panel_anchors(geometry_input.back),
    )
