from __future__ import annotations

from pathlib import Path


class DocSyncError(Exception):
    """Base class for all documentation sync domain errors."""


class ArgumentValidationError(DocSyncError):
    """Raised when CLI argument combinations are invalid."""


class PathValidationError(DocSyncError):
    """Raised for invalid or inaccessible file paths."""


class ManifestFileNotFoundError(PathValidationError):
    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        super().__init__(f"Manifest file not found: {manifest_path}")


class ManifestJsonParseError(DocSyncError):
    def __init__(self, manifest_path: Path, details: str) -> None:
        self.manifest_path = manifest_path
        self.details = details
        super().__init__(f"Invalid JSON in manifest '{manifest_path}': {details}")


class ManifestValidationError(DocSyncError):
    """Raised when manifest content does not satisfy required schema rules."""


class MissingRootFieldError(ManifestValidationError):
    def __init__(self, field_name: str) -> None:
        self.field_name = field_name
        super().__init__(f"Manifest is missing required root field: '{field_name}'")


class EmptyEndpointsError(ManifestValidationError):
    def __init__(self) -> None:
        super().__init__("Manifest 'endpoints' must be a non-empty list")


class MissingEndpointFieldError(ManifestValidationError):
    def __init__(self, endpoint_index: int, field_name: str) -> None:
        self.endpoint_index = endpoint_index
        self.field_name = field_name
        super().__init__(
            f"Endpoint at index {endpoint_index} is missing required field: '{field_name}'"
        )


class UnsupportedHttpMethodError(ManifestValidationError):
    def __init__(self, endpoint_index: int, method: str) -> None:
        self.endpoint_index = endpoint_index
        self.method = method
        super().__init__(
            f"Endpoint at index {endpoint_index} has unsupported HTTP method: '{method}'"
        )


class MarkerValidationError(DocSyncError):
    """Raised when documentation marker constraints are violated."""


class StaleDocumentationError(DocSyncError):
    """Raised in check-mode when generated content does not match documentation."""
