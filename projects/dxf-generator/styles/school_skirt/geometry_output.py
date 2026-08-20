"""Coordinate-geometry output contract for the school-skirt drafting layer.

This module defines the semantic coordinate records that a future geometry
implementation may produce from validated ``PanelGeometryInput`` values. It
contains no drafting algorithm, no side-seam or hem curve formula, no seam
allowance logic, and no DXF adapter behavior.

Panel outline edges remain semantically separated as centre edge, waist, side
seam, and hem so downstream production and adapter layers do not need to infer
edge identity from coordinates, layer numbers, or position heuristics.

All coordinates use millimetres (mm).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Point2D:
    """One Cartesian point in millimetres."""

    x: float
    y: float


@dataclass(frozen=True)
class Path2D:
    """Ordered sampled points representing one semantic geometric path."""

    points: tuple[Point2D, ...]


@dataclass(frozen=True)
class DartGeometry:
    """Coordinate representation of one resolved dart."""

    dart_index: int
    left_waist: Point2D
    apex: Point2D
    right_waist: Point2D


@dataclass(frozen=True)
class PanelOutline:
    """Semantic outer edges of one skirt panel."""

    centre_edge: Path2D
    waist: Path2D
    side_seam: Path2D
    hem: Path2D


@dataclass(frozen=True)
class PanelGeometry:
    """Coordinate geometry for one panel before production allowances."""

    outline: PanelOutline
    darts: tuple[DartGeometry, ...]


@dataclass(frozen=True)
class SchoolSkirtGeometry:
    """Front and back coordinate geometry for the school-skirt style."""

    front: PanelGeometry
    back: PanelGeometry
