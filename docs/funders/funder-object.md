# Funder object

When you fetch a funder using the Python client, you get a `Funder` object with all of OpenAlex's data about that funder. Here's how to access the various properties:

```python
from openalex import Funders

# Get a specific funder
funder = Funders()["F4320332161"]

# The funder object has all the data as Python attributes
print(type(funder))  # <class 'openalex.models.funder.Funder'>
```

## Basic properties

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

# Identifiers
print(funder.id)  # "https://openalex.org/F4320332161"
print(funder.display_name)  # "National Institutes of Health"

# Alternative names
print(funder.alternate_titles)  # ["US National Institutes of Health", "Institutos Nacionales de la Salud", "NIH"]

# Basic information
print(funder.country_code)  # "US"
print(funder.description)  # "medical research organization in the United States"
print(funder.homepage_url)  # "http://www.nih.gov/"

# Scale metrics
print(funder.grants_count)  # 7,109
print(funder.works_count)  # 260,210
print(funder.cited_by_count)  # 7,823,467

# Dates
print(funder.created_date)  # "2023-02-13"
print(funder.updated_date)  # "2023-04-21T16:54:19.012138"
```

## Images

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

# Funder logo/seal
if funder.image_url:
    print(f"Logo URL: {funder.image_url}")
    
if funder.image_thumbnail_url:
    print(f"Thumbnail: {funder.image_thumbnail_url}")
    # Usually includes width parameter you can adjust
```

## Multiple roles

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

# An organization can be a funder, institution, and/or publisher
print(f"This organization has {len(funder.roles)} roles:")

for role in funder.roles:
    print(f"\n{role.role.capitalize()}:")
    print(f"  ID: {role.id}")
    print(f"  Works count: {role.works_count:,}")

# Example: A university might be:
# - funder (funding research)
# - institution (employing researchers)
# - publisher (university press)
```

## Summary statistics

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

stats = funder.summary_stats
if stats:
    print(f"H-index: {stats.h_index}")  # e.g., 985
    print(f"i10-index: {stats.i10_index:,}")  # e.g., 176,682
    print(
        f"2-year mean citedness: {stats.two_year_mean_citedness:.2f}"
    )
    
    # These help assess funding impact
    if stats.h_index > 500:
        print("This funder supports very high-impact research")
```

## Funding trends

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

# Track funding output over the last 10 years
print("Funding trends:")
for count in funder.counts_by_year[:5]:  # Last 5 years
    print(f"  {count.year}: {count.works_count:,} works, "
          f"{count.cited_by_count:,} citations")

# Analyze trends
if len(funder.counts_by_year) >= 2:
    recent = funder.counts_by_year[0]
    previous = funder.counts_by_year[1]
    growth = ((recent.works_count - previous.works_count) / 
              previous.works_count * 100)
    print(f"Year-over-year growth: {growth:+.1f}%")
```

## External identifiers

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

ids = funder.ids
print(f"OpenAlex: {ids.openalex}")
if ids.ror:
    print(f"ROR: {ids.ror}")
if ids.crossref:
    print(f"Crossref: {ids.crossref}")
if ids.doi:
    print(f"DOI: {ids.doi}")
if ids.wikidata:
    print(f"Wikidata: {ids.wikidata}")
```

## Working with funder data

### Find funded works

```python
from openalex import Funders, Works

funder = Funders()["F4320332161"]

def get_funded_works(funder_id, year=None):
    """Get works funded by a specific funder."""
    
    # Build query for funded works
    query = Works().filter(grants={"funder": funder_id})
    
    if year:
        query = query.filter(publication_year=year)
    
    # Get recent works
    recent_works = query.sort(publication_date="desc").get()
    
    print(f"Recent works funded by {funder.display_name}:")
    for work in recent_works.results[:10]:
        print(f"\n{work.title}")
        print(f"  Published: {work.publication_date}")
        
        # Show grant information
        for grant in work.grants:
            grant_funder = grant.get("funder") if isinstance(grant, dict) else grant.funder
            award_id = grant.get("award_id") if isinstance(grant, dict) else grant.award_id
            if grant_funder == funder_id and award_id:
                print(f"  Grant: {award_id}")

# Example usage
get_funded_works(funder.id, year=2023)
```

### Analyze funding impact

