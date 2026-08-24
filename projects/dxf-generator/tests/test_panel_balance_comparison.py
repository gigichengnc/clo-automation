"""Regression tests for the research-only panel-balance comparison runner."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from measurements.body import BodyMeasurements
from styles.school_skirt.research.aldrich_tailored_candidate import (
    AldrichVariant,
    build_aldrich_tailored_skirt_candidate,
)
from styles.school_skirt.research.panel_balance_comparison import (
    PanelBalanceComparisonContext,
    build_symmetric_panel_balance_baseline,
    compare_panel_balance_candidates,
    panel_balance_evidence_from_aldrich,
    render_panel_balance_comparison_markdown,
)


class PanelBalanceComparisonTests(unittest.TestCase):
    def _context(self) -> PanelBalanceComparisonContext:
        return PanelBalanceComparisonContext(
            body=BodyMeasurements(
                waist=700.0,
                hip=900.0,
                waist_to_hip=200.0,
            ),
            finished_waist=710.0,
            finished_hip=930.0,
        )

    def _report(self):
        context = self._context()
        aldrich = build_aldrich_tailored_skirt_candidate(
            context.body,
            variant=AldrichVariant.STANDARD,
        )
        return compare_panel_balance_candidates(
            context,
            (
                ("symmetric baseline", build_symmetric_panel_balance_baseline(context)),
                ("Aldrich standard", panel_balance_evidence_from_aldrich(aldrich)),
            ),
            excluded_candidates=(
                "49/51 published method: not instantiated because the current audit does not yet encode a complete same-finished-contract front/back waist allocation",
            ),
        )

    def test_shared_finished_contract_is_explicit(self):
        context = self._context()
        self.assertEqual(context.waist_ease, 10.0)
        self.assertEqual(context.hip_ease, 30.0)
        self.assertEqual(context.quarter_suppression, 55.0)

    def test_symmetric_and_aldrich_both_conserve_same_finished_contract(self):
        report = self._report()
        symmetric, aldrich = report.rows

        self.assertEqual((symmetric.front_target, symmetric.back_target), (55.0, 55.0))
        self.assertEqual((aldrich.front_target, aldrich.back_target), (47.5, 62.5))
        self.assertTrue(symmetric.conservation_pass)
        self.assertTrue(aldrich.conservation_pass)

    def test_candidate_spans_show_panel_balance_difference(self):
        report = self._report()
        symmetric, aldrich = report.rows

        self.assertEqual((symmetric.front_hip_span, symmetric.back_hip_span), (232.5, 232.5))
        self.assertEqual((aldrich.front_hip_span, aldrich.back_hip_span), (225.0, 240.0))
        self.assertEqual(
            (symmetric.front_finished_waist_span, symmetric.back_finished_waist_span),
            (177.5, 177.5),
        )
        self.assertEqual(
            (aldrich.front_finished_waist_span, aldrich.back_finished_waist_span),
            (177.5, 177.5),
        )

    def test_report_does_not_rank_or_promote_candidates(self):
        report = self._report()
        markdown = render_panel_balance_comparison_markdown(report)

        self.assertEqual(report.status, "RESEARCH_COMPARISON")
        self.assertEqual(report.production_status, "NOT_PRODUCTION_RANKING")
        self.assertIn("No candidate is ranked or selected", markdown)
        self.assertIn("NOT_APPROVED", markdown)
        self.assertIn("NOT_PRODUCTION_DEFAULT", markdown)
        self.assertNotIn("winner", markdown.lower())
        self.assertNotIn("best candidate", markdown.lower())

    def test_49_51_candidate_is_explicitly_excluded_not_guessed(self):
        report = self._report()
        self.assertEqual(len(report.excluded_candidates), 1)
        self.assertIn("49/51", report.excluded_candidates[0])
        self.assertIn("not instantiated", report.excluded_candidates[0])

    def test_report_generates_no_pattern_geometry_or_dxf(self):
        report = self._report()
        self.assertFalse(hasattr(report, "geometry"))
        self.assertFalse(hasattr(report, "dxf"))
        self.assertFalse(hasattr(report, "coordinates"))


if __name__ == "__main__":
    unittest.main()
