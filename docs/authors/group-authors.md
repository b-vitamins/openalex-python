# Group authors

You can group authors to get aggregated statistics without fetching individual author records:

```python
from openalex import Authors

# Create a query that groups authors by their last known institution's continent
continent_stats_query = Authors().group_by(
    "last_known_institutions.continent"
)

# Execute the query to get COUNTS, not individual authors
continent_stats = continent_stats_query.get()

# This returns aggregated statistics, NOT author objects!
print("Authors by continent:")
for group in continent_stats.group_by:
    # Each group has a 'key' (the continent) and 'count'
    print(f"  {group.key}: {group.count:,} authors")
    percentage = (group.count / continent_stats.meta.count) * 100
    print(f"    ({percentage:.1f}% of all authors)")
```

**Key point**: `group_by()` returns COUNTS, not the actual authors. This is much more efficient than trying to fetch millions of author records!

## Understanding group_by results

```python
from openalex import Authors

# The result structure is different from regular queries
result = Authors().group_by("has_orcid").get()

print(result.results)  # Empty list - no individual authors returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
for group in result.group_by:
    orcid_status = "With ORCID" if group.key else "Without ORCID"
    print(f"{orcid_status}: {group.count:,} authors")
```

## Common grouping operations

### Basic grouping

```python
# Ensure imports for runnable example
from openalex import Authors

# Group by whether authors have ORCID
orcid_stats = Authors().group_by("has_orcid").get()
# Shows ORCID adoption rate

# Group by works count to see productivity distribution  
productivity = Authors().group_by("works_count").get()
# Returns counts for each value (1 work, 2 works, etc.)

# Group by citation count
citation_distribution = Authors().group_by("cited_by_count").get()
# See how citations are distributed
```

### Institutional analysis

```python
# Include imports so each block can run independently
from openalex import Authors

# Top institutions by author count
top_institutions = Authors().group_by("last_known_institutions.id").get()
# Returns thousands of institutions ranked by affiliated authors

# Countries with most researchers
countries = Authors().group_by("last_known_institutions.country_code").get()
# See global distribution of researchers

# Institution types
inst_types = Authors().group_by("last_known_institutions.type").get()
# education vs. company vs. government, etc.

# Continental distribution
continents = Authors().group_by("last_known_institutions.continent").get()
```

### Research impact analysis

```python
# Include imports
from openalex import Authors

# Distribution of h-index values
h_index_dist = Authors().group_by("summary_stats.h_index").get()
# See how h-indices are distributed

# Distribution of i10-index
i10_dist = Authors().group_by("summary_stats.i10_index").get()

# 2-year mean citedness distribution
citation_impact = Authors().group_by("summary_stats.2yr_mean_citedness").get()
```

### Geographic analysis

```python
# Import Authors for this example
from openalex import Authors

# Global South representation
global_south = Authors().group_by(
    "last_known_institutions.is_global_south"
).get()
# Shows what percentage of authors are from Global South

# Multi-dimensional: Country AND institution type
country_and_type = Authors().group_by(
    "last_known_institutions.country_code",
    "last_known_institutions.type"
).get()
# See which countries have more university vs. company researchers
```

## Combining filters with group_by

Group_by becomes very powerful when combined with filters:

```python
# Import Authors again for a complete example
from openalex import Authors

# ORCID adoption by country (for top countries only)
orcid_by_country = (
    Authors()
    .filter(has_orcid=True)  # Only authors with ORCID
    .group_by("last_known_institutions.country_code")
    .get()
)
print("Countries with most ORCID adoptions:")
for group in orcid_by_country.group_by[:10]:  # Top 10
    print(f"  {group.key}: {group.count:,} authors with ORCID")

# Productivity distribution for high-impact authors only
elite_productivity = (
    Authors()
    .filter_gt(summary_stats={"h_index": 50})  # High h-index only
    .group_by("works_count")
    .get()
)

# Geographic distribution of prolific authors
prolific_geography = (
    Authors()
    .filter_gt(works_count=100)  # 100+ publications
    .group_by("last_known_institutions.continent")
    .get()
)

# Institution types for early-career researchers
early_career_institutions = (
    Authors()
    .filter_lt(works_count=20)  # Fewer than 20 works
    .filter_gt(works_count=2)   # But more than 2
    .group_by("last_known_institutions.type")
    .get()
)
```

