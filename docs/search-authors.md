# Search authors

Use `authors.search()` to look up authors by name.

```python
from openalex import Authors

authors = Authors()
results = authors.search("carl sagan")
print(results.results[0].display_name)
```

See the [OpenAlex documentation](https://docs.openalex.org/api-entities/authors/search-authors)
for details on how search scoring works.

## Search a specific field

Search can also be used as a filter by appending `.search` to a field:

```python
results = authors.list(filter={"display_name.search": "john smith"})
```

When searching authors there is effectively no difference between the `search` parameter
and the filter `display_name.search` since the name is the only searchable field.

| Search filter | Field that is searched |
|---------------|-----------------------|
| `display_name.search` | `display_name` |

## Autocomplete authors

Use `authors.autocomplete()` to get quick suggestions for a typeahead widget:

```python
suggestions = authors.autocomplete("ronald sw")
```

Each suggestion includes the author's current institution as a hint.
