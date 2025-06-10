# Filter funders

Apply filters to `funders.list()` to narrow the results.

```python
from openalex import Funders

funders = Funders()
canadian = funders.list(filter={"country_code": "ca"})
```

Combine multiple filters using a dictionary:

```python
params = {"country_code": "us", "is_global_south": False}
results = funders.list(filter=params)
```

Attribute filters include fields like `works_count`, `cited_by_count`, and `grants_count`.
Convenience filters handle common cases such as `continent` or text searches like
`display_name.search`.

Refer to the [OpenAlex documentation](https://docs.openalex.org/api-entities/funders/filter-funders) for the full list of available filters.
