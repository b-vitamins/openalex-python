# Publisher object

When you fetch a publisher using the Python client, you get a `Publisher` object with all of OpenAlex's data about that publisher. Here's how to access the various properties:

```python
from openalex import Publishers

# Get a specific publisher
publisher = Publishers()["P4310320990"]

# The publisher object has all the data as Python attributes
print(type(publisher))  # <class 'openalex.models.publisher.Publisher'>
```

## Basic properties

```python
# Identifiers
print(publisher.id)  # "https://openalex.org/P4310320990"
print(publisher.display_name)  # "Elsevier BV"

# Alternate names (list of variations)
print(publisher.alternate_titles)
# ["Elsevier", "elsevier.com", "Elsevier Science", "\u7231\u601d\u97e6\u5c14", ...]

# Hierarchy information
print(publisher.hierarchy_level)  # 1 (has one parent above)
print(publisher.parent_publisher)  # "https://openalex.org/P4310311775"

# Country information
print(publisher.country_codes)  # ["NL"]

# Scale metrics
print(publisher.works_count)  # 13,789,818
print(publisher.cited_by_count)  # 407,508,754

# Dates
print(publisher.created_date)  # "2017-08-08"
print(publisher.updated_date)  # "2024-12-25T14:04:30.578837"
```

## Hierarchy and lineage

Publishers can have parent-child relationships:

```python
# Hierarchy level (0 = top parent, 1 = child, 2 = grandchild, etc.)
print(f"Hierarchy level: {publisher.hierarchy_level}")

# Direct parent
if publisher.parent_publisher:
    print(f"Parent: {publisher.parent_publisher}")
    # To get parent details:
    parent = Publishers()[publisher.parent_publisher]
    print(f"Parent name: {parent.display_name}")

# Full lineage (includes self and all parents up to root)
print(f"Lineage ({len(publisher.lineage)} levels):")
for i, ancestor_id in enumerate(publisher.lineage):
    print(f"  Level {i}: {ancestor_id}")

# Example lineage interpretation:
# lineage[0] = self (P4310320990)
# lineage[1] = parent (P4310311775)  
# lineage[2] = grandparent (if exists)
```

## Summary statistics

Citation and productivity metrics:

```python
stats = publisher.summary_stats
if stats:
    print(f"H-index: {stats.h_index}")  # e.g., 985
    print(f"i10-index: {stats.i10_index:,}")  # e.g., 176,682
    print(f"2-year mean citedness: {stats['2yr_mean_citedness']:.2f}")
    
    # These metrics help assess publisher impact
    if stats.h_index > 500:
        print("This is a very high-impact publisher")
```

## Counts by year

Track publication trends over the last 10 years:

```python
print("Publication trends:")
for count in publisher.counts_by_year:
    print(f"  {count.year}: {count.works_count:,} works, "
          f"{count.cited_by_count:,} citations")

# Analyze trends
if len(publisher.counts_by_year) >= 2:
    recent = publisher.counts_by_year[0]
    previous = publisher.counts_by_year[1]
    growth = ((recent.works_count - previous.works_count) / 
              previous.works_count * 100)
    print(f"Year-over-year growth: {growth:+.1f}%")
```

## External identifiers

Access all known IDs:

```python
ids = publisher.ids
print(f"OpenAlex: {ids.openalex}")
if ids.ror:
    print(f"ROR: {ids.ror}")
if ids.wikidata:
    print(f"Wikidata: {ids.wikidata}")

# Check what IDs are available
available_ids = [
    id_type for id_type, value in ids.dict().items() 
    if value is not None
]
print(f"Available IDs: {', '.join(available_ids)}")
```

## Images

Publisher logos and seals:

```python
# Full-size image (usually from Wikimedia)
if publisher.image_url:
    print(f"Logo URL: {publisher.image_url}")

# Thumbnail version
if publisher.image_thumbnail_url:
    print(f"Thumbnail: {publisher.image_thumbnail_url}")
    # You can modify the width parameter in the URL:
    # Change "width=300" to "width=500" for larger thumbnail
```

## Roles

Publishers can have multiple roles in the academic ecosystem:

