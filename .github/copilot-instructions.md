# Copilot Instructions for `automated-documentation-sync`

These instructions apply to all Copilot-assisted work on this repository.

## Required Context Review

Before making any **production code** changes, read and align with:
- `requirements.md`
- `architecture.md`
- `design-review.md`
- `impl-plan.md`

If any required document is missing, outdated, or ambiguous, pause and ask for human clarification before proceeding.

## Language and Implementation Standards

- Use **Python 3.11+**.
- Add and maintain **type hints** for all new or changed production code.
- Prefer **Python standard-library modules** whenever feasible.
- Use `pathlib.Path` for filesystem paths instead of raw string paths where possible.

## Validation and Safety Requirements

Always validate before processing or writing:
- Input JSON format and schema/expected structure.
- File paths (existence, type, and allowed scope).
- Documentation markers (`DOCS_SYNC` start/end markers) and marker pairing.
- Presence and validity of all required fields.

Never overwrite or modify content outside `DOCS_SYNC` markers.

## Testing and Quality Gates

For every behavior change:
- Add or update **pytest** tests that cover the change.
- Include unit tests and integration tests as applicable.

Before considering work complete, run:
- Ruff lint checks
- Ruff formatting check (or apply formatting as required)
- Unit tests
- Integration tests
- Documentation checks

## Security and Scope Controls

- Do not introduce or expose secrets, credentials, tokens, or private keys.
- Do not perform unrelated refactoring or scope creep in the same change.
- Keep changes focused, minimal, and traceable to requirements.

## Human Approval Gates

Ask for explicit human approval **before**:
- Performing file edits
- Creating commits
- Pushing to remotes
- Creating pull requests

If approval is not explicit, stop and ask first.

