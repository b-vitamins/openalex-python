# Concept object

{% hint style="warning" %}
**DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). We will continue to provide these Concepts for Works, but we will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, we encourage you to look into [Topics](../topics/README.md) instead.
{% endhint %}

When you fetch a concept using the Python client, you get a `Concept` object with all of OpenAlex's data about that concept. Here's how to access the various properties:

```python
from openalex import Concepts

# Get a specific concept
concept = Concepts()["C71924100"]

# The concept object has all the data as Python attributes
print(type(concept))  # <class 'openalex.models.concept.Concept'>
```

## Basic properties

```python
# Import client and fetch a concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# Identifiers
print(concept.id)  # "https://openalex.org/C71924100"
print(concept.wikidata)  # "https://www.wikidata.org/wiki/Q11190" (canonical ID)
print(concept.display_name)  # "Medicine"
print(concept.description)  # "field of study for diagnosing, treating and preventing disease"

# Hierarchy
print(concept.level)  # 0 (root level, 0-5 scale)

# Metrics
print(concept.works_count)  # Number of works tagged with this concept
print(concept.cited_by_count)  # Total citations

# Dates
print(concept.created_date)  # "2017-08-08"
print(concept.updated_date)  # "2021-12-25T14:04:30.578837"
```

## Hierarchical relationships

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# Ancestors (concepts this descends from)
if concept.ancestors:
    print(f"Ancestors ({len(concept.ancestors)}):")
    for ancestor in concept.ancestors:
        print(f"  - {ancestor.display_name} (Level {ancestor.level})")
        print(f"    ID: {ancestor.id}")
        print(f"    Wikidata: {ancestor.wikidata}")

# Related concepts
if concept.related_concepts:
    print(f"\nRelated concepts:")
    for related in concept.related_concepts[:5]:
        print(f"  - {related.display_name} (Level {related.level})")
        print(f"    Score: {related.score:.2f}")  # Strength of association
```

## Summary statistics

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
stats = concept.summary_stats
if stats:
    print(f"H-index: {stats.h_index}")
    print(f"i10-index: {stats.i10_index:,}")
    print(f"2-year mean citedness: {stats.two_year_mean_citedness:.2f}")

    # These help assess concept impact
    if stats.h_index > 200:
        print("This is a high-impact research concept")
```

## Publication trends

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# Track output over the last 10 years
print("Publication trends:")
for count in concept.counts_by_year[:5]:  # Last 5 years
    print(f"  {count.year}: {count.works_count:,} works, "
          f"{count.cited_by_count:,} citations")

# Analyze trends
if len(concept.counts_by_year) >= 2:
    recent = concept.counts_by_year[0]
    previous = concept.counts_by_year[1]
    if previous.works_count > 0:
        growth = ((recent.works_count - previous.works_count) /
                  previous.works_count * 100)
        print(f"Year-over-year growth: {growth:+.1f}%")
```

## External identifiers

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
ids = concept.ids
print(f"OpenAlex: {ids.openalex}")
print(f"Wikidata: {ids.wikidata}")  # Always present (canonical ID)
if ids.mag:
    print(f"MAG: {ids.mag}")
if ids.wikipedia:
    print(f"Wikipedia: {ids.wikipedia}")
if ids.umls_cui:
    print(f"UMLS CUI: {ids.umls_cui}")  # Medical concepts
if ids.umls_aui:
    print(f"UMLS AUI: {ids.umls_aui}")  # Medical concepts
```

## Images

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# Concept visualization (usually from Wikipedia)
if concept.image_url:
    print(f"Image URL: {concept.image_url}")

if concept.image_thumbnail_url:
    print(f"Thumbnail: {concept.image_thumbnail_url}")
```

## International names

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# Names in different languages
if hasattr(concept, 'international') and concept.international:
    if hasattr(concept.international, 'display_name'):
        print("International names:")
        for lang, name in concept.international.display_name.items():
            print(f"  {lang}: {name}")
```

## Works API URL

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# URL to get all works tagged with this concept
print(f"Works URL: {concept.works_api_url}")

# To actually fetch works using the client:
from openalex import Works

# Get recent works with this concept
concept_works = (
    Works()
    .filter(concepts={"id": concept.id})
    .filter(publication_year=2023)
    .sort(publication_date="desc")
    .get()
)

print(f"Recent works tagged with {concept.display_name}:")
for work in concept_works.results[:5]:
    print(f"  - {work.title}")
```

## Working with concept data

### Navigate the concept tree

```python
# Import client
from openalex import Concepts
def explore_concept_tree(concept_id):
    """Navigate up and down the concept hierarchy."""

    concept = Concepts()[concept_id]

    print(f"Concept: {concept.display_name} (Level {concept.level})")

    # Go up: Show ancestors
    if concept.ancestors:
        print("\nAncestors (parent chain):")
        for i, ancestor in enumerate(concept.ancestors):
            indent = "  " * i
            print(f"{indent}^ {ancestor.display_name} (Level {ancestor.level})")

    # Go down: Show descendants
    descendants = (
        Concepts()
        .filter(ancestors={"id": concept_id})
        .filter(level=concept.level + 1)  # Direct children only
        .get(per_page=10)
    )

    if descendants.meta.count > 0:
        print(f"\nDescendants ({descendants.meta.count} direct children):")
        for child in descendants.results:
            print(f"  v {child.display_name}")

            # Count grandchildren
            grandchildren = (
                Concepts()
                .filter(ancestors={"id": child.id})
                .get()
            )
            if grandchildren.meta.count > 1:  # More than just itself
                print(f"    ({grandchildren.meta.count - 1} descendants)")

