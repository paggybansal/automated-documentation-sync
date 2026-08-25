# Automated Documentation Sync Skill

## 1. Purpose
Use this skill to safely implement, review, and verify the Automated Documentation Sync Python CLI so generated API documentation stays accurate without modifying any content outside the approved marker block.

## 2. When to Use This Skill
Use this skill when working on:
- JSON manifest parsing and validation for API endpoints.
- Markdown API reference generation.
- Marker-bounded synchronization into documentation files.
- CLI behavior (`--write`, `--check`, exit-code rules).
- Unit/integration test design and CI validation.
- Architecture/requirements/code reviews for this project.

## 3. Required Inputs
- `requirements.md`
- `architecture.md`
- `design-review.md`
- `impl-plan.md`
- `.github/copilot-instructions.md`
- Current implementation/test files being changed

## 4. Source of Truth
- Default manifest source of truth: `api/endpoints.json`
- Default output document: `docs/API_REFERENCE.md`
- Manifest format: JSON only
- Out of scope: YAML and OpenAPI/Swagger parsing

## 5. Safety Rules
- Use `pathlib.Path` for all file operations.
- Validate paths before file I/O and return readable errors.
- Never overwrite content outside the marker block.
- If marker validation fails, do not write any file changes.
- Use type hints in production code.
- Do not use external network calls, private URLs, secrets, tokens, credentials, or database integrations.

## 6. Manifest Validation Rules
- Root manifest must include:
  - `serviceName`
  - `version`
  - `endpoints`
- `endpoints` must be a non-empty list.
- Every endpoint must include:
  - `method`
  - `path`
  - `summary`
  - `authentication`
- Allowed HTTP methods (uppercase only):
  - `GET`
  - `POST`
  - `PUT`
  - `PATCH`
  - `DELETE`
- Invalid input or files must return exit code `2`.

## 7. Documentation Marker Rules
- Exactly one start marker must exist:
  - `<!-- DOCS_SYNC:START -->`
- Exactly one end marker must exist:
  - `<!-- DOCS_SYNC:END -->`
- The start marker must occur before the end marker.
- Generated content may only be updated between these markers.
- Content outside the marker block must remain unchanged.
- No write may occur if marker validation fails.

## 8. Markdown Rendering Rules
- Render service name and version in generated API reference content.
- Render an endpoint table with columns:
  - `Method`
  - `Path`
  - `Description`
  - `Authentication`
- Normalize endpoint values before table rendering.
- Replace or escape pipe characters (`|`) and line breaks to keep Markdown tables valid.

## 9. CLI Behavior Rules
- Supported arguments:
  - `--write`
  - `--check`
  - `--manifest <path>`
  - `--output <path>`
- Exactly one mode is required: `--write` or `--check`.
- `--write` behavior:
  - If docs are stale, update marker-bounded content and return `0`.
  - If docs are current, return `0` and print a no-update message.
- `--check` behavior:
  - Never modify files.
  - Return `1` if documentation is stale.
  - Return `0` if documentation is current.
- Invalid arguments/input/files/markers must return `2`.

## 10. Testing Rules
- Use `pytest` for unit and CLI integration tests.
- Use `pytest` `tmp_path` for integration test isolation.
- Integration tests must not modify repository source, manifest, or documentation files.
- Add or update tests for every behavior change.
- Verify marker safety, render normalization, exit-code behavior, and no-write guarantees.

## 11. CI Rules
- Use Ruff for linting and formatting verification.
- GitHub Actions PR validation must run:
  - Ruff linting
  - Ruff formatting verification
  - Unit tests
  - Integration tests
  - Documentation freshness check using `docs-sync --check` only
- CI must never modify documentation, commit generated files, or push changes.

## 12. Human-in-the-Loop Rules
- Before production code edits, present a file-level plan and wait for explicit human approval.
- Do not commit, push, or create a PR without explicit human approval.
- Do not delete files or run destructive Git operations without explicit human approval.
- Do not invent test results or command outputs.

## 13. Completion Checklist
- [ ] Reviewed required inputs and aligned with all approved documents.
- [ ] Confirmed JSON-only scope and out-of-scope exclusions.
- [ ] Implemented/validated manifest field and endpoint validation rules.
- [ ] Enforced strict marker validation and no-write-on-failure behavior.
- [ ] Ensured outside-marker content preservation.
- [ ] Applied Markdown value normalization for pipes and line breaks.
- [ ] Implemented/validated CLI modes and exit codes (`0`, `1`, `2`).
- [ ] Added/updated unit and integration tests (with `tmp_path`).
- [ ] Ran Ruff linting and formatting verification.
- [ ] Verified CI uses `docs-sync --check` only and is non-mutating.
- [ ] Summarized changed files and actual commands run/results.
- [ ] Obtained explicit human approval for any commit/push/PR actions.

