"""Regression tests for school-skirt coordinate-geometry output validation."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import (
    DartGeometry,
    PanelGeometry,
    PanelOutline,
    Path2D,
    Point2D,
    SchoolSkirtGeometry,
)
from styles.school_skirt.geometry_output_validation import (
    validate_school_skirt_geometry,
)


class SchoolSkirtGeometryOutputValidationTests(unittest.TestCase):
    def _panel(self, *, darts=None) -> PanelGeometry:
        if darts is None:
            darts = (
                DartGeometry(
                    dart_index=0,
                    left_waist=Point2D(70.0, 0.0),
                    apex=Point2D(75.0, -100.0),
                    right_waist=Point2D(80.0, 0.0),
                ),
            )

        return PanelGeometry(
            outline=PanelOutline(
                centre_edge=Path2D(
                    points=(Point2D(0.0, 0.0), Point2D(0.0, -500.0))
                ),
                waist=Path2D(
                    points=(Point2D(0.0, 0.0), Point2D(195.0, 0.0))
                ),
                side_seam=Path2D(
                    points=(
                        Point2D(195.0, 0.0),
                        Point2D(225.0, -200.0),
                        Point2D(305.0, -500.0),
                    )
                ),
                hem=Path2D(
                    points=(Point2D(0.0, -500.0), Point2D(305.0, -500.0))
                ),
            ),
            darts=darts,
        )

    def _geometry(self, *, front=None, back=None) -> SchoolSkirtGeometry:
        return SchoolSkirtGeometry(
            front=front if front is not None else self._panel(),
            back=back if back is not None else self._panel(),
        )

    def test_valid_geometry_passes(self):
        self.assertEqual(validate_school_skirt_geometry(self._geometry()), [])

    def test_edge_direction_is_not_imposed(self):
        panel = self._panel()
        reversed_waist = Path2D(points=tuple(reversed(panel.outline.waist.points)))
        panel = PanelGeometry(
            outline=PanelOutline(
                centre_edge=panel.outline.centre_edge,
                waist=reversed_waist,
                side_seam=panel.outline.side_seam,
                hem=panel.outline.hem,
            ),
            darts=panel.darts,
        )

        self.assertEqual(
            validate_school_skirt_geometry(self._geometry(front=panel)),
            [],
        )

    def test_path_requires_at_least_two_points(self):
        panel = self._panel()
        panel = PanelGeometry(
            outline=PanelOutline(
                centre_edge=panel.outline.centre_edge,
                waist=Path2D(points=(Point2D(0.0, 0.0),)),
                side_seam=panel.outline.side_seam,
                hem=panel.outline.hem,
            ),
            darts=panel.darts,
        )

        errors = validate_school_skirt_geometry(self._geometry(front=panel))
        self.assertIn("front.outline.waist must contain at least 2 points", errors)

    def test_non_finite_coordinate_is_rejected(self):
        panel = self._panel()
        panel = PanelGeometry(
            outline=PanelOutline(
                centre_edge=panel.outline.centre_edge,
                waist=Path2D(
                    points=(Point2D(0.0, 0.0), Point2D(math.nan, 0.0))
                ),
                side_seam=panel.outline.side_seam,
                hem=panel.outline.hem,
            ),
            darts=panel.darts,
        )

        errors = validate_school_skirt_geometry(self._geometry(front=panel))
        self.assertIn(
            "front.outline.waist.points[1].x must be a finite number",
            errors,
        )

    def test_semantic_edges_must_connect(self):
        panel = self._panel()
        panel = PanelGeometry(
            outline=PanelOutline(
                centre_edge=panel.outline.centre_edge,
                waist=panel.outline.waist,
                side_seam=Path2D(
                    points=(Point2D(196.0, 0.0), Point2D(305.0, -500.0))
                ),
                hem=panel.outline.hem,
            ),
            darts=panel.darts,
        )

        errors = validate_school_skirt_geometry(self._geometry(front=panel))
        self.assertIn("front waist and side_seam must share an endpoint", errors)

    def test_duplicate_dart_indices_are_rejected(self):
        darts = (
            DartGeometry(0, Point2D(50.0, 0.0), Point2D(55.0, -90.0), Point2D(60.0, 0.0)),
            DartGeometry(0, Point2D(90.0, 0.0), Point2D(95.0, -100.0), Point2D(100.0, 0.0)),
        )

        errors = validate_school_skirt_geometry(
            self._geometry(front=self._panel(darts=darts))
        )
        self.assertIn(
            "front dart_index values must be unique within the panel",
            errors,
        )

    def test_degenerate_dart_is_rejected(self):
        darts = (
            DartGeometry(
                dart_index=0,
                left_waist=Point2D(70.0, 0.0),
                apex=Point2D(75.0, -100.0),
                right_waist=Point2D(70.0, 0.0),
            ),
        )

        errors = validate_school_skirt_geometry(
            self._geometry(front=self._panel(darts=darts))
        )
        self.assertIn("front.darts[0] waist legs must not overlap", errors)

    def test_dart_index_must_be_non_negative_integer(self):
        darts = (
            DartGeometry(
                dart_index=-1,
                left_waist=Point2D(70.0, 0.0),
                apex=Point2D(75.0, -100.0),
                right_waist=Point2D(80.0, 0.0),
            ),
        )

        errors = validate_school_skirt_geometry(
            self._geometry(front=self._panel(darts=darts))
        )
        self.assertIn(
            "front.darts[0].dart_index must be a non-negative integer",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
