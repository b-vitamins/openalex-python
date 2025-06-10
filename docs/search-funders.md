# Search funders

Use `funders.search()` to look up funders by name or description.

```python
from openalex import Funders

funders = Funders()
results = funders.search("health")
print(results.results[0].display_name)
```

## Search a specific field

Field-limited search works via filters:

```python
results = funders.list(filter={"display_name.search": "florida"})
```

| Search filter | Field |
|---------------|-------|
| `display_name.search` | `display_name` |
| `description.search` | `description` |

## Autocomplete funders

Get quick suggestions for a typeahead control:

```python
suggestions = funders.autocomplete("national sci")
```
