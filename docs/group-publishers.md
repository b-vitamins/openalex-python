# Group publishers

Summarise publishers with `group_by` on a chosen attribute.

```python
from openalex import Publishers

publishers = Publishers()
result = publishers.list(group_by="country_codes")
for group in result.group_by:
    print(group.key, group.count)
```

You can chain filters and grouping using the query builder:

```python
query = publishers.query().filter(hierarchy_level=0).group_by("country_codes")
result = query.list()
```
