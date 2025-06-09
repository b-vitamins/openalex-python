# Get lists of concepts

> **Warning**
> Concepts are deprecated in favor of Topics. Use them only if you rely on the legacy taxonomy.

List concepts via `client.concepts.list()`.

```python
from openalex import OpenAlex

client = OpenAlex()
result = client.concepts.list()
print(result.meta.count)
```

## Page and sort concepts

Adjust paging and ordering just like other resources:

```python
second = client.concepts.list(per_page=50, page=2)
sorted_concepts = client.concepts.list(sort="cited_by_count:desc")
```

## Sample concepts

Retrieve a random sample:

```python
sample = client.concepts.list(sample=10)
```

## Select fields

Return only specific fields:

```python
mini = client.concepts.list(select=["id", "display_name", "description"])
```
