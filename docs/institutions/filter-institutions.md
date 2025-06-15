# Filter institutions

You can filter institutions using the Python client:

```python
from openalex import Institutions

# Create a filtered query for institutions in Canada
canadian_institutions_query = Institutions().filter(country_code="CA")

# Execute the query to get the first page of results
results = canadian_institutions_query.get()

print(f"Total Canadian institutions: {results.meta.count}")
print(f"Showing first {len(results.results)} institutions")

# Show some examples
for inst in results.results[:5]:
    print(f"- {inst.display_name} ({inst.type})")
```

Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Institutions attribute filters

You can filter using these attributes of the [`Institution`](institution-object.md) object:

### Basic attribute filters

```python
from openalex import Institutions

# Filter by cited_by_count
highly_cited = Institutions().filter(cited_by_count=1000000).get()  # Exactly 1M
very_highly_cited = Institutions().filter_gt(cited_by_count=10000000).get()  # More than 10M

# Filter by works_count
large_institutions = Institutions().filter_gt(works_count=10000).get()  # More than 10k works
small_institutions = Institutions().filter_lt(works_count=100).get()  # Fewer than 100 works

# Filter by type
universities = Institutions().filter(type="education").get()
hospitals = Institutions().filter(type="healthcare").get()
companies = Institutions().filter(type="company").get()
government = Institutions().filter(type="government").get()

# Filter by country
us_institutions = Institutions().filter(country_code="US").get()
uk_institutions = Institutions().filter(country_code="GB").get()

# Multiple countries (OR operation)
european_institutions = Institutions().filter(
    country_code=["DE", "FR", "IT", "ES", "NL", "GB"]
).get()

# Filter by specific IDs
specific_ids = Institutions().filter(
    openalex=["I136199984", "I97018004"]
).get()

# Filter by ROR ID
ror_institution = Institutions().filter(ror="https://ror.org/00jmfr291").get()
```

### Lineage and hierarchy filters

```python
# Find all institutions in a lineage (includes children)
from openalex import Institutions

# Find all institutions in a lineage (includes children)
# For example, all University of California campuses
uc_system_id = "I2803209242"
uc_campuses = Institutions().filter(lineage=uc_system_id).get()
print(f"UC System has {uc_campuses.meta.count} entities")

# Filter by super system status
super_systems = Institutions().filter(is_super_system=True).get()
print(f"Found {super_systems.meta.count} super systems")

# Find child institutions of UC Berkeley
berkeley_children = Institutions().filter(lineage="I40120149").get()
print(f"UC Berkeley has {berkeley_children.meta.count} child institutions")
```

### Repository filters

```python
# Find institutions with repositories
from openalex import Institutions, not_

# Institutions that host at least one repository
has_repository = Institutions().filter(
    repositories={"id": not_(None)}
).get()

# Find institutions hosting specific repository
specific_repo = Institutions().filter(
    repositories={"id": "S4306402521"}  # Specific repository ID
).get()

# Find institutions with repositories in their lineage
repo_lineage = Institutions().filter(
    repositories={"host_organization_lineage": "I130238516"}
).get()
```

### Summary statistics filters

```python
# Filter by h-index
from openalex import Institutions

# Filter by h-index
high_impact = Institutions().filter_gt(summary_stats={"h_index": 500}).get()

# Filter by i10-index  
very_productive = Institutions().filter_gt(summary_stats={"i10_index": 10000}).get()

# Filter by 2-year mean citedness
high_quality = Institutions().filter_gt(
    summary_stats={"2yr_mean_citedness": 5.0}
).get()

# Combine metrics
elite_institutions = (
    Institutions()
    .filter_gt(summary_stats={"h_index": 300})
    .filter_gt(summary_stats={"i10_index": 50000})
    .filter_gt(works_count=50000)
    .get()
)
```

### Concept filters (deprecated)

```python
# Note: x_concepts will be deprecated soon, replaced by Topics
from openalex import Institutions

# Note: x_concepts will be deprecated soon, replaced by Topics
# Filter by concept
biology_focused = Institutions().filter(
    x_concepts={"id": "C86803240"}  # Biology concept
).get()
```

## Convenience filters

These filters aren't attributes of the Institution object, but they're handy:

### Geographic convenience filters

```python
# Filter by continent
from openalex import Institutions

# Filter by continent
north_american = Institutions().filter(continent="north_america").get()
european = Institutions().filter(continent="europe").get()
asian = Institutions().filter(continent="asia").get()

# Filter by Global South status
global_south = Institutions().filter(is_global_south=True).get()
global_north = Institutions().filter(is_global_south=False).get()

print(f"Global South institutions: {global_south.meta.count:,}")
print(f"Global North institutions: {global_north.meta.count:,}")
```

### Boolean filters

```python
# Has ROR ID (most institutions do)
from openalex import Institutions

# Has ROR ID (most institutions do)
with_ror = Institutions().filter(has_ror=True).get()
without_ror = Institutions().filter(has_ror=False).get()

print(f"With ROR: {with_ror.meta.count:,}")
print(f"Without ROR: {without_ror.meta.count:,}")
```

### Text search filters

