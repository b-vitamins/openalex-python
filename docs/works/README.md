---
description: Journal articles, books, datasets, and theses
---

# Works

Works are scholarly documents like journal articles, books, datasets, and theses. OpenAlex indexes over 240M works, with about 50,000 added daily. You can access works in the OpenAlex Python client like this:

```python
from openalex import Works

# Create a query builder for works (this doesn't fetch any data yet)
works_query = Works()

# Execute the query to get the first page of results (25 works by default)
first_page = works_query.get()

print(f"Total works in OpenAlex: {first_page.meta.count:,}")
print(f"Works returned in this page: {len(first_page.results)}")
```

That will return a [`ListResult`](../models/list-result.md) containing [`Work`](work-object.md) objects, describing everything OpenAlex knows about each work. OpenAlex collects new works from many sources, including Crossref, PubMed, institutional and discipline-specific repositories (e.g., arXiv). Many older works originate from the now-defunct Microsoft Academic Graph (MAG).

Works are linked to other works via the `referenced_works` (outgoing citations), `cited_by_api_url` (incoming citations), and `related_works` properties.

## Important: Understanding Query Results

When you use `Works()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual works

## What's next

Learn more about what you can do with works:

* [The Work object](work-object.md)
* [Get a single work](get-a-single-work.md)
* [Get lists of works](get-lists-of-works.md)
* [Filter works](filter-works.md)
* [Search for works](search-works.md)
* [Group works](group-works.md)
