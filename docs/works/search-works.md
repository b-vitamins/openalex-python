# Search works

The best way to search for works is to use the `search` method, which searches across titles, abstracts, and fulltext:

```python
from openalex import Works

# Search works mentioning "dna" published in 2023
results = (
    Works()
    .search("dna")
    .filter(publication_year=2023)
    .sort(relevance_score="desc")
    .get()
)

print(f"Total works matching 'dna': {results.meta.count:,}")
print(f"Showing first {len(results.results)} results")

for i, work in enumerate(results.results[:5], 1):
    print(f"{i}. {work.display_name}")
    print(f"   Relevance score: {work.relevance_score}")
```

Fulltext search is available for a subset of works, see `Work.has_fulltext` for more details.

Search uses relevance ranking, stemming (e.g., "running" matches "run"), and removes common words.

## Search a specific field

You can search within specific fields for more precise results:

```python
# Import Works query builder
from openalex import Works

# Search only in titles
cubist_titles = (
    Works()
    .search_filter(title="cubist")
    .filter(publication_year=2023)
    .get()
)
# Finds works with "cubist" in the title field only

# Search only in abstracts
ai_abstracts = (
    Works()
    .search_filter(abstract="artificial intelligence")
    .filter(publication_year=2023)
    .get()
)
# More specific than general search

# Search in fulltext (when available)
climate_fulltext = (
    Works()
    .search_filter(fulltext="climate change mitigation strategies")
    .filter(publication_year=2023)
    .get()
)
# Searches the complete text of works where we have it

# Search in author affiliation strings
sfu_affiliations = (
    Works()
    .search_filter(raw_affiliation_strings="Simon Fraser University")
    .filter(publication_year=2023)
    .get()
)
# Finds works where author affiliations mention SFU

# Search in both title and abstract
quantum_papers = (
    Works()
    .search_filter(title_and_abstract="quantum computing")
    .filter(publication_year=2023)
    .get()
)
# Searches both fields simultaneously
```

The following fields can be searched:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `abstract.search` | `abstract_inverted_index` | `.search_filter(abstract="...")` |
| `display_name.search` | `display_name` | `.search_filter(display_name="...")` |
| `fulltext.search` | fulltext via n-grams | `.search_filter(fulltext="...")` |
| `raw_affiliation_strings.search` | `authorships.raw_affiliation_strings` | `.search_filter(raw_affiliation_strings="...")` |
| `title.search` | `display_name` | `.search_filter(title="...")` |
| `title_and_abstract.search` | `display_name` and `abstract_inverted_index` | `.search_filter(title_and_abstract="...")` |

## Default search vs field search

```python
# Import Works query builder
from openalex import Works

# Option 1: General search (searches title, abstract, fulltext)
general_search = (
    Works()
    .search("machine learning")
    .filter(publication_year=2023)
    .get()
)

# Option 2: Field-specific search using filter
title_only = (
    Works()
    .filter(default={"search": "machine learning"})
    .filter(publication_year=2023)
    .get()
)

# Option 3: Multiple field searches
specific_search = (
    Works()
    .search_filter(
        title="neural networks",
        abstract="deep learning"
    )
    .filter(publication_year=2023)
    .get()
)
# Must match "neural networks" in title AND "deep learning" in abstract
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
# Import Works query builder
from openalex import Works

# Find recent, highly-cited ML papers
recent_ml_papers = (
    Works()
    .search("machine learning")  # Full-text search
    .filter(publication_year=2023)  # Published in 2023
    .filter(open_access={"is_oa": True})  # Open access only
    .filter_gt(cited_by_count=10)  # More than 10 citations already
    .sort(cited_by_count="desc")  # Most cited first
    .get(per_page=100)  # Get top 100
)

print(f"Found {recent_ml_papers.meta.count:,} highly-cited 2023 ML papers")

# Search specific fields with additional filters  
quantum_2023 = (
    Works()
    .search_filter(title="quantum computing")  # Title must contain this
    .filter(publication_year=2023)
    .filter_gt(cited_by_count=5)
    .get()
)

# Complex query: Find review articles on climate change
climate_reviews = (
    Works()
    .search_filter(
        title="climate change",
        abstract="systematic review"
    )
    .filter(type="article")
    .filter(from_publication_date="2020-01-01")
    .get()
)
```

## Why can't I search by name of related entity?

You cannot directly search for author names, institution names, etc. in work queries. Instead, use a two-step process:

```python
from openalex import Institutions, Authors, Works

# Step 1: Find the institution by name
institutions = Institutions().search("NYU").get()
nyu = institutions.results[0]
print(f"Found: {nyu.display_name} ({nyu.id})")  # New York University (I57206974)

# Step 2: Find works from that institution
nyu_works = Works().filter(
    authorships={"institutions": {"id": nyu.id}}
).get()
print(f"NYU has {nyu_works.meta.count:,} works")

# Similarly for authors
authors = Authors().search("John Smith").get()
if authors.results:
    author = authors.results[0]
    author_works = Works().filter(
        authorships={"author": {"id": author.id}}
    ).get()
```

Why? Because:
- "NYU" might miss "New York University" 
- "J. Smith" might miss "John Smith"
- Multiple people might have the same name

We've already resolved these ambiguities in our entity records!

## Autocomplete works

Create a fast type-ahead search experience:

```python
# Import Works query builder
from openalex import Works

# Get autocomplete suggestions for works
suggestions = Works().filter(publication_year=2023).autocomplete("quantum comp")

# Returns fast, lightweight results
for work in suggestions.results:
    print(f"{work.display_name}")
    print(f"  Authors: {work.hint}")  # Hint shows authors
    print(f"  Citations: {work.cited_by_count}")
    print(f"  Work ID: {work.id}")
    print()
```

Example output:
```
Quantum computation and quantum information
  Authors: Michael A. Nielsen, Isaac L. Chuang  
  Citations: 12453
  Work ID: https://openalex.org/W1234567

Quantum Computing: An Applied Approach
  Authors: Jack D. Hidary
  Citations: 234
  Work ID: https://openalex.org/W2234567
```

## Search tips

1. **Use filters to narrow results**: Pure search might return millions of results
2. **Be specific with field search**: `search_filter(title=...)` is more precise than `search()`
3. **Check fulltext availability**: Not all works have fulltext indexed
4. **Combine strategies**: Use search for discovery, then filters for precision

```python
# Import Works query builder
from openalex import Works

# Good: Specific search with reasonable result size
good_query = (
    Works()
    .search("climate change")
    .filter(publication_year=[2022, 2023])
    .filter(type="article")
    .filter_gt(cited_by_count=5)
    .get()
)

# Less ideal: Still quite broad
broad_query = Works().search("science").filter(publication_year=2023).get()

# Better: Add context
better_query = (
    Works()
    .search("citizen science")
    .filter(primary_topic={"field": {"id": "F10075"}})
    .get()
)
```
