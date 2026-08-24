from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees, hypot

from .model import Cubic, Drawing, Line, Move, Point, SemanticPath, sample_path


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationReport:
    drawing_id: str
    issues: tuple[ValidationIssue, ...]

    @property
    def passed(self) -> bool:
        return not self.issues


def _distance(a: Point, b: Point) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def _same_point(a: Point, b: Point, tolerance: float) -> bool:
    return _distance(a, b) <= tolerance


def _endpoints(path: SemanticPath) -> tuple[Point, Point]:
    start = path.commands[0].to
    end = start
    for command in path.commands[1:]:
        end = command.to
    return start, end


def _normalised_signature(path: SemanticPath, *, digits: int = 6) -> tuple[tuple[float, float], ...]:
    points = sample_path(path, cubic_steps=16)
    forward = tuple((round(point.x, digits), round(point.y, digits)) for point in points)
    reverse = tuple(reversed(forward))
    return min(forward, reverse)


def _orientation(a: Point, b: Point, c: Point) -> float:
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def _on_segment(a: Point, b: Point, p: Point, tolerance: float) -> bool:
    return (
        min(a.x, b.x) - tolerance <= p.x <= max(a.x, b.x) + tolerance
        and min(a.y, b.y) - tolerance <= p.y <= max(a.y, b.y) + tolerance
        and abs(_orientation(a, b, p)) <= tolerance
    )


def _segments_intersect(a: Point, b: Point, c: Point, d: Point, tolerance: float) -> bool:
    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)

    if ((o1 > tolerance and o2 < -tolerance) or (o1 < -tolerance and o2 > tolerance)) and (
        (o3 > tolerance and o4 < -tolerance) or (o3 < -tolerance and o4 > tolerance)
    ):
        return True

    if abs(o1) <= tolerance and _on_segment(a, b, c, tolerance):
        return True
    if abs(o2) <= tolerance and _on_segment(a, b, d, tolerance):
        return True
    if abs(o3) <= tolerance and _on_segment(c, d, a, tolerance):
        return True
    if abs(o4) <= tolerance and _on_segment(c, d, b, tolerance):
        return True
    return False


def _has_self_intersection(path: SemanticPath, *, tolerance: float) -> bool:
    points = sample_path(path, cubic_steps=24)
    segments = list(zip(points, points[1:]))
    for i, (a, b) in enumerate(segments):
        for j in range(i + 2, len(segments)):
            # Adjacent segments share a legitimate endpoint. The first/last pair
            # is also ignored only when the path is intentionally closed.
            c, d = segments[j]
            if i == 0 and j == len(segments) - 1 and _same_point(points[0], points[-1], tolerance):
                continue
            if _segments_intersect(a, b, c, d, tolerance):
                return True
    return False


def _vector_angle_degrees(ax: float, ay: float, bx: float, by: float) -> float:
    la = hypot(ax, ay)
    lb = hypot(bx, by)
    if la == 0 or lb == 0:
        return 180.0
    cosine = max(-1.0, min(1.0, (ax * bx + ay * by) / (la * lb)))
    return degrees(acos(cosine))


def _neckline_has_kink(path: SemanticPath, *, max_angle_degrees: float) -> bool:
    if path.role != "neckline":
        return False

    current = path.commands[0].to
    previous_cubic: Cubic | None = None
    for command in path.commands[1:]:
        if isinstance(command, Cubic):
            if previous_cubic is not None:
                incoming_x = current.x - previous_cubic.control2.x
                incoming_y = current.y - previous_cubic.control2.y
                outgoing_x = command.control1.x - current.x
                outgoing_y = command.control1.y - current.y
                if _vector_angle_degrees(incoming_x, incoming_y, outgoing_x, outgoing_y) > max_angle_degrees:
                    return True
            previous_cubic = command
            current = command.to
        else:
            previous_cubic = None
            current = command.to
    return False


def _find_role(drawing: Drawing, role: str) -> SemanticPath | None:
    matches = drawing.paths_by_role(role)
    if len(matches) == 1:
        return matches[0]
    return None


