"""Regression tests for quadratic research experiment serialization."""

import json
import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
    SchoolSkirtQuadraticBezierStrategyParameters,
)
from styles.school_skirt.side_seam_quadratic_experiment import (
    QuadraticResearchExperimentManifest,
)
from styles.school_skirt.side_seam_quadratic_experiment_serialization import (
    QUADRATIC_RESEARCH_EXPERIMENT_FORMAT,
    QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION,
    serialize_quadratic_research_experiment_manifest,
)


class SchoolSkirtSideSeamQuadraticExperimentSerializationTests(unittest.TestCase):
    def _parameters(
        self,
        *,
        upper_fraction: float,
        upper_offset: float,
        upper_samples: int,
        lower_fraction: float,
        lower_offset: float,
        lower_samples: int,
    ) -> SchoolSkirtQuadraticBezierStrategyParameters:
        return SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=QuadraticBezierSegmentParameters(
                along_fraction=upper_fraction,
                normal_offset=upper_offset,
                sample_count=upper_samples,
            ),
            hip_to_hem=QuadraticBezierSegmentParameters(
                along_fraction=lower_fraction,
                normal_offset=lower_offset,
                sample_count=lower_samples,
            ),
        )

    def _manifest(self) -> QuadraticResearchExperimentManifest:
        return QuadraticResearchExperimentManifest(
            experiment_name="quadratic-upper-offset-study-01",
            candidates=(
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(
                        upper_fraction=0.5,
                        upper_offset=8.0,
                        upper_samples=7,
                        lower_fraction=0.5,
                        lower_offset=0.0,
                        lower_samples=7,
                    ),
                ),
                NamedQuadraticCandidateSpec(
                    "quadratic-research-b",
                    self._parameters(
                        upper_fraction=0.65,
                        upper_offset=20.0,
                        upper_samples=9,
                        lower_fraction=0.4,
                        lower_offset=-6.0,
                        lower_samples=11,
                    ),
                ),
            ),
        )

    def test_serialization_has_exact_versioned_json_shape(self):
        serialized = serialize_quadratic_research_experiment_manifest(
            self._manifest()
        )

        self.assertEqual(
            serialized,
            {
                "format": "school-skirt-quadratic-side-seam-research-experiment",
                "version": 1,
                "experiment_name": "quadratic-upper-offset-study-01",
                "candidates": [
                    {
                        "candidate_id": "quadratic-research-a",
                        "parameters": {
                            "waist_to_hip": {
                                "along_fraction": 0.5,
                                "normal_offset": 8.0,
                                "sample_count": 7,
                            },
                            "hip_to_hem": {
                                "along_fraction": 0.5,
                                "normal_offset": 0.0,
                                "sample_count": 7,
                            },
                        },
                    },
                    {
                        "candidate_id": "quadratic-research-b",
                        "parameters": {
                            "waist_to_hip": {
                                "along_fraction": 0.65,
                                "normal_offset": 20.0,
                                "sample_count": 9,
                            },
                            "hip_to_hem": {
                                "along_fraction": 0.4,
                                "normal_offset": -6.0,
                                "sample_count": 11,
                            },
                        },
                    },
                ],
            },
        )
        self.assertEqual(
            serialized["format"],
            QUADRATIC_RESEARCH_EXPERIMENT_FORMAT,
        )
        self.assertEqual(
            serialized["version"],
            QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION,
        )

    def test_candidate_order_is_preserved_as_json_array_order(self):
        serialized = serialize_quadratic_research_experiment_manifest(
            self._manifest()
        )

        self.assertEqual(
            tuple(candidate["candidate_id"] for candidate in serialized["candidates"]),
            ("quadratic-research-a", "quadratic-research-b"),
        )

    def test_experiment_and_candidate_identity_are_not_normalized(self):
        manifest = QuadraticResearchExperimentManifest(
            experiment_name="  study 01  ",
            candidates=(
                NamedQuadraticCandidateSpec(
                    " quadratic-research-a ",
                    self._parameters(
                        upper_fraction=0.5,
                        upper_offset=8.0,
                        upper_samples=7,
                        lower_fraction=0.5,
                        lower_offset=0.0,
                        lower_samples=7,
                    ),
                ),
            ),
        )

        serialized = serialize_quadratic_research_experiment_manifest(manifest)

        self.assertEqual(serialized["experiment_name"], "  study 01  ")
        self.assertEqual(
            serialized["candidates"][0]["candidate_id"],
            " quadratic-research-a ",
        )

    def test_empty_manifest_serializes_to_empty_candidate_array(self):
        serialized = serialize_quadratic_research_experiment_manifest(
            QuadraticResearchExperimentManifest(
                experiment_name="empty-research-set",
                candidates=(),
            )
        )

        self.assertEqual(serialized["candidates"], [])

    def test_repeated_serialization_is_deterministic_and_standard_json_compatible(self):
        manifest = self._manifest()

        first = serialize_quadratic_research_experiment_manifest(manifest)
        second = serialize_quadratic_research_experiment_manifest(manifest)

        self.assertEqual(first, second)
        first_json = json.dumps(first, allow_nan=False, separators=(",", ":"))
        second_json = json.dumps(second, allow_nan=False, separators=(",", ":"))
        self.assertEqual(first_json, second_json)

    def test_non_finite_numeric_value_is_rejected_as_non_standard_json(self):
        manifest = QuadraticResearchExperimentManifest(
            experiment_name="invalid-numeric-study",
            candidates=(
                NamedQuadraticCandidateSpec(
                    "quadratic-research-a",
                    self._parameters(
                        upper_fraction=0.5,
                        upper_offset=math.nan,
                        upper_samples=7,
                        lower_fraction=0.5,
                        lower_offset=0.0,
                        lower_samples=7,
                    ),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            serialize_quadratic_research_experiment_manifest(manifest)

    def test_serialized_contract_contains_research_data_not_selection_policy(self):
        serialized = serialize_quadratic_research_experiment_manifest(
            self._manifest()
        )
        serialized_text = json.dumps(serialized, allow_nan=False)

        for forbidden in (
            "rank",
            "ranking",
            "score",
            "winner",
            "selected",
            "tolerance",
            "passes",
            "is_production",
        ):
            self.assertNotIn(forbidden, serialized_text)


if __name__ == "__main__":
    unittest.main()
