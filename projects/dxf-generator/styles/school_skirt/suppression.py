"""Suppression-allocation contract for the school-skirt drafting layer.

This module defines the data exchanged between a policy-independent
``SchoolSkirtDraft`` and a future explicit suppression-allocation policy.
It deliberately provides no policy implementation and no fallback values.

A future policy must decide how each panel's quarter suppression is divided
between total dart intake and side-seam shaping. Distribution of total dart
intake across individual darts is a separate later decision.

All values use millimetres (mm).
"""

from dataclasses import dataclass
from typing import Protocol

from styles.school_skirt.draft import SchoolSkirtDraft
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters


@dataclass(frozen=True)
class PanelSuppressionAllocation:
    """Resolved suppression assigned to one panel."""

    dart_intake_total: float
    side_shaping: float


@dataclass(frozen=True)
class SchoolSkirtSuppressionAllocation:
    """Resolved front and back suppression allocations."""

    front: PanelSuppressionAllocation
    back: PanelSuppressionAllocation


class SchoolSkirtSuppressionPolicy(Protocol):
    """Contract implemented by an explicit school-skirt suppression policy."""

    def allocate(
        self,
        draft: SchoolSkirtDraft,
        parameters: SchoolSkirtDraftingParameters,
    ) -> SchoolSkirtSuppressionAllocation:
        """Return explicit front/back allocations for the supplied draft."""
        ...
