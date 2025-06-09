# Filter authors

Use the `filter` argument of `client.authors.list()` to narrow the results.

```python
from openalex import OpenAlex

client = OpenAlex()
# authors that have an ORCID
authors = client.authors.list(filter={"has_orcid": True})
```

Multiple filters may be combined using a dictionary or the `AuthorsFilter` helper:

```python
params = {"has_orcid": True, "last_known_institution.continent": "africa"}
results = client.authors.list(filter=params)

filt = (
    AuthorsFilter()
    .with_orcid("!null")
    .with_last_known_institution_continent("africa")
)
results = client.authors.list(filter=filt)
```

## Attribute filters

Attribute filters correspond to fields on the `Author` object such as
`orcid`, `works_count`, or `last_known_institution.id`.
Pass them directly as keys in the filter dictionary or via `AuthorsFilter`.

```python
params = {"works_count": ">100", "last_known_institution.id": "I27837315"}
results = client.authors.list(filter=params)
```

## Convenience filters

Convenience filters are shortcuts for common queries that aren't single fields.

```python
# search within the display name and require an ORCID
params = {"display_name.search": "tupolev", "has_orcid": True}
results = client.authors.list(filter=params)
```

More examples include `default.search`, `last_known_institution.is_global_south`,
and range filters for cited-by counts. See the
[OpenAlex API documentation](https://docs.openalex.org/api-entities/authors/filter-authors)
for the complete list.
