# Get lists of works

`client.works.list()` returns batches of works along with metadata.

```python
from openalex import OpenAlex

client = OpenAlex()
works = client.works.list()
print(works.meta.count)
```

## Page and sort works

Control pagination and ordering with parameters:

```python
# Second page with 50 items
page2 = client.works.list(per_page=50, page=2)

# Sort by publication year
sorted_works = client.works.list(sort="publication_year")
```

## Sample works

Request a random sample of works:

```python
sample = client.works.list(sample=20)
```

## Select fields

Return only chosen fields from each work:

```python
minimal = client.works.list(select=["id", "display_name"])
```

Filtering and searching are covered in their own guides.
