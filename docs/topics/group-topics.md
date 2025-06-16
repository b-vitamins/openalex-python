# Group topics

You can group topics to get aggregated statistics without fetching individual topic records:

```python
from openalex import Topics

# Create a query that groups topics by domain
domain_stats_query = Topics().group_by("domain.id")

# Execute the query to get COUNTS, not individual topics
domain_stats = domain_stats_query.get()

# This returns aggregated statistics, NOT topic objects!
print("Topics by domain:")
for group in domain_stats.group_by:
    # Each group has a 'key' (the domain ID) and 'count'
    print(f"  Domain {group.key}: {group.count:,} topics")
```

**Key point**: `group_by()` returns COUNTS, not the actual topics. This is efficient for analytics.

## Understanding group_by results

```python
# The result structure is different from regular queries
from openalex import Topics
result = Topics().group_by("field.id").get()

print(result.results)  # Empty list - no individual topics returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
print("Topics by field:")
for group in result.group_by:
    percentage = (group.count / result.meta.count) * 100
    print(f"  Field {group.key}: {group.count:,} topics ({percentage:.1f}%)")
```

## Common grouping operations

### Hierarchical grouping

```python
from openalex import Topics

# Group by domain (highest level)
by_domain = Topics().group_by("domain.id").get()
# Shows distribution across major research areas

# Group by field (second level)
by_field = Topics().group_by("field.id").get()
# More granular than domain

# Group by subfield (third level)
by_subfield = Topics().group_by("subfield.id").get()
# Even more specific categorization

# Show hierarchy distribution
print(f"Domains: {len(by_domain.group_by)}")
print(f"Fields: {len(by_field.group_by)}")
print(f"Subfields: {len(by_subfield.group_by)}")
```

### Activity-based grouping

```python
from openalex import Topics

# Works count distribution
works_dist = Topics().group_by("works_count").get()
# Note: Creates many groups (one per unique count)

# Citation count distribution
citation_dist = Topics().group_by("cited_by_count").get()
# Also creates many unique groups
```

## Combining filters with group_by

Group_by becomes more insightful when combined with filters:

```python
from openalex import Topics

# Field distribution within a specific domain
health_fields = (
    Topics()
    .filter(domain={"id": 4})  # Health Sciences
    .group_by("field.id")
    .get()
)
print("Fields within Health Sciences:")
for group in health_fields.group_by:
    print(f"  Field {group.key}: {group.count} topics")

# Subfield distribution for active topics
active_subfields = (
    Topics()
    .filter_gt(works_count=5000)
    .group_by("subfield.id")
    .get()
)
print("Subfields with active topics (>5k works):")
for group in active_subfields.group_by[:10]:
    print(f"  Subfield {group.key}: {group.count} active topics")

# Domain distribution for highly cited topics
high_impact_domains = (
    Topics()
    .filter_gt(cited_by_count=1000000)
    .group_by("domain.id")
    .get()
)
```

## Multi-dimensional grouping

You can group by two dimensions:

```python
from openalex import Topics

# Count topics by domain
domain_counts = Topics().group_by("domain.id").get()

for group in domain_counts.group_by:
    print(f"Domain {group.key}: {group.count} topics")
```

## Practical examples

### Example 1: Analyze research landscape

```python
from openalex import Topics

def analyze_research_landscape():
    """Comprehensive analysis of the topic hierarchy."""
    
    # Get counts at each level
    domains = Topics().group_by("domain.id").get()
    fields = Topics().group_by("field.id").get()
    subfields = Topics().group_by("subfield.id").get()
    
    print("OpenAlex Research Landscape")
    print("=" * 40)
    print(f"Total topics: ~{Topics().get().meta.count:,}")
    print(f"Domains: {len(domains.group_by)}")
    print(f"Fields: {len(fields.group_by)}")
    print(f"Subfields: {len(subfields.group_by)}")
    
    # Show domain distribution
    print("\nTopics per domain:")
    # Since we don't have domain names in the group_by result,
    # we'd need to fetch some topics to get the names
    for group in domains.group_by:
        # Get one topic from this domain to get its name
        sample = Topics().filter(domain={"id": group.key}).get(per_page=1)
        if sample.results:
            domain_name = sample.results[0].domain.display_name
            print(f"  {domain_name}: {group.count} topics")

analyze_research_landscape()
```

### Example 2: Field concentration analysis

```python
from openalex import Topics

def analyze_field_concentration():
    """Analyze how topics are concentrated across fields."""
    
    # Group by field
    by_field = Topics().group_by("field.id").get()
    
    # Sort groups by count
    sorted_fields = sorted(
        by_field.group_by,
        key=lambda g: g.count,
        reverse=True
    )
    
    # Calculate concentration
    total_topics = sum(g.count for g in by_field.group_by)
    top10_topics = sum(g.count for g in sorted_fields[:10])
    concentration = (top10_topics / total_topics) * 100
    
    print(f"Field Concentration Analysis")
    print(f"Total fields: {len(by_field.group_by)}")
    print(f"Top 10 fields contain {concentration:.1f}% of all topics")
    
    print("\nTop 10 fields by topic count:")
    for i, group in enumerate(sorted_fields[:10], 1):
        # Get field name
        sample = Topics().filter(field={"id": group.key}).get(per_page=1)
        if sample.results:
            field_name = sample.results[0].field.display_name
            percentage = (group.count / total_topics) * 100
            print(f"  {i}. {field_name}: {group.count} topics ({percentage:.1f}%)")

analyze_field_concentration()
```

