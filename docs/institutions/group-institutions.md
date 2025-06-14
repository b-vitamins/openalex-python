# Group institutions

You can group institutions to get aggregated statistics without fetching individual institution records:

```python
from openalex import Institutions

# Create a query that groups institutions by country
country_stats_query = Institutions().group_by("country_code")

# Execute the query to get COUNTS, not individual institutions
country_stats = country_stats_query.get()

# This returns aggregated statistics, NOT institution objects!
print("Institutions by country (top 20):")
for group in country_stats.group_by[:20]:
    # Each group has a 'key' (the country code) and 'count'
    print(f"  {group.key}: {group.count:,} institutions")
```

**Key point**: `group_by()` returns COUNTS, not the actual institutions. This is efficient for analytics.

## Understanding group_by results

```python
# The result structure is different from regular queries
from openalex import Institutions

# The result structure is different from regular queries
result = Institutions().group_by("type").get()

print(result.results)  # Empty list - no individual institutions returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
print("Institutions by type:")
for group in result.group_by:
    percentage = (group.count / result.meta.count) * 100
    print(f"  {group.key}: {group.count:,} ({percentage:.1f}%)")
```

## Common grouping operations

### Basic grouping

```python
# Group by institution type
from openalex import Institutions

# Group by institution type
type_dist = Institutions().group_by("type").get()
# Shows distribution: education, healthcare, company, etc.

# Group by country
by_country = Institutions().group_by("country_code").get()
# See global distribution of institutions

# Group by continent
by_continent = Institutions().group_by("continent").get()
# Broader geographic view

# Group by Global South status
global_south_dist = Institutions().group_by("is_global_south").get()
# Shows Global South vs. Global North distribution

# Group by super system status
super_system_dist = Institutions().group_by("is_super_system").get()
# How many are large super systems

# Group by ROR availability
ror_coverage = Institutions().group_by("has_ror").get()
# Most should have ROR IDs
```

### Research metrics grouping

```python
# Distribution of citation counts
from openalex import Institutions

# Distribution of citation counts
citation_ranges = Institutions().group_by("cited_by_count").get()
# Note: This creates many groups (one per unique count)

# H-index distribution
h_index_dist = Institutions().group_by("summary_stats.h_index").get()

# Works count distribution
productivity_dist = Institutions().group_by("works_count").get()

# 2-year mean citedness
impact_dist = Institutions().group_by("summary_stats.2yr_mean_citedness").get()
```

```python
from openalex import Institutions

# Group institutions by works_count range (10k increments)
size_bins = Institutions().group_by("works_count", interval=10000).get()
for group in size_bins.group_by[:5]:
    print(f"{group.key}: {group.count} institutions")
```

### Repository analysis

```python
# Institutions that host repositories
from openalex import Institutions

# Institutions that host repositories
has_repos = Institutions().group_by(
    "repositories.host_organization"
).get()
# Each group is an institution that hosts repositories
```

## Combining filters with group_by

Group_by becomes more insightful when combined with filters:

```python
# Type distribution by continent
from openalex import Institutions

# Type distribution by continent
europe_types = (
    Institutions()
    .filter(continent="europe")
    .group_by("type")
    .get()
)
print("European institutions by type:")
for group in europe_types.group_by:
    print(f"  {group.key}: {group.count:,}")

# Country distribution for large universities only
large_uni_countries = (
    Institutions()
    .filter(type="education")
    .filter_gt(works_count=10000)
    .group_by("country_code")
    .get()
)
print("Countries with large universities (>10k works):")
for group in large_uni_countries.group_by[:10]:
    print(f"  {group.key}: {group.count} large universities")

# Global South representation by type
global_south_types = (
    Institutions()
    .filter(is_global_south=True)
    .group_by("type")
    .get()
)

# High-impact institutions by country
elite_by_country = (
    Institutions()
    .filter_gt(summary_stats={"h_index": 200})
    .group_by("country_code")
    .get()
)
```

## Multi-dimensional grouping

You can group by two dimensions:

```python
# Type and continent
from openalex import Institutions

# Type and continent
type_continent = Institutions().group_by("type", "continent").get()

# Country and type
country_type = Institutions().group_by("country_code", "type").get()

# This shows which countries have diverse institution types
for group in country_type.group_by[:20]:
    # Keys are pipe-separated for multi-dimensional groups
    country, inst_type = group.key.split('|')
    print(f"{country} - {inst_type}: {group.count}")
```

## Practical examples

### Example 1: Global research landscape

