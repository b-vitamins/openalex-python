# Get lists of publishers

Use `publishers.list()` to retrieve batches of publishers.

```python
from openalex import Publishers

publishers = Publishers()
results = publishers.list()
print(results.meta.count)
```

## Page and sort publishers

Control pagination and ordering with parameters:

```python
# second page with 50 results
page2 = publishers.list(per_page=50, page=2)

# sort by display name descending
sorted_pubs = publishers.list(sort="display_name:desc")
```

## Sample publishers

Request a random sample of publishers:

```python
sample = publishers.list(sample=10)
```

## Select fields

Return only selected fields:

```python
minimal = publishers.list(select=["id", "display_name", "alternate_titles"])
```

Filtering and searching are covered in their own guides.
