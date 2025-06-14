# Get lists of authors

You can get lists of authors using the Python client:

```python
from openalex import Authors

# Create a query for all authors (no filters applied)
all_authors_query = Authors()

# Execute the query to get the FIRST PAGE of results
first_page = all_authors_query.get()

# IMPORTANT: This does NOT return all 93+ million authors!
# It returns only the first 25 authors (one page)
print(f"Total authors matching query: {first_page.meta.count:,}")  # ~93,011,659
print(f"Authors in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
print(f"Results per page: {first_page.meta.per_page}")  # 25
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Author objects for the current page only
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
# Each result shows author information
from openalex import Authors

# Fetch the first page again so this block is standalone
first_page = Authors().get()

# Each result shows author information
for author in first_page.results[:5]:  # First 5 authors
    print(f"\n{author.display_name}")
    print(f"  ID: {author.id}")
    print(f"  Works: {author.works_count}")
    print(f"  Citations: {author.cited_by_count}")
    if author.last_known_institutions:
        inst = author.last_known_institutions[0]
        print(f"  Institution: {inst.display_name}")
```

## Page and sort authors

You can control pagination and sorting:

```python
# Get a specific page with custom page size (max 200 per page)
from openalex import Authors

page2 = Authors().get(per_page=50, page=2)
# This returns authors 51-100 out of millions

# Sort by different fields
# Most cited authors
highly_cited = Authors().sort(cited_by_count="desc").get()

# Most prolific authors
prolific = Authors().sort(works_count="desc").get()

# Combine sorting with pagination
top_cited_page2 = (
    Authors()
    .sort(cited_by_count="desc")
    .get(per_page=100, page=2)
)
# Returns authors 101-200 by citation count
```

## Sample authors

Get a random sample instead of paginated results:

```python
# Get 25 random authors from the entire database
from openalex import Authors

random_sample = Authors().sample(25).get()

# Use a seed for reproducible random sampling
reproducible_sample = Authors().sample(25, seed=42).get()

# Sample from filtered results
orcid_sample = (
    Authors()
    .filter(has_orcid=True)  # Only authors with ORCID
    .sample(10)
    .get()
)
# Returns 10 random authors who have ORCID IDs
```

## Select fields

Limit the fields returned to improve performance:

```python
# Request only specific fields for each author
from openalex import Authors

minimal_authors = Authors().select(["id", "display_name", "orcid"]).get()

# This significantly reduces response size
for author in minimal_authors.results:
    print(author.display_name)  # Available
    print(author.works_count)  # None - not selected
```

## Important notes on result limits

1. **Default page size**: 25 results
2. **Maximum page size**: 200 results
3. **Maximum offset**: 10,000 (page × per_page must be ≤ 10,000)
4. **Total authors**: ~93 million (be careful with broad queries!)
5. **For analytics**: Use `group_by` instead of fetching all authors

Continue on to learn how you can [filter](filter-authors.md) and [search](search-authors.md) lists of authors.
