# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Synchronized dependency files with pyproject.toml for consistency
- Updated requirements.txt to use httpx[http2] and flexible version constraints
- Migrated from mypy to pyright for type checking in development dependencies
- Added pytest-benchmark to support performance benchmarking tests
- Configure pyright for strict type checking with optimized unknown type handling

### Fixed
- Make LogicalExpression class public to resolve private usage warnings
- Remove redundant type checking in validate_numeric_param function
- Remove unnecessary None checks in is_openalex_id function
- Fix unnecessary comparison warnings in publisher hierarchy checks
- Correct type annotation for topic date parsing to include date type
- Fix possibly unbound cache_key variable in async API cache handling
- Add explicit type annotations for generic collections to improve type inference
- Resolve filter type assignment issues with proper type narrowing
- Fix async entity method call to use self instead of parent class
- Remove unused import and simplify error handling in client

### Added
- Comprehensive retry logic for API requests
- Request caching layer for improved performance
- Full async/await support for all API operations
- Extended documentation with advanced usage examples
- Performance monitoring and metrics collection
- Optional metrics collection configurable via `collect_metrics` and reporting
  via `BaseEntity.get_metrics`
- Development guidelines for contributors in `AGENTS.md`
- Behavior-driven test suite covering async, caching, config, pagination, etc.
- Synchronous ``OpenAlexClient`` for simple API access
- Unexcluded ``Source`` model from coverage and added tests
- Unexcluded ``Institution`` model from coverage and added tests
- Unexcluded pagination utilities from coverage and added tests
- Unexcluded metrics performance module from coverage and added tests
- Batch fetching via ``BaseEntity.get_many`` and ``AsyncBaseEntity.get_many``
- Cache warming utility to pre-populate frequently accessed items
- Streaming paginator for memory-efficient iteration
- Operation-specific timeouts for API requests
- Async request queue with rate limiting
- Circuit breaker state transition logging
- Improved timeout errors with context
- Streaming paginator handles empty cursors
- Test isolation utilities to prevent patch interference and improve reliability

### Changed
- Fixed caching logic to handle list queries and thread safety
- License clarification: Now consistently MIT licensed
- Request caching disabled by default
- Cache keys now include endpoint prefix to avoid collisions
- Verified caching behavior with updated tests
- Documentation examples for institutions are now self-contained
- Expanded README with advanced usage and configuration sections
- Updated docs to use `model_dump()` instead of `dict()`
- Refreshed features section in README
- Removed GitHub workflow `tests.yml` to avoid duplicate test runs

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
- Corrected retry counting logic for clients and connection utilities
- Enhanced ``ValidationError`` with contextual fields
- Autocomplete requests now use ``/autocomplete/{endpoint}`` to avoid 404 errors
- Pagination utilities no longer loop indefinitely when cursors are ignored and
  now respect ``max_results`` across sync and async iterators.
- Codecov badge updated with repo token and new `.codecov.yml`

[Unreleased]: https://github.com/b-vitamins/openalex-python/compare/HEAD
