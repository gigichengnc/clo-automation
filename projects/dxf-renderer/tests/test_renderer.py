from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ezdxf

from dxf_renderer.loader import load_dxf_scene
from dxf_renderer.svg import scene_to_svg


class RendererTests(unittest.TestCase):
    def make_fixture(self, path: Path) -> None:
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        msp.add_lwpolyline(
            [(0, 0), (100, 0), (100, 50), (0, 50)],
            close=True,
            dxfattribs={"layer": "OUTLINE"},
        )
        msp.add_line(
            (10, 10),
            (90, 10),
            dxfattribs={"layer": "DETAIL"},
        )
        doc.saveas(path)

    def test_loads_paths_and_preserves_layer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.dxf"
            self.make_fixture(path)
            scene = load_dxf_scene(path)
            self.assertEqual(len(scene.paths), 2)
            self.assertEqual({item.layer for item in scene.paths}, {"OUTLINE", "DETAIL"})
            self.assertEqual(sum(item.closed for item in scene.paths), 1)

    def test_layer_filter(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.dxf"
            self.make_fixture(path)
            scene = load_dxf_scene(path, layers={"OUTLINE"})
            self.assertEqual(len(scene.paths), 1)
            self.assertTrue(scene.paths[0].closed)

    def test_svg_is_deterministic_and_contains_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.dxf"
            self.make_fixture(path)
            scene = load_dxf_scene(path, layers={"OUTLINE"})
            first = scene_to_svg(scene)
            second = scene_to_svg(scene)
            self.assertEqual(first, second)
            self.assertIn('id="outline-pass"', first)
            self.assertIn('data-layer="OUTLINE"', first)
            self.assertIn('fill="none"', first)


if __name__ == "__main__":
    unittest.main()
