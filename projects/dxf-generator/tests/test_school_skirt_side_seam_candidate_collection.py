"""Regression tests for school-skirt side-seam candidate collections."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_candidate_collection import (
    SideSeamCandidateCollection,
)
from styles.school_skirt.side_seam_candidate_report import (
    build_side_seam_candidate_measurement_report,
)
from styles.school_skirt.side_seam_candidate_result import (
    NamedSideSeamCandidateResult,
)


class SchoolSkirtSideSeamCandidateCollectionTests(unittest.TestCase):
    def _vertical_path(self, length: float) -> Path2D:
        return Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -length)))

    def _report(self, upper_back: float = 203.0):
        return build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(upper_back),
            back_hip_to_hem=self._vertical_path(299.0),
        )

    def test_distinct_candidates_preserve_supplied_order_without_ranking(self):
        linear = NamedSideSeamCandidateResult("linear-baseline", self._report())
        legacy = NamedSideSeamCandidateResult("legacy-reference", self._report(204.0))
        future = NamedSideSeamCandidateResult("future-curve-a", self._report(202.0))

        collection = SideSeamCandidateCollection((linear, legacy, future))

        self.assertEqual(collection.candidates, (linear, legacy, future))

    def test_duplicate_candidate_id_is_rejected_even_when_reports_differ(self):
        first = NamedSideSeamCandidateResult("linear-baseline", self._report())
        second = NamedSideSeamCandidateResult("linear-baseline", self._report(205.0))

        with self.assertRaisesRegex(
            ValueError,
            "duplicate side-seam candidate_id: linear-baseline",
        ):
            SideSeamCandidateCollection((first, second))

    def test_same_measurement_report_can_exist_under_distinct_candidate_ids(self):
        report = self._report()
        linear = NamedSideSeamCandidateResult("linear-baseline", report)
        reference = NamedSideSeamCandidateResult("legacy-reference", report)

        collection = SideSeamCandidateCollection((linear, reference))

        self.assertEqual(len(collection.candidates), 2)
        self.assertIs(collection.candidates[0].report, report)
        self.assertIs(collection.candidates[1].report, report)

    def test_empty_collection_is_allowed_without_imposing_comparison_set_size(self):
        collection = SideSeamCandidateCollection(())

        self.assertEqual(collection.candidates, ())

    def test_collection_contains_storage_not_selection_policy(self):
        collection = SideSeamCandidateCollection(
            (NamedSideSeamCandidateResult("future-curve-a", self._report()),)
        )

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
            self.assertFalse(hasattr(collection, attribute))


if __name__ == "__main__":
    unittest.main()
