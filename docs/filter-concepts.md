# Filter concepts

> **Warning**
> Concepts are deprecated in favor of Topics and are not regularly updated.

Use the `filter` argument to narrow results.

```python
from openalex import Concepts

concepts = Concepts()
level_zero = concepts.list(filter={"level": 0})
```

Combine multiple filters using a dictionary:

```python
params = {"cited_by_count": ">100", "has_wikidata": True}
results = concepts.list(filter=params)
```

See [the API docs](https://docs.openalex.org/api-entities/concepts/filter-concepts) for the full list of attribute and convenience filters.
