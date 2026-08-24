"""Suppression contracts for the school-skirt drafting layer.

This module separates two drafting decisions that were previously collapsed:

1. how the garment's required waist-to-hip suppression is allocated between
   the front and back panel families;
2. how each panel target is then divided between dart intake and side shaping.

The policy-independent draft supplies only the global suppression requirement.
No equal-front/back split, dart ratio, side-shaping ratio or fallback is chosen
here.

All values use millimetres (mm).
"""

from dataclasses import dataclass
from typing import Protocol

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


@dataclass(frozen=True)
class PanelSuppressionTargets:
    """Required total suppression for the front and back panel families."""

    front: float
    back: float

    @property
    def total(self) -> float:
        """Return the half-garment suppression represented by front + back."""
        return self.front + self.back


@dataclass(frozen=True)
class PanelSuppressionAllocation:
    """Resolved suppression mechanisms assigned to one panel family."""

    dart_intake_total: float
    side_shaping: float

    @property
    def total(self) -> float:
        return self.dart_intake_total + self.side_shaping


@dataclass(frozen=True)
class SchoolSkirtSuppressionAllocation:
    """Resolved front and back suppression mechanisms."""

    front: PanelSuppressionAllocation
    back: PanelSuppressionAllocation


class SchoolSkirtPanelSuppressionPolicy(Protocol):
    """Contract for an explicit front/back suppression-target policy."""

    def allocate_targets(
        self,
        draft: SchoolSkirtDraft,
        parameters: SchoolSkirtDraftingParameters,
    ) -> PanelSuppressionTargets:
        """Return explicit front/back suppression targets for the draft."""
        ...


class SchoolSkirtSuppressionPolicy(Protocol):
    """Contract for dividing panel targets into darts and side shaping."""

    def allocate(
        self,
        draft: SchoolSkirtDraft,
        targets: PanelSuppressionTargets,
        parameters: SchoolSkirtDraftingParameters,
    ) -> SchoolSkirtSuppressionAllocation:
        """Return dart/side allocations that satisfy the supplied targets."""
        ...
