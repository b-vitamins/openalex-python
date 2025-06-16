# Get a single institution

It's easy to get an institution using the Python client:

```python
from openalex import Institutions

# Get a specific institution by their OpenAlex ID
institution = Institutions()["I27837315"]

# Alternative syntax using the get method
institution = Institutions().get("I27837315")
```

That will return an [`Institution`](institution-object.md) object, describing everything OpenAlex knows about the institution with that ID:

```python
from openalex import Institutions

institution = Institutions()["I27837315"]  # University of Michigan-Ann Arbor

print(f"OpenAlex ID: {institution.id}")
print(f"ROR: {institution.ror}")
print(f"GRID: {institution.ids.grid}")
print(f"Wikidata: {institution.ids.wikidata}")
print(f"Name: {institution.display_name}")
print(f"Country: {institution.country_code}")
print(f"Type: {institution.type}")
print(f"Works: {institution.works_count:,}")
print(f"Citations: {institution.cited_by_count:,}")
if institution.geo:
    print(
        f"Location: {institution.geo.city}, {institution.geo.country}"
    )
    print(
        f"Region: {institution.geo.region}"
    )
    print(
        f"Coordinates: {institution.geo.latitude}, {institution.geo.longitude}"
    )
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
from openalex import Institutions

institution_ids = ["I27837315", "I136199984", "I97018004"]
multiple_institutions = Institutions().filter(openalex=institution_ids).get()

print(f"Found {len(multiple_institutions.results)} institutions")
for inst in multiple_institutions.results:
    print(f"- {inst.display_name} ({inst.type})")
    print(f"  Location: {inst.geo.city}, {inst.geo.country}")
```

## External IDs

You can look up institutions using external IDs such as a ROR ID:

```python
from openalex import Institutions

# Get institution by ROR ID (multiple formats supported)
institution = Institutions()["ror:https://ror.org/00cvxb145"]
institution = Institutions()["ror:00cvxb145"]  # Shorter format

# Get institution by Wikidata ID
institution = Institutions()["wikidata:Q192334"]

# Get institution by MAG ID
institution = Institutions()["mag:114027177"]

# Direct lookup by full URL also works
institution = Institutions()["https://ror.org/00jmfr291"]
```

Available external IDs for institutions are:

| External ID | URN | Example |
|------------|-----|---------|
| ROR | `ror` | `ror:00jmfr291` |
| Microsoft Academic Graph (MAG) | `mag` | `mag:114027177` |
| Wikidata | `wikidata` | `wikidata:Q192334` |

## Select fields

You can use `select` to limit the fields that are returned in an institution object:

```python
from openalex import Institutions

# Fetch only specific fields to reduce response size
minimal_institution = Institutions().select([
    "id",
    "display_name",
    "country_code",
    "type"
])["I27837315"]

# Now only the selected fields are populated
print(minimal_institution.display_name)  # Works
print(minimal_institution.works_count)  # None (not selected)
```
