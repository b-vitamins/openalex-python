# Search sources

Look up journals and repositories by name with `client.sources.search()`.

```python
from openalex import OpenAlex

client = OpenAlex()
results = client.sources.search("jacs")
print(results.results[0].display_name)
```

See the [OpenAlex docs](https://docs.openalex.org/api-entities/sources/search-sources) for details on relevance scoring and advanced options.

## Search a specific field

As with other endpoints, search can be used as a filter by appending `.search` to a field:

```python
results = client.sources.list(filter={"display_name.search": "nature"})
```

## Autocomplete sources

Use `client.sources.autocomplete()` for typeahead suggestions:

```python
suggestions = client.sources.autocomplete("neuro")
```

Each result includes the publisher as a hint.
