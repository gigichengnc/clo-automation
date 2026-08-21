"""Deterministic JSON-compatible serialization for quadratic research manifests.

This module projects one ``QuadraticResearchExperimentManifest`` into a stable,
versioned dictionary made only of JSON-compatible container and scalar types.
It performs no file I/O, deserialization, candidate ranking, tolerance checks,
production selection, seam allowance, or DXF behavior.

Candidate order is preserved exactly. Research values are not normalized or
modified. Standard JSON compatibility is checked with ``allow_nan=False`` so
non-finite numeric values cannot silently become non-standard JSON tokens.
"""

import json

from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
)
from styles.school_skirt.side_seam_quadratic_experiment import (
    QuadraticResearchExperimentManifest,
)


QUADRATIC_RESEARCH_EXPERIMENT_FORMAT = (
    "school-skirt-quadratic-side-seam-research-experiment"
)
QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION = 1


def _serialize_segment_parameters(
    parameters: QuadraticBezierSegmentParameters,
) -> dict[str, object]:
    return {
        "along_fraction": parameters.along_fraction,
        "normal_offset": parameters.normal_offset,
        "sample_count": parameters.sample_count,
    }


def _serialize_candidate(candidate: NamedQuadraticCandidateSpec) -> dict[str, object]:
    return {
        "candidate_id": candidate.candidate_id,
        "parameters": {
            "waist_to_hip": _serialize_segment_parameters(
                candidate.parameters.waist_to_hip
            ),
            "hip_to_hem": _serialize_segment_parameters(
                candidate.parameters.hip_to_hem
            ),
        },
    }


def serialize_quadratic_research_experiment_manifest(
    manifest: QuadraticResearchExperimentManifest,
) -> dict[str, object]:
    """Return one stable JSON-compatible dictionary for the supplied manifest."""

    serialized = {
        "format": QUADRATIC_RESEARCH_EXPERIMENT_FORMAT,
        "version": QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION,
        "experiment_name": manifest.experiment_name,
        "candidates": [
            _serialize_candidate(candidate)
            for candidate in manifest.candidates
        ],
    }

    # Validate generic JSON compatibility without changing the returned shape.
    json.dumps(serialized, allow_nan=False)
    return serialized
