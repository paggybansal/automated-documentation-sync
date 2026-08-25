from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from doc_sync.errors import ManifestFileNotFoundError, ManifestJsonParseError, PathValidationError

DEFAULT_MANIFEST_PATH = Path("api/endpoints.json")


def read_manifest(manifest_path: Path | None = None) -> dict[str, Any]:
    """Read and parse the endpoint manifest from JSON."""
    path = manifest_path or DEFAULT_MANIFEST_PATH

    if not path.exists():
        raise ManifestFileNotFoundError(path)
    if not path.is_file():
        raise PathValidationError(f"Manifest path is not a file: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data: Any = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ManifestJsonParseError(path, str(exc)) from exc
    except OSError as exc:
        raise PathValidationError(f"Unable to read manifest file '{path}': {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestJsonParseError(path, "Manifest root must be a JSON object")

    return data
