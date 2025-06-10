# Filter institutions

Use the `filter` parameter to narrow institution searches.

```python
from openalex import Institutions

institutions = Institutions()
ca_insts = institutions.list(filter={"country_code": "ca"})
```

Multiple filters can be combined:

```python
params = {"country_code": "us", "type": "education"}
results = institutions.list(filter=params)
```

Other attribute filters include `ror`, `works_count`, and `cited_by_count`.

Convenience filters provide shortcuts for common operations, for example:

```python
# institutions in South America with ROR IDs
target = institutions.list(
    filter={"continent": "south_america", "has_ror": True}
)
```

See the [OpenAlex documentation](https://docs.openalex.org/api-entities/institutions/filter-institutions)
for the full list of filters.
