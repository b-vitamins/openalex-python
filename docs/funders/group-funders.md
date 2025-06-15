# Group funders

You can group funders to get aggregated statistics without fetching individual funder records:

```python
from openalex import Funders

# Create a query that groups funders by country
country_stats_query = Funders().group_by("country_code")

# Execute the query to get COUNTS, not individual funders
country_stats = country_stats_query.get()

# This returns aggregated statistics, NOT funder objects!
print("Funders by country (top 20):")
for group in country_stats.group_by[:20]:
    # Each group has a 'key' (the country code) and 'count'
    print(f"  {group.key}: {group.count:,} funders")
```

**Key point**: `group_by()` returns COUNTS, not the actual funders. This is efficient for analytics.

## Understanding group_by results

```python
# The result structure is different from regular queries
from openalex import Funders
result = Funders().group_by("continent").get()

print(result.results)  # Empty list - no individual funders returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
print("Funders by continent:")
for group in result.group_by:
    percentage = (group.count / result.meta.count) * 100
    print(f"  {group.key}: {group.count:,} ({percentage:.1f}%)")
```

## Common grouping operations

### Basic grouping

```python
from openalex import Funders

# Group by country
by_country = Funders().group_by("country_code").get()
# See which countries have the most funders

# Group by continent
by_continent = Funders().group_by("continent").get()
# Broader geographic view

# Group by Global South status
global_south_dist = Funders().group_by("is_global_south").get()
# Shows Global South vs. Global North distribution

# Group by grant count ranges
grant_dist = Funders().group_by("grants_count").get()
# Note: Creates many groups (one per unique count)

# Group by citation impact
citation_dist = Funders().group_by("cited_by_count").get()
# Distribution of citation counts
```

### Research metrics grouping

```python
from openalex import Funders

# H-index distribution
h_index_dist = Funders().group_by("summary_stats.h_index").get()

# i10-index distribution
i10_dist = Funders().group_by("summary_stats.i10_index").get()

# 2-year mean citedness
impact_dist = Funders().group_by("summary_stats.2yr_mean_citedness").get()

# Works count distribution
productivity_dist = Funders().group_by("works_count").get()
```

## Combining filters with group_by

Group_by becomes more insightful when combined with filters:

```python
from openalex import Funders

# Country distribution for large funders only
large_funder_countries = (
    Funders()
    .filter_gt(grants_count=1000)
    .group_by("country_code")
    .get()
)
print("Countries with large funders (>1k grants):")
for group in large_funder_countries.group_by[:10]:
    print(f"  {group.key}: {group.count} large funders")

# Continental distribution of high-impact funders
high_impact_continents = (
    Funders()
    .filter_gt(summary_stats={"h_index": 200})
    .group_by("continent")
    .get()
)

# Global South representation among major funders
global_south_major = (
    Funders()
    .filter_gt(works_count=10000)
    .group_by("is_global_south")
    .get()
)

# Grant distribution by country for active funders
active_funders_grants = (
    Funders()
    .filter_gt(grants_count=100)
    .group_by("country_code")
    .get()
)
```

## Multi-dimensional grouping

You can group by two dimensions:

```python
# Ensure Funders is available
from openalex import Funders

# Country and grant volume
country_grants = Funders().group_by("country_code", "grants_count").get()

# Continent and impact
continent_impact = Funders().group_by("continent", "summary_stats.h_index").get()

# This shows distribution patterns
for group in country_grants.group_by[:20]:
    # Keys are pipe-separated for multi-dimensional groups
    country, grant_count = group.key.split('|')
    print(f"{country} - {grant_count} grants: {group.count} funders")
```

## Practical examples

### Example 1: Global funding landscape

```python
from openalex import Funders

def analyze_global_funding_landscape():
    """Analyze the global distribution of research funders."""
    
    # Overall geographic distribution
    by_continent = Funders().group_by("continent").get()
    
    # High-impact funders by continent
    high_impact_by_continent = (
        Funders()
        .filter_gt(summary_stats={"h_index": 100})
        .group_by("continent")
        .get()
    )
    
    # Calculate impact concentration
    print("Funding Landscape Analysis")
    print("=" * 40)
    
    for cont in by_continent.group_by:
        continent = cont.key
        total = cont.count
        
        # Find high-impact count for this continent
        high_impact = next(
            (g.count for g in high_impact_by_continent.group_by if g.key == continent),
            0
        )
        
        concentration = (high_impact / total * 100) if total > 0 else 0
        print(f"\n{continent}:")
        print(f"  Total funders: {total}")
        print(f"  High-impact (h>100): {high_impact} ({concentration:.1f}%)")

analyze_global_funding_landscape()
```

### Example 2: Funding concentration analysis

