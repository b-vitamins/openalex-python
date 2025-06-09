# Filter topics

Narrow results with the `filter` argument when listing topics.

```python
from openalex import OpenAlex

client = OpenAlex()
epi = client.topics.list(filter={"subfield.id": 2713})
```

You can combine parameters or use the `TopicsFilter` helper:

```python
params = {"field.id": 1047, "works_count": ">1000"}
results = client.topics.list(filter=params)

from openalex import TopicsFilter
filt = TopicsFilter().with_domain_id(4100).with_cited_by_count_range(min_count=50)
results = client.topics.list(filter=filt)
```

See [OpenAlex filter docs](https://docs.openalex.org/api-entities/topics/filter-topics) for a complete list of attribute and convenience filters.
