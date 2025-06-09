# Group topics

Aggregate topics using `group_by`.

```python
from openalex import OpenAlex

client = OpenAlex()
result = client.topics.list(group_by="domain.id")
for group in result.group_by:
    print(group.key, group.count)
```

You can also build a query first and chain additional operations:

```python
query = client.topics.query().filter(field_id=2713).group_by("subfield.id")
result = query.list()
```

Check the [API documentation](https://docs.openalex.org/api-entities/topics/group-topics) for all available group-by fields.
