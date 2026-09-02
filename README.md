# Automated Documentation Sync

## Project Title and Overview

**Automated Documentation Sync** is a Python 3.11+ command-line tool (`docs-sync`)
that reads API endpoint metadata from a JSON manifest, renders a deterministic
Markdown API reference, and safely synchronizes that content into a Markdown
document — updating **only** the content between explicit `DOCS_SYNC` markers.

The tool supports two modes:

- `--write`: update the generated block when it is stale.
- `--check`: detect stale documentation without modifying any file.

## Problem Solved

API reference documentation drifts from the actual API definition when it is
maintained by hand. Stale documentation is easy to merge and hard to detect in
review.

Automated Documentation Sync solves this by:

- Generating the API reference from a single source of truth (`api/endpoints.json`).
- Restricting all writes to a marker-bounded block so manual content is preserved.
- Failing Pull Request validation when documentation is stale, using a
  check-only, non-mutating CI step.

## Features

- JSON manifest parsing with path and format validation.
- Manifest and endpoint schema validation, including uppercase-only HTTP methods.
- Deterministic Markdown generation with service name, version, and an endpoint table.
- Marker-safe synchronization that never touches content outside the markers.
- `--write` and `--check` CLI modes with mutually exclusive, required mode selection.
- Optional `--manifest` and `--output` path overrides.
- Explicit exit codes (`0`, `1`, `2`) for scripting and CI.
- Standard-library-only runtime (no third-party runtime dependencies).
- pytest unit tests and `tmp_path`-isolated CLI integration tests.
- Ruff linting/formatting, optional pre-commit hooks, and GitHub Actions validation.

## Requirements

- **Python 3.11 or newer.**
- No runtime dependencies (standard library only).
- Development dependencies (installed via the `dev` extra):
  - `pytest`
  - `pytest-cov`
  - `ruff`
  - `pre-commit`

## Installation and Setup

Clone the repository and create a virtual environment.

Windows (PowerShell):

```powershell
git clone <repository-url>
cd automated-documentation-sync
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

macOS / Linux (bash):

```bash
git clone <repository-url>
cd automated-documentation-sync
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Verify the installation by running the freshness check from the repository root:

```bash
docs-sync --check
```

Expected output when the checked-in documentation is current:

```text
Documentation is current.
```

Exit code `1` (`Documentation is stale.`) does **not** indicate a broken
installation — it means the generated block in `docs/API_REFERENCE.md` no longer
matches `api/endpoints.json`. Run `docs-sync --write` to refresh it. To inspect
the exit code explicitly:

```powershell
docs-sync --check; echo $LASTEXITCODE   # PowerShell
```

```bash
docs-sync --check; echo $?              # bash
```

If the `docs-sync` console script is not available on your `PATH`, use the
module fallback:

```bash
python -m doc_sync.cli --write
python -m doc_sync.cli --check
```

## Project Structure

```text
automated-documentation-sync/
├── api/
│   └── endpoints.json                      # Default manifest (source of truth)
├── docs/
│   └── API_REFERENCE.md                    # Default output document
├── src/
│   └── doc_sync/
│       ├── __init__.py
│       ├── cli.py                          # Argument parsing, orchestration, exit codes
│       ├── documentation_sync.py           # Marker validation and safe synchronization
│       ├── errors.py                       # Domain error taxonomy
│       ├── manifest_reader.py              # Path checks and JSON loading
│       ├── markdown_renderer.py            # Markdown generation and cell normalization
│       ├── models.py                       # Typed Manifest / Endpoint dataclasses
│       └── validator.py                    # Manifest and endpoint validation rules
├── tests/
│   ├── fixtures/                           # Manifest and Markdown test fixtures
│   ├── integration/                        # CLI integration tests (tmp_path isolated)
│   └── unit/                               # Module-level unit tests
├── .github/
│   ├── copilot-instructions.md
│   ├── prompts/                            # Reusable review and implementation prompts
│   ├── skills/documentation-sync/SKILL.md
│   └── workflows/documentation-sync.yml    # PR / push validation workflow
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.md
├── architecture.md
├── design-review.md
├── impl-plan.md
├── code-review.md
├── CHANGELOG.md
└── README.md
```

## Endpoint Manifest Format

The manifest is **JSON only**. The default path is `api/endpoints.json`.

