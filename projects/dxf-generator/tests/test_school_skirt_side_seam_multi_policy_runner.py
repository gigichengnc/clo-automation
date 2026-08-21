"""Regression tests for explicit school-skirt side-seam multi-policy runs."""

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


class MidpointDetourPolicy:
    def __init__(self, offset: float):
        self.offset = offset

    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        midpoint = Point2D(
            (geometry_input.start.x + geometry_input.end.x) / 2.0 + self.offset,
            (geometry_input.start.y + geometry_input.end.y) / 2.0,
        )
        return Path2D(
            points=(geometry_input.start, midpoint, geometry_input.end)
        )


class BrokenEndPolicy:
    def build(self, geometry_input: SideSeamSegmentGeometryInput) -> Path2D:
        return Path2D(
            points=(
                geometry_input.start,
                Point2D(geometry_input.end.x + 1.0, geometry_input.end.y),
            )
        )


class SchoolSkirtSideSeamMultiPolicyRunnerTests(unittest.TestCase):
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

    def _linear_strategy(self) -> SchoolSkirtSideSeamPiecewiseStrategy:
        return SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=LinearSideSeamSegmentPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

    def test_multiple_explicit_strategies_share_geometry_and_preserve_order(self):
        front = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        back = self._piecewise_input(upper_length=203.0, lower_length=299.0)
        detour = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=MidpointDetourPolicy(offset=10.0),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        evaluation = run_side_seam_policy_candidates(
            front_input=front,
            back_input=back,
            candidates=(
                SideSeamPolicyCandidateSpec("linear-baseline", self._linear_strategy()),
                SideSeamPolicyCandidateSpec("future-curve-a", detour),
            ),
        )

        self.assertEqual(
            tuple(candidate.candidate_id for candidate in evaluation.collection.candidates),
            ("linear-baseline", "future-curve-a"),
        )
        self.assertEqual(
            tuple(row.candidate_id for row in evaluation.snapshot.rows),
            ("linear-baseline", "future-curve-a"),
        )

    def test_distinct_strategies_produce_distinct_measured_upper_mismatch(self):
        front = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        back = self._piecewise_input(upper_length=203.0, lower_length=299.0)
        detour = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=MidpointDetourPolicy(offset=10.0),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        evaluation = run_side_seam_policy_candidates(
            front_input=front,
            back_input=back,
            candidates=(
                SideSeamPolicyCandidateSpec("linear-baseline", self._linear_strategy()),
                SideSeamPolicyCandidateSpec("future-curve-a", detour),
            ),
        )

        linear_upper = evaluation.snapshot.rows[0].waist_to_hip.back_minus_front
        detour_upper = evaluation.snapshot.rows[1].waist_to_hip.back_minus_front
        expected_detour = 2.0 * (
            math.hypot(10.0, 101.5) - math.hypot(10.0, 100.0)
        )

        self.assertEqual(linear_upper, 3.0)
        self.assertAlmostEqual(detour_upper, expected_detour)
        self.assertNotEqual(detour_upper, linear_upper)

    def test_duplicate_candidate_id_safe_stops_via_collection_contract(self):
        front = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        back = self._piecewise_input(upper_length=203.0, lower_length=299.0)

        with self.assertRaisesRegex(
            ValueError,
            "duplicate side-seam candidate_id: linear-baseline",
        ):
            run_side_seam_policy_candidates(
                front_input=front,
                back_input=back,
                candidates=(
                    SideSeamPolicyCandidateSpec(
                        "linear-baseline", self._linear_strategy()
                    ),
                    SideSeamPolicyCandidateSpec(
                        "linear-baseline", self._linear_strategy()
                    ),
                ),
            )

    def test_bad_policy_output_safe_stops_via_single_policy_runner(self):
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        broken = SchoolSkirtSideSeamPiecewiseStrategy(
            waist_to_hip_policy=BrokenEndPolicy(),
            hip_to_hem_policy=LinearSideSeamSegmentPolicy(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "waist_to_hip: side_seam segment endpoints must equal its semantic start and end",
        ):
            run_side_seam_policy_candidates(
                front_input=valid,
                back_input=valid,
                candidates=(SideSeamPolicyCandidateSpec("broken-policy", broken),),
            )

    def test_empty_candidate_specs_build_empty_collection_and_snapshot(self):
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)

        evaluation = run_side_seam_policy_candidates(
            front_input=valid,
            back_input=valid,
            candidates=(),
        )

        self.assertEqual(evaluation.collection.candidates, ())
        self.assertEqual(evaluation.snapshot.rows, ())

    def test_multi_policy_result_contains_comparison_data_not_selection_policy(self):
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)

        evaluation = run_side_seam_policy_candidates(
            front_input=valid,
            back_input=valid,
            candidates=(
                SideSeamPolicyCandidateSpec("linear-baseline", self._linear_strategy()),
            ),
        )

        for target in (evaluation, evaluation.collection, evaluation.snapshot):
            for attribute in (
                "rank",
                "ranking",
                "score",
                "winner",
                "selected",
                "tolerance",
                "passes",
                "is_production",
            ):
                self.assertFalse(hasattr(target, attribute))


if __name__ == "__main__":
    unittest.main()
