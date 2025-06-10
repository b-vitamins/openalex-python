# Search authors

Search for authors by name:

```python
from openalex import Authors

# Simple search
results = Authors().search("marie curie").get()

# Get the first result
if results.results:
    author = results.results[0]
    print(f"{author.display_name} - {author.works_count} works")
```

## Search with Filters

```python
# Search with additional criteria
physicists = (
    Authors()
    .search("einstein")
    .filter(last_known_institution={"country_code": "US"})
    .get()
)
```

## Field-Specific Search

For authors, searching the display name is the primary option:

```python
# Equivalent to search()
authors = Authors().filter(display_name.search="feynman").get()
```

## Autocomplete

Get suggestions for author names:

```python
suggestions = Authors().autocomplete("carl sa")
for suggestion in suggestions.results:
    print(f"{suggestion.display_name} - {suggestion.hint}")
```

The hint typically shows the author's institution.
