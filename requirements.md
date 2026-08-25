# Requirements: Automated Documentation Sync

## 1. Problem Statement
Repository maintainers need a reliable way to keep API reference documentation synchronized with a JSON endpoint manifest. Manual updates are error-prone and can cause stale or inaccurate documentation to be merged. The solution must generate consistent Markdown documentation and validate freshness in Pull Requests, while safely limiting file changes to an explicitly marked generated block.

## 2. User Story
As a repository maintainer, I want to automatically generate and validate API reference documentation from an API endpoint manifest so that API documentation remains accurate and stale documentation is detected before code is merged.

## 3. Stakeholders
- Repository maintainers
- API developers
- Technical writers/documentation owners
- Code reviewers and release approvers
- CI/CD maintainers

## 4. Scope
### In Scope
- Python 3.11+ command-line application.
- JSON manifest parsing from a default or user-specified file path.
- Validation of manifest structure and endpoint fields.
- Markdown generation for API reference content.
- Safe synchronization of generated content only between required DOCS_SYNC markers.
- Check mode that detects stale documentation without modifying files.
- Write mode that updates stale generated content.
- Unit and integration tests using pytest.
- Pull Request validation with Ruff, tests, and documentation freshness checks in GitHub Actions.

### Out of Scope
- YAML input support.
- OpenAPI/Swagger parsing.
- Automatic endpoint discovery from source code.
- Multiple generated blocks in one Markdown document.
- Secrets/tokens/credentials handling.
- External network calls.
- Database integration.
- Cloud deployment.
- Automatic Pull Request merge.

## 5. Functional Requirements
- FR-001: The tool SHALL run on Python 3.11 or newer.
- FR-002: The tool SHALL accept endpoint manifest input in JSON format only.
- FR-003: The default manifest path SHALL be `api/endpoints.json`.
- FR-004: The default output documentation path SHALL be `docs/API_REFERENCE.md`.
- FR-005: The manifest root object SHALL contain required fields: `serviceName`, `version`, and `endpoints`.
- FR-006: The `endpoints` field SHALL be a non-empty list.
- FR-007: Each endpoint object SHALL contain required fields: `method`, `path`, `summary`, and `authentication`.
- FR-008: Allowed endpoint `method` values SHALL be: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- FR-008a: Endpoint `method` validation SHALL be case-sensitive; only uppercase values are valid.
- FR-009: Generated Markdown SHALL include the service name and version.
- FR-010: Generated Markdown SHALL include an endpoint table with columns: `Method`, `Path`, `Description`, `Authentication`.
- FR-011: The tool SHALL only update content between these exact marker lines:
  - `<!-- DOCS_SYNC:START -->`
  - `<!-- DOCS_SYNC:END -->`
- FR-012: The tool SHALL preserve all content outside the marker block unchanged.
- FR-013: If marker lines are missing or the start marker appears after the end marker, the tool SHALL fail without modifying the output file.
- FR-014: The CLI SHALL support `--write` mode to update stale generated content.
- FR-015: The CLI SHALL support `--check` mode to detect stale documentation without modifying files.
- FR-016: The CLI SHALL support optional `--manifest <path>` to override the default manifest path.
- FR-017: The CLI SHALL support optional `--output <path>` to override the default output path.
- FR-018: Missing manifest file SHALL be treated as an error.
- FR-019: Missing output documentation file SHALL be treated as an error.
- FR-020: Invalid JSON SHALL be treated as an error.
- FR-021: Invalid manifest data (including missing required fields, invalid methods, or empty endpoints) SHALL be treated as an error.
- FR-022: The CLI SHALL require exactly one execution mode: `--write` or `--check`.
- FR-023: Providing both `--write` and `--check`, or providing neither, SHALL be treated as an invalid argument error.
- FR-024: The output Markdown file SHALL contain exactly one valid DOCS_SYNC marker pair (`<!-- DOCS_SYNC:START -->` then `<!-- DOCS_SYNC:END -->`); otherwise processing SHALL fail safely without file modification.

