"""Individual dart-intake distribution contract for the school-skirt layer.

This module defines the data exchanged between a validated suppression
allocation and a future explicit dart-distribution policy. It deliberately
provides no distribution algorithm, no equal-split fallback, and no legacy
25 mm intake assumption.

A future policy may use the draft, suppression allocation, and style parameters
to decide how each panel's total dart intake is divided across its individual
darts. Dart positions, dart lengths, and coordinate geometry remain separate
later decisions.

All values use millimetres (mm).
"""

from dataclasses import dataclass
from typing import Protocol

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.suppression import SchoolSkirtSuppressionAllocation


@dataclass(frozen=True)
class PanelDartDistribution:
    """Resolved individual dart intakes for one panel."""

    dart_intakes: tuple[float, ...]


@dataclass(frozen=True)
class SchoolSkirtDartDistribution:
    """Resolved front and back individual dart-intake distributions."""

    front: PanelDartDistribution
    back: PanelDartDistribution


class SchoolSkirtDartDistributionPolicy(Protocol):
    """Contract implemented by an explicit school-skirt dart policy."""

    def distribute(
        self,
        draft: SchoolSkirtDraft,
        allocation: SchoolSkirtSuppressionAllocation,
        parameters: SchoolSkirtDraftingParameters,
    ) -> SchoolSkirtDartDistribution:
        """Return explicit per-dart intakes for the supplied allocation."""
        ...
