# Implementation Plan: Automated Documentation Sync

## 1. Planning Objective
Deliver a Python 3.11+ CLI implementation of Automated Documentation Sync that reads endpoint metadata from JSON, renders deterministic Markdown API reference content, and safely synchronizes only the marker-bounded generated section while meeting all approved FR/NFR and design-review controls.

## 2. Approved Scope Summary
- Build a JSON-only CLI (`docs-sync`) with modes `--write` and `--check`.
- Default paths:
  - Manifest: `api/endpoints.json`
  - Documentation: `docs/API_REFERENCE.md`
- Validate required manifest structure and endpoint fields.
- Enforce strict marker safety:
  - Exactly one `<!-- DOCS_SYNC:START -->`
  - Exactly one `<!-- DOCS_SYNC:END -->`
  - Start marker must appear before end marker
  - No file modification on marker-validation failure
- Preserve all content outside marker boundaries.
- Return exit codes:
  - `0` success/current docs (including `--write` when no change is needed)
  - `1` stale docs in `--check`
  - `2` invalid args/input/markers/errors
- Use stdlib-first implementation with `pathlib.Path` for file operations.
- Include unit tests, CLI integration tests (`tmp_path` isolation), and CI PR validation with `docs-sync --check` only.

## 3. Implementation Principles
- Implement in dependency order; do not start downstream work before required upstream tasks are done.
- Keep module responsibilities aligned with `architecture.md` (`models`, `errors`, `manifest_reader`, `validator`, `markdown_renderer`, `documentation_sync`, `cli`).
- Validate before mutate: all file/path/marker/manifest checks must complete before write attempts.
- File safety first: never alter content outside DOCS_SYNC markers; no writes in `--check`; no writes on validation failure.
- Security and scope controls: local file processing only, no secrets, no network calls, no out-of-scope features.
- Test each behavior change with pytest; maintain clear unit vs integration boundaries.
- Apply human approval gates before major changes, commits, pushes, PR creation, deletion, or destructive Git operations.

## 4. Dependency-Ordered Task List

