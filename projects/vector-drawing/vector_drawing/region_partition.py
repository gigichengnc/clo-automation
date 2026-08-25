"""Research-only raster-region partition to layered SVG prototype.

This module tests one narrow claim:

    normalized raster partition -> closed vector fill regions + independent line layer

It does NOT perform image segmentation, semantic recognition, curve fitting,
AI generation, garment drafting, or production DXF export.

The input is already a *partition*: every cell has exactly one region label.
That distinction matters because raw segmentation masks may overlap or leave
unassigned pixels and therefore do not automatically provide the topology this
module relies on.

The vectorizer traces cell-boundary loops exactly on the integer grid. It is a
Step-0 topology experiment, not a final smooth-line renderer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from html import escape
from typing import Iterable


OUTSIDE = "__outside__"
Point = tuple[int, int]
Edge = tuple[Point, Point]


class BoundaryRole(str, Enum):
    """How a boundary participates in the layered visual document."""

    REGION_BOUNDARY = "region_boundary"
    INTERNAL_DETAIL = "internal_detail"
    CONSTRUCTION = "construction"
    OCCLUSION = "occlusion"
    FILL_ONLY = "fill_only"


@dataclass(frozen=True)
class RegionPartition:
    """A rectangular labelled raster in which every cell has one region id."""

    rows: tuple[tuple[str, ...], ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("partition must contain at least one row")
        width = len(self.rows[0])
        if width == 0:
            raise ValueError("partition rows must contain at least one cell")
        for row_index, row in enumerate(self.rows):
            if len(row) != width:
                raise ValueError("partition rows must have equal width")
            for column_index, label in enumerate(row):
                if not isinstance(label, str) or not label:
                    raise ValueError(
                        f"partition label at ({column_index}, {row_index}) must be a non-empty string"
                    )

    @property
    def width(self) -> int:
        return len(self.rows[0])

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def region_ids(self) -> tuple[str, ...]:
        return tuple(sorted({label for row in self.rows for label in row}))


@dataclass(frozen=True)
class RegionLoop:
    region_id: str
    points: tuple[Point, ...]

    @property
    def closed(self) -> bool:
        return len(self.points) >= 4 and self.points[0] == self.points[-1]


@dataclass(frozen=True)
class LayeredRegionDocument:
    partition: RegionPartition
    loops: tuple[RegionLoop, ...]
    palette: tuple[tuple[str, str], ...]
    boundary_roles: tuple[tuple[str, str, BoundaryRole], ...]
    status: str = "RESEARCH_LAYERED_REGION_DOCUMENT"
    production_status: str = "NOT_PRODUCTION_OUTPUT"


def _cell(partition: RegionPartition, x: int, y: int) -> str:
    if x < 0 or y < 0 or x >= partition.width or y >= partition.height:
        return OUTSIDE
    return partition.rows[y][x]


def _region_boundary_edges(partition: RegionPartition, region_id: str) -> set[Edge]:
    """Return directed cell-boundary edges with region interior on the left."""

    edges: set[Edge] = set()
    for y, row in enumerate(partition.rows):
        for x, label in enumerate(row):
            if label != region_id:
                continue

            if _cell(partition, x, y - 1) != region_id:  # top
                edges.add(((x + 1, y), (x, y)))
            if _cell(partition, x + 1, y) != region_id:  # right
                edges.add(((x + 1, y + 1), (x + 1, y)))
            if _cell(partition, x, y + 1) != region_id:  # bottom
                edges.add(((x, y + 1), (x + 1, y + 1)))
            if _cell(partition, x - 1, y) != region_id:  # left
                edges.add(((x, y), (x, y + 1)))
    return edges


def _chain_directed_loops(region_id: str, edges: set[Edge]) -> tuple[RegionLoop, ...]:
    """Chain a manifold directed edge set into deterministic closed loops."""

    outgoing: dict[Point, list[Point]] = {}
    for start, end in edges:
        outgoing.setdefault(start, []).append(end)

    for point, destinations in outgoing.items():
        if len(destinations) != 1:
            raise ValueError(
                f"region {region_id!r} has non-manifold boundary at {point}: "
                f"expected one outgoing edge, found {len(destinations)}"
            )

    remaining = set(edges)
    loops: list[RegionLoop] = []
    while remaining:
        start_edge = min(remaining)
        start = start_edge[0]
        points = [start]
        current = start

        while True:
            candidates = [edge for edge in remaining if edge[0] == current]
            if len(candidates) != 1:
                raise ValueError(
                    f"region {region_id!r} boundary cannot be chained at {current}"
                )
            edge = candidates[0]
            remaining.remove(edge)
            current = edge[1]
            points.append(current)
            if current == start:
                break
            if len(points) > len(edges) + 1:
                raise ValueError(f"region {region_id!r} boundary loop did not close")

        loop = RegionLoop(region_id=region_id, points=tuple(points))
        if not loop.closed:
            raise ValueError(f"region {region_id!r} produced an open boundary")
        loops.append(loop)

    return tuple(sorted(loops, key=lambda loop: loop.points))


def vectorize_partition(partition: RegionPartition) -> tuple[RegionLoop, ...]:
    """Trace every region into one or more closed integer-grid loops."""

    loops: list[RegionLoop] = []
    for region_id in partition.region_ids:
        loops.extend(
            _chain_directed_loops(
                region_id,
                _region_boundary_edges(partition, region_id),
            )
        )
    return tuple(loops)


def _boundary_key(first: str, second: str) -> tuple[str, str]:
    return tuple(sorted((first, second)))  # type: ignore[return-value]


def normalize_boundary_roles(
    roles: dict[tuple[str, str], BoundaryRole],
) -> tuple[tuple[str, str, BoundaryRole], ...]:
    """Canonicalize unordered boundary-pair roles for deterministic rendering."""

    normalized: dict[tuple[str, str], BoundaryRole] = {}
    for pair, role in roles.items():
        if len(pair) != 2:
            raise ValueError("boundary role keys must contain exactly two region ids")
        first, second = pair
        key = _boundary_key(first, second)
        if key in normalized and normalized[key] is not role:
            raise ValueError(f"conflicting roles for boundary {key}")
        normalized[key] = role
    return tuple((first, second, normalized[(first, second)]) for first, second in sorted(normalized))


def build_layered_region_document(
    partition: RegionPartition,
    *,
    palette: dict[str, str],
    boundary_roles: dict[tuple[str, str], BoundaryRole],
) -> LayeredRegionDocument:
    """Build an inspectable research document from one normalized partition."""

    missing_palette = sorted(set(partition.region_ids) - set(palette))
    if missing_palette:
        raise ValueError(f"palette is missing regions: {missing_palette}")

    return LayeredRegionDocument(
        partition=partition,
        loops=vectorize_partition(partition),
        palette=tuple(sorted(palette.items())),
        boundary_roles=normalize_boundary_roles(boundary_roles),
    )


def _path_data(points: Iterable[Point], scale: float) -> str:
    values = list(points)
    if not values:
        raise ValueError("path requires at least one point")
    commands = [f"M {values[0][0] * scale:g} {values[0][1] * scale:g}"]
    commands.extend(
        f"L {x * scale:g} {y * scale:g}" for x, y in values[1:]
    )
    return " ".join(commands) + " Z"


def _visible_boundary_segments(
    partition: RegionPartition,
    role_map: dict[tuple[str, str], BoundaryRole],
) -> tuple[tuple[Edge, BoundaryRole], ...]:
    """Return unique selected grid segments; FILL_ONLY boundaries are omitted."""

    segments: dict[tuple[Point, Point], BoundaryRole] = {}

    def add_segment(start: Point, end: Point, first: str, second: str) -> None:
        key = _boundary_key(first, second)
        role = role_map.get(key)
        if role is None or role is BoundaryRole.FILL_ONLY:
            return
        undirected = tuple(sorted((start, end)))  # type: ignore[assignment]
        previous = segments.get(undirected)
        if previous is not None and previous is not role:
            raise ValueError(f"conflicting visible roles on segment {undirected}")
        segments[undirected] = role

    for y in range(partition.height):
        for x in range(partition.width):
            current = _cell(partition, x, y)
            right = _cell(partition, x + 1, y)
            below = _cell(partition, x, y + 1)
            if current != right:
                add_segment((x + 1, y), (x + 1, y + 1), current, right)
            if current != below:
                add_segment((x, y + 1), (x + 1, y + 1), current, below)

            if x == 0:
                add_segment((x, y), (x, y + 1), current, OUTSIDE)
            if y == 0:
                add_segment((x, y), (x + 1, y), current, OUTSIDE)

    return tuple(sorted(((edge, role) for edge, role in segments.items()), key=lambda item: (item[1].value, item[0])))


def render_layered_svg(document: LayeredRegionDocument, *, scale: float = 20.0) -> str:
    """Render independent fill and selected line groups as deterministic SVG."""

    if scale <= 0:
        raise ValueError("scale must be greater than zero")

    palette = dict(document.palette)
    role_map = {
        _boundary_key(first, second): role
        for first, second, role in document.boundary_roles
    }
    loops_by_region: dict[str, list[RegionLoop]] = {
        region_id: [] for region_id in document.partition.region_ids
    }
    for loop in document.loops:
        loops_by_region[loop.region_id].append(loop)

    width = document.partition.width * scale
    height = document.partition.height * scale
    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}">',
        '  <g id="regions">',
    ]

    for region_id in document.partition.region_ids:
        subpaths = " ".join(
            _path_data(loop.points, scale)
            for loop in loops_by_region[region_id]
        )
        rows.append(
            f'    <path id="region.{escape(region_id)}" d="{subpaths}" '
            f'fill="{escape(palette[region_id])}" fill-rule="evenodd" stroke="none"/>'
        )

    rows.extend(['  </g>', '  <g id="lines" fill="none" stroke="black">'])
    for index, (edge, role) in enumerate(
        _visible_boundary_segments(document.partition, role_map)
    ):
        (x1, y1), (x2, y2) = edge
        rows.append(
            f'    <path id="line.{index:04d}" data-role="{role.value}" '
            f'd="M {x1 * scale:g} {y1 * scale:g} L {x2 * scale:g} {y2 * scale:g}"/>'
        )
    rows.extend(['  </g>', '</svg>', ''])
    return "\n".join(rows)


def extract_svg_group(svg: str, group_id: str) -> str:
    """Return one exact SVG group for byte-level layer-diff tests."""

    start_token = f'<g id="{group_id}"'
    start = svg.find(start_token)
    if start < 0:
        raise ValueError(f"SVG group {group_id!r} not found")
    end = svg.find("</g>", start)
    if end < 0:
        raise ValueError(f"SVG group {group_id!r} is not closed")
    return svg[start : end + len("</g>")]
