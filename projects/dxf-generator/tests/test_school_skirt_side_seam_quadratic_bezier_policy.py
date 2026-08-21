"""Regression tests for the explicit quadratic Bezier side-seam research policy."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_linear_policy import (
    LinearSideSeamSegmentPolicy,
)
from styles.school_skirt.side_seam_multi_policy_runner import (
    SideSeamPolicyCandidateSpec,
    run_side_seam_policy_candidates,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SchoolSkirtSideSeamPiecewiseStrategy,
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_quadratic_bezier_policy import (
    QuadraticBezierSideSeamSegmentPolicy,
)
from styles.school_skirt.side_seam_segment_output import (
    validate_side_seam_segment_output,
)


class FixedControlPointRule:
    def __init__(self, point: Point2D):
        self.point = point
        self.calls = []

    def resolve(self, geometry_input: SideSeamSegmentGeometryInput) -> Point2D:
        self.calls.append(geometry_input)
        return self.point


class MidpointOffsetControlPointRule:
    def __init__(self, offset_x: float):
        self.offset_x = offset_x

    def resolve(self, geometry_input: SideSeamSegmentGeometryInput) -> Point2D:
        return Point2D(
            x=(geometry_input.start.x + geometry_input.end.x) / 2.0 + self.offset_x,
            y=(geometry_input.start.y + geometry_input.end.y) / 2.0,
        )


class SchoolSkirtSideSeamQuadraticBezierPolicyTests(unittest.TestCase):
    def _piecewise_input(
        self,
        *,
        upper_length: float,
        lower_length: float,
    ) -> SideSeamPiecewiseGeometryInput:
        side_waist = Point2D(0.0, 0.0)
        hip_side = Point2D(0.0, -upper_length)
        hem_side = Point2D(0.0, -(upper_length + lower_length))
        return SideSeamPiecewiseGeometryInput(
            waist_to_hip=SideSeamSegmentGeometryInput(side_waist, hip_side),
            hip_to_hem=SideSeamSegmentGeometryInput(hip_side, hem_side),
        )

    def test_three_samples_match_known_quadratic_bezier_points(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
        )
        policy = QuadraticBezierSideSeamSegmentPolicy(
            control_point_rule=FixedControlPointRule(Point2D(5.0, 10.0)),
            sample_count=3,
        )

        path = policy.build(segment)

        self.assertEqual(
            path,
            Path2D(
                points=(
                    segment.start,
                    Point2D(5.0, 5.0),
                    segment.end,
                )
            ),
        )

    def test_sample_count_is_total_points_and_exact_anchor_objects_are_preserved(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(2.0, 3.0),
            end=Point2D(12.0, -7.0),
        )
        policy = QuadraticBezierSideSeamSegmentPolicy(
            control_point_rule=FixedControlPointRule(Point2D(9.0, 4.0)),
            sample_count=5,
        )

        path = policy.build(segment)

        self.assertEqual(len(path.points), 5)
        self.assertIs(path.points[0], segment.start)
        self.assertIs(path.points[-1], segment.end)

    def test_control_point_rule_is_explicit_and_receives_the_segment(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(0.0, -200.0),
        )
        rule = FixedControlPointRule(Point2D(10.0, -100.0))
        policy = QuadraticBezierSideSeamSegmentPolicy(
            control_point_rule=rule,
            sample_count=5,
        )

        policy.build(segment)

        self.assertEqual(rule.calls, [segment])

    def test_sample_count_requires_an_integer_of_at_least_three(self):
        rule = FixedControlPointRule(Point2D(0.0, 0.0))

        with self.assertRaisesRegex(ValueError, "sample_count must be at least 3"):
            QuadraticBezierSideSeamSegmentPolicy(rule, 2)

        with self.assertRaisesRegex(ValueError, "sample_count must be an integer"):
            QuadraticBezierSideSeamSegmentPolicy(rule, True)

        with self.assertRaisesRegex(ValueError, "sample_count must be an integer"):
            QuadraticBezierSideSeamSegmentPolicy(rule, 3.5)

    def test_non_finite_control_point_safe_stops_before_curve_sampling(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(0.0, -200.0),
        )
        policy = QuadraticBezierSideSeamSegmentPolicy(
            control_point_rule=FixedControlPointRule(Point2D(math.nan, -100.0)),
            sample_count=5,
        )

        with self.assertRaises(ValueError) as context:
            policy.build(segment)

        self.assertEqual(
            str(context.exception),
            "quadratic_bezier.control.x must be a finite number",
        )

    def test_sampled_output_passes_existing_segment_output_contract(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(195.0, 0.0),
            end=Point2D(225.0, -200.0),
        )
        policy = QuadraticBezierSideSeamSegmentPolicy(
            control_point_rule=MidpointOffsetControlPointRule(offset_x=12.0),
            sample_count=7,
        )

        path = policy.build(segment)

        self.assertEqual(validate_side_seam_segment_output(segment, path), [])

    def test_quadratic_candidate_integrates_with_multi_policy_comparison(self):
        front = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        back = self._piecewise_input(upper_length=203.0, lower_length=299.0)
        linear_strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=LinearSideSeamSegmentPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )
        quadratic_strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=QuadraticBezierSideSeamSegmentPolicy(
                control_point_rule=MidpointOffsetControlPointRule(offset_x=12.0),
                sample_count=9,
            ),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        evaluation = run_side_seam_policy_candidates(
            front_input=front,
            back_input=back,
            candidates=(
                SideSeamPolicyCandidateSpec("linear-baseline", linear_strategy),
                SideSeamPolicyCandidateSpec("quadratic-research-a", quadratic_strategy),
            ),
        )

        self.assertEqual(
            tuple(row.candidate_id for row in evaluation.snapshot.rows),
            ("linear-baseline", "quadratic-research-a"),
        )
        linear_upper = evaluation.snapshot.rows[0].waist_to_hip.back_minus_front
        quadratic_upper = evaluation.snapshot.rows[1].waist_to_hip.back_minus_front
        self.assertEqual(linear_upper, 3.0)
        self.assertNotEqual(quadratic_upper, linear_upper)


if __name__ == "__main__":
    unittest.main()
