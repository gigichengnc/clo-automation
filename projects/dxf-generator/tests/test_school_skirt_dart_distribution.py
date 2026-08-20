"""Regression tests for school-skirt individual dart-distribution validation."""

import math
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
from styles.school_skirt.dart_distribution_validation import (
    validate_school_skirt_dart_distribution,
)
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.suppression import (
    PanelSuppressionAllocation,
    SchoolSkirtSuppressionAllocation,
)


class SchoolSkirtDartDistributionValidationTests(unittest.TestCase):
    def _allocation(
        self,
        *,
        front_dart_total: float = 15.0,
        back_dart_total: float = 30.0,
    ) -> SchoolSkirtSuppressionAllocation:
        return SchoolSkirtSuppressionAllocation(
            front=PanelSuppressionAllocation(
                dart_intake_total=front_dart_total,
                side_shaping=30.0,
            ),
            back=PanelSuppressionAllocation(
                dart_intake_total=back_dart_total,
                side_shaping=15.0,
            ),
        )

    def test_uneven_distribution_is_valid_when_totals_match(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(15.0,)),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(),
                SchoolSkirtDraftingParameters(),
                distribution,
            ),
            [],
        )

    def test_dart_count_must_match_distribution_length(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(7.5, 7.5)),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(),
                SchoolSkirtDraftingParameters(),
                distribution,
            ),
            ["front dart distribution must contain exactly 1 intake value(s)"],
        )

    def test_negative_individual_intake_is_rejected(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(15.0,)),
            back=PanelDartDistribution(dart_intakes=(-1.0, 31.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(),
                SchoolSkirtDraftingParameters(),
                distribution,
            ),
            ["back.dart_intakes[0] must be greater than or equal to 0 mm"],
        )

    def test_non_finite_individual_intake_is_rejected(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(math.nan,)),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(),
                SchoolSkirtDraftingParameters(),
                distribution,
            ),
            ["front.dart_intakes[0] must be a finite number"],
        )

    def test_dart_intake_sum_must_match_allocation(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(14.0,)),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(),
                SchoolSkirtDraftingParameters(),
                distribution,
            ),
            [
                "front dart intake sum must equal front.dart_intake_total "
                "(15.0 mm)"
            ],
        )

    def test_zero_dart_count_accepts_empty_distribution_when_total_is_zero(self):
        parameters = SchoolSkirtDraftingParameters(
            front_dart_count=0,
            front_dart_length=0.0,
        )
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=()),
            back=PanelDartDistribution(dart_intakes=(10.0, 20.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(front_dart_total=0.0),
                parameters,
                distribution,
            ),
            [],
        )

    def test_tiny_floating_point_difference_is_tolerated(self):
        distribution = SchoolSkirtDartDistribution(
            front=PanelDartDistribution(dart_intakes=(15.0,)),
            back=PanelDartDistribution(dart_intakes=(9.9999995, 20.0)),
        )

        self.assertEqual(
            validate_school_skirt_dart_distribution(
                self._allocation(),
                SchoolSkirtDraftingParameters(),
                distribution,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
