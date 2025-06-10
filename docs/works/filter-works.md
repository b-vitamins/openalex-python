# Filter works

It's easy to filter works using the Python client:

```python
from openalex import Works

# Create a filtered query for works published in 2020
works_2020_query = Works().filter(publication_year=2020)

# Execute the query to get the first page of results
results = works_2020_query.get()

print(f"Total works from 2020: {results.meta.count:,}")  # e.g., 4,567,890
print(f"Showing first {len(results.results)} works")  # 25
```

\ud83d\udca1 Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Understanding filters vs. results

```python
# This creates a QUERY for ~5 million works from 2023
query_2023 = Works().filter(publication_year=2023)

# This fetches only the FIRST 25 of those millions
first_page = query_2023.get()

# To get more results, use pagination
page2 = query_2023.get(page=2, per_page=100)  # Works 101-200

# Or iterate through all results (use with caution!)
for work in query_2023.paginate(per_page=200):
    # This will make ~25,000 API calls to get all 5M works!
    process(work)
```

## Works attribute filters

You can filter using these attributes of the [`Work`](work-object.md) object:

\u26a0\ufe0f The `host_venue` and `alternate_host_venues` properties have been deprecated in favor of `primary_location` and `locations`.

### Basic attribute filters

```python
# Filter by DOI (returns at most one work)
specific_work = Works().filter(doi="https://doi.org/10.1038/nature12373").get()

# Filter by publication year
recent_works = Works().filter(publication_year=2023).get()
# Returns first 25 works from 2023 (out of millions)

# Filter by year range using a list
range_works = Works().filter(publication_year=[2020, 2021, 2022]).get()
# Returns first 25 works from 2020-2022

# Filter by open access status
oa_works = Works().filter(open_access={"is_oa": True}).get()
# Returns first 25 OA works (out of ~100 million)

# Filter by work type
research_articles = Works().filter(type="article").get()
datasets = Works().filter(type="dataset").get()

# Filter by language
english_works = Works().filter(language="en").get()
spanish_works = Works().filter(language="es").get()

# Filter by citation count (exact match)
exactly_100_citations = Works().filter(cited_by_count=100).get()
```

### Comparison operators

```python
# Greater than: find highly-cited works
highly_cited = Works().filter_gt(cited_by_count=1000).get()
# Returns first 25 works with >1000 citations

# Less than: find recent works with fewer citations  
less_cited = Works().filter_lt(cited_by_count=10).get()

# Combine comparisons for ranges
citation_range = (
    Works()
    .filter_gt(cited_by_count=100)
    .filter_lt(cited_by_count=500)
    .get()
)
# Returns works with 100 < citations < 500

# Date comparisons
recent = Works().filter_gt(publication_year=2020).get()
older = Works().filter_lt(publication_year=2000).get()
```

### Author and institution filters

```python
# Find works by a specific author (using their OpenAlex ID)
author_works = Works().filter(
    authorships={"author": {"id": "A5023888391"}}
).get()
# Returns first 25 works by this author

# Filter by author ORCID
orcid_works = Works().filter(
    authorships={"author": {"orcid": "https://orcid.org/0000-0001-6187-6610"}}
).get()

# Find works from a specific institution
mit_works = Works().filter(
    authorships={"institutions": {"id": "I63966007"}}
).get()
# Returns first 25 works where at least one author is from MIT

# Filter by institution ROR ID
ror_works = Works().filter(
    authorships={"institutions": {"ror": "https://ror.org/042nb2s44"}}
).get()

# Filter by country (returns works with authors from these countries)
us_works = Works().filter(
    authorships={"institutions": {"country_code": "US"}}
).get()

# Multiple countries (OR operation within the list)
international = Works().filter(
    authorships={"institutions": {"country_code": ["US", "UK", "CA"]}}
).get()
# Returns works where authors are from US OR UK OR CA

# Filter by corresponding author
corresponding = Works().filter(authorships={"is_corresponding": True}).get()
# Returns works that have corresponding author information
```

### Location and open access filters

```python
# Find works published in a specific journal
nature_works = Works().filter(
    primary_location={"source": {"id": "S137773608"}}
).get()
# Returns first 25 works published in Nature

# Filter by license type
cc_by_works = Works().filter(
    best_oa_location={"license": "cc-by"}
).get()
# Returns works with Creative Commons BY license

# Filter by version
published_versions = Works().filter(
    primary_location={"version": "publishedVersion"}
).get()

# Find works in specific repository
arxiv_works = Works().filter(
    locations={"source": {"id": "S4306402567"}}
).get()
# Returns works that have a copy in arXiv
```

### Topic and concept filters

```python
# Filter by primary topic (e.g., Machine Learning)
ml_works = Works().filter(primary_topic={"id": "T10159"}).get()
# Returns first 25 works about machine learning

# Filter by topic domain (e.g., Health Sciences)
health_works = Works().filter(
    topics={"domain": {"id": "D4"}}
).get()

# Filter by concepts (deprecated but still available)
medicine_works = Works().filter(concepts={"id": "C71924100"}).get()
```

## Convenience filters

These filters aren't attributes of the Work object, but they're handy for common use cases:

### Text search filters

