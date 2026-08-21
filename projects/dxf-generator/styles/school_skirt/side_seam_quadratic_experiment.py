"""Immutable manifests for reproducible quadratic side-seam research experiments.

This module groups one experiment name with an ordered tuple of already-named
quadratic Bezier research candidate specs, then delegates execution to the
existing named-quadratic runner. The returned bundle keeps the experiment name
attached to the existing measurement-only collection and comparison snapshot.

The supplied candidate order is preserved exactly. This module defines no
candidate defaults, sorting, ranking, scoring, tolerance, pass/fail judgement,
winner selection, production policy, seam allowance, or DXF behavior.

Candidate-parameter and candidate-identifier validation remain owned by the
existing downstream contracts. Empty candidate tuples remain valid because the
existing named runner deliberately supports empty comparison sets.
"""

from dataclasses import dataclass

from styles.school_skirt.side_seam_candidate_collection_evaluator import (
    SideSeamCandidateCollectionEvaluation,
)
from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
)
from styles.school_skirt.side_seam_named_quadratic_runner import (
    run_named_quadratic_candidates,
)
from styles.school_skirt.side_seam_piecewise_policy import (
    SideSeamPiecewiseGeometryInput,
)


@dataclass(frozen=True)
class QuadraticResearchExperimentManifest:
    """One named immutable experiment containing ordered research candidates."""

    experiment_name: str
    candidates: tuple[NamedQuadraticCandidateSpec, ...]


@dataclass(frozen=True)
class QuadraticResearchExperimentEvaluation:
    """Experiment identity attached to the existing comparison evaluation."""

    experiment_name: str
    evaluation: SideSeamCandidateCollectionEvaluation


def run_quadratic_research_experiment(
    *,
    front_input: SideSeamPiecewiseGeometryInput,
    back_input: SideSeamPiecewiseGeometryInput,
    manifest: QuadraticResearchExperimentManifest,
) -> QuadraticResearchExperimentEvaluation:
    """Run one manifest through the existing named quadratic comparison pipeline."""

    return QuadraticResearchExperimentEvaluation(
        experiment_name=manifest.experiment_name,
        evaluation=run_named_quadratic_candidates(
            front_input=front_input,
            back_input=back_input,
            candidates=manifest.candidates,
        ),
    )
