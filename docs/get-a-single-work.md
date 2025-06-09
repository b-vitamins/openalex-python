# Get a single work

Use the client to fetch a `Work` by its OpenAlex identifier.

```python
from openalex import OpenAlex

client = OpenAlex()
work = client.works.get("W2741809807")
print(work.display_name)
```

To look up several works in one request, pass their IDs as a filter:

```python
ids = ["W2741809807", "W2100837269"]
works = client.works.list(filter={"id": ids})
```

## External IDs

Works can also be retrieved by other identifiers such as DOIs or PubMed IDs.

```python
work = client.works.by_doi("10.7717/peerj.4375")
work = client.works.get("pmid:14907713")
```

Supported prefixes:

| External ID | Prefix |
|-------------|-------|
| DOI | `doi:` |
| Microsoft Academic Graph (MAG) | `mag:` |
| PubMed ID (PMID) | `pmid:` |
| PubMed Central ID (PMCID) | `pmcid:` |

Make sure the identifier is valid. Invalid or malformed IDs will either return no result or raise an error.

### Select fields

Return only the fields you need using `select`:

```python
work = client.works.get("W2741809807", select=["id", "display_name"])
```
