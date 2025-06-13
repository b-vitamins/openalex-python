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
- Improved error messages with more context
- Pytest configuration skips docs-based examples
- Refactored test suite for maintainability and clarity

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
