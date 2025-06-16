# Work object

When you fetch a work using the Python client, you get a `Work` object with all of OpenAlex's data about that work. Here's how to access the various properties:

```python
from openalex import Works

# Get a specific work
work = Works()["W2741809807"]

# The work object has all the data as Python attributes
print(type(work))  # <class 'openalex.models.work.Work'>
```

## Basic properties

```python
# Import Works query builder and fetch a work
from openalex import Works
work = Works()["W2741809807"]

def process_abstract(text: str) -> None:
    """Placeholder processing function."""
    pass

# Identifiers
print(work.id)  # "https://openalex.org/W2741809807"
print(work.doi)  # "https://doi.org/10.7717/peerj.4375"

# Title and display name (these are the same)
print(work.title)  # "The state of OA: a large-scale analysis..."
print(work.display_name)  # Same as title

# Publication info
print(work.publication_year)  # 2018
print(work.publication_date)  # "2018-02-13"
print(work.type)  # "article"
print(work.type_crossref)  # "journal-article" (legacy format)

# Basic metadata
print(work.language)  # "en"
print(work.created_date)  # "2017-08-08"
print(work.updated_date)  # "2024-01-01T00:00:00.000000"

# Quality flags
print(work.is_paratext)  # False (True for editorials, TOCs, etc.)
print(work.is_retracted)  # False (True if retracted)
```

## Abstract

The abstract is stored as an inverted index (word positions), but the Python client provides automatic conversion:

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Get abstract as plain text (automatically converted)
if work.abstract:
    print(work.abstract[:200] + "...")
    # "Despite growing interest in Open Access (OA), relatively little is known..."

# Access the raw inverted index if needed
if work.abstract_inverted_index:
    print(list(work.abstract_inverted_index.keys())[:10])
    # ['Despite', 'growing', 'interest', 'in', 'Open', 'Access', ...]
```

## Authorships

Authorships contain author and affiliation information:

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Iterate through all authors
print(f"This work has {len(work.authorships)} authors")

for authorship in work.authorships:
    # Author information
    author = authorship.author
    print(f"\nAuthor: {author.display_name}")
    if author.orcid:
        print(f"  ORCID: {author.orcid}")
    
    # Author position in the paper
    print(f"  Position: {authorship.author_position}")  # "first", "middle", or "last"
    print(f"  Corresponding: {authorship.is_corresponding}")
    
    # Institutional affiliations
    for institution in authorship.institutions:
        print(f"  Institution: {institution.display_name}")
        print(f"    Country: {institution.country_code}")
        print(f"    Type: {institution.type}")  # "education", "company", etc.
        print(f"    ROR: {institution.ror}")
    
    # Raw affiliation strings (as they appear in the paper)
    for raw_text in authorship.raw_affiliation_strings:
        print(f"  Raw text: '{raw_text}'")
    
    # Countries (derived from institutions and raw strings)
    if authorship.countries:
        print(f"  Countries: {', '.join(authorship.countries)}")
```

## Locations (where to find the work)

