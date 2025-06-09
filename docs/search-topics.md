# Search topics

Look up topics by name or description using `client.topics.search()`.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.topics.search("artificial intelligence")
print(results.results[0].display_name)
```

## Search a specific field

Use filter syntax to target a particular field:

```python
results = client.topics.list(filter={"display_name.search": "medical"})
```

| Search filter | Field |
|---------------|-------|
| `display_name.search` | `display_name` |
| `description.search` | `description` |
| `keywords.search` | `keywords` |

## Autocomplete topics

Get quick suggestions for a typeahead interface:

```python
suggestions = client.topics.autocomplete("neuro")
```
