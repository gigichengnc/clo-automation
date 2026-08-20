"""Piecewise side-seam geometry strategy contract for school-skirt panels.

This module separates the semantic side seam into two independent curve
segments: waist-to-hip and hip-to-hem. The shared hip anchor is the explicit
boundary between them.

It deliberately provides no curve implementation, no legacy sine formula, no
Bezier or linear fallback, no sampling-density rule, and no DXF behavior.
Different explicit segment policies may be supplied for the upper and lower
side-seam regions.

All coordinates use millimetres (mm).
"""

from dataclasses import dataclass
from typing import Protocol

from styles.school_skirt.geometry_output import Path2D, Point2D


@dataclass(frozen=True)
class SideSeamSegmentGeometryInput:
    """Semantic start and end anchors for one side-seam curve segment."""

    start: Point2D
    end: Point2D


@dataclass(frozen=True)
class SideSeamPiecewiseGeometryInput:
    """Explicit upper and lower side-seam segments sharing the hip boundary."""

    waist_to_hip: SideSeamSegmentGeometryInput
    hip_to_hem: SideSeamSegmentGeometryInput


class SchoolSkirtSideSeamSegmentGeometryPolicy(Protocol):
    """Contract implemented by one explicit side-seam segment algorithm."""

    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        """Return one semantic curve segment between the supplied anchors."""
        ...


@dataclass(frozen=True)
class SchoolSkirtSideSeamPiecewiseStrategy:
    """Explicit policies used for the upper and lower side-seam segments."""

    waist_to_hip_policy: SchoolSkirtSideSeamSegmentGeometryPolicy
    hip_to_hem_policy: SchoolSkirtSideSeamSegmentGeometryPolicy
