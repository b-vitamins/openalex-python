# Group sources

You can group sources to get aggregated statistics without fetching individual source records:

```python
from openalex import Sources

# Create a query that groups sources by host organization
publisher_stats_query = Sources().group_by("host_organization")

# Execute the query to get COUNTS, not individual sources
publisher_stats = publisher_stats_query.get()

# This returns aggregated statistics, NOT source objects!
print("Sources by publisher (top 20):")
for group in publisher_stats.group_by[:20]:
    # Each group has a 'key' (the publisher name) and 'count'
    print(f"  {group.key}: {group.count:,} sources")
```

**Key point**: `group_by()` returns COUNTS, not the actual sources. This is efficient for analytics.

## Understanding group_by results

```python
from openalex import Sources

# The result structure is different from regular queries
result = Sources().group_by("type").get()

print(result.results)  # Empty list - no individual sources returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
print("Sources by type:")
for group in result.group_by:
    percentage = (group.count / result.meta.count) * 100
    print(f"  {group.key}: {group.count:,} ({percentage:.1f}%)")
```

## Common grouping operations

### Basic grouping

```python
from openalex import Sources

# Group by source type
type_dist = Sources().group_by("type").get()
# Shows: journal, repository, conference, ebook platform, etc.

# Group by country
by_country = Sources().group_by("country_code").get()
# See global distribution of sources

# Group by continent
by_continent = Sources().group_by("continent").get()
# Broader geographic view

# Group by Open Access status
oa_dist = Sources().group_by("is_oa").get()
# Shows OA vs subscription breakdown

# Group by DOAJ inclusion
doaj_dist = Sources().group_by("is_in_doaj").get()
# How many are in DOAJ

# Group by Core status
core_dist = Sources().group_by("is_core").get()
# Leiden Ranking core sources

# Group by ISSN availability
issn_coverage = Sources().group_by("has_issn").get()
# Most should have ISSNs
```

### Financial grouping

```python
from openalex import Sources

# APC currency distribution
apc_currencies = Sources().group_by("apc_prices.currency").get()
# Shows which currencies are used for APCs

# APC amount ranges (in USD)
apc_ranges = Sources().group_by("apc_usd").get()
# Note: Creates many groups (one per unique amount)

# Host organization analysis
by_host = Sources().group_by("host_organization").get()
# Which organizations host the most sources

# Publisher lineage
by_lineage = Sources().group_by("host_organization_lineage").get()
# Including parent/child publisher relationships
```

### Research metrics grouping

```python
from openalex import Sources

# Citation count distribution
citation_dist = Sources().group_by("cited_by_count").get()
# Note: Many unique values, consider filtering first

# Works count distribution
productivity_dist = Sources().group_by("works_count").get()

# Impact factor (2-year mean citedness) ranges
impact_dist = Sources().group_by("summary_stats.2yr_mean_citedness").get()

# H-index distribution
h_index_dist = Sources().group_by("summary_stats.h_index").get()

# i10-index distribution
i10_dist = Sources().group_by("summary_stats.i10_index").get()
```

## Combining filters with group_by

Group_by becomes more insightful when combined with filters:

```python
from openalex import Sources

# Type distribution for OA sources only
oa_types = (
    Sources()
    .filter(is_oa=True)
    .group_by("type")
    .get()
)
print("Open Access sources by type:")
for group in oa_types.group_by:
    print(f"  {group.key}: {group.count:,}")

# Country distribution for high-impact journals
high_impact_countries = (
    Sources()
    .filter(type="journal")
    .filter_gt(summary_stats={"2yr_mean_citedness": 5.0})
    .group_by("country_code")
    .get()
)
print("Countries with high-impact journals (IF > 5):")
for group in high_impact_countries.group_by[:10]:
    print(f"  {group.key}: {group.count} journals")

# APC analysis for DOAJ journals
doaj_apcs = (
    Sources()
    .filter(is_in_doaj=True)
    .group_by("apc_prices.currency")
    .get()
)

# Publisher diversity by region
european_publishers = (
    Sources()
    .filter(continent="europe")
    .group_by("host_organization_name")
    .get()
)
```

## Multi-dimensional grouping

You can group by two dimensions:

```python
from openalex import Sources

# Type and OA status
type_oa = Sources().group_by("type", "is_oa").get()

# Country and type
country_type = Sources().group_by("country_code", "type").get()

# This shows which countries have which types of sources
for group in country_type.group_by[:20]:
    # Keys are pipe-separated for multi-dimensional groups
    country, source_type = group.key.split('|')
    print(f"{country} - {source_type}: {group.count}")

# Publisher and source type
# Group by host organization and source type
publisher_types = Sources().group_by("host_organization", "type").get()
# See what types of sources each publisher has
```

## Practical examples

### Example 1: Open Access landscape analysis

```python
from openalex import Sources

def analyze_oa_landscape():
    """Analyze the global OA publishing landscape."""
    
    # Overall OA distribution
    oa_status = Sources().group_by("is_oa").get()
    
    # OA by source type
    oa_by_type = (
        Sources()
        .filter(is_oa=True)
        .group_by("type")
        .get()
    )
    
    # Geographic distribution of OA
    oa_by_continent = (
        Sources()
        .filter(is_oa=True)
        .group_by("continent")
        .get()
    )
    
    # APC analysis for OA journals
    oa_with_apc = (
        Sources()
        .filter(is_oa=True)
        .filter(type="journal")
        .filter_gt(apc_usd=0)
        .group_by("apc_prices.currency")
        .get()
    )
    
    print("Open Access Landscape Analysis")
    print("=" * 40)
    
    # Calculate OA percentage
    for group in oa_status.group_by:
        status = "Open Access" if group.key else "Subscription"
        percentage = (group.count / oa_status.meta.count) * 100
        print(f"{status}: {group.count:,} ({percentage:.1f}%)")
    
    print("\nOA sources by type:")
    for group in oa_by_type.group_by:
        print(f"  {group.key}: {group.count:,}")
    
    print("\nOA sources by continent:")
    for group in oa_by_continent.group_by:
        print(f"  {group.key}: {group.count:,}")
    
    print("\nAPC currencies for OA journals:")
    for group in oa_with_apc.group_by[:10]:
        print(f"  {group.key}: {group.count:,} journals")

analyze_oa_landscape()
```

