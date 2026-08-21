"""Regression tests for named quadratic Bezier side-seam research candidates."""

import math
import sys
import unittest
from dataclasses import MISSING, fields
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_multi_policy_runner import (
    run_side_seam_policy_candidates,
)
from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
    build_quadratic_policy_candidate_spec,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_quadratic_bezier_policy import (
    QuadraticBezierSideSeamSegmentPolicy,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
    SchoolSkirtQuadraticBezierStrategyParameters,
)


class SchoolSkirtSideSeamNamedQuadraticCandidateTests(unittest.TestCase):
    def _parameters(
        self,
        *,
        upper_offset: float = 12.0,
        lower_offset: float = 0.0,
    ) -> SchoolSkirtQuadraticBezierStrategyParameters:
        return SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=upper_offset,
                sample_count=7,
            ),
            hip_to_hem=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=lower_offset,
                sample_count=7,
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

    def test_named_spec_defines_no_default_identity_or_parameters(self):
        for field in fields(NamedQuadraticCandidateSpec):
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

    def test_adapter_preserves_candidate_id_and_maps_parameters_exactly(self):
        named = NamedQuadraticCandidateSpec(
            candidate_id="quadratic-research-a",
            parameters=self._parameters(upper_offset=12.0, lower_offset=-8.0),
        )

        policy_spec = build_quadratic_policy_candidate_spec(named)

        self.assertEqual(policy_spec.candidate_id, "quadratic-research-a")
        self.assertIsInstance(
            policy_spec.strategy.waist_to_hip_policy,
            QuadraticBezierSideSeamSegmentPolicy,
        )
        self.assertEqual(
            policy_spec.strategy.waist_to_hip_policy.control_point_rule.normal_offset,
            12.0,
        )
        self.assertEqual(
            policy_spec.strategy.hip_to_hem_policy.control_point_rule.normal_offset,
            -8.0,
        )
        self.assertEqual(policy_spec.strategy.waist_to_hip_policy.sample_count, 7)
        self.assertEqual(policy_spec.strategy.hip_to_hem_policy.sample_count, 7)

    def test_adapter_does_not_normalize_candidate_identity(self):
        named = NamedQuadraticCandidateSpec(
            candidate_id=" quadratic-research-a ",
            parameters=self._parameters(),
        )

        policy_spec = build_quadratic_policy_candidate_spec(named)

        self.assertEqual(policy_spec.candidate_id, " quadratic-research-a ")

    def test_invalid_parameters_are_delegated_to_existing_strategy_factory(self):
        named = NamedQuadraticCandidateSpec(
            candidate_id="quadratic-research-a",
            parameters=SchoolSkirtQuadraticBezierStrategyParameters(
                waist_to_hip=QuadraticBezierSegmentParameters(0.5, 12.0, 2),
                hip_to_hem=QuadraticBezierSegmentParameters(0.5, 0.0, 7),
            ),
        )

        with self.assertRaisesRegex(ValueError, "sample_count must be at least 3"):
            build_quadratic_policy_candidate_spec(named)

    def test_invalid_candidate_identity_safe_stops_only_in_existing_run_pipeline(self):
        named = NamedQuadraticCandidateSpec(
            candidate_id=" quadratic-research-a ",
            parameters=self._parameters(),
        )
        policy_spec = build_quadratic_policy_candidate_spec(named)
        valid = self._piecewise_input(upper_length=200.0, lower_length=300.0)

        with self.assertRaisesRegex(
            ValueError,
            "candidate_id must not contain leading or trailing whitespace",
        ):
            run_side_seam_policy_candidates(
                front_input=valid,
                back_input=valid,
                candidates=(policy_spec,),
            )

    def test_distinct_named_parameter_configs_integrate_with_multi_policy_comparison(self):
        front = self._piecewise_input(upper_length=200.0, lower_length=300.0)
        back = self._piecewise_input(upper_length=203.0, lower_length=299.0)
        named_candidates = (
            NamedQuadraticCandidateSpec(
                "quadratic-research-a",
                self._parameters(upper_offset=8.0),
            ),
            NamedQuadraticCandidateSpec(
                "quadratic-research-b",
                self._parameters(upper_offset=20.0),
            ),
        )

        evaluation = run_side_seam_policy_candidates(
            front_input=front,
            back_input=back,
            candidates=tuple(
                build_quadratic_policy_candidate_spec(candidate)
                for candidate in named_candidates
            ),
        )

        self.assertEqual(
            tuple(row.candidate_id for row in evaluation.snapshot.rows),
            ("quadratic-research-a", "quadratic-research-b"),
        )
        first_upper = evaluation.snapshot.rows[0].waist_to_hip.back_minus_front
        second_upper = evaluation.snapshot.rows[1].waist_to_hip.back_minus_front
        self.assertTrue(math.isfinite(first_upper))
        self.assertTrue(math.isfinite(second_upper))
        self.assertNotEqual(first_upper, second_upper)

    def test_named_spec_and_adapter_output_contain_no_selection_policy(self):
        named = NamedQuadraticCandidateSpec(
            candidate_id="quadratic-research-a",
            parameters=self._parameters(),
        )
        policy_spec = build_quadratic_policy_candidate_spec(named)

        for target in (named, policy_spec, policy_spec.strategy):
            for attribute in (
                "rank",
                "ranking",
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
