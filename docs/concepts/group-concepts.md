# Group concepts

{% hint style="warning" %}
⚠️ **DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). We will continue to provide these Concepts for Works, but we will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, we encourage you to look into [Topics](../topics/README.md) instead.
{% endhint %}

You can group concepts to get aggregated statistics without fetching individual concept records:

```python
from openalex import Concepts

# ⚠️ DEPRECATED: Consider using Topics instead
# Create a query that groups concepts by level
level_stats_query = Concepts().group_by("level")

# Execute the query to get COUNTS, not individual concepts
level_stats = level_stats_query.get()

# This returns aggregated statistics, NOT concept objects!
print("Concepts by level:")
for group in level_stats.group_by:
    # Each group has a 'key' (the level) and 'count'
    print(f"  Level {group.key}: {group.count:,} concepts")
```

**Key point**: `group_by()` returns COUNTS, not the actual concepts. This is efficient for analytics.

## Understanding group_by results

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
result = Concepts().group_by("level").get()

print(result.results)  # Empty list - no individual concepts returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
print("Concept hierarchy distribution:")
total_concepts = sum(g.count for g in result.group_by)
for group in result.group_by:
    percentage = (group.count / total_concepts) * 100
    print(f"  Level {group.key}: {group.count:,} concepts ({percentage:.1f}%)")
```

## Common grouping operations

### Hierarchical grouping

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
# Group by level (0-5)
by_level = Concepts().group_by("level").get()
# Shows how concepts are distributed across hierarchy levels

# Group by ancestor
by_ancestor = Concepts().group_by("ancestors.id").get()
# Shows which parent concepts have the most descendants
# Note: This creates many groups (one per unique ancestor)

# Group by presence of Wikidata ID
by_wikidata = Concepts().group_by("has_wikidata").get()
# Should show all concepts have Wikidata IDs
```

### Activity-based grouping

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
# Works count distribution
works_dist = Concepts().group_by("works_count").get()
# Note: Creates many groups (one per unique count)

# Citation count distribution
citation_dist = Concepts().group_by("cited_by_count").get()
# Also creates many unique groups

# H-index distribution
h_index_dist = Concepts().group_by("summary_stats.h_index").get()

# i10-index distribution
i10_dist = Concepts().group_by("summary_stats.i10_index").get()

# 2-year mean citedness
impact_dist = Concepts().group_by("summary_stats.2yr_mean_citedness").get()
```

## Combining filters with group_by

Group_by becomes more insightful when combined with filters:

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
# Level distribution for Computer Science descendants
cs_levels = (
    Concepts()
    .filter(ancestors={"id": "C41008148"})  # Computer Science
    .group_by("level")
    .get()
)
print("CS concept distribution by level:")
for group in cs_levels.group_by:
    print(f"  Level {group.key}: {group.count} concepts")

# Active concepts by level
active_by_level = (
    Concepts()
    .filter_gt(works_count=10000)
    .group_by("level")
    .get()
)
print("Active concepts (>10k works) by level:")
for group in active_by_level.group_by:
    print(f"  Level {group.key}: {group.count} concepts")

# High-impact concepts by level
high_impact_levels = (
    Concepts()
    .filter_gt(summary_stats={"h_index": 100})
    .group_by("level")
    .get()
)
```

## Multi-dimensional grouping

You can group by two dimensions:

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
# Level and ancestor combination
level_ancestor = Concepts().group_by("level", "ancestors.id").get()

# This shows distribution of concepts by level within each ancestor branch
for group in level_ancestor.group_by[:20]:
    # Keys are pipe-separated for multi-dimensional groups
    level, ancestor_id = group.key.split('|')
    print(f"Level {level}, Ancestor {ancestor_id}: {group.count} concepts")
```

## Practical examples

### Example 1: Analyze concept hierarchy

```python
# ⚠️ DEPRECATED: Consider using Topics instead
from openalex import Concepts
def analyze_concept_hierarchy():
    """Comprehensive analysis of the concept tree structure."""
    
    # Get distribution by level
    by_level = Concepts().group_by("level").get()
    
    print("Concept Hierarchy Analysis")
    print("=" * 40)
    
    # Show level distribution
    print("\nConcepts per level:")
    for group in sorted(by_level.group_by, key=lambda g: int(g.key)):
        print(f"  Level {group.key}: {group.count:,} concepts")
    
    # Analyze root concepts
    root_concepts = Concepts().filter(level=0).get(per_page=25)
    print(f"\nRoot concepts: {root_concepts.meta.count}")
    
    # For each root, count descendants
    print("\nDescendants per root concept:")
    for root in root_concepts.results:
        descendants = Concepts().filter(ancestors={"id": root.id}).get()
        print(f"  {root.display_name}: {descendants.meta.count:,} descendants")

