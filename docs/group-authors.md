# Group authors

Aggregate authors using the `group_by` parameter.

```python
from openalex import Authors

authors = Authors()
results = authors.list(group_by="last_known_institution.continent")
for group in results.group_by:
    print(group.key, group.count)
```

Grouping can be combined with other query builder options:

```python
query = (
    authors.query()
    .filter(has_orcid=True)
    .group_by("last_known_institution.continent")
)
results = query.list()
```

See the [API documentation](https://docs.openalex.org/api-entities/authors/group-authors)
for the full list of attributes available for grouping.

## Limitations

When listing works, the `authorships` array is truncated at 100 items to keep
responses small. If this occurs `is_authors_truncated` will be `true`. Filtering
by author IDs won't match beyond that limit.

## Author disambiguation

Read about how OpenAlex clusters publications into author profiles at
[this help page](https://help.openalex.org/hc/en-us/articles/24347048891543-Author-disambiguation).
