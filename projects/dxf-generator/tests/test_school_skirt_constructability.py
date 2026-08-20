"""Regression tests for school-skirt dart constructability validation."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.constructability_validation import (
    validate_school_skirt_constructability,
)
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


class SchoolSkirtConstructabilityValidationTests(unittest.TestCase):
    def _draft(self, *, hip_position: float = 200.0) -> SchoolSkirtDraft:
        return SchoolSkirtDraft(
            quarter_waist=180.0,
            quarter_hip=225.0,
            quarter_suppression=45.0,
            hip_position=hip_position,
            hem_position=500.0,
            hem_half_width=305.0,
        )

    def test_default_dart_lengths_are_constructable(self):
        self.assertEqual(
            validate_school_skirt_constructability(
                self._draft(),
                SchoolSkirtDraftingParameters(),
            ),
            [],
        )

    def test_dart_length_equal_to_hip_position_is_allowed(self):
        parameters = SchoolSkirtDraftingParameters(
            front_dart_length=200.0,
            back_dart_length=200.0,
        )

        self.assertEqual(
            validate_school_skirt_constructability(self._draft(), parameters),
            [],
        )

    def test_front_dart_cannot_extend_below_hip_position(self):
        parameters = SchoolSkirtDraftingParameters(front_dart_length=201.0)

        self.assertEqual(
            validate_school_skirt_constructability(self._draft(), parameters),
            [
                "front_dart_length must be less than or equal to "
                "hip_position (200.0 mm)"
            ],
        )

    def test_back_dart_cannot_extend_below_hip_position(self):
        parameters = SchoolSkirtDraftingParameters(back_dart_length=250.0)

        self.assertEqual(
            validate_school_skirt_constructability(self._draft(), parameters),
            [
                "back_dart_length must be less than or equal to "
                "hip_position (200.0 mm)"
            ],
        )

    def test_zero_dart_count_ignores_unused_dart_length(self):
        parameters = SchoolSkirtDraftingParameters(
            front_dart_count=0,
            front_dart_length=500.0,
        )

        self.assertEqual(
            validate_school_skirt_constructability(self._draft(), parameters),
            [],
        )


if __name__ == "__main__":
    unittest.main()
