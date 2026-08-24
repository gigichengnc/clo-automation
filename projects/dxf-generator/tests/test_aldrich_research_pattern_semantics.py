"""Regression tests for source-faithful Aldrich research pattern semantics."""

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
from styles.school_skirt.research.aldrich_tailored_candidate import AldrichVariant


class AldrichResearchPatternSemanticsTests(unittest.TestCase):
    def _body(self) -> BodyMeasurements:
        return BodyMeasurements(
            waist=700.0,
            hip=900.0,
            waist_to_hip=200.0,
        )

    def test_standard_candidate_preserves_source_native_panel_balance(self):
        result = build_aldrich_research_pattern_semantics(
            self._body(),
            skirt_length=600.0,
            variant=AldrichVariant.STANDARD,
        )

        self.assertTrue(result.semantic_inputs_valid)
        self.assertEqual(result.status, "RESEARCH_PATTERN_INPUTS")
        self.assertEqual(result.production_status, "NOT_FACTORY_READY")

        self.assertEqual(result.geometry_input.front.target_waist_span, 177.5)
        self.assertEqual(result.geometry_input.back.target_waist_span, 177.5)
        self.assertEqual(result.geometry_input.front.hip_span, 225.0)
        self.assertEqual(result.geometry_input.back.hip_span, 240.0)
        self.assertEqual(result.geometry_input.front.waist_span_before_darts, 197.5)
        self.assertEqual(result.geometry_input.back.waist_span_before_darts, 217.5)
        self.assertEqual(result.geometry_input.front.side_shaping, 27.5)
        self.assertEqual(result.geometry_input.back.side_shaping, 22.5)

    def test_standard_candidate_preserves_per_dart_positions_and_lengths(self):
        result = build_aldrich_research_pattern_semantics(
            self._body(),
            skirt_length=600.0,
            variant=AldrichVariant.STANDARD,
        )

        front = result.dart_plan.front.darts
        back = result.dart_plan.back.darts

        self.assertEqual(len(front), 1)
        self.assertAlmostEqual(front[0].center_fraction, 1.0 / 3.0)
        self.assertEqual(front[0].intake, 20.0)
        self.assertEqual(front[0].length, 100.0)

        self.assertEqual(len(back), 2)
        self.assertAlmostEqual(back[0].center_fraction, 1.0 / 3.0)
        self.assertAlmostEqual(back[1].center_fraction, 2.0 / 3.0)
        self.assertEqual(tuple(dart.intake for dart in back), (20.0, 20.0))
        self.assertEqual(tuple(dart.length for dart in back), (140.0, 125.0))

    def test_small_waist_variant_changes_intake_not_source_positions_or_lengths(self):
        result = build_aldrich_research_pattern_semantics(
            self._body(),
            skirt_length=600.0,
            variant=AldrichVariant.SMALL_WAIST,
        )

        self.assertEqual(
            tuple(dart.intake for dart in result.dart_plan.front.darts),
            (25.0,),
        )
        self.assertEqual(
            tuple(dart.intake for dart in result.dart_plan.back.darts),
            (25.0, 25.0),
        )
        self.assertEqual(
            tuple(dart.length for dart in result.dart_plan.back.darts),
            (140.0, 125.0),
        )

    def test_curve_and_production_boundaries_remain_explicit_blockers(self):
        result = build_aldrich_research_pattern_semantics(
            self._body(),
            skirt_length=600.0,
            variant=AldrichVariant.STANDARD,
        )

        blocker_codes = tuple(blocker.code for blocker in result.blockers)
        self.assertEqual(
            blocker_codes,
            (
                "WAIST_CURVE_UNRESOLVED",
                "SIDE_SEAM_CURVE_UNRESOLVED",
                "A_LINE_FLARE_NOT_APPLIED",
                "PRODUCTION_TRANSFORMS_UNRESOLVED",
            ),
        )
        self.assertFalse(hasattr(result, "dxf"))
        self.assertFalse(hasattr(result, "seam_allowance"))

    def test_invalid_skirt_length_safe_stops(self):
        with self.assertRaisesRegex(
            ValueError,
            "skirt_length must be greater than 0 mm",
        ):
            build_aldrich_research_pattern_semantics(
                self._body(),
                skirt_length=0.0,
                variant=AldrichVariant.STANDARD,
            )


if __name__ == "__main__":
    unittest.main()
