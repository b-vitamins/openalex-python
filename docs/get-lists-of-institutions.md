# Get lists of institutions

Use `client.institutions.list()` to retrieve institution records in bulk.

```python
from openalex import OpenAlex

client = OpenAlex()
response = client.institutions.list()
print(response.meta.count)
```

## Page and sort institutions

Control pagination and ordering as needed:

```python
# second page with 50 results
page2 = client.institutions.list(per_page=50, page=2)

# sort by cited_by_count descending
sorted_insts = client.institutions.list(sort="cited_by_count:desc")
```

## Sample institutions

Request a random sample:

```python
sample = client.institutions.list(sample=50, per_page=50)
```

## Select fields

Return only chosen fields from each institution:

```python
minimal = client.institutions.list(select=["id", "ror", "display_name"])
```

Filtering and searching are detailed in other pages.
