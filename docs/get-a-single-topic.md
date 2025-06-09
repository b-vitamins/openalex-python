# Get a single topic

Retrieve a topic record by its OpenAlex ID.

```python
from openalex import OpenAlex

client = OpenAlex()
topic = client.topics.get("T11636")
print(topic.display_name)
```

Use `.select` or the `select` parameter to request only certain fields:

```python
# inline select
brief = client.topics.get("T11636", select=["id", "display_name"])

# chain after fetching
brief = client.topics.get("T11636").select(["id", "display_name"])
```
