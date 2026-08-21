"""Regression tests for named quadratic Bezier side-seam research runs."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
)
from styles.school_skirt.side_seam_named_quadratic_runner import (
    run_named_quadratic_candidates,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
    SchoolSkirtQuadraticBezierStrategyParameters,
)


class SchoolSkirtSideSeamNamedQuadraticRunnerTests(unittest.TestCase):
    def _parameters(
        self,
        *,
        upper_offset: float,
        lower_offset: float = 0.0,
        upper_samples: int = 7,
        lower_samples: int = 7,
    ) -> SchoolSkirtQuadraticBezierStrategyParameters:
        return SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=upper_offset,
                sample_count=upper_samples,
            ),
            hip_to_hem=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=lower_offset,
                sample_count=lower_samples,
            ),
        )

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

    def _inputs(self):
        return (
            self._piecewise_input(upper_length=200.0, lower_length=300.0),
            self._piecewise_input(upper_length=203.0, lower_length=299.0),
        )

    def test_named_runner_preserves_candidate_order_in_collection_and_snapshot(self):
        front, back = self._inputs()
        candidates = (
            NamedQuadraticCandidateSpec(
                "quadratic-research-a",
                self._parameters(upper_offset=8.0),
            ),
            NamedQuadraticCandidateSpec(
                "quadratic-research-b",
                self._parameters(upper_offset=20.0),
            ),
        )

        evaluation = run_named_quadratic_candidates(
            front_input=front,
            back_input=back,
            candidates=candidates,
        )

        self.assertEqual(
            tuple(candidate.candidate_id for candidate in evaluation.collection.candidates),
            ("quadratic-research-a", "quadratic-research-b"),
        )
        self.assertEqual(
            tuple(row.candidate_id for row in evaluation.snapshot.rows),
            ("quadratic-research-a", "quadratic-research-b"),
        )

    def test_distinct_named_parameter_configs_produce_distinct_measurements(self):
        front, back = self._inputs()

        evaluation = run_named_quadratic_candidates(
            front_input=front,
            back_input=back,
            candidates=(
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(upper_offset=8.0),
                ),
                NamedQuadraticCandidateSpec(
                    "quadratic-research-b",
                    self._parameters(upper_offset=20.0),
                ),
            ),
        )

        first = evaluation.snapshot.rows[0].waist_to_hip.back_minus_front
        second = evaluation.snapshot.rows[1].waist_to_hip.back_minus_front
        self.assertTrue(math.isfinite(first))
        self.assertTrue(math.isfinite(second))
        self.assertNotEqual(first, second)

    def test_duplicate_candidate_id_safe_stops_via_existing_collection_contract(self):
        front, back = self._inputs()

        with self.assertRaisesRegex(
            ValueError,
            "duplicate side-seam candidate_id: quadratic-research-a",
        ):
            run_named_quadratic_candidates(
                front_input=front,
                back_input=back,
                candidates=(
                    NamedQuadraticCandidateSpec(
                        "quadratic-research-a",
                        self._parameters(upper_offset=8.0),
                    ),
                    NamedQuadraticCandidateSpec(
                        "quadratic-research-a",
                        self._parameters(upper_offset=20.0),
                    ),
                ),
            )

    def test_invalid_parameters_safe_stop_via_existing_quadratic_factory(self):
        front, back = self._inputs()

        with self.assertRaisesRegex(ValueError, "sample_count must be at least 3"):
            run_named_quadratic_candidates(
                front_input=front,
                back_input=back,
                candidates=(
                    NamedQuadraticCandidateSpec(
                        "quadratic-research-a",
                        self._parameters(upper_offset=8.0, upper_samples=2),
                    ),
                ),
            )

    def test_invalid_candidate_id_safe_stops_via_existing_named_result_pipeline(self):
        front, back = self._inputs()

        with self.assertRaisesRegex(
            ValueError,
            "candidate_id must not contain leading or trailing whitespace",
        ):
            run_named_quadratic_candidates(
                front_input=front,
                back_input=back,
                candidates=(
                    NamedQuadraticCandidateSpec(
                        " quadratic-research-a ",
                        self._parameters(upper_offset=8.0),
                    ),
                ),
            )

    def test_empty_named_candidates_build_empty_collection_and_snapshot(self):
        front, back = self._inputs()

        evaluation = run_named_quadratic_candidates(
            front_input=front,
            back_input=back,
            candidates=(),
        )

        self.assertEqual(evaluation.collection.candidates, ())
        self.assertEqual(evaluation.snapshot.rows, ())

    def test_named_runner_result_contains_data_not_selection_policy(self):
        front, back = self._inputs()

        evaluation = run_named_quadratic_candidates(
            front_input=front,
            back_input=back,
            candidates=(
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(upper_offset=8.0),
                ),
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