Required root fields:

| Field | Type | Rule |
| --- | --- | --- |
| `serviceName` | string | Required |
| `version` | string | Required |
| `endpoints` | list | Required, must be a non-empty list |

Required fields for every endpoint object:

| Field | Type | Rule |
| --- | --- | --- |
| `method` | string | Required; one of `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| `path` | string | Required |
| `summary` | string | Required; rendered as the `Description` column |
| `authentication` | string | Required |

HTTP method validation is **case-sensitive**: only uppercase values are valid.
Lowercase or mixed-case values (for example `get`) are rejected with exit code `2`.

Example manifest:

```json
{
  "serviceName": "Customer Orders API",
  "version": "v1",
  "endpoints": [
    {
      "method": "GET",
      "path": "/orders",
      "summary": "List customer orders with pagination",
      "authentication": "OAuth2 Bearer token"
    },
    {
      "method": "POST",
      "path": "/orders",
      "summary": "Create a new customer order",
      "authentication": "OAuth2 Bearer token"
    },
    {
      "method": "PATCH",
      "path": "/orders/{orderId}/status",
      "summary": "Update order status for fulfillment workflow",
      "authentication": "OAuth2 Bearer token"
    }
  ]
}
```

## Documentation Marker Format

The output document must already exist and must contain exactly one occurrence
of each of these marker strings:

```text
<!-- DOCS_SYNC:START -->
<!-- DOCS_SYNC:END -->
```

Rules:

- Exactly **one** start marker and exactly **one** end marker are required.
- Marker detection is **occurrence-based**, not line-based: any appearance of
  the marker text counts toward the cardinality check, including a marker
  embedded inside another line.
- The start marker **must occur before** the end marker.
- Content **outside** the markers is **never modified**.
- `--check` **never writes files**.
- Invalid markers (missing, duplicated, or out of order) result in **no
  output-file modification** and exit code `2`.

> **Note:** This README is documentation *about* the tool and is not a
> `docs-sync` target. The marker strings shown below appear here for
> illustration only.

Example output document (`docs/API_REFERENCE.md`):

```markdown
# API Reference

## Maintainer Notes
This section is manually maintained and must never be auto-edited.

<!-- DOCS_SYNC:START -->
## API Reference

Service: Customer Orders API
Version: v1

| Method | Path | Description | Authentication |
| --- | --- | --- | --- |
| GET | /orders | List customer orders with pagination | OAuth2 Bearer token |
| POST | /orders | Create a new customer order | OAuth2 Bearer token |
| PATCH | /orders/{orderId}/status | Update order status for fulfillment workflow | OAuth2 Bearer token |
<!-- DOCS_SYNC:END -->

## Change Policy
Only content between DOCS_SYNC markers is generated.
```

## CLI Usage

Default paths:

- Manifest: `api/endpoints.json`
- Output document: `docs/API_REFERENCE.md`

```bash
docs-sync --write
docs-sync --check
docs-sync --write --manifest <path> --output <path>
docs-sync --check --manifest <path> --output <path>
```

Fallback if the `docs-sync` console script is unavailable:

```bash
python -m doc_sync.cli --write
python -m doc_sync.cli --check
```

Arguments:

| Argument | Description |
| --- | --- |
| `--write` | Update the generated block when documentation is stale |
| `--check` | Validate freshness without modifying any file |
| `--manifest <path>` | Override the default manifest path |
| `--output <path>` | Override the default output document path |

Mode rules:

- Exactly one of `--write` or `--check` must be provided.
- Passing both is an invalid-argument error (exit code `2`).
- Passing neither is an invalid-argument error (exit code `2`).

In `--write` mode, when documentation is already current the tool reports that
no update is required, writes nothing, and returns exit code `0`.

## Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | Documentation updated, already current, or no update required |
| `1` | Documentation is stale in `--check` mode |
| `2` | Invalid arguments, missing files, invalid JSON, invalid manifest data, unsupported HTTP method, or invalid documentation markers |

Freshness comparison is **line-ending insensitive**: `\r\n` and `\r` are
normalized to `\n` before the generated block is compared, so a difference in
line endings alone is reported as current and does not trigger a write.

## CLI Output Messages

| Stream | Message | Exit code | Condition |
| --- | --- | --- | --- |
| stdout | `Documentation updated.` | `0` | `--write` replaced a stale block |
| stdout | `No update required.` | `0` | `--write` and the block was already current |
| stdout | `Documentation is current.` | `0` | `--check` and the block was already current |
| stdout | `Documentation is stale.` | `1` | `--check` and the block differs |
| stderr | `Error: Invalid command arguments: <detail>` | `2` | Invalid or missing mode/arguments |
| stderr | `Error: <detail>` | `2` | Missing file, invalid JSON, invalid manifest data, or invalid markers |

## Development and Testing

Run the local validation commands from the repository root:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest tests/unit -v
python -m pytest tests/integration -v
pre-commit run --all-files
docs-sync --check
```

