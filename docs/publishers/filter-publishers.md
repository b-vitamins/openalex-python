# Filter publishers

You can filter publishers using the Python client:

```python
from openalex import Publishers

# Create a filtered query for top-level publishers
parent_publishers_query = Publishers().filter(hierarchy_level=0)

# Execute the query to get the first page of results
results = parent_publishers_query.get()

print(f"Total parent publishers: {results.meta.count}")
print(f"Showing first {len(results.results)} publishers")

# Show some examples
for pub in results.results[:5]:
    print(f"- {pub.display_name}")
```

Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Publishers attribute filters

You can filter using these attributes of the [`Publisher`](publisher-object.md) object:

### Basic attribute filters

```python
from openalex import Publishers

# Filter by cited_by_count
highly_cited = Publishers().filter(cited_by_count=1000000).get()  # Exactly 1M
very_highly_cited = Publishers().filter_gt(cited_by_count=10000000).get()  # More than 10M

# Filter by works_count
large_publishers = Publishers().filter_gt(works_count=100000).get()  # More than 100k works
small_publishers = Publishers().filter_lt(works_count=1000).get()  # Fewer than 1k works

# Filter by hierarchy level
parent_publishers = Publishers().filter(hierarchy_level=0).get()  # Top level only
child_publishers = Publishers().filter(hierarchy_level=1).get()  # One level down
deep_subsidiaries = Publishers().filter_gt(hierarchy_level=1).get()  # Two+ levels down

# Filter by specific publisher ID
specific_ids = Publishers().filter(
    openalex=["P4310319965", "P4310320990"]
).get()
```

### Geographic filters

```python
from openalex import Publishers

# Filter by country
us_publishers = Publishers().filter(country_codes="US").get()
uk_publishers = Publishers().filter(country_codes="GB").get()

# Multiple countries (OR operation)
european_publishers = Publishers().filter(
    country_codes=["DE", "FR", "IT", "ES", "NL"]
).get()
```

### Hierarchy filters

```python
from openalex import Publishers

# Find all subsidiaries of a publisher using lineage
springer_nature_id = "P4310319965"
springer_family = Publishers().filter(lineage=springer_nature_id).get()
# This includes Springer Nature and all its children

# Find direct children only
direct_children = Publishers().filter(parent_publisher=springer_nature_id).get()

# Find publishers with a specific ROR
ror_publisher = Publishers().filter(ror="https://ror.org/02scfj030").get()

# Find publishers with a specific Wikidata ID
wikidata_publisher = Publishers().filter(wikidata="Q746413").get()
```

### Summary statistics filters

```python
from openalex import Publishers

# Filter by h-index
high_impact = Publishers().filter_gt(summary_stats={"h_index": 500}).get()

# Filter by i10-index
very_productive = Publishers().filter_gt(summary_stats={"i10_index": 10000}).get()

# Filter by 2-year mean citedness (impact factor equivalent)
high_quality = Publishers().filter_gt(
    summary_stats={"2yr_mean_citedness": 5.0}
).get()

# Combine metrics
elite_publishers = (
    Publishers()
    .filter_gt(summary_stats={"h_index": 300})
    .filter_gt(summary_stats={"i10_index": 50000})
    .filter_gt(works_count=100000)
    .get()
)
```

## Convenience filters

These filters aren't attributes of the Publisher object, but they're handy for common use cases:

### Geographic convenience filters

```python
from openalex import Publishers

# Filter by continent
european_publishers = Publishers().filter(continent="europe").get()
asian_publishers = Publishers().filter(continent="asia").get()
```

### Text search filters

```python
from openalex import Publishers

# Search in display names
elsevier_search = Publishers().filter(
    display_name={"search": "elsevier"}
).get()

# Alternative: use search_filter
springer_search = Publishers().search_filter(display_name="springer").get()

# Default search (same as using .search() method)
default_search = Publishers().filter(
    default={"search": "university press"}
).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
from openalex import Publishers

# Large US publishers
large_us_publishers = (
    Publishers()
    .filter(country_codes="US")
    .filter_gt(works_count=50000)
    .filter(hierarchy_level=0)  # Parent companies only
    .get()
)

# High-impact European publishers
european_elite = (
    Publishers()
    .filter(continent="europe")
    .filter_gt(summary_stats={"h_index": 200})
    .filter_gt(cited_by_count=1000000)
    .get()
)
```

### NOT operations

```python
from openalex import Publishers

# Publishers NOT from the US
non_us_publishers = Publishers().filter_not(country_codes="US").get()

# Non-parent publishers (subsidiaries only)
subsidiaries = Publishers().filter_not(hierarchy_level=0).get()
```

### Range queries

```python
from openalex import Publishers

# Mid-size publishers (10k-100k works)
mid_size = (
    Publishers()
    .filter_gt(works_count=10000)
    .filter_lt(works_count=100000)
    .get()
)

# Publishers with moderate citation impact
moderate_impact = (
    Publishers()
    .filter_gt(cited_by_count=100000)
    .filter_lt(cited_by_count=1000000)
    .get()
)
```

## Practical examples

### Example 1: Analyze publisher families

```python
from openalex import Publishers

# Get a major publisher
elsevier = Publishers().search("Elsevier BV").get().results[0]

# Find all entities in the Elsevier family
elsevier_family = Publishers().filter(lineage=elsevier.id).get()
print(f"Elsevier family has {elsevier_family.meta.count} entities")

# Show the hierarchy
for pub in elsevier_family.results:
    indent = "  " * pub.hierarchy_level
    print(f"{indent}{pub.display_name} (Level {pub.hierarchy_level})")
```

### Example 2: Compare publishers by region

```python
from openalex import Publishers

# Get top publishers by continent
def top_publishers_by_continent(continent, limit=5):
    return (
        Publishers()
        .filter(continent=continent)
        .sort(works_count="desc")
        .get(per_page=limit)
    )

# Compare different regions
for continent in ["north_america", "europe", "asia"]:
    top_pubs = top_publishers_by_continent(continent)
    print(f"\nTop {continent.title()} publishers:")
    for pub in top_pubs.results:
        print(f"  {pub.display_name}: {pub.works_count:,} works")
```

### Example 3: Find university presses

```python
from openalex import Publishers

# University presses often have "University Press" in the name
uni_presses = Publishers().search("University Press").get(per_page=50)

print(f"Found {uni_presses.meta.count} university presses")

# Analyze their characteristics
total_works = sum(p.works_count for p in uni_presses.results)
avg_works = total_works / len(uni_presses.results)
print(f"Average works per university press: {avg_works:,.0f}")

# Find the largest university presses
largest_uni_presses = (
    Publishers()
    .search("University Press")
    .sort(works_count="desc")
    .get(per_page=10)
)
```

## Performance tips

Since there are only ~10,000 publishers:

1. **Pagination is feasible**: You can actually fetch all publishers if needed
2. **Less need for select()**: Response sizes are manageable
3. **Group by is still useful**: For analytics without fetching details
4. **Hierarchy matters**: Use `lineage` to get entire publisher families efficiently

```python
# Example: Get summary of all publishers efficiently
from openalex import Publishers

def get_publisher_summary():
    # Use group_by for statistics
    by_country = Publishers().group_by("country_codes").get()
    by_level = Publishers().group_by("hierarchy_level").get()

    print("Publishers by country (top 10):")
    for group in by_country.group_by[:10]:
        print(f"  {group.key}: {group.count}")

    print("\nPublishers by hierarchy level:")
    for group in by_level.group_by:
        print(f"  Level {group.key}: {group.count}")
```
