# Search concepts

> **Warning**
> Concepts are the legacy taxonomy and will eventually be replaced by Topics.

Look up concepts by name or description using `concepts.search()`.

```python
from openalex import Concepts

concepts = Concepts()
results = concepts.search("artificial intelligence")
print(results.results[0].display_name)
```

## Search a specific field

Use filter syntax to target a particular field:

```python
results = concepts.list(filter={"display_name.search": "medical"})
```

| Search filter | Field |
|---------------|-------|
| `display_name.search` | `display_name` |

## Autocomplete concepts

Get quick suggestions for a typeahead interface:

```python
suggestions = concepts.autocomplete("comp")
```