```python
# Search in display names
from openalex import Institutions

# Search in display names
tech_search = Institutions().filter(
    display_name={"search": "technology"}
).get()

# Alternative: use search_filter
oxford_search = Institutions().search_filter(display_name="oxford").get()

# Default search (same as using .search() method)
default_search = Institutions().filter(
    default={"search": "medical center"}
).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
# Large US universities
from openalex import Institutions

# Large US universities
large_us_universities = (
    Institutions()
    .filter(country_code="US")
    .filter(type="education")
    .filter_gt(works_count=50000)
    .sort(cited_by_count="desc")
    .get()
)

# High-impact European institutions
european_elite = (
    Institutions()
    .filter(continent="europe")
    .filter_gt(summary_stats={"h_index": 400})
    .filter_gt(cited_by_count=5000000)
    .get()
)

# Global South research leaders
global_south_leaders = (
    Institutions()
    .filter(is_global_south=True)
    .filter(type="education")
    .filter_gt(works_count=10000)
    .sort(cited_by_count="desc")
    .get(per_page=50)
)
```

### NOT operations

```python
# Institutions NOT from the US
from openalex import Institutions

# Institutions NOT from the US
non_us = Institutions().filter_not(country_code="US").get()

# Non-university institutions
non_education = Institutions().filter_not(type="education").get()

# Institutions without repositories
no_repository = Institutions().filter(
    repositories={"id": None}
).get()
```

### Range queries

```python
# Mid-size institutions (1k-10k works)
from openalex import Institutions

# Mid-size institutions (1k-10k works)
mid_size = (
    Institutions()
    .filter_gt(works_count=1000)
    .filter_lt(works_count=10000)
    .get()
)

# Institutions with moderate citation impact
moderate_impact = (
    Institutions()
    .filter_gt(cited_by_count=100000)
    .filter_lt(cited_by_count=1000000)
    .get()
)
```

## Practical examples

### Example 1: Find peer institutions

```python
from openalex import Institutions

def find_peer_institutions(institution_id, radius=0.2):
    """Find institutions similar to a given institution."""
    # First get the reference institution
    ref_inst = Institutions()[institution_id]
    
    # Define peer criteria
    min_works = int(ref_inst.works_count * (1 - radius))
    max_works = int(ref_inst.works_count * (1 + radius))
    
    # Find similar institutions
    peers = (
        Institutions()
        .filter(type=ref_inst.type)
        .filter(country_code=ref_inst.country_code)
        .filter_gt(works_count=min_works)
        .filter_lt(works_count=max_works)
        .filter_not(openalex=institution_id)  # Exclude self
        .sort(works_count="desc")
        .get(per_page=20)
    )
    
    return peers

# Example usage
mit_peers = find_peer_institutions("I63966007")
print(f"Institutions similar to MIT:")
for inst in mit_peers.results:
    print(f"  {inst.display_name}: {inst.works_count:,} works")
```

### Example 2: Regional analysis

```python
# Compare research output by continent
from openalex import Institutions

# Compare research output by continent
def analyze_continents():
    continents = ["north_america", "europe", "asia", "south_america", 
                  "africa", "oceania"]
    
    for continent in continents:
        # Get top institutions
        top_inst = (
            Institutions()
            .filter(continent=continent)
            .filter(type="education")
            .sort(cited_by_count="desc")
            .get(per_page=5)
        )
        
        print(f"\nTop 5 universities in {continent.replace('_', ' ').title()}:")
        for i, inst in enumerate(top_inst.results, 1):
            print(f"  {i}. {inst.display_name} ({inst.country_code})")
            print(f"     Citations: {inst.cited_by_count:,}")

analyze_continents()
```

### Example 3: Institution networks

```python
# Find institutions with shared characteristics
from openalex import Institutions

# Find institutions with shared characteristics
def find_institution_network(country, min_collaborations=1000):
    """Find highly collaborative institutions in a country."""
    
    # Get institutions with many international works
    collaborative = (
        Institutions()
        .filter(country_code=country)
        .filter(type="education")
        .filter_gt(works_count=min_collaborations)
        .sort(cited_by_count="desc")
        .get(per_page=20)
    )
    
    print(f"Highly collaborative institutions in {country}:")
    for inst in collaborative.results:
        # Calculate international collaboration rate
        # (This is a simplified example)
        intl_rate = min(inst.cited_by_count / inst.works_count / 10, 100)
        print(f"  {inst.display_name}")
        print(f"    Works: {inst.works_count:,}")
        print(f"    Estimated international rate: {intl_rate:.1f}%")

find_institution_network("JP")  # Japan
```

## Performance tips

Since there are ~109,000 institutions:

1. **Pagination is feasible**: You can fetch all institutions if needed
2. **Be specific for large queries**: Add filters to reduce result size
3. **Use group_by for analytics**: More efficient than fetching all records
4. **Consider geography**: Filter by country/continent for regional analysis

```python
# Example: Efficiently analyze global institution distribution
from openalex import Institutions

# Example: Efficiently analyze global institution distribution
def global_institution_summary():
    # Use group_by instead of fetching all institutions
    by_type = Institutions().group_by("type").get()
    by_continent = Institutions().group_by("continent").get()
    
    print("Institutions by type:")
    for group in by_type.group_by:
        print(f"  {group.key}: {group.count:,}")
    
    print("\nInstitutions by continent:")
    for group in by_continent.group_by:
        print(f"  {group.key}: {group.count:,}")
```
