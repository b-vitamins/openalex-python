# Search funders

The best way to search for funders is to use the `search` method, which searches the `display_name`, `alternate_titles`, and `description` fields:

```python
from openalex import Funders

# Search for funders related to health
health_search = Funders().search("health")

# Execute to get the first page of results
results = health_search.get()

print(f"Found {results.meta.count} funders matching 'health'")
for funder in results.results[:5]:
    print(f"- {funder.display_name}")
    if funder.alternate_titles:
        print(f"  Also known as: {', '.join(funder.alternate_titles[:2])}")
    if funder.description:
        print(f"  Description: {funder.description[:100]}...")
```

## How funder search works

The search checks multiple fields:

```python
# This searches display_name, alternate_titles, AND description
nih_results = Funders().search("NIH").get()

# This will find:
# - "National Institutes of Health" (via alternate title "NIH")
# - Any funder with "NIH" in the name
# - Funders mentioning "NIH" in their description

# Search is flexible with variations
science_results = Funders().search("science foundation").get()
# Finds "National Science Foundation", "Swiss National Science Foundation", etc.
```

💡 Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
# Search only in display_name
name_only = Funders().filter(
    display_name={"search": "florida"}
).get()

# Or use the search_filter method
name_search = Funders().search_filter(
    display_name="california"
).get()

# Search only in description
desc_search = Funders().filter(
    description={"search": "medical research"}
).get()

# Default search (same as .search() method)
default_search = Funders().filter(
    default={"search": "cancer research"}
).get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` only | `.search_filter(display_name="...")` |
| `description.search` | `description` only | `.filter(description={"search": "..."})` |
| `default.search` | `display_name`, `alternate_titles`, and `description` | `.filter(default={"search": "..."})` |

## Autocomplete funders

Create a fast type-ahead search experience:

```python
# Get autocomplete suggestions
suggestions = Funders().autocomplete("national sci")

# Returns fast, lightweight results
for funder in suggestions.results:
    print(f"{funder.display_name}")
    print(f"  Hint: {funder.hint}")  # Location hint (if available)
    print(f"  Works: {funder.works_count:,}")
    print(f"  Citations: {funder.cited_by_count:,}")
    if funder.external_id:  # ROR ID
        print(f"  ROR: {funder.external_id}")
```

Example output:
```
National Science Foundation
  Hint: United States
  Works: 264,303
  Citations: 6,705,777
  ROR: https://ror.org/021nxhr62

Swiss National Science Foundation
  Hint: Switzerland
  Works: 45,231
  Citations: 1,234,567
  ROR: https://ror.org/00yjd3n13
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
# Search for US health-related funders
us_health_funders = (
    Funders()
    .search("health")
    .filter(country_code="US")
    .get(per_page=20)
)

print(f"Found {us_health_funders.meta.count} US health funders")

# Search for high-impact funders
high_impact_search = (
    Funders()
    .search("Research Council")
    .filter_gt(summary_stats={"h_index": 200})
    .sort(cited_by_count="desc")
    .get()
)

# Search for major European funders
european_funders = (
    Funders()
    .search("European")
    .filter(continent="europe")
    .filter_gt(grants_count=100)
    .get()
)

# Find specialized funders
cancer_funders = (
    Funders()
    .search("cancer")
    .filter_gt(works_count=1000)
    .sort(works_count="desc")
    .get()
)
```

## Search strategies

### Finding government funders

```python
def find_government_funders(country_code=None):
    """Find government funding agencies."""
    
    # Common government funder terms
    gov_terms = ["National", "Ministry", "Department", "Federal", "Government"]
    
    # Build search query
    search_query = " OR ".join(gov_terms)
    query = Funders().search(search_query)
    
    if country_code:
        query = query.filter(country_code=country_code)
    
    results = query.get(per_page=50)
    
    print(f"Government funders{f' in {country_code}' if country_code else ''}:")
    for funder in results.results:
        print(f"  - {funder.display_name} ({funder.country_code})")
        print(f"    Grants: {funder.grants_count:,}")

