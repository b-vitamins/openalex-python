# Filter works

Use filters to narrow down your search results:

```python
from openalex import Works

# Simple filter
papers_2020 = Works().filter(publication_year=2020).get()

# Multiple filters (AND operation)
open_access_2020 = (
    Works()
    .filter(publication_year=2020, is_oa=True)
    .get()
)

# Complex filters
recent_ml_papers = (
    Works()
    .filter(
        publication_year=[2021, 2022, 2023],
        topics={"id": "T10159"},  # Machine Learning
        is_oa=True
    )
    .get()
)
```

## Logical Operations

```python
# OR operation
papers = Works().filter_or(
    type="article",
    type="preprint"
).get()

# NOT operation
not_retracted = Works().filter_not(type="retracted").get()

# Greater than / Less than
highly_cited = Works().filter_gt(cited_by_count=100).get()
recent = Works().filter_gt(publication_year=2020).get()
```

## Nested Filters

```python
# Filter by institution
mit_papers = Works().filter(
    authorships={
        "institutions": {
            "id": "I63966007"  # MIT
        }
    }
).get()

# Filter by author's institution country
us_papers = Works().filter(
    authorships={
        "institutions": {
            "country_code": "US"
        }
    }
).get()
```

## Common Filters

| Filter             | Description               | Example                             |
| ------------------ | ------------------------- | ----------------------------------- |
| `publication_year` | Year of publication       | `filter(publication_year=2023)`     |
| `is_oa`            | Open access status        | `filter(is_oa=True)`                |
| `type`             | Work type                 | `filter(type="article")`            |
| `cited_by_count`   | Citation count            | `filter_gt(cited_by_count=10)`      |
| `doi`              | Digital Object Identifier | `filter(doi="10.1038/nature12373")` |
| `title.search`     | Search in title           | `filter(title.search="quantum")`    |

For a complete list of filters, see the [OpenAlex API documentation](https://docs.openalex.org/api-entities/works/filter-works).
