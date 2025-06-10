# Source object

When you fetch a source using the Python client, you get a `Source` object with all of OpenAlex's data about that source. Here's how to access the various properties:

```python
from openalex import Sources

# Get a specific source
source = Sources()["S137773608"]

# The source object has all the data as Python attributes
print(type(source))  # <class 'openalex.models.source.Source'>
```

## Basic properties

```python
# Identifiers
print(source.id)  # "https://openalex.org/S137773608"
print(source.issn_l)  # "0028-0836" (canonical ISSN)
print(source.issn)  # ["1476-4687", "0028-0836"] (all ISSNs)
print(source.display_name)  # "Nature"

# Alternative names
print(source.abbreviated_title)  # "Nature"
print(source.alternate_titles)  # ["Nat"]

# Basic information
print(source.type)  # "journal"
print(source.country_code)  # "GB"
print(source.homepage_url)  # "https://www.nature.com/"

# Publisher information
print(source.host_organization)  # "https://openalex.org/P4310319965"
print(source.host_organization_name)  # "Springer Nature"
print(source.host_organization_lineage)  # List of parent org IDs
print(source.publisher)  # "Nature Portfolio"

# Scale metrics
print(source.works_count)  # 185,779
print(source.cited_by_count)  # 50,233,439

# Open Access status
print(source.is_oa)  # False
print(source.is_in_doaj)  # False
print(source.is_core)  # True (Leiden Ranking core source)

# Dates
print(source.created_date)  # "2017-08-08"
print(source.updated_date)  # "2024-01-02T00:27:23.088909"
```

## Article Processing Charges (APCs)

```python
# APC information from DOAJ
if source.apc_prices:
    print(f"APCs offered in {len(source.apc_prices)} currencies:")
    for apc in source.apc_prices:
        print(f"  {apc.currency}: {apc.price}")

# APC in USD (converted if necessary)
if source.apc_usd is not None:
    print(f"APC in USD: ${source.apc_usd:,}")
else:
    print("No APC information available")
```

## Summary statistics

```python
stats = source.summary_stats
if stats:
    # Impact factor (2-year mean citedness)
    print(f"Impact Factor: {stats['2yr_mean_citedness']:.3f}")
    
    # H-index for the source
    print(f"H-index: {stats.h_index}")
    
    # i10-index (papers with 10+ citations)
    print(f"i10-index: {stats.i10_index:,}")
    
    # Interpret the metrics
    if stats['2yr_mean_citedness'] > 10:
        print("This is a high-impact journal")
```

## Publication trends

```python
# Track output over the last 10 years
print("Publication trends:")
for count in source.counts_by_year[:5]:  # Last 5 years
    print(f"  {count.year}: {count.works_count:,} works, "
          f"{count.cited_by_count:,} citations")

# Analyze trends
if len(source.counts_by_year) >= 2:
    recent = source.counts_by_year[0]
    previous = source.counts_by_year[1]
    growth = ((recent.works_count - previous.works_count) / 
              previous.works_count * 100)
    print(f"Year-over-year growth: {growth:+.1f}%")
```

## Society information

```python
# Societies that sponsor this source
if source.societies:
    print(f"Published on behalf of {len(source.societies)} society(ies):")
    for society in source.societies:
        print(f"  - {society.organization}")
        if society.url:
            print(f"    URL: {society.url}")
```

## External identifiers

```python
ids = source.ids
print(f"OpenAlex: {ids.openalex}")
print(f"ISSN-L: {ids.issn_l}")
print(f"All ISSNs: {ids.issn}")
if ids.mag:
    print(f"MAG: {ids.mag}")
if ids.fatcat:
    print(f"Fatcat: {ids.fatcat}")
if ids.wikidata:
    print(f"Wikidata: {ids.wikidata}")
```

## Concepts (deprecated)

```python
# Note: x_concepts will be deprecated soon, replaced by Topics
if source.x_concepts:
    print("Top research areas:")
    for concept in source.x_concepts[:5]:
        print(f"  {concept.display_name}: {concept.score:.1f}")
```

## Works API URL

```python
# URL to get all works from this source
print(f"Works URL: {source.works_api_url}")

# To actually fetch works using the client:
from openalex import Works

# Get recent works from this source
source_works = (
    Works()
    .filter(primary_location={"source": {"id": source.id}})
    .filter(publication_year=2023)
    .sort(publication_date="desc")
    .get()
)

print(f"Recent works in {source.display_name}:")
for work in source_works.results[:5]:
    print(f"  - {work.title}")
```

## Working with source data

### Analyze journal quality

