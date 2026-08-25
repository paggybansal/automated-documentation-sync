from pathlib import Path

import pytest

from doc_sync.errors import ManifestFileNotFoundError, ManifestJsonParseError, PathValidationError
from doc_sync.manifest_reader import read_manifest


def _fixture_path(name: str) -> Path:
    return Path(__file__).parents[1] / "fixtures" / name


def test_read_manifest_success_from_fixture() -> None:
    manifest = read_manifest(_fixture_path("valid_endpoints.json"))

    assert manifest["serviceName"] == "Billing API"
    assert manifest["version"] == "v1"
    assert len(manifest["endpoints"]) == 1


def test_read_manifest_raises_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    with pytest.raises(ManifestFileNotFoundError):
        read_manifest(missing)


def test_read_manifest_raises_for_invalid_json() -> None:
    with pytest.raises(ManifestJsonParseError):
        read_manifest(_fixture_path("invalid_json.json"))


def test_read_manifest_raises_for_directory_path(tmp_path: Path) -> None:
    directory_path = tmp_path / "manifest_dir"
    directory_path.mkdir()

    with pytest.raises(PathValidationError):
        read_manifest(directory_path)


def test_read_manifest_raises_for_non_object_root(tmp_path: Path) -> None:
    array_manifest = tmp_path / "array_manifest.json"
    array_manifest.write_text("[]", encoding="utf-8")

    with pytest.raises(ManifestJsonParseError):
        read_manifest(array_manifest)
