# Get lists of topics

You can get lists of topics using the Python client:

```python
from openalex import Topics

# Create a query for all topics (no filters applied)
all_topics_query = Topics()

# Execute the query to get the FIRST PAGE of results
first_page = all_topics_query.get()

# Note: With only ~4,500 topics, fetching all is very easy
print(f"Total topics: {first_page.meta.count:,}")  # ~4,500
print(f"Topics in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Topic objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
from openalex import Topics

# Fetch the first page of topics
first_page = Topics().get()

# Each result shows topic information
for topic in first_page.results[:5]:  # First 5 topics
    print(f"\n{topic.display_name}")
    print(f"  Hierarchy: {topic.domain.display_name} -> {topic.field.display_name} -> {topic.subfield.display_name}")
    print(f"  Works count: {topic.works_count:,}")
    print(f"  Keywords: {', '.join(topic.keywords[:3])}")  # First 3 keywords
    if topic.description:
        print(f"  Description: {topic.description[:100]}...")
```

## Page and sort topics

You can control pagination and sorting:

```python
from openalex import Topics

# Get a specific page with custom page size
page2 = Topics().get(per_page=50, page=2)
# This returns topics 51-100

# Sort by different fields
# Most popular topics (by work count)
most_used = Topics().sort(works_count="desc").get()

# Most cited topics
most_cited = Topics().sort(cited_by_count="desc").get()

# Alphabetical by name
alphabetical = Topics().sort(display_name="asc").get()

# Get ALL topics (very easy with only ~4,500)
# This will make about 23 API calls at 200 per page
all_topics = []
for topic in Topics().paginate(per_page=200):
    all_topics.append(topic)
print(f"Fetched all {len(all_topics)} topics")

# Or more simply, since the dataset is small
all_topics_list = list(Topics().paginate(per_page=200))
```

## Sample topics

Get a random sample of topics:

```python
# Get 10 random topics
from openalex import Topics
random_sample = Topics().sample(10).get(per_page=10)

# Use a seed for reproducible random sampling
reproducible_sample = Topics().sample(10, seed=42).get(per_page=10)

# Sample from filtered results
medical_sample = (
    Topics()
    .filter(domain={"id": 4})  # Health Sciences domain
    .sample(5)
    .get()
)
```

## Select fields

Limit the fields returned to improve performance:

```python
from openalex import Topics

# Request only specific fields
minimal_topics = Topics().select([
    "id",
    "display_name",
    "description",
    "works_count"
]).get()

# This reduces response size significantly
for topic in minimal_topics.results:
    print(f"{topic.display_name}: {topic.works_count:,} works")
    print(topic.keywords)  # None - not selected
```

## Practical examples

### Example: Explore the topic hierarchy

```python
from openalex import Topics

# Get all domains
domains = Topics().group_by("domain.id").get()

print("Topic domains in OpenAlex:")
for domain in domains.group_by:
    # Get sample topics from each domain
    domain_topics = (
        Topics()
        .filter(domain={"id": domain.key})
        .sort(works_count="desc")
        .get(per_page=3)
    )
    
    print(f"\n{domain.key}: {domain.count} topics")
    for topic in domain_topics.results:
        print(f"  - {topic.display_name} ({topic.works_count:,} works)")
```

### Example: Find trending topics

```python
from openalex import Topics

# Get topics with the most recent growth
def find_trending_topics():
    # Get all topics efficiently
    all_topics = list(Topics().paginate(per_page=200))
    
    # Sort by growth rate (simplified - you'd want to look at recent works)
    active_topics = sorted(
        [t for t in all_topics if t.works_count > 1000],
        key=lambda t: t.works_count,
        reverse=True
    )[:20]
    
    print("Most active research topics:")
    for i, topic in enumerate(active_topics, 1):
        print(f"{i}. {topic.display_name}")
        print(f"   {topic.domain.display_name} -> {topic.field.display_name}")
        print(f"   Works: {topic.works_count:,}")

find_trending_topics()
```

### Example: Topic coverage analysis

```python
from openalex import Topics

# Analyze topic distribution across domains
def analyze_topic_coverage():
    # Get domain distribution
    by_domain = Topics().group_by("domain.id").get()
    
    # Get field distribution
    by_field = Topics().group_by("field.id").get()
    
    # Get subfield distribution
    by_subfield = Topics().group_by("subfield.id").get()
    
    print("OpenAlex Topic Hierarchy:")
    print(f"  Domains: {len(by_domain.group_by)}")
    print(f"  Fields: {len(by_field.group_by)}")
    print(f"  Subfields: {len(by_subfield.group_by)}")
    print(f"  Topics: ~{Topics().get().meta.count:,}")
    
    # Show largest domains
    print("
Largest domains by topic count:")
    for domain in by_domain.group_by[:5]:
        print(f"  Domain {domain.key}: {domain.count} topics")

analyze_topic_coverage()
```

Continue on to learn how you can [filter](filter-topics.md) and [search](search-topics.md) lists of topics.
