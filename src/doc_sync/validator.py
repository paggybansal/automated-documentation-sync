from __future__ import annotations

from typing import Any, Final, cast

from doc_sync.errors import (
    EmptyEndpointsError,
    ManifestValidationError,
    MissingEndpointFieldError,
    MissingRootFieldError,
    UnsupportedHttpMethodError,
)
from doc_sync.models import Endpoint, HTTPMethod, Manifest

REQUIRED_ROOT_FIELDS: Final[tuple[str, ...]] = ("serviceName", "version", "endpoints")
REQUIRED_ENDPOINT_FIELDS: Final[tuple[str, ...]] = (
    "method",
    "path",
    "summary",
    "authentication",
)
ALLOWED_METHODS: Final[set[str]] = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def validate_manifest_data(manifest_data: dict[str, Any]) -> Manifest:
    """Validate raw manifest data and convert it into strongly typed models."""
    for field_name in REQUIRED_ROOT_FIELDS:
        if field_name not in manifest_data:
            raise MissingRootFieldError(field_name)

    service_name = manifest_data["serviceName"]
    version = manifest_data["version"]
    endpoints_data = manifest_data["endpoints"]

    if not isinstance(service_name, str) or not service_name.strip():
        raise ManifestValidationError("Manifest field 'serviceName' must be a non-empty string")
    if not isinstance(version, str) or not version.strip():
        raise ManifestValidationError("Manifest field 'version' must be a non-empty string")

    if not isinstance(endpoints_data, list):
        raise ManifestValidationError("Manifest field 'endpoints' must be a list")
    if not endpoints_data:
        raise EmptyEndpointsError()

    endpoints: list[Endpoint] = []
    for idx, endpoint_data in enumerate(endpoints_data):
        if not isinstance(endpoint_data, dict):
            raise ManifestValidationError(f"Endpoint at index {idx} must be a JSON object")

        for field_name in REQUIRED_ENDPOINT_FIELDS:
            if field_name not in endpoint_data:
                raise MissingEndpointFieldError(idx, field_name)

        method = endpoint_data["method"]
        path = endpoint_data["path"]
        summary = endpoint_data["summary"]
        authentication = endpoint_data["authentication"]

        if not isinstance(method, str):
            raise UnsupportedHttpMethodError(idx, str(method))
        if method not in ALLOWED_METHODS:
            raise UnsupportedHttpMethodError(idx, method)

        if not isinstance(path, str) or not path.strip():
            raise ManifestValidationError(f"Endpoint at index {idx} has invalid 'path' value")
        if not isinstance(summary, str) or not summary.strip():
            raise ManifestValidationError(f"Endpoint at index {idx} has invalid 'summary' value")
        if not isinstance(authentication, str) or not authentication.strip():
            raise ManifestValidationError(
                f"Endpoint at index {idx} has invalid 'authentication' value"
            )

        endpoints.append(
            Endpoint(
                method=cast(HTTPMethod, method),
                path=path,
                summary=summary,
                authentication=authentication,
            )
        )

    return Manifest(service_name=service_name, version=version, endpoints=endpoints)
