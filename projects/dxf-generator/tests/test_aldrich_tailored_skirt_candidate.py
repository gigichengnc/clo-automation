"""Regression tests for the quarantined Aldrich tailored-skirt candidate."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from measurements.body import BodyMeasurements
from styles.school_skirt.research.aldrich_tailored_candidate import (
    AldrichVariant,
    build_aldrich_tailored_skirt_candidate,
)


class AldrichTailoredSkirtCandidateTests(unittest.TestCase):
    def _body(self) -> BodyMeasurements:
        return BodyMeasurements(
            waist=700.0,
            hip=900.0,
            waist_to_hip=200.0,
        )

    def test_standard_source_native_values_are_preserved(self):
        candidate = build_aldrich_tailored_skirt_candidate(
            self._body(),
            variant=AldrichVariant.STANDARD,
        )

        self.assertEqual(candidate.status, "RESEARCH_CANDIDATE")
        self.assertEqual(candidate.production_status, "NOT_PRODUCTION_DEFAULT")

        self.assertEqual(candidate.front.hip_span, 225.0)
        self.assertEqual(candidate.back.hip_span, 240.0)
        self.assertEqual(candidate.front.dart_intakes, (20.0,))
        self.assertEqual(candidate.back.dart_intakes, (20.0, 20.0))

        self.assertEqual(candidate.front.pre_dart_waist_span, 197.5)
        self.assertEqual(candidate.back.pre_dart_waist_span, 217.5)
        self.assertEqual(candidate.front.finished_waist_span, 177.5)
        self.assertEqual(candidate.back.finished_waist_span, 177.5)

        self.assertEqual(candidate.front.side_shaping, 27.5)
        self.assertEqual(candidate.back.side_shaping, 22.5)
        self.assertEqual(candidate.front.total_suppression, 47.5)
        self.assertEqual(candidate.back.total_suppression, 62.5)

    def test_source_panel_mean_conserves_canonical_suppression(self):
        candidate = build_aldrich_tailored_skirt_candidate(
            self._body(),
            variant=AldrichVariant.STANDARD,
        )

        self.assertEqual(candidate.canonical_quarter_suppression, 55.0)
        self.assertEqual(candidate.mean_source_panel_suppression, 55.0)

    def test_current_equal_quarter_contract_reports_mapping_mismatch(self):
        candidate = build_aldrich_tailored_skirt_candidate(
            self._body(),
            variant=AldrichVariant.STANDARD,
        )

        self.assertFalse(candidate.compatible_with_current_equal_quarter_contract)
        self.assertEqual(
            candidate.current_contract_validation_errors,
            (
                "front suppression allocation must equal quarter_suppression (55.0 mm)",
                "back suppression allocation must equal quarter_suppression (55.0 mm)",
            ),
        )

    def test_small_waist_variant_is_explicit_not_auto_selected(self):
        candidate = build_aldrich_tailored_skirt_candidate(
            self._body(),
            variant=AldrichVariant.SMALL_WAIST,
        )

        self.assertEqual(candidate.front.dart_intakes, (25.0,))
        self.assertEqual(candidate.back.dart_intakes, (25.0, 25.0))
        self.assertEqual(candidate.front.finished_waist_span, 177.5)
        self.assertEqual(candidate.back.finished_waist_span, 177.5)
        self.assertEqual(candidate.mean_source_panel_suppression, 55.0)

    def test_candidate_does_not_generate_geometry_or_dxf(self):
        candidate = build_aldrich_tailored_skirt_candidate(
            self._body(),
            variant=AldrichVariant.STANDARD,
        )

        self.assertFalse(hasattr(candidate, "geometry"))
        self.assertFalse(hasattr(candidate, "dxf"))
        self.assertFalse(hasattr(candidate, "coordinates"))


if __name__ == "__main__":
    unittest.main()
