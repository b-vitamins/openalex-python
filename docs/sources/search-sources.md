# Search sources

The best way to search for sources is to use the `search` method, which searches across `display_name`, `alternate_titles`, and `abbreviated_title`:

```python
from openalex import Sources

# Search for the abbreviated version of the Journal of the American Chemical Society
jacs_search = Sources().search("jacs")

# Execute to get the first page of results
results = jacs_search.get()

print(f"Found {results.meta.count} sources matching 'jacs'")
for source in results.results[:5]:
    print(f"- {source.display_name}")
    if source.abbreviated_title:
        print(f"  Abbreviated: {source.abbreviated_title}")
    print(f"  Type: {source.type}")
    print(f"  Publisher: {source.host_organization_name}")
```

## How source search works

The search checks multiple fields:

```python
# This searches display_name, alternate_titles, AND abbreviated_title
nature_results = Sources().search("Nature").get()

# This will find:
# - "Nature" (exact match in display_name)
# - "Nature Medicine" (partial match)
# - Sources with "Nature" in alternate titles
# - Sources abbreviated as "Nat." or similar

# Search is flexible with variations
plos_results = Sources().search("PLoS").get()
# Finds "PLOS ONE", "PLOS Biology", etc.
```

Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
from openalex import Sources

# Search only in display_name (not alternatives or abbreviations)
display_only = Sources().filter(
    display_name={"search": "nature"}
).get()

# Or use the search_filter method
search_filter = Sources().search_filter(
    display_name="science"
).get()

# Default search (same as .search() method)
default_search = Sources().filter(
    default={"search": "computer science"}
).get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` only | `.search_filter(display_name="...")` |
| `default.search` | `display_name`, `alternate_titles`, and `abbreviated_title` | `.filter(default={"search": "..."})` |

## Autocomplete sources

Create a fast type-ahead search experience:

```python
from openalex import Sources

# Get autocomplete suggestions
suggestions = Sources().autocomplete("neuro")

# Returns fast, lightweight results
for source in suggestions.results:
    print(f"{source.display_name}")
    print(f"  Publisher: {source.hint}")  # Publisher shown as hint
    print(f"  Type: {source.entity_type}")
    print(f"  Works: {source.works_count:,}")
    print(f"  Citations: {source.cited_by_count:,}")
    if source.external_id:  # ISSN
        print(f"  ISSN: {source.external_id}")
```

Example output:
```
The Journal of Neuroscience
  Publisher: Society for Neuroscience
  Type: source
  Works: 40,376
  Citations: 4,274,712
  ISSN: 0270-6474

Nature Neuroscience
  Publisher: Springer Nature
  Type: source
  Works: 8,542
  Citations: 1,234,567
  ISSN: 1097-6256
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
from openalex import Sources

# Search for open access journals with "medicine" in name
oa_medical = (
    Sources()
    .search("medicine")
    .filter(type="journal")
    .filter(is_oa=True)
    .get(per_page=20)
)

print(f"Found {oa_medical.meta.count} OA medical journals")

# Search for high-impact journals
high_impact_search = (
    Sources()
    .search("Science")
    .filter(type="journal")
    .filter_gt(summary_stats={"2yr_mean_citedness": 5.0})
    .sort(summary_stats={"2yr_mean_citedness": "desc"})
    .get()
)

# Search for repositories
repo_search = (
    Sources()
    .search("University")
    .filter(type="repository")
    .get()
)

# Find specific publisher's journals
elsevier_medical = (
    Sources()
    .search("medical")
    .filter(host_organization="P4310320595")  # Elsevier
    .filter(type="journal")
    .get()
)
```

## Search strategies

### Handling journal variations

```python
from openalex import Sources

# Many journals have multiple names/abbreviations
def find_journal_variations(journal_name):
    """Find all variations of a journal name."""
    
    # Try exact search first
    exact = Sources().search(journal_name).get(per_page=10)
    
    print(f"Searching for '{journal_name}':")
    print(f"Found {exact.meta.count} matches\n")
    
    # Show all variations found
    for source in exact.results:
        print(f"{source.display_name}")
        if source.abbreviated_title:
            print(f"  Abbreviated: {source.abbreviated_title}")
        if source.alternate_titles:
            print(f"  Also known as: {', '.join(source.alternate_titles)}")
        if source.issn:
            print(f"  ISSN(s): {', '.join(source.issn)}")
        print()

