# Search publishers

The best way to search for publishers is to use the `search` method, which searches the `display_name` and `alternate_titles` fields:

```python
from openalex import Publishers

# Search for publishers by name
springer_search = Publishers().search("springer")

# Execute to get the first page of results
results = springer_search.get()

print(f"Found {results.meta.count} publishers matching 'springer'")
for publisher in results.results[:5]:
    print(f"- {publisher.display_name}")
    if publisher.alternate_titles:
        print(f"  Also known as: {', '.join(publisher.alternate_titles[:3])}")
```

## How publisher search works

The search checks both primary and alternate names:

```python
# This searches both display_name and alternate_titles
elsevier_results = Publishers().search("elsevier").get()

# Example matches might include:
# - "Elsevier BV" (display_name)
# - "Elsevier Science" (alternate_title)
# - "Elsevier Health Sciences" (display_name)
# - Publishers with "\u0627\u0644\u0633\u0641\u06cc\u0631" (Arabic for Elsevier) in alternate_titles
```

Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
# Search only in display_name (not alternate_titles)
display_only = Publishers().filter(
    display_name={"search": "elsevier"}
).get()

# Or use the search_filter method
search_filter = Publishers().search_filter(
    display_name="oxford"
).get()

# Default search (same as .search() method)
default_search = Publishers().filter(
    default={"search": "academic press"}
).get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` only | `.search_filter(display_name="...")` |
| `default.search` | `display_name` and `alternate_titles` | `.filter(default={"search": "..."})` |

## Autocomplete publishers

Create a fast type-ahead search experience:

```python
# Get autocomplete suggestions
suggestions = Publishers().autocomplete("els")

# Returns fast, lightweight results
for publisher in suggestions.results:
    print(f"{publisher.display_name}")
    print(f"  Works: {publisher.works_count:,}")
    print(f"  Citations: {publisher.cited_by_count:,}")
    if publisher.external_id:  # Wikidata ID
        print(f"  Wikidata: {publisher.external_id}")
```

Example output:
```
Elsevier BV
  Works: 20,311,868
  Citations: 407,508,754
  Wikidata: https://www.wikidata.org/entity/Q746413

Else Kr\u00f6ner-Fresenius Foundation
  Works: 1,234
  Citations: 45,678
  Wikidata: https://www.wikidata.org/entity/Q1333765
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
# Search for US university presses
us_uni_presses = (
    Publishers()
    .search("University Press")
    .filter(country_codes="US")
    .get()
)

# Large publishers with "Science" in name
science_publishers = (
    Publishers()
    .search("Science")
    .filter_gt(works_count=10000)
    .sort(works_count="desc")
    .get()
)

# Top-level publishers only (no subsidiaries)
parent_publishers = (
    Publishers()
    .search("Nature")
    .filter(hierarchy_level=0)
    .get()
)

# High-impact medical publishers
medical_publishers = (
    Publishers()
    .search("Medical")
    .filter_gt(summary_stats={"h_index": 100})
    .get()
)
```

## Search strategies

### Finding publisher families

```python
# When searching for a publisher group, check hierarchy
def find_publisher_family(search_term):
    # First, find potential matches
    matches = Publishers().search(search_term).get(per_page=20)
    
    families = {}
    for pub in matches.results:
        # Get the top-level parent
        if pub.hierarchy_level == 0:
            family_key = pub.id
        else:
            # Find parent through lineage
            family_key = pub.lineage[-1] if pub.lineage else pub.id
        
        if family_key not in families:
            families[family_key] = []
        families[family_key].append(pub)
    
    return families

# Example usage
nature_families = find_publisher_family("Nature")
for parent_id, members in nature_families.items():
    print(f"\nFamily {parent_id}:")
    for pub in members:
        indent = "  " * pub.hierarchy_level
        print(f"{indent}{pub.display_name}")
```

### Finding regional publishers

```python
# Search for publishers in specific regions
def find_regional_publishers(search_term, country_codes):
    return (
        Publishers()
        .search(search_term)
        .filter(country_codes=country_codes)
        .sort(works_count="desc")
        .get()
    )

# Find Asian academic publishers
asian_academic = find_regional_publishers(
    "Academic", 
    ["CN", "JP", "KR", "IN", "SG"]
)

# Find European open access publishers
eu_oa_publishers = find_regional_publishers(
    "Open Access",
    ["DE", "NL", "GB", "FR", "CH"]
)
```

## Common search patterns

### Disambiguating similar names

```python
# Many publishers have similar names
cambridge_search = Publishers().search("Cambridge").get()

# Distinguish between them using additional filters
cambridge_uni_press = (
    Publishers()
    .search("Cambridge University Press")
    .filter(country_codes="GB")
    .get()
)

# Or use works_count to find the major one
major_cambridge = (
    Publishers()
    .search("Cambridge")
    .sort(works_count="desc")
    .get(per_page=1)
).results[0]
```

### Finding imprints and subsidiaries

```python
# Find all Springer-related entities
springer_all = Publishers().search("Springer").get(per_page=50)

# Separate parents from children
parents = [p for p in springer_all.results if p.hierarchy_level == 0]
imprints = [p for p in springer_all.results if p.hierarchy_level > 0]

print(f"Found {len(parents)} parent companies")
print(f"Found {len(imprints)} imprints/subsidiaries")

# Group by parent
by_parent = {}
for pub in springer_all.results:
    parent = pub.lineage[-1] if pub.lineage else pub.id
    if parent not in by_parent:
        by_parent[parent] = []
    by_parent[parent].append(pub)
```

## Search tips

1. **Check alternate titles**: Publishers often have many name variants
2. **Use hierarchy**: Parent/child relationships help disambiguate
3. **Consider country**: Many publishers have regional branches
4. **Look at scale**: Works_count helps identify major vs. minor publishers
5. **Try partial names**: "Elsevier" finds "Elsevier BV", "Elsevier Ltd", etc.

```python
# Example: Find the "real" publisher among many matches
def find_main_publisher(search_term):
    results = Publishers().search(search_term).get(per_page=10)
    
    # Strategy 1: Highest works count
    by_works = max(results.results, key=lambda p: p.works_count)
    
    # Strategy 2: Top-level only
    parents = [p for p in results.results if p.hierarchy_level == 0]
    
    # Strategy 3: Most cited
    by_citations = max(results.results, key=lambda p: p.cited_by_count)
    
    print(f"Most works: {by_works.display_name} ({by_works.works_count:,})")
    print(f"Parent companies: {[p.display_name for p in parents]}")
    print(f"Most cited: {by_citations.display_name} ({by_citations.cited_by_count:,})")
    
    return by_works  # Usually the best choice
```
