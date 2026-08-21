"""Regression tests for quadratic side-seam research experiment manifests."""

import math
import sys
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Point2D
from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
    SideSeamSegmentGeometryInput,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
    SchoolSkirtQuadraticBezierStrategyParameters,
)
from styles.school_skirt.side_seam_quadratic_experiment import (
    QuadraticResearchExperimentEvaluation,
    QuadraticResearchExperimentManifest,
    run_quadratic_research_experiment,
)


class SchoolSkirtSideSeamQuadraticExperimentTests(unittest.TestCase):
    def _parameters(
        self,
        *,
        upper_offset: float,
    ) -> SchoolSkirtQuadraticBezierStrategyParameters:
        return SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=upper_offset,
                sample_count=7,
            ),
            hip_to_hem=QuadraticBezierSegmentParameters(
                along_fraction=0.5,
                normal_offset=0.0,
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

    def _inputs(self):
        return (
            self._piecewise_input(upper_length=200.0, lower_length=300.0),
            self._piecewise_input(upper_length=203.0, lower_length=299.0),
        )

    def _manifest(self) -> QuadraticResearchExperimentManifest:
        return QuadraticResearchExperimentManifest(
            experiment_name="quadratic-upper-offset-study-01",
            candidates=(
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(upper_offset=8.0),
                ),
                NamedQuadraticCandidateSpec(
                    "quadratic-research-b",
                    self._parameters(upper_offset=20.0),
                ),
            ),
        )

    def test_manifest_fields_define_no_defaults_and_manifest_is_frozen(self):
        for field in fields(QuadraticResearchExperimentManifest):
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

        manifest = self._manifest()
        with self.assertRaises(FrozenInstanceError):
            manifest.experiment_name = "changed"

    def test_run_preserves_experiment_name_and_candidate_order(self):
        front, back = self._inputs()
        manifest = self._manifest()

        result = run_quadratic_research_experiment(
            front_input=front,
            back_input=back,
            manifest=manifest,
        )

        self.assertIsInstance(result, QuadraticResearchExperimentEvaluation)
        self.assertEqual(result.experiment_name, "quadratic-upper-offset-study-01")
        self.assertEqual(
            tuple(
                candidate.candidate_id
                for candidate in result.evaluation.collection.candidates
            ),
            ("quadratic-research-a", "quadratic-research-b"),
        )
        self.assertEqual(
            tuple(row.candidate_id for row in result.evaluation.snapshot.rows),
            ("quadratic-research-a", "quadratic-research-b"),
        )

    def test_distinct_manifest_configs_produce_distinct_measurements(self):
        front, back = self._inputs()

        result = run_quadratic_research_experiment(
            front_input=front,
            back_input=back,
            manifest=self._manifest(),
        )

        first = result.evaluation.snapshot.rows[0].waist_to_hip.back_minus_front
        second = result.evaluation.snapshot.rows[1].waist_to_hip.back_minus_front
        self.assertTrue(math.isfinite(first))
        self.assertTrue(math.isfinite(second))
        self.assertNotEqual(first, second)

    def test_experiment_name_is_preserved_without_normalization(self):
        front, back = self._inputs()
        manifest = QuadraticResearchExperimentManifest(
            experiment_name="  study 01  ",
            candidates=(),
        )

        result = run_quadratic_research_experiment(
            front_input=front,
            back_input=back,
            manifest=manifest,
        )

        self.assertEqual(result.experiment_name, "  study 01  ")

    def test_empty_manifest_builds_empty_collection_and_snapshot(self):
        front, back = self._inputs()
        manifest = QuadraticResearchExperimentManifest(
            experiment_name="empty-research-set",
            candidates=(),
        )

        result = run_quadratic_research_experiment(
            front_input=front,
            back_input=back,
            manifest=manifest,
        )

        self.assertEqual(result.evaluation.collection.candidates, ())
        self.assertEqual(result.evaluation.snapshot.rows, ())

    def test_downstream_candidate_validation_still_owns_duplicate_ids(self):
        front, back = self._inputs()
        manifest = QuadraticResearchExperimentManifest(
            experiment_name="duplicate-id-study",
            candidates=(
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(upper_offset=8.0),
                ),
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(upper_offset=20.0),
                ),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicate side-seam candidate_id: quadratic-research-a",
        ):
            run_quadratic_research_experiment(
                front_input=front,
                back_input=back,
                manifest=manifest,
            )

    def test_manifest_and_result_contain_no_selection_policy(self):
        front, back = self._inputs()
        manifest = self._manifest()
        result = run_quadratic_research_experiment(
            front_input=front,
            back_input=back,
            manifest=manifest,
        )

        for target in (
            manifest,
            result,
            result.evaluation,
            result.evaluation.snapshot,
        ):
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