## Multi-dimensional grouping

You can group by up to two fields:

```python
# Import Authors for this multi-dimensional example
from openalex import Authors

# ORCID adoption by continent
orcid_by_continent = Authors().group_by(
    "has_orcid",
    "last_known_institutions.continent"
).get()

# Institution type by country
inst_type_by_country = Authors().group_by(
    "last_known_institutions.country_code",
    "last_known_institutions.type"
).get()

# Productivity by institution
productivity_by_inst = Authors().group_by(
    "last_known_institutions.id",
    "works_count"
).get()
```

## Practical examples

### Example 1: Analyze your institution's authors

```python
# First, find your institution ID
from openalex import Institutions, Authors
inst = Institutions().search("MIT").get().results[0]

# Author statistics for MIT
mit_authors = (
    Authors()
    .filter(last_known_institutions={"id": inst.id})
    .group_by("has_orcid")
    .get()
)

# Productivity distribution at MIT
mit_productivity = (
    Authors()
    .filter(last_known_institutions={"id": inst.id})
    .group_by("works_count")
    .get()
)

# H-index distribution at MIT
mit_impact = (
    Authors()
    .filter(last_known_institutions={"id": inst.id})
    .filter_gt(works_count=10)  # Established researchers
    .group_by("summary_stats.h_index")
    .get()
)
```

### Example 2: Geographic analysis

```python
# Import Authors for geographic examples
from openalex import Authors

# ORCID adoption by region
orcid_geography = (
    Authors()
    .filter(has_orcid=True)
    .group_by("last_known_institutions.continent")
    .get()
)

# Top countries without ORCID
no_orcid_countries = (
    Authors()
    .filter(has_orcid=False)
    .group_by("last_known_institutions.country_code")
    .get()
)

# Global South productivity
global_south_productivity = (
    Authors()
    .filter(last_known_institutions={"is_global_south": True})
    .group_by("works_count")
    .get()
)
```

### Example 3: Career stage analysis

```python
# Import Authors for career stage analysis
from openalex import Authors

# Define career stages by works count
def analyze_career_stages():
    # Early career (1-10 works)
    early = (
        Authors()
        .filter_gt(works_count=0)
        .filter_lt(works_count=11)
        .group_by("last_known_institutions.type")
        .get()
    )
    
    # Mid career (11-50 works)
    mid = (
        Authors()
        .filter_gt(works_count=10)
        .filter_lt(works_count=51)
        .group_by("last_known_institutions.type")
        .get()
    )
    
    # Senior (50+ works)
    senior = (
        Authors()
        .filter_gt(works_count=50)
        .group_by("last_known_institutions.type")
        .get()
    )
    
    return early, mid, senior

# Geographic mobility (authors with multiple affiliations)
mobile_authors = (
    Authors()
    .filter_gt(affiliations={"institution": {"count": 2}})
    .group_by("last_known_institutions.country_code")
    .get()
)
```

## Sorting grouped results

Control how results are ordered:

```python
# Import Authors to sort grouped data
from openalex import Authors

# Default: sorted by count (descending)
default_sort = Authors().group_by("last_known_institutions.id").get()
# MIT first (most authors), then Harvard, etc.

# Sort by key instead of count
alphabetical = Authors().group_by(
    "last_known_institutions.country_code"
).sort(key="asc").get()
# Afghanistan, Albania, Algeria...

# Sort by count ascending (smallest groups first)
smallest_first = Authors().group_by(
    "last_known_institutions.type"
).sort(count="asc").get()
```

## Important notes

1. **No individual authors returned**: `group_by()` only returns counts
2. **Maximum 10,000 groups**: API limit on number of groups returned
3. **Two dimensions maximum**: Can group by at most 2 fields
4. **Efficient for analytics**: Much faster than fetching all authors
5. **Can't access author details**: Only counts and group keys available

When you need statistics about authors, always prefer `group_by()` over trying to fetch and count individual records!