```python
from openalex import Funders

def analyze_funding_concentration():
    """Analyze how concentrated research funding is."""
    
    # Countries by number of funders
    by_country = Funders().group_by("country_code").get()
    
    # Countries with major funders
    major_funders = (
        Funders()
        .filter_gt(grants_count=1000)
        .group_by("country_code")
        .get()
    )
    
    # Countries with mega-funders
    mega_funders = (
        Funders()
        .filter_gt(cited_by_count=10000000)
        .group_by("country_code")
        .get()
    )
    
    print("Funding Concentration Analysis")
    print("=" * 40)
    
    # Top 10 countries
    total_funders = sum(g.count for g in by_country.group_by)
    top10_count = sum(g.count for g in by_country.group_by[:10])
    concentration = (top10_count / total_funders) * 100
    
    print(f"\nTop 10 countries have {concentration:.1f}% of all funders")
    
    print("\nCountry Rankings:")
    print(f"{'Country':<10} {'Total':<8} {'Major':<8} {'Mega':<8}")
    print("-" * 35)
    
    for group in by_country.group_by[:15]:
        country = group.key
        total = group.count
        
        major = next(
            (g.count for g in major_funders.group_by if g.key == country),
            0
        )
        mega = next(
            (g.count for g in mega_funders.group_by if g.key == country),
            0
        )
        
        print(f"{country:<10} {total:<8} {major:<8} {mega:<8}")

analyze_funding_concentration()
```

### Example 3: Funding impact tiers

```python
from openalex import Funders

def analyze_funding_impact_tiers():
    """Group funders into impact tiers based on h-index."""
    
    # Define impact tiers
    tiers = [
        ("Mega", 500, float('inf')),
        ("Elite", 300, 500),
        ("High", 200, 300),
        ("Medium", 100, 200),
        ("Emerging", 50, 100),
        ("Developing", 0, 50)
    ]
    
    print("Funders by Impact Tier (H-index based)")
    print("=" * 40)
    
    total_funders = Funders().get().meta.count
    
    for tier_name, min_h, max_h in tiers:
        # Build filter
        tier_query = Funders()
        
        if min_h > 0:
            tier_query = tier_query.filter_gt(summary_stats={"h_index": min_h})
        if max_h < float('inf'):
            tier_query = tier_query.filter_lt(summary_stats={"h_index": max_h})
        
        # Get count and geographic distribution
        tier_result = tier_query.get()
        geo_dist = tier_query.group_by("continent").get()
        
        count = tier_result.meta.count
        percentage = (count / total_funders) * 100
        
        print(f"\n{tier_name} tier (h-index {min_h}-{max_h}):")
        print(f"  Funders: {count:,} ({percentage:.1f}%)")
        print("  Geographic distribution:")
        for group in geo_dist.group_by[:5]:
            print(f"    {group.key}: {group.count}")

analyze_funding_impact_tiers()
```

### Example 4: Funding ecosystem comparison

```python
from openalex import Funders

def compare_funding_ecosystems():
    """Compare funding characteristics across regions."""
    
    regions = {
        "North America": ["US", "CA"],
        "Europe": ["GB", "DE", "FR", "NL", "CH"],
        "Asia": ["CN", "JP", "KR", "IN", "SG"]
    }
    
    print("Regional Funding Ecosystem Comparison")
    print("=" * 50)
    
    for region_name, countries in regions.items():
        # Total funders in region
        regional = Funders().filter(country_code=countries).get()
        
        # Funders with many grants
        productive = (
            Funders()
            .filter(country_code=countries)
            .filter_gt(grants_count=500)
            .get()
        )
        
        # High-impact funders
        high_impact = (
            Funders()
            .filter(country_code=countries)
            .filter_gt(summary_stats={"h_index": 200})
            .get()
        )
        
        # Group by specific countries
        by_country = (
            Funders()
            .filter(country_code=countries)
            .group_by("country_code")
            .get()
        )
        
        print(f"\n{region_name}:")
        print(f"  Total funders: {regional.meta.count}")
        print(f"  Productive (>500 grants): {productive.meta.count}")
        print(f"  High-impact (h>200): {high_impact.meta.count}")
        print("  By country:")
        for group in by_country.group_by:
            print(f"    {group.key}: {group.count}")

compare_funding_ecosystems()
```

## Sorting grouped results

Control how results are ordered:

```python
from openalex import Funders

# Default: sorted by count (descending)
default_sort = Funders().group_by("country_code").get()
# US first (most funders), then CN, GB, etc.

# Sort by key instead of count
alphabetical = Funders().group_by("country_code").sort(key="asc").get()
# AF, AL, AM... (alphabetical by country code)

# Sort by count ascending (smallest groups first)
smallest_first = Funders().group_by("continent").sort(count="asc").get()
# Continents with fewest funders first
```

## Important notes

1. **No individual funders returned**: `group_by()` only returns counts
2. **Very efficient**: Much faster than fetching all funders
3. **Limited dimensions**: Maximum 2 fields for grouping
4. **Perfect for small datasets**: With ~32,000 funders, all analyses are fast
5. **Great for policy analysis**: Understand funding landscapes globally

When you need statistics about funders, always prefer `group_by()` over fetching and counting individual records!
