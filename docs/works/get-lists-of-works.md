# Get lists of works

You can get lists of works using the Python client:

```python
from openalex import Works

# Create a query for all works (no filters applied)
all_works_query = Works()

# Execute the query to get the FIRST PAGE of results
first_page = all_works_query.get()

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
# Each result shows basic work information
for work in first_page.results:
    print(f"{work.display_name}")
    print(f"  Type: {work.type}")
    print(f"  Year: {work.publication_year}")
    print(f"  Citations: {work.cited_by_count}")
```

## Page and sort works

You can control pagination and sorting:

```python
# Get a specific page with custom page size (max 200 per page)
page2 = Works().get(per_page=50, page=2)
# This returns works 51-100 out of millions

# Sort results by different fields
recent_works = Works().sort(publication_year="desc").get()
# Returns 25 most recent works

highly_cited = Works().sort(cited_by_count="desc").get()
# Returns 25 most-cited works

# Combine sorting with pagination
top_cited_page2 = (
    Works()
    .sort(cited_by_count="desc")
    .get(per_page=100, page=2)
)
# Returns works 101-200 by citation count
```

## Sample works

Get a random sample instead of paginated results:

```python
# Get 20 random works from the entire database
random_sample = Works().sample(20).get()

# Use a seed for reproducible random sampling
reproducible_sample = Works().sample(20, seed=123).get()

# Sample from filtered results
recent_random = (
    Works()
    .filter(publication_year=2023)
    .sample(10)
    .get()
)
# Returns 10 random works from 2023
```

## Select fields

Limit the fields returned to improve performance:

```python
# Request only specific fields for each work
minimal_works = Works().select(["id", "display_name", "doi"]).get()

# This significantly reduces response size when you don't need all fields
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
