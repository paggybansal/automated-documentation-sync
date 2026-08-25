from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from doc_sync.documentation_sync import SyncMode, SyncStatus, sync_documentation_block
from doc_sync.errors import ArgumentValidationError, DocSyncError
from doc_sync.manifest_reader import DEFAULT_MANIFEST_PATH, read_manifest
from doc_sync.markdown_renderer import render_api_reference_section
from doc_sync.validator import validate_manifest_data

DEFAULT_OUTPUT_PATH = Path("docs/API_REFERENCE.md")


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - exercised via main
        raise ArgumentValidationError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(prog="docs-sync", description="Synchronize generated API docs")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--write", action="store_true", help="Update documentation when stale")
    mode_group.add_argument("--check", action="store_true", help="Check documentation freshness")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path to endpoint manifest JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to markdown documentation file",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()

    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        mode = SyncMode.WRITE if args.write else SyncMode.CHECK

        raw_manifest = read_manifest(args.manifest)
        manifest = validate_manifest_data(raw_manifest)
        generated_block = render_api_reference_section(manifest)
        result = sync_documentation_block(args.output, generated_block, mode)

        if result.status is SyncStatus.UPDATED:
            print("Documentation updated.")
            return 0
        if result.status is SyncStatus.CURRENT:
            if mode is SyncMode.WRITE:
                print("No update required.")
            else:
                print("Documentation is current.")
            return 0

        print("Documentation is stale.")
        return 1
    except ArgumentValidationError as exc:
        print(f"Error: Invalid command arguments: {exc}", file=sys.stderr)
        return 2
    except DocSyncError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

