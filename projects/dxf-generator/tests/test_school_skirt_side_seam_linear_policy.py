"""Regression tests for the opt-in linear school-skirt side-seam baseline."""

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
from styles.school_skirt.side_seam_piecewise_input import (
    build_side_seam_piecewise_input,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_policy import SideSeamGeometryInput
from styles.school_skirt.side_seam_segment_output import (
    join_side_seam_piecewise_output,
    validate_side_seam_segment_output,
)
from styles.school_skirt.side_seam_validation import (
    validate_school_skirt_side_seam,
)


class SchoolSkirtLinearSideSeamPolicyTests(unittest.TestCase):
    def test_linear_policy_returns_exactly_the_two_semantic_anchors(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(195.0, 0.0),
            end=Point2D(225.0, -200.0),
        )

        path = LinearSideSeamSegmentPolicy().build(segment)

        self.assertEqual(
            path,
            Path2D(points=(segment.start, segment.end)),
        )
        self.assertEqual(validate_side_seam_segment_output(segment, path), [])

    def test_two_linear_segments_form_a_complete_three_anchor_side_seam(self):
        geometry_input = SideSeamGeometryInput(
            side_waist=Point2D(195.0, 0.0),
            hip_side=Point2D(225.0, -200.0),
            hem_side=Point2D(305.0, -500.0),
        )
        piecewise = build_side_seam_piecewise_input(geometry_input)
        policy = LinearSideSeamSegmentPolicy()

        upper = policy.build(piecewise.waist_to_hip)
        lower = policy.build(piecewise.hip_to_hem)
        joined = join_side_seam_piecewise_output(piecewise, upper, lower)

        self.assertEqual(
            joined,
            Path2D(
                points=(
                    geometry_input.side_waist,
                    geometry_input.hip_side,
                    geometry_input.hem_side,
                )
            ),
        )
        self.assertEqual(validate_school_skirt_side_seam(geometry_input, joined), [])

    def test_linear_policy_adds_no_midpoints_or_sampling(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(225.0, -200.0),
            end=Point2D(305.0, -500.0),
        )

        path = LinearSideSeamSegmentPolicy().build(segment)

        self.assertEqual(len(path.points), 2)
        self.assertEqual(path.points[0], segment.start)
        self.assertEqual(path.points[1], segment.end)


if __name__ == "__main__":
    unittest.main()
