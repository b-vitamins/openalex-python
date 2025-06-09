# Filter institutions

Use the `filter` parameter to narrow institution searches.

```python
from openalex import OpenAlex

client = OpenAlex()
ca_insts = client.institutions.list(filter={"country_code": "ca"})
```

Multiple filters can be combined:

```python
params = {"country_code": "us", "type": "education"}
results = client.institutions.list(filter=params)
```

A fluent `InstitutionsFilter` is also available:

```python
from openalex import InstitutionsFilter

filt = InstitutionsFilter().with_country_code("us").with_type("education")
results = client.institutions.list(filter=filt)
```

Other attribute filters include `ror`, `works_count`, and `cited_by_count`.

Convenience filters provide shortcuts for common operations, for example:

```python
# institutions in South America with ROR IDs
target = client.institutions.list(
    filter={"continent": "south_america", "has_ror": True}
)
```

See the [OpenAlex documentation](https://docs.openalex.org/api-entities/institutions/filter-institutions)
for the full list of filters.
