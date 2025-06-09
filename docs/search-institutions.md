# Search institutions

Use `client.institutions.search()` to find institutions by name.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.institutions.search("san diego state university")
print(results.results[0].display_name)
```

## Search a specific field

Searching can also be done via filters:

```python
results = client.institutions.list(filter={"display_name.search": "florida"})
```

| Search filter | Field |
|---------------|-------|
| `display_name.search` | `display_name` |

## Autocomplete institutions

Quickly suggest institutions for a typeahead field:

```python
suggestions = client.institutions.autocomplete("harv")
```

Each suggestion includes the location as a hint.
