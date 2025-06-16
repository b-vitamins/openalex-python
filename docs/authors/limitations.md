# Limitations

## Works with more than 100 authors are truncated

When retrieving a list of works in the API, the `authorships` list within each work will be cut off at 100 authorships objects in order to keep things running well. When this happens the boolean value `is_authors_truncated` will be available and set to `true`. This affects a small portion of OpenAlex, as there are around 35,000 works with more than 100 authors. This limitation does not apply to the data snapshot.

```python
from openalex import Works

# Example: Get works with truncated authors
many_author_works = Works().filter_gt(authors_count=100).get()

# Check if authors are truncated
for work in many_author_works.results:
    if hasattr(work, 'is_authors_truncated') and work.is_authors_truncated:
        print(f"{work.title}")
        print(f"  Showing {len(work.authorships)} of {work.authors_count} authors")
        print(f"  Authors truncated: True")
```

To see the full list of authors, get the individual work record, which is never truncated:

```python
# Include imports for standalone example
from openalex import Works

# Get complete work with all 249 authors
full_work = Works()["W2168909179"]
print(f"Total authors: {len(full_work.authorships)}")  # All 249 available

# Iterate through all authors
for i, authorship in enumerate(full_work.authorships, 1):
    print(f"{i}. {authorship.author.display_name}")
```

This affects filtering as well. If you filter works using an author ID or ROR, you will not receive works where that author appears beyond the first 100 positions. The OpenAlex team plans to change this in the future so that filtering works as expected.

```python
# Include imports
from openalex import Works

# This might miss works where the author is listed after position 100
author_works = Works().filter(
    authorships={"author": {"id": "A5023888391"}}
).get()

# For papers with many authors (like particle physics collaborations),
# authors listed after position 100 won't trigger the filter
```