def _expected_join_issues(drawing: Drawing, tolerance: float) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    # role A, endpoint on A, role B, endpoint on B
    rules = [
        ("neckline", "start", "shoulder.left", "start"),
        ("neckline", "end", "shoulder.right", "start"),
        ("shoulder.left", "end", "armhole.left", "start"),
        ("shoulder.right", "end", "armhole.right", "start"),
        ("shoulder.left", "end", "sleeve.left", "start"),
        ("shoulder.right", "end", "sleeve.right", "start"),
        ("armhole.left", "end", "side.left", "start"),
        ("armhole.right", "end", "side.right", "start"),
        ("sleeve.left", "end", "side.left", "start"),
        ("sleeve.right", "end", "side.right", "start"),
        ("side.left", "end", "hem", "start"),
        ("side.right", "end", "hem", "end"),
    ]

    for role_a, end_a, role_b, end_b in rules:
        a = _find_role(drawing, role_a)
        b = _find_role(drawing, role_b)
        if a is None or b is None:
            continue
        a_points = _endpoints(a)
        b_points = _endpoints(b)
        pa = a_points[0 if end_a == "start" else 1]
        pb = b_points[0 if end_b == "start" else 1]
        if not _same_point(pa, pb, tolerance):
            issues.append(
                ValidationIssue(
                    code="ENDPOINT_DISCONTINUITY",
                    message=f"{role_a}.{end_a} does not meet {role_b}.{end_b}",
                    path_ids=(a.path_id, b.path_id),
                )
            )
    return issues


def _symmetry_issues(drawing: Drawing, tolerance: float) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    roles = {path.role: path for path in drawing.paths}
    for role, left in sorted(roles.items()):
        if not role.endswith(".left"):
            continue
        right_role = role[:-5] + ".right"
        right = roles.get(right_role)
        if right is None:
            issues.append(
                ValidationIssue(
                    code="MISSING_MIRROR_PARTNER",
                    message=f"{role} has no {right_role} partner",
                    path_ids=(left.path_id,),
                )
            )
            continue
        left_points = sample_path(left, cubic_steps=24)
        right_points = sample_path(right, cubic_steps=24)
        if len(left_points) != len(right_points) or any(
            abs(lp.x + rp.x) > tolerance or abs(lp.y - rp.y) > tolerance
            for lp, rp in zip(left_points, right_points)
        ):
            issues.append(
                ValidationIssue(
                    code="SYMMETRY_MISMATCH",
                    message=f"{role} and {right_role} are not exact x-axis mirrors",
                    path_ids=(left.path_id, right.path_id),
                )
            )
    return issues


def validate_drawing(
    drawing: Drawing,
    *,
    tolerance: float = 1e-6,
    min_segment_length: float = 1e-5,
    neckline_tangent_tolerance_degrees: float = 5.0,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    signatures: dict[tuple[tuple[float, float], ...], str] = {}
    for path in drawing.paths:
        current = path.commands[0].to
        for command in path.commands[1:]:
            if isinstance(command, Line):
                if _distance(current, command.to) < min_segment_length:
                    issues.append(
                        ValidationIssue(
                            code="ZERO_LENGTH_SEGMENT",
                            message="line segment is zero-length or below minimum length",
                            path_ids=(path.path_id,),
                        )
                    )
                current = command.to
            elif isinstance(command, Cubic):
                if (
                    _distance(current, command.control1) < min_segment_length
                    and _distance(current, command.control2) < min_segment_length
                    and _distance(current, command.to) < min_segment_length
                ):
                    issues.append(
                        ValidationIssue(
                            code="ZERO_LENGTH_SEGMENT",
                            message="cubic segment collapses to a point",
                            path_ids=(path.path_id,),
                        )
                    )
                current = command.to

        signature = _normalised_signature(path)
        duplicate_of = signatures.get(signature)
        if duplicate_of is not None:
            issues.append(
                ValidationIssue(
                    code="DUPLICATE_GEOMETRY",
                    message="path duplicates existing geometry",
                    path_ids=(duplicate_of, path.path_id),
                )
            )
        else:
            signatures[signature] = path.path_id

        if _has_self_intersection(path, tolerance=tolerance):
            issues.append(
                ValidationIssue(
                    code="SELF_INTERSECTION",
                    message="path intersects itself",
                    path_ids=(path.path_id,),
                )
            )

        if _neckline_has_kink(path, max_angle_degrees=neckline_tangent_tolerance_degrees):
            issues.append(
                ValidationIssue(
                    code="CURVE_TANGENT_DISCONTINUITY",
                    message="smooth neckline cubic join exceeds tangent tolerance",
                    path_ids=(path.path_id,),
                )
            )

    issues.extend(_symmetry_issues(drawing, tolerance))
    issues.extend(_expected_join_issues(drawing, tolerance))

    return ValidationReport(drawing_id=drawing.drawing_id, issues=tuple(issues))
