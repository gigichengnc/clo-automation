"""Explicit opt-in linear side-seam segment policy for school-skirt baselines.

This module provides a deliberately simple reference implementation of the
``SchoolSkirtSideSeamSegmentGeometryPolicy`` contract. It connects the supplied
semantic segment anchors with one straight two-point path.

It is not a production default and is not registered implicitly anywhere. It
exists only as an explicit baseline/reference policy for tests, diagnostics,
and later comparison against real drafting curves.

The policy performs no smoothing, interpolation, sampling, legacy sine shaping,
seam allowance, or DXF behavior. All coordinates use millimetres (mm).
"""

from styles.school_skirt.geometry_output import Path2D
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamSegmentGeometryInput,
)


class LinearSideSeamSegmentPolicy:
    """Connect one side-seam segment's semantic anchors with a straight path."""

    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        """Return exactly the supplied start and end anchors, in that order."""

        return Path2D(points=(geometry_input.start, geometry_input.end))
