# Search institutions

The best way to search for institutions is to use the `search` method, which searches the `display_name`, `display_name_alternatives`, and `display_name_acronyms` fields:

```python
from openalex import Institutions

# Search for institutions by name
sdsu_search = Institutions().search("san diego state university")

# Execute to get the first page of results
results = sdsu_search.get()

print(f"Found {results.meta.count} institutions matching 'san diego state university'")
for institution in results.results[:5]:
    print(f"- {institution.display_name}")
    print(f"  Location: {institution.geo.city}, {institution.geo.country}")
    print(f"  Type: {institution.type}")
```

## How institution search works

The search checks multiple name fields:

```python
# This searches display_name, display_name_alternatives, and display_name_acronyms
from openalex import Institutions

mit_results = Institutions().search("MIT").get()

# This will find:
# - "Massachusetts Institute of Technology" (via acronym "MIT")
# - "MIT Press" (in display_name)
# - Any institution with "MIT" in alternatives

# Search is also flexible with variations
stanford_results = Institutions().search("Stanford").get()
# Finds "Stanford University", "Stanford Medicine", etc.
```

Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
from openalex import Institutions

# Search only in display_name (not alternatives or acronyms)
display_only = Institutions().filter(
    display_name={"search": "florida"}
).get()

# Or use the search_filter method
search_filter = Institutions().search_filter(
    display_name="california"
).get()

# Default search (same as .search() method)
default_search = Institutions().filter(
    default={"search": "medical school"}
).get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` only | `.search_filter(display_name="...")` |
| `default.search` | `display_name`, `display_name_alternatives`, and `display_name_acronyms` | `.filter(default={"search": "..."})` |

## Autocomplete institutions

Create a fast type-ahead search experience:

```python
# Get autocomplete suggestions
from openalex import Institutions

# Get autocomplete suggestions
suggestions = Institutions().autocomplete("harv")

# Returns fast, lightweight results with location hints
for institution in suggestions.results:
    print(f"{institution.display_name}")
    print(f"  {institution.hint}")  # Location hint
    print(f"  Works: {institution.works_count:,}")
    print(f"  Citations: {institution.cited_by_count:,}")
    if institution.external_id:  # ROR ID
        print(f"  ROR: {institution.external_id}")
```

Example output:
```
Harvard University
  Cambridge, USA
  Works: 542,547
  Citations: 37,792,327
  ROR: https://ror.org/03vek6s52

Harvey Mudd College
  Claremont, USA
  Works: 12,234
  Citations: 456,789
  ROR: https://ror.org/042tdr378
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
# Search for US universities with "State" in name
from openalex import Institutions

# Search for US universities with "State" in name
state_universities = (
    Institutions()
    .search("State University")
    .filter(country_code="US")
    .filter(type="education")
    .get(per_page=50)
)

print(f"Found {state_universities.meta.count} US state universities")

# Search for medical institutions
medical_centers = (
    Institutions()
    .search("Medical")
    .filter(type="healthcare")
    .sort(works_count="desc")
    .get()
)

# Search for tech institutes globally
tech_institutes = (
    Institutions()
    .search("Technology")
    .filter(type="education")
    .filter_gt(works_count=1000)
    .get()
)

# Find specific campus in a university system
berkeley = (
    Institutions()
    .search("Berkeley")
    .filter(lineage="I2803209242")  # UC System
    .get()
)
```

## Search strategies

### Handling ambiguous names

```python
# Many institutions have similar names
from openalex import Institutions

# Many institutions have similar names
columbia_search = Institutions().search("Columbia").get()

# Be more specific with filters
columbia_university = (
    Institutions()
    .search("Columbia University")
    .filter(country_code="US")
    .filter(type="education")
    .get()
)

# Or use location to disambiguate
columbia_ny = (
    Institutions()
    .search("Columbia")
    .filter(geo={"city": "New York"})
    .get()
)
```

### Finding all campuses/branches

```python
from openalex import Institutions

