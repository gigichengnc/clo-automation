"""Named parameter specs for reproducible quadratic Bezier side-seam research candidates.

This module binds one stable candidate identifier to one pure quadratic Bezier
strategy-parameter spec, then explicitly adapts that data into the existing
``SideSeamPolicyCandidateSpec`` used by the multi-policy comparison runner.

It defines no candidate defaults, preferred curve, ranking, tolerance,
production selection, seam allowance, or DXF behavior. Quadratic parameter
validation remains owned by the existing strategy factory and its downstream
control-point / sampled-curve contracts. Candidate-identifier validation remains
owned by the existing named-result evaluation pipeline.
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_multi_policy_runner import (
    SideSeamPolicyCandidateSpec,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    SchoolSkirtQuadraticBezierStrategyParameters,
    build_quadratic_bezier_side_seam_strategy,
)


@dataclass(frozen=True)
class NamedQuadraticCandidateSpec:
    """One stable candidate identifier plus reproducible quadratic parameters."""

    candidate_id: str
    parameters: SchoolSkirtQuadraticBezierStrategyParameters


def build_quadratic_policy_candidate_spec(
    candidate: NamedQuadraticCandidateSpec,
) -> SideSeamPolicyCandidateSpec:
    """Adapt one named quadratic research configuration to the policy runner."""

    return SideSeamPolicyCandidateSpec(
        candidate_id=candidate.candidate_id,
        strategy=build_quadratic_bezier_side_seam_strategy(candidate.parameters),
    )