| Task ID | Priority | Description | Requirements Covered (FR/NFR) | Dependencies | Blocked By | Expected Files to Create or Modify | Validation or Test Work Required | Definition of Done |
|---|---|---|---|---|---|---|---|---|
| IMP-001 | High | Validate project/tooling baseline: Python 3.11+, package layout assumptions, `pyproject.toml` quality settings, and planned module map from architecture. | FR-001, NFR-001, NFR-007, NFR-009, NFR-011 | None | None | `pyproject.toml` (verify/update only if needed), `src/doc_sync/__init__.py` (if missing) | Run Ruff checks and dry-run pytest discovery once structure exists; verify plan enforces local-only processing with no secrets, credentials, external API calls, or database dependencies. | Tooling baseline is confirmed for Python 3.11+, quality commands are defined, module plan is executable, and security/scope constraints are explicitly captured. |
| IMP-002 | High | Create package skeleton and typed domain data models (`Manifest`, `Endpoint`) with dataclasses and typing contracts. | FR-005, FR-006, FR-007, NFR-003 | IMP-001 | IMP-001 | `src/doc_sync/models.py`, `src/doc_sync/__init__.py` | Add/plan unit tests for model construction and type-shape expectations. | Typed models exist and reflect required manifest and endpoint fields. |
| IMP-003 | High | Define custom domain error taxonomy for argument/path/JSON/validation/marker/stale states. | FR-018, FR-019, FR-020, FR-021, FR-023, FR-024, NFR-004, NFR-012 | IMP-002 | IMP-002 | `src/doc_sync/errors.py` | Unit tests for error mapping/messages format expectations. | Error classes are centralized, explicit, and usable by all layers. |
| IMP-004 | High | Implement JSON manifest reading using `pathlib.Path`, including path existence/readability checks before I/O and readable error reporting. | FR-002, FR-003, FR-016, FR-018, FR-020, NFR-002, NFR-004, NFR-009, NFR-012, DR-002 | IMP-003 | IMP-003 | `src/doc_sync/manifest_reader.py` | Unit tests: missing file, invalid path, invalid JSON, valid parse path; verify local file-only behavior with no network or external file-service access. | Manifest reader enforces local file checks, avoids network/external services, and returns structured, readable failures. |
| IMP-005 | High | Implement manifest and endpoint validation rules (required root fields, non-empty endpoints, endpoint field requirements, uppercase allowed methods). | FR-005, FR-006, FR-007, FR-008, FR-008a, FR-021, NFR-004 | IMP-004 | IMP-004 | `src/doc_sync/validator.py` | Unit tests for each invalid condition and a valid manifest case. | Validator rejects invalid data with actionable errors and accepts valid schema. |
| IMP-006 | High | Implement Markdown rendering with deterministic API reference output and safe normalization for table cells (pipes/line breaks escaped or replaced). | FR-009, FR-010, NFR-001, NFR-004, DR-003 | IMP-005 | IMP-005 | `src/doc_sync/markdown_renderer.py` | Unit tests for output structure and normalization edge cases (`|`, `\n`, `\r\n`). | Renderer emits valid, stable Markdown table content with safe cell formatting. |
| IMP-007 | High | Implement marker-based synchronization logic with strict validation: exactly one start marker, exactly one end marker, start before end, validation before write, no file modification on marker failure; preserve outside content exactly. | FR-011, FR-012, FR-013, FR-019, FR-024, NFR-005, NFR-002, DR-001 | IMP-006 | IMP-006 | `src/doc_sync/documentation_sync.py` | Unit tests: missing markers, duplicate markers, invalid order, unchanged outer content, no-write-on-failure. | Sync layer enforces all marker safety rules and guarantees bounded/non-destructive behavior. |
| IMP-008 | High | Implement CLI orchestration and argument handling for `--write`, `--check`, `--manifest`, `--output`; enforce mode exclusivity; map exit codes; implement `--write` no-change behavior (`0` + "No update required" + no write). | FR-014, FR-015, FR-016, FR-017, FR-022, FR-023, NFR-004, NFR-012, DR-004 | IMP-007 | IMP-007 | `src/doc_sync/cli.py` | Unit tests for argument combinations and exit-code mapping logic. | CLI behavior matches requirements for modes, messages, and exit codes (`0/1/2`). |
| IMP-009 | High | Build comprehensive unit test suite for core modules (`manifest_reader`, `validator`, `markdown_renderer`, `documentation_sync`, CLI internals). | NFR-006, NFR-007 | IMP-008 | IMP-008 | `tests/unit/test_manifest_reader.py`, `tests/unit/test_validator.py`, `tests/unit/test_markdown_renderer.py`, `tests/unit/test_documentation_sync.py`, `tests/unit/test_cli.py` | Execute unit tests with coverage checks and failure-case assertions. | All critical module behaviors and failure paths are covered by unit tests. |
| IMP-010 | High | Build CLI integration tests using pytest `tmp_path` and fixture files; ensure no repository file mutation; validate stale/current/write/error scenarios end-to-end. | FR-014, FR-015, FR-023, FR-024, NFR-006, NFR-005, DR-005 | IMP-009 | IMP-009 | `tests/integration/test_cli_integration.py`, `tests/fixtures/` (if needed) | Run integration suite asserting exit codes, messages, and file mutation boundaries in temporary dirs only. | Integration tests are isolated, deterministic, and do not touch repository source/manifests/docs. |
| IMP-011 | Medium | Add sample manifest and sample documentation files for local/manual validation and integration-fixture realism. | FR-003, FR-004, FR-009, FR-010 | IMP-010 | IMP-010 | `api/endpoints.json`, `docs/API_REFERENCE.md` | Validate samples pass `docs-sync --check`/`--write` expectations in controlled test runs. | Sample files are valid, marker-compliant, and useful for manual smoke checks. |
| IMP-012 | Medium | Add optional local quality automation via pre-commit hooks for Ruff and selected tests. | NFR-007, NFR-006 | IMP-011 | IMP-011 | `.pre-commit-config.yaml` | Run `pre-commit run --all-files` locally and verify hook behavior. | Pre-commit is optional, documented, and aligned with CI quality checks. |
| IMP-013 | High | Implement GitHub Actions PR validation workflow with lint, format-check, unit tests, integration tests, and `docs-sync --check` only; enforce non-mutating CI behavior (no write/commit/push). | NFR-008, NFR-007, NFR-009, FR-015, DR-006 | IMP-010 | IMP-010 | `.github/workflows/pr-validation.yml` | Validate workflow syntax and PR run behavior; confirm check-only docs freshness step and that CI does not use secrets/private URLs or external network services for documentation sync. | CI workflow gates PRs, never modifies documentation or pushes generated changes, and adheres to security/scope constraints. |
| IMP-014 | Medium | Update project documentation for usage, modes, exit codes, safety guarantees, and contributor quality workflow. | FR-014, FR-015, FR-022, FR-023, NFR-007, NFR-010 | IMP-013 | IMP-013 | `README.md`, `CHANGELOG.md` | Review docs against implemented CLI behavior and CI process. | User/developer docs are accurate, concise, and traceable to implemented behavior. |
| IMP-015 | High | Produce final verification report summarizing changed files, requirement coverage, executed commands with actual results, and residual risks. | NFR-006, NFR-007, NFR-008, NFR-011 | IMP-014 | IMP-014 | `impl-plan.md` (status notes), optional release note artifact path TBD | Run Ruff, format verification, unit tests, integration tests, and docs freshness check; capture outcomes. | Final report confirms all acceptance criteria and quality gates are satisfied or documents approved exceptions. |

