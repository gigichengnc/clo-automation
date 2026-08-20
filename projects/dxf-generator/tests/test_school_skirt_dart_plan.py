"""Regression tests for the resolved school-skirt semantic dart plan."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.dart_distribution import (
    PanelDartDistribution,
    SchoolSkirtDartDistribution,
)
from styles.school_skirt.dart_placement import (
    DartPlacement,
    PanelDartPlacement,
    SchoolSkirtDartPlacement,
)
from styles.school_skirt.dart_plan import build_school_skirt_dart_plan
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


class SchoolSkirtDartPlanTests(unittest.TestCase):
    def test_resolved_plan_preserves_indexed_semantics(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(15.0,)),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=(DartPlacement(0.42),)),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        plan = build_school_skirt_dart_plan(
            distribution,
            placement,
            SchoolSkirtDraftingParameters(),
        )

        self.assertEqual(
            [
                (dart.dart_index, dart.intake, dart.center_fraction, dart.length)
                for dart in plan.front.darts
            ],
            [(0, 15.0, 0.42, 100.0)],
        )
        self.assertEqual(
            [
                (dart.dart_index, dart.intake, dart.center_fraction, dart.length)
                for dart in plan.back.darts
            ],
            [
                (0, 10.0, 0.28, 120.0),
                (1, 20.0, 0.73, 120.0),
            ],
        )

    def test_zero_dart_panel_builds_empty_plan(self):
        parameters = SchoolSkirtDraftingParameters(
            front_dart_count=0,
            front_dart_length=0.0,
        )
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=()),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=()),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        plan = build_school_skirt_dart_plan(distribution, placement, parameters)

        self.assertEqual(plan.front.darts, ())

    def test_mismatched_distribution_and_placement_do_not_truncate_silently(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(15.0,)),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=()),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "validated dart distribution and placement must contain matching counts",
        ):
            build_school_skirt_dart_plan(
                distribution,
                placement,
                SchoolSkirtDraftingParameters(),
            )


if __name__ == "__main__":
    unittest.main()
