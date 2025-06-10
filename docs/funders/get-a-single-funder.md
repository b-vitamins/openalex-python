# Get a single funder

It's easy to get a funder using the Python client:

```python
from openalex import Funders

# Get a specific funder by their OpenAlex ID
funder = Funders()["F4320332161"]

# Alternative syntax using the get method
funder = Funders().get("F4320332161")
```

That will return a [`Funder`](funder-object.md) object, describing everything OpenAlex knows about the funder with that ID:

```python
# Access funder properties directly as Python attributes
print(funder.id)  # "https://openalex.org/F4320332161"
print(funder.display_name)  # "National Institutes of Health"
print(funder.alternate_titles)  # ["US National Institutes of Health", "Institutos Nacionales de la Salud", "NIH"]
print(funder.country_code)  # "US"
print(funder.description)  # "medical research organization in the United States"
print(funder.works_count)  # Number of works funded
print(funder.grants_count)  # Number of grants
print(funder.cited_by_count)  # Total citations to funded works
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
# Fetch multiple specific funders in one API call
funder_ids = ["F4320332161", "F4320321001", "F4320306076"]
multiple_funders = Funders().filter(openalex=funder_ids).get()

print(f"Found {len(multiple_funders.results)} funders")
for fund in multiple_funders.results:
    print(f"- {fund.display_name} ({fund.country_code})")
    print(f"  Grants: {fund.grants_count:,}")
    print(f"  Works: {fund.works_count:,}")
```

## External IDs

You can look up funders using external IDs such as a Wikidata ID:

```python
# Get funder by Wikidata ID
nih = Funders()["wikidata:Q390551"]

# Get funder by ROR ID
nsf = Funders()["ror:021nxhr62"]
nsf = Funders()["ror:https://ror.org/021nxhr62"]  # Full URL also works

# Get funder by Crossref ID
wellcome = Funders()["crossref:100010269"]

# Get funder by DOI
funder = Funders()["doi:10.13039/100000002"]
```

Available external IDs for funders are:

| External ID | URN | Example |
|------------|-----|---------|
| ROR | `ror` | `ror:021nxhr62` |
| Wikidata | `wikidata` | `wikidata:Q390551` |
| Crossref | `crossref` | `crossref:100000002` |
| DOI | `doi` | `doi:10.13039/100000002` |

## Select fields

You can use `select` to limit the fields that are returned in a funder object:

```python
# Fetch only specific fields to reduce response size
minimal_funder = Funders().select([
    "id", 
    "display_name", 
    "country_code",
    "grants_count"
]).get("F4320332161")

# Now only the selected fields are populated
print(minimal_funder.display_name)  # Works
print(minimal_funder.works_count)  # None (not selected)
```
