---
description: Topics assigned to works
---

# Topics

Works in OpenAlex are tagged with Topics using an automated system that takes into account the available information about the work, including title, abstract, source (journal) name, and citations. There are around 4,500 Topics. Works are assigned topics using a model that assigns scores for each topic for a work. The highest-scoring topic is that work's [`primary_topic`](../works/work-object/#primary_topic). We also provide additional highly ranked topics for works, in [Work.topics](../works/work-object/README.md#topics).

```python
from openalex import Topics

# Create a query builder for topics
topics_query = Topics()

# Execute the query to get the first page of results (25 topics by default)
first_page = topics_query.get()

print(f"Total topics in OpenAlex: {first_page.meta.count:,}")  # ~4,500
print(f"Topics returned in this page: {len(first_page.results)}")  # 25

# Example: Show some topics
for topic in first_page.results[:5]:
    print(f"\n{topic.display_name}")
    print(f"  Domain: {topic.domain.display_name}")
    print(f"  Field: {topic.field.display_name}")
    print(f"  Subfield: {topic.subfield.display_name}")
    print(f"  Works: {topic.works_count:,}")
```

To learn more about how OpenAlex topics work in general, see [the Topics page at OpenAlex help pages](https://help.openalex.org/how-it-works/topics).

For a detailed description of the methods behind OpenAlex Topics, see our paper: ["OpenAlex: End-to-End Process for Topic Classification"](https://docs.google.com/document/d/1bDopkhuGieQ4F8gGNj7sEc8WSE8mvLZS/edit?usp=sharing&ouid=106329373929967149989&rtpof=true&sd=true). The code and model are available at [`https://github.com/ourresearch/openalex-topic-classification`](https://github.com/ourresearch/openalex-topic-classification).

## Important: Understanding Query Results

When you use `Topics()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual topics

With only ~4,500 topics total, it's very feasible to fetch all topics if needed (about 23 API calls at 200 per page).

## What's next

Learn more about what you can do with topics:

* [The Topic object](topic-object.md)
* [Get a single topic](get-a-single-topic.md)
* [Get lists of topics](get-lists-of-topics.md)
* [Filter topics](filter-topics.md)
* [Search topics](search-topics.md)
* [Group topics](group-topics.md)
