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

    def test_front_waist_dart_pair_is_semantic_and_valid(self):
        spec = DressSpec(front_darts="waist_pair")
        front = build_dress_front_flat(spec)
        self.assertEqual(len(front.paths_by_role("dart.front.left")), 1)
        self.assertEqual(len(front.paths_by_role("dart.front.right")), 1)
        self.assertEqual(len(front.paths_by_role("dart.back.left")), 0)
        self.assertTrue(validate_drawing(front).passed)

    def test_back_replaces_front_darts_with_back_darts(self):
        spec = DressSpec(
            neckline="round",
            sleeve="short",
            silhouette="a_line",
            length="midi",
            back_neckline="shallow_round",
            back_closure="centre_zip",
            front_darts="waist_pair",
            back_darts="waist_pair",
        )
        front = build_dress_front_flat(spec)
        back = build_dress_back_flat(spec)

        self.assertEqual(len(front.paths_by_role("dart.front.left")), 1)
        self.assertEqual(len(front.paths_by_role("dart.back.left")), 0)
        self.assertEqual(len(back.paths_by_role("dart.front.left")), 0)
        self.assertEqual(len(back.paths_by_role("dart.back.left")), 1)
        self.assertEqual(len(back.paths_by_role("dart.back.right")), 1)
        self.assertTrue(validate_drawing(front).passed)
        self.assertTrue(validate_drawing(back).passed)

    def test_explicit_none_and_unspecified_both_draw_no_dart_but_remain_distinct_in_spec(self):
        unspecified = DressSpec(front_darts=None)
        confirmed_none = DressSpec(front_darts="none")
        self.assertIsNone(unspecified.front_darts)
        self.assertEqual(confirmed_none.front_darts, "none")
        self.assertEqual(len(build_dress_front_flat(unspecified).paths_by_role("dart.front.left")), 0)
        self.assertEqual(len(build_dress_front_flat(confirmed_none).paths_by_role("dart.front.left")), 0)

    def test_invalid_view_safe_stops(self):
        with self.assertRaises(ValueError):
            build_dress_view(DressSpec(), view="side")


if __name__ == "__main__":
    unittest.main()