### Example 3: Activity distribution

```python
from openalex import Topics

def analyze_topic_activity():
    """Analyze distribution of research activity across topics."""
    
    # Define activity tiers
    tiers = [
        ("Inactive", 0, 100),
        ("Low", 100, 1000),
        ("Moderate", 1000, 5000),
        ("Active", 5000, 20000),
        ("Very Active", 20000, 100000),
        ("Hyper Active", 100000, float('inf'))
    ]
    
    print("Topic Activity Distribution")
    print("=" * 40)
    
    total_topics = Topics().get().meta.count
    
    for tier_name, min_works, max_works in tiers:
        # Build filter
        tier_query = Topics()
        if min_works > 0:
            tier_query = tier_query.filter_gt(works_count=min_works)
        if max_works < float('inf'):
            tier_query = tier_query.filter_lt(works_count=max_works)
        
        # Get count
        tier_result = tier_query.get()
        count = tier_result.meta.count
        percentage = (count / total_topics) * 100
        
        # Get domain distribution for this tier
        domain_dist = tier_query.group_by("domain.id").get()
        
        print(f"\n{tier_name} ({min_works:,}-{max_works:,} works):")
        print(f"  Topics: {count} ({percentage:.1f}%)")
        print(f"  Distributed across {len(domain_dist.group_by)} domains")

analyze_topic_activity()
```

### Example 4: Hierarchical exploration

```python
from openalex import Topics

def explore_hierarchy(domain_id=None):
    """Explore the topic hierarchy starting from a domain."""
    
    if domain_id:
        # Get fields in this domain
        fields_in_domain = (
            Topics()
            .filter(domain={"id": domain_id})
            .group_by("field.id")
            .get()
        )
        
        print(f"Domain {domain_id} contains {len(fields_in_domain.group_by)} fields")
        
        # For each field, count subfields
        for field_group in fields_in_domain.group_by[:5]:  # Top 5 fields
            subfields_in_field = (
                Topics()
                .filter(domain={"id": domain_id})
                .filter(field={"id": field_group.key})
                .group_by("subfield.id")
                .get()
            )
            
            # Get field name from a sample topic
            sample = (
                Topics()
                .filter(field={"id": field_group.key})
                .get(per_page=1)
            )
            if sample.results:
                field_name = sample.results[0].field.display_name
                print(f"\n  Field: {field_name}")
                print(f"    Topics: {field_group.count}")
                print(f"    Subfields: {len(subfields_in_field.group_by)}")
    else:
        # Show all domains
        all_domains = Topics().group_by("domain.id").get()
        print(f"Total domains: {len(all_domains.group_by)}")
        
        for domain_group in all_domains.group_by:
            # Get domain name
            sample = Topics().filter(domain={"id": domain_group.key}).get(per_page=1)
            if sample.results:
                domain_name = sample.results[0].domain.display_name
                print(f"\nDomain: {domain_name} (ID: {domain_group.key})")
                print(f"  Topics: {domain_group.count}")

# Explore all domains
explore_hierarchy()

# Explore a specific domain
explore_hierarchy(domain_id=4)  # Health Sciences
```

## Sorting grouped results

Control how results are ordered:

```python
from openalex import Topics

# Default: sorted by count (descending)
default_sort = Topics().group_by("field.id").get()
# Fields with most topics first

# Sort by key instead of count
by_id = Topics().group_by("domain.id").sort(key="asc").get()
# Domains in ID order (1, 2, 3, 4...)

# Sort by count ascending (smallest groups first)
smallest_first = Topics().group_by("subfield.id").sort(count="asc").get()
# Subfields with fewest topics first
```

## Important notes

1. **No individual topics returned**: `group_by()` only returns counts
2. **Very efficient**: Even faster than fetching topics (which is already fast)
3. **Limited dimensions**: Maximum 2 fields for grouping
4. **Perfect for tiny datasets**: With ~4,500 topics, all operations are instant
5. **Great for hierarchy analysis**: Understand the topic classification system

When you need statistics about topics, always prefer `group_by()` over fetching and counting individual records!

## Quick analysis with all topics

Since the dataset is so small, you can also do grouping locally:

```python
# Get all topics once
from openalex import Topics
all_topics = list(Topics().all(per_page=200))

# Now do local grouping
from collections import Counter

# Group by domain locally
domain_counts = Counter(t.domain.display_name for t in all_topics)
print("Topics by domain (local count):")
for domain, count in domain_counts.most_common():
    print(f"  {domain}: {count}")

# Group by first keyword
keyword_counts = Counter(
    t.keywords[0] for t in all_topics if t.keywords
)
print("\nMost common first keywords:")
for keyword, count in keyword_counts.most_common(10):
    print(f"  {keyword}: {count}")
```
