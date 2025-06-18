# Test Isolation Migration Guide

This guide explains how to migrate existing tests to use the isolation utilities
introduced to prevent cache and patch interference.

## When to Use Each Base Class

### `IsolatedTestCase`
Use for tests that depend on a clean global state. The base class resets cache
managers and other shared resources before and after each test.

### `CachePatchingTestCase`
Use for tests that need to patch cache-related functions. The provided context
managers ensure patches are cleaned up automatically.

## Migration Steps
1. Replace manual patches of `get_cache_manager` with `patch_cache_manager`.
2. Inherit from `IsolatedTestCase` or `CachePatchingTestCase` as needed.
3. Mark tests that modify global state with `@pytest.mark.modifies_global_state`.
4. Run the test suite to verify behaviour.

## Benefits
- Clear patterns for patching and isolation
- Automatic cleanup of global state
- No cross-test interference
