# Get a single concept

{% hint style="warning" %}
**DEPRECATION WARNING**: These are the original OpenAlex Concepts, which are being deprecated in favor of [Topics](../topics/README.md). OpenAlex will continue to provide these Concepts for Works, but OpenAlex will not be actively maintaining, updating, or providing support for these concepts. Unless you have a good reason to be relying on them, The OpenAlex team encourages you to look into [Topics](../topics/README.md) instead.
{% endhint %}

It's easy to get a concept using the Python client:

```python
from openalex import Concepts

# Get a specific concept by their OpenAlex ID
concept = Concepts()["C71924100"]

# Alternative syntax using the get method
concept = Concepts().get("C71924100")
```

That will return a [`Concept`](concept-object.md) object, describing everything OpenAlex knows about the concept with that ID:

```python
from openalex import Concepts

concept = Concepts()["C71924100"]
# Access concept properties directly as Python attributes
print(concept.id)  # "https://openalex.org/C71924100"
print(concept.wikidata)  # "https://www.wikidata.org/wiki/Q11190" (canonical ID)
print(concept.display_name)  # "Medicine"
print(concept.level)  # 0 (root level)
print(concept.description)  # "field of study for diagnosing, treating and preventing disease"
print(concept.works_count)  # Number of works tagged with this concept
print(concept.cited_by_count)  # Total citations

# Show hierarchical position
print(f"Level in hierarchy: {concept.level}")  # 0-5, where 0 is root
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
from openalex import Concepts
# Fetch multiple specific concepts in one API call
concept_ids = ["C71924100", "C41008148", "C86803240"]
multiple_concepts = Concepts().filter(openalex=concept_ids).get()

print(f"Found {len(multiple_concepts.results)} concepts")
for c in multiple_concepts.results:
    print(f"- {c.display_name} (Level {c.level})")
    print(f"  Works: {c.works_count:,}")
```

## External IDs

You can look up concepts using external IDs such as a Wikidata ID:

```python
from openalex import Concepts
# Get concept by Wikidata ID (canonical external ID)
medicine = Concepts()["wikidata:Q11190"]
medicine = Concepts()["wikidata:https://www.wikidata.org/wiki/Q11190"]  # Full URL

# Get concept by MAG ID
concept = Concepts()["mag:71924100"]
```

Available external IDs for concepts are:

| External ID | URN | Example |
|------------|-----|---------|
| Microsoft Academic Graph (MAG) | `mag` | `mag:71924100` |
| Wikidata | `wikidata` | `wikidata:Q11190` |

## Select fields

You can use `select` to limit the fields that are returned in a concept object:

```python
from openalex import Concepts
# Fetch only specific fields to reduce response size
minimal_concept = Concepts().select([
    "id",
    "display_name",
    "level",
    "works_count"
])["C71924100"]

# Now only the selected fields are populated
print(minimal_concept.display_name)  # Works
print(minimal_concept.description)  # None (not selected)
```

**Remember: For new projects, use [Topics](../topics/README.md) instead of Concepts!**