```python
from openalex import Institutions

def analyze_global_research():
    """Analyze the global distribution of research institutions."""
    
    # Overall distribution by continent
    by_continent = Institutions().group_by("continent").get()
    
    # Research universities by continent
    research_unis = (
        Institutions()
        .filter(type="education")
        .filter_gt(works_count=5000)
        .group_by("continent")
        .get()
    )
    
    # Calculate research intensity
    print("Research intensity by continent:")
    for cont in by_continent.group_by:
        continent = cont.key
        total = cont.count
        
        # Find research count for this continent
        research_count = next(
            (g.count for g in research_unis.group_by if g.key == continent),
            0
        )
        
        intensity = (research_count / total * 100) if total > 0 else 0
        print(f"  {continent}: {research_count}/{total} "
              f"({intensity:.1f}% are major research institutions)")

analyze_global_research()
```

### Example 2: Institution type analysis

```python
from openalex import Institutions

def analyze_institution_ecosystem():
    """Understand the mix of institution types globally."""
    
    # Basic type distribution
    types = Institutions().group_by("type").get()
    
    # Type distribution in Global South vs North
    global_south_types = (
        Institutions()
        .filter(is_global_south=True)
        .group_by("type")
        .get()
    )
    
    global_north_types = (
        Institutions()
        .filter(is_global_south=False)
        .group_by("type")
        .get()
    )
    
    print("Institution type comparison:")
    print("Type | Global South | Global North")
    print("-" * 40)
    
    for type_group in types.group_by:
        inst_type = type_group.key
        
        south_count = next(
            (g.count for g in global_south_types.group_by if g.key == inst_type),
            0
        )
        north_count = next(
            (g.count for g in global_north_types.group_by if g.key == inst_type),
            0
        )
        
        print(f"{inst_type:<12} | {south_count:>12,} | {north_count:>12,}")

analyze_institution_ecosystem()
```

### Example 3: Research concentration

```python
from openalex import Institutions

def analyze_research_concentration():
    """Analyze how research is concentrated globally."""
    
    # Countries by number of high-output institutions
    high_output = (
        Institutions()
        .filter_gt(works_count=50000)
        .group_by("country_code")
        .get()
    )
    
    # Countries by number of high-impact institutions
    high_impact = (
        Institutions()
        .filter_gt(summary_stats={"h_index": 300})
        .group_by("country_code")
        .get()
    )
    
    # Combine the analyses
    print("Research concentration by country:")
    print("Country | High Output | High Impact")
    print("-" * 40)
    
    # Get unique countries from both
    countries = set()
    for g in high_output.group_by[:20]:
        countries.add(g.key)
    for g in high_impact.group_by[:20]:
        countries.add(g.key)
    
    for country in sorted(countries):
        output_count = next(
            (g.count for g in high_output.group_by if g.key == country),
            0
        )
        impact_count = next(
            (g.count for g in high_impact.group_by if g.key == country),
            0
        )
        
        if output_count > 0 or impact_count > 0:
            print(f"{country:>7} | {output_count:>11} | {impact_count:>11}")

analyze_research_concentration()
```

### Example 4: Repository hosting

```python
from openalex import Institutions

def analyze_repository_landscape():
    """Analyze which institutions host repositories."""
    
    # Basic count of institutions with repositories
    has_repo = (
        Institutions()
        .filter(repositories={"id": {"exists": True}})
        .get()
    )
    
    print(f"Institutions hosting repositories: {has_repo.meta.count:,}")
    
    # By country
    repo_by_country = (
        Institutions()
        .filter(repositories={"id": {"exists": True}})
        .group_by("country_code")
        .get()
    )
    
    print("\nTop 10 countries by repository-hosting institutions:")
    for group in repo_by_country.group_by[:10]:
        print(f"  {group.key}: {group.count} institutions with repositories")
```

## Sorting grouped results

Control how results are ordered:

```python
# Default: sorted by count (descending)
from openalex import Institutions

# Default: sorted by count (descending)
default_sort = Institutions().group_by("country_code").get()
# US first (most institutions), then CN, GB, etc.

# Sort by key instead of count
alphabetical = Institutions().group_by("country_code").sort(key="asc").get()
# AF, AL, AM... (alphabetical by country code)

# Sort by count ascending (smallest groups first)
smallest_first = Institutions().group_by("type").sort(count="asc").get()
# Rarest types first
```

## Important notes

1. **No individual institutions returned**: `group_by()` only returns counts
2. **Efficient for analytics**: Much faster than fetching all institutions
3. **Limited dimensions**: Maximum 2 fields for grouping
4. **Can handle all institutions**: With ~109,000 total, aggregations are fast
5. **Great for comparative analysis**: Understand global patterns

When you need statistics about institutions, always prefer `group_by()` over fetching and counting individual records!
