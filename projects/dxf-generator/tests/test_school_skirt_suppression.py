"""Regression tests for school-skirt suppression-target/allocation validation."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.suppression import (
    PanelSuppressionAllocation,
    PanelSuppressionTargets,
    SchoolSkirtSuppressionAllocation,
)
from styles.school_skirt.suppression_validation import (
    validate_school_skirt_panel_suppression_targets,
    validate_school_skirt_suppression_allocation,
)


class SchoolSkirtSuppressionValidationTests(unittest.TestCase):
    def _draft(self, quarter_suppression: float = 45.0) -> SchoolSkirtDraft:
        return SchoolSkirtDraft(
            quarter_waist=180.0,
            quarter_hip=225.0,
            quarter_suppression=quarter_suppression,
            hip_position=200.0,
            hem_position=500.0,
            hem_half_width=305.0,
        )

    def test_symmetric_panel_targets_conserve_half_garment_suppression(self):
        targets = PanelSuppressionTargets(front=45.0, back=45.0)
        self.assertEqual(
            validate_school_skirt_panel_suppression_targets(self._draft(), targets),
            [],
        )

    def test_asymmetric_panel_targets_are_valid_when_total_is_conserved(self):
        targets = PanelSuppressionTargets(front=37.5, back=52.5)
        self.assertEqual(
            validate_school_skirt_panel_suppression_targets(self._draft(), targets),
            [],
        )

    def test_panel_targets_must_conserve_global_requirement(self):
        targets = PanelSuppressionTargets(front=40.0, back=40.0)
        self.assertEqual(
            validate_school_skirt_panel_suppression_targets(self._draft(), targets),
            [
                "front + back suppression targets must equal twice "
                "quarter_suppression (90.0 mm)"
            ],
        )

    def test_valid_allocation_matches_explicit_panel_targets(self):
        targets = PanelSuppressionTargets(front=45.0, back=45.0)
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=20.0,
                side_shaping=25.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )

        self.assertEqual(
            validate_school_skirt_suppression_allocation(targets, allocation),
            [],
        )

    def test_asymmetric_allocation_matches_asymmetric_targets(self):
        targets = PanelSuppressionTargets(front=47.5, back=62.5)
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=20.0,
                side_shaping=27.5,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=40.0,
                side_shaping=22.5,
            ),
        )

        self.assertEqual(
            validate_school_skirt_suppression_allocation(targets, allocation),
            [],
        )

    def test_front_total_must_equal_explicit_front_target(self):
        targets = PanelSuppressionTargets(front=45.0, back=45.0)
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=20.0,
                side_shaping=20.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )

        self.assertEqual(
            validate_school_skirt_suppression_allocation(targets, allocation),
            [
                "front suppression allocation must equal its explicit panel "
                "target (45.0 mm)"
            ],
        )

    def test_negative_component_is_rejected(self):
        targets = PanelSuppressionTargets(front=45.0, back=45.0)
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=-1.0,
                side_shaping=46.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )

        self.assertEqual(
            validate_school_skirt_suppression_allocation(targets, allocation),
            ["front.dart_intake_total must be greater than or equal to 0 mm"],
        )

    def test_non_finite_panel_target_is_rejected(self):
        targets = PanelSuppressionTargets(front=math.nan, back=45.0)
        self.assertEqual(
            validate_school_skirt_panel_suppression_targets(self._draft(), targets),
            ["targets.front must be a finite number"],
        )

    def test_negative_required_suppression_safe_stops(self):
        targets = PanelSuppressionTargets(front=0.0, back=0.0)
        self.assertEqual(
            validate_school_skirt_panel_suppression_targets(
                self._draft(quarter_suppression=-5.0),
                targets,
            ),
            [
                "quarter_suppression must be greater than or equal to 0 mm "
                "for suppression allocation"
            ],
        )

    def test_tiny_floating_point_difference_is_tolerated(self):
        targets = PanelSuppressionTargets(front=45.0, back=45.0000004)
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=20.0,
                side_shaping=25.0000004,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )

        self.assertEqual(
            validate_school_skirt_panel_suppression_targets(self._draft(), targets),
            [],
        )
        self.assertEqual(
            validate_school_skirt_suppression_allocation(targets, allocation),
            [],
        )


if __name__ == "__main__":
    unittest.main()
