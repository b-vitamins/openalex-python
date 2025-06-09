# Get a single concept

> **Warning**
> Concepts are the older taxonomy in OpenAlex and have been mostly replaced by Topics. They remain available but are no longer actively maintained.

```python
from openalex import OpenAlex

client = OpenAlex()
concept = client.concepts.get("C71924100")
print(concept.display_name)
```

Request a subset of fields using `select` or by chaining `.select()`:

```python
brief = client.concepts.get("C71924100", select=["id", "display_name"])
brief = client.concepts.get("C71924100").select(["id", "display_name"])
```

You can also lookup by external identifiers such as Wikidata:

```python
concept = client.concepts.get("wikidata:Q11190")
```
