# Get lists of funders

Retrieve batches of funders using `client.funders.list()`.

```python
from openalex import OpenAlex

client = OpenAlex()
response = client.funders.list()
print(response.meta.count)
```

## Page and sort funders

Control pagination and ordering with parameters:

```python
# second page with 50 results
page2 = client.funders.list(per_page=50, page=2)

# sort by display name descending
sorted_funders = client.funders.list(sort="display_name:desc")
```

## Sample funders

Retrieve a random sample:

```python
sample = client.funders.list(sample=10)
```

## Select fields

Return only specific fields from each record:

```python
minimal = client.funders.list(select=["id", "display_name", "alternate_titles"])
```

Use filtering and searching to further narrow results.