```python
# A publisher might also be a funder or institution
print(f"This organization has {len(publisher.roles)} roles:")

for role in publisher.roles:
    print(f"\n{role.role.capitalize()}:")
    print(f"  ID: {role.id}")
    print(f"  Works count: {role.works_count:,}")

# Example: Yale University might have:
# - role: "institution" (as a university)
# - role: "publisher" (Yale University Press)
# - role: "funder" (funding research)
```

## Sources API URL

Get all journals/sources from this publisher:

```python
# This is the API URL to get all sources
print(f"Sources URL: {publisher.sources_api_url}")

# To actually fetch the sources using the client:
from openalex import Sources

# Get all sources published by this publisher
publisher_sources = Sources().filter(
    host_organization={"id": publisher.id}
).get()

print(f"{publisher.display_name} publishes {publisher_sources.meta.count} sources")

# Show some example journals
for source in publisher_sources.results[:5]:
    print(f"  - {source.display_name}")
    if source.issn_l:
        print(f"    ISSN-L: {source.issn_l}")
```

## Working with publisher hierarchies

### Get all subsidiaries

```python
# Find all children of this publisher
children = Publishers().filter(parent_publisher=publisher.id).get()

print(f"{publisher.display_name} has {children.meta.count} direct subsidiaries:")
for child in children.results:
    print(f"  - {child.display_name}")

# Get entire family tree (all descendants)
family = Publishers().filter(lineage=publisher.id).get()
print(f"Entire family: {family.meta.count} publishers")
```

### Navigate up the hierarchy

```python
def get_publisher_chain(publisher_id):
    """Get the full chain from publisher to top parent."""
    chain = []
    current_id = publisher_id
    
    while current_id:
        pub = Publishers()[current_id]
        chain.append(pub)
        current_id = pub.parent_publisher
    
    return chain

# Example usage
chain = get_publisher_chain(publisher.id)
print("Publisher hierarchy (child to parent):")
for i, pub in enumerate(chain):
    indent = "  " * i
    print(f"{indent}\u2192 {pub.display_name} (Level {pub.hierarchy_level})")
```

## Analyze publisher portfolio

```python
# Get a sample of recent works from this publisher
from openalex import Works

recent_works = (
    Works()
    .filter(primary_location={"source": {"host_organization": publisher.id}})
    .filter(publication_year=2023)
    .get(per_page=100)
)

# Analyze work types
work_types = {}
for work in recent_works.results:
    work_type = work.type or "unknown"
    work_types[work_type] = work_types.get(work_type, 0) + 1

print(f"\nWork types published in 2023:")
for work_type, count in sorted(work_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {work_type}: {count}")

# Analyze open access
oa_count = sum(1 for w in recent_works.results if w.open_access.is_oa)
oa_percentage = (oa_count / len(recent_works.results)) * 100
print(f"\nOpen Access rate: {oa_percentage:.1f}%")
```

## Geographic analysis

```python
# For publishers with multiple country codes
if len(publisher.country_codes) > 1:
    print(f"International publisher with presence in:")
    for country in publisher.country_codes:
        print(f"  - {country}")

# Find other publishers in the same country
same_country = Publishers().filter(
    country_codes=publisher.country_codes[0]
).get()
print(f"\nOther publishers in {publisher.country_codes[0]}: "
      f"{same_country.meta.count - 1}")
```

## Handling missing data

Many fields can be None or empty:

```python
# Safe access patterns
if publisher.parent_publisher:
    print(f"Has parent: {publisher.parent_publisher}")
else:
    print("This is a top-level publisher")

if publisher.image_url:
    print(f"Logo available: {publisher.image_url}")
else:
    print("No logo available")

# Handle missing statistics
if publisher.summary_stats and publisher.summary_stats.h_index is not None:
    print(f"H-index: {publisher.summary_stats.h_index}")
else:
    print("H-index not calculated")

# Safe navigation for nested fields
parent_name = None
if publisher.parent_publisher:
    try:
        parent = Publishers()[publisher.parent_publisher]
        parent_name = parent.display_name
    except Exception:
        parent_name = "Unknown"
```
