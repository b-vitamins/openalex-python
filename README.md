# OpenAlex Python Client

A modern Python client for the [OpenAlex](https://openalex.org) API with full type annotations and a fluent interface.

## Features

- **Fluent, chainable interface** inspired by PyAlex
- **Fully typed** with comprehensive Pydantic models
- **Autocomplete support** in IDEs
- **Automatic retries** and rate limiting
- **Pagination** helpers for large result sets

## Installation

```bash
pip install openalex
```

## Quick Start

```python
from openalex import Works, Authors

# Get a single work
work = Works()["W2741809807"]
print(work.title)
print(work.abstract)  # Automatically converts inverted index

# Search for works
quantum_papers = (
    Works()
    .search("quantum computing")
    .filter(publication_year=2023, is_oa=True)
    .get()
)

for paper in quantum_papers.results:
    print(f"{paper.title} - {paper.cited_by_count} citations")

# Complex queries with logical operators
recent_papers = (
    Works()
    .filter_gt(cited_by_count=10)
    .filter_lt(publication_year=2024)
    .filter_not(type="retracted")
    .sort(cited_by_count="desc")
    .get()
)

# Get authors by ORCID
author = Authors()["https://orcid.org/0000-0002-1234-5678"]

# Pagination
for work in Works().filter(authorships={"author": {"id": author.id}}).paginate():
    process_work(work)
```

## Configuration

Set your email for the polite pool and get faster response times:

```python
from openalex import Works, OpenAlexConfig

config = OpenAlexConfig(email="your-email@example.com")
works = Works(config=config)
```

## Examples

### Search and Filter

```python
# Search with field-specific filters
results = (
    Works()
    .search_filter(title="climate change", abstract="temperature")
    .filter(publication_year=[2020, 2021, 2022])
    .get()
)

# OR operations
open_papers = Works().filter_or(
    is_oa=True,
    best_open_version="publishedVersion"
).get()

# Complex nested filters
ml_papers = Works().filter(
    topics={"id": "T10159"},  # Machine Learning
    authorships={
        "institutions": {
            "country_code": ["US", "UK", "CA"]
        }
    }
).get()
```

### Group and Aggregate

```python
# Group by open access status
grouped = Works().filter(publication_year=2023).group_by("oa_status").get()

for group in grouped.group_by:
    print(f"{group.key}: {group.count} papers")
```

### Select Specific Fields

```python
# Get only essential fields for performance
papers = (
    Works()
    .filter(journal="Nature")
    .select(["id", "title", "doi", "publication_date"])
    .get(per_page=200)
)
```

## Available Entities

- `Works()` - Scholarly works (papers, books, datasets)
- `Authors()` - Researchers and their publications
- `Institutions()` - Universities and research organizations
- `Sources()` - Journals, conferences, repositories
- `Topics()` - Research topics and fields
- `Publishers()` - Academic publishers
- `Funders()` - Research funding organizations
- `Keywords()` - Keywords from works
- `Concepts()` - Research concepts (deprecated)

## Error Handling

```python
from openalex import Works, NotFoundError

try:
    work = Works()["W99999999"]
except NotFoundError as e:
    print(f"Work not found: {e.message}")
```

## License

MIT
