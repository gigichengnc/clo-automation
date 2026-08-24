"""Regression tests for Aldrich side-seam research curve candidates."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from measurements.body import BodyMeasurements
from styles.school_skirt.research.aldrich_pattern_semantics import (
    build_aldrich_research_pattern_semantics,
)
from styles.school_skirt.research.aldrich_side_seam_candidates import (
    ALDRICH_RESEARCH_OUTWARD_DEVIATION_MM,
    compare_aldrich_side_seam_curve_candidates,
)
from styles.school_skirt.research.aldrich_tailored_candidate import AldrichVariant


class AldrichSideSeamCandidateTests(unittest.TestCase):
    def _comparison(self):
        semantics = build_aldrich_research_pattern_semantics(
            BodyMeasurements(waist=700.0, hip=900.0, waist_to_hip=200.0),
            skirt_length=600.0,
            variant=AldrichVariant.STANDARD,
        )
        self.assertTrue(semantics.semantic_inputs_valid)
        return compare_aldrich_side_seam_curve_candidates(semantics)

    def test_comparison_is_non_production_and_contains_three_named_candidates(self):
        comparison = self._comparison()
        self.assertEqual(comparison.status, "RESEARCH_CURVE_COMPARISON")
        self.assertEqual(comparison.production_status, "NO_PRODUCTION_SELECTION")
        self.assertEqual(
            tuple(candidate.name for candidate in comparison.candidates),
            (
                "linear_reference",
                "single_quadratic_5mm",
                "piecewise_quadratic_5mm",
            ),
        )
        for candidate in comparison.candidates:
            self.assertEqual(candidate.status, "RESEARCH_CURVE_CANDIDATE")
            self.assertEqual(candidate.production_status, "NOT_FACTORY_READY")

    def test_linear_reference_preserves_hip_with_zero_curve_deviation(self):
        candidate = self._comparison().candidates[0]
        for panel in (candidate.front, candidate.back):
            self.assertTrue(panel.metrics.hip_anchor_preserved)
            self.assertAlmostEqual(panel.metrics.hip_anchor_error, 0.0, places=9)
            self.assertAlmostEqual(panel.metrics.max_chord_normal_deviation, 0.0, places=9)
            self.assertAlmostEqual(panel.metrics.hip_join_gap, 0.0, places=9)
            self.assertGreater(panel.metrics.length, 0.0)
            self.assertIsNotNone(panel.metrics.hip_tangent_angle_degrees)

    def test_single_quadratic_has_five_mm_deviation_but_does_not_force_hip_anchor(self):
        candidate = self._comparison().candidates[1]
        for panel in (candidate.front, candidate.back):
            self.assertAlmostEqual(
                panel.metrics.max_chord_normal_deviation,
                ALDRICH_RESEARCH_OUTWARD_DEVIATION_MM,
                places=6,
            )
            self.assertFalse(panel.metrics.hip_anchor_preserved)
            self.assertGreater(panel.metrics.hip_anchor_error, 0.0)
            self.assertIsNone(panel.metrics.hip_join_gap)
            self.assertIsNone(panel.metrics.hip_tangent_angle_degrees)

    def test_piecewise_quadratic_preserves_hip_and_five_mm_upper_curve(self):
        candidate = self._comparison().candidates[2]
        for panel in (candidate.front, candidate.back):
            self.assertAlmostEqual(
                panel.metrics.max_chord_normal_deviation,
                ALDRICH_RESEARCH_OUTWARD_DEVIATION_MM,
                places=6,
            )
            self.assertTrue(panel.metrics.hip_anchor_preserved)
            self.assertAlmostEqual(panel.metrics.hip_anchor_error, 0.0, places=9)
            self.assertAlmostEqual(panel.metrics.hip_join_gap, 0.0, places=9)
            self.assertIsNotNone(panel.metrics.hip_tangent_angle_degrees)
            self.assertGreaterEqual(panel.metrics.hip_tangent_angle_degrees, 0.0)

    def test_length_comparison_is_measurement_only(self):
        comparison = self._comparison()
        for candidate in comparison.candidates:
            self.assertTrue(math.isfinite(candidate.back_minus_front_length))
            self.assertTrue(math.isfinite(candidate.absolute_length_difference))
            self.assertGreaterEqual(candidate.absolute_length_difference, 0.0)
            self.assertAlmostEqual(
                candidate.absolute_length_difference,
                abs(candidate.back_minus_front_length),
                places=9,
            )


if __name__ == "__main__":
    unittest.main()
