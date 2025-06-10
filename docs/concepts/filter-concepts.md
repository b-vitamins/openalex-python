# Filter concepts

{% hint style="warning" %}
⚠️ **DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). We will continue to provide these Concepts for Works, but we will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, we encourage you to look into [Topics](../topics/README.md) instead.
{% endhint %}

You can filter concepts using the Python client:

```python
from openalex import Concepts

# ⚠️ DEPRECATED: Consider using Topics instead
# Create a filtered query for top-level concepts
root_concepts_query = Concepts().filter(level=0)

# Execute the query to get the first page of results
results = root_concepts_query.get()

print(f"Total root concepts: {results.meta.count}")  # Should be 19
print(f"Showing first {len(results.results)} concepts")

# Show some examples
for concept in results.results[:5]:
    print(f"- {concept.display_name}")
    print(f"  Works: {concept.works_count:,}")
```

Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Concepts attribute filters

You can filter using these attributes of the [`Concept`](concept-object.md) object:

### Basic attribute filters

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Filter by cited_by_count
highly_cited = Concepts().filter(cited_by_count=1000000).get()  # Exactly 1M
very_highly_cited = Concepts().filter_gt(cited_by_count=10000000).get()  # More than 10M

# Filter by works_count
large_concepts = Concepts().filter_gt(works_count=100000).get()  # More than 100k works
small_concepts = Concepts().filter_lt(works_count=1000).get()  # Fewer than 1k works

# Filter by level (0-5)
root_level = Concepts().filter(level=0).get()  # 19 root concepts
mid_level = Concepts().filter(level=3).get()  # Mid-level specificity
leaf_level = Concepts().filter(level=5).get()  # Most specific concepts

# Filter by specific IDs
specific_ids = Concepts().filter(
    openalex=["C71924100", "C41008148"]
).get()
```

### Hierarchical filters

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Filter by ancestors
# Get all descendants of Computer Science (C41008148)
cs_descendants = Concepts().filter(ancestors={"id": "C41008148"}).get()

# Get direct children only (one level down)
cs_children = (
    Concepts()
    .filter(ancestors={"id": "C41008148"})
    .filter(level=1)  # CS is level 0, so children are level 1
    .get()
)

# Find concepts under multiple ancestors
interdisciplinary = (
    Concepts()
    .filter(ancestors={"id": ["C41008148", "C71924100"]})  # CS AND Medicine
    .get()
)
```

### Summary statistics filters

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Filter by h-index
high_h_index = Concepts().filter_gt(summary_stats={"h_index": 200}).get()

# Filter by i10-index
productive = Concepts().filter_gt(summary_stats={"i10_index": 10000}).get()

# Filter by 2-year mean citedness
high_impact = Concepts().filter_gt(
    summary_stats={"2yr_mean_citedness": 5.0}
).get()

# Combine metrics
elite_concepts = (
    Concepts()
    .filter_gt(summary_stats={"h_index": 300})
    .filter_gt(summary_stats={"i10_index": 50000})
    .filter_gt(works_count=100000)
    .get()
)
```

## Convenience filters

These filters aren't attributes of the Concept object, but they're handy:

### Boolean filters

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Has Wikidata ID (currently all concepts have one)
with_wikidata = Concepts().filter(has_wikidata=True).get()
without_wikidata = Concepts().filter(has_wikidata=False).get()

print(f"With Wikidata: {with_wikidata.meta.count:,}")  # Should be ~65,000
print(f"Without Wikidata: {without_wikidata.meta.count:,}")  # Should be 0
```

### Text search filters

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Search in display names
ai_search = Concepts().filter(
    display_name={"search": "artificial intelligence"}
).get()

# Alternative: use search_filter
medical_search = Concepts().search_filter(display_name="medical").get()

# Default search (searches display_name and description)
default_search = Concepts().filter(
    default={"search": "machine learning"}
).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# High-impact computer science concepts
high_impact_cs = (
    Concepts()
    .filter(ancestors={"id": "C41008148"})  # Under Computer Science
    .filter_gt(works_count=10000)
    .filter_gt(summary_stats={"h_index": 100})
    .sort(cited_by_count="desc")
    .get()
)

# Mid-level concepts with many works
active_mid_level = (
    Concepts()
    .filter(level=3)  # Mid-level specificity
    .filter_gt(works_count=50000)
    .sort(works_count="desc")
    .get(per_page=50)
)

# Specific branch of the tree
ml_concepts = (
    Concepts()
    .filter(ancestors={"id": "C119857082"})  # Machine Learning ancestor
    .filter_gt(level=2)  # More specific than level 2
    .get()
)
```

### NOT operations

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Concepts NOT under Computer Science
non_cs = Concepts().filter_not(ancestors={"id": "C41008148"}).get()

# Non-root concepts
non_root = Concepts().filter_not(level=0).get()

# Concepts with limited impact
low_impact = Concepts().filter_not(
    summary_stats={"h_index": {"gte": 50}}
).get()
```

### Range queries

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Mid-level concepts (levels 2-4)
mid_levels = (
    Concepts()
    .filter_gte(level=2)
    .filter_lte(level=4)
    .get()
)

