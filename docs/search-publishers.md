# Search publishers

Look up publishers by name with `publishers.search()`.

```python
from openalex import Publishers

publishers = Publishers()
results = publishers.search("springer")
print(results.results[0].display_name)
```

## Search a specific field

Search can also be used as a filter by appending `.search` to a field name:

```python
results = publishers.list(filter={"display_name.search": "elsevier"})
```

## Autocomplete publishers

Get quick suggestions as a user types:

```python
suggestions = publishers.autocomplete("els")
```