analyze_concept_hierarchy()
```

### Example 2: Research activity distribution

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
def analyze_research_activity():
    """Analyze how research activity is distributed across concepts."""
    
    # Define activity tiers based on works count
    tiers = [
        ("Inactive", 0, 100),
        ("Low", 100, 1000),
        ("Moderate", 1000, 10000),
        ("Active", 10000, 100000),
        ("Very Active", 100000, 1000000),
        ("Hyper Active", 1000000, float('inf'))
    ]
    
    print("Research Activity Distribution")
    print("=" * 40)
    
    total_concepts = Concepts().get().meta.count
    
    for tier_name, min_works, max_works in tiers:
        # Build filter
        tier_query = Concepts()
        if min_works > 0:
            tier_query = tier_query.filter_gt(works_count=min_works)
        if max_works < float('inf'):
            tier_query = tier_query.filter_lt(works_count=max_works)
        
        # Get count and level distribution
        tier_result = tier_query.get()
        level_dist = tier_query.group_by("level").get()
        
        count = tier_result.meta.count
        percentage = (count / total_concepts) * 100
        
        print(f"\n{tier_name} ({min_works:,}-{max_works:,} works):")
        print(f"  Concepts: {count:,} ({percentage:.1f}%)")
        print(f"  Level distribution:", end="")
        for group in sorted(level_dist.group_by, key=lambda g: int(g.key)):
            print(f" L{group.key}:{group.count}", end="")
        print()

analyze_research_activity()
```

### Example 3: Impact analysis

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
def analyze_concept_impact():
    """Analyze impact metrics across the concept hierarchy."""
    
    # Group by h-index ranges
    h_index_ranges = [
        ("Low", 0, 50),
        ("Medium", 50, 100),
        ("High", 100, 200),
        ("Very High", 200, 500),
        ("Elite", 500, float('inf'))
    ]
    
    print("Concept Impact Analysis (by h-index)")
    print("=" * 40)
    
    for range_name, min_h, max_h in h_index_ranges:
        # Build query
        query = Concepts()
        if min_h > 0:
            query = query.filter_gte(summary_stats={"h_index": min_h})
        if max_h < float('inf'):
            query = query.filter_lt(summary_stats={"h_index": max_h})
        
        # Get results
        result = query.get()
        level_dist = query.group_by("level").get()
        
        if result.meta.count > 0:
            print(f"\n{range_name} impact (h-index {min_h}-{max_h}):")
            print(f"  Concepts: {result.meta.count:,}")
            
            # Show some examples
            examples = query.sort(summary_stats={"h_index": "desc"}).get(per_page=3)
            print("  Examples:")
            for concept in examples.results:
                h_index = concept.summary_stats.h_index if concept.summary_stats else "N/A"
                print(f"    - {concept.display_name} (h={h_index})")

analyze_concept_impact()
```

### Example 4: Domain comparison

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
def compare_domains():
    
    # Get all root concepts
    roots = Concepts().filter(level=0).get(per_page=25)
    
    print("Domain Comparison")
    print("=" * 60)
    print(f"{'Domain':<30} {'Descendants':<12} {'Avg Level':<10}")
    print("-" * 60)
    
    for root in roots.results:
        # Get all descendants
        descendants = (
            Concepts()
            .filter(ancestors={"id": root.id})
            .get()
        )
        
        # Get level distribution
        level_dist = (
            Concepts()
            .filter(ancestors={"id": root.id})
            .group_by("level")
            .get()
        )
        
        # Calculate average level
        total_concepts = 0
        weighted_sum = 0
        for group in level_dist.group_by:
            level = int(group.key)
            count = group.count
            total_concepts += count
            weighted_sum += level * count
        
        avg_level = weighted_sum / total_concepts if total_concepts > 0 else 0
        
        print(f"{root.display_name[:29]:<30} "
              f"{descendants.meta.count:<12,} "
              f"{avg_level:<10.2f}")

compare_domains()
```

## Sorting grouped results

Control how results are ordered:

```python
from openalex import Concepts
# ⚠️ DEPRECATED: Consider using Topics instead
# Default: sorted by count (descending)
default_sort = Concepts().group_by("level").get()
# Most populous levels first

# Sort by key instead of count
by_level_order = Concepts().group_by("level").sort(key="asc").get()
# Level 0, 1, 2, 3, 4, 5 in order

# Sort by count ascending (smallest groups first)
smallest_first = Concepts().group_by("ancestors.id").sort(count="asc").get()
# Ancestors with fewest descendants first
```

## Important notes

1. **No individual concepts returned**: `group_by()` only returns counts
2. **Efficient for analytics**: Much faster than fetching all concepts
3. **Limited dimensions**: Maximum 2 fields for grouping
4. **Good for hierarchy analysis**: Understand the concept tree structure
5. **DEPRECATED**: Remember to use Topics for new projects!

When you need statistics about concepts, prefer `group_by()` over fetching and counting individual records.

**⚠️ Final reminder: Concepts are deprecated! Please use [Topics](../topics/README.md) instead for all new development.**
