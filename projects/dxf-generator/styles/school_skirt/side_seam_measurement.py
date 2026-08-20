"""Length measurement and comparison for school-skirt side-seam paths.

This module measures already-resolved ``Path2D`` geometry and reports front/back
side-seam length differences. It deliberately makes no drafting-policy choice,
sets no acceptable mismatch tolerance, and performs no pass/fail judgement.

Lengths are measured as the sum of Euclidean distances between consecutive
sampled points. Therefore the result describes the resolved polyline geometry
supplied by a curve policy; this layer does not resample or smooth it.

All coordinates and returned lengths use millimetres (mm).
"""

from dataclasses import dataclass
import math

from styles.school_skirt.geometry_output import Path2D, Point2D


@dataclass(frozen=True)
class SideSeamLengthComparison:
    """Measured front/back side-seam lengths without an acceptance decision."""

    front_length: float
    back_length: float
    back_minus_front: float
    absolute_difference: float


def _validate_point(name: str, point: Point2D) -> None:
    for axis_name, value in (("x", point.x), ("y", point.y)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name}.{axis_name} must be numeric")
        if not math.isfinite(value):
            raise ValueError(f"{name}.{axis_name} must be a finite number")


def measure_path_length(path: Path2D) -> float:
    """Return the Euclidean polyline length of one validated path."""

    if len(path.points) < 2:
        raise ValueError("path must contain at least 2 points to measure length")

    for index, point in enumerate(path.points):
        _validate_point(f"path.points[{index}]", point)

    segment_lengths = (
        math.hypot(second.x - first.x, second.y - first.y)
        for first, second in zip(path.points, path.points[1:])
    )
    return math.fsum(segment_lengths)


def compare_side_seam_lengths(
    front: Path2D,
    back: Path2D,
) -> SideSeamLengthComparison:
    """Measure front/back paths and report their signed and absolute difference."""

    front_length = measure_path_length(front)
    back_length = measure_path_length(back)
    back_minus_front = back_length - front_length

    return SideSeamLengthComparison(
        front_length=front_length,
        back_length=back_length,
        back_minus_front=back_minus_front,
        absolute_difference=abs(back_minus_front),
    )
