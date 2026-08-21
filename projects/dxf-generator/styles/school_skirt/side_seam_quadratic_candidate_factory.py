"""Parameter specs and factory for quadratic Bezier side-seam research strategies.

This module stores reproducible research parameters for the upper and lower
school-skirt side-seam segments, then explicitly composes those parameters into
the existing chord-relative control-point rule and sampled quadratic Bezier
segment policy.

It defines no default parameter values, preferred skirt curve, candidate
ranking, production policy, seam allowance, or DXF behavior. Parameter
validation remains owned by the existing control-point and quadratic-policy
contracts when the factory builds a strategy.
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_chord_relative_control_point import (
    ChordRelativeBezierControlPointRule,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SchoolSkirtSideSeamPiecewiseStrategy,
)
from styles.school_skirt.side_seam_quadratic_bezier_policy import (
    QuadraticBezierSideSeamSegmentPolicy,
)


@dataclass(frozen=True)
class QuadraticBezierSegmentParameters:
    """Explicit reproducible research parameters for one side-seam segment."""

    along_fraction: float
    normal_offset: float
    sample_count: int


@dataclass(frozen=True)
class SchoolSkirtQuadraticBezierStrategyParameters:
    """Explicit upper and lower parameter sets for one piecewise strategy."""

    waist_to_hip: QuadraticBezierSegmentParameters
    hip_to_hem: QuadraticBezierSegmentParameters


def _build_segment_policy(
    parameters: QuadraticBezierSegmentParameters,
) -> QuadraticBezierSideSeamSegmentPolicy:
    return QuadraticBezierSideSeamSegmentPolicy(
        control_point_rule=ChordRelativeBezierControlPointRule(
            along_fraction=parameters.along_fraction,
            normal_offset=parameters.normal_offset,
        ),
        sample_count=parameters.sample_count,
    )


def build_quadratic_bezier_side_seam_strategy(
    parameters: SchoolSkirtQuadraticBezierStrategyParameters,
) -> SchoolSkirtSideSeamPiecewiseStrategy:
    """Build one explicit quadratic research strategy from pure parameter data."""

    return SchoolSkirtSideSeamPiecewiseStrategy(
        waist_to_hip_policy=_build_segment_policy(parameters.waist_to_hip),
        hip_to_hem_policy=_build_segment_policy(parameters.hip_to_hem),
    )
