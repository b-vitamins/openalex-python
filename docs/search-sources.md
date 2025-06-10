# Search sources

Look up journals and repositories by name with `sources.search()`.

```python
from openalex import Sources

sources = Sources()
results = sources.search("jacs")
print(results.results[0].display_name)
```

See the [OpenAlex docs](https://docs.openalex.org/api-entities/sources/search-sources) for details on relevance scoring and advanced options.

## Search a specific field

As with other endpoints, search can be used as a filter by appending `.search` to a field:

```python
results = sources.list(filter={"display_name.search": "nature"})
```

## Autocomplete sources

Use `sources.autocomplete()` for typeahead suggestions:

```python
suggestions = sources.autocomplete("neuro")
```

Each result includes the publisher as a hint.
