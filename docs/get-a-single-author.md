# Get a single author

Use `Authors().get()` to fetch an author by OpenAlex ID.

```python
from openalex import Authors

authors = Authors()
author = authors.get("A5023888391")
print(author.display_name)
```

You can request several authors at once by filtering on their IDs:

```python
ids = ["A5023888391", "A5053780153"]
authors = authors.list(filter={"id": ids})
```

## External IDs

Authors can also be retrieved using ORCID or other external identifiers:

```python
author = authors.by_orcid("0000-0002-1298-3089")
author = authors.get("orcid:0000-0002-1298-3089")
```

Supported prefixes:

| External ID | Prefix |
|-------------|-------|
| ORCID | `orcid` |
| Scopus | `scopus` |
| Twitter | `twitter` |
| Wikipedia | `wikipedia` |

Make sure the identifier is valid; incorrect or malformed IDs return no result.

## Select fields

Limit returned data with `select`:

```python
author = authors.get(
    "A5023888391", select=["id", "display_name", "orcid"]
)
```
