"""DXF-first deterministic vector rendering primitives."""

from .loader import load_dxf_scene
from .model import Point2D, VectorPath, VectorScene
from .svg import scene_to_svg, write_svg

__all__ = [
    "Point2D",
    "VectorPath",
    "VectorScene",
    "load_dxf_scene",
    "scene_to_svg",
    "write_svg",
]
