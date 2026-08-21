"""Regression tests for quadratic Bezier side-seam research parameter factories."""

import math
import sys
import unittest
from dataclasses import MISSING, fields
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_chord_relative_control_point import (
    ChordRelativeBezierControlPointRule,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_policy_candidate_runner import (
    run_side_seam_policy_candidate,
)
from styles.school_skirt.side_seam_quadratic_bezier_policy import (
    QuadraticBezierSideSeamSegmentPolicy,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
    SchoolSkirtQuadraticBezierStrategyParameters,
    build_quadratic_bezier_side_seam_strategy,
)


class SchoolSkirtSideSeamQuadraticCandidateFactoryTests(unittest.TestCase):
    def _parameters(self) -> SchoolSkirtQuadraticBezierStrategyParameters:
        return SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=12.0,
                sample_count=7,
            ),
            hip_to_hem=QuadraticBezierSegmentParameters(
                along_fraction=0.65,
                normal_offset=-8.0,
                sample_count=9,
            ),
        )

    def _piecewise_input(
        self,
        *,
        upper_length: float,
        lower_length: float,
    ) -> SideSeamPiecewiseGeometryInput:
        side_waist = Point2D(0.0, 0.0)
        hip_side = Point2D(0.0, -upper_length)
        hem_side = Point2D(0.0, -(upper_length + lower_length))
        return SideSeamPiecewiseGeometryInput(
            waist_to_hip=SideSeamSegmentGeometryInput(side_waist, hip_side),
            hip_to_hem=SideSeamSegmentGeometryInput(hip_side, hem_side),
        )

    def test_factory_maps_upper_and_lower_parameters_exactly(self):
        strategy = build_quadratic_bezier_side_seam_strategy(self._parameters())

        upper = strategy.waist_to_hip_policy
        lower = strategy.hip_to_hem_policy

        self.assertIsInstance(upper, QuadraticBezierSideSeamSegmentPolicy)
        self.assertIsInstance(lower, QuadraticBezierSideSeamSegmentPolicy)
        self.assertIsInstance(
            upper.control_point_rule,
            ChordRelativeBezierControlPointRule,
        )
        self.assertIsInstance(
            lower.control_point_rule,
            ChordRelativeBezierControlPointRule,
        )

        self.assertEqual(upper.control_point_rule.along_fraction, 0.5)
        self.assertEqual(upper.control_point_rule.normal_offset, 12.0)
        self.assertEqual(upper.sample_count, 7)
        self.assertEqual(lower.control_point_rule.along_fraction, 0.65)
        self.assertEqual(lower.control_point_rule.normal_offset, -8.0)
        self.assertEqual(lower.sample_count, 9)

    def test_parameter_specs_define_no_default_research_values(self):
        for field in fields(QuadraticBezierSegmentParameters):
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

        for field in fields(SchoolSkirtQuadraticBezierStrategyParameters):
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

    def test_upper_and_lower_parameter_sets_remain_independent(self):
        parameters = SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(0.5, 15.0, 5),
            hip_to_hem=QuadraticBezierSegmentParameters(0.25, 0.0, 11),
        )

        strategy = build_quadratic_bezier_side_seam_strategy(parameters)

        self.assertEqual(strategy.waist_to_hip_policy.sample_count, 5)
        self.assertEqual(strategy.hip_to_hem_policy.sample_count, 11)
        self.assertEqual(
            strategy.waist_to_hip_policy.control_point_rule.normal_offset,
            15.0,
        )
        self.assertEqual(
            strategy.hip_to_hem_policy.control_point_rule.normal_offset,
            0.0,
        )

    def test_invalid_sample_count_is_delegated_to_quadratic_policy_contract(self):
        parameters = SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(0.5, 12.0, 2),
            hip_to_hem=QuadraticBezierSegmentParameters(0.5, 0.0, 7),
        )

        with self.assertRaisesRegex(ValueError, "sample_count must be at least 3"):
            build_quadratic_bezier_side_seam_strategy(parameters)

    def test_invalid_control_parameters_are_delegated_to_control_point_contract(self):
        parameters = SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(math.nan, 12.0, 7),
            hip_to_hem=QuadraticBezierSegmentParameters(0.5, 0.0, 7),
        )

        with self.assertRaisesRegex(
            ValueError,
            "along_fraction must be a finite number",
        ):
            build_quadratic_bezier_side_seam_strategy(parameters)

    def test_factory_strategy_integrates_with_existing_candidate_runner(self):
        strategy = build_quadratic_bezier_side_seam_strategy(self._parameters())

        result = run_side_seam_policy_candidate(
            candidate_id="quadratic-research-a",
            front_input=self._piecewise_input(
                upper_length=200.0,
                lower_length=300.0,
            ),
            back_input=self._piecewise_input(
                upper_length=203.0,
                lower_length=299.0,
            ),
            strategy=strategy,
        )

        self.assertEqual(result.candidate_id, "quadratic-research-a")
        self.assertTrue(math.isfinite(result.report.waist_to_hip.back_minus_front))
        self.assertTrue(math.isfinite(result.report.hip_to_hem.back_minus_front))
        self.assertTrue(math.isfinite(result.report.total.back_minus_front))

    def test_factory_strategy_contains_geometry_policy_not_selection_policy(self):
        strategy = build_quadratic_bezier_side_seam_strategy(self._parameters())

        for target in (
            strategy,
            strategy.waist_to_hip_policy,
            strategy.hip_to_hem_policy,
        ):
            for attribute in (
                "rank",
                "score",
                "winner",
                "selected",
                "tolerance",
                "passes",
                "is_production",
            ):
                self.assertFalse(hasattr(target, attribute))


if __name__ == "__main__":
    unittest.main()
