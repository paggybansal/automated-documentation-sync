# Pull Request: Automated Documentation Sync CLI

## Summary

Implements the Automated Documentation Sync Python CLI.

The tool reads API endpoint metadata from a JSON manifest, generates Markdown API
reference content, and safely updates only the content between protected
DOCS_SYNC markers in a Markdown document.

## Changes Made

### Documentation and Planning

- Added approved requirements, architecture, design review, and implementation plan.
- Added GitHub Copilot repository instructions, reusable prompts, and the
  Documentation Sync skill.
- Added code review records and final verification report.

### Python Application

- Added typed API manifest and endpoint data models.
- Added JSON manifest reading and validation.
- Added custom readable domain errors.
- Added deterministic Markdown API reference rendering.
- Added Markdown table-value normalization for pipe characters and line breaks.
- Added strict DOCS_SYNC marker validation.
- Added marker-safe documentation synchronization.
- Added CLI support for:
  - `--write`
  - `--check`
  - `--manifest`
  - `--output`
- Added exit-code behavior:
  - `0` for successful update/current documentation
  - `1` for stale documentation in check mode
  - `2` for invalid arguments or input/domain errors

### Testing and Automation

- Added pytest unit tests.
- Added pytest CLI integration tests using `tmp_path`.
- Added sample `api/endpoints.json`.
- Added generated `docs/API_REFERENCE.md`.
- Added pre-commit checks.
- Added GitHub Actions validation for Pull Requests and pushes to `main`.

## Safety Controls

- Exactly one `<!-- DOCS_SYNC:START -->` marker is required.
- Exactly one `<!-- DOCS_SYNC:END -->` marker is required.
- The start marker must occur before the end marker.
- Content outside the marker block is preserved.
- Invalid markers result in no output-file modification.
- `--check` never writes documentation.
- CI runs `docs-sync --check` only and never runs write mode.

## Test Evidence

| Command | Result |
|---|---|
| `python -m ruff check .` | Passed — "All checks passed!" |
| `python -m ruff format --check .` | Passed — "40 files already formatted" |
| `python -m pytest tests/unit -v` | Passed — 38 tests |
| `python -m pytest tests/integration -v` | Passed — 17 tests |
| `docs-sync --write` | Exit 0 — "No update required." |
| `docs-sync --check` | Exit 0 — "Documentation is current." |
| `pre-commit run --all-files` | Not run locally — environment-level `git check-attr` subprocess error on this machine, unrelated to project code; underlying Ruff checks pass via direct invocation above |

## Known Limitations

The following are intentionally out of scope:

- YAML manifests
- OpenAPI/Swagger parsing
- Automatic endpoint discovery from source code
- Multiple generated documentation blocks in one document
- External API calls
- Databases
- Cloud deployment
- Automatic Pull Request merge

## Reviewer Checklist

- [ ] Review JSON manifest validation and readable error handling.
- [ ] Review Markdown table generation and value normalization.
- [ ] Review marker validation and file-safety behavior.
- [ ] Confirm content outside DOCS_SYNC markers is preserved.
- [ ] Confirm `--check` does not modify files.
- [ ] Confirm CLI exit codes are documented and tested.
- [ ] Confirm test coverage includes success and failure paths.
- [ ] Confirm GitHub Actions uses `docs-sync --check` only.
- [ ] Confirm no secrets, credentials, or private URLs are included.