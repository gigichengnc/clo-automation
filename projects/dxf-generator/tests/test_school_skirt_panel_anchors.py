"""Regression tests for canonical school-skirt panel anchor points."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.panel_anchors import build_school_skirt_panel_anchors
from styles.school_skirt.panel_geometry_input import (
    PanelGeometryInput,
    SchoolSkirtPanelGeometryInput,
)


class SchoolSkirtPanelAnchorTests(unittest.TestCase):
    def _geometry_input(self) -> SchoolSkirtPanelGeometryInput:
        return SchoolSkirtPanelGeometryInput(
            front=PanelGeometryInput(
                target_waist_span=180.0,
                waist_span_before_darts=195.0,
                hip_span=225.0,
                hem_span=305.0,
                hip_position=200.0,
                hem_position=500.0,
                side_shaping=30.0,
                darts=(),
            ),
            back=PanelGeometryInput(
                target_waist_span=180.0,
                waist_span_before_darts=210.0,
                hip_span=225.0,
                hem_span=305.0,
                hip_position=200.0,
                hem_position=500.0,
                side_shaping=15.0,
                darts=(),
            ),
        )

    def test_canonical_frame_and_semantic_anchors_are_mapped(self):
        anchors = build_school_skirt_panel_anchors(self._geometry_input())

        self.assertEqual(anchors.front.centre_waist, Point2D(0.0, 0.0))
        self.assertEqual(anchors.front.centre_hem, Point2D(0.0, -500.0))
        self.assertEqual(anchors.front.side_waist, Point2D(195.0, 0.0))
        self.assertEqual(anchors.front.hip_side, Point2D(225.0, -200.0))
        self.assertEqual(anchors.front.hem_side, Point2D(305.0, -500.0))

    def test_front_and_back_side_waist_anchors_remain_distinct(self):
        anchors = build_school_skirt_panel_anchors(self._geometry_input())

        self.assertEqual(anchors.front.side_waist, Point2D(195.0, 0.0))
        self.assertEqual(anchors.back.side_waist, Point2D(210.0, 0.0))

        for panel in (anchors.front, anchors.back):
            self.assertEqual(panel.centre_waist, Point2D(0.0, 0.0))
            self.assertEqual(panel.centre_hem, Point2D(0.0, -500.0))
            self.assertEqual(panel.hip_side, Point2D(225.0, -200.0))
            self.assertEqual(panel.hem_side, Point2D(305.0, -500.0))


if __name__ == "__main__":
    unittest.main()
