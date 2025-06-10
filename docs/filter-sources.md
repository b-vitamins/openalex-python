# Filter sources

Use the `filter` argument of `sources.list()` to narrow the returned sources.

```python
from openalex import Sources

sources = Sources()
# sources that have an ISSN
sources = sources.list(filter={"has_issn": True})
```

Combine multiple filters using a dictionary:

```python
params = {"is_oa": True, "host_organization.id": "P4310320547"}
results = sources.list(filter=params)
```

Other useful filters include ranges like `apc_usd`, `summary_stats.h_index` and text search using `display_name.search`.
See the [OpenAlex docs](https://docs.openalex.org/api-entities/sources/filter-sources) for the full list.
