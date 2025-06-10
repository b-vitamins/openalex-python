# Get lists of topics

List topics using `topics.list()`.

```python
from openalex import Topics

topics = Topics()
resp = topics.list()
print(resp.meta.count)
```

## Page and sort topics

Adjust pagination and ordering:

```python
page2 = topics.list(per_page=50, page=2)
sorted_topics = topics.list(sort="cited_by_count:desc")
```

## Sample topics

Retrieve a random sample:

```python
sample = topics.list(sample=10)
```

## Select fields

Return only specific fields:

```python
mini = topics.list(select=["id", "display_name", "description"])
```
