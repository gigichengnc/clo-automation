#!/usr/bin/env python3
"""Generate a research-only school-skirt panel-balance comparison report.

This tool compares a symmetric architectural baseline with the quarantined
Winifred Aldrich tailored-skirt candidate under the *same* finished-waist and
finished-hip contract. It does not select a winner, modify the production gate,
generate pattern geometry, or export DXF.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from measurements.body import BodyMeasurements
from styles.school_skirt.research.aldrich_tailored_candidate import (
    ALDRICH_HIP_EASE_MM,
    ALDRICH_WAIST_EASE_MM,
    AldrichVariant,
    build_aldrich_tailored_skirt_candidate,
)
from styles.school_skirt.research.panel_balance_comparison import (
    PanelBalanceComparisonContext,
    build_symmetric_panel_balance_baseline,
    compare_panel_balance_candidates,
    panel_balance_evidence_from_aldrich,
    render_panel_balance_comparison_markdown,
)


EXCLUDED_49_51 = (
    "49/51 published method: not instantiated because the current audit does not "
    "yet encode a complete same-finished-contract front/back waist allocation"
)


def build_report(
    *,
    waist: float,
    hip: float,
    waist_to_hip: float,
    variant: AldrichVariant,
) -> str:
    body = BodyMeasurements(
        waist=waist,
        hip=hip,
        waist_to_hip=waist_to_hip,
    )

    # The controlled comparison intentionally fixes the finished garment to the
    # Aldrich candidate's stated ease so that panel-balance differences are not
    # confounded by different finished waist/hip measurements.
    context = PanelBalanceComparisonContext(
        body=body,
        finished_waist=waist + ALDRICH_WAIST_EASE_MM,
        finished_hip=hip + ALDRICH_HIP_EASE_MM,
    )

    aldrich = build_aldrich_tailored_skirt_candidate(body, variant=variant)
    report = compare_panel_balance_candidates(
        context,
        (
            ("symmetric baseline", build_symmetric_panel_balance_baseline(context)),
            (
                f"Aldrich {variant.value}",
                panel_balance_evidence_from_aldrich(aldrich),
            ),
        ),
        excluded_candidates=(EXCLUDED_49_51,),
    )
    return render_panel_balance_comparison_markdown(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare research school-skirt panel-balance candidates."
    )
    parser.add_argument("--waist", type=float, required=True, help="Body waist in mm")
    parser.add_argument("--hip", type=float, required=True, help="Body hip in mm")
    parser.add_argument(
        "--waist-to-hip",
        type=float,
        required=True,
        help="Body waist-to-hip vertical measurement in mm",
    )
    parser.add_argument(
        "--variant",
        choices=[variant.value for variant in AldrichVariant],
        required=True,
        help="Explicit Aldrich research variant; never auto-selected",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown output path; stdout is used when omitted",
    )
    args = parser.parse_args()

    markdown = build_report(
        waist=args.waist,
        hip=args.hip,
        waist_to_hip=args.waist_to_hip,
        variant=AldrichVariant(args.variant),
    )

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
