"""Filesystem I/O for quadratic side-seam research experiment manifests.

This module is a deliberately thin filesystem adapter around the existing strict
JSON text codec. It reads and writes UTF-8 text only; it does not create parent
directories, alter experiment identities, rank candidates, choose production
policies, add seam allowance, or perform DXF behavior.

Filesystem errors remain filesystem errors. JSON/schema errors remain owned by
the strict text codec. Written file content is exactly the deterministic JSON
text returned by the codec, including its single trailing newline.
"""

from pathlib import Path

from styles.school_skirt.side_seam_quadratic_experiment import (
    QuadraticResearchExperimentManifest,
)
from styles.school_skirt.side_seam_quadratic_experiment_json import (
    dump_quadratic_research_experiment_manifest,
    load_quadratic_research_experiment_manifest,
)


def write_quadratic_research_experiment_file(
    path: str | Path,
    manifest: QuadraticResearchExperimentManifest,
) -> None:
    """Write one manifest as deterministic UTF-8 JSON text to ``path``."""

    target = Path(path)
    text = dump_quadratic_research_experiment_manifest(manifest)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def read_quadratic_research_experiment_file(
    path: str | Path,
) -> QuadraticResearchExperimentManifest:
    """Read one UTF-8 JSON experiment file through the strict text codec."""

    source = Path(path)
    with source.open("r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    return load_quadratic_research_experiment_manifest(text)
