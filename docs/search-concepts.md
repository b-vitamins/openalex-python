# Search concepts

> **Warning**
> Concepts are the legacy taxonomy and will eventually be replaced by Topics.

Look up concepts by name or description using `client.concepts.search()`.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.concepts.search("artificial intelligence")
print(results.results[0].display_name)
```

## Search a specific field

Use filter syntax to target a particular field:

```python
results = client.concepts.list(filter={"display_name.search": "medical"})
```

| Search filter | Field |
|---------------|-------|
| `display_name.search` | `display_name` |

## Autocomplete concepts

Get quick suggestions for a typeahead interface:

```python
suggestions = client.concepts.autocomplete("comp")
```
