"""Regression tests for school-skirt panel geometry input consistency."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.dart_plan import ResolvedDart
from styles.school_skirt.panel_geometry_input import (
    PanelGeometryInput,
    SchoolSkirtPanelGeometryInput,
)
from styles.school_skirt.panel_geometry_input_validation import (
    validate_school_skirt_panel_geometry_input,
)


class SchoolSkirtPanelGeometryInputValidationTests(unittest.TestCase):
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
                darts=(ResolvedDart(0, 15.0, 0.42, 100.0),),
            ),
            back=PanelGeometryInput(
                target_waist_span=180.0,
                waist_span_before_darts=210.0,
                hip_span=225.0,
                hem_span=305.0,
                hip_position=200.0,
                hem_position=500.0,
                side_shaping=15.0,
                darts=(
                    ResolvedDart(0, 10.0, 0.28, 120.0),
                    ResolvedDart(1, 20.0, 0.73, 120.0),
                ),
            ),
        )

    def test_consistent_front_and_back_inputs_are_valid(self):
        self.assertEqual(
            validate_school_skirt_panel_geometry_input(self._geometry_input()),
            [],
        )

    def test_pre_dart_waist_must_match_resolved_dart_total(self):
        geometry_input = self._geometry_input()
        geometry_input = SchoolSkirtPanelGeometryInput(
            front=PanelGeometryInput(
                **{
                    **geometry_input.front.__dict__,
                    "waist_span_before_darts": 194.0,
                }
            ),
            back=geometry_input.back,
        )

        self.assertEqual(
            validate_school_skirt_panel_geometry_input(geometry_input),
            [
                "front pre-dart waist expansion must equal resolved dart intake total "
                "(15.0 mm)",
                "front hip-to-pre-dart-waist difference must equal side_shaping "
                "(30.0 mm)",
            ],
        )

    def test_side_shaping_must_match_hip_to_pre_dart_waist_difference(self):
        geometry_input = self._geometry_input()
        geometry_input = SchoolSkirtPanelGeometryInput(
            front=geometry_input.front,
            back=PanelGeometryInput(
                **{
                    **geometry_input.back.__dict__,
                    "side_shaping": 14.0,
                }
            ),
        )

        self.assertEqual(
            validate_school_skirt_panel_geometry_input(geometry_input),
            [
                "back hip-to-pre-dart-waist difference must equal side_shaping "
                "(14.0 mm)"
            ],
        )

    def test_zero_dart_panel_is_valid_when_pre_dart_equals_target(self):
        geometry_input = self._geometry_input()
        geometry_input = SchoolSkirtPanelGeometryInput(
            front=PanelGeometryInput(
                target_waist_span=180.0,
                waist_span_before_darts=180.0,
                hip_span=225.0,
                hem_span=305.0,
                hip_position=200.0,
                hem_position=500.0,
                side_shaping=45.0,
                darts=(),
            ),
            back=geometry_input.back,
        )

        self.assertEqual(
            validate_school_skirt_panel_geometry_input(geometry_input),
            [],
        )

    def test_tiny_floating_point_difference_is_tolerated(self):
        geometry_input = self._geometry_input()
        geometry_input = SchoolSkirtPanelGeometryInput(
            front=geometry_input.front,
            back=PanelGeometryInput(
                **{
                    **geometry_input.back.__dict__,
                    "waist_span_before_darts": 210.0000005,
                    "side_shaping": 14.9999995,
                }
            ),
        )

        self.assertEqual(
            validate_school_skirt_panel_geometry_input(geometry_input),
            [],
        )


if __name__ == "__main__":
    unittest.main()
