"""Markdown reporting for Aldrich side-seam research candidates.

The report is descriptive only. It exposes measured curve properties without
ranking, selecting, or approving any candidate for production.
"""

from styles.school_skirt.research.aldrich_side_seam_candidates import (
    AldrichSideSeamCurveComparison,
)


def _fmt_optional(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def render_aldrich_side_seam_comparison_markdown(
    comparison: AldrichSideSeamCurveComparison,
) -> str:
    """Render a non-ranked Markdown comparison of front/back curve metrics."""

    lines = [
        "# Aldrich Side-Seam Curve Candidate Comparison",
        "",
        f"Status: `{comparison.status}` / `{comparison.production_status}`",
        "",
        f"Source instruction under study: `{comparison.source_instruction}`",
        "",
        "The source instruction does not uniquely specify a mathematical curve family. These rows are explicit research interpretations only.",
        "",
        "## Candidate metrics",
        "",
        "| Candidate | Panel | Length mm | Max chord-normal deviation mm | Hip anchor error mm | Hip preserved | Hip join gap mm | Hip tangent angle deg |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |",
    ]

    for candidate in comparison.candidates:
        for panel_name, panel in (("front", candidate.front), ("back", candidate.back)):
            metrics = panel.metrics
            lines.append(
                "| "
                f"{candidate.name} | {panel_name} | {metrics.length:.3f} | "
                f"{metrics.max_chord_normal_deviation:.3f} | "
                f"{metrics.hip_anchor_error:.3f} | "
                f"{'yes' if metrics.hip_anchor_preserved else 'no'} | "
                f"{_fmt_optional(metrics.hip_join_gap)} | "
                f"{_fmt_optional(metrics.hip_tangent_angle_degrees)} |"
            )
        lines.append(
            f"\n`{candidate.name}` front/back length difference: "
            f"{candidate.back_minus_front_length:.3f} mm "
            f"(absolute {candidate.absolute_length_difference:.3f} mm).\n"
        )
        lines.append(f"Interpretation: {candidate.interpretation}")
        lines.append("")

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "No candidate is ranked or selected by this report.",
            "",
            "A smaller front/back length difference, smaller tangent angle, or exact hip-anchor passage is not by itself evidence of better fit or production correctness.",
            "",
            "These curves remain research geometry. Waist curvature, A-line flare, seam allowance, notches, grain, closure, material layers, and factory DXF remain unresolved.",
            "",
        ]
    )
    return "\n".join(lines)
