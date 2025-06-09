# Group concepts

> **Warning**
> Concepts are deprecated in favor of Topics.

Aggregate concepts by a particular attribute using `group_by`.

```python
from openalex import OpenAlex

client = OpenAlex()
result = client.concepts.list(group_by="level")
for group in result.group_by:
    print(group.key, group.count)
```

You can also build a query with additional filters before grouping:

```python
query = client.concepts.query().filter(has_wikidata=True).group_by("level")
result = query.list()
```

See the [API documentation](https://docs.openalex.org/api-entities/concepts/group-concepts) for all available group-by fields.
