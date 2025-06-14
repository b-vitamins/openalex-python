# Filter authors

You can filter authors using the Python client:

```python
from openalex import Authors

# Create a filtered query for authors with ORCID
authors_with_orcid_query = Authors().filter(has_orcid=True)

# Execute the query to get the first page of results
results = authors_with_orcid_query.get()

print(f"Total authors with ORCID: {results.meta.count:,}")  # e.g., 12,345,678
print(f"Showing first {len(results.results)} authors")  # 25
```

Remember: `.filter()` builds the query, `.get()` executes it and returns one page of results.

## Understanding filters vs. results

```python
# This creates a QUERY for millions of authors with ORCID
from openalex import Authors

query_orcid = Authors().filter(has_orcid=True)

# This fetches only the FIRST 25 of those millions
first_page = query_orcid.get()

# To get more results, use pagination
page2 = query_orcid.get(page=2, per_page=100)  # Authors 101-200

# Or iterate through all results (use with extreme caution!)
for author in query_orcid.paginate(per_page=200):
    # This could make thousands of API calls!
    process(author)
```

## Authors attribute filters

You can filter using these attributes of the [`Author`](author-object.md) object:

### Basic attribute filters

```python
# Filter by cited_by_count
from openalex import Authors

highly_cited = Authors().filter(cited_by_count=1000).get()  # Exactly 1000
very_highly_cited = Authors().filter_gt(cited_by_count=10000).get()  # More than 10k

# Filter by works_count  
prolific = Authors().filter_gt(works_count=100).get()  # More than 100 works
new_authors = Authors().filter_lt(works_count=5).get()  # Fewer than 5 works

# Filter by ORCID (specific ID)
specific_author = Authors().filter(
    orcid="https://orcid.org/0000-0001-6187-6610"
).get()

# Filter by Scopus ID
scopus_author = Authors().filter(scopus=36455008000).get()

# Filter by OpenAlex ID (useful for batch operations)
specific_ids = Authors().filter(
    openalex=["A5023888391", "A5014077037"]
).get()
```

### Institutional affiliation filters

```python
# Filter by last known institution
from openalex import Authors

mit_authors = Authors().filter(
    last_known_institutions={"id": "I63966007"}
).get()
# Authors whose most recent affiliation is MIT

# Filter by institution country
us_authors = Authors().filter(
    last_known_institutions={"country_code": "US"}
).get()

# Filter by institution type
university_authors = Authors().filter(
    last_known_institutions={"type": "education"}
).get()

# Filter by ROR ID
ror_authors = Authors().filter(
    last_known_institutions={"ror": "https://ror.org/042nb2s44"}
).get()

# Filter by any affiliation (not just last known)
ever_at_stanford = Authors().filter(
    affiliations={"institution": {"id": "I97018004"}}
).get()
# Authors who have ever been affiliated with Stanford
```

### Geographic filters

```python
# Filter by continent
from openalex import Authors

african_authors = Authors().filter(
    last_known_institutions={"continent": "africa"}
).get()

# Filter by Global South
global_south_authors = Authors().filter(
    last_known_institutions={"is_global_south": True}
).get()
```

### Summary statistics filters

```python
# Filter by h-index
from openalex import Authors

high_impact = Authors().filter_gt(summary_stats={"h_index": 50}).get()
# Authors with h-index > 50

# Filter by i10-index
productive = Authors().filter_gt(summary_stats={"i10_index": 100}).get()
# Authors with >100 papers with 10+ citations

# Filter by 2-year mean citedness
rising_stars = Authors().filter_gt(
    summary_stats={"2yr_mean_citedness": 5.0}
).get()

# Combine metrics
elite_authors = (
    Authors()
    .filter_gt(summary_stats={"h_index": 100})
    .filter_gt(summary_stats={"i10_index": 500})
    .get()
)
```

## Convenience filters

These filters aren't attributes of the Author object, but they're handy for common use cases:

### Text search filters

```python
# Search in display names
from openalex import Authors

smith_authors = Authors().filter(
    display_name={"search": "smith"}
).get()
# Finds authors with "smith" in their name

# Alternative: use search_filter
johnsons = Authors().search_filter(display_name="johnson").get()

# Default search (same as using .search() method)
default_search = Authors().filter(
    default={"search": "albert einstein"}
).get()
```

### Boolean filters

```python
# Has ORCID
from openalex import Authors

authors_with_orcid = Authors().filter(has_orcid=True).get()
authors_without_orcid = Authors().filter(has_orcid=False).get()
```

## Complex filtering

### Combining filters (AND operations)

```python
# US authors at universities with high impact
from openalex import Authors

us_university_stars = (
    Authors()
    .filter(last_known_institutions={
        "country_code": "US",
        "type": "education"
    })
    .filter_gt(summary_stats={"h_index": 30})
    .filter_gt(works_count=50)
    .get()
)

# Specific institution with ORCID
harvard_with_orcid = (
    Authors()
    .filter(last_known_institutions={"id": "I136199984"})  # Harvard
    .filter(has_orcid=True)
    .get()
)
```

### NOT operations

```python
# Authors NOT from the US
from openalex import Authors

non_us_authors = Authors().filter_not(
    last_known_institutions={"country_code": "US"}
).get()

# Authors without ORCID
no_orcid = Authors().filter_not(has_orcid=True).get()
```

### Range queries

```python
# Mid-career authors (10-50 works)
from openalex import Authors

mid_career = (
    Authors()
    .filter_gt(works_count=10)
    .filter_lt(works_count=50)
    .get()
)

# Specific citation range
moderate_impact = (
    Authors()
    .filter_gt(cited_by_count=100)
    .filter_lt(cited_by_count=1000)
    .get()
)
```

## Finding authors from specific institutions

Since you can't search by institution name directly, use a two-step process:

```python
from openalex import Institutions, Authors

# Step 1: Find the institution
institutions = Institutions().search("Yale University").get()
yale = institutions.results[0]
print(f"Found: {yale.display_name} ({yale.id})")

# Step 2: Find authors from that institution
yale_authors = Authors().filter(
    last_known_institutions={"id": yale.id}
).get()
print(f"Yale has {yale_authors.meta.count:,} affiliated authors")

# Or find anyone who was EVER at Yale
ever_at_yale = Authors().filter(
    affiliations={"institution": {"id": yale.id}}
).get()
```

## Performance tips

1. **Be specific**: More filters = fewer results = faster queries
2. **Use select()**: Only fetch fields you need
3. **Check counts first**: See how many results match before paginating
4. **Avoid paginating large result sets**: Use group_by for analytics

```python
# Check result count before deciding to paginate
from openalex import Authors

query = Authors().filter(last_known_institutions={"country_code": "US"})
first_page = query.get()

if first_page.meta.count > 100000:
    print(f"Warning: {first_page.meta.count:,} results!")
    print("Consider adding more filters or using group_by")
else:
    # Safe to paginate through results
    for author in query.paginate():
        process(author)
```
