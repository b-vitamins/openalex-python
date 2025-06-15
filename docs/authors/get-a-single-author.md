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
# Re-fetch the author so this block is independent
from openalex import Authors

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
# Include imports for standalone execution
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

author = Authors()["A5086198262"]
name = author.display_name
print(name) # Yoshua Bengio

author = Authors()["https://orcid.org/0000-0002-9322-3515"] # ORCID
assert name == author.display_name

author = Authors()["orcid:0000-0002-9322-3515"] # Shorter URN format
assert name == author.display_name
```

Available external IDs for authors are:

| External ID | URN         | Example                                       |
|-------------|-------------|-----------------------------------------------|
| ORCID       | `orcid`     | `orcid:0000-0001-6187-6610`                   |
| Scopus      | `scopus`    | `scopus:7004185353`                           |
| Twitter     | `twitter`   | `twitter:jasonpriem`                          |
| Wikipedia   | `wikipedia` | `wikipedia:en.wikipedia.org/wiki/Person_Name` |

## Select fields

You can use `select` to limit the fields that are returned in an author object:

```python
# Import again so the block is self‑contained
from openalex import Authors

# Fetch only specific fields to reduce response size
minimal_author = Authors().get(
    "A5023888391", select=["id", "display_name", "orcid"]
)

# Now only the selected fields are populated
print(minimal_author.display_name)  # Works
print(minimal_author.works_count)  # None (not selected)
```
