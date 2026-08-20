"""Straight centre-edge geometry for school-skirt panels.

This module is the first concrete coordinate primitive in the school-skirt
geometry layer. It connects the canonical centre-waist and centre-hem anchors
with one straight semantic path.

It does not create waist geometry, side seams, hem curves, darts, seam
allowances, or DXF entities. No sampling-density or curve policy is involved.
All coordinates use millimetres (mm).
"""

from styles.school_skirt.geometry_output import Path2D
from styles.school_skirt.panel_anchors import (
    PanelAnchorPoints,
    SchoolSkirtPanelAnchors,
)


def build_panel_centre_edge(anchors: PanelAnchorPoints) -> Path2D:
    """Return the straight centre edge from waist to hem for one panel."""

    return Path2D(points=(anchors.centre_waist, anchors.centre_hem))


def build_school_skirt_centre_edges(
    anchors: SchoolSkirtPanelAnchors,
) -> tuple[Path2D, Path2D]:
    """Return front and back centre-edge paths in that order."""

    return (
        build_panel_centre_edge(anchors.front),
        build_panel_centre_edge(anchors.back),
    )
