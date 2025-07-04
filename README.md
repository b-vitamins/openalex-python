<div align="center">
  <img src="assets/openalex-logo.png" alt="OpenAlex Logo" width="400">
  <br>
  <sub>Logo adapted from <a href="https://commons.wikimedia.org/wiki/File:OpenAlex-logo-5.2de7053c.png">OurResearch</a>, CC0, via Wikimedia Commons</sub>
  
  # Python Client for the OpenAlex API

  [![Python](https://github.com/b-vitamins/openalex-python/actions/workflows/python.yml/badge.svg)](https://github.com/b-vitamins/openalex-python/actions/workflows/python.yml)
  [![codecov](https://codecov.io/gh/b-vitamins/openalex-python/graph/badge.svg?token=XB5KI75WU1)](https://codecov.io/gh/b-vitamins/openalex-python)
</div>

> **Disclaimer**: This is an **unofficial** client library for OpenAlex. It is not endorsed by or affiliated with OpenAlex or its parent organization. The library's author is not associated with OpenAlex.

> **Note**: This project is inspired by and builds upon [PyAlex](https://github.com/J535D165/pyalex).

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
work = Works()["W2741809807"]
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

### Entity Navigation

```python
# Navigate from work to authors to institutions
work = Works()["W2741809807"]

# Get the first author
first_author = Authors()[work.authorships[0].author.id]
print(f"First author: {first_author.display_name}")

# Get their primary institution
if first_author.affiliations:
    from openalex import Institutions
    institution = Institutions()[first_author.affiliations[0].institution.id]
    print(f"Institution: {institution.display_name}")
    print(f"Type: {institution.type}")
```

### Complex Filtering

```python
# Combine multiple filters
from openalex import Works

# Papers NOT about COVID but mentioning pandemic
non_covid_pandemic = (
    Works()
    .search("pandemic")
    .filter_not(title_and_abstract="covid")
    .filter(publication_year=">2020")
    .get()
)

# Works from US or UK institutions published in 2023
anglo_american = (
    Works()
    .filter(
        authorships={"institutions": {"country_code": ["US", "GB"]}},
        publication_year=2023
    )
    .get()
)

# High-impact open access papers
high_impact_oa = (
    Works()
    .filter(cited_by_count=">100", is_oa=True)
    .filter(publication_year=[2020, 2021, 2022, 2023])
    .get()
)
```

### Field Selection and Grouping

```python
# Only fetch needed fields for better performance
minimal_works = (
    Works()
    .filter(publication_year=2024)
    .select(["id", "title", "cited_by_count", "doi"])
    .get(per_page=100)
)

# Group results instead of fetching individual records
yearly_output = (
    Works()
    .filter(authorships={"institutions": {"id": "I114027177"}})
    .group_by("publication_year")
    .get()
)

for group in yearly_output.groups:
    print(f"{group.key}: {group.count} papers")

# Get OA status breakdown for an institution
oa_breakdown = (
    Works()
    .filter(
        authorships={"institutions": {"id": "I114027177"}},
        publication_year=2023
    )
    .group_by("open_access.oa_status")
    .get()
)
```

### Pagination

```python
# Iterate through results without loading all into memory
for work in Works().filter(publication_year=2024).paginate(per_page=200):
    process_work(work)  # Process one at a time
    
# Manual pagination with cursor
page1 = Works().filter(publication_year=2024).get(per_page=100)
if page1.meta.next_cursor:
    page2 = Works().filter(publication_year=2024).get(
        cursor=page1.meta.next_cursor
    )

# Get all results (use with caution on large result sets)
all_2024_cs_papers = (
    Works()
    .filter(
        publication_year=2024,
        primary_topic={"subfield": {"id": "S2207399551"}}  # Computer Science
    )
    .all()
)
print(f"Found {len(all_2024_cs_papers)} CS papers from 2024")
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

### Configuration

```python
from openalex import OpenAlexConfig, Works

# Configure the client
config = OpenAlexConfig(
    email="your-email@example.com",  # Polite pool access (faster)
    api_key="your-api-key",          # Optional: higher rate limits
    retry_count=3,                   # Automatic retries on failure
    cache_enabled=True,              # Cache responses
    cache_ttl=3600,                 # Cache for 1 hour
    timeout=30,                      # Request timeout in seconds
)

works = Works(config=config)
```

## Documentation

- **[Getting Started Guide](docs/getting-started.md)** - Step-by-step introduction
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Performance Guide](docs/performance-guide.md)** - Optimization tips

### Entity-Specific Guides

- [Works](docs/works/) - Papers, books, datasets
- [Authors](docs/authors/) - Researcher profiles
- [Institutions](docs/institutions/) - Universities and organizations
- [Sources](docs/sources/) - Journals and repositories
- [Topics](docs/topics/) - Research topics (replaces Concepts)
- [Publishers](docs/publishers/) - Publishing organizations
- [Funders](docs/funders/) - Funding organizations
- [Concepts](docs/concepts/) - Legacy concept tags (deprecated)

### Examples

- **[basic.py](examples/basic.py)** - Simple usage patterns
- **[advanced.py](examples/advanced.py)** - Complex queries and performance
- **[async.py](examples/async.py)** - Asynchronous operations

## Features

A Python client for the [OpenAlex](https://openalex.org) API with the following capabilities:

### Core Functionality
- [x] **Type-safe data models** - Pydantic models for all OpenAlex entities
- [x] **Fluent query interface** - Method chaining (`.filter().sort().select()`)
- [x] **Comprehensive filtering** - Including comparison operators and boolean logic
- [x] **Field selection** - Fetch only needed fields for better performance
- [x] **Search functionality** - Full-text search across entities
- [x] **Sorting** - Multi-field sorting with configurable order
- [x] **Group-by queries** - Aggregate statistics without fetching individual records

### Async Support
- [x] **Full async/await API** - Complete mirror of synchronous interface
- [x] **Concurrent fetching** - `get_many()` for efficient multi-entity retrieval
- [x] **Async pagination** - All pagination strategies available in async
- [x] **Semaphore concurrency control** - Prevent overwhelming the API

### Pagination
- [x] **Cursor-based pagination** - Efficient for large datasets
- [x] **Page-based pagination** - Traditional pagination with page numbers
- [x] **Streaming paginator** - Memory-efficient iteration
- [x] **Auto-pagination** - Simple `.paginate()` method

### Reliability & Performance
- [x] **Automatic retries** - Exponential backoff for transient failures
- [x] **Rate limiting** - Configurable request throttling
- [x] **Circuit breaker** - Fail fast when API is down
- [x] **Connection pooling** - Reuse HTTP connections
- [x] **In-memory caching** - Reduce duplicate API calls (off by default)
- [ ] **Redis cache backend** - For persistent, distributed caching
- [ ] **Request/response middleware** - For custom authentication, logging, etc.
- [ ] **Adaptive rate limiting** - Automatically adjust to API response headers

### Developer Experience
- [x] **Full type hints** - IDE autocomplete and type checking
- [x] **Structured exceptions** - Different error types for different failures
- [x] **Environment variable config** - Easy configuration management
- [x] **Comprehensive documentation** - Examples and API reference
- [ ] **Async context managers** - Better resource lifecycle management
- [ ] **Request retry budgets** - Limit total retry time across requests

### Data Handling
- [x] **Automatic validation** - Pydantic validates all API responses
- [x] **Flexible result formats** - Individual entities, lists, or generators
- [x] **Group-by aggregations** - Statistical summaries
- [ ] **Streaming JSON parsing** - For extremely large single responses
- [ ] **Bulk operations** - Send multiple updates in one request (when API supports it)

For the official OpenAlex API documentation, visit [docs.openalex.org](https://docs.openalex.org/).

## Contributing

Please see the [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the [OpenAlex](https://openalex.org) API
- Inspired by [PyAlex](https://github.com/J535D165/pyalex)
