# Get a single publisher

It's easy to get a publisher using the Python client:

```python
from openalex import Publishers

# Get a specific publisher by their OpenAlex ID
publisher = Publishers()["P4310319965"]

# Alternative syntax using the get method
publisher = Publishers().get("P4310319965")
```

That will return a [`Publisher`](publisher-object.md) object, describing everything OpenAlex knows about the publisher with that ID:

```python
from openalex import Publishers

publisher = Publishers()["P4310319965"]  # Springer Nature

# Access publisher properties directly as Python attributes
print(publisher.id)
print(publisher.display_name)
print(publisher.alternate_titles)
print(publisher.hierarchy_level)
print(f"Works: {publisher.works_count:,}")
print(f"Citations: {publisher.cited_by_count:,}")
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python

from openalex import Publishers

# Fetch multiple specific publishers in one API call
publisher_ids = ["P4310319965", "P4310320990", "P4310319900"]
multiple_publishers = Publishers().filter(openalex=publisher_ids).get()

print(f"Found {len(multiple_publishers.results)} publishers")
for pub in multiple_publishers.results:
    print(f"- {pub.display_name} ({pub.works_count:,} works)")
```

## External IDs

You can look up publishers using external IDs such as a Wikidata ID:

```python
# Get publisher by Wikidata ID
from openalex import Publishers

publisher = Publishers()["wikidata:Q1479654"]

# Get publisher by ROR ID
publisher = Publishers()["ror:https://ror.org/02scfj030"]

# Direct lookup by full URL also works
publisher = Publishers()["https://www.wikidata.org/entity/Q746413"]
```

Available external IDs for publishers are:

| External ID | URN | Example |
|------------|-----|---------|
| ROR | `ror` | `ror:02scfj030` |
| Wikidata | `wikidata` | `wikidata:Q746413` |

## Select fields

You can use `select` to limit the fields that are returned in a publisher object:

```python
# Fetch only specific fields to reduce response size
from openalex import Publishers

minimal_publisher = Publishers().select(["id", "display_name", "works_count"]).get("P4310319965")

# Now only the selected fields are populated
print(minimal_publisher.display_name)  # Works
print(minimal_publisher.cited_by_count)  # None (not selected)
```

## Publisher hierarchy and alternate titles

```python
from openalex import Publishers

publisher = Publishers()["P4310320990"]  # Elsevier BV
print(f"Primary name: {publisher.display_name}")

if publisher.parent_publisher:
    parent = Publishers()[publisher.parent_publisher]
    print(f"Parent: {parent.display_name}")

if publisher.alternate_titles:
    print("Also known as:")
    for alt in publisher.alternate_titles[:5]:
        print(f"  - {alt}")
```
