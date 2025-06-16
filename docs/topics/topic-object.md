# Topic object

When you fetch a topic using the Python client, you get a `Topic` object with all of OpenAlex's data about that topic. Here's how to access the various properties:

```python
from openalex import Topics

# Get a specific topic
topic = Topics()["T11636"]

# The topic object has all the data as Python attributes
print(type(topic))  # <class 'openalex.models.topic.Topic'>
```

## Basic properties

```python
# Fetch the topic again for this example
from openalex import Topics
topic = Topics()["T11636"]

# Identifiers
print(topic.id)  # "https://openalex.org/T11636"
print(topic.display_name)  # "Artificial Intelligence in Medicine"

# Description (AI-generated)
print(topic.description)
# "This cluster of papers explores the intersection of artificial intelligence 
#  and medicine, focusing on applications in healthcare, medical imaging..."

# Metrics
print(topic.works_count)  # 21,737
print(topic.cited_by_count)  # Total citations to works with this topic

# Dates
print(topic.updated_date)  # "2024-02-05T05:00:03.798420"
```

## Hierarchical classification

```python
# Fetch the topic again
from openalex import Topics
topic = Topics()["T11636"]

# Topics are organized in a 4-level hierarchy
# Domain (broadest)
print(f"Domain: {topic.domain.display_name} (ID: {topic.domain.id})")
# "Health Sciences (ID: 4)"

# Field
print(f"Field: {topic.field.display_name} (ID: {topic.field.id})")
# "Medicine (ID: 27)"

# Subfield
print(f"Subfield: {topic.subfield.display_name} (ID: {topic.subfield.id})")
# "Health Informatics (ID: 2718)"

# Topic (most specific)
print(f"Topic: {topic.display_name}")
# "Artificial Intelligence in Medicine"

# Show full hierarchy
print(f"Full hierarchy: {topic.domain.display_name} -> {topic.field.display_name} -> {topic.subfield.display_name} -> {topic.display_name}")
```

## Keywords

```python
# Fetch the topic again
from openalex import Topics
topic = Topics()["T11636"]

# AI-generated keywords for this topic
if topic.keywords:
    print(f"Number of keywords: {len(topic.keywords)}")
    print("Keywords:")
    for keyword in topic.keywords[:10]:  # First 10
        print(f"  - {keyword}")
    
    # Keywords can be multi-word phrases
    single_word = [k for k in topic.keywords if ' ' not in k]
    multi_word = [k for k in topic.keywords if ' ' in k]
    print(f"\nSingle-word keywords: {len(single_word)}")
    print(f"Multi-word phrases: {len(multi_word)}")
```

## External identifiers

```python
# Fetch the topic again
from openalex import Topics
topic = Topics()["T11636"]

ids = topic.ids
print(f"OpenAlex: {ids.openalex}")
if ids.wikipedia:
    print(f"Wikipedia: {ids.wikipedia}")
    # "https://en.wikipedia.org/wiki/Artificial_intelligence_in_healthcare"
```

## Working with topic data

### Find works in a topic

```python
from openalex import Topics, Works

topic = Topics()["T11636"]

def get_works_for_topic(topic_id, recent_only=False):
    """Get works that have this topic."""
    
    # Build query for works with this topic
    query = Works().filter(topics={"id": topic_id})
    
    if recent_only:
        query = query.filter(publication_year=2023)
    
    # Get recent highly-cited works
    top_works = query.sort(cited_by_count="desc").get()
    
    print(f"Top works in topic '{topic.display_name}':")
    for work in top_works.results[:10]:
        print(f"\n{work.title}")
        print(f"  Citations: {work.cited_by_count}")
        print(f"  Published: {work.publication_date}")
        
        # Show if this is the primary topic
        pt = work.primary_topic
        pt_id = pt.get("id") if isinstance(pt, dict) else getattr(pt, "id", None)
        if pt_id == topic_id:
            print(f"  Primary topic: Yes")

# Example usage
get_works_for_topic(topic.id, recent_only=True)
```

