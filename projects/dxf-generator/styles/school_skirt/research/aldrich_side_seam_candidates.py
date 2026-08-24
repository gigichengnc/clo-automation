"""Research-only side-seam curve candidates for Aldrich skirt semantics.

This module compares three explicit curve interpretations against the same
source-faithful Aldrich research pattern inputs:

- ``linear_reference``: two straight segments through the semantic hip anchor;
- ``single_quadratic_5mm``: one quadratic Bezier from waist to hem with a
  5 mm maximum chord-normal outward deviation; this candidate does not force
  passage through the semantic hip anchor;
- ``piecewise_quadratic_5mm``: a quadratic waist-to-hip segment with a 5 mm
  maximum chord-normal outward deviation, followed by a linear hip-to-hem
  segment, preserving the semantic hip anchor.

The source instruction to curve the side seam outward by 5 mm does not uniquely
specify a mathematical curve family. These are therefore named research
interpretations only. No candidate is ranked or selected, and no seam allowance,
notches, grain, closure, material rule, DXF, or factory output is produced.

All coordinates and lengths use millimetres (mm).
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.panel_anchors import (
    PanelAnchorPoints,
    build_school_skirt_panel_anchors,
)
from styles.school_skirt.research.aldrich_pattern_semantics import (
    AldrichResearchPatternSemantics,
)
from styles.school_skirt.side_seam_chord_relative_control_point import (
    ChordRelativeBezierControlPointRule,
)
from styles.school_skirt.side_seam_linear_policy import LinearSideSeamSegmentPolicy
from styles.school_skirt.side_seam_measurement import measure_path_length
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_quadratic_bezier_policy import (
    QuadraticBezierSideSeamSegmentPolicy,
)


ALDRICH_RESEARCH_OUTWARD_DEVIATION_MM = 5.0
# For a quadratic Bezier whose control point is at the chord midpoint, the
# midpoint curve displacement is half the control-point normal offset.
ALDRICH_RESEARCH_CONTROL_NORMAL_OFFSET_MM = 2.0 * ALDRICH_RESEARCH_OUTWARD_DEVIATION_MM
ALDRICH_RESEARCH_SAMPLE_COUNT = 101


@dataclass(frozen=True)
class SideSeamCurveMetrics:
    length: float
    max_chord_normal_deviation: float
    hip_anchor_error: float
    hip_anchor_preserved: bool
    hip_join_gap: float | None
    hip_tangent_angle_degrees: float | None


@dataclass(frozen=True)
class PanelSideSeamCurveCandidate:
    path: Path2D
    metrics: SideSeamCurveMetrics


@dataclass(frozen=True)
class AldrichSideSeamCurveCandidate:
    name: str
    front: PanelSideSeamCurveCandidate
    back: PanelSideSeamCurveCandidate
    back_minus_front_length: float
    absolute_length_difference: float
    interpretation: str
    status: str = "RESEARCH_CURVE_CANDIDATE"
    production_status: str = "NOT_FACTORY_READY"


@dataclass(frozen=True)
class AldrichSideSeamCurveComparison:
    candidates: tuple[AldrichSideSeamCurveCandidate, ...]
    source_instruction: str = "curve the side seam outward by 5 mm"
    status: str = "RESEARCH_CURVE_COMPARISON"
    production_status: str = "NO_PRODUCTION_SELECTION"


def _distance(first: Point2D, second: Point2D) -> float:
    return math.hypot(second.x - first.x, second.y - first.y)


def _combine(first: Path2D, second: Path2D) -> Path2D:
    if not first.points or not second.points:
        raise ValueError("side-seam segments must contain points")
    if _distance(first.points[-1], second.points[0]) > 1e-6:
        raise ValueError("piecewise side-seam segments must share an endpoint")
    return Path2D(points=(*first.points, *second.points[1:]))


def _point_to_chord_signed_normal_distance(
    point: Point2D,
    start: Point2D,
    end: Point2D,
) -> float:
    dx = end.x - start.x
    dy = end.y - start.y
    chord_length = math.hypot(dx, dy)
    if chord_length == 0.0:
        raise ValueError("side-seam chord must have non-zero length")
    left_normal_x = -dy / chord_length
    left_normal_y = dx / chord_length
    return (
        (point.x - start.x) * left_normal_x
        + (point.y - start.y) * left_normal_y
    )


def _max_chord_normal_deviation(
    path: Path2D,
    segments: tuple[tuple[Point2D, Point2D, int, int], ...],
) -> float:
    """Return maximum positive left-normal deviation across indexed path regions."""

    deviations: list[float] = []
    for start, end, start_index, end_index in segments:
        deviations.extend(
            _point_to_chord_signed_normal_distance(point, start, end)
            for point in path.points[start_index : end_index + 1]
        )
    return max(deviations, default=0.0)


def _min_point_distance(path: Path2D, target: Point2D) -> float:
    return min(_distance(point, target) for point in path.points)


def _vector_angle_degrees(
    first: tuple[float, float],
    second: tuple[float, float],
) -> float:
    first_length = math.hypot(*first)
    second_length = math.hypot(*second)
    if first_length == 0.0 or second_length == 0.0:
        raise ValueError("tangent vectors must have non-zero length")
    cosine = (
        first[0] * second[0] + first[1] * second[1]
    ) / (first_length * second_length)
    cosine = max(-1.0, min(1.0, cosine))
    return math.degrees(math.acos(cosine))


def _piecewise_join_metrics(
    upper: Path2D,
    lower: Path2D,
) -> tuple[float, float]:
    gap = _distance(upper.points[-1], lower.points[0])
    upper_tangent = (
        upper.points[-1].x - upper.points[-2].x,
        upper.points[-1].y - upper.points[-2].y,
    )
    lower_tangent = (
        lower.points[1].x - lower.points[0].x,
        lower.points[1].y - lower.points[0].y,
    )
    return gap, _vector_angle_degrees(upper_tangent, lower_tangent)


def _linear_reference(anchors: PanelAnchorPoints) -> PanelSideSeamCurveCandidate:
    linear = LinearSideSeamSegmentPolicy()
    upper = linear.build(
        SideSeamSegmentGeometryInput(start=anchors.side_waist, end=anchors.hip_side)
    )
    lower = linear.build(
        SideSeamSegmentGeometryInput(start=anchors.hip_side, end=anchors.hem_side)
    )
    path = _combine(upper, lower)
    gap, angle = _piecewise_join_metrics(upper, lower)
    return PanelSideSeamCurveCandidate(
        path=path,
        metrics=SideSeamCurveMetrics(
            length=measure_path_length(path),
            max_chord_normal_deviation=0.0,
            hip_anchor_error=_min_point_distance(path, anchors.hip_side),
            hip_anchor_preserved=True,
            hip_join_gap=gap,
            hip_tangent_angle_degrees=angle,
        ),
    )


def _quadratic_policy() -> QuadraticBezierSideSeamSegmentPolicy:
    return QuadraticBezierSideSeamSegmentPolicy(
        control_point_rule=ChordRelativeBezierControlPointRule(
            along_fraction=0.5,
            normal_offset=ALDRICH_RESEARCH_CONTROL_NORMAL_OFFSET_MM,
        ),
        sample_count=ALDRICH_RESEARCH_SAMPLE_COUNT,
    )


def _single_quadratic(anchors: PanelAnchorPoints) -> PanelSideSeamCurveCandidate:
    path = _quadratic_policy().build(
        SideSeamSegmentGeometryInput(start=anchors.side_waist, end=anchors.hem_side)
    )
    return PanelSideSeamCurveCandidate(
        path=path,
        metrics=SideSeamCurveMetrics(
            length=measure_path_length(path),
            max_chord_normal_deviation=_max_chord_normal_deviation(
                path,
                ((anchors.side_waist, anchors.hem_side, 0, len(path.points) - 1),),
            ),
            hip_anchor_error=_min_point_distance(path, anchors.hip_side),
            hip_anchor_preserved=_min_point_distance(path, anchors.hip_side) <= 1e-6,
            hip_join_gap=None,
            hip_tangent_angle_degrees=None,
        ),
    )


def _piecewise_quadratic(anchors: PanelAnchorPoints) -> PanelSideSeamCurveCandidate:
    upper = _quadratic_policy().build(
        SideSeamSegmentGeometryInput(start=anchors.side_waist, end=anchors.hip_side)
    )
    lower = LinearSideSeamSegmentPolicy().build(
        SideSeamSegmentGeometryInput(start=anchors.hip_side, end=anchors.hem_side)
    )
    path = _combine(upper, lower)
    gap, angle = _piecewise_join_metrics(upper, lower)
    upper_end_index = len(upper.points) - 1
    return PanelSideSeamCurveCandidate(
        path=path,
        metrics=SideSeamCurveMetrics(
            length=measure_path_length(path),
            max_chord_normal_deviation=_max_chord_normal_deviation(
                path,
                (
                    (anchors.side_waist, anchors.hip_side, 0, upper_end_index),
                    (
                        anchors.hip_side,
                        anchors.hem_side,
                        upper_end_index,
                        len(path.points) - 1,
                    ),
                ),
            ),
            hip_anchor_error=_min_point_distance(path, anchors.hip_side),
            hip_anchor_preserved=True,
            hip_join_gap=gap,
            hip_tangent_angle_degrees=angle,
        ),
    )


def _pair_candidate(
    name: str,
    front: PanelSideSeamCurveCandidate,
    back: PanelSideSeamCurveCandidate,
    interpretation: str,
) -> AldrichSideSeamCurveCandidate:
    difference = back.metrics.length - front.metrics.length
    return AldrichSideSeamCurveCandidate(
        name=name,
        front=front,
        back=back,
        back_minus_front_length=difference,
        absolute_length_difference=abs(difference),
        interpretation=interpretation,
    )


def compare_aldrich_side_seam_curve_candidates(
    semantics: AldrichResearchPatternSemantics,
) -> AldrichSideSeamCurveComparison:
    """Build three non-ranked side-seam research candidates for front/back panels."""

    if not semantics.semantic_inputs_valid:
        raise ValueError("Aldrich research pattern semantics must validate first")

    anchors = build_school_skirt_panel_anchors(semantics.geometry_input)

    linear_front = _linear_reference(anchors.front)
    linear_back = _linear_reference(anchors.back)
    single_front = _single_quadratic(anchors.front)
    single_back = _single_quadratic(anchors.back)
    piecewise_front = _piecewise_quadratic(anchors.front)
    piecewise_back = _piecewise_quadratic(anchors.back)

    return AldrichSideSeamCurveComparison(
        candidates=(
            _pair_candidate(
                "linear_reference",
                linear_front,
                linear_back,
                "two straight segments through the semantic hip anchor",
            ),
            _pair_candidate(
                "single_quadratic_5mm",
                single_front,
                single_back,
                "one waist-to-hem quadratic with 5 mm maximum chord-normal deviation; hip passage is not constrained",
            ),
            _pair_candidate(
                "piecewise_quadratic_5mm",
                piecewise_front,
                piecewise_back,
                "5 mm waist-to-hip quadratic plus linear hip-to-hem segment; semantic hip anchor is preserved",
            ),
        )
    )
