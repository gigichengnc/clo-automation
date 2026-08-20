"""Dart-placement contract for the school-skirt drafting layer.

This module defines the data exchanged between validated dart-distribution
results and a future explicit dart-placement policy. It deliberately provides
no placement algorithm, no equal-spacing fallback, and no legacy segment
formula.

Each dart is represented by a normalized centre position along its panel waist
span: 0.0 is the centre edge and 1.0 is the side-seam edge. This keeps placement
semantic and dimensionless; later geometry is responsible for mapping the
position onto physical coordinates.

Dart intake, dart length, and coordinate geometry remain separate concerns.
"""

from dataclasses import dataclass
from typing import Protocol

from styles.school_skirt.dart_distribution import SchoolSkirtDartDistribution
from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.suppression import SchoolSkirtSuppressionAllocation


@dataclass(frozen=True)
class DartPlacement:
    """One dart centre expressed along a normalized panel-waist span."""

    center_fraction: float


@dataclass(frozen=True)
class PanelDartPlacement:
    """Resolved dart placements for one panel."""

    darts: tuple[DartPlacement, ...]


@dataclass(frozen=True)
class SchoolSkirtDartPlacement:
    """Resolved front and back dart placements."""

    front: PanelDartPlacement
    back: PanelDartPlacement


class SchoolSkirtDartPlacementPolicy(Protocol):
    """Contract implemented by an explicit school-skirt placement policy."""

    def place(
        self,
        draft: SchoolSkirtDraft,
        allocation: SchoolSkirtSuppressionAllocation,
        distribution: SchoolSkirtDartDistribution,
        parameters: SchoolSkirtDraftingParameters,
    ) -> SchoolSkirtDartPlacement:
        """Return explicit normalized dart-centre placements."""
        ...
