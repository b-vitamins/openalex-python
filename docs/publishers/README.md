---
description: Companies and organizations that distribute works
---

# Publishers

Publishers are companies and organizations that distribute journal articles, books, and theses. OpenAlex indexes about 10,000 publishers. You can access publishers in the Python client like this:

```python
from openalex import Publishers

# Create a query builder for publishers
publishers_query = Publishers()

# Execute the query to get the first page of results (25 publishers by default)
first_page = publishers_query.get()

print(f"Total publishers in OpenAlex: {first_page.meta.count:,}")  # ~10,000
print(f"Publishers returned in this page: {len(first_page.results)}")  # 25
```

Our publisher data is closely tied to the publisher information in Wikidata. So the [Canonical External ID](../../how-to-use-the-api/get-single-entities/#canonical-external-ids) for OpenAlex publishers is a Wikidata ID, and almost every publisher has one. Publishers are linked to sources through the `host_organization` field.

## Important: Understanding Query Results

When you use `Publishers()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual publishers

With only ~10,000 publishers total, it's actually feasible to fetch all publishers if needed (unlike works or authors).

## What's next

Learn more about what you can do with publishers:

* [The Publisher object](publisher-object.md)
* [Get a single publisher](get-a-single-publisher.md)
* [Get lists of publishers](get-lists-of-publishers.md)
* [Filter publishers](filter-publishers.md)
* [Search publishers](search-publishers.md)
* [Group publishers](group-publishers.md)
