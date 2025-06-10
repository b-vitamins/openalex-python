# Get a single institution

Fetch an institution record by its OpenAlex ID.

```python
from openalex import Institutions

institutions = Institutions()
inst = institutions.get("I27837315")
print(inst.display_name)
```

You can pass multiple IDs to `list` when you need several records at once:

```python
ids = ["I27837315", "I201448701"]
insts = institutions.list(filter={"id": ids})
```

## External IDs

Institutions can be looked up via ROR, MAG, or Wikidata identifiers:

```python
inst = institutions.get("ror:https://ror.org/00cvxb145")
```

Supported prefixes:

| External ID | Prefix |
|-------------|--------|
| ROR | `ror` |
| MAG | `mag` |
| Wikidata | `wikidata` |

## Select fields

Limit the returned data using `select` or by chaining `.select` on the result:

```python
inst = institutions.get("I27837315", select=["id", "display_name"])

inst = institutions.get("I27837315").select(["id", "display_name"])
```