```python
# Search in abstracts only
ai_abstracts = Works().filter(
    abstract={"search": "artificial intelligence"}
).get()
# Returns works with "artificial intelligence" in the abstract

# Search in titles only
climate_titles = Works().filter(
    title={"search": "climate change"}
).get()

# Search in both title and abstract
quantum_search = Works().filter(
    title_and_abstract={"search": "quantum computing"}
).get()

# Full-text search (when available)
ml_fulltext = Works().filter(
    fulltext={"search": "machine learning algorithms"}
).get()
# Only searches works where we have full-text indexed

# Search in author affiliation strings
amsterdam_affiliations = Works().filter(
    raw_affiliation_strings={"search": "University of Amsterdam"}
).get()
```

### Count filters

```python
# Filter by number of authors
single_author_works = Works().filter(authors_count=1).get()

# Works with many authors (>10)
collaborative_works = Works().filter_gt(authors_count=10).get()

# Works with many concepts assigned
interdisciplinary = Works().filter_gt(concepts_count=5).get()

# International collaborations (3+ countries)
international_collabs = Works().filter_gt(countries_distinct_count=3).get()
```

### Date range filters

```python
# Works published from a specific date onwards
recent_works = Works().filter(from_publication_date="2023-01-01").get()
# Returns first 25 works published after Jan 1, 2023

# Works published before a date
older_works = Works().filter(to_publication_date="2020-12-31").get()

# Combine for a date range
pandemic_era = Works().filter(
    from_publication_date="2020-01-01",
    to_publication_date="2023-12-31"
).get()

# Filter by when works were added to OpenAlex (requires API key)
newly_added = Works().filter(from_created_date="2024-01-01").get()

# Filter by when works were last updated
recently_updated = Works().filter(from_updated_date="2024-06-01").get()
```

### Citation relationship filters

```python
# Find works that cite a specific paper
citing_works = Works().filter(cites="W2741809807").get()
# Returns first 25 works that reference W2741809807

# Find works cited by a specific paper  
references = Works().filter(cited_by="W2766808518").get()
# Returns works in the reference list of W2766808518

# Find related works (algorithmically determined)
related = Works().filter(related_to="W2486144666").get()
```

### Boolean and existence filters

```python
# Check for presence of identifiers
has_doi = Works().filter(has_doi=True).get()
has_pmid = Works().filter(has_pmid=True).get()
has_pmcid = Works().filter(has_pmcid=True).get()

# Check for content availability  
has_abstract = Works().filter(has_abstract=True).get()
has_fulltext = Works().filter(has_fulltext=True).get()  # Has indexed full text
has_references = Works().filter(has_references=True).get()

# Check for author information
has_orcid = Works().filter(has_orcid=True).get()
# At least one author has ORCID

# Special work types
paratext_only = Works().filter(is_paratext=True).get()  # Editorials, TOCs, etc.
retracted_works = Works().filter(is_retracted=True).get()

# Open access version filters
has_accepted_version = Works().filter(
    has_oa_accepted_or_published_version=True
).get()
has_preprint = Works().filter(has_oa_submitted_version=True).get()
```

## Combining filters

### AND operations (default)

```python
# Each filter() call adds an AND condition
recent_ml_papers = (
    Works()
    .filter(publication_year=2023)  # AND
    .filter(primary_topic={"id": "T10159"})  # AND
    .filter(open_access={"is_oa": True})  # AND
    .filter_gt(cited_by_count=10)
    .get()
)
# Returns OA ML papers from 2023 with >10 citations
# This is a very specific query that might return 0-100 results
```

### OR operations

```python
# OR within a single field (use list)
multilingual = Works().filter(language=["en", "es", "fr"]).get()
# Returns works in English OR Spanish OR French

# OR between different values of same field
article_or_preprint = Works().filter_or(
    type="article",
    type="preprint"
).get()

# OR with different fields requires multiple queries
# (The API doesn't support OR across different fields)
```

### NOT operations

```python
# Exclude retracted works
not_retracted = Works().filter_not(is_retracted=True).get()

# Exclude specific types
not_paratext = Works().filter_not(is_paratext=True).get()

# Combine NOT with other filters
good_recent_works = (
    Works()
    .filter(publication_year=2023)
    .filter_not(is_retracted=True)
    .filter_not(is_paratext=True)
    .filter_gt(cited_by_count=5)
    .get()
)
```

## Nested filtering examples

```python
# Complex author-institution query
harvard_chemists = Works().filter(
    authorships={
        "institutions": {
            "id": "I136199984",  # Harvard
            "lineage": "I136199984"  # Include sub-institutions
        }
    },
    primary_topic={
        "field": {"display_name": "Chemistry"}
    }
).get()

# Multiple location criteria
gold_oa_in_doaj = Works().filter(
    locations={
        "source": {
            "is_in_doaj": True,
            "type": "journal"
        },
        "is_oa": True,
        "version": "publishedVersion"
    }
).get()

# Grant-funded research
nsf_funded_recent = Works().filter(
    grants={"funder": "F4320306076"},  # NSF
    publication_year=[2022, 2023, 2024]
).get()
```

## Performance tips

1. **Be specific**: More filters = fewer results = faster queries
2. **Use select()**: Only fetch fields you need
3. **Avoid paginating large result sets**: Use group_by for analytics
4. **Check meta.count first**: See how many results match before paginating

```python
# Check result count before deciding to paginate
query = Works().filter(authorships={"institutions": {"id": "I12345"}})
first_page = query.get()

if first_page.meta.count > 10000:
    print(f"Warning: {first_page.meta.count:,} results!")
    print("Consider adding more filters or using group_by")
else:
    # Safe to paginate through results
    for work in query.paginate():
        process(work)
```
