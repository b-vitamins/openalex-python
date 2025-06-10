---
description: Journals and repositories that host works
---

# Sources

Sources are where works are hosted. OpenAlex indexes about 249,000 sources. There are several types, including journals, conferences, preprint repositories, and institutional repositories.

```python
from openalex import Sources

# Create a query builder for sources
sources_query = Sources()

# Execute the query to get the first page of results (25 sources by default)
first_page = sources_query.get()

print(f"Total sources in OpenAlex: {first_page.meta.count:,}")  # ~249,000
print(f"Sources returned in this page: {len(first_page.results)}")  # 25
```

The [Canonical External ID](../../how-to-use-the-api/get-single-entities/#canonical-external-ids) for sources is ISSN-L, which is a special "main" ISSN assigned to every source (sources tend to have multiple ISSNs). About 90% of sources in OpenAlex have an ISSN-L or ISSN.

Our information about sources comes from Crossref, the ISSN Network, and MAG. These datasets are joined automatically where possible, but there's also a lot of manual combining involved. We do not curate journals, so any journal that is available in the data sources should make its way into OpenAlex.

Several sources may host the same work. OpenAlex reports both the primary host source (generally wherever the [version of record](https://en.wikipedia.org/wiki/Version_of_record) lives), and alternate host sources (like preprint repositories).

Sources are linked to works via the [`works.primary_location`](../works/work-object/#primary_location) and [`works.locations`](../works/work-object/#locations) properties.

## Important: Understanding Query Results

When you use `Sources()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual sources

With ~249,000 sources total, it's feasible to fetch all sources if needed, though it will require about 1,250 API calls at 200 per page.

## What's next

Learn more about what you can do with sources:

* [The Source object](source-object.md)
* [Get a single source](get-a-single-source.md)
* [Get lists of sources](get-lists-of-sources.md)
* [Filter sources](filter-sources.md)
* [Search sources](search-sources.md)
* [Group sources](group-sources.md)
