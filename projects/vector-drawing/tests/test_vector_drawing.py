import unittest

from vector_drawing.dxf import render_dxf
from vector_drawing.fashion_flat import DressSpec, build_dress_flat
from vector_drawing.prompt import PromptParseError, parse_prompt
from vector_drawing.svg import render_svg


class VectorDrawingTests(unittest.TestCase):
    def test_dress_is_semantically_symmetric(self):
        drawing = build_dress_flat(DressSpec())
        left = drawing.paths_by_role("side.left")[0]
        right = drawing.paths_by_role("side.right")[0]
        mirrored = left.mirror_x(path_id="test", role="side.right")
        self.assertEqual(mirrored.commands, right.commands)

    def test_svg_has_stable_semantic_ids(self):
        drawing = build_dress_flat(DressSpec(neckline="v", sleeve="short"))
        svg = render_svg(drawing)
        self.assertIn('id="outline.neckline"', svg)
        self.assertIn('data-role="sleeve.left"', svg)
        self.assertIn('viewBox=', svg)

    def test_dxf_is_r12_and_contains_art_layers(self):
        dxf = render_dxf(build_dress_flat(DressSpec()))
        self.assertIn("AC1009", dxf)
        self.assertIn("ART_OUTLINE", dxf)
        self.assertTrue(dxf.rstrip().endswith("EOF"))

    def test_invalid_spec_safe_stops(self):
        with self.assertRaises(ValueError):
            DressSpec(neckline="invented")
        with self.assertRaises(ValueError):
            DressSpec(back_neckline="invented")
        with self.assertRaises(ValueError):
            DressSpec(back_closure="invented")

    def test_prompt_maps_to_controlled_spec(self):
        result = parse_prompt("round-neck short-sleeve midi A-line dress")
        self.assertEqual(result.garment, "dress")
        self.assertEqual(result.spec, DressSpec(neckline="round", sleeve="short", silhouette="a_line", length="midi"))

    def test_chinese_prompt_maps_to_controlled_spec(self):
        result = parse_prompt("圓領 短袖 中長 A字 連衣裙")
        self.assertEqual(result.spec, DressSpec(neckline="round", sleeve="short", silhouette="a_line", length="midi"))

    def test_back_prompt_maps_to_explicit_semantics(self):
        result = parse_prompt(
            "round-neck short-sleeve midi A-line dress shallow round back neckline centre-back zipper",
            require_back=True,
        )
        self.assertEqual(result.spec.back_neckline, "shallow_round")
        self.assertEqual(result.spec.back_closure, "centre_zip")

    def test_chinese_back_prompt_maps_to_explicit_semantics(self):
        result = parse_prompt("圓領 短袖 中長 A字 連衣裙 淺圓後領 後中拉鏈", require_back=True)
        self.assertEqual(result.spec.back_neckline, "shallow_round")
        self.assertEqual(result.spec.back_closure, "centre_zip")

    def test_back_prompt_requires_explicit_back_categories(self):
        with self.assertRaises(PromptParseError):
            parse_prompt("round-neck short-sleeve midi A-line dress", require_back=True)

    def test_prompt_requires_explicit_categories(self):
        with self.assertRaises(PromptParseError):
            parse_prompt("a nice midi dress")

    def test_prompt_rejects_conflicting_semantics(self):
        with self.assertRaises(PromptParseError):
            parse_prompt("round-neck V-neck short-sleeve midi A-line dress")

    def test_prompt_rejects_unsupported_feature(self):
        with self.assertRaises(PromptParseError):
            parse_prompt("round-neck long-sleeve midi A-line dress")


if __name__ == "__main__":
    unittest.main()
