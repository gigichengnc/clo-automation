"""Regression tests for named school-skirt side-seam candidate results."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_candidate_report import (
    build_side_seam_candidate_measurement_report,
)
from styles.school_skirt.side_seam_candidate_result import (
    NamedSideSeamCandidateResult,
)


class SchoolSkirtSideSeamCandidateResultTests(unittest.TestCase):
    def _vertical_path(self, length: float) -> Path2D:
        return Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -length)))

    def _report(self):
        return build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(203.0),
            back_hip_to_hem=self._vertical_path(299.0),
        )

    def test_candidate_id_is_bound_to_the_exact_measurement_report(self):
        report = self._report()

        result = NamedSideSeamCandidateResult(
            candidate_id="linear-baseline",
            report=report,
        )

        self.assertEqual(result.candidate_id, "linear-baseline")
        self.assertIs(result.report, report)

    def test_same_measurements_can_remain_distinct_by_candidate_identity(self):
        report = self._report()

        linear = NamedSideSeamCandidateResult("linear-baseline", report)
        reference = NamedSideSeamCandidateResult("legacy-reference", report)

        self.assertNotEqual(linear, reference)
        self.assertEqual(linear.report, reference.report)
        self.assertNotEqual(linear.candidate_id, reference.candidate_id)

    def test_empty_candidate_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "candidate_id must not be empty"):
            NamedSideSeamCandidateResult("", self._report())

    def test_leading_or_trailing_whitespace_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "candidate_id must not contain leading or trailing whitespace",
        ):
            NamedSideSeamCandidateResult(" linear-baseline ", self._report())

    def test_non_string_candidate_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "candidate_id must be a string"):
            NamedSideSeamCandidateResult(123, self._report())

    def test_named_result_contains_identity_and_measurements_not_selection_policy(self):
        result = NamedSideSeamCandidateResult("future-curve-a", self._report())

        for attribute in (
            "rank",
            "score",
            "passes",
            "tolerance",
            "selected",
            "is_production",
        ):
            self.assertFalse(hasattr(result, attribute))


if __name__ == "__main__":
    unittest.main()
