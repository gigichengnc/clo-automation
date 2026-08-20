"""Minimal CLI for the first parametric sizing prototype.

The CLI can collect body measurements and a garment request interactively or
load them from JSON, validate each layer, and resolve a school-skirt garment
specification. It does not generate or modify any DXF files.
"""

import argparse
import json
from pathlib import Path

from garment.request import GarmentRequest
from garment.validation import validate_garment_request
from measurements.body import BodyMeasurements
from measurements.validation import validate_body_measurements
from styles.school_skirt.spec import (
    DEFAULT_HIP_EASE_MM,
    DEFAULT_WAIST_EASE_MM,
    build_school_skirt_spec,
)
from styles.school_skirt.validation import validate_school_skirt_spec_inputs


_BODY_FIELDS = (
    "waist",
    "hip",
    "waist_to_hip",
)

_GARMENT_FIELDS = (
    "requested_length",
)


def _read_mm(label: str) -> float:
    """Read one numeric value in millimetres."""
    raw = input(f"{label} (mm): ").strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{label} must be a number") from exc


def _read_interactive() -> tuple[BodyMeasurements, GarmentRequest]:
    """Collect body measurements and the garment request from standard input."""
    body = BodyMeasurements(
        waist=_read_mm("Waist"),
        hip=_read_mm("Hip"),
        waist_to_hip=_read_mm("Waist to hip"),
    )
    request = GarmentRequest(
        requested_length=_read_mm("Requested skirt length"),
    )
    return body, request


def _read_json(path: Path) -> tuple[BodyMeasurements, GarmentRequest]:
    """Load body measurements and garment request from a JSON object."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read input file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"input file is not valid JSON: {path}") from exc

    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")

    body_data = data.get("body")
    garment_data = data.get("garment")
    if not isinstance(body_data, dict):
        raise ValueError("input JSON must contain a body object")
    if not isinstance(garment_data, dict):
        raise ValueError("input JSON must contain a garment object")

    missing_body = [field for field in _BODY_FIELDS if field not in body_data]
    if missing_body:
        raise ValueError(f"missing body field(s): {', '.join(missing_body)}")

    missing_garment = [field for field in _GARMENT_FIELDS if field not in garment_data]
    if missing_garment:
        raise ValueError(f"missing garment field(s): {', '.join(missing_garment)}")

    try:
        body_values = {field: float(body_data[field]) for field in _BODY_FIELDS}
        garment_values = {field: float(garment_data[field]) for field in _GARMENT_FIELDS}
    except (TypeError, ValueError) as exc:
        raise ValueError("all measurements and garment dimensions must be numeric") from exc

    return BodyMeasurements(**body_values), GarmentRequest(**garment_values)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate inputs for school-skirt DXF sizing.")
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON file containing separate body and garment objects in mm",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    print("DXF Generator — school-skirt sizing inputs")
    print("All dimensions use millimetres (mm).")
    print()

    try:
        if args.input:
            body, request = _read_json(args.input)
            print(f"Loaded inputs from: {args.input}")
        else:
            body, request = _read_interactive()
    except ValueError as exc:
        print(f"Input error: {exc}")
        return 2

    errors = validate_body_measurements(body)
    errors.extend(validate_garment_request(request))
    errors.extend(
        validate_school_skirt_spec_inputs(
            waist_ease=DEFAULT_WAIST_EASE_MM,
            hip_ease=DEFAULT_HIP_EASE_MM,
        )
    )
    if errors:
        print("\nInputs are not valid:")
        for error in errors:
            print(f"- {error}")
        return 1

    spec = build_school_skirt_spec(body, request)

    print("\nBody measurements accepted:")
    print(f"- waist: {body.waist:.1f} mm")
    print(f"- hip: {body.hip:.1f} mm")
    print(f"- waist_to_hip: {body.waist_to_hip:.1f} mm")

    print("\nGarment request accepted:")
    print(f"- requested_length: {request.requested_length:.1f} mm")

    print("\nSchool-skirt garment measurements:")
    print(f"- garment_waist: {spec.garment_waist:.1f} mm")
    print(f"- garment_hip: {spec.garment_hip:.1f} mm")
    print(f"- waist_to_hip: {spec.waist_to_hip:.1f} mm")
    print(f"- skirt_length: {spec.skirt_length:.1f} mm")
    print(f"- waist_ease: {spec.waist_ease:.1f} mm")
    print(f"- hip_ease: {spec.hip_ease:.1f} mm")

    print("\nNo DXF has been generated yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
