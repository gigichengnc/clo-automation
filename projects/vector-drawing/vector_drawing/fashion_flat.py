from __future__ import annotations

from dataclasses import dataclass

from .flat_details import (
    build_centre_button_row,
    build_patch_pocket_pair,
    build_shoulder_princess_seam_pair,
    build_waist_dart_pair,
)
from .model import Cubic, Drawing, Line, Move, Point, SemanticPath


_LENGTH_Y = {
    "mini": 210.0,
    "knee": 245.0,
    "midi": 285.0,
    "maxi": 325.0,
}


@dataclass(frozen=True)
class DressSpec:
    neckline: str = "round"       # round | v
    sleeve: str = "sleeveless"    # sleeveless | short
    silhouette: str = "a_line"    # a_line | straight
    length: str = "midi"          # mini | knee | midi | maxi
    back_neckline: str | None = None   # same_as_front | shallow_round
    back_closure: str | None = None    # none | centre_zip
    front_darts: str | None = None     # none | waist_pair; None = unspecified
    back_darts: str | None = None      # none | waist_pair; None = unspecified
    front_pockets: str | None = None   # none | patch_pair; None = unspecified
    front_buttons: str | None = None   # none | centre_row; None = unspecified
    front_princess_seams: str | None = None  # none | shoulder_pair; None = unspecified

    def __post_init__(self) -> None:
        allowed = {
            "neckline": ({"round", "v"}, self.neckline),
            "sleeve": ({"sleeveless", "short"}, self.sleeve),
            "silhouette": ({"a_line", "straight"}, self.silhouette),
            "length": (set(_LENGTH_Y), self.length),
        }
        optional_allowed = {
            "back_neckline": ({"same_as_front", "shallow_round"}, self.back_neckline),
            "back_closure": ({"none", "centre_zip"}, self.back_closure),
            "front_darts": ({"none", "waist_pair"}, self.front_darts),
            "back_darts": ({"none", "waist_pair"}, self.back_darts),
            "front_pockets": ({"none", "patch_pair"}, self.front_pockets),
            "front_buttons": ({"none", "centre_row"}, self.front_buttons),
            "front_princess_seams": ({"none", "shoulder_pair"}, self.front_princess_seams),
        }
        for name, (options, value) in allowed.items():
            if value not in options:
                raise ValueError(f"unsupported {name}: {value}")
        for name, (options, value) in optional_allowed.items():
            if value is not None and value not in options:
                raise ValueError(f"unsupported {name}: {value}")


def _path(path_id: str, role: str, *commands, layer: str = "outline") -> SemanticPath:
    return SemanticPath(path_id=path_id, role=role, commands=tuple(commands), layer=layer)


def build_dress_flat(spec: DressSpec) -> Drawing:
    hem_y = _LENGTH_Y[spec.length]
    waist_y = 125.0
    shoulder_y = 45.0
    underarm_y = 92.0

    neck = Point(-25.0, 42.0)
    shoulder = Point(-63.0, shoulder_y)
    underarm = Point(-55.0, underarm_y)
    waist = Point(-42.0, waist_y)
    hem_x = -84.0 if spec.silhouette == "a_line" else -49.0
    hem = Point(hem_x, hem_y)

    paths: list[SemanticPath] = []

    left_shoulder = _path(
        "outline.shoulder.left",
        "shoulder.left",
        Move(neck),
        Cubic(Point(-37.0, 42.0), Point(-51.0, 44.0), shoulder),
    )
    paths.append(left_shoulder)
    paths.append(left_shoulder.mirror_x(path_id="outline.shoulder.right", role="shoulder.right"))

    if spec.sleeve == "sleeveless":
        left_arm = _path(
            "outline.armhole.left",
            "armhole.left",
            Move(shoulder),
            Cubic(Point(-66.0, 58.0), Point(-66.0, 79.0), underarm),
        )
        paths.append(left_arm)
        paths.append(left_arm.mirror_x(path_id="outline.armhole.right", role="armhole.right"))
    else:
        sleeve_outer = Point(-88.0, 76.0)
        sleeve_inner = Point(-72.0, 98.0)
        left_sleeve = _path(
            "outline.sleeve.left",
            "sleeve.left",
            Move(shoulder),
            Cubic(Point(-72.0, 51.0), Point(-84.0, 61.0), sleeve_outer),
            Line(sleeve_inner),
            Cubic(Point(-66.0, 95.0), Point(-61.0, 93.0), underarm),
        )
        paths.append(left_sleeve)
        paths.append(left_sleeve.mirror_x(path_id="outline.sleeve.right", role="sleeve.right"))
        sleeve_hem = _path(
            "detail.sleeve_hem.left",
            "sleeve_hem.left",
            Move(sleeve_outer),
            Cubic(Point(-83.0, 82.0), Point(-78.0, 91.0), sleeve_inner),
            layer="detail",
        )
        paths.append(sleeve_hem)
        paths.append(sleeve_hem.mirror_x(path_id="detail.sleeve_hem.right", role="sleeve_hem.right"))

    left_side = _path(
        "outline.side.left",
        "side.left",
        Move(underarm),
        Cubic(Point(-52.0, 105.0), Point(-47.0, 116.0), waist),
        Cubic(Point(hem_x * 0.66, 172.0), Point(hem_x * 0.90, hem_y - 38.0), hem),
    )
    paths.append(left_side)
    paths.append(left_side.mirror_x(path_id="outline.side.right", role="side.right"))

    hem_path = _path(
        "outline.hem",
        "hem",
        Move(hem),
        Cubic(Point(hem.x * 0.55, hem_y + 4.0), Point(-hem.x * 0.55, hem_y + 4.0), hem.mirror_x()),
    )
    paths.append(hem_path)

    if spec.neckline == "round":
        neckline = _path(
            "outline.neckline",
            "neckline",
            Move(neck),
            Cubic(Point(-18.0, 63.0), Point(-8.0, 70.0), Point(0.0, 70.0)),
            Cubic(Point(8.0, 70.0), Point(18.0, 63.0), neck.mirror_x()),
        )
    else:
        neckline = _path(
            "outline.neckline",
            "neckline",
            Move(neck),
            Line(Point(0.0, 82.0)),
            Line(neck.mirror_x()),
        )
    paths.append(neckline)

    centre = _path(
        "guide.centre_front",
        "centre_front",
        Move(Point(0.0, 84.0)),
        Line(Point(0.0, hem_y - 8.0)),
        layer="guide",
    )
    waist_guide = _path(
        "guide.waist",
        "waist",
        Move(waist),
        Cubic(Point(-22.0, waist_y + 2.0), Point(22.0, waist_y + 2.0), waist.mirror_x()),
        layer="guide",
    )
    paths.extend([centre, waist_guide])

    if spec.front_darts == "waist_pair":
        paths.extend(build_waist_dart_pair(view="front", waist_y=waist_y))
    if spec.front_pockets == "patch_pair":
        paths.extend(build_patch_pocket_pair())
    if spec.front_buttons == "centre_row":
        paths.extend(build_centre_button_row())
    if spec.front_princess_seams == "shoulder_pair":
        paths.extend(build_shoulder_princess_seam_pair())

    return Drawing(
        drawing_id=f"dress-{spec.neckline}-{spec.sleeve}-{spec.silhouette}-{spec.length}",
        width=220.0,
        height=hem_y + 25.0,
        paths=tuple(paths),
    )
