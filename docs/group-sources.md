# Group sources

Summarise sources by a chosen attribute with `group_by`.

```python
from openalex import Sources

sources = Sources()
result = sources.list(group_by="publisher")
for group in result.group_by:
    print(group.key, group.count)
```

You can chain operations using the query builder:

```python
query = sources.query().filter(has_issn=True).group_by("country_code")
result = query.list()
```

See the [API documentation](https://docs.openalex.org/api-entities/sources/group-sources) for all available group-by fields.
