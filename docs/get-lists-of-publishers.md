# Get lists of publishers

Use `client.publishers.list()` to retrieve batches of publishers.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.publishers.list()
print(results.meta.count)
```

## Page and sort publishers

Control pagination and ordering with parameters:

```python
# second page with 50 results
page2 = client.publishers.list(per_page=50, page=2)

# sort by display name descending
sorted_pubs = client.publishers.list(sort="display_name:desc")
```

## Sample publishers

Request a random sample of publishers:

```python
sample = client.publishers.list(sample=10)
```

## Select fields

Return only selected fields:

```python
minimal = client.publishers.list(select=["id", "display_name", "alternate_titles"])
```

Filtering and searching are covered in their own guides.
