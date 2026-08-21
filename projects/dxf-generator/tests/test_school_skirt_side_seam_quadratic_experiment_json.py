"""Regression tests for the quadratic research experiment JSON text codec."""

import json
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
from styles.school_skirt.side_seam_quadratic_experiment_json import (
    dump_quadratic_research_experiment_manifest,
    load_quadratic_research_experiment_manifest,
)
from styles.school_skirt.side_seam_quadratic_experiment_serialization import (
    QUADRATIC_RESEARCH_EXPERIMENT_FORMAT,
    QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION,
    serialize_quadratic_research_experiment_manifest,
)


class SchoolSkirtSideSeamQuadraticExperimentJsonTests(unittest.TestCase):
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
                upper_fraction,
                upper_offset,
                upper_samples,
            ),
            hip_to_hem=QuadraticBezierSegmentParameters(
                lower_fraction,
                lower_offset,
                lower_samples,
            ),
        )

    def _manifest(self) -> QuadraticResearchExperimentManifest:
        return QuadraticResearchExperimentManifest(
            experiment_name="quadratic-曲線-study-01",
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

    def _valid_serialized_dict(self):
        return serialize_quadratic_research_experiment_manifest(self._manifest())

    def test_dump_is_deterministic_utf8_safe_pretty_json_with_one_trailing_newline(self):
        manifest = self._manifest()

        first = dump_quadratic_research_experiment_manifest(manifest)
        second = dump_quadratic_research_experiment_manifest(manifest)

        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertFalse(first.endswith("\n\n"))
        self.assertIn("quadratic-曲線-study-01", first)
        self.assertEqual(json.loads(first), self._valid_serialized_dict())

    def test_dump_then_load_round_trips_the_exact_manifest(self):
        manifest = self._manifest()

        loaded = load_quadratic_research_experiment_manifest(
            dump_quadratic_research_experiment_manifest(manifest)
        )

        self.assertEqual(loaded, manifest)

    def test_load_preserves_candidate_order_and_identity_without_normalization(self):
        serialized = self._valid_serialized_dict()
        serialized["experiment_name"] = "  study 01  "
        serialized["candidates"][0]["candidate_id"] = " candidate-a "

        loaded = load_quadratic_research_experiment_manifest(
            json.dumps(serialized, ensure_ascii=False)
        )

        self.assertEqual(loaded.experiment_name, "  study 01  ")
        self.assertEqual(
            tuple(candidate.candidate_id for candidate in loaded.candidates),
            (" candidate-a ", "quadratic-research-b"),
        )

    def test_empty_manifest_round_trips(self):
        manifest = QuadraticResearchExperimentManifest(
            experiment_name="empty-study",
            candidates=(),
        )

        loaded = load_quadratic_research_experiment_manifest(
            dump_quadratic_research_experiment_manifest(manifest)
        )

        self.assertEqual(loaded, manifest)

    def test_malformed_json_and_invalid_top_level_shape_safe_stop(self):
        with self.assertRaisesRegex(ValueError, "invalid experiment JSON"):
            load_quadratic_research_experiment_manifest("{not valid json}")

        with self.assertRaisesRegex(ValueError, "root must be a JSON object"):
            load_quadratic_research_experiment_manifest("[]")

        serialized = self._valid_serialized_dict()
        serialized["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "root has invalid shape"):
            load_quadratic_research_experiment_manifest(json.dumps(serialized))

    def test_unknown_format_and_version_safe_stop(self):
        serialized = self._valid_serialized_dict()
        serialized["format"] = "other-format"
        with self.assertRaisesRegex(ValueError, "unsupported experiment format"):
            load_quadratic_research_experiment_manifest(json.dumps(serialized))

        serialized = self._valid_serialized_dict()
        serialized["version"] = QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION + 1
        with self.assertRaisesRegex(
            ValueError,
            "unsupported experiment format version",
        ):
            load_quadratic_research_experiment_manifest(json.dumps(serialized))

        self.assertEqual(
            QUADRATIC_RESEARCH_EXPERIMENT_FORMAT,
            "school-skirt-quadratic-side-seam-research-experiment",
        )

    def test_duplicate_keys_and_non_standard_numeric_constants_safe_stop(self):
        duplicate_key_text = (
            '{"format":"school-skirt-quadratic-side-seam-research-experiment",'
            '"version":1,"version":1,"experiment_name":"study","candidates":[]}'
        )
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key: version"):
            load_quadratic_research_experiment_manifest(duplicate_key_text)

        nan_text = (
            '{"format":"school-skirt-quadratic-side-seam-research-experiment",'
            '"version":1,"experiment_name":"study","candidates":['
            '{"candidate_id":"a","parameters":{"waist_to_hip":'
            '{"along_fraction":0.5,"normal_offset":NaN,"sample_count":7},'
            '"hip_to_hem":{"along_fraction":0.5,"normal_offset":0.0,'
            '"sample_count":7}}}]}'
        )
        with self.assertRaisesRegex(
            ValueError,
            "non-standard JSON numeric constant: NaN",
        ):
            load_quadratic_research_experiment_manifest(nan_text)

    def test_wrong_primitive_types_and_nested_shape_safe_stop(self):
        serialized = self._valid_serialized_dict()
        serialized["version"] = True
        with self.assertRaisesRegex(ValueError, "root.version must be an integer"):
            load_quadratic_research_experiment_manifest(json.dumps(serialized))

        serialized = self._valid_serialized_dict()
        serialized["candidates"][0]["parameters"]["waist_to_hip"][
            "sample_count"
        ] = 7.5
        with self.assertRaisesRegex(ValueError, "sample_count must be an integer"):
            load_quadratic_research_experiment_manifest(json.dumps(serialized))

        serialized = self._valid_serialized_dict()
        del serialized["candidates"][0]["parameters"]["hip_to_hem"]["normal_offset"]
        with self.assertRaisesRegex(ValueError, "hip_to_hem has invalid shape"):
            load_quadratic_research_experiment_manifest(json.dumps(serialized))


if __name__ == "__main__":
    unittest.main()
