# Group publishers

You can group publishers to get aggregated statistics without fetching individual publisher records:

```python
from openalex import Publishers

# Create a query that groups publishers by country
country_stats_query = Publishers().group_by("country_codes")

# Execute the query to get COUNTS, not individual publishers
country_stats = country_stats_query.get()

# This returns aggregated statistics, NOT publisher objects!
print("Publishers by country:")
for group in country_stats.group_by[:10]:  # Top 10 countries
    # Each group has a 'key' (the country code) and 'count'
    print(f"  {group.key}: {group.count:,} publishers")
```

**Key point**: `group_by()` returns COUNTS, not the actual publishers. This is efficient for analytics.

## Understanding group_by results

```python
# The result structure is different from regular queries
result = Publishers().group_by("hierarchy_level").get()

print(result.results)  # Empty list - no individual publishers returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
print("Publishers by hierarchy level:")
for group in result.group_by:
    print(f"  Level {group.key}: {group.count:,} publishers")
```

## Common grouping operations

### Basic grouping

```python
# Group by hierarchy level
hierarchy_dist = Publishers().group_by("hierarchy_level").get()
# Shows how many parent vs. subsidiary publishers

# Group by country
by_country = Publishers().group_by("country_codes").get()
# See global distribution of publishers

# Group by lineage (to analyze publisher families)
by_lineage = Publishers().group_by("lineage").get()
# Note: This will have many groups (one per family tree path)
```

### Summary statistics grouping

```python
# Distribution of h-index values
h_index_dist = Publishers().group_by("summary_stats.h_index").get()
# See how research impact is distributed

# Distribution of i10-index
i10_dist = Publishers().group_by("summary_stats.i10_index").get()

# 2-year mean citedness distribution
impact_dist = Publishers().group_by("summary_stats.2yr_mean_citedness").get()
```

## Combining filters with group_by

Group_by becomes more insightful when combined with filters:

```python
# Country distribution for large publishers only
large_pub_countries = (
    Publishers()
    .filter_gt(works_count=100000)  # Large publishers only
    .group_by("country_codes")
    .get()
)
print("Countries with large publishers:")
for group in large_pub_countries.group_by:
    print(f"  {group.key}: {group.count} large publishers")

# Hierarchy levels for high-impact publishers
high_impact_hierarchy = (
    Publishers()
    .filter_gt(summary_stats={"h_index": 200})
    .group_by("hierarchy_level")
    .get()
)

# Parent publishers by continent
parent_by_continent = (
    Publishers()
    .filter(hierarchy_level=0)  # Parents only
    .group_by("continent")
    .get()
)
```

## Multi-dimensional grouping

While the API supports grouping by two dimensions, it's less common for publishers:

```python
# Publishers by country and hierarchy level
country_hierarchy = Publishers().group_by(
    "country_codes",
    "hierarchy_level"
).get()

# This shows which countries have more complex publisher structures
for group in country_hierarchy.group_by[:20]:
    country, level = group.key.split('|')  # Keys are pipe-separated
    print(f"{country} Level {level}: {group.count} publishers")
```

## Practical examples

### Example 1: Analyze publisher market concentration

```python
# Get top countries by publisher count
def analyze_market_concentration():
    # Total publishers by country
    by_country = Publishers().group_by("country_codes").get()
    
    # Large publishers by country  
    large_by_country = (
        Publishers()
        .filter_gt(works_count=100000)
        .group_by("country_codes")
        .get()
    )
    
    # Calculate concentration
    country_data = {}
    for group in by_country.group_by[:10]:
        country = group.key
        total = group.count
        
        # Find large publisher count for this country
        large_count = next(
            (g.count for g in large_by_country.group_by if g.key == country), 
            0
        )
        
        concentration = (large_count / total * 100) if total > 0 else 0
        country_data[country] = {
            'total': total,
            'large': large_count,
            'concentration': concentration
        }
    
    print("Market concentration by country:")
    for country, data in sorted(
        country_data.items(), 
        key=lambda x: x[1]['concentration'], 
        reverse=True
    ):
        print(f"  {country}: {data['large']} of {data['total']} "
              f"({data['concentration']:.1f}% concentration)")

analyze_market_concentration()
```

### Example 2: Publisher hierarchy analysis

```python
# Analyze publisher organizational structures
def analyze_hierarchies():
    # Overall hierarchy distribution
    hierarchy_dist = Publishers().group_by("hierarchy_level").get()
    
    print("Publisher hierarchy distribution:")
    total_publishers = sum(g.count for g in hierarchy_dist.group_by)
    for group in hierarchy_dist.group_by:
        pct = (group.count / total_publishers) * 100
        print(f"  Level {group.key}: {group.count:,} ({pct:.1f}%)")
    
    # Countries with complex hierarchies
    deep_hierarchies = (
        Publishers()
        .filter_gt(hierarchy_level=1)  # 2+ levels deep
        .group_by("country_codes")
        .get()
    )
    
    print("\nCountries with complex publisher hierarchies:")
    for group in deep_hierarchies.group_by[:10]:
        print(f"  {group.key}: {group.count} multi-level subsidiaries")

analyze_hierarchies()
```

### Example 3: Impact analysis

```python
# Analyze research impact distribution
def analyze_impact():
    # Group by h-index ranges
    h_ranges = [0, 50, 100, 200, 300, 500, 1000]
    
    print("Publishers by h-index range:")
    for i in range(len(h_ranges) - 1):
        range_pubs = (
            Publishers()
            .filter_gt(summary_stats={"h_index": h_ranges[i]})
            .filter_lt(summary_stats={"h_index": h_ranges[i+1]})
            .get()
        )
        print(f"  {h_ranges[i]}-{h_ranges[i+1]}: "
              f"{range_pubs.meta.count} publishers")
    
    # Top countries by high-impact publishers
    high_impact_countries = (
        Publishers()
        .filter_gt(summary_stats={"h_index": 200})
        .group_by("country_codes")
        .get()
    )
    
    print("\nCountries with high-impact publishers (h-index > 200):")
    for group in high_impact_countries.group_by[:10]:
        print(f"  {group.key}: {group.count} publishers")

analyze_impact()
```

## Sorting grouped results

Control how results are ordered:

```python
# Default: sorted by count (descending)
default_sort = Publishers().group_by("country_codes").get()
# US first (most publishers), then GB, DE, etc.

# Sort by key instead of count  
alphabetical = Publishers().group_by("country_codes").sort(key="asc").get()
# AF, AL, AM... (alphabetical by country code)

# Sort by count ascending (smallest groups first)
smallest_first = Publishers().group_by("hierarchy_level").sort(count="asc").get()
# Rarest hierarchy levels first
```

## Important notes

1. **No individual publishers returned**: `group_by()` only returns counts
2. **Efficient for analytics**: Much faster than fetching all publishers
3. **Limited dimensions**: Maximum 2 fields for grouping
4. **Can handle all publishers**: With only ~10,000 total, aggregations are fast
5. **Great for market analysis**: Understand publisher landscape without details

When you need statistics about publishers, always prefer `group_by()` over fetching and counting individual records!
