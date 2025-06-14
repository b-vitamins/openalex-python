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
- Synchronous ``OpenAlexClient`` for simple API access

### Changed
- Fixed caching logic to handle list queries and thread safety
- License clarification: Now consistently MIT licensed
- Request caching disabled by default
- Verified caching behavior with updated tests
- Documentation examples for institutions are now self-contained

### Fixed
- Retry logic now honors `max_retries` without exceeding the limit
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
- Custom HTTP error handling now returns the correct exception types and
  captures ``retry-after`` values without triggering long retries in tests
- Updated Ruff configuration to ignore test-only warnings
- Pytest configuration skips docs-based examples
- Refactored test suite for maintainability and clarity

- Fixed utility helpers and improved parameter, retry, and text functions to
  pass unit tests
- Query builder now correctly handles search and group_by parameters
  and autocomplete results no longer raise validation errors
- Async query methods align with sync API and handle partial metadata

### Fixed
- License inconsistency between LICENSE file and pyproject.toml
- AsyncQuery pagination now respects cursors and returns correct counts
- Configuration now loads API key and email from environment variables and is
  immutable after creation
- Retry logic interprets ``max_retries`` as the number of retries
- Paginator iteration now yields pages and ``ListResult`` exposes ``groups``
  for group-by queries
- Parameter serialization encodes spaces correctly and preserves comparison operators
- Cache managers are isolated per configuration instance
- Retry decorator now uses ``max_retries`` plus the initial attempt
- Pagination utilities no longer loop indefinitely when cursors are ignored and
  now respect ``max_results`` across sync and async iterators.

[Unreleased]: https://github.com/b-vitamins/openalex-python/compare/HEAD
