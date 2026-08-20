"""Regression tests for school-skirt side-seam candidate measurement reports."""

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


class SchoolSkirtSideSeamCandidateReportTests(unittest.TestCase):
    def _vertical_path(self, length: float) -> Path2D:
        return Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -length)))

    def test_report_localizes_upper_lower_and_total_differences(self):
        report = build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(203.0),
            back_hip_to_hem=self._vertical_path(299.0),
        )

        self.assertEqual(report.waist_to_hip.front_length, 200.0)
        self.assertEqual(report.waist_to_hip.back_length, 203.0)
        self.assertEqual(report.waist_to_hip.back_minus_front, 3.0)
        self.assertEqual(report.waist_to_hip.absolute_difference, 3.0)

        self.assertEqual(report.hip_to_hem.front_length, 300.0)
        self.assertEqual(report.hip_to_hem.back_length, 299.0)
        self.assertEqual(report.hip_to_hem.back_minus_front, -1.0)
        self.assertEqual(report.hip_to_hem.absolute_difference, 1.0)

        self.assertEqual(report.total.front_length, 500.0)
        self.assertEqual(report.total.back_length, 502.0)
        self.assertEqual(report.total.back_minus_front, 2.0)
        self.assertEqual(report.total.absolute_difference, 2.0)

    def test_total_signed_difference_equals_sum_of_segment_differences(self):
        report = build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(180.0),
            front_hip_to_hem=self._vertical_path(320.0),
            back_waist_to_hip=self._vertical_path(184.5),
            back_hip_to_hem=self._vertical_path(318.5),
        )

        self.assertEqual(
            report.total.back_minus_front,
            report.waist_to_hip.back_minus_front + report.hip_to_hem.back_minus_front,
        )

    def test_report_can_show_mismatch_is_only_in_upper_segment(self):
        report = build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(203.0),
            back_hip_to_hem=self._vertical_path(300.0),
        )

        self.assertEqual(report.waist_to_hip.absolute_difference, 3.0)
        self.assertEqual(report.hip_to_hem.absolute_difference, 0.0)
        self.assertEqual(report.total.absolute_difference, 3.0)

    def test_report_contains_measurements_only_not_acceptance_policy(self):
        report = build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(200.001),
            back_hip_to_hem=self._vertical_path(300.0),
        )

        for comparison in (
            report.waist_to_hip,
            report.hip_to_hem,
            report.total,
        ):
            self.assertFalse(hasattr(comparison, "passes"))
            self.assertFalse(hasattr(comparison, "tolerance"))


if __name__ == "__main__":
    unittest.main()
