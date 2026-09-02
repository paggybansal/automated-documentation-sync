from pathlib import Path

from doc_sync.errors import (
    DocSyncError,
    ManifestFileNotFoundError,
    ManifestJsonParseError,
    MissingEndpointFieldError,
    MissingRootFieldError,
    UnsupportedHttpMethodError,
)


def test_manifest_file_not_found_error_contains_path() -> None:
    err = ManifestFileNotFoundError(Path("api/endpoints.json"))

    assert isinstance(err, DocSyncError)
    assert "Manifest file not found" in str(err)
    assert "endpoints.json" in str(err)


def test_manifest_json_parse_error_contains_path_and_details() -> None:
    err = ManifestJsonParseError(Path("api/endpoints.json"), "Expecting value")

    assert "Invalid JSON in manifest" in str(err)
    assert "endpoints.json" in str(err)
    assert "Expecting value" in str(err)


def test_missing_field_errors_include_context() -> None:
    root_err = MissingRootFieldError("serviceName")
    endpoint_err = MissingEndpointFieldError(0, "method")
    method_err = UnsupportedHttpMethodError(0, "fetch")

    assert "serviceName" in str(root_err)
    assert "index 0" in str(endpoint_err)
    assert "method" in str(endpoint_err)
    assert "fetch" in str(method_err)

