# Get a single topic

Retrieve a topic record by its OpenAlex ID.

```python
from openalex import Topics

topics = Topics()
topic = topics.get("T11636")
print(topic.display_name)
```

Use `.select` or the `select` parameter to request only certain fields:

```python
# inline select
brief = topics.get("T11636", select=["id", "display_name"])

# chain after fetching
brief = topics.get("T11636").select(["id", "display_name"])
```
