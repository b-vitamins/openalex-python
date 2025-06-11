# Development Guidelines for Codex Agents

This file outlines best practices for future development within this
repository. These instructions apply to all files unless overridden by a
more specific `AGENTS.md` in a subdirectory. Please follow these
conventions when creating pull requests.

## Housekeeping
- Keep the repository tidy and consistent.
- Delete unused code or files as you refactor.
- Maintain up-to-date dependencies in `pyproject.toml` and
  `requirements*.txt`.

## Design and Architecture
- Follow the existing modular architecture. New features should live in
  appropriately named modules within `openalex/`.
- Keep functions short and focused. Prefer composition over inheritance.
- Type hints are required for all public functions and methods.
- Document public APIs in the docstrings using reStructuredText.

## Development Practices
- Use `pre-commit` hooks locally if possible.
- Code style is enforced with Ruff and Black-compatible formatting.
- Run the full test suite with `pytest` before committing.
- Run static type checking with `mypy openalex`.

## Commit Messages
- Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Format: `type(scope?): description`.
- Examples:
  - `feat: add async support for API`
  - `fix(utils): handle rate limit errors`
  - `docs: update usage example`
- Keep commits small and focused. Separate functional changes from
  formatting-only commits.

## Pull Request Formatting
- Title: concise summary written in sentence case.
- Body must contain two sections:
  - `## Summary` – bullet points describing what changed.
  - `## Testing` – commands run and their results.
- Reference relevant issues when applicable.

## Commit Sequencing
- If a feature spans multiple logical changes, split them into multiple
  commits in a logical order (e.g., tests, implementation, docs).
- Avoid fixing unrelated issues in the same commit.

## CHANGELOG Maintenance
- Follow [Keep a Changelog](https://keepachangelog.com/) style.
- Update the `Unreleased` section with every user-facing change.
- Add links to new version tags when a release is cut.
- Keep version numbers compliant with [SemVer](https://semver.org/).

## Pre-commit Checks
Run these commands before opening a PR:

```bash
pip install --no-cache-dir -r requirements-dev.txt
ruff check .
mypy openalex
pytest
```

Any failures should be addressed before committing.


## Version Management
- Bump the patch number for bug fixes, the minor number for backward-compatible features, and the major number for breaking changes.
- Keep `openalex/__init__.py` and `pyproject.toml` versions in sync.
- Tag releases as `v<major>.<minor>.<patch>` and update the changelog links.

## Code Housekeeping
- Run `pre-commit autoupdate` monthly and commit updated hook versions.
- Remove obsolete code and unused dependencies.
- Check for outdated packages with `pip list --outdated` and update when reasonable.

## Testing Standards
- Maintain at least 85% coverage (enforced in `pytest.ini`).
- Organize tests under `tests/` using `test_*.py` naming.
- Mark slow or integration tests with `@pytest.mark.slow` or `@pytest.mark.integration`.

## Documentation Standards
- Document public APIs with reStructuredText docstrings.
- Update `README.md` and relevant docs for any user-facing change.
- Add an entry to `CHANGELOG.md` under `Unreleased` for every feature or fix.


