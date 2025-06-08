# OpenAlex Python Client

A Python client for the [OpenAlex API](https://docs.openalex.org/).

## Features

- **Async Support** - Both synchronous and asynchronous clients
- **Type Safety** - Type annotations with Pydantic v2 models
- **Performance** - Built on httpx and orjson
- **Automatic Retries** - Configurable retry logic with exponential backoff
- **Rate Limiting** - Respects API rate limits automatically
- **Pagination** - Iterate through large result sets
- **Error Handling** - Exception types for different errors
- **Zero Config** - Sensible defaults, optional configuration

## Installation

```bash
pip install openalex
```

Or with Poetry:

```bash
poetry add openalex
```

## Quick Start

```python
from openalex import OpenAlex

# Initialize the client
client = OpenAlex(email="your-email@example.com")  # Email for polite pool

# Get a specific work
work = client.works.get("W2741809807")
print(f"{work.title} - {work.cited_by_count} citations")

# Search for works
results = client.works.search("machine learning")
for work in results.results[:5]:
    print(f"{work.title} ({work.publication_year})")

# Filter works
recent_ml_papers = client.works.filter(
    search="deep learning",
    filter={
        "publication_year": [2022, 2023, 2024],
        "is_oa": True,
        "type": "article"
    }
).list()

# Pagination - iterate through all results
for work in client.works.paginate(filter={"is_oa": True}):
    if work.cited_by_count > 100:
        print(work.title)
```

## Async Support

```python
import asyncio
from openalex import AsyncOpenAlex

async def main():
    async with AsyncOpenAlex(email="your-email@example.com") as client:
        # Async operations
        work = await client.works.get("W2741809807")
        print(work.title)
        
        # Concurrent searches
        results = await client.search_all("quantum computing")
        print(f"Found {results['works'].meta.count} works")

asyncio.run(main())
```

## Advanced Usage

### Working with Filters

```python
# Create a filter object for reuse
ml_filter = client.works.filter()
    .with_publication_year([2020, 2021, 2022])
    .with_type("article") 
    .with_open_access(True)

# Use the filter
results = client.works.list(filter=ml_filter)

# Or use dict-based filtering
results = client.works.list(filter={
    "authorships.author.id": "A123456789",
    "concepts.id": "C41008148",  # Computer Science
    "cited_by_count": ">100"
})
```

### Pagination Options

```python
# Basic pagination
for work in client.works.paginate():
    print(work.title)
    
# Control page size and limit total results
for work in client.works.paginate(per_page=100, max_results=1000):
    process_work(work)

# Get all results as a list (be careful with large datasets!)
all_works = client.works.paginate(filter={"is_oa": True}).all()

# Iterate by pages instead of individual items
for page in client.works.paginate().pages():
    print(f"Processing {len(page.results)} works")
    for work in page.results:
        process_work(work)
```

### Entity Relationships

```python
# Get works by a specific author
author = client.authors.get("A123456789")
author_works = client.works.by_author(author.id).paginate()

# Get works from an institution
institution = client.institutions.get("I123456789")
inst_works = client.works.by_institution(institution.id).list()

# Get authors who cite a specific work
work = client.works.get("W2741809807")
citing_works = client.works.cited_by(work.id).paginate()
```

### Autocomplete

```python
# Autocomplete across all entity types
suggestions = client.autocomplete("einstein")
for result in suggestions.results:
    print(f"{result.display_name} ({result.entity_type})")

# Autocomplete for specific entity type
author_suggestions = client.authors.autocomplete("einstein")
```

### Custom Configuration

```python
from openalex import OpenAlex, OpenAlexConfig, RetryConfig

# Custom configuration
config = OpenAlexConfig(
    email="your-email@example.com",
    api_key="your-premium-key",  # For premium access
    retry_count=5,
    timeout=60.0,
    per_page=200,
)

# Custom retry logic
retry_config = RetryConfig(
    max_attempts=5,
    initial_wait=2.0,
    max_wait=120.0,
)

client = OpenAlex(
    config=config,
    retry_config=retry_config,
    rate_limit=50.0,  # Requests per second
)
```

## Available Resources

- **Works** - Scholarly works (papers, books, datasets, etc.)
- **Authors** - Researchers and their publication history
- **Institutions** - Universities, research institutes, companies
- **Sources** - Journals, conferences, repositories
- **Concepts** - Research topics and fields (deprecated but still available)
- **Topics** - New hierarchical topic classification
- **Publishers** - Academic publishers and their portfolios
- **Funders** - Research funding organizations
- **Keywords** - Keywords extracted from works

Each resource supports:
- `.get(id)` - Get a single entity
- `.list(filter)` - List entities with optional filtering
- `.search(query)` - Full-text search
- `.filter(**params)` - Build filter objects
- `.paginate()` - Iterate through all results
- `.random()` - Get a random entity
- `.autocomplete(query)` - Autocomplete suggestions

## Error Handling

```python
from openalex import OpenAlex, NotFoundError, RateLimitError

client = OpenAlex()

try:
    work = client.works.get("W99999999")
except NotFoundError as e:
    print(f"Work not found: {e.message}")
except RateLimitError as e:
    print(f"Rate limit hit. Retry after {e.retry_after} seconds")
```

## Performance Tips

1. **Use pagination** for large result sets instead of increasing `per_page`
2. **Enable caching** for frequently accessed data
3. **Use field selection** to reduce response size:
   ```python
   client.works.list(select=["id", "title", "cited_by_count"])
   ```
4. **Batch operations** with async client for concurrent requests
5. **Set appropriate timeouts** for your use case

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Thanks to the [OpenAlex team](https://openalex.org/) for providing this free scholarly data API.
