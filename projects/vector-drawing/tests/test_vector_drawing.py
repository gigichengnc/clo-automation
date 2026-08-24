import unittest

from vector_drawing.dxf import render_dxf
from vector_drawing.fashion_flat import DressSpec, build_dress_flat
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


if __name__ == "__main__":
    unittest.main()
