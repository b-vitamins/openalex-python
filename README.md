<div align="center">
  <img src="assets/openalex-logo.png" alt="OpenAlex Logo" width="400">
  <br>
  <sub>Logo adapted from <a href="https://commons.wikimedia.org/wiki/File:OpenAlex-logo-5.2de7053c.png">OurResearch</a>, CC0, via Wikimedia Commons</sub>
  
  # Python Client for the OpenAlex API

  [![Python](https://github.com/b-vitamins/openalex-python/actions/workflows/python.yml/badge.svg)](https://github.com/b-vitamins/openalex-python/actions/workflows/python.yml)
  [![codecov](https://codecov.io/gh/b-vitamins/openalex-python/graph/badge.svg?branch=master)](https://codecov.io/gh/b-vitamins/openalex-python)
</div>

> **Disclaimer**: This is an **unofficial** client library for OpenAlex. It is not endorsed by or affiliated with OpenAlex or its parent organization. The library's author is not associated with OpenAlex.

> **Note**: This project is inspired by and builds upon the excellent work of [PyAlex](https://github.com/J535D165/pyalex).

A Python client for the [OpenAlex](https://openalex.org) API with:

- **Async support** with HTTP/2
- **Automatic retries** with exponential backoff
- **Type hints** and Pydantic models
- **Fluent query API**
- **Built-in caching**
- **Connection pooling** and concurrent requests
- **Comprehensive error handling**
- **Documentation and examples**

For the official OpenAlex API documentation, please visit [docs.openalex.org](https://docs.openalex.org/).

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/b-vitamins/openalex-python.git
cd openalex-python

# Install with Poetry
poetry install

# Or install dependencies directly
pip install -r requirements.txt
```

### Basic Usage

```python
from openalex import Works, Authors

# Get a specific work
work = Works().get("W2741809807")
print(f"{work.title} has been cited {work.cited_by_count} times")

# Search for works
climate_papers = (
    Works()
    .search("climate change")
    .filter(publication_year=2024, is_oa=True)
    .sort("cited_by_count", "desc")
    .get(per_page=10)
)

for paper in climate_papers.results:
    print(f"{paper.title} - {paper.cited_by_count} citations")

# Find highly-cited authors in machine learning
ml_authors = (
    Authors()
    .search("machine learning")
    .filter(works_count=">50", cited_by_count=">1000")
    .get()
)
```

### Async Usage

```python
import asyncio
from openalex import AsyncWorks

async def get_trending_papers():
    works = AsyncWorks()
    
    # Fetch multiple queries in parallel
    results = await asyncio.gather(
        works.search("quantum computing").get(),
        works.search("artificial intelligence").get(),
        works.search("climate change").get(),
    )
    
    for topic_results in results:
        print(f"Found {topic_results.meta.count} papers")

# Run async function
asyncio.run(get_trending_papers())
```

## Documentation

- [API Reference](docs/api-reference.md)
- Examples: [basic.py](examples/basic.py), [advanced.py](examples/advanced.py), [async.py](examples/async.py)
- [Performance Guide](docs/performance-guide.md)

## Configuration

```python
from openalex import OpenAlexConfig, Works

# Configure the client
config = OpenAlexConfig(
    email="your-email@example.com",  # Optional: for polite pool
    api_key="your-api-key",          # Optional: for higher rate limits
    retry_count=3,                   # Automatic retries
    cache_enabled=True,              # Enable caching
    cache_ttl=3600,                 # Cache for 1 hour
)

works = Works(config=config)
```

## Features

### Field Selection
```python
# Only fetch specific fields for performance
minimal_works = (
    Works()
    .filter(publication_year=2024)
    .select("id", "title", "cited_by_count")
    .get()
)
```

### Grouping and Aggregation
```python
# Group works by open access status
oa_stats = (
    Works()
    .filter(publication_year=2024)
    .group_by("is_oa")
    .get()
)

for group in oa_stats.groups:
    print(f"OA={group.key}: {group.count} works")
```

### Auto-Pagination
```python
# Automatically fetch all pages
for work in Works().filter(publication_year=2024).all():
    process_work(work)  # Processes items as they're fetched
```

### Complex Queries
```python
from openalex import Authors, Institutions

# Find authors at specific institutions with complex filters
authors = (
    Authors()
    .filter(
        affiliations=["Harvard University", "MIT"],
        works_count=">100",
        cited_by_count=">5000",
    )
    .sort("cited_by_count", "desc")
    .get()
)
```

## Performance Tips

1. **Use field selection** to reduce response size
2. **Enable caching** for frequently accessed data
3. **Use async for parallel requests**
4. **Batch operations** when possible
5. **Set appropriate timeouts** for your use case

## Contributing

Please see the [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the amazing [OpenAlex](https://openalex.org) API - see their [documentation](https://docs.openalex.org/) for API details
- Inspired by [PyAlex](https://github.com/J535D165/pyalex) - the original Python client for OpenAlex
