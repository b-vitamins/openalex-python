# Filter publishers

Limit results from `publishers.list()` using the `filter` parameter.

```python
from openalex import Publishers

publishers = Publishers()
# top level publishers
publishers = publishers.list(filter={"hierarchy_level": 0})
```

Combine several filters with a dictionary or the `PublishersFilter` helper:

```python
params = {"country_codes": "US", "hierarchy_level": 0}
results = publishers.list(filter=params)

filt = (
    PublishersFilter()
    .with_country_codes("US")
    .with_hierarchy_level(0)
)
results = publishers.list(filter=filt)
```

Other useful fields include `parent_publisher`, ranges on `works_count`, and text search using `display_name.search`.
See the [OpenAlex docs](https://docs.openalex.org/api-entities/publishers/filter-publishers) for the full list.
