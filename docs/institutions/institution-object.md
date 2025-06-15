# Institution object

When you fetch an institution using the Python client, you get an `Institution` object with all of OpenAlex's data about that institution. Here's how to access the various properties:

```python
from openalex import Institutions

# Get a specific institution
institution = Institutions()["I114027177"]

# The institution object has all the data as Python attributes
print(type(institution))  # <class 'openalex.models.institution.Institution'>
```

## Basic properties

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Identifiers
print(institution.id)  # "https://openalex.org/I114027177"
print(institution.ror)  # "https://ror.org/0130frc33" (canonical ID)
print(institution.display_name)  # "University of North Carolina at Chapel Hill"

# Alternative names
print(institution.display_name_acronyms)  # ["UNC"]
print(institution.display_name_alternatives)  # ["UNC-Chapel Hill"]

# Basic information
print(institution.type)  # "education"
print(institution.country_code)  # "US"
print(institution.homepage_url)  # "http://www.unc.edu/"

# Scale metrics
print(institution.works_count)  # 202,704
print(institution.cited_by_count)  # 21,199,844

# Dates
print(institution.created_date)  # "2017-08-08"
print(institution.updated_date)  # "2024-01-02T00:27:23.088909"

# Special flags
print(institution.is_super_system)  # False (True for large systems like UC System)
```

## Geographic information

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
geo = institution.geo
if geo:
    print(f"City: {geo.city}")  # "Chapel Hill"
    print(f"Region: {geo.region}")  # "North Carolina"
    print(f"Country: {geo.country}")  # "United States"
    print(f"Country code: {geo.country_code}")  # "US"
    print(f"Coordinates: {geo.latitude}, {geo.longitude}")
    print(f"GeoNames ID: {geo.geonames_city_id}")  # "4460162"
```

## Hierarchical relationships (lineage)

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Lineage shows the institution hierarchy
print(f"Lineage depth: {len(institution.lineage)}")
for i, ancestor_id in enumerate(institution.lineage):
    print(f"  Level {i}: {ancestor_id}")
    
# lineage[0] is always self
# lineage[1] is parent (if exists)
# lineage[2] is grandparent (if exists), etc.

# Get parent institution details
if len(institution.lineage) > 1:
    parent_id = institution.lineage[1]
    parent = Institutions()[parent_id]
    print(f"Parent: {parent.display_name}")
```

## Associated institutions

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Related institutions (siblings, children, related)
print(f"Associated institutions: {len(institution.associated_institutions)}")

for assoc in institution.associated_institutions:
    print(f"\n{assoc.display_name}")
    print(f"  Type: {assoc.type}")
    print(f"  Country: {assoc.country_code}")
    print(f"  Relationship: {assoc.relationship}")  # "parent", "child", or "related"
    print(f"  ROR: {assoc.ror}")
```

## Repositories

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Repositories hosted by this institution
if institution.repositories:
    print(f"Hosts {len(institution.repositories)} repositories:")
    
    for repo in institution.repositories:
        print(f"\n{repo.display_name}")
        print(f"  ID: {repo.id}")
        print(f"  Host: {repo.host_organization_name}")
        print(f"  Lineage: {repo.host_organization_lineage}")
```

## Multiple roles

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# An organization can be an institution, funder, and/or publisher
print(f"This organization has {len(institution.roles)} roles:")

for role in institution.roles:
    print(f"\n{role.role.capitalize()}:")
    print(f"  ID: {role.id}")
    print(f"  Works count: {role.works_count:,}")

# Example: Yale might be:
# - institution (as a university)
# - funder (funding research)
# - publisher (Yale University Press)
```

## Summary statistics

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
stats = institution.summary_stats
if stats:
    print(f"H-index: {stats.h_index}")  # e.g., 985
    print(f"i10-index: {stats.i10_index:,}")  # e.g., 176,682
    print(f"2-year mean citedness: {stats['2yr_mean_citedness']:.2f}")
    
    # These help assess institutional research impact
    if stats.h_index > 500:
        print("This is a very high-impact research institution")
```

## Publication trends

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Track output over the last 10 years
print("Publication trends:")
for count in institution.counts_by_year:
    print(f"  {count.year}: {count.works_count:,} works, "
          f"{count.cited_by_count:,} citations")

# Analyze trends
if len(institution.counts_by_year) >= 2:
    recent = institution.counts_by_year[0]
    previous = institution.counts_by_year[1]
    growth = ((recent.works_count - previous.works_count) / 
              previous.works_count * 100)
    print(f"Year-over-year growth: {growth:+.1f}%")
```

## External identifiers

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
ids = institution.ids
print(f"OpenAlex: {ids.openalex}")
print(f"ROR: {ids.ror}")
if ids.grid:
    print(f"GRID: {ids.grid}")  # Legacy ID
if ids.mag:
    print(f"MAG: {ids.mag}")  # Microsoft Academic Graph ID
if ids.wikipedia:
    print(f"Wikipedia: {ids.wikipedia}")
if ids.wikidata:
    print(f"Wikidata: {ids.wikidata}")
```

## International names

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Names in different languages
if hasattr(institution, 'international') and institution.international:
    if hasattr(institution.international, 'display_name'):
        print("International names:")
        for lang, name in institution.international.display_name.items():
            print(f"  {lang}: {name}")
```

