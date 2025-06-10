# Filter authors

Filter authors using various criteria:

```python
from openalex import Authors

# Authors with ORCID
authors_with_orcid = Authors().filter(has_orcid=True).get()

# Multiple filters
african_authors = (
    Authors()
    .filter(
        has_orcid=True,
        last_known_institution={"continent": "africa"}
    )
    .get()
)
```

## Search Filters

```python
# Search in display name
smiths = Authors().filter(display_name.search="smith").get()

# Search with other filters
prolific_johns = (
    Authors()
    .filter(display_name.search="john")
    .filter_gt(works_count=50)
    .get()
)
```

## Range Filters

```python
# Highly cited authors
highly_cited = Authors().filter_gt(cited_by_count=1000).get()

# Authors with moderate publication count
moderate_publishers = (
    Authors()
    .filter_gt(works_count=10)
    .filter_lt(works_count=100)
    .get()
)
```

## Institution Filters

```python
# Authors from a specific institution
mit_authors = Authors().filter(
    last_known_institution={"id": "I63966007"}
).get()

# Authors from US institutions
us_authors = Authors().filter(
    last_known_institution={"country_code": "US"}
).get()
```

For more filter options, see the [OpenAlex API documentation](https://docs.openalex.org/api-entities/authors/filter-authors).
