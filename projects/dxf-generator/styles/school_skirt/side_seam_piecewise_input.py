"""Composer and semantic validation for piecewise school-skirt side-seam input.

This module deterministically splits the three validated side-seam anchors into
an upper waist-to-hip segment and a lower hip-to-hem segment. It contains no
curve algorithm, sampling rule, seam allowance, or DXF behavior.

The hip anchor is the explicit shared boundary between the two segments.
All coordinates use millimetres (mm).
"""

import math

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_policy import SideSeamGeometryInput


_PIECEWISE_INPUT_TOLERANCE_MM = 1e-6


def _points_close(first: Point2D, second: Point2D) -> bool:
    return math.isclose(
        first.x,
        second.x,
        rel_tol=0.0,
        abs_tol=_PIECEWISE_INPUT_TOLERANCE_MM,
    ) and math.isclose(
        first.y,
        second.y,
        rel_tol=0.0,
        abs_tol=_PIECEWISE_INPUT_TOLERANCE_MM,
    )


def build_side_seam_piecewise_input(
    geometry_input: SideSeamGeometryInput,
) -> SideSeamPiecewiseGeometryInput:
    """Split side-waist, hip-side, and hem-side anchors into two segments."""

    return SideSeamPiecewiseGeometryInput(
        waist_to_hip=SideSeamSegmentGeometryInput(
            start=geometry_input.side_waist,
            end=geometry_input.hip_side,
        ),
        hip_to_hem=SideSeamSegmentGeometryInput(
            start=geometry_input.hip_side,
            end=geometry_input.hem_side,
        ),
    )


def validate_side_seam_piecewise_input(
    geometry_input: SideSeamGeometryInput,
    piecewise_input: SideSeamPiecewiseGeometryInput,
) -> list[str]:
    """Return semantic endpoint errors; empty means segment policies may run."""

    errors = []

    if not _points_close(piecewise_input.waist_to_hip.start, geometry_input.side_waist):
        errors.append("waist_to_hip.start must equal side_waist")

    if not _points_close(piecewise_input.waist_to_hip.end, geometry_input.hip_side):
        errors.append("waist_to_hip.end must equal hip_side")

    if not _points_close(piecewise_input.hip_to_hem.start, geometry_input.hip_side):
        errors.append("hip_to_hem.start must equal hip_side")

    if not _points_close(piecewise_input.hip_to_hem.end, geometry_input.hem_side):
        errors.append("hip_to_hem.end must equal hem_side")

    if not _points_close(
        piecewise_input.waist_to_hip.end,
        piecewise_input.hip_to_hem.start,
    ):
        errors.append("waist_to_hip.end and hip_to_hem.start must share the hip boundary")

    return errors
