# Get lists of publishers

You can get lists of publishers using the Python client:

```python
from openalex import Publishers

# Create a query for all publishers (no filters applied)
all_publishers_query = Publishers()

# Execute the query to get the FIRST PAGE of results
first_page = all_publishers_query.get()

# Note: With ~10,000 total publishers, this is actually manageable
# unlike works (240M+) or authors (93M+)
print(f"Total publishers: {first_page.meta.count:,}")  # ~10,000
print(f"Publishers in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Publisher objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
# Each result shows publisher information
from openalex import Publishers

first_page = Publishers().get()
for publisher in first_page.results[:5]:
    print(f"\n{publisher.display_name}")
    print(f"  ID: {publisher.id}")
    print(f"  Works: {publisher.works_count:,}")
    print(f"  Citations: {publisher.cited_by_count:,}")
    print(f"  Hierarchy: Level {publisher.hierarchy_level}")
    if publisher.country_codes:
        print(f"  Countries: {', '.join(publisher.country_codes)}")
```

## Page and sort publishers

You can control pagination and sorting:

```python
# Get a specific page with custom page size
from openalex import Publishers

page2 = Publishers().get(per_page=50, page=2)
# This returns publishers 51-100

# Sort by different fields
# Largest publishers by work count
largest_publishers = Publishers().sort(works_count="desc").get()

# Most cited publishers
most_cited = Publishers().sort(cited_by_count="desc").get()

# Alphabetical by name
alphabetical = Publishers().sort(display_name="asc").get()

# Get many publishers without hitting the API too hard
some_publishers = []
for i, page in enumerate(Publishers().paginate(per_page=200)):
    if i >= 2:  # Stop after about 400 results
        break
    some_publishers.extend(page.results)
print(f"Fetched {len(some_publishers)} publishers")
```

## Sample publishers

Get a random sample of publishers:

```python
from openalex import Publishers

# Get 10 random publishers
random_sample = Publishers().sample(10).get()

# Use a seed for reproducible random sampling
reproducible_sample = Publishers().sample(10, seed=42).get()

# Sample from filtered results
top_level_sample = (
    Publishers()
    .filter(hierarchy_level=0)  # Only parent publishers
    .sample(5)
    .get()
)
```

## Select fields

Limit the fields returned to improve performance:

```python
# Request only specific fields
from openalex import Publishers

minimal_publishers = Publishers().select([
    "id",
    "display_name",
    "alternate_titles"
]).get()

# This reduces response size significantly
for publisher in minimal_publishers.results:
    print(publisher.display_name)  # Available
    print(publisher.works_count)  # None - not selected
```

## Practical example: Publisher hierarchy

```python
from openalex import Publishers

# Get all top-level publishers
parent_publishers = Publishers().filter(hierarchy_level=0).get()
print(f"Found {parent_publishers.meta.count} parent publishers")

# For each parent, you could get their children
for parent in parent_publishers.results[:5]:
    # Get publishers that have this one as parent
    children = Publishers().filter(parent_publisher=parent.id).get()
    print(f"\n{parent.display_name} has {children.meta.count} subsidiaries")
```

Continue on to learn how you can [filter](filter-publishers.md) and [search](search-publishers.md) lists of publishers.
