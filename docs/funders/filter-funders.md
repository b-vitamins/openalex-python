# Filter funders

You can filter funders using the Python client:

```python
from openalex import Funders

# Create a filtered query for funders in Canada
canadian_funders_query = Funders().filter(country_code="CA")

# Execute the query to get the first page of results
results = canadian_funders_query.get()

print(f"Total Canadian funders: {results.meta.count}")
print(f"Showing first {len(results.results)} funders")

# Show some examples
for funder in results.results[:5]:
    print(f"- {funder.display_name}")
    print(f"  Grants: {funder.grants_count:,}")
```

💡 Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Funders attribute filters

You can filter using these attributes of the [`Funder`](funder-object.md) object:

### Basic attribute filters

```python
# Filter by cited_by_count
highly_cited = Funders().filter(cited_by_count=1000000).get()  # Exactly 1M
very_highly_cited = Funders().filter_gt(cited_by_count=10000000).get()  # More than 10M

# Filter by works_count
large_funders = Funders().filter_gt(works_count=10000).get()  # More than 10k works
small_funders = Funders().filter_lt(works_count=100).get()  # Fewer than 100 works

# Filter by grants_count
major_funders = Funders().filter_gt(grants_count=1000).get()  # More than 1k grants
minor_funders = Funders().filter_lt(grants_count=10).get()  # Fewer than 10 grants

# Filter by country
us_funders = Funders().filter(country_code="US").get()
uk_funders = Funders().filter(country_code="GB").get()

# Multiple countries (OR operation)
european_funders = Funders().filter(
    country_code=["DE", "FR", "GB", "NL", "CH", "SE"]
).get()

# Filter by specific IDs
specific_ids = Funders().filter(
    openalex=["F4320332161", "F4320306076"]
).get()

# Filter by ROR ID
ror_funder = Funders().filter(ror="https://ror.org/021nxhr62").get()

# Filter by Wikidata ID
wiki_funder = Funders().filter(wikidata="Q390551").get()
```

### Summary statistics filters

```python
# Filter by h-index
high_h_index = Funders().filter_gt(summary_stats={"h_index": 500}).get()

# Filter by i10-index
productive = Funders().filter_gt(summary_stats={"i10_index": 50000}).get()

# Filter by 2-year mean citedness
high_impact = Funders().filter_gt(
    summary_stats={"2yr_mean_citedness": 5.0}
).get()

# Combine metrics
elite_funders = (
    Funders()
    .filter_gt(summary_stats={"h_index": 400})
    .filter_gt(summary_stats={"i10_index": 100000})
    .filter_gt(works_count=50000)
    .get()
)
```

## Convenience filters

These filters aren't attributes of the Funder object, but they're handy:

### Geographic convenience filters

```python
# Filter by continent
north_american = Funders().filter(continent="north_america").get()
european = Funders().filter(continent="europe").get()
asian = Funders().filter(continent="asia").get()

# Filter by Global South status
global_south = Funders().filter(is_global_south=True).get()
global_north = Funders().filter(is_global_south=False).get()

print(f"Global South funders: {global_south.meta.count:,}")
print(f"Global North funders: {global_north.meta.count:,}")
```

### Text search filters

```python
# Search in display names
health_search = Funders().filter(
    display_name={"search": "health"}
).get()

# Search in descriptions
medical_desc = Funders().filter(
    description={"search": "medical research"}
).get()

# Alternative: use search_filter
science_search = Funders().search_filter(display_name="science").get()

# Default search (searches display_name, alternate_titles, and description)
default_search = Funders().filter(
    default={"search": "cancer research"}
).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
# Large US government funders
us_gov_funders = (
    Funders()
    .filter(country_code="US")
    .filter_gt(grants_count=1000)
    .filter(display_name={"search": "national"})
    .sort(cited_by_count="desc")
    .get()
)

# High-impact European funders
european_elite = (
    Funders()
    .filter(continent="europe")
    .filter_gt(summary_stats={"h_index": 300})
    .filter_gt(cited_by_count=1000000)
    .get()
)

# Global South research funders
global_south_research = (
    Funders()
    .filter(is_global_south=True)
    .filter_gt(works_count=1000)
    .sort(cited_by_count="desc")
    .get(per_page=50)
)
```

### NOT operations

```python
# Funders NOT from the US
non_us = Funders().filter_not(country_code="US").get()

# Funders without many grants
low_grant_volume = Funders().filter_not(
    grants_count={"gte": 100}
).get()
```

### Range queries

```python
# Mid-size funders (100-1000 grants)
mid_size = (
    Funders()
    .filter_gt(grants_count=100)
    .filter_lt(grants_count=1000)
    .get()
)

# Funders with moderate citation impact
moderate_impact = (
    Funders()
    .filter_gt(cited_by_count=100000)
    .filter_lt(cited_by_count=1000000)
    .get()
)
```

