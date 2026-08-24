from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not (isfinite(self.x) and isfinite(self.y)):
            raise ValueError("Point coordinates must be finite")

    def mirror_x(self) -> "Point":
        return Point(-self.x, self.y)


@dataclass(frozen=True)
class Move:
    to: Point

    def mirror_x(self) -> "Move":
        return Move(self.to.mirror_x())


@dataclass(frozen=True)
class Line:
    to: Point

    def mirror_x(self) -> "Line":
        return Line(self.to.mirror_x())


@dataclass(frozen=True)
class Cubic:
    control1: Point
    control2: Point
    to: Point

    def mirror_x(self) -> "Cubic":
        return Cubic(self.control1.mirror_x(), self.control2.mirror_x(), self.to.mirror_x())


Command = Move | Line | Cubic


@dataclass(frozen=True)
class SemanticPath:
    path_id: str
    role: str
    commands: tuple[Command, ...]
    layer: str = "outline"

    def __post_init__(self) -> None:
        if not self.path_id:
            raise ValueError("path_id is required")
        if not self.role:
            raise ValueError("role is required")
        if not self.commands or not isinstance(self.commands[0], Move):
            raise ValueError("path must begin with Move")

    def mirror_x(self, *, path_id: str, role: str | None = None) -> "SemanticPath":
        return SemanticPath(
            path_id=path_id,
            role=role or self.role,
            commands=tuple(command.mirror_x() for command in self.commands),
            layer=self.layer,
        )


@dataclass(frozen=True)
class Drawing:
    drawing_id: str
    width: float
    height: float
    paths: tuple[SemanticPath, ...]

    def __post_init__(self) -> None:
        if not self.drawing_id:
            raise ValueError("drawing_id is required")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("drawing dimensions must be positive")
        ids = [path.path_id for path in self.paths]
        if len(ids) != len(set(ids)):
            raise ValueError("path IDs must be unique")

    def paths_by_role(self, role: str) -> tuple[SemanticPath, ...]:
        return tuple(path for path in self.paths if path.role == role)


def cubic_point(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    u = 1.0 - t
    return Point(
        u**3 * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t**3 * p3.x,
        u**3 * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t**3 * p3.y,
    )


def sample_path(path: SemanticPath, *, cubic_steps: int = 24) -> list[Point]:
    if cubic_steps < 2:
        raise ValueError("cubic_steps must be >= 2")
    points: list[Point] = []
    current: Point | None = None
    for command in path.commands:
        if isinstance(command, Move):
            current = command.to
            points.append(current)
        elif isinstance(command, Line):
            if current is None:
                raise ValueError("Line before Move")
            current = command.to
            points.append(current)
        elif isinstance(command, Cubic):
            if current is None:
                raise ValueError("Cubic before Move")
            start = current
            for i in range(1, cubic_steps + 1):
                points.append(cubic_point(start, command.control1, command.control2, command.to, i / cubic_steps))
            current = command.to
    return points
