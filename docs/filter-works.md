# Filter works

Use the `filter` argument of `works.list()` to narrow results. Filter
keys follow the same names as the API.

```python
from openalex import Works

works = Works()
# works published in 2020
works = works.list(filter={"publication_year": 2020})
```

Multiple filters can be combined by passing a dictionary:

```python
params = {"publication_year": 2020, "is_oa": True}
works = works.list(filter=params)
```

For more complex queries you can build a `WorksFilter` object:

```python
from openalex import WorksFilter

filt = WorksFilter().with_publication_year(2020).with_open_access()
works = works.list(filter=filt)
```

## Attribute filters

Attribute filters match fields on the `Work` object. Pass them as a
dictionary or use helper methods on `WorksFilter`.

```python
# by author and work type
params = {"authorships.author.id": "A123456789", "type": "article"}
results = works.list(filter=params)

filt = WorksFilter().with_author_id("A123456789").with_type("article")
results = works.list(filter=filt)
```

Other common attribute filters include `publication_year`, `concepts.id`, and
`primary_location.source.id`.

## Convenience filters

Convenience filters offer shortcuts for frequent queries that are not direct
properties of the work record.

```python
# works that cite a specific paper and have an abstract
params = {"cites": "W2741809807", "has_abstract": True}
results = works.list(filter=params)

filt = WorksFilter().with_cites("W2741809807").with_has_abstract(True)
results = works.list(filter=filt)
```

Other examples are `from_publication_date`, `has_fulltext`, and
`best_open_version`.

For a complete list of available filters see the [OpenAlex API
documentation](https://docs.openalex.org/api-entities/works/filter-works).

