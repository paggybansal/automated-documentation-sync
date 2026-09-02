# Copilot Instructions for `automated-documentation-sync`

These instructions apply to all Copilot-assisted work on this repository.

## Project Context

This repository is a Python 3.11+ CLI project named **Automated Documentation Sync**.
The application reads API endpoint metadata from a JSON manifest, generates Markdown API documentation, and safely synchronizes only content between DOCS_SYNC markers in a Markdown file.

## Required Context Review

Before changing any **production code**, read and align with:
- `requirements.md`
- `architecture.md`
- `design-review.md`
- `impl-plan.md`

If requirements or behavior are ambiguous, ask clarification questions before implementation.

## Language and Implementation Standards

- Use **Python 3.11+**.
- Add and maintain **type hints** for all new or changed production code.
- Prefer Python standard-library modules unless a dependency is clearly justified.
- Prefer and use standard modules such as `pathlib`, `argparse`, `json`, `dataclasses`, and `typing` where appropriate.
- Use `pathlib.Path` for filesystem operations instead of raw string paths where possible.

## Validation and Safety Requirements

Validate all inputs before processing or writing:
- Input JSON format and parse validity.
- Required manifest fields.
- Endpoint fields.
- File paths (existence, type, and allowed scope).
- Command-line arguments.
- Documentation markers and pairing using these exact lines:
  - `<!-- DOCS_SYNC:START -->`
  - `<!-- DOCS_SYNC:END -->`

Never overwrite or modify content outside these marker boundaries.

## Failure Handling Requirements

Fail safely and return clear errors for:
- Missing files.
- Invalid JSON.
- Empty endpoints.
- Missing required fields.
- Missing markers.
- Invalid marker order.

## Testing and Quality Gates

For every behavior change:
- Add or update **pytest** tests.

Before claiming work is done, run and verify:
- Ruff linting.
- Ruff formatting verification.
- Unit tests.
- Integration tests.
- Documentation freshness validation.

## Security and Scope Controls

- Never add or expose secrets, tokens, credentials, private URLs, or environment files.
- Avoid unrelated refactoring.

## Human Approval Gates

Before editing production code:
- Present a file-level plan.
- Wait for explicit human approval.

Never perform the following without explicit human approval:
- Commit.
- Push.
- Create a pull request.
- Delete files.
- Perform destructive Git operations.

## Task Completion Reporting

At task completion, summarize:
- Changed files.
- Decisions made.
- Commands run and their actual results.

