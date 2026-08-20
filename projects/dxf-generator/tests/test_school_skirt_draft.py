"""Regression tests for policy-independent school-skirt draft values.

These fixtures are synthetic. They intentionally avoid dart-allocation policy,
legacy defect compatibility, coordinate geometry, and DXF generation.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from garment.request import GarmentRequest
from measurements.body import BodyMeasurements
from styles.school_skirt.draft import build_school_skirt_draft
from styles.school_skirt.draft_validation import validate_school_skirt_draft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.spec import build_school_skirt_spec


class SchoolSkirtDraftRegressionTests(unittest.TestCase):
    def _build_draft(
        self,
        *,
        waist: float,
        hip: float,
        waist_to_hip: float,
        requested_length: float,
    ):
        body = BodyMeasurements(
            waist=waist,
            hip=hip,
            waist_to_hip=waist_to_hip,
        )
        request = GarmentRequest(requested_length=requested_length)
        spec = build_school_skirt_spec(body, request)
        return build_school_skirt_draft(spec, SchoolSkirtDraftingParameters())

    def test_synthetic_medium_drop_policy_independent_values(self):
        draft = self._build_draft(
            waist=700.0,
            hip=900.0,
            waist_to_hip=200.0,
            requested_length=500.0,
        )

        self.assertEqual(draft.quarter_waist, 180.0)
        self.assertEqual(draft.quarter_hip, 225.0)
        self.assertEqual(draft.quarter_suppression, 45.0)
        self.assertEqual(draft.hip_position, 200.0)
        self.assertEqual(draft.hem_position, 500.0)
        self.assertEqual(draft.hem_half_width, 305.0)
        self.assertEqual(validate_school_skirt_draft(draft), [])

    def test_length_equal_to_hip_depth_safe_stops(self):
        draft = self._build_draft(
            waist=700.0,
            hip=900.0,
            waist_to_hip=200.0,
            requested_length=200.0,
        )

        self.assertEqual(
            validate_school_skirt_draft(draft),
            ["hem_position must be greater than hip_position"],
        )


if __name__ == "__main__":
    unittest.main()
