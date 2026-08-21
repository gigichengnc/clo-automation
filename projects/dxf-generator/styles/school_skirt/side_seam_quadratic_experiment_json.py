"""Strict JSON text codec for quadratic side-seam research experiment manifests.

This module converts one versioned quadratic research experiment manifest to
stable JSON text and reconstructs the manifest from strict JSON text. It performs
no filesystem I/O, candidate ranking, tolerance checks, production selection,
seam allowance, or DXF behavior.

Decoding validates the versioned serialization shape, rejects duplicate object
keys and non-standard JSON numeric constants, and preserves experiment/candidate
identity and candidate order exactly. Garment-domain validation remains owned by
the existing downstream quadratic strategy contracts.
"""

import json
import math

from styles.school_skirt.side_seam_named_quadratic_candidate import (
    NamedQuadraticCandidateSpec,
)
from styles.school_skirt.side_seam_quadratic_candidate_factory import (
    QuadraticBezierSegmentParameters,
    SchoolSkirtQuadraticBezierStrategyParameters,
)
from styles.school_skirt.side_seam_quadratic_experiment import (
    QuadraticResearchExperimentManifest,
)
from styles.school_skirt.side_seam_quadratic_experiment_serialization import (
    QUADRATIC_RESEARCH_EXPERIMENT_FORMAT,
    QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION,
    serialize_quadratic_research_experiment_manifest,
)


def _reject_non_standard_constant(value: str):
    raise ValueError(f"non-standard JSON numeric constant: {value}")


def _object_without_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _require_object(value, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a JSON object")
    return value


def _require_exact_keys(value: dict, expected: tuple[str, ...], path: str) -> None:
    expected_set = set(expected)
    actual_set = set(value)
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing keys: {', '.join(missing)}")
        if extra:
            parts.append(f"unexpected keys: {', '.join(extra)}")
        raise ValueError(f"{path} has invalid shape ({'; '.join(parts)})")


def _require_string(value, path: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{path} must be a string")
    return value


def _require_number(value, path: str):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path} must be numeric")
    if not math.isfinite(value):
        raise ValueError(f"{path} must be a finite number")
    return value


def _require_integer(value, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} must be an integer")
    return value


def _load_segment_parameters(value, path: str) -> QuadraticBezierSegmentParameters:
    segment = _require_object(value, path)
    _require_exact_keys(
        segment,
        ("along_fraction", "normal_offset", "sample_count"),
        path,
    )
    return QuadraticBezierSegmentParameters(
        along_fraction=_require_number(
            segment["along_fraction"],
            f"{path}.along_fraction",
        ),
        normal_offset=_require_number(
            segment["normal_offset"],
            f"{path}.normal_offset",
        ),
        sample_count=_require_integer(
            segment["sample_count"],
            f"{path}.sample_count",
        ),
    )


def _load_candidate(value, index: int) -> NamedQuadraticCandidateSpec:
    path = f"root.candidates[{index}]"
    candidate = _require_object(value, path)
    _require_exact_keys(candidate, ("candidate_id", "parameters"), path)

    parameters_path = f"{path}.parameters"
    parameters = _require_object(candidate["parameters"], parameters_path)
    _require_exact_keys(
        parameters,
        ("waist_to_hip", "hip_to_hem"),
        parameters_path,
    )

    return NamedQuadraticCandidateSpec(
        candidate_id=_require_string(candidate["candidate_id"], f"{path}.candidate_id"),
        parameters=SchoolSkirtQuadraticBezierStrategyParameters(
            waist_to_hip=_load_segment_parameters(
                parameters["waist_to_hip"],
                f"{parameters_path}.waist_to_hip",
            ),
            hip_to_hem=_load_segment_parameters(
                parameters["hip_to_hem"],
                f"{parameters_path}.hip_to_hem",
            ),
        ),
    )


def dump_quadratic_research_experiment_manifest(
    manifest: QuadraticResearchExperimentManifest,
) -> str:
    """Return deterministic UTF-8-safe JSON text terminated by one newline."""

    serialized = serialize_quadratic_research_experiment_manifest(manifest)
    return json.dumps(
        serialized,
        ensure_ascii=False,
        allow_nan=False,
        indent=2,
    ) + "\n"


def load_quadratic_research_experiment_manifest(
    text: str,
) -> QuadraticResearchExperimentManifest:
    """Parse strict versioned JSON text into one immutable research manifest."""

    if not isinstance(text, str):
        raise ValueError("experiment JSON text must be a string")

    try:
        raw = json.loads(
            text,
            parse_constant=_reject_non_standard_constant,
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid experiment JSON: {exc.msg}") from exc

    root = _require_object(raw, "root")
    _require_exact_keys(
        root,
        ("format", "version", "experiment_name", "candidates"),
        "root",
    )

    format_name = _require_string(root["format"], "root.format")
    if format_name != QUADRATIC_RESEARCH_EXPERIMENT_FORMAT:
        raise ValueError(f"unsupported experiment format: {format_name}")

    version = _require_integer(root["version"], "root.version")
    if version != QUADRATIC_RESEARCH_EXPERIMENT_FORMAT_VERSION:
        raise ValueError(f"unsupported experiment format version: {version}")

    experiment_name = _require_string(root["experiment_name"], "root.experiment_name")

    candidates_raw = root["candidates"]
    if not isinstance(candidates_raw, list):
        raise ValueError("root.candidates must be a JSON array")

    return QuadraticResearchExperimentManifest(
        experiment_name=experiment_name,
        candidates=tuple(
            _load_candidate(candidate, index)
            for index, candidate in enumerate(candidates_raw)
        ),
    )
