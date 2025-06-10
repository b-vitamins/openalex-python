# Get a single source

It's easy to get a source using the Python client:

```python
from openalex import Sources

# Get a specific source by their OpenAlex ID
source = Sources()["S137773608"]

# Alternative syntax using the get method
source = Sources().get("S137773608")
```

That will return a [`Source`](source-object.md) object, describing everything OpenAlex knows about the source with that ID:

```python
# Access source properties directly as Python attributes
print(source.id)  # "https://openalex.org/S137773608"
print(source.issn_l)  # "0028-0836"
print(source.issn)  # ["1476-4687", "0028-0836"]
print(source.display_name)  # "Nature"
print(source.type)  # "journal"
print(source.works_count)  # Number of works in this source
print(source.cited_by_count)  # Total citations to works in this source
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
# Fetch multiple specific sources in one API call
source_ids = ["S137773608", "S125754415", "S202381698"]
multiple_sources = Sources().filter(openalex=source_ids).get()

print(f"Found {len(multiple_sources.results)} sources")
for src in multiple_sources.results:
    print(f"- {src.display_name} ({src.type})")
    print(f"  Publisher: {src.host_organization_name}")
    print(f"  Open Access: {src.is_oa}")
```

**Tip**: Sources are also available via an alias:
```python
from openalex import Journals
journals = Journals()  # Same as Sources()
```

## External IDs

You can look up sources using external IDs such as an ISSN:

```python
# Get source by ISSN
nature_comms = Sources()["issn:2041-1723"]

# Multiple ISSN formats work
source = Sources()["issn:1476-4687"]  # Print ISSN
source = Sources()["issn:0028-0836"]  # Electronic ISSN

# Get source by Wikidata ID
source = Sources()["wikidata:Q180445"]

# Get source by MAG ID
source = Sources()["mag:137773608"]

# Get source by Fatcat ID
source = Sources()["fatcat:z3ijzhu7zzey3f7jwws7rzopoq"]
```

Available external IDs for sources are:

| External ID | URN | Example |
|------------|-----|---------|
| ISSN | `issn` | `issn:2041-1723` |
| Fatcat | `fatcat` | `fatcat:z3ijzhu7zzey3f7jwws7rzopoq` |
| Microsoft Academic Graph (MAG) | `mag` | `mag:137773608` |
| Wikidata | `wikidata` | `wikidata:Q180445` |

## Select fields

You can use `select` to limit the fields that are returned in a source object:

```python
# Fetch only specific fields to reduce response size
minimal_source = Sources().select([
    "id", 
    "display_name", 
    "type",
    "is_oa"
]).get("S137773608")

# Now only the selected fields are populated
print(minimal_source.display_name)  # Works
print(minimal_source.works_count)  # None (not selected)
```
