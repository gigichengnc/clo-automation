"""Side-seam geometry policy contract for school-skirt panels.

This module defines the narrow semantic input and protocol for a future
school-skirt side-seam geometry implementation. It deliberately provides no
curve algorithm, no linear fallback, no sine or Bezier formula, no sampling
rule, and no DXF behavior.

The policy receives only the three side-seam anchors required to construct the
semantic edge: side waist, hip side, and hem side. It does not receive centre
edge, waist, dart, seam-allowance, or adapter data.

All coordinates use millimetres (mm).
"""

from dataclasses import dataclass
from typing import Protocol

from styles.school_skirt.geometry_output import Path2D, Point2D


@dataclass(frozen=True)
class SideSeamGeometryInput:
    """The three semantic anchors available to a side-seam geometry policy."""

    side_waist: Point2D
    hip_side: Point2D
    hem_side: Point2D


class SchoolSkirtSideSeamGeometryPolicy(Protocol):
    """Contract implemented by an explicit school-skirt side-seam policy."""

    def build(self, geometry_input: SideSeamGeometryInput) -> Path2D:
        """Return one semantic side-seam path through the supplied anchors."""
        ...
