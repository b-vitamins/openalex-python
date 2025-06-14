# Get lists of institutions

You can get lists of institutions using the Python client:

```python
from openalex import Institutions

# Fetch the first page of institutions (25 results by default)
first_page = Institutions().get()

print(f"Total institutions: {first_page.meta.count:,}")  # ~109,000
print(f"Institutions in this response: {len(first_page.results)}")  # 25
print(f"Current page: {first_page.meta.page}")  # 1

# Show the first few institutions
for institution in first_page.results[:5]:
    print(f"\n{institution.display_name}")
    print(f"  Type: {institution.type}")
    print(f"  Country: {institution.country_code}")
    print(f"  Works: {institution.works_count:,}")
    print(f"  Citations: {institution.cited_by_count:,}")
    if institution.geo:
        print(f"  Location: {institution.geo.city}, {institution.geo.country}")
```

The response contains:
- **meta**: Information about pagination and total results
- **results**: List of Institution objects for the current page
- **group_by**: Empty list (used only when grouping results)

## Page and sort institutions

You can control pagination and sorting:

```python
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
# This will make about 550 API calls at 200 per page
all_institutions = []
for institution in Institutions().paginate(per_page=200):
    all_institutions.append(institution)
print(f"Fetched all {len(all_institutions)} institutions")
```

## Sample institutions

Get a random sample of institutions:

```python
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

```python
from openalex import Institutions

# Universities in the United States
us_universities = (
    Institutions()
    .filter(country_code="US")
    .filter(type="education")
    .get(per_page=5)
)
for inst in us_universities.results:
    print(f"- {inst.display_name} ({inst.country_code})")
```

```python
from openalex import Institutions

# Institutions in Cambridge, Massachusetts
cambridge_ma = Institutions().filter(
    geo={"city": "Cambridge", "region": "Massachusetts"}
).get()
print(f"Institutions in Cambridge, MA: {cambridge_ma.meta.count}")
```

## Practical examples

### Example: Analyze institutions by type

```python
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

Continue on to learn how you can [filter](filter-institutions.md) and [search](search-institutions.md) lists of institutions.