## 5. Task Dependencies and Blockers
- Critical path: `IMP-001 -> IMP-002 -> IMP-003 -> IMP-004 -> IMP-005 -> IMP-006 -> IMP-007 -> IMP-008 -> IMP-009 -> IMP-010 -> IMP-013 -> IMP-014 -> IMP-015`
- Parallelizable after core implementation:
  - `IMP-011` can proceed after `IMP-010`.
  - `IMP-012` can proceed after `IMP-011`.
- Governance blocker (applies to all implementation tasks beyond planning): explicit human approval before major production-code edits, commit/push/PR/deletion/destructive git operations.
- Quality blocker before closure: all mandatory checks must pass (Ruff, formatting verification, unit tests, integration tests, docs freshness check).

## 6. Testing Plan
- Unit-test focus by module:
  - `models`: model validity and required field contracts.
  - `manifest_reader`: path checks (`pathlib.Path`), missing files, invalid JSON, successful parse.
  - `validator`: root fields, empty endpoints, missing endpoint fields, invalid methods.
  - `markdown_renderer`: service/version rendering, table layout, safe normalization of `|` and line breaks.
  - `documentation_sync`: marker cardinality/order checks, no-write-on-invalid-markers, preserve-outside-content guarantee.
  - `cli`: mode exclusivity, argument errors, exit-code mapping, "No update required" in current `--write`.
- Integration-test focus (pytest `tmp_path` only):
  - Fresh vs stale detection in `--check`.
  - Stale update and no-change behavior in `--write`.
  - End-to-end failures returning exit `2` for missing files, invalid JSON, invalid manifest, invalid markers.
  - Assertion that repository files are not touched.
- Minimum required validation scenarios:
  - exactly one start marker and one end marker
  - start marker before end marker
  - no mutation when marker validation fails
  - no mutation in `--check`
  - no mutation in `--write` when already current

## 7. GitHub Actions and Local Quality Automation Plan
- GitHub Actions PR workflow stages:
  1. Ruff linting.
  2. Ruff formatting verification.
  3. Unit tests.
  4. CLI integration tests.
  5. Documentation freshness validation via `docs-sync --check` only.
- CI safety controls:
  - Never execute write mode in CI.
  - Never modify docs, commit generated files, or push changes.
- Local automation:
  - Optional `pre-commit` hooks mirror lint/format checks and can include lightweight test checks.
  - Developers run full pytest + docs freshness checks before submitting PRs.

## 8. Risk and Mitigation Plan
- **Risk:** Marker parsing defects could overwrite unintended content.
  - **Mitigation:** Enforce DR-001 rules (single marker pair, strict order, validate-before-write, no write on failure) and add focused tests.
- **Risk:** Path mistakes could read/write wrong files.
  - **Mitigation:** Use `pathlib.Path`, require existence checks before I/O, return readable path-specific errors (DR-002).
- **Risk:** Markdown table corruption from endpoint text.
  - **Mitigation:** Normalize pipes and line breaks before rendering; test edge cases (DR-003).
- **Risk:** Confusing write behavior when docs are already current.
  - **Mitigation:** Explicit exit `0` with "No update required" and no write; integration assertion (DR-004).
- **Risk:** Integration tests accidentally mutate repository files.
  - **Mitigation:** Use pytest `tmp_path` fixtures exclusively and enforce non-mutation checks (DR-005).
- **Risk:** CI could mutate docs if misconfigured.
  - **Mitigation:** `docs-sync --check` only in CI; forbid write/commit/push behaviors (DR-006).

## 9. Definition of Done
- All in-scope FR/NFR and accepted DR controls are implemented and traced to tests.
- CLI behaviors and exit codes (`0`, `1`, `2`) match requirements, including mode exclusivity and no-change write behavior.
- Marker safety guarantees are verified: exact one start/end marker, correct ordering, and no file modifications on validation failures.
- Unit and integration tests pass locally and in CI; integration tests are isolated with `tmp_path`.
- Ruff linting and format verification pass.
- GitHub Actions PR validation runs docs freshness in check-only mode and is non-mutating.
- README/CHANGELOG reflect final behavior.
- Final verification report is produced with changed files, decisions, and command results.

## 10. Human Approval

- Reviewer: Parag Bansal
- Review Date: <use actual date>
- Status: Approved for Implementation
- Notes: The dependency-ordered implementation plan was reviewed. The scope,
  task ordering, safety controls, test strategy, and CI validation approach
  are approved for implementation.
- 