## Images

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Institution logo/seal
if institution.image_url:
    print(f"Logo URL: {institution.image_url}")
    
if institution.image_thumbnail_url:
    print(f"Thumbnail: {institution.image_thumbnail_url}")
```

## Concepts (deprecated)

```python
# Note: x_concepts will be deprecated soon, replaced by Topics
if institution.x_concepts:
    print("Top research areas:")
    for concept in institution.x_concepts[:5]:
        print(f"  {concept.display_name}: {concept.score:.1f}")
```

## Works API URL

```python
# Setup
from openalex import Institutions, Works
institution = Institutions()["I114027177"]
# URL to get all works from this institution
print(f"Works URL: {institution.works_api_url}")

# To actually fetch works using the client:

# Get recent works from this institution
inst_works = (
    Works()
    .filter(institutions={"id": institution.id})
    .filter(publication_year=2023)
    .sort(publication_date="desc")
    .get()
)

print(f"Recent works from {institution.display_name}:")
for work in inst_works.results[:5]:
    print(f"  - {work.title}")
```

## Working with institution data

### Find all sub-institutions

```python
def get_all_children(institution_id):
    """Get all institutions that have this one in their lineage."""
    children = Institutions().filter(lineage=institution_id).get()
    
    # Exclude self
    children_only = [
        inst for inst in children.results 
        if inst.id != institution_id
    ]
    
    return children_only

# Example: Find all UC campuses
uc_system = "I2803209242"
campuses = get_all_children(uc_system)
print(f"UC System campuses:")
for campus in campuses:
    print(f"  - {campus.display_name}")
```

### Analyze institutional collaboration

```python
from openalex import Institutions, Works

institution = Institutions()["I114027177"]
def analyze_collaborations(institution_id, year=2023):
    """Find top collaborating institutions."""
    from openalex import Works
    
    # Get sample of recent works
    works = (
        Works()
        .filter(institutions={"id": institution_id})
        .filter(publication_year=year)
        .select(["id", "authorships"])
        .get(per_page=200)
    )
    
    # Count collaborating institutions
    collab_counts = {}
    for work in works.results:
        institutions_in_work = set()
        for authorship in work.authorships:
            for inst in authorship.institutions:
                if inst.id != institution_id:
                    institutions_in_work.add((inst.id, inst.display_name))
        
        for inst_id, inst_name in institutions_in_work:
            if inst_id not in collab_counts:
                collab_counts[inst_id] = {"name": inst_name, "count": 0}
            collab_counts[inst_id]["count"] += 1
    
    # Sort by collaboration frequency
    top_collabs = sorted(
        collab_counts.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )[:10]
    
    print(f"Top collaborators for {institution.display_name}:")
    for inst_id, data in top_collabs:
        print(f"  {data['name']}: {data['count']} joint works")

# Example usage
analyze_collaborations(institution.id)
```

### Compare peer institutions

```python
from openalex import Institutions

def compare_peers(institution_ids):
    """Compare multiple institutions."""
    institutions = []
    for inst_id in institution_ids:
        inst = Institutions()[inst_id]
        institutions.append(inst)
    
    print("Institution comparison:")
    print("-" * 80)
    print(f"{'Institution':<40} {'Works':>10} {'Citations':>15} {'H-index':>10}")
    print("-" * 80)
    
    for inst in institutions:
        h_index = inst.summary_stats.h_index if inst.summary_stats else "N/A"
        print(f"{inst.display_name:<40} "
              f"{inst.works_count:>10,} "
              f"{inst.cited_by_count:>15,} "
              f"{h_index:>10}")

# Compare Ivy League schools
ivy_league = [
    "I136199984",  # Harvard
    "I35403681",   # Yale  
    "I8689696",    # Princeton
    "I142606108",  # Columbia
]
compare_peers(ivy_league)
```

## Handling missing data

Many fields can be None or empty:

```python
# Setup
from openalex import Institutions
institution = Institutions()["I114027177"]
# Safe access patterns
if institution.geo:
    print(f"Located in: {institution.geo.city}")
else:
    print("Location information not available")

if institution.homepage_url:
    print(f"Website: {institution.homepage_url}")
else:
    print("No website listed")

# Handle missing statistics
if institution.summary_stats and institution.summary_stats.h_index is not None:
    print(f"H-index: {institution.summary_stats.h_index}")
else:
    print("H-index not calculated")

# Check for associated institutions
if not institution.associated_institutions:
    print("No associated institutions listed")

# International names might not exist
intl_names = getattr(institution, 'international', None)
if intl_names and hasattr(intl_names, 'display_name'):
    print(f"Has names in {len(intl_names.display_name)} languages")
```

## The DehydratedInstitution object

When institutions appear in other objects (like in work authorships), you get a simplified version:

```python
# Setup
from openalex import Institutions, Works
institution = Institutions()["I114027177"]
# Get a work to see dehydrated institutions
work = Works()["W2741809807"]

# Access dehydrated institutions in authorships
for authorship in work.authorships:
    for inst in authorship.institutions:
        # Only these fields are available in dehydrated version:
        print(inst.id)
        print(inst.display_name)
        print(inst.ror)
        print(inst.country_code)
        print(inst.type)
        print(inst.lineage)
        
        # To get full details, fetch the complete institution:
        full_inst = Institutions()[inst.id]
        print(f"Full works count: {full_inst.works_count}")
```
