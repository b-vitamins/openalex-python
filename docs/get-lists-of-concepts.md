# Get lists of concepts

> **Warning**
> Concepts are deprecated in favor of Topics. Use them only if you rely on the legacy taxonomy.

List concepts via `concepts.list()`.

```python
from openalex import Concepts

concepts = Concepts()
result = concepts.list()
print(result.meta.count)
```

## Page and sort concepts

Adjust paging and ordering just like other resources:

```python
second = concepts.list(per_page=50, page=2)
sorted_concepts = concepts.list(sort="cited_by_count:desc")
```

## Sample concepts

Retrieve a random sample:

```python
sample = concepts.list(sample=10)
```

## Select fields

Return only specific fields:

```python
mini = concepts.list(select=["id", "display_name", "description"])
```
