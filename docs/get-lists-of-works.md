# Get lists of works

`works.list()` returns batches of works along with metadata.

```python
from openalex import Works

works = Works()
works = works.list()
print(works.meta.count)
```

## Page and sort works

Control pagination and ordering with parameters:

```python
# Second page with 50 items
page2 = works.list(per_page=50, page=2)

# Sort by publication year
sorted_works = works.list(sort="publication_year")
```

## Sample works

Request a random sample of works:

```python
sample = works.list(sample=20)
```

## Select fields

Return only chosen fields from each work:

```python
minimal = works.list(select=["id", "display_name"])
```

Filtering and searching are covered in their own guides.
