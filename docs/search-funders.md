# Search funders

Use `client.funders.search()` to look up funders by name or description.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.funders.search("health")
print(results.results[0].display_name)
```

## Search a specific field

Field-limited search works via filters:

```python
results = client.funders.list(filter={"display_name.search": "florida"})
```

| Search filter | Field |
|---------------|-------|
| `display_name.search` | `display_name` |
| `description.search` | `description` |

## Autocomplete funders

Get quick suggestions for a typeahead control:

```python
suggestions = client.funders.autocomplete("national sci")
```
