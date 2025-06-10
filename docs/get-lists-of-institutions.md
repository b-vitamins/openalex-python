# Get lists of institutions

Use `institutions.list()` to retrieve institution records in bulk.

```python
from openalex import Institutions

institutions = Institutions()
response = institutions.list()
print(response.meta.count)
```

## Page and sort institutions

Control pagination and ordering as needed:

```python
# second page with 50 results
page2 = institutions.list(per_page=50, page=2)

# sort by cited_by_count descending
sorted_insts = institutions.list(sort="cited_by_count:desc")
```

## Sample institutions

Request a random sample:

```python
sample = institutions.list(sample=50, per_page=50)
```

## Select fields

Return only chosen fields from each institution:

```python
minimal = institutions.list(select=["id", "ror", "display_name"])
```

Filtering and searching are detailed in other pages.
