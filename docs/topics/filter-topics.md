# Filter topics

You can filter topics using the Python client:

```python
from openalex import Topics

# Create a filtered query for topics in the "Epidemiology" subfield
epidemiology_topics_query = Topics().filter(subfield={"id": 2713})

# Execute the query to get the first page of results
results = epidemiology_topics_query.get()

print(f"Total Epidemiology topics: {results.meta.count}")
print(f"Showing first {len(results.results)} topics")

# Show some examples
for topic in results.results[:5]:
    print(f"- {topic.display_name}")
    print(f"  Works: {topic.works_count:,}")
```

Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Topics attribute filters

You can filter using these attributes of the [`Topic`](topic-object.md) object:

### Basic attribute filters

```python
from openalex import Topics

# Filter by cited_by_count
highly_cited = Topics().filter(cited_by_count=1000000).get()  # Exactly 1M
very_highly_cited = Topics().filter_gt(cited_by_count=10000000).get()  # More than 10M

# Filter by works_count
large_topics = Topics().filter_gt(works_count=10000).get()  # More than 10k works
small_topics = Topics().filter_lt(works_count=100).get()  # Fewer than 100 works

# Filter by specific IDs
specific_ids = Topics().filter(
    openalex=["T11636", "T10017"]
).get()
```

### Hierarchical filters

```python
from openalex import Topics

# Filter by domain
health_topics = Topics().filter(domain={"id": 4}).get()  # Health Sciences

# Filter by field
medicine_topics = Topics().filter(field={"id": 27}).get()  # Medicine

# Filter by subfield
epidemiology_topics = Topics().filter(subfield={"id": 2713}).get()  # Epidemiology

# Combine hierarchical filters
medical_informatics = (
    Topics()
    .filter(domain={"id": 4})  # Health Sciences
    .filter(field={"id": 27})  # Medicine
    .filter(subfield={"id": 2718})  # Health Informatics
    .get()
)
```

## Convenience filters

These filters aren't attributes of the Topic object, but they're handy:

### Text search filters

```python
from openalex import Topics

# Search in display names
ai_search = Topics().filter(
    display_name={"search": "artificial intelligence"}
).get()

# Alternative: use search_filter
medical_search = Topics().search_filter(display_name="medical").get()

# Default search (searches display_name, description, and keywords)
default_search = Topics().filter(
    default={"search": "machine learning healthcare"}
).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
from openalex import Topics

# Large medical topics
large_medical = (
    Topics()
    .filter(domain={"id": 4})  # Health Sciences
    .filter_gt(works_count=5000)
    .sort(cited_by_count="desc")
    .get()
)

# Computer science topics with many works
active_cs_topics = (
    Topics()
    .filter(domain={"id": 2})  # Physical Sciences (includes CS)
    .filter(field={"id": 17})  # Computer Science
    .filter_gt(works_count=10000)
    .get(per_page=50)
)

# Highly cited biology topics
high_impact_bio = (
    Topics()
    .filter(domain={"id": 1})  # Life Sciences
    .filter(field={"id": 5})  # Biology
    .filter_gt(cited_by_count=1000000)
    .get()
)
```

### NOT operations

```python
from openalex import Topics

# Topics NOT in Health Sciences
non_health = Topics().filter_not(domain={"id": 4}).get()

# Topics with few works
low_activity = Topics().filter_lt(works_count=1000).get()
```

### Range queries

```python
from openalex import Topics

# Mid-size topics (1k-10k works)
mid_size = (
    Topics()
    .filter_gt(works_count=1000)
    .filter_lt(works_count=10000)
    .get()
)

# Topics with moderate citations
moderate_impact = (
    Topics()
    .filter_gt(cited_by_count=100000)
    .filter_lt(cited_by_count=1000000)
    .get()
)
```

## Practical examples

### Example 1: Find interdisciplinary topics

```python
from openalex import Topics

def find_interdisciplinary_topics():
    """Find topics that might span multiple fields."""

    # Look for topics with certain keywords
    interdisciplinary_keywords = [
        "interdisciplinary", "cross-disciplinary", "multidisciplinary",
        "systems", "complexity", "integrated"
    ]

    results = []
    for keyword in interdisciplinary_keywords:
        topics = (
            Topics()
            .search(keyword)
            .filter_gt(works_count=1000)
            .get(per_page=10)
        )
        results.extend(topics.results)

    # Remove duplicates
    unique_topics = {t.id: t for t in results}.values()

    print("Potentially interdisciplinary topics:")
    for topic in sorted(unique_topics, key=lambda t: t.works_count, reverse=True)[:20]:
        print(f"{topic.display_name}")
        print(f"  {topic.domain.display_name} -> {topic.field.display_name} -> {topic.subfield.display_name}")
        print(f"  Works: {topic.works_count:,}")

find_interdisciplinary_topics()
```

