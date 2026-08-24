import unittest

from vector_drawing.fashion_flat import DressSpec
from vector_drawing.validation import validate_drawing
from vector_drawing.views import build_dress_back_flat, build_dress_front_flat, build_dress_view, build_dress_views


class FlatViewTests(unittest.TestCase):
    def test_front_does_not_require_back_semantics(self):
        front = build_dress_front_flat(DressSpec(neckline="round", sleeve="short", silhouette="a_line", length="midi"))
        self.assertTrue(front.drawing_id.endswith("-front"))
        self.assertEqual(len(front.paths_by_role("centre_front")), 1)
        self.assertEqual(len(front.paths_by_role("centre_back")), 0)

    def test_back_missing_semantics_safe_stops(self):
        with self.assertRaises(ValueError):
            build_dress_back_flat(DressSpec())

    def test_same_as_front_back_without_closure_is_explicit(self):
        spec = DressSpec(
            neckline="v",
            sleeve="short",
            silhouette="straight",
            length="knee",
            back_neckline="same_as_front",
            back_closure="none",
        )
        front = build_dress_front_flat(spec)
        back = build_dress_back_flat(spec)
        self.assertEqual(front.paths_by_role("neckline")[0].commands, back.paths_by_role("neckline")[0].commands)
        self.assertEqual(len(back.paths_by_role("back_closure.centre_zip")), 0)
        self.assertEqual(len(back.paths_by_role("centre_back")), 1)

    def test_shallow_round_back_with_centre_zip_is_distinct(self):
        spec = DressSpec(
            neckline="round",
            sleeve="short",
            silhouette="a_line",
            length="midi",
            back_neckline="shallow_round",
            back_closure="centre_zip",
        )
        front = build_dress_front_flat(spec)
        back = build_dress_back_flat(spec)
        self.assertNotEqual(front.paths_by_role("neckline")[0].commands, back.paths_by_role("neckline")[0].commands)
        self.assertEqual(len(back.paths_by_role("back_closure.centre_zip")), 1)
        self.assertTrue(validate_drawing(back).passed)

    def test_shared_spec_builds_two_valid_views_when_back_is_explicit(self):
        spec = DressSpec(
            neckline="round",
            sleeve="sleeveless",
            silhouette="a_line",
            length="maxi",
            back_neckline="shallow_round",
            back_closure="none",
        )
        views = build_dress_views(spec)
        self.assertEqual(set(views), {"front", "back"})
        self.assertTrue(validate_drawing(views["front"]).passed)
        self.assertTrue(validate_drawing(views["back"]).passed)

    def test_invalid_view_safe_stops(self):
        with self.assertRaises(ValueError):
            build_dress_view(DressSpec(), view="side")


if __name__ == "__main__":
    unittest.main()
