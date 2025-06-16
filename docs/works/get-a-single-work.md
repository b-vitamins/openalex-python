# Get a single work

It's easy to get a work using the Python client. Here's an example:

```python
from openalex import Works

# Get a specific work by its OpenAlex ID
work = Works()["W2741809807"]

# Alternative syntax using the get method
work = Works().get("W2741809807")
```

That will return a [`Work`](work-object.md) object, describing everything OpenAlex knows about the work with that ID.

```python
# Access work properties directly as Python attributes
from openalex import Works

work = Works()["W2741809807"]
print(work.id)  # "https://openalex.org/W2741809807"
print(work.doi)  # "https://doi.org/10.7717/peerj.4375"
print(work.title)  # "The state of OA: a large-scale analysis..."
print(work.publication_year)  # 2018
print(work.publication_date)  # "2018-02-13"
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
# Import Works query builder
from openalex import Works

# Fetch multiple specific works in one API call
ids = ["W2741809807", "W2755950973", "W2898525390"]
multiple_works = Works().filter(openalex_id=ids).get()

# This returns a page with up to 50 works (if all IDs are valid)
print(f"Found {len(multiple_works.results)} works")
```

## External IDs

You can look up works using external IDs such as a DOI:

```python
# Import Works query builder
from openalex import Works

# Get work by DOI (multiple formats supported)
work = Works()["https://doi.org/10.7717/peerj.4375"]
work = Works()["doi:10.7717/peerj.4375"]  # Shorter URN format

# Get work by PubMed ID
work = Works()["pmid:14907713"]

# Get work by PubMed Central ID (use a valid PMCID)
work = Works()["pmcid:PMC3000000"]

# Get work by Microsoft Academic Graph ID
work = Works()["mag:2741809807"]
```

Available external IDs for works are:

| External ID                    | URN     |
| ------------------------------ | ------- |
| DOI                            | `doi`   |
| Microsoft Academic Graph (MAG) | `mag`   |
| PubMed ID (PMID)               | `pmid`  |
| PubMed Central ID (PMCID)      | `pmcid` |

\u26a0\ufe0f You must make sure that the ID(s) you supply are valid and correct. If an ID you request is incorrect, you will get no result.

## Select fields

You can use `select` to limit the fields that are returned in a work object:

```python
# Import Works query builder
from openalex import Works

# Fetch only specific fields to reduce response size and improve performance
minimal_work = Works().select(["id", "display_name", "cited_by_count"])["W2741809807"]

# Now only the selected fields are populated
print(minimal_work.display_name)  # Works
print(minimal_work.abstract)  # None (not selected)
```

## Authorship information

```python
from openalex import Works

work = Works()["W2741809807"]
print(f"Title: {work.title}")
for authorship in work.authorships:
    author_name = authorship.author.display_name
    institutions = [inst.display_name for inst in authorship.institutions]
    print(f"{author_name} - {', '.join(institutions) if institutions else 'No affiliation'}")
```

## Open Access status

```python
from openalex import Works

work = Works()["W2741809807"]
print(f"Title: {work.title}")
if work.open_access.is_oa:
    print("Open Access: Yes")
    print(f"OA Status: {work.open_access.oa_status}")
    if work.open_access.oa_url:
        print(f"OA URL: {work.open_access.oa_url}")
else:
    print("Open Access: No")
```

## Identifier summary

```python
from openalex import Works

work = Works()["W2741809807"]
print("Identifiers:")
print(f"  OpenAlex: {work.id}")
if work.doi:
    print(f"  DOI: {work.doi}")
if work.ids and work.ids.pmid:
    print(f"  PubMed: {work.ids.pmid}")
if work.ids and work.ids.pmcid:
    print(f"  PMC: {work.ids.pmcid}")
if work.ids and work.ids.mag:
    print(f"  MAG: {work.ids.mag}")
```