```python
def analyze_journal_quality(source_id):
    """Comprehensive quality analysis of a journal."""
    source = Sources()[source_id]
    
    print(f"Journal Quality Analysis: {source.display_name}")
    print("=" * 50)
    
    # Basic info
    print(f"Type: {source.type}")
    print(f"Publisher: {source.host_organization_name}")
    print(f"Country: {source.country_code}")
    print(f"Open Access: {source.is_oa}")
    
    # Impact metrics
    if source.summary_stats:
        stats = source.summary_stats
        print(f"\nImpact Metrics:")
        print(f"  Impact Factor: {stats['2yr_mean_citedness']:.3f}")
        print(f"  H-index: {stats.h_index}")
        print(f"  Total citations: {source.cited_by_count:,}")
        
        # Quality tier
        if stats['2yr_mean_citedness'] > 20:
            tier = "Elite"
        elif stats['2yr_mean_citedness'] > 10:
            tier = "High Impact"
        elif stats['2yr_mean_citedness'] > 5:
            tier = "Good"
        elif stats['2yr_mean_citedness'] > 2:
            tier = "Average"
        else:
            tier = "Developing"
        print(f"  Quality Tier: {tier}")
    
    # Publishing volume
    print(f"\nPublishing Volume:")
    print(f"  Total works: {source.works_count:,}")
    if source.counts_by_year:
        recent_avg = sum(c.works_count for c in source.counts_by_year[:3]) / 3
        print(f"  Recent average: {recent_avg:.0f} works/year")
    
    # APC information
    if source.apc_usd is not None:
        print(f"\nArticle Processing Charge: ${source.apc_usd:,}")
        if source.is_oa and source.apc_usd == 0:
            print("  (Diamond Open Access)")

# Example usage
analyze_journal_quality("S137773608")  # Nature
```

### Compare similar sources

```python
def compare_sources(source_ids):
    """Compare multiple sources side by side."""
    sources = []
    for sid in source_ids:
        sources.append(Sources()[sid])
    
    print("Source Comparison")
    print("-" * 100)
    print(f"{'Source':<40} {'Type':<12} {'IF':>6} {'Works':>8} {'OA':<5} {'APC':>8}")
    print("-" * 100)
    
    for src in sources:
        impact_factor = "N/A"
        if src.summary_stats and '2yr_mean_citedness' in src.summary_stats:
            impact_factor = f"{src.summary_stats['2yr_mean_citedness']:.2f}"
        
        apc = "N/A"
        if src.apc_usd is not None:
            apc = f"${src.apc_usd:,}"
        elif src.is_oa:
            apc = "$0"
        
        print(f"{src.display_name[:39]:<40} "
              f"{src.type:<12} "
              f"{impact_factor:>6} "
              f"{src.works_count:>8,} "
              f"{'Yes' if src.is_oa else 'No':<5} "
              f"{apc:>8}")

# Compare top science journals
compare_sources([
    "S137773608",  # Nature
    "S3880285",    # Science
    "S125754415",  # Cell
    "S140251998",  # PNAS
])
```

### Find related sources

```python
def find_related_sources(source_id):
    """Find sources similar to a given source."""
    source = Sources()[source_id]
    
    # Find sources from same publisher
    same_publisher = (
        Sources()
        .filter(host_organization=source.host_organization)
        .filter(type=source.type)
        .filter_not(openalex=source_id)
        .sort(cited_by_count="desc")
        .get(per_page=10)
    )
    
    print(f"Sources related to {source.display_name}")
    print(f"\nFrom same publisher ({source.host_organization_name}):")
    for src in same_publisher.results[:5]:
        print(f"  - {src.display_name}")
    
    # Find sources with similar impact
    if source.summary_stats and '2yr_mean_citedness' in source.summary_stats:
        impact = source.summary_stats['2yr_mean_citedness']
        min_impact = impact * 0.7
        max_impact = impact * 1.3
        
        similar_impact = (
            Sources()
            .filter(type="journal")
            .filter_gt(summary_stats={"2yr_mean_citedness": min_impact})
            .filter_lt(summary_stats={"2yr_mean_citedness": max_impact})
            .filter_not(openalex=source_id)
            .sort(summary_stats={"2yr_mean_citedness": "desc"})
            .get(per_page=10)
        )
        
        print(f"\nWith similar impact factor ({impact:.1f}):")
        for src in similar_impact.results[:5]:
            src_if = src.summary_stats['2yr_mean_citedness']
            print(f"  - {src.display_name} (IF: {src_if:.1f})")

# Find sources related to Nature
find_related_sources("S137773608")
```

## Handling missing data

Many fields can be None or empty:

```python
# Safe access patterns
if source.homepage_url:
    print(f"Homepage: {source.homepage_url}")
else:
    print("No homepage listed")

# Handle missing statistics
if source.summary_stats and '2yr_mean_citedness' in source.summary_stats:
    print(f"Impact Factor: {source.summary_stats['2yr_mean_citedness']:.3f}")
else:
    print("Impact Factor not calculated")

# Check for society sponsorship
if not source.societies:
    print("No society sponsorship listed")

# APC might not be available
if source.apc_usd is not None:
    print(f"APC: ${source.apc_usd}")
elif source.is_oa:
    print("Open Access (no APC information)")
else:
    print("Subscription journal")

# Some sources might not have ISSNs
if source.issn:
    print(f"ISSNs: {', '.join(source.issn)}")
else:
    print("No ISSN available")
```

## The DehydratedSource object

When sources appear in other objects (like in work locations), you get a simplified version:

```python
# Get a work to see dehydrated sources
from openalex import Works
work = Works()["W2741809807"]

# Access dehydrated source in primary location
if work.primary_location and work.primary_location.source:
    source = work.primary_location.source
    # Only these fields are available in dehydrated version:
    print(source.id)
    print(source.display_name)
    print(source.type)
    print(source.is_oa)
    print(source.is_in_doaj)
    print(source.is_core)
    print(source.host_organization)
    print(source.host_organization_name)
    print(source.issn_l)
    print(source.issn)
    
    # To get full details, fetch the complete source:
    full_source = Sources()[source.id]
    print(f"Full works count: {full_source.works_count}")
```
