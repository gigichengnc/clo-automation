"""Regression tests for research-only skirt panel-balance candidates."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.research.panel_balance_candidate import (
    PanelBalanceEvidence,
    evaluate_panel_balance_candidate,
)


class PanelBalanceCandidateTests(unittest.TestCase):
    def _draft(self) -> SchoolSkirtDraft:
        return SchoolSkirtDraft(
            quarter_waist=177.5,
            quarter_hip=232.5,
            quarter_suppression=55.0,
            hip_position=200.0,
            hem_position=500.0,
            hem_half_width=300.0,
        )

    def test_symmetric_candidate_can_conserve_global_suppression(self):
        candidate = PanelBalanceEvidence(
            front_hip_span=232.5,
            back_hip_span=232.5,
            front_finished_waist_span=177.5,
            back_finished_waist_span=177.5,
            provenance="architectural symmetric baseline",
        )

        evaluation = evaluate_panel_balance_candidate(self._draft(), candidate)

        self.assertEqual(candidate.targets.front, 55.0)
        self.assertEqual(candidate.targets.back, 55.0)
        self.assertTrue(evaluation.compatible_with_global_suppression)

    def test_asymmetric_candidate_can_conserve_global_suppression(self):
        candidate = PanelBalanceEvidence(
            front_hip_span=225.0,
            back_hip_span=240.0,
            front_finished_waist_span=177.5,
            back_finished_waist_span=177.5,
            provenance="Aldrich tailored-skirt research mapping",
        )

        evaluation = evaluate_panel_balance_candidate(self._draft(), candidate)

        self.assertEqual(candidate.targets.front, 47.5)
        self.assertEqual(candidate.targets.back, 62.5)
        self.assertEqual(candidate.targets.total, 110.0)
        self.assertTrue(evaluation.compatible_with_global_suppression)

    def test_candidate_with_wrong_global_total_is_rejected(self):
        candidate = PanelBalanceEvidence(
            front_hip_span=225.0,
            back_hip_span=240.0,
            front_finished_waist_span=180.0,
            back_finished_waist_span=180.0,
            provenance="deliberately inconsistent fixture",
        )

        evaluation = evaluate_panel_balance_candidate(self._draft(), candidate)

        self.assertFalse(evaluation.compatible_with_global_suppression)
        self.assertEqual(
            evaluation.validation_errors,
            (
                "front + back suppression targets must equal twice quarter_suppression (110.0 mm)",
            ),
        )

    def test_candidate_is_research_only_and_has_no_geometry(self):
        candidate = PanelBalanceEvidence(
            front_hip_span=232.5,
            back_hip_span=232.5,
            front_finished_waist_span=177.5,
            back_finished_waist_span=177.5,
            provenance="fixture",
        )

        self.assertEqual(candidate.status, "RESEARCH_CANDIDATE")
        self.assertEqual(candidate.production_status, "NOT_PRODUCTION_DEFAULT")
        self.assertFalse(hasattr(candidate, "geometry"))
        self.assertFalse(hasattr(candidate, "dxf"))
        self.assertFalse(hasattr(candidate, "coordinates"))


if __name__ == "__main__":
    unittest.main()
