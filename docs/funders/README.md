---
description: Organizations that fund research
---

# Funders

Funders are organizations that fund research. OpenAlex indexes about 32,000 funders. Funder data comes from Crossref, and is enhanced with data from Wikidata and ROR.

```python
from openalex import Funders

funders_query = Funders()

first_page = funders_query.get()

print(f"Total funders in OpenAlex: {first_page.meta.count:,}")  # ~32,000
print(f"Funders returned in this page: {len(first_page.results)}")  # 25
```

Funders are connected to works through [grants](../works/work-object/#grants).

## Important: Understanding Query Results

When you use `Funders()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual funders

With only ~32,000 funders total, it's very feasible to fetch all funders if needed (about 160 API calls at 200 per page).

## What's next

Learn more about what you can do with funders:

* [The Funder object](funder-object.md)
* [Get a single funder](get-a-single-funder.md)
* [Get lists of funders](get-lists-of-funders.md)
* [Filter funders](filter-funders.md)
* [Search funders](search-funders.md)
* [Group funders](group-funders.md)
