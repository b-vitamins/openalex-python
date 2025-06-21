<!--
OpenAlex Python Testing Excellence Guide
-->

# OpenAlex Python: Testing Excellence Guide

This document defines the canonical standards for the `tests/` directory.
It serves three purposes:
1. **Objective Evaluation**: Provides a rigorous, objective basis for identifying technical debt and code smell in the test infrastructure.
2. **Contributor Guide**: Sets clear, detailed expectations for new tests, including style, structure, and code quality.
3. **Refactoring Blueprint**: Acts as a mulit-stage, precise guide for evolving/modernizing the current suite toward the platonic ideal.

## Table of Contents
1. [Directory Layout and Categories](#directory-layout-and-categories)
2. [Unit Tests](#unit-tests)
   - [Mirroring and Placement](#mirroring-and-placement)
   - [Isolation](#isolation)
   - [Fixture and Helper Use](#fixture-and-helper-use)
   - [Mocking and Flakiness](#mocking-and-flakiness)
3. [Behavior, Integration & Docs](#behavior-integration-docs)
4. [Fixtures, Helpers, Data, and Mocking](#fixtures-helpers-data-and-mocking)
5. [Naming, Markers & Structure](#naming-markers--structure)
6. [Duplication and Redundancy Policies](#duplication-and-redundancy-policies)
7. [Flakiness, Determinism, and Reliability](#flakiness-determinism-and-reliability)
8. [Test Quality Checklist](#test-quality-checklist)
9. [Refactoring Plan](#refactoring-plan)
10. [FAQ and Anti-pattern Reference](#faq-and-anti-pattern-reference)

---

## Directory Layout and Categories

Every file and directory under `tests/` should fall into one of these categories:

- **unit/**: One-to-one mirrors of internal code structure, for isolated, fast, deterministic tests. Each file must **mirror the `openalex/` directory structure, except:**
    - leaf node: `openalex/foo/bar.py` → `tests/unit/test_foo/test_bar.py`
    - single module: `openalex/utils.py` → `tests/unit/test_utils.py`
    - All unit test module and class/function names must directly relate to the tested code.
- **behavior/**: Tests expected, likely or user-relevant behaviors, API contracts, or high-level outcomes (often spanning several units, sometimes using modest integration).
- **integration/**: Any test which hits external resources (network, DB, etc), or which validates system-level features end-to-end. These are allowed to be slow/flaky and should be run less often.
- **fixtures/**:
    - **fixtures/data/**: *Canonical location for all real response data*. All entity fixtures and tests must load from here. Changes/additions must be reviewed for upstream consistency.
    - **fixtures/api_responses.py**: Helper module for programmatic or dynamic mock responses, always using/building from above data.
    - Additional fixtures/helpers in `conftest.py` for reusable or session/data loading patterns only.
- **helpers/**: For generic test/mocking utilities, NOT for test logic itself.
- **docs/**: For doctest/example verification directly from documentation, not for feature/unit/behavior testing.

No test should be present outside the above structure without compelling rationale.

## Unit Tests
### Mirroring and Placement
- Each unit test file **must** only test code in the corresponding leaf/module of `openalex/`.
- Structure and naming must match: e.g. test classes `TestBar` in `test_bar.py` for `Bar` in `bar.py`.
- Top-level test class and method names must exactly describe the code/feature being validated.

### Isolation
- Unit tests **must not** depend on other test code (functions, classes, fixtures) except:
   - Shared data fixtures in `conftest.py` or explicitly documented helpers ("helpers").
   - Never call helpers from another test except through conftest-registered fixtures.
- **Never** couple test logic between files or modules.
- Test with **only** canonical fixtures; never bake complex logic into tests that would be better as a reusable fixture or factory.

### Fixture and Helper Use
- **Canonical data**: All "realistic" entity data comes from `fixtures/data/`. No unrelated ad-hoc dicts in tests.
- **Minimal fixture dependency**: Imported fixtures must be declared explicitly in the test function/class signature.
- **Helpers**: Use only as explicitly registered pytest fixtures or in the central `helpers` directory.

### Mocking and Flakiness
- Prefer using built-in fixtures, patching/mocking via `pytest` and `unittest.mock` with strict scoping (never global monkeypatch).
- When simulating remote resources, import only helpers/fixtures that are clearly named and self-contained.
- Tests that require mocking network/caches/async must either use canonical shared mocks or request a new helper in `helpers/`.
- Never mock the code under test itself or the behavior of the SUT, only its dependencies.

## Behavior, Integration & Docs
- **Behavior tests**: May span multiple units, but must clearly document intent and boundaries.
- **Integration**: Allowed to be slower and can use network/resources, but **must be marked**.
- **Docs**: Covber code snippets in documentation only, never test implementation logic or behaviors.

## Fixtures, Helpers, Data, and Mocking
- Only `fixtures/data/` contains authoritative static entity data for *all* types (authors, works, etc).
- Additional fixture files/modules must clearly indicate their purpose by naming (`api_responses.py` etc).
- `conftest.py` provides only "universal" fixtures—avoid technical debt by never letting it become a grab bag.
- Any repetitive mocking patterns must become shared helpers. If you find yourself copy-pasting, refactor.

## Naming, Markers & Structure

### Comprehensive Naming Convention

This section establishes the canonical naming standards for all test files, classes, and methods in the OpenAlex Python test suite.

#### File Naming Convention

**Test Files**
All test files **MUST** follow the pattern: `test_[subject].py`

**Examples:**
- `test_author.py` - Tests for Author model
- `test_work_validation.py` - Tests for Work validation logic
- `test_cache_performance.py` - Tests for cache performance
- `test_async_entities.py` - Tests for async entity operations

**Special Suffixes**
- `test_[subject]_extended.py` - Extended/edge case tests for a subject
- `test_[subject]_coverage.py` - Coverage-focused tests for edge cases
- `test_[subject]_validation.py` - Validation-specific tests

**Avoid:**
- ❌ `test_[subject]_extra.py` (use `_extended` instead)
- ❌ `test_[subject]_cover.py` (use `_coverage` instead)
- ❌ Non-descriptive names like `test_misc.py`

#### Class Naming Convention

**Primary Test Classes**
Test classes **MUST** follow the pattern: `Test[Subject][Type]`

**Examples:**
- `TestAuthorModel` - Tests for Author model
- `TestCacheBehavior` - Tests for cache behavior
- `TestAsyncBehavior` - Tests for async functionality
- `TestOpenAlexClient` - Tests for OpenAlex client

**Subject Naming Rules**
- Use PascalCase (CapitalizedWords)
- Be specific and descriptive
- Match the code being tested when possible

**Good Examples:**
- `TestWorkValidation` - Clear scope (Work validation)
- `TestPaginationBehavior` - Clear scope (pagination behavior)
- `TestMemoryCache` - Specific component (memory cache)

**Avoid:**
- ❌ `TestUtils` (too generic)
- ❌ `TestStuff` (non-descriptive)
- ❌ `TestMisc` (catch-all class)

#### Method Naming Convention

**Test Methods**
Test methods **MUST** follow the pattern: `test_[subject]_[behavior]_[context]`

**Structure:**
1. **subject** - What is being tested (snake_case)
2. **behavior** - What it should do (snake_case)  
3. **context** - Under what conditions (optional, snake_case)

**Examples:**
```python
# Basic patterns
def test_author_basic_fields_are_parsed_correctly(self):
def test_cache_prevents_duplicate_api_calls(self):
def test_pagination_respects_max_results_parameter(self):

# With context
def test_work_validation_raises_error_for_invalid_doi(self):
def test_client_retries_on_temporary_server_errors(self):
def test_async_pagination_handles_empty_results_gracefully(self):
```

**Behavioral Naming Guidelines**

Use descriptive action verbs that explain the expected behavior:

**Preferred Verbs:**
- `validates`, `raises_error`, `returns`, `creates`, `updates`, `deletes`
- `handles`, `processes`, `transforms`, `filters`, `sorts`
- `prevents`, `allows`, `blocks`, `enables`, `disables`
- `respects`, `follows`, `ignores`, `skips`

**Examples:**
```python
def test_filter_validates_entity_id_format(self):
def test_cache_handles_concurrent_access_safely(self):
def test_client_follows_cursor_pagination_correctly(self):
def test_retry_respects_rate_limit_headers(self):
```

**Context Specification**

Add context when testing edge cases or specific conditions:

```python
def test_author_parsing_with_missing_orcid(self):
def test_pagination_when_results_exceed_api_limit(self):
def test_cache_expiration_after_ttl_timeout(self):
def test_error_handling_during_network_failure(self):
```

#### Directory-Specific Conventions

**Unit Tests (`tests/unit/`)**
- Test single components in isolation
- Class names: `Test[Component]Model`, `Test[Component]Utils`
- Method focus: implementation details, edge cases, validation

```python
class TestAuthorModel:
    def test_author_basic_fields_are_parsed_correctly(self):
    def test_author_validation_raises_error_for_invalid_data(self):
    def test_author_orcid_normalization_handles_various_formats(self):
```

**Behavior Tests (`tests/behavior/`)**
- Test user-facing functionality and workflows
- Class names: `Test[Feature]Behavior`
- Method focus: end-to-end workflows, API contracts

```python
class TestPaginationBehavior:
    def test_pagination_iterates_through_all_results(self):
    def test_pagination_respects_max_results_parameter(self):
    def test_pagination_handles_empty_result_sets(self):
```

**Integration Tests (`tests/integration/`)**
- Test system-wide interactions
- Class names: `Test[System]Integration`
- Method focus: performance, external dependencies

```python
class TestCachePerformance:
    def test_cache_hit_performance_is_significantly_faster(self):
    def test_cache_size_limits_prevent_memory_exhaustion(self):
```

#### Docstring Convention

Every test class and method **MUST** have a docstring following this pattern:

**Class Docstrings**
```python
class TestAuthorModel:
    """Test that Author model correctly parses and validates entity data."""
```

**Method Docstrings**
```python
def test_author_basic_fields_are_parsed_correctly(self):
    """Test that basic author fields are parsed correctly from fixture data."""
```

**Template:** `"Test that [specific behavior being verified]."`

#### Anti-Patterns to Avoid

**File Names**
- ❌ `test_misc.py`, `test_utils.py` (too generic)
- ❌ `author_test.py` (wrong prefix)
- ❌ `test_author_stuff.py` (non-descriptive)

**Class Names**  
- ❌ `TestEverything` (too broad)
- ❌ `AuthorTests` (missing "Test" prefix)
- ❌ `TestAuthorStuff` (non-descriptive)

**Method Names**
- ❌ `test_author()` (too generic)
- ❌ `test_it_works()` (non-descriptive) 
- ❌ `test_author_test_1()` (numbered tests)
- ❌ `testAuthorFields()` (wrong case)

#### Examples by Category

**Model Tests**
```python
# File: tests/unit/models/test_author.py
@pytest.mark.unit
class TestAuthorModel:
    def test_author_basic_fields_are_parsed_correctly(self):
    def test_author_validation_raises_error_for_missing_id(self):
    def test_author_orcid_normalization_handles_various_formats(self):
```

**Behavior Tests**
```python
# File: tests/behavior/test_pagination.py  
@pytest.mark.behavior
class TestPaginationBehavior:
    def test_pagination_iterates_through_all_results(self):
    def test_pagination_respects_max_results_parameter(self):
    def test_pagination_handles_cursor_based_navigation(self):
```

**Integration Tests**
```python
# File: tests/integration/test_cache_performance.py
@pytest.mark.integration
class TestCachePerformance:
    def test_cache_hit_performance_meets_benchmarks(self):
    def test_cache_concurrent_access_maintains_consistency(self):
```

### Pytest Markers
- Use built-in pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.behavior`)
- New markers established:
  - `@pytest.mark.isolated`: Tests requiring isolation from global state
  - `@pytest.mark.modifies_global_state`: Tests that modify global state
  - `@pytest.mark.benchmark`: Performance benchmark tests
  - `@pytest.mark.requires_api`: Tests requiring network access
- Each new marker must be documented in pytest.ini and here
- **No magic imports**: Always import directly
- All tests must have docstrings describing their intent and coverage
- Each test must test a single logical behavior or code path

## Duplication and Redundancy Policies
- If any test or fixture duplicates existing code or logic, that is a technical debt smell.
- *Explicitly prohibited*: Duplicating entity dicts/fixtures, duplicating mocking/patch logic, duplicating test class logic across files.
- All entity data must derive from `fixtures/data/` or its canonical loaders.
- If two tests are nearly identical (other than names), refactor using parameterization, fixtures, or test utils.

## Flakiness, Determinism, and Reliability
- **Flakiness**: Any test that fails intermittently is immediately quarantined or marked. Causes must be tracked in the README or test docstring.
- **Determinism**: All unit and behavior tests must run the same way every time, regardless of order or environment, except where integration requires otherwise.
- **Do not** depend on wall clock time, system clock, random, or network except with explicit marker and rationale.
- Use dependency injection, helper mocks, and isolated objects.

## Test Quality Checklist
- [ ] All new test modules follow the mirroring policy.
- [ ] All new entity tests load from fixtures/data/ only.
- [ ] No fixture or helper code reinvents or duplicates another.
- [ ] All test files and classes are named for the code under test.
- [ ] No test code or logic is invoked by other test code except fixtures/helpers.
- [ ] Only the documented canonical fixtures/helpers are imported—no magic globals.
- [ ] Markers used are documented here or in the test module.
- [ ] Any apparent duplication or cross-file dependency is documented or refactored.

## Refactoring Plan (for maintainers)
1. **Fix fixture centralization**: Move all data loads to fixtures/data/ and have all helper patterns use only those.
2. **Purge duplicated test and mocking patterns**: Make patches and repeated setups helpers or fixtures.
3. **Restructure test dirs**: If "models", "behavior", "docs" or other folders become misaligned with code, refile tests.
4. **Normalize naming and docstrings**: Standardize all class, method, fixture, and file names.
5. **Audit and mark flaky/integration tests**: Apply markers and isolation, and update documentation for any exceptions.
6. **Ongoing review**: All new PRs are checked using the Test Quality Checklist above.

## FAQ and Anti-pattern Reference
- *Can I put entity dicts in my test?* No. Use `fixtures/data/`.
- *Can a test import or call another test?* No. Only fixtures/helpers are shared.
- *Can I parametrize across types/integration/unit in one file?* No. Separate per category and code file.
- *When should I add a fixture or helper?* At the second copy/paste or "almost identical" test logic.
- *What markers are in use?*
  - `@pytest.mark.unit`: For pure-internal/leaf / isolated tests.
  - `@pytest.mark.integration`: Network/resources.
  - `@pytest.mark.behavior`: Cross-unit observable behaviors/"feature" tests.
  - `@pytest.mark.isolated`: Tests requiring isolation from global state.
  - `@pytest.mark.modifies_global_state`: Tests that modify global state.
  - `@pytest.mark.benchmark`: Performance benchmark tests.
  - `@pytest.mark.requires_api`: Tests requiring network access.
  - Any new marker must be documented in this README, pytest.ini, and in the test module header.

---

This document is the sole reference for technical debt assessment and improvement of the OpenAlex Python test suite. Any violation must either be fixed, marked, or documented here.