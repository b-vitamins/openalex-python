# API Reference

## Client Configuration

### OpenAlexConfig

Configuration object for the OpenAlex client.

```python
from openalex import OpenAlexConfig

config = OpenAlexConfig(
    email="your@email.com",           # For polite pool (optional)
    api_key="your-api-key",          # For higher rate limits (optional)
    base_url="https://api.openalex.org",  # API endpoint
    user_agent="MyApp/1.0",          # Custom user agent
    retry_count=3,                   # Number of retries
    retry_initial_wait=1.0,          # Initial retry wait (seconds)
    retry_max_wait=60.0,             # Max retry wait (seconds)
    retry_exponential_base=2.0,      # Exponential backoff base
    timeout=30.0,                    # Request timeout (seconds)
    cache_enabled=True,              # Enable caching
    cache_maxsize=1000,              # Max cache entries
    cache_ttl=3600,                  # Default cache TTL (seconds)
)
```

## Entity Classes

### Works

Access scholarly works (papers, books, datasets, etc.).

```python
from openalex import Works

works = Works()

# Get a specific work
work = works.get("W2741809807")

# Search works
results = works.search("climate change").get()

# Filter works
filtered = works.filter(
    publication_year=2024,
    is_oa=True,
    type="article"
).get()

# Complex queries
complex_results = (
    works
    .search("machine learning")
    .filter(
        publication_year="2020-2024",
        cited_by_count=">50",
        institutions={"country_code": "US"}
    )
    .sort("cited_by_count", "desc")
    .select("id", "title", "cited_by_count")
    .get(per_page=50)
)
```

#### Work Methods

- `get(id)` - Get a single work by ID
- `search(query)` - Full-text search
- `filter(**kwargs)` - Filter results
- `sort(field, order)` - Sort results
- `select(*fields)` - Select specific fields
- `group_by(field)` - Group results
- `all()` - Iterate through all results
- `count()` - Get count of results
- `random()` - Get a random work
- `autocomplete(query)` - Autocomplete search
- `ngrams(work_id)` - Get work n-grams

### Authors

Access information about scholarly authors.

```python
from openalex import Authors

authors = Authors()

# Get specific author
author = authors.get("A2208157607")

# Search authors
results = authors.search("einstein").get()

# Filter by metrics
prolific_authors = authors.filter(
    works_count=">100",
    cited_by_count=">5000"
).get()
```

#### Author Methods

Similar to Works, plus:
- Filters: `works_count`, `cited_by_count`, `h_index`, `i10_index`
- Grouping: Can group by institution, country

### Institutions

Access information about research institutions.

```python
from openalex import Institutions

institutions = Institutions()

# Get specific institution
mit = institutions.get("I63966007")

# Search institutions
results = institutions.search("Harvard").get()

# Filter by type and country
universities = institutions.filter(
    type="education",
    country_code="US"
).get()
```

### Sources

Access information about publication sources (journals, conferences, etc.).

```python
from openalex import Sources

sources = Sources()

# Get specific source
nature = sources.get("S137773608")

# Filter by type
journals = sources.filter(
    type="journal",
    is_in_doaj=True
).get()
```

### Topics

Access research topics and fields.

```python
from openalex import Topics

topics = Topics()

# Get specific topic
ml_topic = topics.get("T10119")

# Search topics
ai_topics = topics.search("artificial intelligence").get()
```

### Publishers

Access publisher information.

```python
from openalex import Publishers

publishers = Publishers()

# Get specific publisher
elsevier = publishers.get("P4310311648")

# List major publishers
major_publishers = publishers.filter(
    works_count=">10000"
).sort("works_count", "desc").get()
```

### Funders

Access research funder information.

```python
from openalex import Funders

funders = Funders()

# Search funders
nsf = funders.search("National Science Foundation").get()
```

## Query Building

### Filtering

```python
# Basic filters
.filter(publication_year=2024)
.filter(is_oa=True)

# Comparison operators
.filter(cited_by_count=">100")      # Greater than
.filter(publication_year="<2020")   # Less than
.filter(works_count="100-500")      # Range

# Multiple values (OR)
.filter(type=["article", "book"])

# Negation
.filter(is_oa="!true")              # NOT open access

# Complex filters with OR and AND
.filter(
    institutions={"id": ["I123", "I456"]},
    publication_year=">2020,<2024",
)
```

### Search

```python
# Default search (searches multiple fields)
.search("quantum computing")

# Field-specific search
.search_filter(
    title="neural networks",
    abstract="deep learning"
)
```

### Sorting

```python
.sort("cited_by_count", "desc")    # Descending
.sort("publication_date", "asc")   # Ascending
```

### Pagination

```python
# Manual pagination
page1 = works.filter(year=2024).get(page=1, per_page=50)
page2 = works.filter(year=2024).get(page=2, per_page=50)

# Auto pagination
for work in works.filter(year=2024).all():
    process(work)  # Automatically fetches all pages
```

### Field Selection

```python
# Select specific fields
.select("id", "title", "cited_by_count", "doi")

# Nested fields
.select("id", "title", "authorships.author.display_name")
```

### Grouping

```python
# Group by single field
by_year = works.group_by("publication_year").get()

# Access groups
for group in by_year.groups:
    print(f"{group.key}: {group.count} works")
```

## Async API

All entity classes have async equivalents:

```python
from openalex import AsyncWorks, AsyncAuthors
import asyncio

async def main():
    works = AsyncWorks()
    
    # Same API, but async
    work = await works.get("W2741809807")
    results = await works.search("AI").get()
    
    # Parallel requests
    results = await asyncio.gather(
        works.search("quantum").get(),
        works.search("climate").get(),
    )

asyncio.run(main())
```

## Error Handling

```python
from openalex import (
    Works,
    NotFoundError,
    RateLimitError,
    ValidationError,
    APIError
)

try:
    work = Works().get("invalid-id")
except NotFoundError:
    print("Work not found")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Invalid query: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Type Hints

All methods are fully typed:

```python
from openalex import Works, Work, ListResult

# Type hints for better IDE support
def analyze_works(query: str) -> list[Work]:
    results: ListResult[Work] = Works().search(query).get()
    return results.results

# Async with types
async def get_work_async(work_id: str) -> Work:
    works = AsyncWorks()
    work: Work = await works.get(work_id)
    return work
```
