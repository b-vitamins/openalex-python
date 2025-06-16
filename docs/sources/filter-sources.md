# Filter sources

You can filter sources using the Python client:

```python
from openalex import Sources

# Create a filtered query for sources with ISSNs
sources_with_issn_query = Sources().filter(has_issn=True)

# Execute the query to get the first page of results
results = sources_with_issn_query.get()

print(f"Total sources with ISSN: {results.meta.count:,}")
print(f"Showing first {len(results.results)} sources")

# Show some examples
for source in results.results[:5]:
    print(f"- {source.display_name}: {source.issn_l}")
```

Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Sources attribute filters

You can filter using these attributes of the [`Source`](source-object.md) object:

### Basic attribute filters

```python
from openalex import Sources

# Filter by cited_by_count
highly_cited = Sources().filter(cited_by_count=1000000).get()  # Exactly 1M
very_highly_cited = Sources().filter_gt(cited_by_count=10000000).get()  # More than 10M

# Filter by works_count
large_sources = Sources().filter_gt(works_count=10000).get()  # More than 10k works
small_sources = Sources().filter_lt(works_count=100).get()  # Fewer than 100 works

# Filter by type
journals = Sources().filter(type="journal").get()
repositories = Sources().filter(type="repository").get()
conferences = Sources().filter(type="conference").get()
ebook_platforms = Sources().filter(type="ebook platform").get()

# Filter by country
us_sources = Sources().filter(country_code="US").get()
uk_sources = Sources().filter(country_code="GB").get()

# Multiple countries (OR operation)
european_sources = Sources().filter(
    country_code=["DE", "FR", "IT", "ES", "NL", "GB"]
).get()

# Filter by specific IDs
specific_ids = Sources().filter(
    openalex=["S137773608", "S125754415"]
).get()

# Filter by ISSN
nature_journal = Sources().filter(issn="0028-0836").get()
```

### Host organization filters

```python
from openalex import Sources

# Filter by host organization (publisher or institution)
elsevier_sources = Sources().filter(host_organization="P4310320595").get()

# Filter by publisher lineage (includes all children)
# This finds all sources from a publisher and its imprints
springer_nature_lineage = Sources().filter(
    host_organization_lineage="P4310319965"
).get()

# Filter by exact host organization (publisher) match
exact_publisher = Sources().filter(host_organization="P4310320595").get()
```

### Open Access filters

```python
from openalex import Sources

# Open Access sources
oa_sources = Sources().filter(is_oa=True).get()
subscription_sources = Sources().filter(is_oa=False).get()

# DOAJ listed sources
doaj_sources = Sources().filter(is_in_doaj=True).get()

# Core sources (CWTS Leiden Ranking)
core_sources = Sources().filter(is_core=True).get()
```

### APC (Article Processing Charge) filters

```python
from openalex import Sources

# Filter by APC amount in USD
expensive_apc = Sources().filter_gt(apc_usd=5000).get()
affordable_apc = Sources().filter_lt(apc_usd=1000).get()
no_apc = Sources().filter(apc_usd=0).get()

# Filter by APC currency
gbp_apc = Sources().filter(apc_prices={"currency": "GBP"}).get()
eur_apc = Sources().filter(apc_prices={"currency": "EUR"}).get()

# Filter by specific APC price
specific_price = Sources().filter(apc_prices={"price": 3000}).get()
```

### Summary statistics filters

```python
from openalex import Sources

# Filter by impact factor (2-year mean citedness)
high_impact = Sources().filter_gt(summary_stats={"2yr_mean_citedness": 10.0}).get()
medium_impact = (
    Sources()
    .filter_gt(summary_stats={"2yr_mean_citedness": 2.0})
    .filter_lt(summary_stats={"2yr_mean_citedness": 5.0})
    .get()
)

# Filter by h-index
high_h_index = Sources().filter_gt(summary_stats={"h_index": 200}).get()

# Filter by i10-index
productive = Sources().filter_gt(summary_stats={"i10_index": 5000}).get()

# Combine metrics
elite_journals = (
    Sources()
    .filter_gt(summary_stats={"h_index": 300})
    .filter_gt(summary_stats={"2yr_mean_citedness": 15.0})
    .filter_gt(works_count=10000)
    .get()
)
```

### Concept filters (deprecated)

```python
from openalex import Sources

# Note: x_concepts will be deprecated soon, replaced by Topics
# Filter by concept
medical_sources = Sources().filter(
    x_concepts={"id": "C71924100"}  # Medicine concept
).get()
```

## Convenience filters

These filters aren't attributes of the Source object, but they're handy:

### Geographic convenience filters

```python
from openalex import Sources

# Filter by continent
north_american = Sources().filter(continent="north_america").get()
european = Sources().filter(continent="europe").get()
asian = Sources().filter(continent="asia").get()

# Filter by Global South status
global_south = Sources().filter(is_global_south=True).get()
global_north = Sources().filter(is_global_south=False).get()

print(f"Global South sources: {global_south.meta.count:,}")
print(f"Global North sources: {global_north.meta.count:,}")
```

### Boolean filters

```python
from openalex import Sources

# Has ISSN
with_issn = Sources().filter(has_issn=True).get()
without_issn = Sources().filter(has_issn=False).get()

print(f"With ISSN: {with_issn.meta.count:,}")
print(f"Without ISSN: {without_issn.meta.count:,}")
```

### Text search filters

