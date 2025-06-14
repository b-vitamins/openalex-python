# Getting Started with OpenAlex Python Client

This guide walks you from installation to your first queries.

## Installation

```bash
pip install openalex
```

## Your First Query

```python
# Your first OpenAlex query
from openalex import Works

# Get any work by its DOI
work = Works().filter(doi="https://doi.org/10.1038/nature12373").get()
if work.results:
    paper = work.results[0]
    print(f"Found: {paper.title}")
    print(f"Authors: {len(paper.authorships)}")
```

## Understanding Results

```python
# Complete example showing result structure
from openalex import Authors

# Search for an author
results = Authors().search("Yann LeCun").get()

# Understanding the response
print(f"Total matches: {results.meta.count}")
print(f"Results in this page: {len(results.results)}")
print(f"Results per page: {results.meta.per_page}")

# Examining first result
if results.results:
    author = results.results[0]
    print(f"\nAuthor: {author.display_name}")
    print(f"Works: {author.works_count}")
    print(f"Institution: {author.last_known_institution.display_name if author.last_known_institution else 'Unknown'}")
```

## Configuration Setup

```python
# Setting up configuration (optional but recommended)
from openalex import config

# Set your email for the polite pool
config.email = "your-email@example.com"

# Verify configuration
from openalex import Works

test = Works().filter(publication_year=2024).get(per_page=1)
print(f"Success! API is working. Found {test.meta.count} works from 2024")
```

## Basic Filtering

```python
# Complete filtering example
from openalex import Works

# Filter works multiple ways
filtered_works = (
    Works()
    .filter(
        publication_year=2023,           # Published in 2023
        is_oa=True,                     # Open access only
        type="article"                   # Journal articles only
    )
    .search("artificial intelligence")   # Search in title/abstract
    .sort(cited_by_count="desc")        # Most cited first
    .get(per_page=5)                    # Get 5 results
)

print(f"Found {filtered_works.meta.count} AI papers from 2023")
for work in filtered_works.results:
    print(f"- {work.title[:80]}...")
    print(f"  Citations: {work.cited_by_count}")
```

