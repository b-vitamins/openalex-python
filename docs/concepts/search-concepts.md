# Search concepts

{% hint style="warning" %}
⚠️ **DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). We will continue to provide these Concepts for Works, but we will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, we encourage you to look into [Topics](../topics/README.md) instead.
{% endhint %}

The best way to search for concepts is to use the `search` method, which searches the `display_name` and `description` fields:

```python
from openalex import Concepts

# ⚠️ DEPRECATED: Consider using Topics instead
# Search for concepts related to artificial intelligence
ai_search = Concepts().search("artificial intelligence")

# Execute to get the first page of results
results = ai_search.get()

print(f"Found {results.meta.count} concepts matching 'artificial intelligence'")
for concept in results.results[:5]:
    print(f"\n{concept.display_name} (Level {concept.level})")
    if concept.description:
        print(f"  {concept.description[:100]}...")
    print(f"  Works: {concept.works_count:,}")
```

## How concept search works

The search checks multiple fields:

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# This searches display_name AND description
ml_results = Concepts().search("machine learning").get()

# This will find concepts where:
# - "machine learning" appears in the display_name
# - "machine learning" is mentioned in the description

# Search is flexible with variations
ai_results = Concepts().search("AI").get()
# May find "Artificial Intelligence", "AI applications", etc.
```

Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# Search only in display_name
name_only = Concepts().filter(
    display_name={"search": "medical"}
).get()

# Or use the search_filter method
name_search = Concepts().search_filter(
    display_name="computer"
).get()

# Default search (searches display_name and description)
default_search = Concepts().filter(
    default={"search": "quantum computing"}
).get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` only | `.search_filter(display_name="...")` |
| `default.search` | `display_name` and `description` | `.filter(default={"search": "..."})` |

## Autocomplete concepts

Create a fast type-ahead search experience:

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# Get autocomplete suggestions
suggestions = Concepts().autocomplete("comp")

# Returns fast, lightweight results with descriptions as hints
for concept in suggestions.results:
    print(f"{concept.display_name}")
    print(f"  Hint: {concept.hint}")  # Description as hint
    print(f"  Works: {concept.works_count:,}")
    print(f"  Citations: {concept.cited_by_count:,}")
    if concept.external_id:  # Wikidata ID
        print(f"  Wikidata: {concept.external_id}")
```

Example output:
```
Computer science
  Hint: theoretical study of the formal foundation enabling the automated processing...
  Works: 76,722,605
  Citations: 392,939,277
  Wikidata: https://www.wikidata.org/wiki/Q21198

Computational biology  
  Hint: interdisciplinary field that applies computational methods to biological problems
  Works: 1,234,567
  Citations: 12,345,678
  Wikidata: https://www.wikidata.org/wiki/Q844976
```

## Combining search with filters

Search is most powerful when combined with filters:

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# Search for AI concepts at specific levels
ai_subfields = (
    Concepts()
    .search("artificial intelligence")
    .filter(level=2)  # Subfield level
    .get(per_page=20)
)

print(f"Found {ai_subfields.meta.count} AI subfields")

# Search for medical concepts with many works
active_medical = (
    Concepts()
    .search("medical")
    .filter_gt(works_count=50000)
    .sort(works_count="desc")
    .get()
)

# Search within a specific branch
cs_concepts = (
    Concepts()
    .search("algorithm")
    .filter(ancestors={"id": "C41008148"})  # Under Computer Science
    .get()
)

# Find emerging concepts
emerging = (
    Concepts()
    .search("quantum")
    .filter_gt(works_count=1000)
    .filter_lt(works_count=10000)
    .filter_gt(level=2)  # Not too general
    .get()
)
```

## Search strategies

### Finding concepts in a domain

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
def search_in_domain(search_term, domain_concept_id):
    """Search for concepts within a specific domain."""
    
    results = (
        Concepts()
        .search(search_term)
        .filter(ancestors={"id": domain_concept_id})
        .get(per_page=20)
    )
    
    print(f"'{search_term}' concepts in domain:")
    for concept in results.results:
        # Show the path from root to this concept
        path = " → ".join([a.display_name for a in concept.ancestors])
        print(f"\n{concept.display_name}")
        print(f"  Path: {path} → {concept.display_name}")
        print(f"  Level: {concept.level}")
        print(f"  Works: {concept.works_count:,}")

# Search for learning concepts in Computer Science
search_in_domain("learning", "C41008148")

