# Group funders

Summarise funders by an attribute using `group_by`.

```python
from openalex import OpenAlex

client = OpenAlex()
result = client.funders.list(group_by="country_code")
for group in result.group_by:
    print(group.key, group.count)
```

Chaining is possible with the query builder:

```python
query = client.funders.query().filter(country_code="US").group_by("continent")
result = query.list()
```

See the [API documentation](https://docs.openalex.org/api-entities/funders/group-funders) for all group-by fields.
