# Get lists of sources

You can get lists of sources using the Python client:

```python
from openalex import Sources

# Create a query for all sources (no filters applied)
all_sources_query = Sources()

# Execute the query to get the FIRST PAGE of results
first_page = all_sources_query.get()

# Note: With ~249,000 total sources, pagination is needed
print(f"Total sources: {first_page.meta.count:,}")  # ~249,000
print(f"Sources in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Source objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
from openalex import Sources

first_page = Sources().get()
for source in first_page.results[:5]:  # First 5 sources
    print(f"\n{source.display_name}")
    print(f"  Type: {source.type}")
    print(f"  Publisher: {source.host_organization_name}")
    print(f"  Open Access: {source.is_oa}")
    print(f"  Works: {source.works_count:,}")
    print(f"  Citations: {source.cited_by_count:,}")
    if source.issn_l:
        print(f"  ISSN-L: {source.issn_l}")
```

## Page and sort sources

You can control pagination and sorting:

```python
from openalex import Sources

# Get a specific page with custom page size
page2 = Sources().get(per_page=50, page=2)
# This returns sources 51-100

# Sort by different fields
# Most cited sources (highest impact)
most_cited = Sources().sort(cited_by_count="desc").get()

# Sources with most works
most_productive = Sources().sort(works_count="desc").get()

# Sort by impact factor (2-year mean citedness)
high_impact = Sources().sort(**{"summary_stats.2yr_mean_citedness": "desc"}).get()

# Alphabetical by name
alphabetical = Sources().sort(display_name="asc").get()

# Get ALL sources (feasible with ~249,000)
# This will make about 1,250 API calls at 200 per page
all_sources = []
for source in Sources().paginate(per_page=200, cursor="*", max_results=12000):
    all_sources.append(source)
print(f"Fetched {len(all_sources)} sources")
```

## Sample sources

Get a random sample of sources:

```python
from openalex import Sources

# Get 10 random sources
random_sample = Sources().sample(10).get(per_page=10)

# Use a seed for reproducible random sampling
reproducible_sample = Sources().sample(10, seed=42).get(per_page=10)

# Sample from filtered results
oa_journal_sample = (
    Sources()
    .filter(type="journal")
    .filter(is_oa=True)
    .sample(20)
    .get(per_page=20)
)
```

## Select fields

Limit the fields returned to improve performance:

```python
from openalex import Sources

# Request only specific fields
minimal_sources = Sources().select([
    "id", 
    "display_name",
    "issn",
    "type",
    "is_oa",
    "works_count"
]).get()

# This reduces response size significantly
for source in minimal_sources.results:
    print(f"{source.display_name} - {source.type}")
    print(source.host_organization_name)  # None - not selected
```

## Practical examples

### Example: Analyze source types

```python
from openalex import Sources

# Get different types of sources
journals = Sources().filter(type="journal").get()
repositories = Sources().filter(type="repository").get()
conferences = Sources().filter(type="conference").get()
ebook_platforms = Sources().filter(type="ebook platform").get()

print(f"Journals: {journals.meta.count:,}")
print(f"Repositories: {repositories.meta.count:,}")
print(f"Conferences: {conferences.meta.count:,}")
print(f"eBook platforms: {ebook_platforms.meta.count:,}")
```

### Example: Find high-impact journals

```python
from openalex import Sources

# Get top scientific journals by impact
high_impact_journals = (
    Sources()
    .filter(type="journal")
    .filter_gt(summary_stats={"2yr_mean_citedness": 5.0})
    .filter_gt(works_count=1000)
    .sort(**{"summary_stats.2yr_mean_citedness": "desc"})
    .get(per_page=20)
)

print("Top 20 high-impact journals (IF > 5.0):")
for i, journal in enumerate(high_impact_journals.results, 1):
    impact_factor = journal.summary_stats.two_year_mean_citedness
    print(f"{i}. {journal.display_name}")
    print(f"   Impact Factor: {impact_factor:.2f}")
    print(f"   Works: {journal.works_count:,}")
```

### Example: Open Access landscape

```python
from openalex import Sources

# Analyze OA vs subscription sources
def analyze_oa_landscape():
    # Get counts for different OA statuses
    all_sources = Sources().get()
    oa_sources = Sources().filter(is_oa=True).get()
    doaj_sources = Sources().filter(is_in_doaj=True).get()
    
    # Calculate percentages
    oa_percent = (oa_sources.meta.count / all_sources.meta.count) * 100
    doaj_percent = (doaj_sources.meta.count / all_sources.meta.count) * 100
    
    print(f"Total sources: {all_sources.meta.count:,}")
    print(f"Open Access sources: {oa_sources.meta.count:,} ({oa_percent:.1f}%)")
    print(f"DOAJ listed: {doaj_sources.meta.count:,} ({doaj_percent:.1f}%)")
    
    # Get top OA journals
    top_oa = (
        Sources()
        .filter(is_oa=True)
        .filter(type="journal")
        .sort(cited_by_count="desc")
        .get(per_page=10)
    )
    
    print("\nTop 10 Open Access journals by citations:")
    for journal in top_oa.results:
        print(f"  - {journal.display_name}: {journal.cited_by_count:,} citations")

analyze_oa_landscape()
```

Continue on to learn how you can [filter](filter-sources.md) and [search](search-sources.md) lists of sources.
