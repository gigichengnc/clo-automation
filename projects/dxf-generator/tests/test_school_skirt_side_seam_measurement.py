"""Regression tests for school-skirt side-seam length measurement."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_measurement import (
    SideSeamLengthComparison,
    compare_side_seam_lengths,
    measure_path_length,
)


class SchoolSkirtSideSeamMeasurementTests(unittest.TestCase):
    def test_polyline_length_sums_consecutive_euclidean_segments(self):
        path = Path2D(
            points=(
                Point2D(0.0, 0.0),
                Point2D(3.0, 4.0),
                Point2D(6.0, 8.0),
            )
        )

        self.assertEqual(measure_path_length(path), 10.0)

    def test_reversing_path_direction_does_not_change_length(self):
        path = Path2D(
            points=(
                Point2D(195.0, 0.0),
                Point2D(225.0, -200.0),
                Point2D(305.0, -500.0),
            )
        )
        reversed_path = Path2D(points=tuple(reversed(path.points)))

        self.assertEqual(measure_path_length(path), measure_path_length(reversed_path))

    def test_sampling_on_same_straight_line_preserves_length(self):
        unsampled = Path2D(points=(Point2D(0.0, 0.0), Point2D(6.0, 8.0)))
        sampled = Path2D(
            points=(
                Point2D(0.0, 0.0),
                Point2D(3.0, 4.0),
                Point2D(6.0, 8.0),
            )
        )

        self.assertEqual(measure_path_length(unsampled), 10.0)
        self.assertEqual(measure_path_length(sampled), 10.0)

    def test_front_back_comparison_reports_signed_and_absolute_difference(self):
        front = Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -500.0)))
        back = Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -503.0)))

        self.assertEqual(
            compare_side_seam_lengths(front, back),
            SideSeamLengthComparison(
                front_length=500.0,
                back_length=503.0,
                back_minus_front=3.0,
                absolute_difference=3.0,
            ),
        )

    def test_measurement_reports_geometry_without_applying_a_tolerance(self):
        front = Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -500.0)))
        back = Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -500.000001)))

        comparison = compare_side_seam_lengths(front, back)

        self.assertGreater(comparison.absolute_difference, 0.0)
        self.assertFalse(hasattr(comparison, "passes"))
        self.assertFalse(hasattr(comparison, "tolerance"))

    def test_short_path_safe_stops_measurement(self):
        with self.assertRaisesRegex(
            ValueError,
            "path must contain at least 2 points to measure length",
        ):
            measure_path_length(Path2D(points=(Point2D(0.0, 0.0),)))

    def test_non_finite_coordinate_safe_stops_measurement(self):
        path = Path2D(
            points=(Point2D(0.0, 0.0), Point2D(math.nan, -500.0))
        )

        with self.assertRaises(ValueError) as context:
            measure_path_length(path)

        self.assertEqual(
            str(context.exception),
            "path.points[1].x must be a finite number",
        )


if __name__ == "__main__":
    unittest.main()
