"""Drafting parameters for the school-skirt style.

These values are separated from body and garment measurements so style choices
remain explicit. Dart intake is deliberately not defined here because it must
be resolved from garment suppression by an explicit drafting policy.

This module contains no pattern geometry and does not generate or modify DXF
files. All values use millimetres (mm) unless otherwise stated.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SchoolSkirtDraftingParameters:
    """Style-specific choices used by the school-skirt drafting layer."""

    flare: float = 80.0
    front_dart_count: int = 1
    front_dart_length: float = 100.0
    back_dart_count: int = 2
    back_dart_length: float = 120.0
    waistband_height: float = 70.0
