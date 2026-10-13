# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- JSON manifest validation for required root fields (`serviceName`, `version`,
  `endpoints`), a non-empty `endpoints` list, required endpoint fields, and
  uppercase-only HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- Markdown API reference generation with service name, version, and a
  `Method` / `Path` / `Description` / `Authentication` table, with pipe and
  line-break normalization to keep tables valid.
- Marker-safe synchronization bounded by `<!-- DOCS_SYNC:START -->` and
  `<!-- DOCS_SYNC:END -->`, requiring exactly one correctly ordered marker pair
  and preserving all content outside the markers.
- `docs-sync` CLI with mutually exclusive, required `--write` and `--check`
  modes, plus optional `--manifest` and `--output` overrides defaulting to
  `api/endpoints.json` and `docs/API_REFERENCE.md`.
- Exit codes: `0` updated, current, or no update required; `1` stale in
  `--check` mode; `2` invalid arguments, missing files, invalid JSON, invalid
  manifest data, unsupported HTTP methods, or invalid markers.
- Unit tests for all core modules and `tmp_path`-isolated CLI integration tests
  that never modify repository files.
- Pre-commit checks for Ruff linting, Ruff formatting verification, and file
  hygiene (trailing whitespace, end-of-file, YAML, large files).
- GitHub Actions validation on pull requests and pushes to `main`, running Ruff
  linting, Ruff formatting verification, unit tests, integration tests, and
  `docs-sync --check` only, in a non-mutating configuration.
