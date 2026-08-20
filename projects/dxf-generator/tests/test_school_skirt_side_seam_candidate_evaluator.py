"""Regression tests for school-skirt side-seam candidate evaluation composition."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_candidate_evaluator import (
    evaluate_side_seam_candidate,
)


class SchoolSkirtSideSeamCandidateEvaluatorTests(unittest.TestCase):
    def _vertical_path(self, length: float) -> Path2D:
        return Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -length)))

    def test_evaluator_builds_named_result_from_four_segment_paths(self):
        result = evaluate_side_seam_candidate(
            candidate_id="linear-baseline",
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(203.0),
            back_hip_to_hem=self._vertical_path(299.0),
        )

        self.assertEqual(result.candidate_id, "linear-baseline")
        self.assertEqual(result.report.waist_to_hip.back_minus_front, 3.0)
        self.assertEqual(result.report.hip_to_hem.back_minus_front, -1.0)
        self.assertEqual(result.report.total.back_minus_front, 2.0)

    def test_evaluator_preserves_signed_and_absolute_segment_measurements(self):
        result = evaluate_side_seam_candidate(
            candidate_id="future-curve-a",
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(198.5),
            back_hip_to_hem=self._vertical_path(302.5),
        )

        self.assertEqual(result.report.waist_to_hip.back_minus_front, -1.5)
        self.assertEqual(result.report.waist_to_hip.absolute_difference, 1.5)
        self.assertEqual(result.report.hip_to_hem.back_minus_front, 2.5)
        self.assertEqual(result.report.hip_to_hem.absolute_difference, 2.5)
        self.assertEqual(result.report.total.back_minus_front, 1.0)
        self.assertEqual(result.report.total.absolute_difference, 1.0)

    def test_invalid_candidate_id_is_rejected_by_named_result_contract(self):
        with self.assertRaisesRegex(
            ValueError,
            "candidate_id must not contain leading or trailing whitespace",
        ):
            evaluate_side_seam_candidate(
                candidate_id=" linear-baseline ",
                front_waist_to_hip=self._vertical_path(200.0),
                front_hip_to_hem=self._vertical_path(300.0),
                back_waist_to_hip=self._vertical_path(200.0),
                back_hip_to_hem=self._vertical_path(300.0),
            )

    def test_invalid_path_is_rejected_by_measurement_layer(self):
        with self.assertRaisesRegex(
            ValueError,
            "path must contain at least 2 points to measure length",
        ):
            evaluate_side_seam_candidate(
                candidate_id="future-curve-a",
                front_waist_to_hip=Path2D(points=(Point2D(0.0, 0.0),)),
                front_hip_to_hem=self._vertical_path(300.0),
                back_waist_to_hip=self._vertical_path(200.0),
                back_hip_to_hem=self._vertical_path(300.0),
            )

    def test_evaluator_output_contains_measurements_not_selection_policy(self):
        result = evaluate_side_seam_candidate(
            candidate_id="future-curve-b",
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(201.0),
            back_hip_to_hem=self._vertical_path(300.0),
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
