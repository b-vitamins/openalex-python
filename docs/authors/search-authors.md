# Search authors

The best way to search for authors is to use the `search` method, which searches the `display_name` and `display_name_alternatives` fields:

```python
from openalex import Authors

# Search for authors by name
sagan_search = Authors().search("carl sagan")

# Execute to get the first page of results
results = sagan_search.get()

print(f"Found {results.meta.count} authors matching 'carl sagan'")
for author in results.results[:5]:
    print(f"- {author.display_name}")
    if author.last_known_institutions:
        print(f"  {author.last_known_institutions[0].display_name}")
```

## How name searching works

The search is intelligent about name variations:

```python
# Searching without middle initial returns names with AND without
smiths = Authors().search("John Smith").get()
# Returns: "John Smith", "John W. Smith", "John William Smith", etc.

# Diacritics are handled flexibly
tarrago1 = Authors().search("David Tarrago").get()
tarrago2 = Authors().search("David Tarrag\u00f3").get()
# Both can find "David Tarrag\u00f3" and "David Tarrago"
# When searching with diacritics, those versions are prioritized
```

Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
# Search using filter syntax
filter_search = Authors().filter(
    display_name={"search": "john smith"}
).get()

# Or use the search_filter method
search_filter = Authors().search_filter(
    display_name="john smith"
).get()

# For authors, these are equivalent to .search()
# since display_name is the only searchable field
general_search = Authors().search("john smith").get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` and `display_name_alternatives` | `.search_filter(display_name="...")` |
| `default.search` | Same as above | `.filter(default={"search": "..."})` |

## Autocomplete authors

Create a fast type-ahead search experience:

```python
# Get autocomplete suggestions
suggestions = Authors().autocomplete("ronald sw")

# Returns fast, lightweight results with institutional hints
for author in suggestions.results:
    print(f"{author.display_name}")
    print(f"  {author.hint}")  # Last known institution
    print(f"  Works: {author.works_count}")
    print(f"  Citations: {author.cited_by_count}")
    if author.external_id:  # ORCID if available
        print(f"  ORCID: {author.external_id}")
```

Example output:
```
Ronald Swanstrom
  University of North Carolina at Chapel Hill, USA
  Works: 339
  Citations: 19142
  ORCID: https://orcid.org/0000-0001-7777-0773

Ronald Swoboda
  University of Vienna, Austria  
  Works: 45
  Citations: 892
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
# Search for John Smith at Harvard
harvard_smiths = (
    Authors()
    .search("John Smith")
    .filter(last_known_institutions={"id": "I136199984"})  # Harvard
    .get()
)

# High-impact authors named Chen
prolific_chens = (
    Authors()
    .search("Chen")
    .filter_gt(works_count=100)
    .filter_gt(summary_stats={"h_index": 30})
    .sort(cited_by_count="desc")
    .get()
)

# Authors named Maria with ORCID
maria_with_orcid = (
    Authors()
    .search("Maria")
    .filter(has_orcid=True)
    .get()
)

# Recent authors (based on their affiliations)
recent_authors = (
    Authors()
    .search("machine learning")
    .filter(affiliations={"institution": {"type": "education"}})
    .get()
)
```

## Search tips

1. **Name variations**: The search handles common variations automatically
2. **No wildcards needed**: "John" finds "John", "Johnson", "Johnny", etc.
3. **Case insensitive**: "smith" = "Smith" = "SMITH"
4. **Order matters**: "John Smith" vs "Smith John" return different results
5. **Use filters**: Narrow results by institution, metrics, etc.

## Common search patterns

```python
# Find potential duplicates for an author
def find_similar_authors(name, institution_id=None):
    query = Authors().search(name)
    if institution_id:
        query = query.filter(affiliations={"institution": {"id": institution_id}})
    return query.get(per_page=50)

# Find co-authors from a specific country
def find_collaborators(name, country_code):
    return (
        Authors()
        .search(name)
        .filter(last_known_institutions={"country_code": country_code})
        .sort(cited_by_count="desc")
        .get()
    )

# Search for rising stars in a field
def find_rising_stars(field_keyword, min_recent_citations=100):
    return (
        Authors()
        .search(field_keyword)
        .filter_gt(summary_stats={"2yr_mean_citedness": 5.0})
        .filter_gt(cited_by_count=min_recent_citations)
        .filter_lt(works_count=50)  # Early career
        .get()
    )
```

## Handling ambiguous names

For common names, add context:

```python
# Too broad - many results
broad_search = Authors().search("J Smith").get()
print(f"Found {broad_search.meta.count:,} 'J Smith' authors")

# Better - add context
specific_search = (
    Authors()
    .search("John Smith")
    .filter(last_known_institutions={"country_code": "US"})
    .filter_gt(works_count=10)
    .get()
)
print(f"Found {specific_search.meta.count} specific matches")

# Best - use known identifiers when possible
if known_orcid:
    author = Authors()[known_orcid]  # Direct lookup
```
