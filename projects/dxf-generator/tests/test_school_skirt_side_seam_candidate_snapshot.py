"""Regression tests for school-skirt side-seam candidate comparison snapshots."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.geometry_output import Path2D, Point2D
from styles.school_skirt.side_seam_candidate_collection import (
    SideSeamCandidateCollection,
)
from styles.school_skirt.side_seam_candidate_report import (
    build_side_seam_candidate_measurement_report,
)
from styles.school_skirt.side_seam_candidate_result import (
    NamedSideSeamCandidateResult,
)
from styles.school_skirt.side_seam_candidate_snapshot import (
    SideSeamCandidateComparisonSnapshot,
    SideSeamMismatchSnapshot,
    build_side_seam_candidate_comparison_snapshot,
)


class SchoolSkirtSideSeamCandidateSnapshotTests(unittest.TestCase):
    def _vertical_path(self, length: float) -> Path2D:
        return Path2D(points=(Point2D(0.0, 0.0), Point2D(0.0, -length)))

    def _candidate(
        self,
        candidate_id: str,
        *,
        upper_back: float,
        lower_back: float,
    ) -> NamedSideSeamCandidateResult:
        report = build_side_seam_candidate_measurement_report(
            front_waist_to_hip=self._vertical_path(200.0),
            front_hip_to_hem=self._vertical_path(300.0),
            back_waist_to_hip=self._vertical_path(upper_back),
            back_hip_to_hem=self._vertical_path(lower_back),
        )
        return NamedSideSeamCandidateResult(candidate_id, report)

    def test_snapshot_preserves_candidate_order_without_ranking(self):
        collection = SideSeamCandidateCollection(
            (
                self._candidate(
                    "linear-baseline", upper_back=203.0, lower_back=299.0
                ),
                self._candidate(
                    "legacy-reference", upper_back=204.0, lower_back=301.0
                ),
                self._candidate(
                    "future-curve-a", upper_back=201.0, lower_back=300.0
                ),
            )
        )

        snapshot = build_side_seam_candidate_comparison_snapshot(collection)

        self.assertEqual(
            tuple(row.candidate_id for row in snapshot.rows),
            ("linear-baseline", "legacy-reference", "future-curve-a"),
        )

    def test_snapshot_projects_upper_lower_and_total_mismatch_exactly(self):
        collection = SideSeamCandidateCollection(
            (
                self._candidate(
                    "linear-baseline", upper_back=203.0, lower_back=299.0
                ),
            )
        )

        row = build_side_seam_candidate_comparison_snapshot(collection).rows[0]

        self.assertEqual(
            row.waist_to_hip,
            SideSeamMismatchSnapshot(back_minus_front=3.0, absolute_difference=3.0),
        )
        self.assertEqual(
            row.hip_to_hem,
            SideSeamMismatchSnapshot(back_minus_front=-1.0, absolute_difference=1.0),
        )
        self.assertEqual(
            row.total,
            SideSeamMismatchSnapshot(back_minus_front=2.0, absolute_difference=2.0),
        )

    def test_empty_collection_builds_an_empty_snapshot(self):
        snapshot = build_side_seam_candidate_comparison_snapshot(
            SideSeamCandidateCollection(())
        )

        self.assertEqual(snapshot, SideSeamCandidateComparisonSnapshot(rows=()))

    def test_snapshot_contains_comparison_data_not_selection_policy(self):
        snapshot = build_side_seam_candidate_comparison_snapshot(
            SideSeamCandidateCollection(
                (
                    self._candidate(
                        "future-curve-a", upper_back=201.0, lower_back=300.0
                    ),
                )
            )
        )

        for target in (snapshot, snapshot.rows[0]):
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
