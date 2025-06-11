# Performance Optimization Guide

This guide covers best practices for optimizing performance when using the OpenAlex Python client.

## Table of Contents
- [Field Selection](#field-selection)
- [Caching Strategy](#caching-strategy)
- [Async Operations](#async-operations)
- [Batch Processing](#batch-processing)
- [Connection Management](#connection-management)
- [Memory Management](#memory-management)

## Field Selection

Reduce payload size by selecting only the fields you need:

```python
# Bad: fetches all fields (can be 10KB+ per work)
works = Works().filter(publication_year=2024).get()

# Good: fetches only specific fields (reduced to ~500 bytes per work)
works = (
    Works()
    .filter(publication_year=2024)
    .select("id", "title", "cited_by_count", "doi")
    .get()
)

# Typical size reductions:
# - Full work: ~10-50KB
# - Minimal fields: ~0.5-2KB
# - 95% reduction in data transfer!
```

### Common Field Selection Patterns

```python
# For bibliometric analysis
.select("id", "cited_by_count", "publication_year", "is_oa")

# For displaying results
.select("id", "title", "display_name", "authorships", "publication_date")

# For link building
.select("id", "doi", "ids", "primary_location")
```

## Caching Strategy

### Configuration

```python
config = OpenAlexConfig(
    cache_enabled=True,
    cache_maxsize=5000,      # Number of entries
    cache_ttl=3600,          # Default TTL in seconds
)
```

### Cache-Friendly Patterns

```python
# Good: reusable queries
def get_institution_works(inst_id: str, year: int):
    return Works().filter(
        institutions={"id": inst_id},
        publication_year=year
    ).get()

# Bad: unique queries that will not benefit from cache
def get_works_with_random_param():
    return Works().filter(
        random_param=uuid.uuid4()  # Different every time!
    ).get()
```

### Custom TTL by Entity Type

Different entities change at different rates:

```python
# Sources, Topics, Institutions - change rarely (24h TTL)
sources = Sources(config=OpenAlexConfig(cache_ttl=86400))

# Works - change frequently (1h TTL)
works = Works(config=OpenAlexConfig(cache_ttl=3600))

# Authors - moderate change rate (4h TTL)
authors = Authors(config=OpenAlexConfig(cache_ttl=14400))
```

## Async Operations

### Parallel Requests

```python
import asyncio
from openalex import AsyncWorks, AsyncAuthors

async def parallel_analysis():
    works = AsyncWorks()
    authors = AsyncAuthors()
    
    # Sequential (slow)
    ml_works = await works.search("machine learning").get()
    dl_works = await works.search("deep learning").get()
    ai_works = await works.search("artificial intelligence").get()
    # Total time: 3x API latency
    
    # Parallel (fast)
    results = await asyncio.gather(
        works.search("machine learning").get(),
        works.search("deep learning").get(),
        works.search("artificial intelligence").get(),
    )
    # Total time: 1x API latency
```

### Async Streaming

```python
async def process_large_dataset():
    works = AsyncWorks()
    
    # Process items as they arrive
    async for work in works.filter(publication_year=2024).all():
        await process_work(work)  # Process immediately
        # Memory efficient - only one page in memory at a time
```

## Batch Processing

### Combining Filters

```python
# Multiple API calls
harvard_works = Works().filter(institutions={"id": "I136199984"}).get()
mit_works = Works().filter(institutions={"id": "I63966007"}).get()
stanford_works = Works().filter(institutions={"id": "I97018004"}).get()

# Single API call with OR
combined = Works().filter(
    institutions={"id": ["I136199984", "I63966007", "I97018004"]}
).get()
```

### Efficient Pagination

```python
# For large datasets, use cursor pagination
def process_all_2024_works():
    works = Works()
    
    # Process in chunks
    for work in works.filter(publication_year=2024).all():
        process(work)
        
        # This automatically handles pagination
        # Fetches next page only when needed
```

## Connection Management

### Connection Pooling

```python
# Reuse connections across requests
config = OpenAlexConfig(
    email="your@email.com",
    # Connection pooling is automatic
)

# Reuses connection
works = Works(config=config)
for i in range(100):
    work = works.get(f"W{i}")  # Reuses same connection

# Creates new connection each time
for i in range(100):
    works = Works()  # New connection!
    work = works.get(f"W{i}")
```

### Async Connection Management

```python
from openalex import AsyncWorks, close_all_async_connections

async def main():
    works = AsyncWorks()
    
    # Use connection
    results = await works.search("test").get()
    
    # Clean up when done
    await close_all_async_connections()
```

## Memory Management

### Streaming Large Datasets

```python
# Loads everything into memory
all_works = list(Works().filter(publication_year=2024).all())
# Can use GBs of memory!

# Process one at a time
for work in Works().filter(publication_year=2024).all():
    process(work)
    # Only one page (~25 items) in memory
```

### Selective Field Loading

```python
# Full objects with all fields
works = Works().filter(cited_by_count=">1000").get()
# Each work can be 50KB+

# Minimal fields
works = (
    Works()
    .filter(cited_by_count=">1000")
    .select("id", "title", "cited_by_count")
    .get()
)
# Each work is <1KB
```

## Performance Benchmarks

| Operation | Without Optimization | With Optimization | Improvement |
|-----------|---------------------|-------------------|-------------|
| Fetch 1000 works | 40s | 8s (parallel) | 5x faster |
| Second identical query | 200ms | 1ms (cached) | 200x faster |
| Memory for 10k works | 500MB | 50MB (selected fields) | 10x less |
| API calls for batch | 10 calls | 1 call (OR query) | 10x fewer |

## Monitoring Performance

```python
import time
from openalex import Works, OpenAlexConfig

# Enable cache stats
config = OpenAlexConfig(cache_enabled=True)
works = Works(config=config)

# Measure performance
start = time.time()
results = works.search("quantum").get()
duration = time.time() - start

print(f"Query took: {duration:.3f}s")

# Check cache performance
stats = works.cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1%}")
print(f"Cache size: {stats['size']}/{stats['maxsize']}")
```

## Best Practices Summary

1. **Always select only needed fields** - biggest performance win
2. **Enable caching** for repeated queries
3. **Use async for parallel operations**
4. **Batch similar queries** with OR conditions
5. **Stream large datasets** instead of loading all
6. **Reuse client instances** for connection pooling
7. **Monitor cache stats** to optimize TTL
8. **Set appropriate timeouts** for your use case

Following these practices can improve performance by 10-100x depending on your use case!
