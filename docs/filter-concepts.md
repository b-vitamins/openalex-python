# Filter concepts

> **Warning**
> Concepts are deprecated in favor of Topics and are not regularly updated.

Use the `filter` argument to narrow results.

```python
from openalex import OpenAlex

client = OpenAlex()
level_zero = client.concepts.list(filter={"level": 0})
```

Combine multiple filters or use the `ConceptsFilter` helper:

```python
params = {"cited_by_count": ">100", "has_wikidata": True}
results = client.concepts.list(filter=params)

from openalex import ConceptsFilter
filt = ConceptsFilter().with_level(1).with_has_wikidata(True)
results = client.concepts.list(filter=filt)
```

See [the API docs](https://docs.openalex.org/api-entities/concepts/filter-concepts) for the full list of attribute and convenience filters.