### Analyze topic evolution

```python
def analyze_topic_growth(topic_id):
    """Analyze how a topic has grown over time."""
    from openalex import Topics, Works
    
    topic = Topics()[topic_id]
    
    print(f"Growth Analysis: {topic.display_name}")
    print("=" * 50)
    
    # Get work counts by year
    current_year = 2024
    for year in range(current_year - 5, current_year + 1):
        year_works = (
            Works()
            .filter(primary_topic={"id": topic_id})
            .filter(publication_year=year)
            .get()
        )
        
        print(f"{year}: {year_works.meta.count:,} works")
    
    # Show related topics (topics in same subfield)
    related = (
        Topics()
        .filter(subfield={"id": topic.subfield.id})
        .filter_not(openalex=topic_id)
        .sort(works_count="desc")
        .get(per_page=5)
    )
    
    print(f"\nRelated topics in {topic.subfield.display_name}:")
    for t in related.results:
        print(f"  - {t.display_name} ({t.works_count:,} works)")

# Example usage
analyze_topic_growth("T11636")
```

### Topic similarity and relationships

```python
def find_related_topics(topic_id):
    """Find topics related to a given topic."""
    from openalex import Topics
    source_topic = Topics()[topic_id]
    
    # Same subfield (most related)
    same_subfield = (
        Topics()
        .filter(subfield={"id": source_topic.subfield.id})
        .filter_not(openalex=topic_id)
        .sort(works_count="desc")
        .get(per_page=10)
    )
    
    print(f"Topics in same subfield ({source_topic.subfield.display_name}):")
    for t in same_subfield.results:
        print(f"  - {t.display_name} ({t.works_count:,} works)")
    
    # Same field but different subfield
    same_field = (
        Topics()
        .filter(field={"id": source_topic.field.id})
        .filter_not(subfield={"id": source_topic.subfield.id})
        .sort(works_count="desc")
        .get(per_page=5)
    )
    
    print(f"\nOther topics in {source_topic.field.display_name}:")
    for t in same_field.results:
        print(f"  - {t.display_name} ({t.subfield.display_name})")
    
    # Search for topics with similar keywords
    if source_topic.keywords:
        keyword_search = " OR ".join(source_topic.keywords[:3])
        similar_keywords = (
            Topics()
            .search(keyword_search)
            .filter_not(openalex=topic_id)
            .get(per_page=5)
        )
        
        print(f"\nTopics with similar keywords:")
        for t in similar_keywords.results:
            print(f"  - {t.display_name}")

find_related_topics("T11636")
```

### Compare topics

```python
def compare_topics(topic_ids):
    """Compare multiple topics side by side."""
    from openalex import Topics
    topics = []
    for tid in topic_ids:
        topics.append(Topics()[tid])
    
    print("Topic Comparison")
    print("-" * 80)
    print(f"{'Topic':<40} {'Field':<20} {'Works':>10} {'Domain':<15}")
    print("-" * 80)
    
    for t in topics:
        print(f"{t.display_name[:39]:<40} "
              f"{t.field.display_name[:19]:<20} "
              f"{t.works_count:>10,} "
              f"{t.domain.display_name:<15}")
    
    # Show keyword overlap
    print("\nKeyword Analysis:")
    all_keywords = set()
    topic_keywords = {}
    
    for t in topics:
        if t.keywords:
            topic_keywords[t.id] = set(t.keywords)
            all_keywords.update(t.keywords)
    
    # Find common keywords
    if len(topic_keywords) > 1:
        common = set.intersection(*topic_keywords.values())
        if common:
            print(f"Common keywords: {', '.join(list(common)[:5])}")

# Compare AI-related topics
compare_topics(["T11636", "T10017", "T10159"])
```

### Topic hierarchy navigation