# Search for therapy concepts in Medicine
search_in_domain("therapy", "C71924100")
```

### Multi-level search

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
def hierarchical_search(search_term):
    """Search at different levels of the hierarchy."""
    
    print(f"Searching for '{search_term}' at different levels:")
    
    for level in range(6):  # Levels 0-5
        results = (
            Concepts()
            .search(search_term)
            .filter(level=level)
            .get(per_page=5)
        )
        
        if results.meta.count > 0:
            print(f"\nLevel {level} ({results.meta.count} results):")
            for concept in results.results[:3]:
                print(f"  - {concept.display_name} ({concept.works_count:,} works)")

hierarchical_search("network")
```

### Related concept discovery

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
def discover_related_concepts(concept_id):
    """Find concepts related to a given concept through various methods."""
    
    source = Concepts()[concept_id]
    print(f"Finding concepts related to: {source.display_name}")
    
    # Method 1: Search using the concept name
    name_search = Concepts().search(source.display_name).filter_not(openalex=concept_id).get()
    
    print(f"\nConcepts with similar names:")
    for concept in name_search.results[:5]:
        print(f"  - {concept.display_name} (Level {concept.level})")
    
    # Method 2: Get siblings (same parent)
    if source.ancestors:
        parent_id = source.ancestors[-1].id
        siblings = (
            Concepts()
            .filter(ancestors={"id": parent_id})
            .filter(level=source.level)
            .filter_not(openalex=concept_id)
            .get(per_page=5)
        )
        
        print(f"\nSibling concepts:")
        for concept in siblings.results:
            print(f"  - {concept.display_name}")
    
    # Method 3: Use related_concepts if available
    if hasattr(source, 'related_concepts') and source.related_concepts:
        print(f"\nDirectly related concepts:")
        for related in source.related_concepts[:5]:
            print(f"  - {related.display_name} (score: {related.score:.2f})")

discover_related_concepts("C154945302")  # Machine learning
```

## Common search patterns

### Finding interdisciplinary concepts

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# Bioinformatics, computational biology, etc.
bio_comp = (
    Concepts()
    .search("computational OR informatics")
    .filter(ancestors={"id": ["C86803240", "C41008148"]})  # Biology AND CS
    .get()
)

# Medical AI
medical_ai = (
    Concepts()
    .search("artificial intelligence OR machine learning")
    .filter(ancestors={"id": "C71924100"})  # Under Medicine
    .get()
)

# Environmental economics
env_econ = (
    Concepts()
    .search("environmental OR climate")
    .filter(ancestors={"id": "C162324750"})  # Under Economics
    .get()
)
```

### Research trend discovery

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# Find emerging concepts with specific terms
emerging_tech = (
    Concepts()
    .search("blockchain OR cryptocurrency OR NFT OR metaverse")
    .filter_gt(works_count=100)
    .filter_lt(works_count=10000)
    .sort(works_count="desc")
    .get()
)

# Climate-related concepts
climate_concepts = (
    Concepts()
    .search("climate OR warming OR carbon OR sustainability")
    .filter_gt(level=2)  # Not too general
    .filter_gt(works_count=1000)
    .get()
)
```

## Search tips

1. **Use both name and description**: Default search covers both fields
2. **Try different terms**: "AI" vs "artificial intelligence"
3. **Consider the hierarchy**: Add level filters for specificity
4. **Use ancestors**: Search within specific domains
5. **Check related concepts**: Explore the concept graph

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
# Example: Comprehensive concept search
def comprehensive_search(search_terms, min_works=1000):
    """Search with multiple strategies."""
    
    all_results = {}
    
    for term in search_terms:
        # General search
        general = Concepts().search(term).filter_gt(works_count=min_works).get()
        
        # Collect unique concepts
        for concept in general.results:
            if concept.id not in all_results:
                all_results[concept.id] = concept
    
    # Sort by relevance (works_count as proxy)
    sorted_concepts = sorted(
        all_results.values(),
        key=lambda c: c.works_count,
        reverse=True
    )
    
    print(f"Found {len(sorted_concepts)} unique concepts")
    for concept in sorted_concepts[:20]:
        print(f"\n{concept.display_name} (Level {concept.level})")
        if concept.ancestors:
            path = " → ".join([a.display_name for a in concept.ancestors])
            print(f"  Path: {path}")
        print(f"  Works: {concept.works_count:,}")

# Search for AI/ML concepts comprehensively
comprehensive_search([
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "AI", "ML"
])
```

**⚠️ Final reminder: Concepts are deprecated! Please migrate to [Topics](../topics/README.md) for better support and accuracy.**
