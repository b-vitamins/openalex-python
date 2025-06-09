# Get lists of topics

List topics using `client.topics.list()`.

```python
from openalex import OpenAlex

client = OpenAlex()
resp = client.topics.list()
print(resp.meta.count)
```

## Page and sort topics

Adjust pagination and ordering:

```python
page2 = client.topics.list(per_page=50, page=2)
sorted_topics = client.topics.list(sort="cited_by_count:desc")
```

## Sample topics

Retrieve a random sample:

```python
sample = client.topics.list(sample=10)
```

## Select fields

Return only specific fields:

```python
mini = client.topics.list(select=["id", "display_name", "description"])
```