## 6. Non-Functional Requirements
- NFR-001: Implementation SHALL use Python standard-library modules where possible; additional runtime dependencies SHALL be avoided unless clearly justified.
- NFR-002: File-system operations SHALL use `pathlib.Path`.
- NFR-003: Production code SHALL use type hints.
- NFR-004: Error messages SHALL be understandable and actionable for maintainers.
- NFR-005: The tool SHALL prioritize file safety by preventing writes outside marker boundaries.
- NFR-006: The project SHALL include pytest unit tests and pytest-based CLI integration tests for behavior changes.
- NFR-007: Code quality SHALL be validated with Ruff linting and Ruff formatting verification.
- NFR-008: GitHub Actions Pull Request validation SHALL run linting, formatting verification, unit tests, integration tests, and documentation freshness checks.
- NFR-009: The solution SHALL not include secrets, tokens, credentials, private URLs, environment files, external API calls, or database dependencies.
- NFR-010: Changes SHALL avoid unrelated refactoring.
- NFR-011: Implementation work for this project SHALL be performed with GitHub Copilot in PyCharm, with explicit human approval before major changes.
- NFR-012: Error messages SHALL include enough context for diagnosis, including the failing file path and the failing field or validation condition when applicable.

## 7. CLI Behavior and Exit Codes
- Supported arguments:
  - `--write`: Update generated documentation block when stale.
  - `--check`: Validate documentation freshness without file modification.
  - `--manifest <path>`: Optional manifest file path override.
  - `--output <path>`: Optional output Markdown file path override.
- Mode rules:
  - Exactly one of `--write` or `--check` MUST be provided.
  - Passing both `--write` and `--check` is invalid.
  - Passing neither `--write` nor `--check` is invalid.
- Exit codes:
  - `0`: Successful write, no changes needed, or documentation is current.
  - `1`: Documentation is stale in `--check` mode.
  - `2`: Invalid command arguments, missing files, invalid JSON, invalid manifest data, missing required fields, empty endpoints, missing markers, or invalid marker order.

## 8. Error Handling Requirements
- EHR-001: Missing manifest file SHALL return exit code `2` with a clear error message.
- EHR-002: Missing output file SHALL return exit code `2` with a clear error message.
- EHR-003: Invalid JSON parse failures SHALL return exit code `2` with a clear error message.
- EHR-004: Missing root fields (`serviceName`, `version`, `endpoints`) SHALL return exit code `2`.
- EHR-005: Empty `endpoints` SHALL return exit code `2`.
- EHR-006: Missing endpoint fields (`method`, `path`, `summary`, `authentication`) SHALL return exit code `2`.
- EHR-007: Unsupported HTTP methods SHALL return exit code `2`.
- EHR-008: Missing markers or invalid marker order SHALL return exit code `2` and MUST NOT modify the output file.
- EHR-009: In `--check` mode, stale documentation SHALL return exit code `1` and MUST NOT modify files.
- EHR-010: Providing both `--write` and `--check` SHALL return exit code `2` with a clear argument error.
- EHR-011: Providing neither `--write` nor `--check` SHALL return exit code `2` with a clear argument error.
- EHR-012: If more than one DOCS_SYNC marker pair is present, processing SHALL return exit code `2` and MUST NOT modify the output file.

## 9. Acceptance Criteria
- AC-001: Given a valid JSON manifest at `api/endpoints.json` and a valid target file at `docs/API_REFERENCE.md`, the tool generates valid Markdown content containing service name, version, and endpoint table.
- AC-002: The tool updates only content between `<!-- DOCS_SYNC:START -->` and `<!-- DOCS_SYNC:END -->` and preserves all other file content.
- AC-003: `--check` returns `1` when generated content is stale and does not modify files.
- AC-004: `--check` returns `0` when documentation is current.
- AC-005: `--write` updates stale generated content and returns `0`.
- AC-006: Missing manifest or output file returns `2` with understandable errors.
- AC-007: Invalid JSON returns `2` with understandable errors.
- AC-008: Missing required root or endpoint fields returns `2`.
- AC-009: Empty endpoints list returns `2`.
- AC-010: Invalid marker presence/order returns `2` and output file remains unchanged.
- AC-011: Allowed methods are enforced as `GET`, `POST`, `PUT`, `PATCH`, `DELETE`; invalid methods return `2`.
- AC-012: CI Pull Request workflow validates Ruff linting, Ruff formatting, unit tests, integration tests, and documentation freshness.
- AC-013: Passing both `--write` and `--check` returns `2` with an invalid argument error.
- AC-014: Passing neither `--write` nor `--check` returns `2` with an invalid argument error.
- AC-015: Lowercase or mixed-case HTTP method values are rejected and return `2`.
- AC-016: If the output file contains more than one marker pair, processing returns `2` and leaves the file unchanged.

