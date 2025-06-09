# Get a single funder

Fetch a funder record by its OpenAlex identifier.

```python
from openalex import OpenAlex

client = OpenAlex()
funder = client.funders.get("F4320332161")
print(funder.display_name)
```

Multiple IDs can be requested in one call:

```python
ids = ["F4320332161", "F4320321001"]
funders = client.funders.list(filter={"id": ids})
```

## External IDs

Funders can also be looked up by identifiers such as ROR or Wikidata.

```python
funder = client.funders.by_ror("021nxhr62")
funder = client.funders.get("wikidata:Q390551")
```

### Select fields

Only request the fields you need using `select` or by chaining `.select`:

```python
funder = client.funders.get("F4320332161", select=["id", "display_name"])

funder = client.funders.get("F4320332161").select(["id", "display_name"])
```
