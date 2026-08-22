"""Regression tests for quadratic research experiment filesystem I/O."""

import sys
import tempfile
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
from styles.school_skirt.side_seam_quadratic_experiment_file import (
    read_quadratic_research_experiment_file,
    write_quadratic_research_experiment_file,
)
from styles.school_skirt.side_seam_quadratic_experiment_json import (
    dump_quadratic_research_experiment_manifest,
)


class SchoolSkirtSideSeamQuadraticExperimentFileTests(unittest.TestCase):
    def _manifest(self) -> QuadraticResearchExperimentManifest:
        return QuadraticResearchExperimentManifest(
            experiment_name="quadratic-曲線-study-01",
            candidates=(
                NamedQuadraticCandidateSpec(
                    candidate_id="quadratic-research-a",
                    parameters=SchoolSkirtQuadraticBezierStrategyParameters(
                        waist_to_hip=QuadraticBezierSegmentParameters(0.5, 8.0, 7),
                        hip_to_hem=QuadraticBezierSegmentParameters(0.5, 0.0, 7),
                    ),
                ),
                NamedQuadraticCandidateSpec(
                    candidate_id="quadratic-research-b",
                    parameters=SchoolSkirtQuadraticBezierStrategyParameters(
                        waist_to_hip=QuadraticBezierSegmentParameters(0.65, 20.0, 9),
                        hip_to_hem=QuadraticBezierSegmentParameters(0.4, -6.0, 11),
                    ),
                ),
            ),
        )

    def test_write_then_read_round_trips_exact_manifest(self):
        manifest = self._manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "experiment.json"

            write_quadratic_research_experiment_file(path, manifest)
            loaded = read_quadratic_research_experiment_file(path)

        self.assertEqual(loaded, manifest)

    def test_written_text_exactly_matches_deterministic_json_codec(self):
        manifest = self._manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "experiment.json"

            write_quadratic_research_experiment_file(path, manifest)
            written = path.read_text(encoding="utf-8")

        self.assertEqual(written, dump_quadratic_research_experiment_manifest(manifest))
        self.assertTrue(written.endswith("\n"))
        self.assertFalse(written.endswith("\n\n"))

    def test_utf8_identity_is_preserved_on_disk(self):
        manifest = self._manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "曲線-experiment.json"

            write_quadratic_research_experiment_file(path, manifest)
            raw = path.read_bytes()
            loaded = read_quadratic_research_experiment_file(path)

        self.assertIn("quadratic-曲線-study-01".encode("utf-8"), raw)
        self.assertEqual(loaded.experiment_name, "quadratic-曲線-study-01")

    def test_string_paths_are_supported_without_changing_file_identity(self):
        manifest = self._manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "experiment.json"

            write_quadratic_research_experiment_file(str(path), manifest)
            loaded = read_quadratic_research_experiment_file(str(path))

        self.assertEqual(loaded, manifest)

    def test_missing_file_error_is_not_wrapped_or_suppressed(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"

            with self.assertRaises(FileNotFoundError):
                read_quadratic_research_experiment_file(missing)

    def test_missing_parent_directory_is_not_created_implicitly(self):
        manifest = self._manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not-created" / "experiment.json"

            with self.assertRaises(FileNotFoundError):
                write_quadratic_research_experiment_file(path, manifest)

            self.assertFalse(path.parent.exists())

    def test_invalid_json_file_delegates_to_strict_text_codec(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("{not valid json}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "invalid experiment JSON"):
                read_quadratic_research_experiment_file(path)

    def test_file_adapter_contains_no_selection_policy(self):
        manifest = self._manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "experiment.json"
            write_quadratic_research_experiment_file(path, manifest)
            loaded = read_quadratic_research_experiment_file(path)

        for target in (manifest, loaded):
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
