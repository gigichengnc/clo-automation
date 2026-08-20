"""Regression tests for school-skirt dart-placement validation."""

import math
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from styles.school_skirt.dart_placement import (
    DartPlacement,
    PanelDartPlacement,
    SchoolSkirtDartPlacement,
)
from styles.school_skirt.dart_placement_validation import (
    validate_school_skirt_dart_placement,
)
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


class SchoolSkirtDartPlacementValidationTests(unittest.TestCase):
    def test_distinct_uneven_positions_are_valid(self):
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=(DartPlacement(0.42),)),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(
                SchoolSkirtDraftingParameters(),
                placement,
            ),
            [],
        )

    def test_dart_count_must_match_placement_count(self):
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(
                darts=(DartPlacement(0.3), DartPlacement(0.7)),
            ),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(
                SchoolSkirtDraftingParameters(),
                placement,
            ),
            ["front dart placement must contain exactly 1 dart(s)"],
        )

    def test_non_finite_position_is_rejected(self):
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=(DartPlacement(math.nan),)),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(
                SchoolSkirtDraftingParameters(),
                placement,
            ),
            ["front.darts[0].center_fraction must be a finite number"],
        )

    def test_position_outside_normalized_span_is_rejected(self):
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=(DartPlacement(1.01),)),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(
                SchoolSkirtDraftingParameters(),
                placement,
            ),
            [
                "front.darts[0].center_fraction must be between 0.0 and 1.0 inclusive"
            ],
        )

    def test_boundary_positions_remain_allowed(self):
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=(DartPlacement(0.0),)),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.0), DartPlacement(1.0)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(
                SchoolSkirtDraftingParameters(),
                placement,
            ),
            [],
        )

    def test_duplicate_positions_are_rejected_with_tolerance(self):
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=(DartPlacement(0.42),)),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.5), DartPlacement(0.5000005)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(
                SchoolSkirtDraftingParameters(),
                placement,
            ),
            [
                "back dart placements must not overlap within "
                "1e-06 normalized fraction"
            ],
        )

    def test_zero_dart_count_accepts_empty_placement(self):
        parameters = SchoolSkirtDraftingParameters(
            front_dart_count=0,
            front_dart_length=0.0,
        )
        placement = SchoolSkirtDartPlacement(
            front=PanelDartPlacement(darts=()),
            back=PanelDartPlacement(
                darts=(DartPlacement(0.28), DartPlacement(0.73)),
            ),
        )

        self.assertEqual(
            validate_school_skirt_dart_placement(parameters, placement),
            [],
        )


if __name__ == "__main__":
    unittest.main()
