from pathlib import Path

import pytest

from doc_sync.documentation_sync import (
    END_MARKER,
    START_MARKER,
    SyncMode,
    SyncStatus,
    sync_documentation_block,
)
from doc_sync.errors import ArgumentValidationError, MarkerValidationError, PathValidationError


def _fixture_path(name: str) -> Path:
    return Path(__file__).parents[1] / "fixtures" / name


def _read_fixture(name: str) -> str:
    return _fixture_path(name).read_text(encoding="utf-8")


def _write_fixture_copy(tmp_path: Path, name: str) -> Path:
    target = tmp_path / name
    target.write_text(_read_fixture(name), encoding="utf-8")
    return target


def test_sync_write_mode_updates_stale_content_and_preserves_outer_content(tmp_path: Path) -> None:
    output_path = _write_fixture_copy(tmp_path, "docs_with_markers_stale.md")

    result = sync_documentation_block(output_path, "CURRENT GENERATED CONTENT", SyncMode.WRITE)
    updated_content = output_path.read_text(encoding="utf-8")

    assert result.status is SyncStatus.UPDATED
    assert result.changed is True
    assert updated_content.startswith("# API Reference\n\nIntro text.\n")
    assert updated_content.endswith("\n\nFooter text.\n")
    assert f"{START_MARKER}\nCURRENT GENERATED CONTENT\n{END_MARKER}" in updated_content


def test_sync_write_mode_returns_current_without_writing_when_current(tmp_path: Path) -> None:
    output_path = _write_fixture_copy(tmp_path, "docs_with_markers_current.md")
    original_content = output_path.read_text(encoding="utf-8")

    result = sync_documentation_block(output_path, "CURRENT GENERATED CONTENT", SyncMode.WRITE)

    assert result.status is SyncStatus.CURRENT
    assert result.changed is False
    assert output_path.read_text(encoding="utf-8") == original_content


def test_sync_check_mode_returns_stale_without_writing(tmp_path: Path) -> None:
    output_path = _write_fixture_copy(tmp_path, "docs_with_markers_stale.md")
    original_content = output_path.read_text(encoding="utf-8")

    result = sync_documentation_block(output_path, "CURRENT GENERATED CONTENT", SyncMode.CHECK)

    assert result.status is SyncStatus.STALE
    assert result.changed is False
    assert output_path.read_text(encoding="utf-8") == original_content


def test_sync_check_mode_returns_current_without_writing(tmp_path: Path) -> None:
    output_path = _write_fixture_copy(tmp_path, "docs_with_markers_current.md")

    result = sync_documentation_block(output_path, "CURRENT GENERATED CONTENT", SyncMode.CHECK)

    assert result.status is SyncStatus.CURRENT
    assert result.changed is False


@pytest.mark.parametrize(
    ("fixture_name", "mode"),
    [
        ("docs_missing_start_marker.md", SyncMode.WRITE),
        ("docs_missing_end_marker.md", SyncMode.WRITE),
        ("docs_invalid_marker_order.md", SyncMode.WRITE),
        ("docs_duplicate_markers.md", SyncMode.WRITE),
        ("docs_missing_start_marker.md", SyncMode.CHECK),
        ("docs_missing_end_marker.md", SyncMode.CHECK),
        ("docs_invalid_marker_order.md", SyncMode.CHECK),
        ("docs_duplicate_markers.md", SyncMode.CHECK),
    ],
)
def test_sync_rejects_invalid_marker_config_without_writing(
    tmp_path: Path, fixture_name: str, mode: SyncMode
) -> None:
    output_path = _write_fixture_copy(tmp_path, fixture_name)
    original_content = output_path.read_text(encoding="utf-8")

    with pytest.raises(MarkerValidationError):
        sync_documentation_block(output_path, "NEW BLOCK", mode)

    assert output_path.read_text(encoding="utf-8") == original_content


def test_sync_raises_for_missing_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "missing.md"

    with pytest.raises(PathValidationError):
        sync_documentation_block(output_path, "NEW BLOCK", SyncMode.WRITE)


def test_sync_rejects_invalid_mode_type(tmp_path: Path) -> None:
    output_path = _write_fixture_copy(tmp_path, "docs_with_markers_stale.md")

    with pytest.raises(ArgumentValidationError):
        sync_documentation_block(output_path, "NEW BLOCK", "check")  # type: ignore[arg-type]


def test_sync_treats_line_ending_only_block_difference_as_current(tmp_path: Path) -> None:
    output_path = tmp_path / "docs_crlf.md"
    output_path.write_text(
        "# API Reference\r\n\r\n"
        "Intro text.\r\n"
        "<!-- DOCS_SYNC:START -->\r\n"
        "CURRENT GENERATED CONTENT\r\n"
        "<!-- DOCS_SYNC:END -->\r\n"
        "\r\n"
        "Footer text.\r\n",
        encoding="utf-8",
    )
    original = output_path.read_text(encoding="utf-8")

    result = sync_documentation_block(output_path, "CURRENT GENERATED CONTENT", SyncMode.WRITE)

    assert result.status is SyncStatus.CURRENT
    assert result.changed is False
    assert output_path.read_text(encoding="utf-8") == original


def test_sync_wraps_output_read_os_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_path = _write_fixture_copy(tmp_path, "docs_with_markers_stale.md")

    def _raise_read_error(self: Path, *, encoding: str) -> str:
        raise OSError("read failure")

    monkeypatch.setattr(Path, "read_text", _raise_read_error)

    with pytest.raises(PathValidationError):
        sync_documentation_block(output_path, "NEW BLOCK", SyncMode.CHECK)


