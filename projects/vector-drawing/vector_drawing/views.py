from __future__ import annotations

from .fashion_flat import DressSpec, build_dress_flat
from .model import Cubic, Drawing, Line, Move, Point, SemanticPath


_SUPPORTED_VIEWS = {"front", "back"}


def _replace_back_neckline(path: SemanticPath, *, spec: DressSpec) -> SemanticPath:
    if path.role != "neckline":
        return path
    if spec.back_neckline == "same_as_front":
        return path
    if spec.back_neckline == "shallow_round":
        start = path.commands[0].to
        end = path.commands[-1].to
        return SemanticPath(
            path_id=path.path_id,
            role=path.role,
            commands=(
                Move(start),
                Cubic(Point(-18.0, 50.0), Point(-8.0, 56.0), Point(0.0, 56.0)),
                Cubic(Point(8.0, 56.0), Point(18.0, 50.0), end),
            ),
            layer=path.layer,
        )
    raise ValueError("back view requires explicit back_neckline")


def _neckline_centre(path: SemanticPath) -> Point:
    centre_candidates = [command.to for command in path.commands if abs(command.to.x) <= 1e-9]
    if len(centre_candidates) != 1:
        raise ValueError("back neckline must expose exactly one centre point")
    return centre_candidates[0]


def _back_centre_guide(path: SemanticPath, *, has_zip: bool) -> SemanticPath:
    if path.role != "centre_front":
        return path
    end = path.commands[-1].to
    start_y = 132.0 if has_zip else path.commands[0].to.y
    return SemanticPath(
        path_id="guide.centre_back",
        role="centre_back",
        commands=(Move(Point(0.0, start_y)), Line(Point(0.0, end.y))),
        layer=path.layer,
    )


def build_dress_view(spec: DressSpec, *, view: str) -> Drawing:
    """Build one deterministic technical-flat view from the shared DressSpec.

    Front geometry uses the existing front semantics. A back view requires
    explicit back-neckline and back-closure values. Missing back semantics
    safe-stop instead of being inferred.
    """
    if view not in _SUPPORTED_VIEWS:
        raise ValueError(f"unsupported view: {view}")

    base = build_dress_flat(spec)
    if view == "front":
        return Drawing(
            drawing_id=f"{base.drawing_id}-front",
            width=base.width,
            height=base.height,
            paths=base.paths,
        )

    if spec.back_neckline is None or spec.back_closure is None:
        raise ValueError("back view requires explicit back_neckline and back_closure")

    has_zip = spec.back_closure == "centre_zip"
    paths: list[SemanticPath] = []
    back_neckline: SemanticPath | None = None

    for path in base.paths:
        if path.role == "neckline":
            back_neckline = _replace_back_neckline(path, spec=spec)
            paths.append(back_neckline)
        elif path.role == "centre_front":
            paths.append(_back_centre_guide(path, has_zip=has_zip))
        else:
            paths.append(path)

    if back_neckline is None:
        raise ValueError("back view has no neckline geometry")

    if has_zip:
        centre = _neckline_centre(back_neckline)
        paths.append(
            SemanticPath(
                path_id="detail.back_closure.centre_zip",
                role="back_closure.centre_zip",
                commands=(Move(centre), Line(Point(0.0, 125.0))),
                layer="detail",
            )
        )
    elif spec.back_closure != "none":
        raise ValueError(f"unsupported back_closure: {spec.back_closure}")

    return Drawing(
        drawing_id=f"{base.drawing_id}-back",
        width=base.width,
        height=base.height,
        paths=tuple(paths),
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
