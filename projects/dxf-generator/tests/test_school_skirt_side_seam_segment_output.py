"""Regression tests for piecewise school-skirt side-seam segment output."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_segment_output import (
    join_side_seam_piecewise_output,
    validate_side_seam_segment_output,
)


class SchoolSkirtSideSeamSegmentOutputTests(unittest.TestCase):
    def _piecewise_input(self) -> SideSeamPiecewiseGeometryInput:
        side_waist = Point2D(195.0, 0.0)
        hip_side = Point2D(225.0, -200.0)
        hem_side = Point2D(305.0, -500.0)
        return SideSeamPiecewiseGeometryInput(
            waist_to_hip=SideSeamSegmentGeometryInput(side_waist, hip_side),
            hip_to_hem=SideSeamSegmentGeometryInput(hip_side, hem_side),
        )

    def test_valid_sampled_segments_join_with_one_hip_point(self):
        geometry_input = self._piecewise_input()
        upper = Path2D(
            points=(
                Point2D(195.0, 0.0),
                Point2D(205.0, -90.0),
                Point2D(225.0, -200.0),
            )
        )
        lower = Path2D(
            points=(
                Point2D(225.0, -200.0),
                Point2D(260.0, -350.0),
                Point2D(305.0, -500.0),
            )
        )

        joined = join_side_seam_piecewise_output(geometry_input, upper, lower)

        self.assertEqual(
            joined,
            Path2D(
                points=(
                    Point2D(195.0, 0.0),
                    Point2D(205.0, -90.0),
                    Point2D(225.0, -200.0),
                    Point2D(260.0, -350.0),
                    Point2D(305.0, -500.0),
                )
            ),
        )
        self.assertEqual(joined.points.count(Point2D(225.0, -200.0)), 1)

    def test_reversed_segment_outputs_are_oriented_before_joining(self):
        geometry_input = self._piecewise_input()
        upper = Path2D(
            points=(
                Point2D(225.0, -200.0),
                Point2D(205.0, -90.0),
                Point2D(195.0, 0.0),
            )
        )
        lower = Path2D(
            points=(
                Point2D(305.0, -500.0),
                Point2D(260.0, -350.0),
                Point2D(225.0, -200.0),
            )
        )

        joined = join_side_seam_piecewise_output(geometry_input, upper, lower)

        self.assertEqual(joined.points[0], Point2D(195.0, 0.0))
        self.assertEqual(joined.points[2], Point2D(225.0, -200.0))
        self.assertEqual(joined.points[-1], Point2D(305.0, -500.0))

    def test_segment_endpoint_mismatch_is_rejected(self):
        segment_input = SideSeamSegmentGeometryInput(
            start=Point2D(195.0, 0.0),
            end=Point2D(225.0, -200.0),
        )
        path = Path2D(
            points=(Point2D(194.0, 0.0), Point2D(225.0, -200.0))
        )

        self.assertEqual(
            validate_side_seam_segment_output(segment_input, path),
            ["side_seam segment endpoints must equal its semantic start and end"],
        )

    def test_non_finite_segment_coordinate_is_rejected(self):
        segment_input = SideSeamSegmentGeometryInput(
            start=Point2D(195.0, 0.0),
            end=Point2D(225.0, -200.0),
        )
        path = Path2D(
            points=(Point2D(195.0, 0.0), Point2D(math.nan, -200.0))
        )

        self.assertEqual(
            validate_side_seam_segment_output(segment_input, path),
            ["side_seam_segment.points[1].x must be a finite number"],
        )

    def test_broken_piecewise_hip_boundary_safe_stops_before_joining(self):
        geometry_input = self._piecewise_input()
        broken = SideSeamPiecewiseGeometryInput(
            waist_to_hip=geometry_input.waist_to_hip,
            hip_to_hem=SideSeamSegmentGeometryInput(
                start=Point2D(226.0, -200.0),
                end=geometry_input.hip_to_hem.end,
            ),
        )
        upper = Path2D(
            points=(geometry_input.waist_to_hip.start, geometry_input.waist_to_hip.end)
        )
        lower = Path2D(points=(broken.hip_to_hem.start, broken.hip_to_hem.end))

        with self.assertRaisesRegex(
            ValueError,
            "piecewise side seam segments must share the same hip boundary",
        ):
            join_side_seam_piecewise_output(broken, upper, lower)

    def test_invalid_segment_output_safe_stops_joiner(self):
        geometry_input = self._piecewise_input()
        upper = Path2D(
            points=(Point2D(194.0, 0.0), geometry_input.waist_to_hip.end)
        )
        lower = Path2D(
            points=(geometry_input.hip_to_hem.start, geometry_input.hip_to_hem.end)
        )

        with self.assertRaisesRegex(
            ValueError,
            "waist_to_hip: side_seam segment endpoints must equal its semantic start and end",
        ):
            join_side_seam_piecewise_output(geometry_input, upper, lower)


if __name__ == "__main__":
    unittest.main()
