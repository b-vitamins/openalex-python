# Get lists of funders

Retrieve batches of funders using `funders.list()`.

```python
from openalex import Funders

funders = Funders()
response = funders.list()
print(response.meta.count)
```

## Page and sort funders

Control pagination and ordering with parameters:

```python
# second page with 50 results
page2 = funders.list(per_page=50, page=2)

# sort by display name descending
sorted_funders = funders.list(sort="display_name:desc")
```

## Sample funders

Retrieve a random sample:

```python
sample = funders.list(sample=10)
```

## Select fields

Return only specific fields from each record:

```python
minimal = funders.list(select=["id", "display_name", "alternate_titles"])
```

Use filtering and searching to further narrow results.
