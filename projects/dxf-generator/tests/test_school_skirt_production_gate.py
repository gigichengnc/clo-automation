"""Regression tests for the production-readiness gate of the A-line skirt pilot.

The gate must reuse canonical measurement/spec/draft layers, preserve safe-stop
behavior, and never promote prototype drafting values into production defaults.
"""

import inspect
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from garment.request import GarmentRequest
from measurements.body import BodyMeasurements
from styles.school_skirt.parameters import SchoolSkirtDraftingParameters
from styles.school_skirt.production_gate import (
    ProductionGateStatus,
    build_school_skirt_production_gate,
)


class SchoolSkirtProductionGateTests(unittest.TestCase):
    def _build_gate(self):
        body = BodyMeasurements(
            waist=700.0,
            hip=900.0,
            waist_to_hip=200.0,
        )
        request = GarmentRequest(requested_length=500.0)
        parameters = SchoolSkirtDraftingParameters(
            flare=80.0,
            front_dart_count=1,
            front_dart_length=100.0,
            back_dart_count=2,
            back_dart_length=120.0,
            waistband_height=70.0,
        )
        return build_school_skirt_production_gate(
            body,
            request,
            waist_ease=20.0,
            hip_ease=0.0,
            parameters=parameters,
        )

    def test_reuses_canonical_spec_and_policy_independent_draft_math(self):
        gate = self._build_gate()

        self.assertIsNotNone(gate.spec)
        self.assertIsNotNone(gate.draft)
        assert gate.spec is not None
        assert gate.draft is not None

        self.assertEqual(gate.spec.garment_waist, 720.0)
        self.assertEqual(gate.spec.garment_hip, 900.0)
        self.assertEqual(gate.spec.waist_to_hip, 200.0)
        self.assertEqual(gate.spec.skirt_length, 500.0)

        self.assertEqual(gate.draft.quarter_waist, 180.0)
        self.assertEqual(gate.draft.quarter_hip, 225.0)
        self.assertEqual(gate.draft.quarter_suppression, 45.0)
        self.assertEqual(gate.draft.hip_position, 200.0)
        self.assertEqual(gate.draft.hem_position, 500.0)
        self.assertEqual(gate.draft.hem_half_width, 305.0)

        self.assertEqual(
            gate.assessment("policy_independent_draft").status,
            ProductionGateStatus.SUPPORTED,
        )

    def test_numeric_parameter_validity_is_not_production_approval(self):
        gate = self._build_gate()

        self.assertEqual(
            gate.assessment("drafting_parameter_inputs").status,
            ProductionGateStatus.SUPPORTED,
        )
        self.assertEqual(
            gate.assessment("drafting_parameter_provenance").status,
            ProductionGateStatus.NEEDS_RULE,
        )
        self.assertFalse(gate.ready_for_pattern_geometry)

    def test_suppression_is_split_into_two_explicit_production_blockers(self):
        gate = self._build_gate()

        self.assertEqual(
            gate.assessment("panel_suppression_target_policy").status,
            ProductionGateStatus.NEEDS_RULE,
        )
        self.assertEqual(
            gate.assessment("suppression_allocation_policy").status,
            ProductionGateStatus.NEEDS_RULE,
        )

    def test_unresolved_production_rules_remain_explicit_blockers(self):
        gate = self._build_gate()
        blockers = {item.requirement for item in gate.blockers}

        self.assertTrue(
            {
                "drafting_parameter_provenance",
                "panel_suppression_target_policy",
                "suppression_allocation_policy",
                "dart_distribution_policy",
                "dart_placement_policy",
                "side_seam_policy",
                "hem_policy",
                "waist_finish_policy",
                "closure_policy",
                "material_layer_policy",
                "production_transforms",
            }.issubset(blockers)
        )

    def test_invalid_canonical_input_stops_before_spec_or_draft(self):
        gate = build_school_skirt_production_gate(
            BodyMeasurements(
                waist=True,
                hip=900.0,
                waist_to_hip=200.0,
            ),
            GarmentRequest(requested_length=500.0),
            waist_ease=20.0,
            hip_ease=0.0,
            parameters=SchoolSkirtDraftingParameters(),
        )

        self.assertEqual(
            gate.assessment("body_inputs").status,
            ProductionGateStatus.UNSUPPORTED,
        )
        self.assertIsNone(gate.spec)
        self.assertIsNone(gate.draft)
        self.assertFalse(gate.ready_for_pattern_geometry)

    def test_production_gate_has_no_ease_or_parameter_defaults(self):
        signature = inspect.signature(build_school_skirt_production_gate)

        self.assertIs(signature.parameters["waist_ease"].default, inspect._empty)
        self.assertIs(signature.parameters["hip_ease"].default, inspect._empty)
        self.assertIs(signature.parameters["parameters"].default, inspect._empty)

    def test_gate_stops_before_coordinate_or_dxf_generation(self):
        gate = self._build_gate()

        self.assertEqual(gate.source_contract, "school-skirt-production-gate-v0.1")
        self.assertFalse(hasattr(gate, "geometry"))
        self.assertFalse(hasattr(gate, "dxf"))
        self.assertFalse(hasattr(gate, "coordinates"))


if __name__ == "__main__":
    unittest.main()
