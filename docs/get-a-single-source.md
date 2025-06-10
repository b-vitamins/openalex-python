# Get a single source

Fetch a journal or repository using its OpenAlex identifier.

```python
from openalex import Sources

sources = Sources()
source = sources.get("S137773608")
print(source.display_name)
```

Multiple IDs can be requested in one call using `filter`:

```python
ids = ["S137773608", "S4306400806"]
sources = sources.list(filter={"id": ids})
```

## External IDs

Works can also be looked up by ISSN or other external IDs. Pass the identifier
with the appropriate prefix:

```python
by_issn = sources.get("issn:2041-1723")
```

Supported prefixes:

| External ID | Prefix |
|-------------|-------|
| ISSN | `issn:` |
| Fatcat | `fatcat:` |
| Microsoft Academic Graph (MAG) | `mag:` |
| Wikidata | `wikidata:` |

Make sure the ID is valid or no results will be returned.

### Select fields

Return only a subset of fields using `select`:

```python
minimal = sources.get("S137773608", select=["id", "display_name"])
```
