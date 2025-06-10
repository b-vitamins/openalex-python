# Group works

You can group works to get aggregated statistics without fetching individual works:

```python
from openalex import Works

# Create a query that groups works by their open access status
oa_stats_query = Works().group_by("oa_status")

# Execute the query to get COUNTS, not individual works
oa_stats = oa_stats_query.get()

# This returns aggregated statistics, NOT work objects!
print("Open Access statistics for all works in OpenAlex:")
for group in oa_stats.group_by:
    # Each group has a 'key' (the OA status) and 'count'
    print(f"  {group.key}: {group.count:,} works")
    percentage = (group.count / oa_stats.meta.count) * 100
    print(f"    ({percentage:.1f}% of all works)")
```

Output example:
```
Open Access statistics for all works in OpenAlex:
  gold: 12,345,678 works (5.0% of all works)
  green: 23,456,789 works (9.5% of all works)
  hybrid: 3,456,789 works (1.4% of all works)
  bronze: 8,901,234 works (3.6% of all works)
  closed: 197,456,789 works (80.5% of all works)
```

**Key point**: `group_by()` returns COUNTS, not the actual works. This is much more efficient than trying to fetch millions of works!

## Understanding group_by results

```python
# The result structure is different from regular queries
result = Works().group_by("publication_year").get()

print(result.results)  # Empty list - no individual works returned!
print(result.group_by)  # List of groups with counts

# Access the grouped data
for group in result.group_by:
    print(f"Year {group.key}: {group.count:,} works")
```

## Common grouping operations

### Basic grouping

```python
# Group by publication year to see publication trends
yearly_counts = Works().group_by("publication_year").get()
# Returns ~100 groups (one per year) with counts

# Group by work type to see distribution
type_distribution = Works().group_by("type").get()
# Shows how many articles, datasets, books, etc.

# Group by language
language_stats = Works().group_by("language").get()
# See distribution across languages

# Group by whether works are retracted
retraction_stats = Works().group_by("is_retracted").get()
# Usually shows ~99.9% false, ~0.1% true
```

### Open Access analysis

```python
# Analyze OA trends over time (two-dimensional grouping)
oa_by_year = Works().group_by("publication_year", "open_access.oa_status").get()
# Returns counts for each year-status combination

# Check OA status for recent works only
recent_oa = (
    Works()
    .filter(publication_year=[2020, 2021, 2022, 2023])
    .group_by("open_access.oa_status")
    .get()
)
# More focused analysis of recent OA trends

# Find repositories with most OA works
top_repositories = (
    Works()
    .filter(open_access={"is_oa": True})
    .group_by("repository")
    .get()
)
# Shows which repositories host the most OA content
```

### Author and institution analysis

```python
# Find most prolific authors (by author ID, not name)
prolific_authors = Works().group_by("authorships.author.id").get()
# Returns thousands of groups, one per author ID

# Find most productive institutions
top_institutions = Works().group_by("authorships.institutions.id").get()
# Useful for institutional rankings

# Analyze international collaboration
countries = Works().group_by("authorships.institutions.country_code").get()
# See research output by country

# Research output by continent
continental = Works().group_by("authorships.institutions.continent").get()
# Broader geographic analysis

# Identify Global South research
global_south_stats = Works().group_by(
    "authorships.institutions.is_global_south"
).get()
```

### Publisher and source analysis

```python
# Find top publishing venues
top_journals = Works().group_by("primary_location.source.id").get()
# Groups by source (journal/repository) ID

# Analyze by source type
source_types = Works().group_by("primary_location.source.type").get()
# Shows distribution: journal vs. repository vs. conference, etc.

# Find major publishers
publishers = Works().group_by(
    "primary_location.source.publisher_lineage"
).get()
# Groups by publisher hierarchy

# Check DOAJ coverage
doaj_coverage = Works().group_by(
    "primary_location.source.is_in_doaj"
).get()
# See how many works are in DOAJ-indexed journals
```

### Topic and field analysis

