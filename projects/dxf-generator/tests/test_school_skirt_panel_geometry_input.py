"""Regression tests for school-skirt panel geometry semantic inputs."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.dart_plan import (
    PanelDartPlan,
    ResolvedDart,
    SchoolSkirtDartPlan,
)
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.panel_geometry_input import (
    build_school_skirt_panel_geometry_input,
)
from styles.school_skirt.suppression import (
    PanelSuppressionAllocation,
    SchoolSkirtSuppressionAllocation,
)


class SchoolSkirtPanelGeometryInputTests(unittest.TestCase):
    def _draft(self) -> SchoolSkirtDraft:
        return SchoolSkirtDraft(
            quarter_waist=180.0,
            quarter_hip=225.0,
            quarter_suppression=45.0,
            hip_position=200.0,
            hem_position=500.0,
            hem_half_width=305.0,
        )

    def test_front_and_back_semantics_remain_distinct(self):
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=15.0,
                side_shaping=30.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )
        dart_plan = SchoolSkirtDartPlan(
            front=PanelDartPlan(
                darts=(ResolvedDart(0, 15.0, 0.42, 100.0),),
            ),
            back=PanelDartPlan(
                darts=(
                    ResolvedDart(0, 10.0, 0.28, 120.0),
                    ResolvedDart(1, 20.0, 0.73, 120.0),
                ),
            ),
        )

        geometry_input = build_school_skirt_panel_geometry_input(
            self._draft(),
            allocation,
            dart_plan,
        )

        self.assertEqual(geometry_input.front.target_waist_span, 180.0)
        self.assertEqual(geometry_input.front.waist_span_before_darts, 195.0)
        self.assertEqual(geometry_input.front.side_shaping, 30.0)
        self.assertEqual(geometry_input.front.darts, dart_plan.front.darts)

        self.assertEqual(geometry_input.back.target_waist_span, 180.0)
        self.assertEqual(geometry_input.back.waist_span_before_darts, 210.0)
        self.assertEqual(geometry_input.back.side_shaping, 15.0)
        self.assertEqual(geometry_input.back.darts, dart_plan.back.darts)

        for panel in (geometry_input.front, geometry_input.back):
            self.assertEqual(panel.hip_span, 225.0)
            self.assertEqual(panel.hem_span, 305.0)
            self.assertEqual(panel.hip_position, 200.0)
            self.assertEqual(panel.hem_position, 500.0)

    def test_zero_dart_panel_keeps_target_and_pre_dart_waist_equal(self):
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=0.0,
                side_shaping=45.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )
        dart_plan = SchoolSkirtDartPlan(
            front=PanelDartPlan(darts=()),
            back=PanelDartPlan(
                darts=(
                    ResolvedDart(0, 10.0, 0.28, 120.0),
                    ResolvedDart(1, 20.0, 0.73, 120.0),
                ),
            ),
        )

        geometry_input = build_school_skirt_panel_geometry_input(
            self._draft(),
            allocation,
            dart_plan,
        )

        self.assertEqual(geometry_input.front.target_waist_span, 180.0)
        self.assertEqual(geometry_input.front.waist_span_before_darts, 180.0)
        self.assertEqual(geometry_input.front.darts, ())


if __name__ == "__main__":
    unittest.main()
