# Get lists of funders

You can get lists of funders using the Python client:

```python
from openalex import Funders

# Create a query for all funders (no filters applied)
all_funders_query = Funders()

# Execute the query to get the FIRST PAGE of results
first_page = all_funders_query.get()

# Note: With only ~32,000 funders, fetching all is very feasible
print(f"Total funders: {first_page.meta.count:,}")  # ~32,000
print(f"Funders in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Funder objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
from openalex import Funders

# Each result shows funder information
first_page = Funders().get()
for funder in first_page.results[:5]:  # First 5 funders
    print(f"\n{funder.display_name}")
    print(f"  Country: {funder.country_code}")
    print(f"  Grants: {funder.grants_count:,}")
    print(f"  Funded works: {funder.works_count:,}")
    print(f"  Citations: {funder.cited_by_count:,}")
    if funder.description:
        print(f"  Description: {funder.description}")
```

## Page and sort funders

You can control pagination and sorting:

```python
from openalex import Funders

# Get a specific page with custom page size
page2 = Funders().get(per_page=50, page=2)
# This returns funders 51-100

# Sort by different fields
# Largest funders by grant count
most_grants = Funders().sort(grants_count="desc").get()

# Most cited funders
most_cited = Funders().sort(cited_by_count="desc").get()

# Alphabetical by name
alphabetical = Funders().sort(display_name="asc").get()

# Get ALL funders (very feasible with ~32,000)
# This will make about 160 API calls at 200 per page
# Avoid exceeding the 10k limit by stopping early
all_funders = []
page_count = 0
for page in Funders().paginate(per_page=200):
    page_count += 1
    if page_count > 5:  # Stop after 1,000 funders
        break
    all_funders.extend(page.results)
print(f"Fetched {len(all_funders)} funders")
```

## Sample funders

Get a random sample of funders:

```python
from openalex import Funders

# Get 10 random funders
random_sample = Funders().sample(10).get(per_page=10)

# Use a seed for reproducible random sampling
reproducible_sample = Funders().sample(10, seed=42).get(per_page=10)

# Sample from filtered results
us_funder_sample = (
    Funders()
    .filter(country_code="US")
    .sample(5)
    .get()
)
```

## Select fields

Limit the fields returned to improve performance:

```python
from openalex import Funders

# Request only specific fields
minimal_funders = Funders().select([
    "id", 
    "display_name",
    "alternate_titles",
    "country_code",
    "grants_count"
]).get()

# This reduces response size significantly
for funder in minimal_funders.results:
    print(f"{funder.display_name} ({funder.country_code})")
    print(funder.homepage_url)  # None - not selected
```

## Practical examples

### Example: Analyze funding landscape

```python
# Get major funding agencies
from openalex import Funders
major_funders = (
    Funders()
    .filter_gt(grants_count=1000)
    .sort(grants_count="desc")
    .get(per_page=20)
)

print("Top 20 funding agencies by grant count:")
for i, funder in enumerate(major_funders.results, 1):
    print(f"{i}. {funder.display_name} ({funder.country_code})")
    print(f"   Grants: {funder.grants_count:,}")
    print(f"   Funded works: {funder.works_count:,}")
    print(f"   Total citations: {funder.cited_by_count:,}")
```

### Example: Geographic distribution

```python
# Analyze funders by region
from openalex import Funders
def analyze_funding_by_region():
    regions = {
        "North America": ["US", "CA"],
        "Europe": ["GB", "DE", "FR", "NL", "CH", "SE", "NO", "DK", "FI"],
        "Asia": ["CN", "JP", "KR", "IN", "SG", "TW"],
        "Oceania": ["AU", "NZ"]
    }
    
    for region, countries in regions.items():
        regional_funders = Funders().filter(country_code=countries).get()
        
        # Get top funder in region
        top_funder = (
            Funders()
            .filter(country_code=countries)
            .sort(cited_by_count="desc")
            .get(per_page=1)
        )
        
        print(f"\n{region}:")
        print(f"  Total funders: {regional_funders.meta.count:,}")
        if top_funder.results:
            print(f"  Top funder: {top_funder.results[0].display_name}")
            print(f"  Citations: {top_funder.results[0].cited_by_count:,}")

analyze_funding_by_region()
```

### Example: Funding impact analysis

```python
# Find high-impact funders
from openalex import Funders
def find_high_impact_funders(min_h_index=200):
    """Find funders supporting high-impact research."""
    
    high_impact = (
        Funders()
        .filter_gt(summary_stats={"h_index": min_h_index})
        .sort(**{"summary_stats.h_index": "desc"})
        .get(per_page=20)
    )
    
    print(f"Funders with h-index > {min_h_index}:")
    for funder in high_impact.results:
        h_index = funder.summary_stats.h_index if funder.summary_stats else "N/A"
        mean_cite = funder.summary_stats["2yr_mean_citedness"] if funder.summary_stats else "N/A"
        
        print(f"\n{funder.display_name}")
        print(f"  H-index: {h_index}")
        print(f"  Mean citedness: {mean_cite:.2f}" if isinstance(mean_cite, float) else f"  Mean citedness: {mean_cite}")
        print(f"  Works funded: {funder.works_count:,}")

find_high_impact_funders(min_h_index=300)
```

Continue on to learn how you can [filter](filter-funders.md) and [search](search-funders.md) lists of funders.
