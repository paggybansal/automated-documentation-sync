import json
from pathlib import Path
from typing import Any

import pytest

from doc_sync.errors import (
    EmptyEndpointsError,
    ManifestValidationError,
    MissingEndpointFieldError,
    MissingRootFieldError,
    UnsupportedHttpMethodError,
)
from doc_sync.validator import validate_manifest_data


def _fixture_path(name: str) -> Path:
    return Path(__file__).parents[1] / "fixtures" / name


def _load_fixture(name: str) -> dict[str, Any]:
    with _fixture_path(name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _valid_manifest() -> dict[str, Any]:
    return {
        "serviceName": "Billing API",
        "version": "v1",
        "endpoints": [
            {
                "method": "GET",
                "path": "/invoices",
                "summary": "List invoices",
                "authentication": "OAuth2",
            }
        ],
    }


def test_validate_manifest_data_success() -> None:
    manifest = validate_manifest_data(_load_fixture("valid_endpoints.json"))

    assert manifest.service_name == "Billing API"
    assert manifest.endpoints[0].method == "GET"


def test_validate_manifest_data_missing_root_field() -> None:
    data = _valid_manifest()
    del data["serviceName"]

    with pytest.raises(MissingRootFieldError):
        validate_manifest_data(data)


def test_validate_manifest_data_missing_version_root_field() -> None:
    data = _valid_manifest()
    del data["version"]

    with pytest.raises(MissingRootFieldError):
        validate_manifest_data(data)


def test_validate_manifest_data_missing_endpoints_root_field() -> None:
    data = _valid_manifest()
    del data["endpoints"]

    with pytest.raises(MissingRootFieldError):
        validate_manifest_data(data)


def test_validate_manifest_data_empty_endpoints() -> None:
    data = _load_fixture("empty_endpoints.json")

    with pytest.raises(EmptyEndpointsError):
        validate_manifest_data(data)


def test_validate_manifest_data_missing_endpoint_field() -> None:
    data = _load_fixture("missing_field_endpoints.json")

    with pytest.raises(MissingEndpointFieldError):
        validate_manifest_data(data)


def test_validate_manifest_data_rejects_unsupported_http_method() -> None:
    data = _valid_manifest()
    endpoint = data["endpoints"][0]
    endpoint["method"] = "FETCH"

    with pytest.raises(UnsupportedHttpMethodError):
        validate_manifest_data(data)


def test_validate_manifest_data_rejects_lowercase_http_method() -> None:
    data = _valid_manifest()
    endpoint = data["endpoints"][0]
    endpoint["method"] = "get"

    with pytest.raises(UnsupportedHttpMethodError):
        validate_manifest_data(data)


def test_validate_manifest_data_requires_non_empty_service_name() -> None:
    data = _valid_manifest()
    data["serviceName"] = ""

    with pytest.raises(ManifestValidationError):
        validate_manifest_data(data)
