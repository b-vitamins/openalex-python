# Get lists of sources

Use `client.sources.list()` to retrieve batches of journals, repositories, and other sources.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.sources.list()
print(results.meta.count)
```

## Page and sort sources

Control pagination and ordering just like other endpoints:

```python
# second page with 50 results
page2 = client.sources.list(per_page=50, page=2)

# order by cited-by count descending
sorted_sources = client.sources.list(sort="cited_by_count:desc")
```

## Sample sources

Request a random sample of sources:

```python
sample = client.sources.list(sample=10)
```

## Select fields

Limit the fields returned for each source:

```python
minimal = client.sources.list(select=["id", "display_name", "issn"])
```

Filtering and searching are covered in their own guides.