# Examples
find_government_funders("US")
find_government_funders("GB")
```

### Finding foundation funders

```python
def find_foundations(focus_area=None):
    """Find private foundations and charities."""
    
    # Search for foundations
    query = Funders().search("Foundation OR Trust OR Charity")
    
    if focus_area:
        # Add focus area to search
        query = Funders().search(f"({focus_area}) AND (Foundation OR Trust)")
    
    # Exclude government funders
    foundations = query.get(per_page=30)
    
    print(f"Private foundations{f' focused on {focus_area}' if focus_area else ''}:")
    for funder in foundations.results:
        if "National" not in funder.display_name:  # Simple filter
            print(f"\n{funder.display_name} ({funder.country_code})")
            if funder.description:
                print(f"  {funder.description[:100]}...")
            print(f"  Works funded: {funder.works_count:,}")

# Examples
find_foundations()
find_foundations("medical")
find_foundations("education")
```

### International funder search

```python
def search_international_funders(search_term):
    """Search for funders across multiple languages/variations."""
    
    results = Funders().search(search_term).get(per_page=20)
    
    print(f"International results for '{search_term}':")
    
    # Group by country
    by_country = {}
    for funder in results.results:
        country = funder.country_code or "Unknown"
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(funder)
    
    # Display grouped results
    for country, funders in sorted(by_country.items()):
        print(f"\n{country}:")
        for f in funders:
            print(f"  - {f.display_name}")
            if f.alternate_titles:
                print(f"    AKA: {', '.join(f.alternate_titles[:2])}")

search_international_funders("Science")
search_international_funders("Research")
```

## Common search patterns

### Finding funding opportunities by field

```python
# Medical research funders
medical_funders = (
    Funders()
    .search("medical OR health OR biomedical")
    .filter_gt(grants_count=100)
    .sort(grants_count="desc")
    .get()
)

# Technology and engineering funders
tech_funders = (
    Funders()
    .search("technology OR engineering OR computer")
    .filter_gt(works_count=1000)
    .get()
)

# Environmental funders
env_funders = (
    Funders()
    .search("environment OR climate OR sustainability")
    .get()
)
```

### Regional funder discovery

```python
# Find funders in specific regions
def find_regional_funders(region, min_grants=50):
    if region == "EU":
        results = (
            Funders()
            .search("European OR EU")
            .filter_gt(grants_count=min_grants)
            .get()
        )
    elif region == "Asia-Pacific":
        results = (
            Funders()
            .filter(continent="asia")
            .filter_gt(grants_count=min_grants)
            .sort(cited_by_count="desc")
            .get()
        )
    else:
        results = (
            Funders()
            .filter(continent=region.lower())
            .filter_gt(grants_count=min_grants)
            .get()
        )
    
    return results

# Examples
eu_funders = find_regional_funders("EU")
apac_funders = find_regional_funders("Asia-Pacific")
```

## Search tips

1. **Use alternate names**: Many funders are known by acronyms (NIH, NSF, etc.)
2. **Search descriptions**: Useful for finding funders by mission/focus
3. **Combine with filters**: Narrow by country, size, or impact
4. **Consider language**: International funders may have non-English names
5. **Use boolean operators**: "cancer AND research" for more specific results

```python
# Example: Comprehensive funder search
def comprehensive_funder_search(keywords, country=None, min_impact=None):
    """Search with multiple strategies."""
    
    all_results = {}
    
    # Search each keyword
    for keyword in keywords:
        query = Funders().search(keyword)
        
        if country:
            query = query.filter(country_code=country)
        
        if min_impact:
            query = query.filter_gt(summary_stats={"h_index": min_impact})
        
        results = query.get(per_page=20)
        
        # Collect unique funders
        for funder in results.results:
            all_results[funder.id] = funder
    
    print(f"Found {len(all_results)} unique funders")
    
    # Sort by relevance (cited_by_count as proxy)
    sorted_funders = sorted(
        all_results.values(), 
        key=lambda f: f.cited_by_count, 
        reverse=True
    )
    
    for funder in sorted_funders[:10]:
        print(f"\n{funder.display_name} ({funder.country_code})")
        print(f"  Works: {funder.works_count:,}")
        print(f"  H-index: {funder.summary_stats.h_index if funder.summary_stats else 'N/A'}")

# Search for cancer research funders
comprehensive_funder_search(
    ["cancer", "oncology", "tumor"],
    country="US",
    min_impact=100
)
```
