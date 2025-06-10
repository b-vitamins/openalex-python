# Filter topics

Narrow results with the `filter` argument when listing topics.

```python
from openalex import Topics

topics = Topics()
epi = topics.list(filter={"subfield.id": 2713})
```

Combine parameters using a dictionary:

```python
params = {"field.id": 1047, "works_count": ">1000"}
results = topics.list(filter=params)
```

See [OpenAlex filter docs](https://docs.openalex.org/api-entities/topics/filter-topics) for a complete list of attribute and convenience filters.
