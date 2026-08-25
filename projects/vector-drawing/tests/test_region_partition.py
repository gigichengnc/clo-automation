"""Regression tests for the research raster-region layered SVG prototype."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vector_drawing.region_partition import (
    BoundaryRole,
    RegionPartition,
    build_layered_region_document,
    extract_svg_group,
    render_layered_svg,
    vectorize_partition,
)


class RegionPartitionPrototypeTests(unittest.TestCase):
    def _partition(self) -> RegionPartition:
        return RegionPartition(
            rows=(
                ("background", "background", "background", "background", "background", "background"),
                ("background", "body", "body", "body", "body", "background"),
                ("background", "body", "shadow", "shadow", "body", "background"),
                ("background", "body", "shadow", "shadow", "body", "background"),
                ("background", "body", "belt", "belt", "body", "background"),
                ("background", "background", "background", "background", "background", "background"),
            )
        )

    def _roles(self):
        return {
            ("background", "body"): BoundaryRole.REGION_BOUNDARY,
            ("body", "shadow"): BoundaryRole.FILL_ONLY,
            ("body", "belt"): BoundaryRole.INTERNAL_DETAIL,
            ("belt", "shadow"): BoundaryRole.FILL_ONLY,
        }

    def test_partition_vectorizes_to_closed_region_loops(self):
        loops = vectorize_partition(self._partition())

        self.assertGreaterEqual(len(loops), 4)
        self.assertEqual(
            {loop.region_id for loop in loops},
            {"background", "body", "shadow", "belt"},
        )
        self.assertTrue(all(loop.closed for loop in loops))
        self.assertTrue(all(loop.points[0] == loop.points[-1] for loop in loops))

    def test_palette_change_does_not_change_line_layer(self):
        partition = self._partition()
        first = build_layered_region_document(
            partition,
            palette={
                "background": "#ffffff",
                "body": "#d33a3a",
                "shadow": "#a32727",
                "belt": "#202020",
            },
            boundary_roles=self._roles(),
        )
        second = build_layered_region_document(
            partition,
            palette={
                "background": "#ffffff",
                "body": "#2d63d6",
                "shadow": "#20469b",
                "belt": "#f2d24c",
            },
            boundary_roles=self._roles(),
        )

        first_svg = render_layered_svg(first)
        second_svg = render_layered_svg(second)

        self.assertEqual(
            extract_svg_group(first_svg, "lines"),
            extract_svg_group(second_svg, "lines"),
        )
        self.assertNotEqual(
            extract_svg_group(first_svg, "regions"),
            extract_svg_group(second_svg, "regions"),
        )

    def test_fill_only_boundary_can_exist_without_becoming_a_line(self):
        partition = self._partition()
        fill_only = build_layered_region_document(
            partition,
            palette={
                "background": "#ffffff",
                "body": "#d33a3a",
                "shadow": "#a32727",
                "belt": "#202020",
            },
            boundary_roles=self._roles(),
        )

        visible_shadow_role = dict(self._roles())
        visible_shadow_role[("body", "shadow")] = BoundaryRole.INTERNAL_DETAIL
        visible = build_layered_region_document(
            partition,
            palette={
                "background": "#ffffff",
                "body": "#d33a3a",
                "shadow": "#a32727",
                "belt": "#202020",
            },
            boundary_roles=visible_shadow_role,
        )

        fill_only_lines = extract_svg_group(render_layered_svg(fill_only), "lines")
        visible_lines = extract_svg_group(render_layered_svg(visible), "lines")

        self.assertNotEqual(fill_only_lines, visible_lines)
        self.assertLess(
            fill_only_lines.count("<path"),
            visible_lines.count("<path"),
        )

    def test_diagonal_touching_region_safe_stops_as_non_manifold(self):
        partition = RegionPartition(
            rows=(
                ("a", "b"),
                ("b", "a"),
            )
        )

        with self.assertRaisesRegex(ValueError, "non-manifold"):
            vectorize_partition(partition)

    def test_raw_mask_style_missing_cells_are_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            RegionPartition(rows=(("body", ""),))


if __name__ == "__main__":
    unittest.main()
