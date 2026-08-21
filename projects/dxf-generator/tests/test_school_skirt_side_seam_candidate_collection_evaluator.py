"""Regression tests for school-skirt side-seam candidate collection evaluation."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_candidate_collection_evaluator import (
    SideSeamCandidateCollectionEvaluation,
    SideSeamCandidatePathSet,
    evaluate_side_seam_candidate_collection,
)


class SchoolSkirtSideSeamCandidateCollectionEvaluatorTests(unittest.TestCase):
    def _vertical_path(self, length: float) -> Path2D:
        return Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -length)))

    def _candidate(
        self,
        candidate_id: str,
        *,
        upper_back: float,
        lower_back: float,
    ) -> SideSeamCandidatePathSet:
        return SideSeamCandidatePathSet(
            candidate_id=candidate_id,
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(upper_back),
            back_hip_to_hem=self._vertical_path(lower_back),
        )

    def test_collection_evaluator_preserves_order_and_builds_snapshot(self):
        evaluation = evaluate_side_seam_candidate_collection(
            (
                self._candidate(
                    "linear-baseline", upper_back=203.0, lower_back=299.0
                ),
                self._candidate(
                    "legacy-reference", upper_back=204.0, lower_back=301.0
                ),
                self._candidate(
                    "future-curve-a", upper_back=201.0, lower_back=300.0
                ),
            )
        )

        self.assertEqual(
            tuple(candidate.candidate_id for candidate in evaluation.collection.candidates),
            ("linear-baseline", "legacy-reference", "future-curve-a"),
        )
        self.assertEqual(
            tuple(row.candidate_id for row in evaluation.snapshot.rows),
            ("linear-baseline", "legacy-reference", "future-curve-a"),
        )

        linear_row = evaluation.snapshot.rows[0]
        self.assertEqual(linear_row.waist_to_hip.back_minus_front, 3.0)
        self.assertEqual(linear_row.hip_to_hem.back_minus_front, -1.0)
        self.assertEqual(linear_row.total.back_minus_front, 2.0)

    def test_duplicate_candidate_id_safe_stops_via_collection_contract(self):
        with self.assertRaisesRegex(
            ValueError,
            "duplicate side-seam candidate_id: linear-baseline",
        ):
            evaluate_side_seam_candidate_collection(
                (
                    self._candidate(
                        "linear-baseline", upper_back=203.0, lower_back=299.0
                    ),
                    self._candidate(
                        "linear-baseline", upper_back=205.0, lower_back=300.0
                    ),
                )
            )

    def test_invalid_path_safe_stops_via_measurement_layer(self):
        invalid = SideSeamCandidatePathSet(
            candidate_id="future-curve-a",
            front_waist_to_hip=Path2D(points=(Point2D(0.0, 0.0),)),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(200.0),
            back_hip_to_hem=self._vertical_path(300.0),
        )

        with self.assertRaisesRegex(
            ValueError,
            "path must contain at least 2 points to measure length",
        ):
            evaluate_side_seam_candidate_collection((invalid,))

    def test_empty_input_builds_empty_collection_and_snapshot(self):
        evaluation = evaluate_side_seam_candidate_collection(())

        self.assertEqual(evaluation.collection.candidates, ())
        self.assertEqual(evaluation.snapshot.rows, ())

    def test_collection_evaluation_contains_data_not_selection_policy(self):
        evaluation = evaluate_side_seam_candidate_collection(
            (
                self._candidate(
                    "future-curve-b", upper_back=201.0, lower_back=300.0
                ),
            )
        )

        self.assertIsInstance(evaluation, SideSeamCandidateCollectionEvaluation)
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
