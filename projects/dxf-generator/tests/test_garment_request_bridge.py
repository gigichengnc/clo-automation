from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "projects" / "dxf-generator"))
sys.path.insert(0, str(REPO_ROOT / "projects" / "vector-drawing"))

from garment_request_bridge import BridgeStatus, build_production_pattern_request  # noqa: E402
from vector_drawing.fashion_flat import DressSpec  # noqa: E402


class GarmentRequestBridgeTests(unittest.TestCase):
    def test_basic_illustration_spec_is_not_promoted_to_production_ready(self):
        request = build_production_pattern_request(DressSpec())
        self.assertFalse(request.ready_for_drafting)
        self.assertEqual(request.assessment("garment_type").status, BridgeStatus.SUPPORTED)
        self.assertEqual(request.assessment("length").status, BridgeStatus.NEEDS_RULE)
        self.assertEqual(request.assessment("front_neckline").status, BridgeStatus.NEEDS_RULE)
        self.assertEqual(request.assessment("body_measurements").status, BridgeStatus.NEEDS_RULE)

    def test_unspecified_optional_semantic_is_a_blocker_not_confirmed_none(self):
        request = build_production_pattern_request(DressSpec())
        assessment = request.assessment("front_darts")
        self.assertIsNone(assessment.value)
        self.assertEqual(assessment.status, BridgeStatus.NEEDS_RULE)
        self.assertIn("explicit_front_darts", assessment.required_inputs)

    def test_explicit_none_can_pass_through_without_illustration_geometry(self):
        request = build_production_pattern_request(
            DressSpec(
                front_darts="none",
                back_darts="none",
                front_pockets="none",
                front_buttons="none",
                front_princess_seams="none",
                back_neckline="same_as_front",
                back_closure="none",
            )
        )
        for feature in (
            "front_darts",
            "back_darts",
            "front_pockets",
            "front_buttons",
            "front_princess_seams",
            "back_closure",
        ):
            self.assertEqual(request.assessment(feature).status, BridgeStatus.SUPPORTED)

    def test_illustration_dart_semantic_requires_real_production_dart_rules(self):
        request = build_production_pattern_request(DressSpec(front_darts="waist_pair"))
        assessment = request.assessment("front_darts")
        self.assertEqual(assessment.status, BridgeStatus.NEEDS_RULE)
        self.assertIn("suppression_policy", assessment.required_inputs)
        self.assertIn("front_dart_intake", assessment.required_inputs)
        self.assertIn("front_dart_length", assessment.required_inputs)
        self.assertIn("front_dart_placement", assessment.required_inputs)

    def test_patch_pocket_button_and_princess_semantics_need_independent_rules(self):
        request = build_production_pattern_request(
            DressSpec(
                front_pockets="patch_pair",
                front_buttons="centre_row",
                front_princess_seams="shoulder_pair",
            )
        )
        self.assertEqual(request.assessment("front_pockets").status, BridgeStatus.NEEDS_RULE)
        self.assertIn("pocket_dimensions", request.assessment("front_pockets").required_inputs)
        self.assertEqual(request.assessment("front_buttons").status, BridgeStatus.NEEDS_RULE)
        self.assertIn("button_spacing", request.assessment("front_buttons").required_inputs)
        self.assertEqual(request.assessment("front_princess_seams").status, BridgeStatus.NEEDS_RULE)
        self.assertIn("princess_shaping_policy", request.assessment("front_princess_seams").required_inputs)

    def test_short_sleeve_never_reuses_illustration_curve_as_pattern_geometry(self):
        request = build_production_pattern_request(DressSpec(sleeve="short"))
        assessment = request.assessment("sleeve")
        self.assertEqual(assessment.status, BridgeStatus.NEEDS_RULE)
        self.assertIn("armhole_drafting_policy", assessment.required_inputs)
        self.assertIn("sleeve_cap_policy", assessment.required_inputs)
        self.assertNotIn("svg", assessment.reason.lower())
        self.assertNotIn("bezier", assessment.reason.lower())

    def test_unknown_semantic_value_is_unsupported(self):
        fake = SimpleNamespace(
            neckline="round",
            sleeve="short",
            silhouette="experimental_shape",
            length="midi",
            back_neckline="same_as_front",
            back_closure="none",
            front_darts="none",
            back_darts="none",
            front_pockets="none",
            front_buttons="none",
            front_princess_seams="none",
        )
        request = build_production_pattern_request(fake)
        self.assertEqual(request.assessment("silhouette").status, BridgeStatus.UNSUPPORTED)

    def test_request_contains_semantics_and_rules_not_drawing_coordinates(self):
        request = build_production_pattern_request(
            DressSpec(
                neckline="v",
                sleeve="short",
                silhouette="a_line",
                length="midi",
                front_darts="waist_pair",
                front_pockets="patch_pair",
            )
        )
        serialized_names = {item.feature for item in request.features}
        forbidden = {"x", "y", "path", "control1", "control2", "drawing_width", "drawing_height"}
        self.assertTrue(serialized_names.isdisjoint(forbidden))


if __name__ == "__main__":
    unittest.main()
