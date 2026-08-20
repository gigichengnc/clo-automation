"""Regression tests for numeric input validation and CLI JSON parsing."""

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cli import _read_json
from garment.request import GarmentRequest
from garment.validation import validate_garment_request
from measurements.body import BodyMeasurements
from measurements.validation import validate_body_measurements
from styles.school_skirt.validation import validate_school_skirt_spec_inputs


class NumericInputValidationTests(unittest.TestCase):
    def test_body_nan_is_rejected(self):
        body = BodyMeasurements(
            waist=math.nan,
            hip=900.0,
            waist_to_hip=200.0,
        )

        self.assertEqual(
            validate_body_measurements(body),
            ["waist must be a finite number"],
        )

    def test_garment_infinity_is_rejected(self):
        request = GarmentRequest(requested_length=math.inf)

        self.assertEqual(
            validate_garment_request(request),
            ["requested_length must be a finite number"],
        )

    def test_non_finite_ease_is_rejected(self):
        self.assertEqual(
            validate_school_skirt_spec_inputs(
                waist_ease=math.nan,
                hip_ease=math.inf,
            ),
            [
                "waist_ease must be a finite number",
                "hip_ease must be a finite number",
            ],
        )

    def test_json_boolean_dimension_is_rejected(self):
        data = {
            "body": {
                "waist": True,
                "hip": 900.0,
                "waist_to_hip": 200.0,
            },
            "garment": {
                "requested_length": 500.0,
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "input.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(
                ValueError,
                r"body\.waist must be numeric, not boolean",
            ):
                _read_json(path)


if __name__ == "__main__":
    unittest.main()
