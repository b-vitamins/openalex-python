# Get lists of authors

`authors.list()` returns batches of authors with a metadata object.

```python
from openalex import Authors

authors = Authors()
response = authors.list()
print(response.meta.count)
```

## Page and sort authors

Use `page`, `per_page`, and `sort` to control the results:

```python
# second page with 50 results
page2 = authors.list(per_page=50, page=2)

# sort by cited_by_count descending
sorted_authors = authors.list(sort="cited_by_count:desc")
```

## Sample authors

Request a random set of authors:

```python
sample = authors.list(sample=25)
```

## Select fields

Restrict the fields returned for each author:

```python
minimal = authors.list(select=["id", "display_name", "orcid"])
```

Filtering and searching are covered in other pages.
