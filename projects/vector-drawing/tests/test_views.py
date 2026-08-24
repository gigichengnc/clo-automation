import unittest

from vector_drawing.fashion_flat import DressSpec
from vector_drawing.validation import validate_drawing
from vector_drawing.views import build_dress_back_flat, build_dress_front_flat, build_dress_view, build_dress_views


class FlatViewTests(unittest.TestCase):
    def test_same_spec_builds_front_and_back(self):
        views = build_dress_views(DressSpec(neckline="round", sleeve="short", silhouette="a_line", length="midi"))
        self.assertEqual(set(views), {"front", "back"})
        self.assertTrue(views["front"].drawing_id.endswith("-front"))
        self.assertTrue(views["back"].drawing_id.endswith("-back"))

    def test_front_and_back_use_distinct_centre_guides(self):
        spec = DressSpec()
        front = build_dress_front_flat(spec)
        back = build_dress_back_flat(spec)
        self.assertEqual(len(front.paths_by_role("centre_front")), 1)
        self.assertEqual(len(front.paths_by_role("centre_back")), 0)
        self.assertEqual(len(back.paths_by_role("centre_front")), 0)
        self.assertEqual(len(back.paths_by_role("centre_back")), 1)

    def test_v01_back_does_not_invent_different_outline(self):
        spec = DressSpec(neckline="v", sleeve="short", silhouette="straight", length="knee")
        front = build_dress_front_flat(spec)
        back = build_dress_back_flat(spec)
        front_outline = [(p.role, p.commands) for p in front.paths if p.layer == "outline"]
        back_outline = [(p.role, p.commands) for p in back.paths if p.layer == "outline"]
        self.assertEqual(front_outline, back_outline)

    def test_both_views_pass_geometry_validation(self):
        spec = DressSpec(neckline="round", sleeve="sleeveless", silhouette="a_line", length="maxi")
        self.assertTrue(validate_drawing(build_dress_front_flat(spec)).passed)
        self.assertTrue(validate_drawing(build_dress_back_flat(spec)).passed)

    def test_invalid_view_safe_stops(self):
        with self.assertRaises(ValueError):
            build_dress_view(DressSpec(), view="side")


if __name__ == "__main__":
    unittest.main()
