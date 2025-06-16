# Author object

When you fetch an author using the Python client, you get an `Author` object with all of OpenAlex's data about that author. Here's how to access the various properties:

```python
from openalex import Authors

# Get a specific author
author = Authors()["A5023888391"]

# The author object has all the data as Python attributes
print(type(author))  # <class 'openalex.models.author.Author'>
```

## Basic properties

```python
from openalex import Authors

author = Authors()["A5023888391"]

# Identifiers
print(author.id)  # "https://openalex.org/A5023888391"
print(author.orcid)  # "https://orcid.org/0000-0001-6187-6610"

# Name information
print(author.display_name)  # "Jason Priem"
print(author.display_name_alternatives)  # ["Jason R Priem"]

# Productivity metrics
print(author.works_count)  # 38
print(author.cited_by_count)  # Total citations across all works

# Dates
print(author.created_date)  # "2017-08-08"
print(author.updated_date)  # "2024-01-02T00:00:00"

# API URL for this author's works
print(author.works_api_url)  # URL to get all works by this author
```

## Affiliations

Authors have institutional affiliations over time:

```python
from openalex import Authors

author = Authors()["A5023888391"]

# All known affiliations throughout career
print(f"Known affiliations: {len(author.affiliations)}")

for affiliation in author.affiliations:
    institution = affiliation.institution
    print(f"\n{institution.display_name}")
    print(f"  Type: {institution.type}")
    print(f"  Country: {institution.country_code}")
    print(f"  Years: {affiliation.years}")  # List of years

# Example output:
# OurResearch
#   Type: nonprofit
#   Country: CA
#   Years: [2018, 2019, 2020]
```

## Last known institutions

The most recent institutional affiliation(s):

```python
from openalex import Authors

author = Authors()["A5023888391"]

# Can be multiple if author had multiple affiliations in latest work
if author.last_known_institutions:
    print(f"Last known at {len(author.last_known_institutions)} institution(s):")

    for inst in author.last_known_institutions:
        print(f"\n{inst.display_name}")
        print(f"  Type: {inst.type}")  # education, company, etc.
        print(f"  Country: {inst.country_code}")
        print(f"  ROR: {inst.ror}")
        print(f"  Lineage: {inst.lineage}")  # Parent institutions
else:
    print("No known institutional affiliation")
```

## Summary statistics

Citation and productivity metrics:

```python
from openalex import Authors

author = Authors()["A5023888391"]

stats = author.summary_stats
if stats:
    print(f"H-index: {stats.h_index}")  # e.g., 45
    print(f"i10-index: {stats.i10_index}")  # e.g., 205
    print(f"2-year mean citedness: {stats.two_year_mean_citedness:.2f}")

    # Interpretation
    if stats.h_index > 40:
        print("This is a highly influential researcher")
    if stats.i10_index > 100:
        print("Very productive with many well-cited papers")
```

## Citations by year

Track citation trends:

```python
from openalex import Authors

author = Authors()["A5023888391"]

# Get citations for the last 10 years
print("Citations by year:")
for count in author.counts_by_year:
    print(f"  {count.year}: {count.works_count} works, "
          f"{count.cited_by_count} citations")

# Calculate recent impact
recent_citations = sum(
    c.cited_by_count
    for c in author.counts_by_year
    if c.year >= 2020
)
print(f"Citations since 2020: {recent_citations}")
```

## External identifiers

Access all known IDs:

```python
from openalex import Authors

author = Authors()["A5023888391"]

ids = author.ids
print(f"OpenAlex: {ids.openalex}")
print(f"ORCID: {ids.orcid}")
if ids.scopus:
    print(f"Scopus: {ids.scopus}")
if ids.twitter:
    print(f"Twitter: {ids.twitter}")
if ids.wikipedia:
    print(f"Wikipedia: {ids.wikipedia}")

# Check what IDs are available
available_ids = [
    id_type for id_type, value in ids.model_dump().items()
    if value is not None
]
print(f"Available IDs: {', '.join(available_ids)}")
```

## Concepts (deprecated)

Research areas associated with this author:

```python
from openalex import Authors

author = Authors()["A5023888391"]

# Note: x_concepts will be deprecated soon, replaced by Topics
if author.x_concepts:
    print("Top research areas:")
    for concept in author.x_concepts[:5]:  # Top 5
        print(f"  {concept.display_name}: {concept.score:.1f}%")

# Example output:
# Top research areas:
#   Computer science: 97.4%
#   Political science: 78.9%
#   Economics: 65.3%
```

