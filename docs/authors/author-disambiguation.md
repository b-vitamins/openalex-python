# Author disambiguation

The OpenAlex team provides a help page explaining their author disambiguation system, including how author IDs are assigned and how you can curate a profile.

Go to [this page](https://help.openalex.org/hc/en-us/articles/24347048891543-Author-disambiguation) to find out what you need to know!

## Quick example with the Python client

```python
from openalex import Authors

# Authors may have variations in their name
# OpenAlex's disambiguation system links these together
author = Authors().search("John R Smith").get().results[0]

# Check name variations returned
print(f"Primary name: {author.display_name}")
print(f"Also known as: {author.display_name_alternatives}")

# The OpenAlex ID uniquely identifies this author
# across all name variations
print(f"Unique ID: {author.id}")
```