### Example 2: Publisher concentration analysis

```python
from openalex import Sources

def analyze_publisher_concentration():
    """Analyze market concentration in academic publishing."""
    
    # Top publishers by number of sources
    by_publisher = Sources().group_by("host_organization").get()
    
    # Top publishers of OA sources
    oa_publishers = (
        Sources()
        .filter(is_oa=True)
        .group_by("host_organization")
        .get()
    )
    
    # Regional publisher diversity
    regions = {
        "North America": ["US", "CA"],
        "Europe": ["GB", "DE", "NL", "FR"],
        "Asia": ["CN", "JP", "IN", "KR"]
    }
    
    print("Publisher Concentration Analysis")
    print("=" * 40)
    
    # Show top 10 publishers
    print("\nTop 10 publishers by source count:")
    total_sources = by_publisher.meta.count
    top10_count = 0
    for i, group in enumerate(by_publisher.group_by[:10], 1):
        percentage = (group.count / total_sources) * 100
        top10_count += group.count
        print(f"{i}. {group.key}: {group.count:,} ({percentage:.1f}%)")
    
    concentration = (top10_count / total_sources) * 100
    print(f"\nTop 10 publishers control {concentration:.1f}% of all sources")
    
    # Regional analysis
    print("\nPublisher diversity by region:")
    for region, countries in regions.items():
        regional_publishers = (
            Sources()
            .filter(country_code=countries)
            .group_by("host_organization")
            .get()
        )
        
        unique_publishers = len(regional_publishers.group_by)
        print(f"  {region}: {unique_publishers} unique publishers")

analyze_publisher_concentration()
```

### Example 3: Journal quality metrics

```python
from openalex import Sources

def analyze_journal_quality_tiers():
    """Group journals into quality tiers based on impact factor."""
    
    # Define impact factor tiers
    tiers = [
        ("Elite", 20.0, float('inf')),
        ("High", 10.0, 20.0),
        ("Good", 5.0, 10.0),
        ("Average", 2.0, 5.0),
        ("Low", 0.0, 2.0)
    ]
    
    print("Journal Quality Tiers (by Impact Factor)")
    print("=" * 40)
    
    total_journals = Sources().filter(type="journal").get().meta.count
    
    for tier_name, min_if, max_if in tiers:
        # Build filter
        tier_query = Sources().filter(type="journal")
        
        if min_if > 0:
            tier_query = tier_query.filter_gt(
                summary_stats={"2yr_mean_citedness": min_if}
            )
        if max_if < float('inf'):
            tier_query = tier_query.filter_lt(
                summary_stats={"2yr_mean_citedness": max_if}
            )
        
        # Get count for this tier
        tier_result = tier_query.get()
        count = tier_result.meta.count
        percentage = (count / total_journals) * 100
        
        print(f"\n{tier_name} tier (IF {min_if}-{max_if}):")
        print(f"  Journals: {count:,} ({percentage:.1f}%)")
        
        # Show geographic distribution for this tier
        geo_dist = tier_query.group_by("continent").get()
        print("  By continent:")
        for group in geo_dist.group_by[:5]:
            print(f"    {group.key}: {group.count}")

analyze_journal_quality_tiers()
```

### Example 4: Repository landscape

```python
from openalex import Sources

def analyze_repository_ecosystem():
    """Analyze the repository landscape."""
    
    # Total repositories
    all_repos = Sources().filter(type="repository").get()
    
    # By country
    repo_countries = (
        Sources()
        .filter(type="repository")
        .group_by("country_code")
        .get()
    )
    
    # By host organization
    repo_hosts = (
        Sources()
        .filter(type="repository")
        .group_by("host_organization_name")
        .get()
    )
    
    print(f"Repository Landscape Analysis")
    print(f"Total repositories: {all_repos.meta.count:,}")
    print("=" * 40)
    
    print("\nTop 10 countries by repository count:")
    for group in repo_countries.group_by[:10]:
        print(f"  {group.key}: {group.count} repositories")
    
    print("\nTop repository hosts:")
    for group in repo_hosts.group_by[:10]:
        if group.key:  # Some might not have host org
            print(f"  {group.key}: {group.count} repositories")
```

## Sorting grouped results

Control how results are ordered:

```python
from openalex import Sources

# Default: sorted by count (descending)
default_sort = Sources().group_by("host_organization").get()
# Elsevier first (most sources), then Springer, etc.

# Sort by key instead of count
alphabetical = Sources().group_by("type").sort(key="asc").get()
# conference, ebook platform, journal... (alphabetical)

# Sort by count ascending (smallest groups first)
smallest_first = Sources().group_by("host_organization").sort(count="asc").get()
# Publishers with fewest sources first
```

## Important notes

1. **No individual sources returned**: `group_by()` only returns counts
2. **Efficient for analytics**: Much faster than fetching all sources
3. **Limited dimensions**: Maximum 2 fields for grouping
4. **Can handle all sources**: With ~249,000 total, aggregations are fast
5. **Great for market analysis**: Understand publishing landscape

When you need statistics about sources, always prefer `group_by()` over fetching and counting individual records!
