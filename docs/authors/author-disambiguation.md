# Author disambiguation

We have created a page in our help docs to give you all the information you need about our author disambiguation including information about author IDs, how we disambiguate authors, and how you can curate your author profile. 

Go to [this page](https://help.openalex.org/hc/en-us/articles/24347048891543-Author-disambiguation) to find out what you need to know!

## Quick example with the Python client

```python
from openalex import Authors

# Authors may have variations in their name
# Our disambiguation system links these together
author = Authors().search("John R Smith").get().results[0]

# Check name variations we've found
print(f"Primary name: {author.display_name}")
print(f"Also known as: {author.display_name_alternatives}")

# The OpenAlex ID uniquely identifies this author
# across all name variations
print(f"Unique ID: {author.id}")
```