## Working with author data

### Get all works by an author

```python
# Import both Authors and Works for this example
from openalex import Authors, Works

author = Authors()["A5023888391"]

# Option 1: Use the works_api_url
# This is just the URL - you'd need to fetch it separately

# Option 2: Use the Works entity (recommended)
from openalex import Works

author_works = Works().filter(
    authorships={"author": {"id": author.id}}
).get()

print(f"Retrieved {len(author_works.results)} of {author.works_count} works")

# Get all works with pagination
for page in Works().filter(
    authorships={"author": {"id": author.id}}
).paginate():
    for work in page.results:
        print(f"- {work.title} ({work.publication_year})")
```

### Find co-authors

```python
# Import required classes
from openalex import Authors, Works

author = Authors()["A5023888391"]

# Get a sample of works to find co-authors
sample_works = (
    Works()
    .filter(authorships={"author": {"id": author.id}})
    .get(per_page=50)
)

# Collect co-authors
co_authors = set()
for work in sample_works.results:
    for authorship in work.authorships:
        # API may return raw dicts here when using select
        if isinstance(authorship, dict):
            from openalex.models.work import Authorship

            authorship = Authorship(**authorship)
        if authorship.author.id != author.id:
            co_authors.add(
                (
                    authorship.author.id,
                    authorship.author.display_name,
                )
            )

print(f"Found {len(co_authors)} co-authors in sample")
for co_id, co_name in list(co_authors)[:10]:
    print(f"  {co_name} ({co_id})")
```

### Analyze author trajectory

```python
# Import Authors for this analysis
from openalex import Authors

author = Authors()["A5023888391"]

# Get yearly productivity
yearly_works = author.counts_by_year

# Find peak years
peak_year = max(yearly_works, key=lambda x: x.works_count)
print(f"Most productive year: {peak_year.year} "
      f"({peak_year.works_count} works)")

peak_citations_year = max(yearly_works, key=lambda x: x.cited_by_count)
print(f"Most cited year: {peak_citations_year.year} "
      f"({peak_citations_year.cited_by_count} citations)")

# Career trajectory
early_career = [c for c in yearly_works if c.year <= 2015]
recent = [c for c in yearly_works if c.year >= 2020]

if early_career and recent:
    early_avg = sum(c.works_count for c in early_career) / len(early_career)
    recent_avg = sum(c.works_count for c in recent) / len(recent)

    if recent_avg > early_avg * 1.5:
        print("Increasing productivity over time")
    elif recent_avg < early_avg * 0.5:
        print("Decreasing productivity (possibly emeritus)")
```

## Handling missing data

Many fields can be None or empty:

```python
# Import Authors for missing-data examples
from openalex import Authors

author = Authors()["A5023888391"]

# Safe access patterns
if author.orcid:
    print(f"ORCID: {author.orcid}")
else:
    print("No ORCID ID available")

# Check for affiliations
if not author.affiliations:
    print("No affiliation information")

if not author.last_known_institutions:
    print("No current institutional affiliation known")

# Handle missing stats
if author.summary_stats and author.summary_stats.h_index is not None:
    print(f"H-index: {author.summary_stats.h_index}")
else:
    print("H-index not calculated")

# Safe navigation for nested fields
last_inst_name = None
if author.last_known_institutions and author.last_known_institutions[0]:
    last_inst_name = author.last_known_institutions[0].display_name
```

## The DehydratedAuthor object

When authors appear in other objects (like in work authorships), you get a simplified version:

```python
# Get a work to see dehydrated authors
from openalex import Works, Authors
work = Works()["W2741809807"]

# Access dehydrated authors in authorships
for authorship in work.authorships:
    dehydrated_author = authorship.author

    # Only these fields are available in dehydrated version:
    print(dehydrated_author.id)
    print(dehydrated_author.display_name)
    print(dehydrated_author.orcid)  # If available

    # Other fields are not included to save space
    # To get full details, fetch the complete author:
    if dehydrated_author.orcid:
        full_author = Authors()[dehydrated_author.id]
        print(f"Full works count: {full_author.works_count}")
```
