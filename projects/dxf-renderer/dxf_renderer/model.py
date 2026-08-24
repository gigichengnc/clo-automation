from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float


@dataclass(frozen=True)
class VectorPath:
    points: tuple[Point2D, ...]
    closed: bool
    layer: str
    source: str | None = None
    entity_type: str | None = None

    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError("VectorPath requires at least two points")


@dataclass(frozen=True)
class VectorScene:
    paths: tuple[VectorPath, ...]
    units: str = "mm"

    @classmethod
    def from_paths(cls, paths: Iterable[VectorPath], units: str = "mm") -> "VectorScene":
        return cls(tuple(paths), units=units)

    def filtered(self, layers: set[str] | None = None) -> "VectorScene":
        if layers is None:
            return self
        return VectorScene(tuple(path for path in self.paths if path.layer in layers), units=self.units)

    def bounds(self) -> tuple[float, float, float, float]:
        if not self.paths:
            raise ValueError("Cannot compute bounds of an empty scene")
        xs = [point.x for path in self.paths for point in path.points]
        ys = [point.y for path in self.paths for point in path.points]
        return min(xs), min(ys), max(xs), max(ys)
