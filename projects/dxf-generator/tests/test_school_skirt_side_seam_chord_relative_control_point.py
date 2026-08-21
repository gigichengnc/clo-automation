"""Regression tests for the chord-relative Bezier control-point research rule."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_chord_relative_control_point import (
    ChordRelativeBezierControlPointRule,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_quadratic_bezier_policy import (
    QuadraticBezierSideSeamSegmentPolicy,
)
from styles.school_skirt.side_seam_segment_output import (
    validate_side_seam_segment_output,
)


class SchoolSkirtSideSeamChordRelativeControlPointTests(unittest.TestCase):
    def test_vertical_downward_chord_positive_offset_moves_to_left_normal(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(0.0, -200.0),
        )
        rule = ChordRelativeBezierControlPointRule(
            along_fraction=0.5,
            normal_offset=12.0,
        )

        self.assertEqual(rule.resolve(segment), Point2D(12.0, -100.0))

    def test_horizontal_rightward_chord_positive_offset_moves_upward(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
        )
        rule = ChordRelativeBezierControlPointRule(
            along_fraction=0.25,
            normal_offset=2.0,
        )

        self.assertEqual(rule.resolve(segment), Point2D(2.5, 2.0))

    def test_negative_normal_offset_moves_to_opposite_side(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(0.0, -200.0),
        )
        rule = ChordRelativeBezierControlPointRule(
            along_fraction=0.5,
            normal_offset=-12.0,
        )

        self.assertEqual(rule.resolve(segment), Point2D(-12.0, -100.0))

    def test_along_fraction_is_not_restricted_to_chord_interior(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
        )
        rule = ChordRelativeBezierControlPointRule(
            along_fraction=1.25,
            normal_offset=0.0,
        )

        self.assertEqual(rule.resolve(segment), Point2D(12.5, 0.0))

    def test_parameters_must_be_finite_numeric_values(self):
        with self.assertRaisesRegex(ValueError, "along_fraction must be numeric"):
            ChordRelativeBezierControlPointRule(True, 0.0)

        with self.assertRaisesRegex(ValueError, "normal_offset must be numeric"):
            ChordRelativeBezierControlPointRule(0.5, False)

        with self.assertRaisesRegex(
            ValueError,
            "along_fraction must be a finite number",
        ):
            ChordRelativeBezierControlPointRule(math.nan, 0.0)

        with self.assertRaisesRegex(
            ValueError,
            "normal_offset must be a finite number",
        ):
            ChordRelativeBezierControlPointRule(0.5, math.inf)

    def test_zero_length_chord_safe_stops_because_normal_is_undefined(self):
        point = Point2D(5.0, -20.0)
        segment = SideSeamSegmentGeometryInput(start=point, end=point)
        rule = ChordRelativeBezierControlPointRule(
            along_fraction=0.5,
            normal_offset=12.0,
        )

        with self.assertRaisesRegex(
            ValueError,
            "side-seam segment chord must have non-zero length",
        ):
            rule.resolve(segment)

    def test_rule_integrates_with_quadratic_policy_and_existing_segment_contract(self):
        segment = SideSeamSegmentGeometryInput(
            start=Point2D(195.0, 0.0),
            end=Point2D(225.0, -200.0),
        )
        policy = QuadraticBezierSideSeamSegmentPolicy(
            control_point_rule=ChordRelativeBezierControlPointRule(
                along_fraction=0.5,
                normal_offset=12.0,
            ),
            sample_count=7,
        )

        path = policy.build(segment)

        self.assertEqual(len(path.points), 7)
        self.assertIs(path.points[0], segment.start)
        self.assertIs(path.points[-1], segment.end)
        self.assertEqual(validate_side_seam_segment_output(segment, path), [])


if __name__ == "__main__":
    unittest.main()
