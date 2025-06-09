# Get a single publisher

Fetch a publisher record by its OpenAlex ID.

```python
from openalex import OpenAlex

client = OpenAlex()
publisher = client.publishers.get("P4310319965")
print(publisher.display_name)
```

You can request multiple IDs at once with `filter`:

```python
ids = ["P4310319965", "P4310320990"]
publishers = client.publishers.list(filter={"id": ids})
```

## External IDs

Publishers can also be looked up by external identifiers such as Wikidata or ROR.

```python
publisher = client.publishers.get("wikidata:Q1479654")
```

## Select fields

Return only chosen fields from the record:

```python
minimal = client.publishers.get("P4310319965", select=["id", "display_name"])
```