def find_all_campuses(university_name):
    """Find all campuses of a university system."""
    # First search broadly
    all_matches = Institutions().search(university_name).get(per_page=100)
    
    # Group by main institution (using lineage)
    campus_groups = {}
    for inst in all_matches.results:
        # Find the root institution
        root = inst.lineage[-1] if inst.lineage else inst.id
        if root not in campus_groups:
            campus_groups[root] = []
        campus_groups[root].append(inst)
    
    # Show the largest group
    largest_group = max(campus_groups.values(), key=len)
    print(f"Found {len(largest_group)} related institutions:")
    for inst in largest_group:
        print(f"  - {inst.display_name} ({inst.geo.city})")

# Example usage
find_all_campuses("University of California")
```

### International variations

```python
# Handle international name variations
from openalex import Institutions

# Handle international name variations
def search_international(english_name):
    """Search for institutions including international variations."""
    results = Institutions().search(english_name).get(per_page=20)
    
    print(f"Results for '{english_name}':")
    for inst in results.results:
        print(f"\n{inst.display_name}")
        
        # Check for international names
        if hasattr(inst, 'international') and inst.international:
            if hasattr(inst.international, 'display_name'):
                print("  Also known as:")
                for lang, name in inst.international.display_name.items():
                    if name != inst.display_name:
                        print(f"    {lang}: {name}")

search_international("Peking University")
```

## Common search patterns

### Finding specific institution types

```python
# Research universities
from openalex import Institutions

# Research universities
research_unis = (
    Institutions()
    .search("University")
    .filter(type="education")
    .filter_gt(works_count=10000)
    .filter_gt(summary_stats={"h_index": 100})
    .get()
)

# Medical schools and hospitals
medical_institutions = (
    Institutions()
    .search("Medical OR Hospital OR Clinic")
    .filter(type=["education", "healthcare"])
    .get()
)

# Government research institutions
gov_research = (
    Institutions()
    .search("National Laboratory OR Research Institute")
    .filter(type="government")
    .get()
)
```

### Regional searches

```python
# Find all universities in a city
from openalex import Institutions

# Find all universities in a city
def universities_in_city(city_name):
    return (
        Institutions()
        .search(city_name)
        .filter(type="education")
        .get(per_page=50)
    )

boston_unis = universities_in_city("Boston")
print(f"Universities in Boston: {boston_unis.meta.count}")

# Find institutions by name pattern in a country
def find_pattern_in_country(pattern, country_code):
    return (
        Institutions()
        .search(pattern)
        .filter(country_code=country_code)
        .get()
    )

# Find all "Imperial" institutions in UK
imperial_uk = find_pattern_in_country("Imperial", "GB")
```

## Search tips

1. **Try variations**: "MIT" vs "Massachusetts Institute of Technology"
2. **Use acronyms**: Many institutions are known by acronyms
3. **Add location**: Disambiguate using country or city filters
4. **Check alternatives**: Institution might be listed under alternate names
5. **Consider language**: International institutions may have multiple names

```python
from openalex import Institutions

# Example: Comprehensive institution search
def comprehensive_search(name, country=None, type=None):
    """Search with fallback strategies."""
    
    # First try exact search
    query = Institutions().search(name)
    if country:
        query = query.filter(country_code=country)
    if type:
        query = query.filter(type=type)
    
    results = query.get()
    
    if results.meta.count == 0:
        print(f"No exact matches for '{name}'")
        
        # Try broader search
        words = name.split()
        if len(words) > 1:
            # Try first word only
            broad_results = Institutions().search(words[0]).get(per_page=10)
            print(f"\nDid you mean one of these?")
            for inst in broad_results.results:
                print(f"  - {inst.display_name} ({inst.country_code})")
    
    return results

# Usage
comprehensive_search("Stanford Medical School", country="US", type="education")
```
