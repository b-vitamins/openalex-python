# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive retry logic for API requests
- Request caching layer for improved performance
- Full async/await support for all API operations
- Extended documentation with advanced usage examples
- Performance monitoring and metrics collection
- Development guidelines for contributors in `AGENTS.md`
- Behavior-driven test suite covering async, caching, config, pagination, etc.

### Changed
- License clarification: Now consistently MIT licensed

### Fixed
- Updated Pydantic models for works and related entities to match OpenAlex data
  fixtures used in tests.
- Expanded author model with topics, topic share, and ORCID validation.
- Fixed institution model URLs to return strings and added ``parent_institution`` parsing.
- Updated publisher model to validate URLs and expose citation metrics via
  convenience properties.
- Standardized concept, funder, and keyword models to use plain strings for URL
  fields and added missing convenience properties.
- Added international description support and default level handling for
  concepts.
- Removed client-side trimming of ``counts_by_year`` lists; tests now reflect
  full data from fixtures.
- Improved error messages with more context
- Updated Ruff configuration to ignore test-only warnings
- Pytest configuration skips docs-based examples
- Refactored test suite for maintainability and clarity

- Fixed utility helpers and improved parameter, retry, and text functions to
  pass unit tests
- Query builder now correctly handles search and group_by parameters
  and autocomplete results no longer raise validation errors

### Fixed
- License inconsistency between LICENSE file and pyproject.toml

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Support for all OpenAlex entity types (Works, Authors, Institutions, etc.)
- Comprehensive data models with Pydantic validation
- Search and filter capabilities
- Pagination support
- Type hints throughout
- Basic documentation and examples

[Unreleased]: https://github.com/b-vitamins/openalex-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/b-vitamins/openalex-python/releases/tag/v0.1.0
