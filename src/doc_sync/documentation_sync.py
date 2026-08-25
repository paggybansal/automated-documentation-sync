from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from doc_sync.errors import ArgumentValidationError, MarkerValidationError, PathValidationError

START_MARKER = "<!-- DOCS_SYNC:START -->"
END_MARKER = "<!-- DOCS_SYNC:END -->"


class SyncMode(StrEnum):
    WRITE = "write"
    CHECK = "check"


class SyncStatus(StrEnum):
    UPDATED = "updated"
    CURRENT = "current"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class SyncResult:
    status: SyncStatus
    changed: bool


def _marker_counts(content: str) -> tuple[int, int]:
    return content.count(START_MARKER), content.count(END_MARKER)


def _normalize_line_endings(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def validate_marker_block(content: str) -> tuple[int, int, int, int]:
    """Validate marker cardinality/order and return replacement boundaries."""
    start_count, end_count = _marker_counts(content)

    if start_count != 1:
        raise MarkerValidationError(
            f"Expected exactly one start marker '{START_MARKER}', found {start_count}"
        )
    if end_count != 1:
        raise MarkerValidationError(f"Expected exactly one end marker '{END_MARKER}', found {end_count}")

    start_marker_index = content.find(START_MARKER)
    end_marker_index = content.find(END_MARKER)
    if start_marker_index > end_marker_index:
        raise MarkerValidationError("Invalid marker order: start marker appears after end marker")

    block_start = start_marker_index + len(START_MARKER)
    block_end = end_marker_index
    return start_marker_index, block_start, block_end, end_marker_index + len(END_MARKER)


def sync_documentation_block(output_path: Path, generated_block: str, mode: SyncMode) -> SyncResult:
    """Check or update marker-bounded generated content in the target markdown file."""
    if not isinstance(mode, SyncMode):
        raise ArgumentValidationError(f"Invalid sync mode: {mode!r}")

    if not output_path.exists():
        raise PathValidationError(f"Output documentation file not found: {output_path}")
    if not output_path.is_file():
        raise PathValidationError(f"Output documentation path is not a file: {output_path}")

    try:
        original_content = output_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PathValidationError(f"Unable to read output documentation file '{output_path}': {exc}") from exc

    _, block_start, block_end, _ = validate_marker_block(original_content)

    current_block = original_content[block_start:block_end]
    target_block = f"\n{generated_block}\n"
    is_current = _normalize_line_endings(current_block) == _normalize_line_endings(target_block)

    if mode == SyncMode.CHECK:
        if is_current:
            return SyncResult(status=SyncStatus.CURRENT, changed=False)
        return SyncResult(status=SyncStatus.STALE, changed=False)

    if is_current:
        return SyncResult(status=SyncStatus.CURRENT, changed=False)

    updated_content = f"{original_content[:block_start]}{target_block}{original_content[block_end:]}"
    try:
        output_path.write_text(updated_content, encoding="utf-8")
    except OSError as exc:
        raise PathValidationError(
            f"Unable to write output documentation file '{output_path}': {exc}"
        ) from exc

    return SyncResult(status=SyncStatus.UPDATED, changed=True)
