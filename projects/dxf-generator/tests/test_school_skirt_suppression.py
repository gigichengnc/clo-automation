"""Regression tests for school-skirt suppression-allocation validation."""

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
    SchoolSkirtSuppressionAllocation,
)
from styles.school_skirt.suppression_validation import (
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

    def test_valid_allocation_conserves_suppression(self):
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
            validate_school_skirt_suppression_allocation(self._draft(), allocation),
            [],
        )

    def test_front_total_must_equal_quarter_suppression(self):
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
            validate_school_skirt_suppression_allocation(self._draft(), allocation),
            ["front suppression allocation must equal quarter_suppression (45.0 mm)"],
        )

    def test_negative_component_is_rejected(self):
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
            validate_school_skirt_suppression_allocation(self._draft(), allocation),
            ["front.dart_intake_total must be greater than or equal to 0 mm"],
        )

    def test_non_finite_component_is_rejected(self):
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=math.nan,
                side_shaping=45.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=30.0,
                side_shaping=15.0,
            ),
        )

        self.assertEqual(
            validate_school_skirt_suppression_allocation(self._draft(), allocation),
            ["front.dart_intake_total must be a finite number"],
        )

    def test_negative_required_suppression_safe_stops(self):
        allocation = SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=0.0,
                side_shaping=0.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=0.0,
                side_shaping=0.0,
            ),
        )

        self.assertEqual(
            validate_school_skirt_suppression_allocation(
                self._draft(quarter_suppression=-5.0),
                allocation,
            ),
            [
                "quarter_suppression must be greater than or equal to 0 mm "
                "for suppression allocation"
            ],
        )

    def test_tiny_floating_point_difference_is_tolerated(self):
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
            validate_school_skirt_suppression_allocation(self._draft(), allocation),
            [],
        )


if __name__ == "__main__":
    unittest.main()
