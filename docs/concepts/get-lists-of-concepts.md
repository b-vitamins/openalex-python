# Get lists of concepts

{% hint style="warning" %}
**DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). OpenAlex will continue to provide these Concepts for Works, but OpenAlex will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, The OpenAlex team encourages you to look into [Topics](../topics/README.md) instead.
{% endhint %}

You can get lists of concepts using the Python client:

```python
from openalex import Concepts

# Create a query for all concepts (no filters applied)
all_concepts_query = Concepts()

# Execute the query to get the FIRST PAGE of results
first_page = all_concepts_query.get()

# Note: With ~65,000 concepts, fetching all is manageable
print(f"Total concepts: {first_page.meta.count:,}")  # ~65,000
print(f"Concepts in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Concept objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
from openalex import Concepts

first_page = Concepts().get()
# Each result shows concept information
for concept in first_page.results[:5]:  # First 5 concepts
    print(f"\n{concept.display_name} (Level {concept.level})")
    if concept.description:
        print(f"  Description: {concept.description[:100]}...")
    print(f"  Works: {concept.works_count:,}")
    print(f"  Citations: {concept.cited_by_count:,}")
    print(f"  Wikidata: {concept.wikidata}")
```

## Page and sort concepts

You can control pagination and sorting:

```python
# Import client
from openalex import Concepts
# Get a specific page with custom page size
page2 = Concepts().get(per_page=50, page=2)
# This returns concepts 51-100

# Sort by different fields
# Most used concepts (by work count)
most_used = Concepts().sort(works_count="desc").get()

# Most cited concepts
most_cited = Concepts().sort(cited_by_count="desc").get()

# Get root-level concepts (level 0)
root_concepts = Concepts().filter(level=0).sort(display_name="asc").get()
print(f"Found {root_concepts.meta.count} root concepts")  # Should be 19

# Get many concepts without downloading everything
some_concepts = []
page_count = 0
for page in Concepts().paginate(per_page=200):
    page_count += 1
    if page_count > 2:  # Roughly 400 concepts
        break
    some_concepts.extend(page.results)

print(f"Fetched {len(some_concepts)} concepts")
```

## Sample concepts

Get a random sample of concepts:

```python
from openalex import Concepts
# Get 10 random concepts
random_sample = Concepts().sample(10).get(per_page=10)

# Use a seed for reproducible random sampling
reproducible_sample = Concepts().sample(10, seed=42).get(per_page=10)

# Sample from filtered results
level2_sample = (
    Concepts()
    .filter(level=2)
    .sample(5)
    .get()
)
```

## Select fields

Limit the fields returned to improve performance:

```python
from openalex import Concepts
# Request only specific fields
minimal_concepts = Concepts().select([
    "id",
    "display_name",
    "description",
    "level",
    "works_count"
]).get()

# This reduces response size significantly
for concept in minimal_concepts.results:
    print(f"{concept.display_name} (Level {concept.level}): {concept.works_count:,} works")
    print(concept.ancestors)  # None - not selected
```

## Practical examples

### Example: Explore the concept tree

```python
from openalex import Concepts
def explore_concept_hierarchy():
    """Explore the 6-level concept hierarchy."""

    # Get root concepts (level 0)
    root_concepts = Concepts().filter(level=0).get(per_page=25)
    print(f"Root concepts (Level 0): {root_concepts.meta.count}")

    for root in root_concepts.results[:5]:
        print(f"\n{root.display_name}")

        # Get children (level 1)
        children = (
            Concepts()
            .filter(ancestors={"id": root.id})
            .filter(level=1)
            .get()
        )
        print(f"  Children: {children.meta.count}")

        for child in children.results[:3]:
            print(f"    - {child.display_name}")

explore_concept_hierarchy()
```

### Example: Analyze concept distribution by level

```python
from openalex import Concepts
def analyze_concept_levels():
    """Analyze how concepts are distributed across levels."""

    print("Concept distribution by level:")
    for level in range(6):  # Levels 0-5
        level_concepts = Concepts().filter(level=level).get()
        print(f"  Level {level}: {level_concepts.meta.count:,} concepts")

    # Get examples from each level
    print("\nExample concepts at each level:")
    for level in range(6):
        examples = (
            Concepts()
            .filter(level=level)
            .sort(works_count="desc")
            .get(per_page=3)
        )
        print(f"\nLevel {level}:")
        for concept in examples.results:
            print(f"  - {concept.display_name} ({concept.works_count:,} works)")

analyze_concept_levels()
```

### Example: Find research hotspots

```python
from openalex import Concepts
def find_research_hotspots(min_works=10000):
    """Find highly active research concepts."""

    hotspots = (
        Concepts()
        .filter_gt(works_count=min_works)
        .sort(cited_by_count="desc")
        .get(per_page=20)
    )

    print(f"Research hotspots (> {min_works:,} works):")
    for i, concept in enumerate(hotspots.results, 1):
        impact = concept.cited_by_count / concept.works_count if concept.works_count > 0 else 0
        print(f"\n{i}. {concept.display_name} (Level {concept.level})")
        print(f"   Works: {concept.works_count:,}")
        print(f"   Citations: {concept.cited_by_count:,}")
        print(f"   Avg citations/work: {impact:.1f}")

find_research_hotspots()
```

Continue on to learn how you can [filter](filter-concepts.md) and [search](search-concepts.md) lists of concepts.

**Remember: Concepts are deprecated! Use [Topics](../topics/README.md) for new projects.**