# Moderate activity (10k-100k works)
moderate_activity = (
    Concepts()
    .filter_gt(works_count=10000)
    .filter_lt(works_count=100000)
    .get()
)
```

## Practical examples

### Example 1: Navigate concept tree

```python
# ⚠️ DEPRECATED: Consider using Topics instead
def explore_concept_branch(concept_id, max_depth=3):
    """Explore a branch of the concept tree."""
    
    # Get the root concept
    root = Concepts()[concept_id]
    print(f"Root: {root.display_name} (Level {root.level})")
    
    # Recursive function to explore descendants
    def get_descendants(ancestor_id, current_level, max_level):
        if current_level > max_level:
            return
        
        descendants = (
            Concepts()
            .filter(ancestors={"id": ancestor_id})
            .filter(level=current_level)
            .sort(works_count="desc")
            .get(per_page=10)
        )
        
        indent = "  " * current_level
        for desc in descendants.results[:5]:
            print(f"{indent}- {desc.display_name} ({desc.works_count:,} works)")
            # Recursively get children
            get_descendants(desc.id, current_level + 1, max_level)
    
    # Start exploration
    get_descendants(root.id, root.level + 1, root.level + max_depth)

# Explore Computer Science branch
explore_concept_branch("C41008148")
```

### Example 2: Find interdisciplinary concepts

```python
# ⚠️ DEPRECATED: Consider using Topics instead
def find_interdisciplinary_concepts():
    """Find concepts that bridge multiple fields."""
    
    # Get all root concepts
    root_concepts = Concepts().filter(level=0).get(per_page=25)
    
    # For each pair of roots, find concepts with both as ancestors
    interdisciplinary = []
    
    for i, root1 in enumerate(root_concepts.results):
        for root2 in root_concepts.results[i+1:]:
            # Find concepts descended from both
            shared = (
                Concepts()
                .filter(ancestors={"id": [root1.id, root2.id]})
                .get()
            )
            
            if shared.meta.count > 0:
                print(f"\n{root1.display_name} ∩ {root2.display_name}: {shared.meta.count} concepts")
                for concept in shared.results[:3]:
                    print(f"  - {concept.display_name}")

find_interdisciplinary_concepts()
```

### Example 3: Analyze research trends

```python
# ⚠️ DEPRECATED: Consider using Topics instead
def analyze_research_trends(min_works=50000):
    """Find rapidly growing research areas."""
    
    # Get active concepts
    active_concepts = (
        Concepts()
        .filter_gt(works_count=min_works)
        .filter_gt(level=1)  # Not too general
        .get(per_page=100)
    )
    
    print(f"Analyzing {active_concepts.meta.count} active concepts...")
    
    # For each concept, look at growth metrics
    growing_concepts = []
    for concept in active_concepts.results:
        if concept.counts_by_year and len(concept.counts_by_year) >= 2:
            recent = concept.counts_by_year[0]
            previous = concept.counts_by_year[1]
            
            if previous.works_count > 0:
                growth_rate = ((recent.works_count - previous.works_count) / 
                              previous.works_count * 100)
                
                if growth_rate > 20:  # 20% growth
                    growing_concepts.append({
                        "concept": concept,
                        "growth_rate": growth_rate,
                        "recent_works": recent.works_count
                    })
    
    # Sort by growth rate
    growing_concepts.sort(key=lambda x: x["growth_rate"], reverse=True)
    
    print("\nFastest growing concepts:")
    for item in growing_concepts[:10]:
        concept = item["concept"]
        print(f"\n{concept.display_name} (Level {concept.level})")
        print(f"  Growth rate: {item['growth_rate']:.1f}%")
        print(f"  Recent works: {item['recent_works']:,}")

analyze_research_trends()
```

### Example 4: Concept similarity

```python
# ⚠️ DEPRECATED: Consider using Topics instead
def find_similar_concepts(concept_id):
    """Find concepts similar to a given concept."""
    
    source = Concepts()[concept_id]
    
    # Strategy 1: Same parent
    if source.ancestors:
        parent_id = source.ancestors[-1].id  # Immediate parent
        siblings = (
            Concepts()
            .filter(ancestors={"id": parent_id})
            .filter(level=source.level)
            .filter_not(openalex=concept_id)
            .sort(works_count="desc")
            .get()
        )
        
        print(f"Sibling concepts of {source.display_name}:")
        for sibling in siblings.results[:5]:
            print(f"  - {sibling.display_name} ({sibling.works_count:,} works)")
    
    # Strategy 2: Use related_concepts if available
    if hasattr(source, 'related_concepts') and source.related_concepts:
        print(f"\nRelated concepts:")
        for related in source.related_concepts[:5]:
            print(f"  - {related.display_name} (score: {related.score:.2f})")

find_similar_concepts("C154945302")  # Try with "Machine learning"
```

## Performance tips

Since there are ~65,000 concepts:

1. **Fetching all is feasible**: You can get all concepts in ~325 API calls
2. **Consider the hierarchy**: Use level filters to narrow results
3. **Cache the tree structure**: Concept relationships change rarely
4. **Use ancestors for branches**: Efficiently get entire subtrees

```python
# ⚠️ DEPRECATED: Consider using Topics instead
# Example: Efficiently analyze concept distribution
def concept_distribution_summary():
    # Use group_by instead of fetching all concepts
    by_level = Concepts().group_by("level").get()
    
    print("Concepts by level:")
    for group in by_level.group_by:
        print(f"  Level {group.key}: {group.count:,}")
    
    # Get root distribution
    roots = Concepts().filter(level=0).get(per_page=25)
    print(f"\nRoot concepts: {roots.meta.count}")
    for root in roots.results:
        # Count descendants
        descendants = Concepts().filter(ancestors={"id": root.id}).get()
        print(f"  {root.display_name}: {descendants.meta.count:,} descendants")
```

**⚠️ Final reminder: Concepts are deprecated! Please use [Topics](../topics/README.md) for all new projects.**
