# Performance Optimization Guide

Tips for working efficiently with the OpenAlex client.

## Efficient Filtering

```python
# Always filter the Works entity - it has 250M+ records
from openalex import Works

filtered_works = (
    Works()
    .filter(publication_year=2023)
    .filter(topics={"id": "T10017"})
    .get(per_page=100)
)
print(f"Filtered to {filtered_works.meta.count} specific works")
```

## Batch Processing

```python
# Process large result sets efficiently
from openalex import Works

# Set up query
query = Works().filter(
    publication_year=2023,
    is_oa=True,
    type="article"
)

# Process in batches
processed = 0
for page in query.paginate(per_page=200):  # Max allowed
    for work in page.results:
        processed += 1

    print(f"Processed {processed} works so far...")

    if processed >= 1000:
        break

print(f"Completed processing {processed} works")
```

## Stream Results

```python
# Iterate over results one item at a time
from openalex import Works

query = Works().filter(publication_year=2023)

for work in query.stream(per_page=200, max_results=500):
    print(work.id)
```

## Select Fields

```python
# Reduce response size by selecting only needed fields
from openalex import Works

# Get only specific fields
minimal_works = (
    Works()
    .filter(publication_year=2023)
    .select(["id", "title", "doi", "cited_by_count"])
    .get(per_page=100)
)

# Much smaller response size
work = minimal_works.results[0]
print(f"Title: {work.title}")
print(f"DOI: {work.doi}")
# Note: Other fields will be None
```

## Async for Speed

```python
# Use async for concurrent requests
import asyncio
from openalex import AsyncWorks, AsyncAuthors

async def get_author_works(author_id):
    """Get recent works for an author"""
    works = await AsyncWorks().filter(
        authorships={"author": {"id": author_id}},
        publication_year=">2020"
    ).get(per_page=10)
    return works.results

async def analyze_collaboration():
    """Analyze recent works from multiple authors"""
    author_ids = ["A5023888391", "A5001721193", "A5082969844"]

    # Fetch concurrently
    tasks = [get_author_works(aid) for aid in author_ids]
    all_results = await asyncio.gather(*tasks)

    # Process results
    for author_id, works in zip(author_ids, all_results):
        print(f"Author {author_id}: {len(works)} recent works")

# Run async function
asyncio.run(analyze_collaboration())
```

## Caching Strategy

```python
# Example of simple caching for repeated queries
from openalex import Works
from datetime import datetime, timedelta

# Simple cache dictionary
cache = {}
cache_duration = timedelta(hours=1)

def get_cached_results(query_key, query_func):
    """Get results from cache or fetch if needed"""
    now = datetime.now()

    if query_key in cache:
        result, timestamp = cache[query_key]
        if now - timestamp < cache_duration:
            print("Using cached results")
            return result

    # Fetch fresh results
    print("Fetching fresh results")
    result = query_func()
    cache[query_key] = (result, now)
    return result

# Use the cache
query_key = "ml_papers_2023"
results = get_cached_results(
    query_key,
    lambda: Works().filter(
        publication_year=2023,
        topics={"id": "T10017"}
    ).get(per_page=100)
)

print(f"Got {len(results.results)} results")
```

## Rate Limiting

```python
# Handle rate limits gracefully
from openalex import Works, config
import time

# Configure retries
config.max_retries = 3
config.retry_backoff_factor = 1.0

# Process with rate awareness
def process_many_queries(queries):
    """Process multiple queries with rate limit awareness"""
    results = []

    for i, query in enumerate(queries):
        try:
            result = query.get(per_page=100)
            results.append(result)

            # Optional: Add small delay between requests
            if i < len(queries) - 1:
                time.sleep(0.1)  # 100ms delay

        except Exception as e:
            print(f"Error on query {i}: {e}")
            # Could implement exponential backoff here
            time.sleep(1)

    return results

# Example queries
queries = [
    Works().filter(publication_year=2023, topics={"id": topic_id})
    for topic_id in ["T10017", "T11679", "T12098"]
]

all_results = process_many_queries(queries)
print(f"Successfully processed {len(all_results)} queries")
```

## Resilience Patterns

The client can optionally enable a circuit breaker to prevent cascading
failures. When multiple consecutive requests fail, the circuit opens and
temporarily blocks additional calls until a cooldown period has passed.

```python
from openalex import Works, OpenAlexConfig

config = OpenAlexConfig(circuit_breaker_failure_threshold=3)
works = Works(config=config)

try:
    works.get("W999")
except Exception as exc:
    print(f"Request failed: {exc}")
```