Run the full test suite (unit + integration with coverage):

```bash
python -m pytest
```

### Known Issues

The following quality gates currently fail in the repository and are tracked as
follow-up source-code work. They are unrelated to documentation content:

- `python -m ruff check .` reports `UP035` in `src/doc_sync/cli.py`
  (`Sequence` should be imported from `collections.abc` instead of `typing`).
- `python -m ruff format --check .` reports files that would be reformatted,
  primarily due to line-ending differences against the configured `lf` style.
- One unit test fails:
  `tests/unit/test_documentation_sync.py::test_sync_treats_line_ending_only_block_difference_as_current`.

Integration tests and `docs-sync --check` pass. Expect the linting, formatting,
and unit-test steps to fail in CI until these items are resolved.

## Pre-Commit Usage

Pre-commit is optional for local development and mirrors the CI quality checks.

```bash
pre-commit install
pre-commit run --all-files
```

Configured hooks (`.pre-commit-config.yaml`):

- `ruff` (linting)
- `ruff-format` with `--check` (formatting verification)
- `trailing-whitespace`
- `end-of-file-fixer`
- `check-yaml`
- `check-added-large-files`

Pre-commit **never** runs `docs-sync --write` and never regenerates
documentation automatically.

## GitHub Actions Validation

The workflow `.github/workflows/documentation-sync.yml` runs on pull requests
and on pushes to `main`. It uses Python 3.11 and installs the project with
`python -m pip install -e ".[dev]"`.

GitHub Actions runs:

1. Ruff linting — `python -m ruff check .`
2. Ruff formatting verification — `python -m ruff format --check .`
3. Unit tests — `python -m pytest tests/unit -v`
4. Integration tests — `python -m pytest tests/integration -v`
5. `docs-sync --check` **only**

CI is check-only and non-mutating: it never runs write mode, never modifies
documentation, and never commits, pushes, merges, or deploys.

## Safety Controls

- All validation (paths, JSON, manifest fields, markers) completes **before**
  any write is attempted.
- All filesystem operations use `pathlib.Path`.
- Only content between `<!-- DOCS_SYNC:START -->` and `<!-- DOCS_SYNC:END -->`
  is generated or replaced; content outside the markers is never modified.
- Exactly one start marker and one end marker are required, and the start marker
  must occur before the end marker.
- Invalid markers cause a safe failure with **no** output-file modification.
- `--check` never writes files.
- `--write` writes nothing when the documentation is already current.
- Processing is local-file only: no external API calls, no network access, no
  databases.
- No secrets, tokens, credentials, private URLs, or environment files are used,
  required, or stored by this project.

## Scope Limitations

The following are explicitly **out of scope**:

- YAML manifest input.
- OpenAPI / Swagger parsing.
- Cloud deployment.
- External API calls.
- Databases.
- Automatic endpoint discovery from source code.
- Automatic Pull Request merge.
- Multiple generated blocks in a single Markdown document.

## Example Workflow

1. Update the manifest:

   ```bash
   # edit api/endpoints.json
   ```

2. Detect staleness (expected exit code `1`):

   ```bash
   docs-sync --check
   ```

3. Update the generated block (expected exit code `0`):

   ```bash
   docs-sync --write
   ```

4. Confirm the documentation is current (expected exit code `0`):

   ```bash
   docs-sync --check
   ```

5. Run local quality gates:

   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m pytest tests/unit -v
   python -m pytest tests/integration -v
   pre-commit run --all-files
   ```

6. Open a Pull Request. GitHub Actions re-runs linting, formatting
   verification, unit tests, integration tests, and `docs-sync --check` only.
