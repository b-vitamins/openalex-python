# Group works

Use `group_by` to aggregate works by a given field.

```python
from openalex import Works

works = Works()
# count works for each open access status
result = works.list(group_by="oa_status")
for group in result.group_by:
    print(group.key, group.count)
```

You can combine grouping with filters or other parameters via the query builder:

```python
query = works.query().filter(is_oa=True).group_by("publication_year")
result = query.list()
```

See the [OpenAlex API documentation](https://docs.openalex.org/api-entities/works/group-works) for the full list of supported group-by attributes.
