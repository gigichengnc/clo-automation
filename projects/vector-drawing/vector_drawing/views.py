from __future__ import annotations

from dataclasses import replace

from .fashion_flat import DressSpec, build_dress_flat
from .model import Drawing, SemanticPath


_SUPPORTED_VIEWS = {"front", "back"}


def _rename_centre_guide(path: SemanticPath, *, view: str) -> SemanticPath:
    if view == "front" and path.role == "centre_front":
        return path
    if view == "back" and path.role == "centre_front":
        return replace(path, path_id="guide.centre_back", role="centre_back")
    return path


def build_dress_view(spec: DressSpec, *, view: str) -> Drawing:
    """Build one deterministic technical-flat view from the shared DressSpec.

    v0.1 intentionally has no back-specific neckline, closure, dart or seam
    semantics yet. Therefore front/back share the supported outer garment
    geometry and differ only in view identity / centre guide. This is an
    explicit limitation rather than an inferred back design.
    """
    if view not in _SUPPORTED_VIEWS:
        raise ValueError(f"unsupported view: {view}")

    base = build_dress_flat(spec)
    paths = tuple(_rename_centre_guide(path, view=view) for path in base.paths)
    return Drawing(
        drawing_id=f"{base.drawing_id}-{view}",
        width=base.width,
        height=base.height,
        paths=paths,
    )


def build_dress_front_flat(spec: DressSpec) -> Drawing:
    return build_dress_view(spec, view="front")


def build_dress_back_flat(spec: DressSpec) -> Drawing:
    return build_dress_view(spec, view="back")


def build_dress_views(spec: DressSpec) -> dict[str, Drawing]:
    return {
        "front": build_dress_front_flat(spec),
        "back": build_dress_back_flat(spec),
    }
