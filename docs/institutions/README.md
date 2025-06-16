---
description: Universities and other organizations to which authors claim affiliations
---

# Institutions

Institutions are universities and other organizations to which authors claim affiliations. OpenAlex indexes about 109,000 institutions. You can access institutions in the Python client like this:

```python
from openalex import Institutions

institutions_query = Institutions()

first_page = institutions_query.get()

print(f"Total institutions in OpenAlex: {first_page.meta.count:,}")  # ~109,000
print(f"Institutions returned in this page: {len(first_page.results)}")  # 25
```

The [Canonical External ID](../../how-to-use-the-api/get-single-entities/#canonical-external-ids) for institutions is the ROR ID. All institutions in OpenAlex have ROR IDs.

OpenAlex compiles institution information from Crossref, PubMed, ROR, MAG, and publisher websites. To link institutions to works, they parse every affiliation string listed by each author. These strings can be messy, so the OpenAlex team trained an algorithm to interpret them and identify the correct institutions with reasonably high reliability.

For example, both "MIT, Boston, USA" and "Massachusetts Institute of Technology" are recognized as the same institution (https://ror.org/042nb2s44).

Institutions are linked to works via the `works.authorships` property.

Most papers provide raw strings for author affiliations (e.g., "Univ. of Florida, Gainesville FL"). Parsing these to determine the actual institution is nontrivial. More information, including code, models, and test sets, is available in the [OpenAlex institution parsing repository](https://github.com/ourresearch/openalex-institution-parsing).

## Important: Understanding Query Results

When you use `Institutions()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual institutions

With ~109,000 institutions total, it's feasible to fetch all institutions if needed (unlike works with 240M+ records).

## What's next

Learn more about what you can do with institutions:

* [The Institution object](institution-object.md)
* [Get a single institution](get-a-single-institution.md)
* [Get lists of institutions](get-lists-of-institutions.md)
* [Filter institutions](filter-institutions.md)
* [Search institutions](search-institutions.md)
* [Group institutions](group-institutions.md)
