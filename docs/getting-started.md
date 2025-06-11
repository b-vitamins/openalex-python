# Getting Started with OpenAlex Python Client

This guide will help you get up and running with the OpenAlex Python client.

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/b-vitamins/openalex-python.git
cd openalex-python

# Install with Poetry
poetry install
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/b-vitamins/openalex-python.git
cd openalex-python

# Install dependencies
pip install -r requirements.txt
```

## Basic Concepts

### Entities

OpenAlex provides access to several entity types:

- **Works**: Scholarly papers, books, datasets, etc.
- **Authors**: Researchers and scholars
- **Institutions**: Universities, research organizations
- **Sources**: Journals, conferences, repositories
- **Topics**: Research topics and fields
- **Publishers**: Academic publishers
- **Funders**: Research funding organizations

### Query Building

The client uses a fluent interface for building queries:

```python
from openalex import Works

# Build a query step by step
results = (
    Works()
    .search("climate change")           # Search query
    .filter(publication_year=2024)      # Filter by year
    .filter(is_oa=True)                 # Only open access
    .sort("cited_by_count", "desc")     # Sort by citations
    .select("id", "title", "doi")       # Select specific fields
    .get(per_page=50)                   # Execute query
)
```

## Common Use Cases

### Finding Recent Papers on a Topic

```python
from openalex import Works

# Get recent AI papers
ai_papers = (
    Works()
    .search("artificial intelligence")
    .filter(publication_year="2023-2024")
    .sort("publication_date", "desc")
    .get()
)

for paper in ai_papers.results[:10]:
    print(f"{paper.publication_date}: {paper.title}")
```

### Analyzing Author Productivity

```python
from openalex import Authors

# Find prolific authors in your field
prolific_authors = (
    Authors()
    .search("machine learning")
    .filter(works_count=">100")
    .sort("cited_by_count", "desc")
    .get()
)

for author in prolific_authors.results[:5]:
    print(f"{author.display_name}: {author.works_count} works, {author.cited_by_count} citations")
```

### Institution Collaboration Analysis

```python
from openalex import Works

# Find collaborations between institutions
harvard_mit_collab = (
    Works()
    .filter(
        institutions={"id": "I136199984"},     # Harvard
        authorships={"institutions": {"id": "I63966007"}}  # MIT
    )
    .filter(publication_year="2020-2024")
    .get()
)

print(f"Harvard-MIT collaborations (2020-2024): {harvard_mit_collab.meta.count}")
```

### Tracking Open Access Trends

```python
from openalex import Works

# Analyze OA percentage by year
for year in range(2020, 2025):
    stats = (
        Works()
        .filter(publication_year=year)
        .group_by("is_oa")
        .get()
    )
    
    total = sum(g.count for g in stats.groups)
    oa_count = next((g.count for g in stats.groups if g.key == "true"), 0)
    
    print(f"{year}: {oa_count/total*100:.1f}% open access")
```

## Configuration Options

### Basic Configuration

```python
from openalex import OpenAlexConfig, Works

config = OpenAlexConfig(
    email="your@email.com",     # Polite pool access
    api_key="your-key",         # Higher rate limits
)

works = Works(config=config)
```

### Performance Configuration

```python
config = OpenAlexConfig(
    # Caching
    cache_enabled=True,
    cache_maxsize=5000,
    cache_ttl=3600,
    
    # Retries
    retry_count=3,
    retry_initial_wait=1.0,
    retry_max_wait=60.0,
    
    # Timeouts
    timeout=30.0,
)
```

## Next Steps

 - Check out the [Advanced Examples](../examples/advanced.py)
- Read the [API Reference](api-reference.md)
- Learn about [Performance Optimization](performance-guide.md)

## Getting Help

If you encounter issues:

1. Check the examples in the `examples/` directory
2. Review the API reference documentation
3. Open an issue on [GitHub](https://github.com/b-vitamins/openalex-python/issues)
