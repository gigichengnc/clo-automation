"""Regression tests for piecewise school-skirt side-seam input composition."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_piecewise_input import (
    build_side_seam_piecewise_input,
    validate_side_seam_piecewise_input,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_policy import SideSeamGeometryInput


class SchoolSkirtSideSeamPiecewiseInputTests(unittest.TestCase):
    def _input(self) -> SideSeamGeometryInput:
        return SideSeamGeometryInput(
            side_waist=Point2D(195.0, 0.0),
            hip_side=Point2D(225.0, -200.0),
            hem_side=Point2D(305.0, -500.0),
        )

    def test_composer_maps_the_three_anchors_deterministically(self):
        geometry_input = self._input()

        piecewise = build_side_seam_piecewise_input(geometry_input)

        self.assertEqual(
            piecewise,
            SideSeamPiecewiseGeometryInput(
                waist_to_hip=SideSeamSegmentGeometryInput(
                    start=geometry_input.side_waist,
                    end=geometry_input.hip_side,
                ),
                hip_to_hem=SideSeamSegmentGeometryInput(
                    start=geometry_input.hip_side,
                    end=geometry_input.hem_side,
                ),
            ),
        )
        self.assertEqual(validate_side_seam_piecewise_input(geometry_input, piecewise), [])

    def test_shared_hip_boundary_cannot_be_broken(self):
        geometry_input = self._input()
        piecewise = SideSeamPiecewiseGeometryInput(
            waist_to_hip=SideSeamSegmentGeometryInput(
                start=geometry_input.side_waist,
                end=geometry_input.hip_side,
            ),
            hip_to_hem=SideSeamSegmentGeometryInput(
                start=Point2D(226.0, -200.0),
                end=geometry_input.hem_side,
            ),
        )

        self.assertEqual(
            validate_side_seam_piecewise_input(geometry_input, piecewise),
            [
                "hip_to_hem.start must equal hip_side",
                "waist_to_hip.end and hip_to_hem.start must share the hip boundary",
            ],
        )

    def test_waist_endpoint_cannot_be_substituted(self):
        geometry_input = self._input()
        piecewise = build_side_seam_piecewise_input(geometry_input)
        piecewise = SideSeamPiecewiseGeometryInput(
            waist_to_hip=SideSeamSegmentGeometryInput(
                start=Point2D(194.0, 0.0),
                end=piecewise.waist_to_hip.end,
            ),
            hip_to_hem=piecewise.hip_to_hem,
        )

        self.assertEqual(
            validate_side_seam_piecewise_input(geometry_input, piecewise),
            ["waist_to_hip.start must equal side_waist"],
        )

    def test_hem_endpoint_cannot_be_substituted(self):
        geometry_input = self._input()
        piecewise = build_side_seam_piecewise_input(geometry_input)
        piecewise = SideSeamPiecewiseGeometryInput(
            waist_to_hip=piecewise.waist_to_hip,
            hip_to_hem=SideSeamSegmentGeometryInput(
                start=piecewise.hip_to_hem.start,
                end=Point2D(304.0, -500.0),
            ),
        )

        self.assertEqual(
            validate_side_seam_piecewise_input(geometry_input, piecewise),
            ["hip_to_hem.end must equal hem_side"],
        )


if __name__ == "__main__":
    unittest.main()