# Example usage
find_journal_variations("JAMA")
find_journal_variations("BMJ")
```

### Finding sources by topic

```python
from openalex import Sources

def find_sources_by_topic(topic, source_type=None):
    """Find sources related to a specific topic."""
    
    # Build query
    query = Sources().search(topic)
    if source_type:
        query = query.filter(type=source_type)
    
    # Get results sorted by relevance (default)
    results = query.get(per_page=20)
    
    print(f"Top sources for '{topic}':")
    for i, source in enumerate(results.results, 1):
        print(f"\n{i}. {source.display_name}")
        print(f"   Type: {source.type}")
        print(f"   Works: {source.works_count:,}")
        if source.summary_stats and source.type == "journal":
            impact = source.summary_stats.get("2yr_mean_citedness", 0)
            print(f"   Impact Factor: {impact:.2f}")

# Examples
find_sources_by_topic("artificial intelligence", "journal")
find_sources_by_topic("climate change")
find_sources_by_topic("COVID", "repository")
```

### Publisher catalog search

```python
from openalex import Sources

def search_publisher_catalog(publisher_id, search_term):
    """Search within a specific publisher's sources."""
    
    results = (
        Sources()
        .search(search_term)
        .filter(host_organization_lineage=publisher_id)
        .get(per_page=50)
    )
    
    print(f"Found {results.meta.count} sources matching '{search_term}'")
    
    # Group by type
    by_type = {}
    for source in results.results:
        if source.type not in by_type:
            by_type[source.type] = []
        by_type[source.type].append(source)
    
    # Display grouped results
    for source_type, sources in by_type.items():
        print(f"\n{source_type.title()}s ({len(sources)}):")
        for src in sources[:5]:  # First 5 of each type
            print(f"  - {src.display_name}")

# Search Springer Nature catalog
search_publisher_catalog("P4310319965", "quantum")
```

## Common search patterns

### Finding specific journal types

```python
# Open access journals in a field
oa_cs_journals = (
    Sources()
    .search("computer")
    .filter(type="journal")
    .filter(is_oa=True)
    .filter_gt(works_count=100)
    .get()
)

# High-impact journals by keyword
top_medical = (
    Sources()
    .search("medical OR medicine OR clinical")
    .filter(type="journal")
    .filter_gt(summary_stats={"2yr_mean_citedness": 10.0})
    .sort(summary_stats={"2yr_mean_citedness": "desc"})
    .get()
)

# Conference proceedings
ml_conferences = (
    Sources()
    .search("machine learning OR neural")
    .filter(type="conference")
    .get()
)
```

### Regional source discovery

```python
from openalex import Sources

# Find sources from specific regions
def find_regional_sources(search_term, country_codes):
    return (
        Sources()
        .search(search_term)
        .filter(country_code=country_codes)
        .get(per_page=50)
    )

# Asian science journals
asian_science = find_regional_sources(
    "science", 
    ["CN", "JP", "KR", "IN", "SG"]
)

# European open access
eu_oa = (
    Sources()
    .search("research")
    .filter(continent="europe")
    .filter(is_oa=True)
    .get()
)
```

## Search tips

1. **Use abbreviations**: Many journals are known by abbreviated titles
2. **Try multiple terms**: "AI" vs "artificial intelligence"
3. **Check alternate titles**: Journal names change over time
4. **Filter by type**: Narrow down to journals, repositories, etc.
5. **Consider publisher**: Search within specific publisher catalogs

```python
from openalex import Sources

# Example: Comprehensive journal search
def comprehensive_journal_search(search_terms, min_impact=None):
    """Search for journals with multiple strategies."""
    
    all_results = set()
    
    # Try each search term
    for term in search_terms:
        results = (
            Sources()
            .search(term)
            .filter(type="journal")
            .get(per_page=100)
        )
        
        for source in results.results:
            # Apply additional filters
            if min_impact and source.summary_stats:
                impact = source.summary_stats.get("2yr_mean_citedness", 0)
                if impact < min_impact:
                    continue
            
            all_results.add((source.id, source.display_name))
    
    print(f"Found {len(all_results)} unique journals")
    for source_id, name in sorted(all_results, key=lambda x: x[1]):
        print(f"  - {name}")
    
    return all_results

# Search for AI/ML journals
comprehensive_journal_search(
    ["artificial intelligence", "machine learning", "neural network", "AI", "ML"],
    min_impact=2.0
)
```
