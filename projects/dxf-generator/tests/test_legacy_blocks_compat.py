"""Regression tests for the forensic legacy blocks compatibility layer."""

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from legacy_blocks_compat import parse, upright


def _poly(layer, points):
    rows = [f"0\nPOLYLINE\n8\n{layer}\n66\n1\n70\n1\n"]
    for x, y in points:
        rows.append(f"0\nVERTEX\n8\n{layer}\n10\n{x}\n20\n{y}\n")
    rows.append(f"0\nSEQEND\n8\n{layer}\n")
    return "".join(rows)


def _block(name, material, net, cut, grain):
    return (
        f"0\nBLOCK\n8\n1\n2\n{name}\n70\n0\n10\n0\n20\n0\n"
        + _poly("1", cut)
        + _poly("14", net)
        + f"0\nLINE\n8\n7\n10\n{grain[0][0]}\n20\n{grain[0][1]}\n"
          f"11\n{grain[1][0]}\n21\n{grain[1][1]}\n"
        + f"0\nTEXT\n8\n1\n10\n0\n20\n0\n1\nMaterial: {material}\n"
        + "0\nENDBLK\n"
    )


class LegacyBlocksCompatTests(unittest.TestCase):
    def _write(self, text):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "fixture.dxf"
        path.write_bytes(text.replace("\n", "\r\n").encode("gb18030"))
        self.addCleanup(directory.cleanup)
        return path

    def test_parse_preserves_first_duplicate_block_occurrence(self):
        text = (
            "999\nANSI/AAMA\n0\nSECTION\n2\nBLOCKS\n"
            + _block(
                "X.L",
                "shell",
                [(0, 0), (2, 0), (2, 1), (0, 1)],
                [(-1, -1), (3, -1), (3, 2), (-1, 2)],
                [(0, 0), (1, 0)],
            )
            + _block(
                "X.L",
                "lining",
                [(10, 0), (12, 0), (12, 1), (10, 1)],
                [(9, -1), (13, -1), (13, 2), (9, 2)],
                [(10, 0), (11, 0)],
            )
            + "0\nENDSEC\n0\nEOF\n"
        )
        parsed = parse(self._write(text))
        self.assertEqual(list(parsed), ["X.L"])
        self.assertIn("Material: shell", parsed["X.L"]["texts"])
        self.assertNotIn("Material: lining", parsed["X.L"]["texts"])

    def test_parse_exposes_layers_text_and_grainline(self):
        text = "0\nSECTION\n2\nBLOCKS\n" + _block(
            "X.L",
            "shell",
            [(0, 0), (2, 0), (2, 1), (0, 1)],
            [(-1, -1), (3, -1), (3, 2), (-1, 2)],
            [(0, 0), (1, 0)],
        ) + "0\nENDSEC\n0\nEOF\n"
        item = parse(self._write(text))["X.L"]
        self.assertEqual([p["layer"] for p in item["polys"]], ["1", "14"])
        self.assertEqual(item["grainlines"][0].shape, (2, 2))
        self.assertIn("Material: shell", item["texts"])

    def test_upright_centers_on_net_centroid_and_rotates_horizontal_grain_to_positive_y(self):
        text = "0\nSECTION\n2\nBLOCKS\n" + _block(
            "X.L",
            "shell",
            [(10, 20), (12, 20), (12, 22), (10, 22)],
            [(9, 19), (13, 19), (13, 23), (9, 23)],
            [(10, 20), (12, 20)],
        ) + "0\nENDSEC\n0\nEOF\n"
        net, cut, grain = upright(parse(self._write(text))["X.L"])
        np.testing.assert_allclose(net.mean(axis=0), [0, 0], atol=1e-12)
        direction = grain[1] - grain[0]
        self.assertAlmostEqual(direction[0], 0.0, places=12)
        self.assertGreater(direction[1], 0.0)
        np.testing.assert_allclose(cut.min(axis=0), [-2, -2], atol=1e-12)
        np.testing.assert_allclose(cut.max(axis=0), [2, 2], atol=1e-12)

    def test_upright_flips_downward_grainline_to_positive_y(self):
        text = "0\nSECTION\n2\nBLOCKS\n" + _block(
            "X.L",
            "shell",
            [(-1, -2), (1, -2), (1, 2), (-1, 2)],
            [(-2, -3), (2, -3), (2, 3), (-2, 3)],
            [(0, 1), (0, -1)],
        ) + "0\nENDSEC\n0\nEOF\n"
        net, _, grain = upright(parse(self._write(text))["X.L"])
        direction = grain[1] - grain[0]
        self.assertAlmostEqual(direction[0], 0.0, places=12)
        self.assertGreater(direction[1], 0.0)
        np.testing.assert_allclose(net.mean(axis=0), [0, 0], atol=1e-12)

    def test_upright_rejects_missing_net_contour(self):
        with self.assertRaisesRegex(ValueError, "missing layer 14"):
            upright(
                {
                    "polys": [
                        {"layer": "1", "pts": np.array([[0, 0], [1, 0]])}
                    ],
                    "grainlines": [np.array([[0, 0], [1, 0]])],
                }
            )

    def test_upright_rejects_missing_grainline(self):
        with self.assertRaisesRegex(ValueError, "missing layer-7 grainline"):
            upright(
                {
                    "polys": [
                        {"layer": "1", "pts": np.array([[0, 0], [1, 0]])},
                        {"layer": "14", "pts": np.array([[0, 0], [1, 0]])},
                    ],
                    "grainlines": [],
                }
            )

    def test_upright_rejects_zero_length_grainline(self):
        with self.assertRaisesRegex(ValueError, "non-zero length"):
            upright(
                {
                    "polys": [
                        {"layer": "1", "pts": np.array([[0, 0], [1, 0]])},
                        {"layer": "14", "pts": np.array([[0, 0], [1, 0]])},
                    ],
                    "grainlines": [np.array([[0, 0], [0, 0]])],
                }
            )


if __name__ == "__main__":
    unittest.main()