## 10. Assumptions
- The target Markdown file already exists and contains exactly one marker pair for generated content.
- The manifest schema for this phase is limited to fields explicitly defined in these requirements.
- Local developer workflows may optionally use pre-commit, but CI is the enforcement source of truth.
- Any behavior not explicitly defined here defaults to fail-safe validation with non-destructive file handling.

## 11. Risks
- Marker misuse in documentation files may block updates until corrected.
- Strict required fields may require manifest migration work for existing repositories.
- Stale docs checks can fail Pull Requests if contributors do not run local checks before pushing.
- Divergence between local environments and CI can cause inconsistent quality outcomes without documented setup.

## 12. Clarification Decision Log
| Decision ID | Topic | Decision | Status |
| --- | --- | --- | --- |
| CDL-001 | Runtime version | Python 3.11+ | Approved |
| CDL-002 | Manifest format | JSON only; YAML/OpenAPI out of scope | Approved |
| CDL-003 | Default paths | Manifest: `api/endpoints.json`; Output: `docs/API_REFERENCE.md` | Approved |
| CDL-004 | Required root fields | `serviceName`, `version`, `endpoints` | Approved |
| CDL-005 | Endpoint list rule | `endpoints` must be non-empty | Approved |
| CDL-006 | Required endpoint fields | `method`, `path`, `summary`, `authentication` | Approved |
| CDL-007 | Allowed methods | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` | Approved |
| CDL-008 | Markdown output | Include service name, version, and table with Method/Path/Description/Authentication | Approved |
| CDL-009 | Safe update boundaries | Update only between exact DOCS_SYNC markers | Approved |
| CDL-010 | Preserve outside content | Never modify content outside marker block | Approved |
| CDL-011 | Marker failure behavior | Missing markers or invalid order fails safely with no file change | Approved |
| CDL-012 | CLI options | `--write`, `--check`, `--manifest`, `--output` | Approved |
| CDL-013 | Exit codes | `0` success/current, `1` stale in check mode, `2` validation/input/argument/marker errors | Approved |
| CDL-014 | Missing files behavior | Missing manifest and missing output are errors | Approved |
| CDL-015 | Invalid JSON behavior | Invalid JSON is an error | Approved |
| CDL-016 | Quality gates | pytest unit + integration tests, Ruff lint + format validation, GitHub Actions PR checks | Approved |
| CDL-017 | Security/scope constraints | No secrets/credentials/private URLs/external calls/databases/cloud deployment | Approved |
| CDL-018 | Feature boundaries | No endpoint auto-discovery, no multi-block generation, no auto-merge | Approved |
| CDL-019 | CLI mode determinism | Exactly one mode required; both or neither are invalid arguments | Approved |
| CDL-020 | Method validation strictness | HTTP methods are uppercase and case-sensitive | Approved |
| CDL-021 | Marker-pair cardinality | Exactly one marker pair is supported; multiple pairs are an error | Approved |
| CDL-022 | Governance gate | Copilot in PyCharm with explicit human approval before major changes | Approved |

## 13. Human Approval
- Reviewer: Parag Bansal
- Review Date: 2026-<MM>-<DD>
- Status : Approved
- Notes: Requirements reviewed after GitHub Copilot clarification questions.
  The agreed scope is approved for architecture design.

