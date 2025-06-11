# Contributing to OpenAlex Python Client

We love your input! We want to make contributing to this project as easy and transparent as possible.

## Development Setup

1. Fork the repo and clone your fork
2. Install Poetry: `pip install poetry`
3. Install dependencies: `poetry install`
4. Install pre-commit hooks: `pre-commit install`
5. Create a branch: `git checkout -b my-feature`

## Development Workflow

1. Make your changes
2. Add tests for new functionality
3. Run tests: `pytest`
4. Run linting: `ruff check .`
5. Run type checking: `mypy openalex`
6. Commit with conventional commits

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openalex --cov-report=html

# Run specific test file
pytest tests/test_works.py

# Run async tests
pytest tests/test_async.py
```

## Code Style

We use:
- `ruff` for linting and formatting
- `mypy` for type checking
- `pre-commit` for git hooks

Code is automatically formatted on commit.

## Commit Messages

We use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `perf:` Performance improvements
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Examples:
```
feat: add async support for Works entity
fix: handle rate limit errors gracefully
docs: update examples for field selection
```

## Pull Request Process

1. Update documentation for new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Create PR with clear description
6. Link any related issues

## Adding New Features

### Adding a New Entity

1. Create model in `openalex/models/`
2. Add sync and async classes to `openalex/entities.py`
3. Add tests in `tests/`
4. Update documentation

### Adding a New Filter

1. Add to appropriate model
2. Update query builder
3. Add tests
4. Document in API reference

## Reporting Issues

Use GitHub Issues to report bugs. Include:
- Python version
- OpenAlex client version
- Minimal code to reproduce
- Error messages
- Expected behavior

## Getting Help

- Check existing issues and PRs
- Review the documentation
- Ask in discussions

Thank you for contributing!
