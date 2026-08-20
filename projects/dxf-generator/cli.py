"""Minimal CLI for the first parametric sizing prototype.

The CLI can collect four measurements interactively or load them from a JSON
file, then builds BodyMeasurements and runs validation. It does not generate or
modify any DXF files.
"""

import argparse
import json
from pathlib import Path

from measurements.body import BodyMeasurements
from measurements.validation import validate_body_measurements


_FIELDS = (
    "waist",
    "hip",
    "waist_to_hip",
    "garment_length",
)


def _read_mm(label: str) -> float:
    """Read one numeric measurement in millimetres."""
    raw = input(f"{label} (mm): ").strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{label} must be a number") from exc


def _read_interactive() -> BodyMeasurements:
    """Collect the four measurements from standard input."""
    return BodyMeasurements(
        waist=_read_mm("Waist"),
        hip=_read_mm("Hip"),
        waist_to_hip=_read_mm("Waist to hip"),
        garment_length=_read_mm("Garment length"),
    )


def _read_json(path: Path) -> BodyMeasurements:
    """Load the four required measurements from a JSON object."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read input file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"input file is not valid JSON: {path}") from exc

    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")

    missing = [field for field in _FIELDS if field not in data]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")

    try:
        values = {field: float(data[field]) for field in _FIELDS}
    except (TypeError, ValueError) as exc:
        raise ValueError("all measurements must be numeric") from exc

    return BodyMeasurements(**values)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate body measurements for DXF sizing.")
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON file containing waist, hip, waist_to_hip, and garment_length in mm",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    print("DXF Generator — body measurements")
    print("Measurements use millimetres (mm).")
    print()

    try:
        if args.input:
            measurements = _read_json(args.input)
            print(f"Loaded measurements from: {args.input}")
        else:
            measurements = _read_interactive()
    except ValueError as exc:
        print(f"Input error: {exc}")
        return 2

    errors = validate_body_measurements(measurements)
    if errors:
        print("\nMeasurements are not valid:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nMeasurements accepted:")
    print(f"- waist: {measurements.waist:.1f} mm")
    print(f"- hip: {measurements.hip:.1f} mm")
    print(f"- waist_to_hip: {measurements.waist_to_hip:.1f} mm")
    print(f"- garment_length: {measurements.garment_length:.1f} mm")
    print("\nNo DXF has been generated yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
