"""Drafting parameters for the school-skirt style.

These values are separated from body and garment measurements so style choices
remain explicit. This module contains no pattern geometry and does not generate
or modify DXF files.

All values use millimetres (mm).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SchoolSkirtDraftingParameters:
    """Style-specific constants used by the school-skirt drafting layer."""

    flare: float = 80.0
    front_dart_take: float = 25.0
    front_dart_length: float = 100.0
    back_dart_take: float = 25.0
    back_dart_length: float = 120.0
    waistband_height: float = 70.0