## Practical examples

### Example 1: Find peer funders

```python
def find_peer_funders(funder_id, radius=0.2):
    """Find funders similar to a given funder."""
    # First get the reference funder
    ref_funder = Funders()[funder_id]
    
    # Define peer criteria
    min_grants = int(ref_funder.grants_count * (1 - radius))
    max_grants = int(ref_funder.grants_count * (1 + radius))
    
    # Find similar funders
    peers = (
        Funders()
        .filter(country_code=ref_funder.country_code)
        .filter_gt(grants_count=min_grants)
        .filter_lt(grants_count=max_grants)
        .filter_not(openalex=funder_id)  # Exclude self
        .sort(grants_count="desc")
        .get(per_page=20)
    )
    
    return peers

# Example usage
nsf_peers = find_peer_funders("F4320306076")
print("Funders similar to NSF:")
for funder in nsf_peers.results:
    print(f"  {funder.display_name}: {funder.grants_count:,} grants")
```

### Example 2: Regional funding analysis

```python
def analyze_regional_funding():
    """Compare funding landscapes across regions."""
    
    regions = {
        "North America": ["US", "CA", "MX"],
        "Europe": ["GB", "DE", "FR", "IT", "ES", "NL", "CH"],
        "Asia": ["CN", "JP", "KR", "IN", "SG"],
        "Latin America": ["BR", "AR", "CL", "MX", "CO"]
    }
    
    for region_name, countries in regions.items():
        # Get funders from region
        regional_funders = Funders().filter(country_code=countries).get()
        
        # Get high-impact funders from region
        high_impact = (
            Funders()
            .filter(country_code=countries)
            .filter_gt(summary_stats={"h_index": 100})
            .get()
        )
        
        impact_percent = (high_impact.meta.count / regional_funders.meta.count * 100 
                         if regional_funders.meta.count > 0 else 0)
        
        print(f"\n{region_name}:")
        print(f"  Total funders: {regional_funders.meta.count:,}")
        print(f"  High-impact (h>100): {high_impact.meta.count:,} ({impact_percent:.1f}%)")

analyze_regional_funding()
```

### Example 3: Funding specialization

```python
def find_specialized_funders(search_term, min_focus_score=0.8):
    """Find funders specialized in a particular area."""
    
    # Search for funders mentioning the term
    specialized = (
        Funders()
        .search(search_term)
        .filter_gt(works_count=100)  # Active funders only
        .get(per_page=20)
    )
    
    print(f"Funders specializing in '{search_term}':")
    for funder in specialized.results:
        # Check if alternate titles also mention the term
        alt_mentions = sum(1 for alt in (funder.alternate_titles or []) 
                           if search_term.lower() in alt.lower())
        
        if funder.description and search_term.lower() in funder.description.lower():
            print(f"\n{funder.display_name} ({funder.country_code})")
            print(f"  Description: {funder.description[:100]}...")
            print(f"  Works funded: {funder.works_count:,}")
            if funder.summary_stats:
                print(f"  H-index: {funder.summary_stats.h_index}")

find_specialized_funders("cancer")
find_specialized_funders("climate")
```

### Example 4: Multi-role organizations

```python
def find_multi_role_organizations():
    """Find organizations that are funders, institutions, and/or publishers."""
    
    # Get funders with high activity
    active_funders = (
        Funders()
        .filter_gt(works_count=1000)
        .get(per_page=200)
    )
    
    multi_role_count = 0
    examples = []
    
    for funder in active_funders.results:
        if funder.roles and len(funder.roles) > 1:
            multi_role_count += 1
            if len(examples) < 5:  # Collect first 5 examples
                examples.append(funder)
    
    print(f"Found {multi_role_count} multi-role organizations")
    print("\nExamples:")
    
    for org in examples:
        print(f"\n{org.display_name}")
        for role in org.roles:
            print(f"  - {role.role}: {role.works_count:,} works")

find_multi_role_organizations()
```

## Performance tips

Since there are only ~32,000 funders:

1. **Fetching all is feasible**: You can get all funders in ~160 API calls
2. **Complex filters are fast**: Don't hesitate to use multiple filters
3. **Use group_by for analytics**: Still more efficient than fetching all
4. **Consider caching**: The funder list changes slowly

```python
# Example: Efficiently analyze global funding distribution
def global_funding_summary():
    # Use group_by instead of fetching all funders
    by_country = Funders().group_by("country_code").get()
    by_continent = Funders().group_by("continent").get()
    
    print("Funders by continent:")
    for group in by_continent.group_by:
        print(f"  {group.key}: {group.count:,}")
    
    print("\nTop 10 countries by funder count:")
    for group in by_country.group_by[:10]:
        print(f"  {group.key}: {group.count:,}")
```
