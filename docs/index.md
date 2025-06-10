# OpenAlex Python Client Documentation

A modern Python client for OpenAlex with a fluent, chainable interface and full type annotations.

## Quick Start

```python
from openalex import Works, Authors

# Get a work by ID
work = Works()["W2741809807"]

# Search and filter
papers = (
    Works()
    .search("climate change")
    .filter(publication_year=2023, is_oa=True)
    .get()
)

# Complex queries
results = (
    Works()
    .filter_gt(cited_by_count=10)
    .filter_not(type="retracted")
    .sort(publication_year="desc")
    .get()
)
```

## Available Entities

Each entity supports the same fluent interface:

- [Works](get-a-single-work.md) - Academic papers, books, datasets
- [Authors](get-a-single-author.md) - Researchers
- [Institutions](get-a-single-institution.md) - Universities and organizations
- [Sources](get-a-single-source.md) - Journals and repositories
- [Topics](get-a-single-topic.md) - Research topics
- [Publishers](get-a-single-publisher.md) - Academic publishers
- [Funders](get-a-single-funder.md) - Funding organizations
- [Concepts](concepts/get-a-single-concept.md) - Research concepts (deprecated)

## Common Operations

- **Get by ID**: `Works()["W123"]`
- **Filter**: `.filter(is_oa=True)`
- **Search**: `.search("quantum")`
- **Sort**: `.sort(cited_by_count="desc")`
- **Select fields**: `.select(["id", "title"])`
- **Paginate**: `.paginate()`
- **Group by**: `.group_by("oa_status")`

## Logical Operations

- **OR**: `.filter_or(type="article", type="preprint")`
- **NOT**: `.filter_not(is_retracted=True)`
- **Greater than**: `.filter_gt(cited_by_count=100)`
- **Less than**: `.filter_lt(publication_year=2020)`

## Configuration

```python
from openalex import Works, OpenAlexConfig

config = OpenAlexConfig(
    email="your-email@example.com",  # For polite pool
    api_key="your-api-key",  # For premium access
)

works = Works(config=config)
```
