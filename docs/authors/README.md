---
description: People who create works
---

# Authors

Authors are people who create works. You can access authors in the OpenAlex Python client like this:

```python
from openalex import Authors

# Create a query builder for authors
authors_query = Authors()

# Execute the query to get the first page of results (25 authors by default)
first_page = authors_query.get()

print(f"Total authors in OpenAlex: {first_page.meta.count:,}")  # ~93,011,659
print(f"Authors returned in this page: {len(first_page.results)}")  # 25
```

The [Canonical External ID](../../how-to-use-the-api/get-single-entities/#canonical-external-ids) for authors is ORCID; only a small percentage of authors have one, but the percentage is higher for more recent works.

OpenAlex gathers author information from MAG, Crossref, PubMed, ORCID, and publisher websites, among other sources. To learn more about how they combine this data to build author records, see [Author Disambiguation](https://help.openalex.org/hc/en-us/articles/24347048891543-Author-disambiguation).

Authors are linked to works via the `works.authorships` property.

## Important: Understanding Query Results

When you use `Authors()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual authors

## What's next

Learn more about what you can do with authors:

* [The Author object](author-object.md)
* [Get a single author](get-a-single-author.md)
* [Get lists of authors](get-lists-of-authors.md)
* [Filter authors](filter-authors.md)
* [Search authors](search-authors.md)
* [Group authors](group-authors.md)
