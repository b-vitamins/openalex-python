# Get lists of works

You can get lists of works using the Python client:

```python
from openalex import Works

# Create a filtered query for works from 2023
works_2023 = Works().filter(publication_year=2023)

# Execute the query to get the FIRST PAGE of results
first_page = works_2023.get()

# IMPORTANT: This does NOT return all 240+ million works!
# It returns only the first 25 works (one page)
print(f"Total works matching query: {first_page.meta.count:,}")  # ~245,684,392
print(f"Works in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
print(f"Results per page: {first_page.meta.per_page}")  # 25
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Work objects for the current page only
- **group_by**: Empty list (used only when grouping results)

## Understanding pagination

```python
from openalex import Works

first_page = Works().filter(publication_year=2023).get()
for work in first_page.results:
    print(f"{work.display_name}")
    print(f"  Type: {work.type}")
    print(f"  Year: {work.publication_year}")
    print(f"  Citations: {work.cited_by_count}")
```

## Page and sort works

You can control pagination and sorting:

```python
from openalex import Works

# Get a specific page with custom page size (max 200 per page)
page2 = Works().filter(publication_year=2023).get(per_page=50, page=2)
# This returns works 51-100 from 2023

# Sort results by publication year
recent_works = (
    Works()
    .filter(publication_year=2023)
    .sort(publication_year="desc")
    .get()
)

# Sort by citation count
highly_cited = (
    Works()
    .filter(publication_year=2023)
    .sort(cited_by_count="desc")
    .get()
)

# Combine sorting with pagination
top_cited_page2 = (
    Works()
    .filter(publication_year=2023)
    .sort(cited_by_count="desc")
    .get(per_page=100, page=2)
)
```

## Sample works

Get a random sample instead of paginated results:

```python
from openalex import Works

# Get 20 random works from 2023
random_sample = Works().filter(publication_year=2023).sample(20).get()

# Use a seed for reproducible sampling
reproducible_sample = (
    Works()
    .filter(publication_year=2023)
    .sample(20, seed=123)
    .get()
)

# Sample from filtered results
recent_random = (
    Works()
    .filter(publication_year=2023)
    .sample(10)
    .get()
)
```

## Select fields

Limit the fields returned to improve performance:

```python
from openalex import Works

# Request only specific fields for each work
minimal_works = (
    Works()
    .filter(publication_year=2023)
    .select(["id", "display_name", "doi"])
    .get()
)

for work in minimal_works.results:
    print(work.display_name)  # Available
    print(work.abstract)  # None - not selected
```

## Important notes on result limits

1. **Default page size**: 25 results
2. **Maximum page size**: 200 results  
3. **Maximum offset**: 10,000 (page \u00d7 per_page must be \u2264 10,000)
4. **For more results**: Use cursor pagination (see pagination docs)
5. **For analytics**: Use `group_by` instead of fetching all works

Continue on to learn how you can [filter](filter-works.md) and [search](search-works.md) lists of works.
