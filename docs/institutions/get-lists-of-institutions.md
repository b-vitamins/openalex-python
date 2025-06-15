# Get lists of institutions

You can get lists of institutions using the Python client:

```python
from openalex import Institutions

# Create a query for all institutions (no filters applied)
all_institutions_query = Institutions()

# Execute the query to get the FIRST PAGE of results
first_page = all_institutions_query.get()

# Note: With ~109,000 total institutions, this is manageable
# (unlike works with 240M+ or authors with 93M+)
print(f"Total institutions: {first_page.meta.count:,}")  # ~109,000
print(f"Institutions in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Institution objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Understanding the results

```python
# Each result shows institution information
from openalex import Institutions

first_page = Institutions().get()
for institution in first_page.results[:5]:  # First 5 institutions
    print(f"\n{institution.display_name}")
    print(f"  Type: {institution.type}")
    print(f"  Country: {institution.country_code}")
    print(f"  Works: {institution.works_count:,}")
    print(f"  Citations: {institution.cited_by_count:,}")
    if institution.geo:
        print(f"  Location: {institution.geo.city}, {institution.geo.country}")
```

## Page and sort institutions

You can control pagination and sorting:

```python
from openalex import Institutions

# Get a specific page with custom page size
page2 = Institutions().get(per_page=50, page=2)
# This returns institutions 51-100

# Sort by different fields
# Largest institutions by work count
largest_institutions = Institutions().sort(works_count="desc").get()

# Most cited institutions  
most_cited = Institutions().sort(cited_by_count="desc").get()

# Alphabetical by name
alphabetical = Institutions().sort(display_name="asc").get()

# Get ALL institutions (feasible with ~109,000)
# Limit to the first 1,000 to avoid huge downloads
all_institutions = []
for institution in Institutions().paginate(per_page=200):
    all_institutions.append(institution)
    if len(all_institutions) >= 1000:  # Stop after 1,000
        break
print(f"Fetched {len(all_institutions)} institutions")
```

## Sample institutions

Get a random sample of institutions:

```python
# Get 50 random institutions
from openalex import Institutions

# Get 50 random institutions
random_sample = Institutions().sample(50).get(per_page=50)

# Use a seed for reproducible random sampling
reproducible_sample = Institutions().sample(50, seed=42).get(per_page=50)

# Sample from filtered results
university_sample = (
    Institutions()
    .filter(type="education")  # Only universities
    .sample(10)
    .get()
)
```

## Select fields

Limit the fields returned to improve performance:

```python
# Request only specific fields
from openalex import Institutions

# Request only specific fields
minimal_institutions = Institutions().select([
    "id", 
    "display_name",
    "ror",
    "country_code",
    "type"
]).get()

# This reduces response size significantly
for institution in minimal_institutions.results:
    print(f"{institution.display_name} ({institution.country_code})")
    print(institution.cited_by_count)  # None - not selected
```

## Practical examples

### Example: Analyze institutions by type

```python
# Get different types of institutions
from openalex import Institutions

# Get different types of institutions
education = Institutions().filter(type="education").get()
healthcare = Institutions().filter(type="healthcare").get()
companies = Institutions().filter(type="company").get()
government = Institutions().filter(type="government").get()

print(f"Universities: {education.meta.count:,}")
print(f"Healthcare: {healthcare.meta.count:,}")
print(f"Companies: {companies.meta.count:,}")
print(f"Government: {government.meta.count:,}")
```

### Example: Find research powerhouses

```python
# Get top research institutions globally
from openalex import Institutions

# Get top research institutions globally
global_leaders = (
    Institutions()
    .filter(type="education")
    .filter_gt(works_count=10000)
    .sort(cited_by_count="desc")
    .get(per_page=20)
)

print("Top 20 research universities by citations:")
for i, inst in enumerate(global_leaders.results, 1):
    print(f"{i}. {inst.display_name} ({inst.country_code})")
    print(f"   Works: {inst.works_count:,}, Citations: {inst.cited_by_count:,}")
```

### Example: Filter by type and location

```python
from openalex import Institutions

# US healthcare institutions in Boston
boston_healthcare = (
    Institutions()
    .search("Boston")
    .filter(type="healthcare")
    .filter(country_code="US")
    .get()
)

print(
    f"Boston healthcare institutions: {boston_healthcare.meta.count}"
)
for inst in boston_healthcare.results[:5]:
    print(f"- {inst.display_name} ({inst.geo.city})")
```

Continue on to learn how you can [filter](filter-institutions.md) and [search](search-institutions.md) lists of institutions.