explore_concept_tree("C41008148")  # Computer Science
```

### Analyze concept impact

```python
# Import client
from openalex import Concepts
def analyze_concept_impact(concept_id):
    """Comprehensive impact analysis of a concept."""
    concept = Concepts()[concept_id]

    print(f"Impact Analysis: {concept.display_name}")
    print("=" * 50)

    # Basic metrics
    print(f"\nBasic Metrics:")
    print(f"  Level: {concept.level}")
    print(f"  Works: {concept.works_count:,}")
    print(f"  Citations: {concept.cited_by_count:,}")

    # Impact metrics
    if concept.summary_stats:
        stats = concept.summary_stats
        print(f"\nImpact Metrics:")
        print(f"  H-index: {stats.h_index}")
        print(f"  i10-index: {stats.i10_index:,}")
        print(f"  Mean citedness: {stats.two_year_mean_citedness:.2f}")

        # Calculate average citations per work
        if concept.works_count > 0:
            avg_citations = concept.cited_by_count / concept.works_count
            print(f"  Avg citations/work: {avg_citations:.1f}")

    # Trend analysis
    if concept.counts_by_year and len(concept.counts_by_year) >= 5:
        recent_years = concept.counts_by_year[:5]
        recent_works = sum(y.works_count for y in recent_years)
        recent_citations = sum(y.cited_by_count for y in recent_years)

        print(f"\nRecent Activity (last 5 years):")
        print(f"  Works: {recent_works:,}")
        print(f"  Citations: {recent_citations:,}")

# Example usage
analyze_concept_impact("C154945302")  # Machine learning
```

### Compare concepts

```python
# Import client
from openalex import Concepts
def compare_concepts(concept_ids):
    """Compare multiple concepts side by side."""
    concepts = []
    for cid in concept_ids:
        concepts.append(Concepts()[cid])

    print("Concept Comparison")
    print("-" * 80)
    print(f"{'Concept':<30} {'Level':<6} {'Works':>10} {'Citations':>12} {'H-index':>8}")
    print("-" * 80)

    for c in concepts:
        h_index = c.summary_stats.h_index if c.summary_stats else "N/A"
        print(f"{c.display_name[:29]:<30} "
              f"{c.level:<6} "
              f"{c.works_count:>10,} "
              f"{c.cited_by_count:>12,} "
              f"{h_index:>8}")

# Compare AI-related concepts
compare_concepts([
    "C154945302",  # Machine learning
    "C107457646",  # Deep learning
    "C23123220",   # Artificial neural network
    "C204321447"   # Natural language processing
])
```

### Find concept relationships

```python
# Import client
from openalex import Concepts
def find_concept_relationships(concept_id):
    """Find various relationships for a concept."""

    concept = Concepts()[concept_id]
    print(f"Relationships for: {concept.display_name}")

    # Direct relationships
    if concept.related_concepts:
        print(f"\nDirectly related ({len(concept.related_concepts)}):")
        for related in sorted(concept.related_concepts[:10],
                            key=lambda x: x.score, reverse=True):
            print(f"  - {related.display_name} (score: {related.score:.2f})")

    # Sibling concepts (same parent)
    if concept.ancestors and concept.level > 0:
        parent_id = concept.ancestors[-1].id
        siblings = (
            Concepts()
            .filter(ancestors={"id": parent_id})
            .filter(level=concept.level)
            .filter_not(openalex=concept_id)
            .sort(works_count="desc")
            .get(per_page=10)
        )

        print(f"\nSibling concepts ({siblings.meta.count}):")
        for sibling in siblings.results[:5]:
            print(f"  - {sibling.display_name} ({sibling.works_count:,} works)")

    # Descendant statistics
    all_descendants = Concepts().filter(ancestors={"id": concept_id}).get()
    if all_descendants.meta.count > 1:  # More than just itself
        desc_by_level = (
            Concepts()
            .filter(ancestors={"id": concept_id})
            .group_by("level")
            .get()
        )

        print(f"\nDescendant distribution:")
        for group in sorted(desc_by_level.group_by, key=lambda g: int(g.key)):
            if int(group.key) > concept.level:
                print(f"  Level {group.key}: {group.count} concepts")

find_concept_relationships("C41008148")  # Computer Science
```

## Handling missing data

Many fields can be None or empty:

```python
# Fetch concept
from openalex import Concepts
concept = Concepts()["C71924100"]
# Safe access patterns
if concept.description:
    print(f"Description: {concept.description}")
else:
    print("No description available")

# Handle missing statistics
if concept.summary_stats and concept.summary_stats.h_index is not None:
    print(f"H-index: {concept.summary_stats.h_index}")
else:
    print("H-index not calculated")

# Check for ancestors
if not concept.ancestors:
    print("This is a root concept (no ancestors)")

# Related concepts might be empty
if not concept.related_concepts:
    print("No related concepts listed")

# International names might not exist
intl_names = getattr(concept, 'international', None)
if intl_names and hasattr(intl_names, 'display_name'):
    print(f"Has names in {len(intl_names.display_name)} languages")
```

## The DehydratedConcept object

When concepts appear in other objects (like in work concepts or ancestors), you get a simplified version:

```python
# Get a work to see dehydrated concepts
from openalex import Works
from openalex import Concepts
work = Works()["W2741809807"]

# Access dehydrated concepts in works
if work.concepts:
    for concept in work.concepts:
        # Only these fields are available in dehydrated version:
        print(concept.id)
        print(concept.display_name)
        print(concept.level)
        print(concept.wikidata)
        print(concept.score)  # Confidence score for this tagging

        # To get full details, fetch the complete concept:
        full_concept = Concepts()[concept.id]
        print(f"Full description: {full_concept.description}")
```

**Final reminder: Concepts are deprecated! Please migrate to [Topics](../topics/README.md) for better support and more accurate research classification.**

