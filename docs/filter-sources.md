# Filter sources

Use the `filter` argument of `sources.list()` to narrow the returned sources.

```python
from openalex import Sources

sources = Sources()
# sources that have an ISSN
sources = sources.list(filter={"has_issn": True})
```

Multiple filters can be combined with a dictionary or the `SourcesFilter` helper:

```python
params = {"is_oa": True, "host_organization.id": "P4310320547"}
results = sources.list(filter=params)

filt = (
    SourcesFilter()
    .with_is_oa(is_oa=True)
    .with_publisher("P4310320547")
)
results = sources.list(filter=filt)
```

Other useful filters include ranges like `apc_usd`, `summary_stats.h_index` and text search using `display_name.search`.
See the [OpenAlex docs](https://docs.openalex.org/api-entities/sources/filter-sources) for the full list.
