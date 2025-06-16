# Concepts

{% hint style="warning" %}
**DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). OpenAlex will continue to provide these Concepts for Works, but OpenAlex will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, The OpenAlex team encourages you to look into [Topics](../topics/README.md) instead.
{% endhint %}

Concepts are abstract ideas that works are about. OpenAlex indexes about 65k concepts.

```python
from openalex import Concepts

# Create a query builder for concepts
concepts_query = Concepts()

# Execute the query to get the first page of results (25 concepts by default)
first_page = concepts_query.get()

print(f"Total concepts in OpenAlex: {first_page.meta.count:,}")  # ~65,000
print(f"Concepts returned in this page: {len(first_page.results)}")  # 25

# Show deprecation warning
print("\nWARNING: Concepts are deprecated. Use Topics instead!")
```

The [Canonical External ID](../../how-to-use-the-api/get-single-entities/#canonical-external-ids) for OpenAlex concepts is the Wikidata ID, and each OpenAlex concept has one, because all OpenAlex concepts are also Wikidata concepts.

Concepts are hierarchical, like a tree. There are 19 root-level concepts, and six layers of descendants branching out from them, containing about 65 thousand concepts all told. This concept tree is a modified version of [the one created by MAG](https://arxiv.org/abs/1805.12216).

You can view all the concepts and their position in the tree [as a spreadsheet here](https://docs.google.com/spreadsheets/d/1LBFHjPt4rj_9r0t0TTAlT68NwOtNH8Z21lBMsJDMoZg/edit#gid=1473310811). About 85% of works are tagged with at least one concept (here's the [breakdown of concept counts per work](https://docs.google.com/spreadsheets/d/17DoJjyl1XVNZdVWs7fUy91z69U2tD8qtnBsaqJ-Zigo/edit#gid=0)).

## How concepts are assigned

Each work is tagged with multiple concepts, based on the title, abstract, and the title of its host venue. The tagging is done using an automated classifier that was trained on MAG's corpus; you can read more about the development and operation of this classifier in [Automated concept tagging for OpenAlex, an open index of scholarly articles.](https://docs.google.com/document/d/1OgXSLriHO3Ekz0OYoaoP_h0sPcuvV4EqX7VgLLblKe4/edit) You can implement the classifier yourself using [the OpenAlex models and code](https://github.com/ourresearch/openalex-concept-tagging).

A score is available for each [concept in a work](../works/work-object/#concepts), showing the classifier's confidence in choosing that concept. However, when assigning a lower-level child concept, OpenAlex also assigns all of its parent concepts up to the root. This means some concept assignment scores will be 0.0. The tagger adds concepts to works written in different languages, but it is optimized for English.

Concepts are linked to works via the [`concepts`](../works/work-object/#concepts) property, and to other concepts via the [`ancestors`](concept-object.md#ancestors) and [`related_concepts`](concept-object.md#related_concepts) properties.

## Important: Understanding Query Results

When you use `Concepts()`, you're creating a **query builder**, not fetching data. The data is only retrieved when you call:
- `.get()` - Returns one page of results (25-200 items)
- `.paginate()` - Returns an iterator for all results
- `.group_by(...).get()` - Returns aggregated counts, not individual concepts

With ~65,000 concepts total, it's feasible to fetch all concepts if needed (about 325 API calls at 200 per page).

## What's next

Learn more about what you can do with concepts:

* [The Concept object](concept-object.md)
* [Get a single concept](get-a-single-concept.md)
* [Get lists of concepts](get-lists-of-concepts.md)
* [Filter concepts](filter-concepts.md)
* [Search concepts](search-concepts.md)
* [Group concepts](group-concepts.md)

**Remember: Consider using [Topics](../topics/README.md) instead of Concepts for new projects!**
