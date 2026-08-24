"""CLI for controlled Aldrich side-seam research comparisons."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from measurements.body import BodyMeasurements
from styles.school_skirt.research.aldrich_pattern_semantics import (
    build_aldrich_research_pattern_semantics,
)
from styles.school_skirt.research.aldrich_side_seam_candidates import (
    compare_aldrich_side_seam_curve_candidates,
)
from styles.school_skirt.research.aldrich_side_seam_report import (
    render_aldrich_side_seam_comparison_markdown,
)
from styles.school_skirt.research.aldrich_tailored_candidate import (
    AldrichVariant,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare non-production Aldrich side-seam curve candidates."
    )
    parser.add_argument("--waist", type=float, required=True)
    parser.add_argument("--hip", type=float, required=True)
    parser.add_argument("--waist-to-hip", type=float, required=True)
    parser.add_argument("--skirt-length", type=float, required=True)
    parser.add_argument(
        "--variant",
        choices=tuple(item.value for item in AldrichVariant),
        required=True,
    )
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    body = BodyMeasurements(
        waist=args.waist,
        hip=args.hip,
        waist_to_hip=args.waist_to_hip,
    )
    semantics = build_aldrich_research_pattern_semantics(
        body,
        skirt_length=args.skirt_length,
        variant=AldrichVariant(args.variant),
    )
    comparison = compare_aldrich_side_seam_curve_candidates(semantics)
    report = render_aldrich_side_seam_comparison_markdown(comparison)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