```python
def explore_topic_hierarchy(topic_id):
    """Explore the hierarchical context of a topic."""
    from openalex import Topics
    topic = Topics()[topic_id]
    
    print(f"Hierarchy for: {topic.display_name}")
    print("=" * 50)
    
    # Show full path
    print(f"\nFull path:")
    print(f"  Domain: {topic.domain.display_name} (ID: {topic.domain.id})")
    print(f"  v")
    print(f"  Field: {topic.field.display_name} (ID: {topic.field.id})")
    print(f"  v")
    print(f"  Subfield: {topic.subfield.display_name} (ID: {topic.subfield.id})")
    print(f"  v")
    print(f"  Topic: {topic.display_name}")
    
    # Count siblings at each level
    domain_fields = Topics().filter(domain={"id": topic.domain.id}).group_by("field.id").get()
    field_subfields = Topics().filter(field={"id": topic.field.id}).group_by("subfield.id").get()
    subfield_topics = Topics().filter(subfield={"id": topic.subfield.id}).get()
    
    print(f"\nContext:")
    fields_len = len(domain_fields.group_by or [])
    subfields_len = len(field_subfields.group_by or [])
    print(f"  Fields in {topic.domain.display_name}: {fields_len}")
    print(f"  Subfields in {topic.field.display_name}: {subfields_len}")
    print(f"  Topics in {topic.subfield.display_name}: {subfield_topics.meta.count}")
    
    # Show some sibling topics
    siblings = (
        Topics()
        .filter(subfield={"id": topic.subfield.id})
        .filter_not(openalex=topic_id)
        .sort(works_count="desc")
        .get(per_page=5)
    )
    
    print(f"\nSibling topics in {topic.subfield.display_name}:")
    for t in siblings.results:
        print(f"  - {t.display_name} ({t.works_count:,} works)")

explore_topic_hierarchy("T11636")
```

## Handling missing data

Some fields might be None or empty:

```python
# Fetch the topic again
from openalex import Topics
topic = Topics()["T11636"]

# Safe access patterns
if topic.description:
    print(f"Description: {topic.description[:200]}...")
else:
    print("No description available")

# Keywords might be empty
if topic.keywords:
    print(f"Keywords: {', '.join(topic.keywords[:5])}")
else:
    print("No keywords available")

# Wikipedia might not exist
if topic.ids.wikipedia:
    print(f"Wikipedia: {topic.ids.wikipedia}")
else:
    print("No Wikipedia page")

# Some topics might have very few works
if topic.works_count < 100:
    print(f"Note: This is a small topic with only {topic.works_count} works")
```

## Working with all topics

Since there are only ~4,500 topics, you can easily work with all of them:

```python
# Fetch the Topics client
from openalex import Topics

# Load all topics for comprehensive analysis
def load_all_topics():
    """Load all topics into memory for analysis."""
    print("Loading all topics...")
    all_topics = list(Topics().all(per_page=200))
    print(f"Loaded {len(all_topics)} topics")
    
    # Create useful indexes
    by_domain = {}
    by_field = {}
    by_subfield = {}
    
    for topic in all_topics:
        # Index by domain
        domain_name = topic.domain.display_name
        if domain_name not in by_domain:
            by_domain[domain_name] = []
        by_domain[domain_name].append(topic)
        
        # Index by field
        field_name = topic.field.display_name
        if field_name not in by_field:
            by_field[field_name] = []
        by_field[field_name].append(topic)
        
        # Index by subfield
        subfield_name = topic.subfield.display_name
        if subfield_name not in by_subfield:
            by_subfield[subfield_name] = []
        by_subfield[subfield_name].append(topic)
    
    return {
        "all": all_topics,
        "by_domain": by_domain,
        "by_field": by_field,
        "by_subfield": by_subfield
    }

# Use this for complex analyses
topic_data = load_all_topics()

# Example: Find largest subfields
largest_subfields = sorted(
    topic_data["by_subfield"].items(),
    key=lambda x: len(x[1]),
    reverse=True
)[:10]

print("\nLargest subfields by topic count:")
for subfield, topics in largest_subfields:
    total_works = sum(t.works_count for t in topics)
    print(f"  {subfield}: {len(topics)} topics, {total_works:,} works")
```