```python
from openalex import Sources

# Search in display names
neurology_search = Sources().filter(
    display_name={"search": "neurology"}
).get()

# Alternative: use search_filter
medical_search = Sources().search_filter(display_name="medical").get()

# Default search (same as using .search() method)
default_search = Sources().filter(
    default={"search": "computer science"}
).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
from openalex import Sources

# High-impact OA journals
high_impact_oa = (
    Sources()
    .filter(type="journal")
    .filter(is_oa=True)
    .filter_gt(summary_stats={"2yr_mean_citedness": 5.0})
    .sort(**{"summary_stats.2yr_mean_citedness": "desc"})
    .get()
)

# US repositories with many works
large_us_repos = (
    Sources()
    .filter(country_code="US")
    .filter(type="repository")
    .filter_gt(works_count=10000)
    .get()
)

# DOAJ journals with no APCs
free_oa_journals = (
    Sources()
    .filter(is_in_doaj=True)
    .filter(apc_usd=0)
    .get(per_page=50)
)
```

### NOT operations

```python
from openalex import Sources

# Sources NOT from the US
non_us = Sources().filter_not(country_code="US").get()

# Non-journal sources
non_journals = Sources().filter_not(type="journal").get()

# Sources without APC information
no_apc = Sources().filter(apc_usd=None).get()
```

### Range queries

```python
from openalex import Sources

# Mid-range impact factor (2-5)
mid_impact = (
    Sources()
    .filter_gt(summary_stats={"2yr_mean_citedness": 2.0})
    .filter_lt(summary_stats={"2yr_mean_citedness": 5.0})
    .get()
)

# Sources with moderate output (100-1000 works/year)
moderate_output = (
    Sources()
    .filter_gt(works_count=100)
    .filter_lt(works_count=1000)
    .get()
)
```

## Practical examples

### Example 1: Find affordable OA options

```python
from openalex import Sources

def find_affordable_oa_journals(max_apc=1500, min_impact=2.0):
    """Find OA journals with reasonable APCs and decent impact."""

    affordable_oa = (
        Sources()
        .filter(type="journal")
        .filter(is_oa=True)
        .filter_lt(apc_usd=max_apc)
        .filter_gt(summary_stats={"2yr_mean_citedness": min_impact})
        .sort(**{"summary_stats.2yr_mean_citedness": "desc"})
        .get(per_page=20)
    )

    print(f"Affordable OA journals (APC < ${max_apc}, IF > {min_impact}):")
    for journal in affordable_oa.results:
        apc = journal.apc_usd or 0
        impact = (
            journal.summary_stats.get("2yr_mean_citedness")
            if isinstance(journal.summary_stats, dict)
            else journal.summary_stats.two_year_mean_citedness
        )
        print(f"\n{journal.display_name}")
        print(f"  APC: ${apc}")
        print(f"  Impact Factor: {impact:.2f}")
        print(f"  Publisher: {journal.host_organization_name}")

    return affordable_oa

# Find options
find_affordable_oa_journals(max_apc=2000, min_impact=3.0)
```

### Example 2: Publisher analysis

```python
from openalex import Sources

def analyze_publisher_portfolio(publisher_id):
    """Analyze all sources from a publisher."""

    # Get all sources from this publisher
    publisher_sources = (
        Sources()
        .filter(host_organization_lineage=publisher_id)
        .get(per_page=200)
    )

    # Analyze by type
    types = {}
    oa_count = 0
    total_citations = 0

    for source in publisher_sources.results:
        types[source.type] = types.get(source.type, 0) + 1
        if source.is_oa:
            oa_count += 1
        total_citations += source.cited_by_count

    print(f"Publisher portfolio analysis:")
    print(f"Total sources: {publisher_sources.meta.count}")
    print(f"Open Access: {oa_count} ({oa_count/len(publisher_sources.results)*100:.1f}%)")
    print(f"Total citations: {total_citations:,}")
    print("\nBy type:")
    for source_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source_type}: {count}")

# Analyze Elsevier
analyze_publisher_portfolio("P4310320595")
```

### Example 3: Regional comparison

```python
from openalex import Sources

def compare_regions():
    """Compare sources across different regions."""

    regions = {
        "North America": ["US", "CA", "MX"],
        "Europe": ["GB", "DE", "FR", "IT", "ES", "NL"],
        "Asia": ["CN", "JP", "KR", "IN", "SG"],
        "Latin America": ["BR", "AR", "CL", "MX", "CO"]
    }

    for region_name, countries in regions.items():
        # Get sources from region
        regional_sources = Sources().filter(country_code=countries).get()

        # Get OA sources from region
        regional_oa = (
            Sources()
            .filter(country_code=countries)
            .filter(is_oa=True)
            .get()
        )

        oa_percent = (regional_oa.meta.count / regional_sources.meta.count * 100
                     if regional_sources.meta.count > 0 else 0)

        print(f"\n{region_name}:")
        print(f"  Total sources: {regional_sources.meta.count:,}")
        print(f"  Open Access: {regional_oa.meta.count:,} ({oa_percent:.1f}%)")

compare_regions()
```

## Performance tips

Since there are ~249,000 sources:

1. **Pagination is manageable**: You can fetch all sources if needed
2. **Be specific for targeted queries**: Add filters to reduce result size
3. **Use group_by for analytics**: More efficient than fetching all records
4. **Consider source type**: Filter by type for more relevant results

```python
from openalex import Sources

# Example: Efficiently analyze journal landscape
def journal_landscape_summary():
    # Use group_by instead of fetching all sources
    by_type = Sources().group_by("type").get()
    by_oa_status = Sources().filter(type="journal").group_by("is_oa").get()

    print("Sources by type:")
    for group in by_type.group_by:
        print(f"  {group.key}: {group.count:,}")

    print("\nJournals by OA status:")
    for group in by_oa_status.group_by:
        status = "Open Access" if group.key else "Subscription"
        print(f"  {status}: {group.count:,}")
```