```python
from openalex import Funders

def analyze_funder_impact(funder_id):
    """Comprehensive impact analysis of a funder."""
    funder = Funders()[funder_id]
    
    print(f"Funding Impact Analysis: {funder.display_name}")
    print("=" * 50)
    
    # Basic metrics
    print(f"\nBasic Metrics:")
    print(f"  Grants: {funder.grants_count:,}")
    print(f"  Funded works: {funder.works_count:,}")
    print(f"  Total citations: {funder.cited_by_count:,}")
    
    # Impact metrics
    if funder.summary_stats:
        stats = funder.summary_stats
        print(f"\nImpact Metrics:")
        print(f"  H-index: {stats.h_index}")
        print(f"  i10-index: {stats.i10_index:,}")
        print(f"  Mean citedness: {stats.two_year_mean_citedness:.2f}")
        
        # Impact per dollar (if grant count available)
        if funder.grants_count > 0:
            citations_per_grant = funder.cited_by_count / funder.grants_count
            print(f"  Citations per grant: {citations_per_grant:.0f}")
    
    # Trend analysis
    if funder.counts_by_year and len(funder.counts_by_year) >= 5:
        recent_years = funder.counts_by_year[:5]
        recent_works = sum(y.works_count for y in recent_years)
        recent_citations = sum(y.cited_by_count for y in recent_years)
        
        print(f"\nRecent Performance (last 5 years):")
        print(f"  Works: {recent_works:,}")
        print(f"  Citations: {recent_citations:,}")
        print(f"  Avg citations/work: {recent_citations/recent_works:.1f}")

analyze_funder_impact("F4320332161")  # NIH
```

### Compare funders

```python
from openalex import Funders

def compare_funders(funder_ids):
    """Compare multiple funders side by side."""
    funders = []
    for fid in funder_ids:
        funders.append(Funders()[fid])
    
    print("Funder Comparison")
    print("-" * 80)
    print(f"{'Funder':<40} {'Country':<8} {'Grants':>10} {'Works':>10} {'H-index':>10}")
    print("-" * 80)
    
    for fund in funders:
        h_index = fund.summary_stats.h_index if fund.summary_stats else "N/A"
        print(f"{fund.display_name[:39]:<40} "
              f"{fund.country_code:<8} "
              f"{fund.grants_count:>10,} "
              f"{fund.works_count:>10,} "
              f"{h_index:>10}")

# Compare major funders
compare_funders([
    "F4320332161",  # NIH
    "F4320306076",  # NSF
    "F4320308380",  # Wellcome Trust
    "F4320321001",  # NSFC China
])
```

### Find related funders

```python
from openalex import Funders

def find_related_funders(funder_id):
    """Find funders with similar characteristics or focus."""
    source_funder = Funders()[funder_id]
    
    # Search for funders with similar names/descriptions
    if source_funder.description:
        # Extract key terms from description
        key_terms = source_funder.description.split()[:3]
        search_query = " ".join(key_terms)
        
        similar = (
            Funders()
            .search(search_query)
            .filter_not(openalex=funder_id)
            .get(per_page=10)
        )
        
        print(f"Funders similar to {source_funder.display_name}:")
        for fund in similar.results:
            print(f"  - {fund.display_name} ({fund.country_code})")
            if fund.description:
                print(f"    {fund.description}")
    
    # Find funders in same country with similar scale
    peers = (
        Funders()
        .filter(country_code=source_funder.country_code)
        .filter_gt(grants_count=source_funder.grants_count * 0.5)
        .filter_lt(grants_count=source_funder.grants_count * 2.0)
        .filter_not(openalex=funder_id)
        .get()
    )
    
    print(f"\nPeer funders in {source_funder.country_code}:")
    for fund in peers.results[:5]:
        print(f"  - {fund.display_name}: {fund.grants_count:,} grants")

# Find funders related to NSF
find_related_funders("F4320306076")
```

## Handling missing data

Many fields can be None or empty:

```python
# Setup
from openalex import Funders
funder = Funders()["F4320332161"]

# Safe access patterns
if funder.homepage_url:
    print(f"Website: {funder.homepage_url}")
else:
    print("No website listed")

# Handle missing statistics
if funder.summary_stats and funder.summary_stats.h_index is not None:
    print(f"H-index: {funder.summary_stats.h_index}")
else:
    print("H-index not calculated")

# Check for alternate titles
if not funder.alternate_titles:
    print("No alternate names listed")

# Description might be missing
if funder.description:
    print(f"Description: {funder.description}")
else:
    print("No description available")

# Some funders might not have grant counts
if funder.grants_count is not None:
    print(f"Grants: {funder.grants_count:,}")
else:
    print("Grant count not available")
```

## The DehydratedFunder object

When funders appear in other objects (like in work grants), you get a simplified version:

```python
# Get a work to see dehydrated funders
from openalex import Funders, Works
work = Works()["W2741809807"]

# Access dehydrated funders in grants
if work.grants:
    for grant in work.grants:
        if grant.funder:
            # Only these fields are available in dehydrated version:
            print(grant.funder.id)
            print(grant.funder.display_name)
            
            # To get full details, fetch the complete funder:
            full_funder = Funders()[grant.funder.id]
            print(f"Full grant count: {full_funder.grants_count}")
```