### Example 2: Domain comparison

```python
from openalex import Topics

def compare_domains():
    """Compare research activity across domains."""

    # Get domain list
    domains_grouped = Topics().group_by("domain.id").get()

    print("Research Activity by Domain:")
    print("-" * 60)

    for domain_group in domains_grouped.group_by:
        # Get top topics in this domain
        top_topics = (
            Topics()
            .filter(domain={"id": domain_group.key})
            .sort(works_count="desc")
            .get(per_page=5)
        )

        if top_topics.results:
            domain_name = top_topics.results[0].domain.display_name
            total_works = sum(t.works_count for t in top_topics.results)

            print(f"{domain_name}:")
            print(f"  Total topics: {domain_group.count}")
            print(f"  Top 5 topics total works: {total_works:,}")
            print("  Most active topics:")
            for topic in top_topics.results[:3]:
                print(f"    - {topic.display_name} ({topic.works_count:,} works)")

compare_domains()
```

### Example 3: Find emerging topics

```python
from openalex import Topics

def find_emerging_topics(min_works=500, max_works=5000):
    """Find topics that might be emerging (moderate activity)."""

    # Topics with moderate work counts might be emerging
    emerging = (
        Topics()
        .filter_gt(works_count=min_works)
        .filter_lt(works_count=max_works)
        .sort(works_count="desc")
        .get(per_page=50)
    )

    # Filter for topics with modern keywords
    modern_keywords = [
        "AI", "machine learning", "deep learning", "neural",
        "COVID", "pandemic", "climate", "sustainability",
        "quantum", "nano", "synthetic biology", "CRISPR"
    ]

    emerging_modern = []
    for topic in emerging.results:
        # Check if any modern keywords appear
        topic_text = f"{topic.display_name} {' '.join(topic.keywords or [])}"
        if any(kw.lower() in topic_text.lower() for kw in modern_keywords):
            emerging_modern.append(topic)

    print(f"Potentially emerging topics ({min_works}-{max_works} works):")
    for topic in emerging_modern[:20]:
        print(f"{topic.display_name}")
        print(f"  Field: {topic.field.display_name}")
        print(f"  Works: {topic.works_count:,}")
        if topic.keywords:
            print(f"  Keywords: {', '.join(topic.keywords[:5])}")

find_emerging_topics()
```

### Example 4: Field deep dive

```python
from openalex import Topics

def analyze_field(field_id, field_name):
    """Deep analysis of a specific field."""

    # Get all topics in field
    field_topics = list(
        Topics()
        .filter(field={"id": field_id})
        .all(per_page=200)
    )

    print(f"Analysis of {field_name}")
    print("=" * 50)
    print(f"Total topics: {len(field_topics)}")

    # Group by subfield
    subfields = {}
    for topic in field_topics:
        subfield_name = topic.subfield.display_name
        if subfield_name not in subfields:
            subfields[subfield_name] = []
        subfields[subfield_name].append(topic)

    print(f"Subfields: {len(subfields)}")

    # Show subfield distribution
    print("Subfield breakdown:")
    for subfield, topics in sorted(subfields.items(), key=lambda x: len(x[1]), reverse=True):
        total_works = sum(t.works_count for t in topics)
        print(f"  {subfield}: {len(topics)} topics, {total_works:,} works")

    # Find most active topics
    top_topics = sorted(field_topics, key=lambda t: t.works_count, reverse=True)[:10]
    print(f"Top 10 most active topics in {field_name}:")
    for i, topic in enumerate(top_topics, 1):
        print(f"  {i}. {topic.display_name} ({topic.works_count:,} works)")

# Example usage
analyze_field(17, "Computer Science")
analyze_field(27, "Medicine")
```

## Performance tips

Since there are only ~4,500 topics:

1. **Fetching all is trivial**: You can get all topics in ~23 API calls
2. **Cache the full list**: Topics change slowly, so caching makes sense
3. **Do client-side filtering**: With so few topics, local filtering is fast
4. **Use group_by sparingly**: With small data, local grouping might be faster

```python
from openalex import Topics

# Example: Efficiently work with all topics
def get_all_topics_cached():
    """Get all topics and cache them."""
    # In practice, you'd want to persist this cache
    all_topics = list(Topics().all(per_page=200))
    return all_topics

# Use the cache for complex analyses
all_topics = get_all_topics_cached()

# Now do local filtering/analysis
ai_topics = [t for t in all_topics if "artificial intelligence" in t.display_name.lower()]
large_topics = [t for t in all_topics if t.works_count > 10000]
medical_topics = [t for t in all_topics if t.domain.id == 4]
```