Works can be found in multiple locations (journal, repositories, etc.):

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Primary location (usually the publisher's version)
primary = work.primary_location
if primary:
    print(f"Primary location: {primary.source.display_name}")
    print(f"  Type: {primary.source.type}")  # "journal", "repository", etc.
    print(f"  Version: {primary.version}")  # "publishedVersion", "acceptedVersion", etc.
    print(f"  License: {primary.license}")  # "cc-by", etc.
    print(f"  Open Access: {primary.is_oa}")
    print(f"  URL: {primary.landing_page_url}")
    if primary.pdf_url:
        print(f"  PDF: {primary.pdf_url}")

# Best open access location
if work.best_oa_location:
    print(f"\nBest OA location: {work.best_oa_location.source.display_name}")
    print(f"  URL: {work.best_oa_location.landing_page_url}")

# All locations (including repositories, preprint servers, etc.)
print(f"\nFound in {work.locations_count} locations total:")
for i, location in enumerate(work.locations, 1):
    print(f"{i}. {location.source.display_name}")
    print(f"   Version: {location.version}, OA: {location.is_oa}")
```

## Open Access information

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Comprehensive OA information
oa = work.open_access
print(f"Open Access: {oa.is_oa}")
print(f"OA Status: {oa.oa_status}")  
# Possible values: "gold", "green", "hybrid", "bronze", "closed"

if oa.oa_url:
    print(f"Free to read at: {oa.oa_url}")

print(f"Available in repository: {oa.any_repository_has_fulltext}")

# For detailed OA analysis, check locations
gold_oa = any(loc.is_oa and loc.source.type == "journal" 
              for loc in work.locations)
green_oa = any(loc.is_oa and loc.source.type == "repository" 
               for loc in work.locations)
```

## Citations and references

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Citation count
print(f"Cited by {work.cited_by_count:,} other works")

# To actually get citing works:
citing = Works().filter(cites=work.id).get()
print(f"Recent citations: {len(citing.results)}")

# References (works this paper cites)
print(f"\nThis work references {len(work.referenced_works)} other works")
# Show first 5 references
for ref_id in work.referenced_works[:5]:
    print(f"  \u2192 {ref_id}")

# Related works (algorithmically determined)
print(f"\n{len(work.related_works)} related works identified")
for related_id in work.related_works[:3]:
    print(f"  \u2194 {related_id}")

# Citation trend by year
print("\nCitations by year:")
for count in work.counts_by_year:
    print(f"  {count.year}: {count.cited_by_count}")
```

## Topics and research areas

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Primary topic (most relevant)
if work.primary_topic:
    topic = work.primary_topic
    print(f"Primary research topic: {topic.display_name}")
    print(f"  Relevance score: {topic.score:.3f}")
    print(f"  Subfield: {topic.subfield.display_name}")
    print(f"  Field: {topic.field.display_name}")
    print(f"  Domain: {topic.domain.display_name}")

# All topics (up to 3)
print(f"\nAll {len(work.topics)} topics:")
for topic in work.topics:
    print(f"  \u2022 {topic.display_name} (score: {topic.score:.3f})")

# Keywords extracted from the work
if work.keywords:
    print(f"\nKeywords:")
    for kw in work.keywords:
        print(f"  \u2022 {kw.display_name} (score: {kw.score:.3f})")

# Sustainable Development Goals relevance
if work.sustainable_development_goals:
    print(f"\nRelevant to SDGs:")
    for sdg in work.sustainable_development_goals:
        print(f"  \u2022 {sdg.display_name} (score: {sdg.score:.3f})")

# Legacy concepts (being phased out)
print(f"\n{len(work.concepts)} concepts assigned")
for concept in work.concepts[:5]:
    print(f"  \u2022 {concept.display_name} (score: {concept.score:.3f})")
```

## Bibliographic information

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Traditional bibliographic metadata
if work.biblio:
    print(f"Volume: {work.biblio.volume}")
    print(f"Issue: {work.biblio.issue}")
    print(f"Pages: {work.biblio.first_page}-{work.biblio.last_page}")

# Note: These are strings because values like "Spring" or "Supplement 1" exist
```

## All identifiers

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Access all known identifiers
ids = work.ids
print(f"OpenAlex ID: {ids.openalex}")
print(f"DOI: {ids.doi}")
if ids.pmid:
    print(f"PubMed ID: {ids.pmid}")
if ids.pmcid:
    print(f"PubMed Central ID: {ids.pmcid}")
if ids.mag:
    print(f"Microsoft Academic ID: {ids.mag}")

# Check which indexes include this work
print(f"Indexed in: {', '.join(work.indexed_in)}")
# e.g., ["crossref", "pubmed"]
```

## Funding information

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Grant funding
if work.grants:
    print(f"Funded by {len(work.grants)} grants:")
    for grant in work.grants:
        print(f"  \u2022 {grant.funder_display_name}")
        if grant.award_id:
            print(f"    Award: {grant.award_id}")
```

## Article Processing Charges (APC)

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# List price for publishing
if work.apc_list:
    apc = work.apc_list
    print(f"APC list price: {apc.value} {apc.currency}")
    print(f"  (${apc.value_usd} USD)")
    print(f"  Source: {apc.provenance}")

# What was actually paid
if work.apc_paid:
    paid = work.apc_paid
    print(f"APC actually paid: {paid.value} {paid.currency}")
    print(f"  (${paid.value_usd} USD)")
    print(f"  Source: {paid.provenance}")
```

## Additional metadata

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# MeSH terms (for biomedical works from PubMed)
if work.mesh:
    print("MeSH terms:")
    for mesh in work.mesh:
        print(f"  \u2022 {mesh.descriptor_name}")
        if mesh.qualifier_name:
            print(f"    Qualifier: {mesh.qualifier_name}")
        print(f"    Major topic: {mesh.is_major_topic}")

# Full-text availability
print(f"Has indexed fulltext: {work.has_fulltext}")
if work.has_fulltext:
    print(f"Fulltext source: {work.fulltext_origin}")  # "pdf" or "ngrams"

# Collaboration metrics
print(f"Distinct institutions: {work.institutions_distinct_count}")
print(f"Distinct countries: {work.countries_distinct_count}")

# Corresponding author details
if work.corresponding_author_ids:
    print(f"Corresponding authors: {work.corresponding_author_ids}")
if work.corresponding_institution_ids:
    print(f"Corresponding institutions: {work.corresponding_institution_ids}")

# Advanced citation metrics (when available)
if work.fwci is not None:
    print(f"Field-Weighted Citation Impact: {work.fwci:.2f}")
    
if work.citation_normalized_percentile:
    cnp = work.citation_normalized_percentile
    print(f"Citation percentile: {cnp.value:.1%}")
    print(f"  In top 1%: {cnp.is_in_top_1_percent}")
    print(f"  In top 10%: {cnp.is_in_top_10_percent}")
```

## Convenience methods and properties

The Work object includes helpful computed properties:

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

# Abstract as text (mentioned earlier)
abstract_text = work.abstract  # Automatically converted from inverted index

# Check data availability
has_authors = len(work.authorships) > 0
has_references = len(work.referenced_works) > 0
has_fulltext = work.has_fulltext

# Safe access patterns for nested data
# Get first author name (safely)
first_author_name = None
if work.authorships and work.authorships[0].author:
    first_author_name = work.authorships[0].author.display_name

# Get primary source name (safely)
source_name = None
if work.primary_location and work.primary_location.source:
    source_name = work.primary_location.source.display_name

# Count authors from specific country
us_authors = sum(
    1 for authorship in work.authorships
    if "US" in (authorship.countries or [])
)
```

## Working with None values

Many fields can be None, so always check:

```python
# Import Works and fetch work
from openalex import Works
work = Works()["W2741809807"]

def process_abstract(text: str) -> None:
    """Placeholder processing function."""
    pass

# Safe patterns for optional fields
if work.abstract:
    process_abstract(work.abstract)

if work.primary_location:
    source = work.primary_location.source
    if source:
        print(source.display_name)

# Or use Python's optional chaining (3.8+)
source_name = work.primary_location.source.display_name if work.primary_location and work.primary_location.source else None

# For lists, check if they exist and have content
if work.authorships:
    for authorship in work.authorships:
        # Process each author
        pass
```
