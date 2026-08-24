from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import ezdxf
from ezdxf.entities import DXFEntity
from ezdxf.path import make_path

from .model import Point2D, VectorPath, VectorScene


def _iter_render_entities(
    entity: DXFEntity,
    root_source: str | None = None,
) -> Iterator[tuple[DXFEntity, str | None]]:
    if entity.dxftype() != "INSERT":
        yield entity, root_source
        return

    source = root_source or str(entity.dxf.name)
    for child in entity.virtual_entities():
        if child.dxftype() == "INSERT":
            yield from _iter_render_entities(child, source)
        else:
            yield child, source


def _entity_to_path(
    entity: DXFEntity,
    *,
    tolerance: float,
    source: str | None,
) -> VectorPath | None:
    try:
        path = make_path(entity)
    except (TypeError, ValueError, AttributeError):
        return None

    try:
        vertices = list(path.flattening(distance=tolerance))
    except (TypeError, ValueError, ZeroDivisionError):
        return None

    if len(vertices) < 2:
        return None

    points = tuple(Point2D(float(vertex.x), float(vertex.y)) for vertex in vertices)
    layer = str(getattr(entity.dxf, "layer", "0"))
    return VectorPath(
        points=points,
        closed=bool(path.is_closed),
        layer=layer,
        source=source,
        entity_type=entity.dxftype(),
    )


def load_dxf_scene(
    filename: str | Path,
    *,
    layers: set[str] | None = None,
    tolerance: float = 0.25,
) -> VectorScene:
    """Load renderable 2D vector geometry from a DXF.

    INSERT entities are expanded using ezdxf's transformation logic. Text and
    point-only construction data are intentionally ignored in v0.1. Curves are
    deterministically flattened to line segments at ``tolerance`` drawing units.
    """
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    doc = ezdxf.readfile(str(filename))
    paths: list[VectorPath] = []

    for entity in doc.modelspace():
        for render_entity, source in _iter_render_entities(entity):
            layer = str(getattr(render_entity.dxf, "layer", "0"))
            if layers is not None and layer not in layers:
                continue
            vector_path = _entity_to_path(
                render_entity,
                tolerance=tolerance,
                source=source,
            )
            if vector_path is not None:
                paths.append(vector_path)

    return VectorScene.from_paths(paths, units="mm")
