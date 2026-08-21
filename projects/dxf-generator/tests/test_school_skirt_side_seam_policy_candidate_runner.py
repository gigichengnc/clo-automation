"""Regression tests for explicit school-skirt side-seam policy candidate runs."""

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
from styles.school_skirt.side_seam_piecewise_policy import (
    SchoolSkirtSideSeamPiecewiseStrategy,
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_policy_candidate_runner import (
    run_side_seam_policy_candidate,
)


class RecordingLinearPolicy:
    def __init__(self):
        self.calls = []

    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        self.calls.append(geometry_input)
        return Path2D(points=(geometry_input.start, geometry_input.end))


class BrokenEndPolicy:
    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        return Path2D(
            points=(
                geometry_input.start,
                Point2D(geometry_input.end.x + 1.0, geometry_input.end.y),
            )
        )


class SchoolSkirtSideSeamPolicyCandidateRunnerTests(unittest.TestCase):
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

    def test_explicit_linear_strategy_generates_and_evaluates_candidate(self):
        strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=LinearSideSeamSegmentPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        result = run_side_seam_policy_candidate(
            candidate_id="linear-baseline",
            front_input=self._piecewise_input(upper_length=200.0, lower_length=300.0),
            back_input=self._piecewise_input(upper_length=203.0, lower_length=299.0),
            strategy=strategy,
        )

        self.assertEqual(result.candidate_id, "linear-baseline")
        self.assertEqual(result.report.waist_to_hip.back_minus_front, 3.0)
        self.assertEqual(result.report.hip_to_hem.back_minus_front, -1.0)
        self.assertEqual(result.report.total.back_minus_front, 2.0)

    def test_upper_and_lower_policies_are_each_used_for_front_and_back(self):
        upper_policy = RecordingLinearPolicy()
        lower_policy = RecordingLinearPolicy()
        strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=upper_policy,
            hip_to_hem_policy=lower_policy,
        )
        front = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        back = self._piecewise_input(upper_length=203.0, lower_length=299.0)

        run_side_seam_policy_candidate(
            candidate_id="recording-reference",
            front_input=front,
            back_input=back,
            strategy=strategy,
        )

        self.assertEqual(upper_policy.calls, [front.waist_to_hip, back.waist_to_hip])
        self.assertEqual(lower_policy.calls, [front.hip_to_hem, back.hip_to_hem])

    def test_invalid_policy_output_safe_stops_before_measurement(self):
        strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=BrokenEndPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "waist_to_hip: side_seam segment endpoints must equal its semantic start and end",
        ):
            run_side_seam_policy_candidate(
                candidate_id="broken-policy",
                front_input=self._piecewise_input(
                    upper_length=200.0,
                    lower_length=300.0,
                ),
                back_input=self._piecewise_input(
                    upper_length=200.0,
                    lower_length=300.0,
                ),
                strategy=strategy,
            )

    def test_broken_piecewise_hip_boundary_safe_stops_via_join_contract(self):
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        broken = SideSeamPiecewiseGeometryInput(
            waist_to_hip=valid.waist_to_hip,
            hip_to_hem=SideSeamSegmentGeometryInput(
                start=Point2D(1.0, -200.0),
                end=valid.hip_to_hem.end,
            ),
        )
        strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=LinearSideSeamSegmentPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "piecewise side seam segments must share the same hip boundary",
        ):
            run_side_seam_policy_candidate(
                candidate_id="broken-input",
                front_input=broken,
                back_input=valid,
                strategy=strategy,
            )

    def test_invalid_candidate_id_is_delegated_to_named_result_contract(self):
        strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=LinearSideSeamSegmentPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)

        with self.assertRaisesRegex(
            ValueError,
            "candidate_id must not contain leading or trailing whitespace",
        ):
            run_side_seam_policy_candidate(
                candidate_id=" linear-baseline ",
                front_input=valid,
                back_input=valid,
                strategy=strategy,
            )

    def test_runner_output_contains_measurements_not_selection_policy(self):
        strategy = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=LinearSideSeamSegmentPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)

        result = run_side_seam_policy_candidate(
            candidate_id="future-curve-a",
            front_input=valid,
            back_input=valid,
            strategy=strategy,
        )

        for attribute in (
            "rank",
            "score",
            "winner",
            "selected",
            "tolerance",
            "passes",
            "is_production",
        ):
            self.assertFalse(hasattr(result, attribute))


if __name__ == "__main__":
    unittest.main()
