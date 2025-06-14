# Get a single author

It's easy to get an author using the Python client:

```python
from openalex import Authors

# Get a specific author by their OpenAlex ID
author = Authors()["A5023888391"]

# Alternative syntax using the get method
author = Authors().get("A5023888391")
```

That will return an [`Author`](author-object.md) object, describing everything OpenAlex knows about the author with that ID:

```python
from openalex import Authors

# Fetch the author again to keep the example self-contained
author = Authors()["A5023888391"]

# Access author properties directly as Python attributes
print(author.id)  # "https://openalex.org/A5023888391"
print(author.orcid)  # "https://orcid.org/0000-0001-6187-6610"
print(author.display_name)  # "Jason Priem"
print(author.works_count)  # 53
print(author.cited_by_count)  # Total citations across all works
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
from openalex import Authors

# Fetch multiple specific authors in one API call
author_ids = ["A5023888391", "A5014077037", "A5032731615"]
multiple_authors = Authors().filter(openalex=author_ids).get()

# This returns a page with up to 50 authors (if all IDs are valid)
print(f"Found {len(multiple_authors.results)} authors")
for author in multiple_authors.results:
    print(f"- {author.display_name} ({author.works_count} works)")
```

Authors are also available via an alias: `People()` works the same as `Authors()`

## External IDs

You can look up authors using external IDs such as an ORCID:

```python
from openalex import Authors

# Get author by ORCID (multiple formats supported)
author = Authors()["https://orcid.org/0000-0002-1298-3089"]
author = Authors()["orcid:0000-0002-1298-3089"]  # Shorter URN format

# Get author by Scopus ID
author = Authors()["scopus:7004185353"]

# Get author by Twitter handle
author = Authors()["twitter:jasonpriem"]

# Get author by Wikipedia page
author = Authors()["wikipedia:https://en.wikipedia.org/wiki/Heather_Piwowar"]
```

Available external IDs for authors are:

| External ID | URN | Example |
|------------|-----|---------|
| ORCID | `orcid` | `orcid:0000-0001-6187-6610` |
| Scopus | `scopus` | `scopus:7004185353` |
| Twitter | `twitter` | `twitter:jasonpriem` |
| Wikipedia | `wikipedia` | `wikipedia:en.wikipedia.org/wiki/Person_Name` |

## Select fields

You can use `select` to limit the fields that are returned in an author object:

```python
from openalex import Authors

# Fetch only specific fields to reduce response size
minimal_author = Authors().select(["id", "display_name", "orcid"]).get("A5023888391")

# Now only the selected fields are populated
print(minimal_author.display_name)  # Works
print(minimal_author.works_count)  # None (not selected)
```
