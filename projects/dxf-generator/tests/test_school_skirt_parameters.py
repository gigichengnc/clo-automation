"""Regression tests for school-skirt drafting-parameter validation."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.parameters_validation import validate_school_skirt_parameters


class SchoolSkirtParameterValidationTests(unittest.TestCase):
    def test_defaults_are_valid(self):
        self.assertEqual(
            validate_school_skirt_parameters(SchoolSkirtDraftingParameters()),
            [],
        )

    def test_negative_flare_is_not_rejected_as_policy(self):
        parameters = SchoolSkirtDraftingParameters(flare=-20.0)
        self.assertEqual(validate_school_skirt_parameters(parameters), [])

    def test_boolean_dart_count_is_rejected(self):
        parameters = SchoolSkirtDraftingParameters(front_dart_count=True)
        self.assertEqual(
            validate_school_skirt_parameters(parameters),
            ["front_dart_count must be an integer"],
        )

    def test_negative_dart_count_is_rejected(self):
        parameters = SchoolSkirtDraftingParameters(back_dart_count=-1)
        self.assertEqual(
            validate_school_skirt_parameters(parameters),
            ["back_dart_count must be greater than or equal to 0"],
        )

    def test_non_finite_flare_is_rejected(self):
        parameters = SchoolSkirtDraftingParameters(flare=math.inf)
        self.assertEqual(
            validate_school_skirt_parameters(parameters),
            ["flare must be a finite number"],
        )

    def test_non_positive_waistband_height_is_rejected(self):
        parameters = SchoolSkirtDraftingParameters(waistband_height=0.0)
        self.assertEqual(
            validate_school_skirt_parameters(parameters),
            ["waistband_height must be greater than 0 mm"],
        )

    def test_positive_dart_count_requires_positive_length(self):
        parameters = SchoolSkirtDraftingParameters(front_dart_length=0.0)
        self.assertEqual(
            validate_school_skirt_parameters(parameters),
            [
                "front_dart_length must be greater than 0 mm when "
                "front_dart_count is greater than 0"
            ],
        )

    def test_zero_dart_count_allows_zero_length(self):
        parameters = SchoolSkirtDraftingParameters(
            front_dart_count=0,
            front_dart_length=0.0,
        )
        self.assertEqual(validate_school_skirt_parameters(parameters), [])


if __name__ == "__main__":
    unittest.main()
