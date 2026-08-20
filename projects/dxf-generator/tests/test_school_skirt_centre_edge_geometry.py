"""Regression tests for straight school-skirt centre-edge geometry."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.centre_edge_geometry import (
    build_panel_centre_edge,
    build_school_skirt_centre_edges,
)
from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.panel_anchors import (
    PanelAnchorPoints,
    SchoolSkirtPanelAnchors,
)


class SchoolSkirtCentreEdgeGeometryTests(unittest.TestCase):
    def _panel_anchors(self, hem_y: float = -500.0) -> PanelAnchorPoints:
        return PanelAnchorPoints(
            centre_waist=Point2D(0.0, 0.0),
            centre_hem=Point2D(0.0, hem_y),
            side_waist=Point2D(195.0, 0.0),
            hip_side=Point2D(225.0, -200.0),
            hem_side=Point2D(305.0, hem_y),
        )

    def test_panel_centre_edge_connects_only_centre_anchors(self):
        anchors = self._panel_anchors()

        self.assertEqual(
            build_panel_centre_edge(anchors),
            Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -500.0))),
        )

    def test_front_and_back_centre_edges_are_built_independently(self):
        anchors = SchoolSkirtPanelAnchors(
            front=self._panel_anchors(-500.0),
            back=self._panel_anchors(-620.0),
        )

        front, back = build_school_skirt_centre_edges(anchors)

        self.assertEqual(
            front,
            Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -500.0))),
        )
        self.assertEqual(
            back,
            Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -620.0))),
        )


if __name__ == "__main__":
    unittest.main()