```python
# Analyze research by primary topic
topics = Works().group_by("primary_topic.id").get()
# Returns counts for each research topic

# Broader analysis by scientific field
fields = Works().group_by("primary_topic.field.id").get()
# Groups into major fields like "Medicine", "Physics", etc.

# Even broader - by domain
domains = Works().group_by("primary_topic.domain.id").get()
# Usually 4-5 major domains like "Health Sciences", "Physical Sciences"

# Find interdisciplinary works (those with many topics)
topic_counts = Works().group_by("topics_count").get()
# Distribution of how many topics are assigned to works
```

## Combining filters with group_by

Group_by becomes very powerful when combined with filters:

```python
# Analyze 2023 research by country
research_2023_by_country = (
    Works()
    .filter(publication_year=2023)  # Only 2023 works
    .group_by("authorships.institutions.country_code")
    .get()
)
print(f"Research output by country in 2023:")
for group in research_2023_by_country.group_by[:10]:  # Top 10
    print(f"  {group.key}: {group.count:,} works")

# OA adoption by institution type
oa_by_inst_type = (
    Works()
    .filter(open_access={"is_oa": True})  # Only OA works
    .group_by("authorships.institutions.type")
    .get()
)
# Shows whether universities, companies, etc. publish more OA

# Citation impact by OA status
highly_cited_oa = (
    Works()
    .filter_gt(cited_by_count=100)  # Highly cited works only
    .group_by("open_access.oa_status")
    .get()
)
# See if OA works are more likely to be highly cited

# Funding analysis
nsf_funded_by_year = (
    Works()
    .filter(grants={"funder": "F4320306076"})  # NSF funded
    .group_by("publication_year")
    .get()
)
# Track NSF funding output over time
```

## Multi-dimensional grouping

You can group by multiple fields (limited to 2 dimensions):

```python
# OA status by year - great for trend analysis
oa_trends = Works().group_by(
    "publication_year", 
    "open_access.oa_status"
).get()

# Research types by country
country_types = Works().group_by(
    "authorships.institutions.country_code",
    "type"
).get()

# Topics by institution
inst_topics = Works().group_by(
    "authorships.institutions.id",
    "primary_topic.field.id"
).get()
```

## Sorting grouped results

Control how results are ordered:

```python
# Default: sorted by count (descending)
default_sort = Works().group_by("type").get()
# Articles first (most common), then books, etc.

# Sort by key instead of count
alphabetical = Works().group_by("type").sort(key="asc").get()
# article, book, chapter, dataset...

# Sort by count ascending (least common first)
rare_first = Works().group_by("type").sort(count="asc").get()
# Rarest types appear first
```

## Practical examples

### Example 1: Analyze your institution's research

```python
# First, find your institution ID
from openalex import Institutions
inst = Institutions().search("Stanford University").get().results[0]

# Analyze research output
stanford_analysis = (
    Works()
    .filter(authorships={"institutions": {"id": inst.id}})
    .group_by("publication_year")
    .get()
)

# OA adoption at Stanford
stanford_oa = (
    Works()
    .filter(authorships={"institutions": {"id": inst.id}})
    .filter(publication_year=[2020, 2021, 2022, 2023])
    .group_by("open_access.oa_status")
    .get()
)
```

### Example 2: Journal analysis

```python
# Analyze a specific journal
nature_stats = (
    Works()
    .filter(primary_location={"source": {"id": "S137773608"}})  # Nature
    .group_by("publication_year")
    .get()
)

# Topic distribution in Nature
nature_topics = (
    Works()
    .filter(primary_location={"source": {"id": "S137773608"}})
    .group_by("primary_topic.field.display_name")
    .get()
)
```

### Example 3: Research trends

```python
# Track AI/ML research growth
ml_trend = (
    Works()
    .filter(primary_topic={"id": "T10159"})  # Machine Learning topic
    .group_by("publication_year")
    .get()
)

# Geographic distribution of ML research
ml_geography = (
    Works()
    .filter(primary_topic={"id": "T10159"})
    .filter(publication_year=2023)
    .group_by("authorships.institutions.country_code")
    .get()
)
```

## Important notes

1. **No individual works returned**: `group_by()` only returns counts
2. **Maximum 10,000 groups**: API limit on number of groups returned
3. **Two dimensions maximum**: Can group by at most 2 fields
4. **Efficient for analytics**: Much faster than fetching all works
5. **Can't access work details**: Only counts and group keys available

When you need statistics, always prefer `group_by()` over trying to fetch and count individual works!
