"""Minimal interactive CLI for the first parametric sizing prototype.

This step only collects four measurements, builds BodyMeasurements, and runs
validation. It does not generate or modify any DXF files.
"""

from measurements.body import BodyMeasurements
from measurements.validation import validate_body_measurements


def _read_mm(label: str) -> float:
    """Read one numeric measurement in millimetres."""
    raw = input(f"{label} (mm): ").strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{label} must be a number") from exc


def main() -> int:
    print("DXF Generator — body measurements")
    print("Enter measurements in millimetres (mm).")
    print()

    try:
        measurements = BodyMeasurements(
            waist=_read_mm("Waist"),
            hip=_read_mm("Hip"),
            waist_to_hip=_read_mm("Waist to hip"),
            garment_length=_read_mm("Garment length"),
        )
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
