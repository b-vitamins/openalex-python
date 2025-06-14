# Get a single topic

It's easy to get a topic using the Python client:

```python
from openalex import Topics

# Get a specific topic by the OpenAlex ID
topic = Topics()["T11636"]  # Artificial Intelligence in Medicine
print(topic.display_name)

# Alternative syntax using the get method
topic = Topics().get("T11636")
print(topic.display_name)
```

That will return a [`Topic`](topic-object.md) object, describing everything OpenAlex knows about the topic with that ID:

```python
from openalex import Topics

# Fetch the topic again to keep this block self-contained
topic = Topics()["T11636"]

# Access topic properties directly as Python attributes
print(topic.id)  # "https://openalex.org/T11636"
print(topic.display_name)  # "Artificial Intelligence in Medicine"
print(topic.description)  # AI-generated description
print(f"Works: {topic.works_count:,}")

# Hierarchical classification
print(f"Domain: {topic.domain.display_name}")  # "Health Sciences"
print(f"Field: {topic.field.display_name}")  # "Medicine"
print(f"Subfield: {topic.subfield.display_name}")  # "Health Informatics"

# Keywords
print(f"Keywords: {', '.join(topic.keywords[:5])}")  # First 5 keywords

# Sibling topics in the same subfield
if topic.siblings:
    print("Sibling topics:")
    for sibling in topic.siblings[:5]:
        print(f"- {sibling.display_name}")
```

You can make up to 50 of these queries at once by requesting a list of entities and filtering on IDs:

```python
from openalex import Topics

# Fetch multiple specific topics in one API call
topic_ids = ["T11636", "T10017", "T10159"]
multiple_topics = Topics().filter(openalex=topic_ids).get()

print(f"Found {len(multiple_topics.results)} topics")
for t in multiple_topics.results:
    print(f"- {t.display_name}")
    print(f"  {t.domain.display_name} -> {t.field.display_name} -> {t.subfield.display_name}")
    print(f"  Works: {t.works_count:,}")
```

## Select fields

You can use `select` to limit the fields that are returned in a topic object:

```python
from openalex import Topics

# Fetch only specific fields to reduce response size
minimal_topic = Topics().select([
    "id",
    "display_name",
    "works_count"
]).get("T11636")

# Now only the selected fields are populated
print(minimal_topic.display_name)  # Works
print(minimal_topic.description)  # None (not selected)
```
