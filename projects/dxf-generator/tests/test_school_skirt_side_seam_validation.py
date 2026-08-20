"""Regression tests for school-skirt side-seam policy output validation."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_policy import SideSeamGeometryInput
from styles.school_skirt.side_seam_validation import (
    validate_school_skirt_side_seam,
)


class SchoolSkirtSideSeamValidationTests(unittest.TestCase):
    def _input(self) -> SideSeamGeometryInput:
        return SideSeamGeometryInput(
            side_waist=Point2D(195.0, 0.0),
            hip_side=Point2D(225.0, -200.0),
            hem_side=Point2D(305.0, -500.0),
        )

    def test_three_semantic_anchors_form_a_valid_path(self):
        path = Path2D(
            points=(
                Point2D(195.0, 0.0),
                Point2D(225.0, -200.0),
                Point2D(305.0, -500.0),
            )
        )

        self.assertEqual(validate_school_skirt_side_seam(self._input(), path), [])

    def test_path_direction_may_be_reversed(self):
        path = Path2D(
            points=(
                Point2D(305.0, -500.0),
                Point2D(225.0, -200.0),
                Point2D(195.0, 0.0),
            )
        )

        self.assertEqual(validate_school_skirt_side_seam(self._input(), path), [])

    def test_extra_sampled_points_are_allowed_when_hip_anchor_is_explicit(self):
        path = Path2D(
            points=(
                Point2D(195.0, 0.0),
                Point2D(208.0, -90.0),
                Point2D(225.0, -200.0),
                Point2D(260.0, -350.0),
                Point2D(305.0, -500.0),
            )
        )

        self.assertEqual(validate_school_skirt_side_seam(self._input(), path), [])

    def test_hip_anchor_cannot_be_skipped(self):
        path = Path2D(
            points=(
                Point2D(195.0, 0.0),
                Point2D(230.0, -210.0),
                Point2D(305.0, -500.0),
            )
        )

        self.assertEqual(
            validate_school_skirt_side_seam(self._input(), path),
            ["side_seam path must contain hip_side as an explicit point"],
        )

    def test_endpoints_must_be_side_waist_and_hem_side(self):
        path = Path2D(
            points=(
                Point2D(190.0, 0.0),
                Point2D(225.0, -200.0),
                Point2D(305.0, -500.0),
            )
        )

        self.assertEqual(
            validate_school_skirt_side_seam(self._input(), path),
            [
                "side_seam endpoints must be side_waist and hem_side in either direction"
            ],
        )

    def test_non_finite_sample_coordinate_is_rejected(self):
        path = Path2D(
            points=(
                Point2D(195.0, 0.0),
                Point2D(math.nan, -200.0),
                Point2D(305.0, -500.0),
            )
        )

        self.assertEqual(
            validate_school_skirt_side_seam(self._input(), path),
            ["side_seam.points[1].x must be a finite number"],
        )

    def test_two_point_path_cannot_hide_the_hip_anchor(self):
        path = Path2D(
            points=(Point2D(195.0, 0.0), Point2D(305.0, -500.0))
        )

        self.assertEqual(
            validate_school_skirt_side_seam(self._input(), path),
            [
                "side_seam path must contain at least 3 points so all semantic anchors remain explicit",
                "side_seam path must contain hip_side as an explicit point",
            ],
        )


if __name__ == "__main__":
    unittest.main()
