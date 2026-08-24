import unittest

from vector_drawing.fashion_flat import DressSpec, build_dress_flat
from vector_drawing.model import Cubic, Drawing, Line, Move, Point, SemanticPath
from vector_drawing.validation import validate_drawing


class VectorValidationTests(unittest.TestCase):
    def test_supported_dress_variants_are_geometry_valid(self):
        variants = [
            DressSpec(neckline="round", sleeve="sleeveless", silhouette="a_line", length="midi"),
            DressSpec(neckline="round", sleeve="short", silhouette="straight", length="knee"),
            DressSpec(neckline="v", sleeve="sleeveless", silhouette="straight", length="mini"),
            DressSpec(neckline="v", sleeve="short", silhouette="a_line", length="maxi"),
        ]
        for spec in variants:
            with self.subTest(spec=spec):
                report = validate_drawing(build_dress_flat(spec))
                self.assertTrue(report.passed, report.issues)

    def test_zero_length_segment_is_rejected(self):
        path = SemanticPath(
            path_id="bad.zero",
            role="detail",
            commands=(Move(Point(0.0, 0.0)), Line(Point(0.0, 0.0))),
        )
        drawing = Drawing("bad-zero", 100.0, 100.0, (path,))
        codes = {issue.code for issue in validate_drawing(drawing).issues}
        self.assertIn("ZERO_LENGTH_SEGMENT", codes)

    def test_duplicate_geometry_is_rejected_even_with_different_ids(self):
        a = SemanticPath(
            path_id="a",
            role="detail.a",
            commands=(Move(Point(0.0, 0.0)), Line(Point(20.0, 0.0))),
        )
        b = SemanticPath(
            path_id="b",
            role="detail.b",
            commands=(Move(Point(20.0, 0.0)), Line(Point(0.0, 0.0))),
        )
        drawing = Drawing("bad-duplicate", 100.0, 100.0, (a, b))
        codes = {issue.code for issue in validate_drawing(drawing).issues}
        self.assertIn("DUPLICATE_GEOMETRY", codes)

    def test_self_intersection_is_rejected(self):
        crossing = SemanticPath(
            path_id="bad.crossing",
            role="detail",
            commands=(
                Move(Point(0.0, 0.0)),
                Line(Point(20.0, 20.0)),
                Line(Point(0.0, 20.0)),
                Line(Point(20.0, 0.0)),
            ),
        )
        drawing = Drawing("bad-crossing", 100.0, 100.0, (crossing,))
        codes = {issue.code for issue in validate_drawing(drawing).issues}
        self.assertIn("SELF_INTERSECTION", codes)

    def test_symmetry_mismatch_is_rejected(self):
        left = SemanticPath(
            path_id="left",
            role="side.left",
            commands=(Move(Point(-20.0, 0.0)), Line(Point(-30.0, 50.0))),
        )
        right = SemanticPath(
            path_id="right",
            role="side.right",
            commands=(Move(Point(20.0, 0.0)), Line(Point(31.0, 50.0))),
        )
        drawing = Drawing("bad-symmetry", 100.0, 100.0, (left, right))
        codes = {issue.code for issue in validate_drawing(drawing).issues}
        self.assertIn("SYMMETRY_MISMATCH", codes)

    def test_round_neckline_kink_is_rejected(self):
        neckline = SemanticPath(
            path_id="bad.neckline",
            role="neckline",
            commands=(
                Move(Point(-20.0, 0.0)),
                Cubic(Point(-15.0, 10.0), Point(-5.0, 10.0), Point(0.0, 10.0)),
                Cubic(Point(0.0, 20.0), Point(15.0, 10.0), Point(20.0, 0.0)),
            ),
        )
        drawing = Drawing("bad-neckline", 100.0, 100.0, (neckline,))
        codes = {issue.code for issue in validate_drawing(drawing).issues}
        self.assertIn("CURVE_TANGENT_DISCONTINUITY", codes)


if __name__ == "__main__":
    unittest.main()
