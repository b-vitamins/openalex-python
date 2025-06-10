# Search works

Search across titles, abstracts, and full text:

```python
from openalex import Works

# Basic search
results = Works().search("climate change").get()

# Search with filters
recent_climate_papers = (
    Works()
    .search("climate change")
    .filter(publication_year=[2022, 2023])
    .filter(is_oa=True)
    .get()
)
```

## Field-Specific Search

Use `search_filter()` to search within specific fields:

```python
# Search in title only
title_matches = (
    Works()
    .search_filter(title="quantum computing")
    .get()
)

# Search in abstract
abstract_matches = (
    Works()
    .search_filter(abstract="machine learning")
    .get()
)

# Multiple field searches
specific_papers = (
    Works()
    .search_filter(
        title="neural networks",
        abstract="classification"
    )
    .get()
)
```

## Advanced Search

```python
# Combine search with complex filters
results = (
    Works()
    .search("artificial intelligence")
    .filter(
        publication_year=2023,
        is_oa=True,
        type="article"
    )
    .filter_gt(cited_by_count=5)
    .sort(cited_by_count="desc")
    .get()
)
```

## Autocomplete

Get suggestions for typeahead:

```python
suggestions = Works().autocomplete("quan")
for suggestion in suggestions.results:
    print(suggestion.display_name)
```

See the [OpenAlex documentation](https://docs.openalex.org/api-entities/works/search-works) for more details on search behavior.
