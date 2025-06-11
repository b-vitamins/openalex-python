# Search topics

The best way to search for topics is to use the `search` method, which searches the `display_name`, `description`, and `keywords` fields:

```python
from openalex import Topics

# Search for topics related to artificial intelligence
ai_search = Topics().search("artificial intelligence")

# Execute to get the first page of results
results = ai_search.get()

print(f"Found {results.meta.count} topics matching 'artificial intelligence'")
for topic in results.results[:5]:
    print(f"\n{topic.display_name}")
    print(f"  {topic.domain.display_name} -> {topic.field.display_name} -> {topic.subfield.display_name}")
    print(f"  Works: {topic.works_count:,}")
    if topic.keywords:
        print(f"  Keywords: {', '.join(topic.keywords[:5])}")
```

## How topic search works

The search checks multiple fields:

```python
# This searches display_name, description, AND keywords
ml_results = Topics().search("machine learning").get()

# This will find topics where:
# - "machine learning" appears in the name
# - "machine learning" is mentioned in the description
# - "machine learning" is one of the keywords

# Search is flexible with variations
climate_results = Topics().search("climate change").get()
# Finds topics about climate, global warming, environmental change, etc.
```

Read more about search relevance, stemming, and boolean searches in the [search documentation](../../how-to-use-the-api/get-lists-of-entities/search-entities.md).

## Search a specific field

You can also use search as a filter:

```python
# Search only in display_name
name_only = Topics().filter(
    display_name={"search": "medical"}
).get()

# Or use the search_filter method
name_search = Topics().search_filter(
    display_name="cancer"
).get()

# Search only in description
desc_search = Topics().filter(
    description={"search": "artificial intelligence applications"}
).get()

# Search only in keywords
keyword_search = Topics().filter(
    keywords={"search": "deep learning"}
).get()

# Default search (same as .search() method)
default_search = Topics().filter(
    default={"search": "quantum computing"}
).get()
```

Available search fields:

| Search filter | Field that is searched | Python method |
|---------------|------------------------|---------------|
| `display_name.search` | `display_name` only | `.search_filter(display_name="...")` |
| `description.search` | `description` only | `.filter(description={"search": "..."})` |
| `keywords.search` | `keywords` only | `.filter(keywords={"search": "..."})` |
| `default.search` | `display_name`, `description`, and `keywords` | `.filter(default={"search": "..."})` |

## Combining search with filters

Search is most powerful when combined with filters:

```python
# Search for AI topics in Computer Science
cs_ai_topics = (
    Topics()
    .search("artificial intelligence")
    .filter(field={"id": 17})  # Computer Science
    .get(per_page=20)
)

print(f"Found {cs_ai_topics.meta.count} AI topics in Computer Science")

# Search for medical topics with many works
active_medical = (
    Topics()
    .search("medical")
    .filter_gt(works_count=5000)
    .sort(works_count="desc")
    .get()
)

# Search within a specific domain
health_topics = (
    Topics()
    .search("therapy treatment")
    .filter(domain={"id": 4})  # Health Sciences
    .get()
)

# Find emerging topics with specific keywords
emerging_quantum = (
    Topics()
    .search("quantum")
    .filter_gt(works_count=100)
    .filter_lt(works_count=1000)
    .get()
)
```

## Search strategies

### Finding interdisciplinary topics

```python
def find_interdisciplinary_topics(term1, term2):
    """Find topics that bridge two areas."""
    
    # Search for topics mentioning both terms
    combined_search = Topics().search(f"{term1} {term2}").get()
    
    print(f"Topics bridging '{term1}' and '{term2}':")
    for topic in combined_search.results[:10]:
        print(f"\n{topic.display_name}")
        print(f"  Field: {topic.field.display_name}")
        print(f"  Description: {topic.description[:150]}..." if topic.description else "  No description")
        print(f"  Works: {topic.works_count:,}")

# Examples
find_interdisciplinary_topics("computer", "biology")
find_interdisciplinary_topics("physics", "medicine")
find_interdisciplinary_topics("economics", "psychology")
```

### Keyword-based discovery

```python
def discover_topics_by_keywords(keywords_list):
    """Find topics that match specific keywords."""
    
    all_results = {}
    
    for keyword in keywords_list:
        # Search in keywords field specifically
        results = (
            Topics()
            .filter(keywords={"search": keyword})
            .get(per_page=10)
        )
        
        for topic in results.results:
            if topic.id not in all_results:
                all_results[topic.id] = {
                    "topic": topic,
                    "matched_keywords": []
                }
            all_results[topic.id]["matched_keywords"].append(keyword)
    
    # Sort by number of matching keywords
    sorted_results = sorted(
        all_results.values(),
        key=lambda x: len(x["matched_keywords"]),
        reverse=True
    )
    
    print("Topics matching your keywords:")
    for result in sorted_results[:10]:
        topic = result["topic"]
        matches = result["matched_keywords"]
        print(f"\n{topic.display_name}")
        print(f"  Matched keywords: {', '.join(matches)}")
        print(f"  All keywords: {', '.join(topic.keywords[:5])}...")

# Example usage
discover_topics_by_keywords([
    "neural networks", "deep learning", "machine learning",
    "artificial intelligence", "computer vision"
])
```

