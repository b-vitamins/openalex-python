# Group institutions

Aggregate institutions with the `group_by` parameter.

```python
from openalex import Institutions

institutions = Institutions()
results = institutions.list(group_by="country_code")
for group in results.group_by:
    print(group.key, group.count)
```

Grouping can be chained with other query builder methods:

```python
query = institutions.query().filter(country_code="us").group_by("type")
results = query.list()
```

See the [API documentation](https://docs.openalex.org/api-entities/institutions/group-institutions)
for the complete list of grouping attributes.