### Hierarchical search

```python
def search_within_hierarchy(search_term, domain_id=None, field_id=None):
    """Search for topics within a specific part of the hierarchy."""
    
    query = Topics().search(search_term)
    
    if domain_id:
        query = query.filter(domain={"id": domain_id})
    if field_id:
        query = query.filter(field={"id": field_id})
    
    results = query.get(per_page=20)
    
    print(f"Search results for '{search_term}':")
    if domain_id or field_id:
        print(f"  Filtered to: ", end="")
        if domain_id:
            print(f"Domain {domain_id}", end="")
        if field_id:
            print(f", Field {field_id}", end="")
        print()
    
    for topic in results.results:
        print(f"\n{topic.display_name}")
        print(f"  {topic.domain.display_name} -> {topic.field.display_name} -> {topic.subfield.display_name}")
        print(f"  Works: {topic.works_count:,}")

# Examples
search_within_hierarchy("genetics", domain_id=1)  # Life Sciences only
search_within_hierarchy("learning", field_id=17)  # Computer Science only
```

## Common search patterns

### Finding research trends

```python
# Emerging technology topics
emerging_tech = (
    Topics()
    .search("blockchain OR cryptocurrency OR NFT OR metaverse")
    .filter_gt(works_count=100)
    .sort(works_count="desc")
    .get()
)

# Environmental research topics
environmental = (
    Topics()
    .search("climate OR sustainability OR renewable OR carbon")
    .filter_gt(works_count=1000)
    .get()
)

# Health crisis topics
health_crisis = (
    Topics()
    .search("COVID OR pandemic OR vaccine OR epidemiology")
    .sort(works_count="desc")
    .get()
)
```

### Topic similarity search

```python
def find_similar_topics(topic_id):
    """Find topics similar to a given topic."""
    
    # Get the reference topic
    ref_topic = Topics()[topic_id]
    
    # Search using keywords from the reference topic
    if ref_topic.keywords:
        search_terms = " OR ".join(ref_topic.keywords[:5])
        similar = Topics().search(search_terms).get(per_page=20)
        
        # Filter out the reference topic itself
        similar_topics = [t for t in similar.results if t.id != topic_id]
        
        print(f"Topics similar to '{ref_topic.display_name}':")
        for topic in similar_topics[:10]:
            print(f"  - {topic.display_name} ({topic.works_count:,} works)")

find_similar_topics("T11636")  # AI in Medicine
```

## Search tips

1. **Use multiple terms**: "machine learning" finds more than just "ML"
2. **Try variations**: "AI" vs "artificial intelligence"
3. **Check keywords**: Topics have AI-generated keywords that aid discovery
4. **Consider hierarchy**: Search within specific domains/fields
5. **Combine with filters**: Narrow results by work count or hierarchy

```python
# Example: Comprehensive topic search
def comprehensive_topic_search(search_terms, min_works=100):
    """Search with multiple strategies."""
    
    all_results = set()
    
    # Try each search term
    for term in search_terms:
        # General search
        general = Topics().search(term).filter_gt(works_count=min_works).get()
        all_results.update(t.id for t in general.results)
        
        # Keyword-specific search
        keyword = Topics().filter(keywords={"search": term}).get()
        all_results.update(t.id for t in keyword.results)
    
    # Fetch full details for unique topics
    if all_results:
        unique_topics = Topics().filter(openalex=list(all_results)).get(per_page=50)
        
        # Sort by relevance (work count as proxy)
        sorted_topics = sorted(
            unique_topics.results,
            key=lambda t: t.works_count,
            reverse=True
        )
        
        print(f"Found {len(sorted_topics)} unique topics")
        for topic in sorted_topics[:20]:
            print(f"\n{topic.display_name}")
            print(f"  {topic.field.display_name} -> {topic.subfield.display_name}")
            print(f"  Works: {topic.works_count:,}")

# Search for AI/ML topics comprehensively
comprehensive_topic_search([
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "AI", "ML"
])
```

## Quick topic discovery

Since there are only ~4,500 topics, you can also browse them all:

```python
# Get all topics for browsing
def browse_all_topics():
    """Load all topics for interactive browsing."""
    
    print("Loading all topics...")
    all_topics = list(Topics().paginate(per_page=200))
    print(f"Loaded {len(all_topics)} topics")
    
    # Now you can search locally with any criteria
    # Example: Find all topics with "bio" in the name
    bio_topics = [t for t in all_topics if "bio" in t.display_name.lower()]
    print(f"\nFound {len(bio_topics)} topics with 'bio' in the name")
    
    return all_topics

# This is feasible because the dataset is small
all_topics = browse_all_topics()
```
