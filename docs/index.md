# OpenAlex Python Client Documentation

Welcome to the official client for the [OpenAlex](https://openalex.org) scholarly metadata API. The library offers a fluent interface with type hints and async support.

## Quick Start

```python
from openalex import Works

work = Works()["W2741809807"]
print(f"Title: {work.title}")
print(f"Year: {work.publication_year}")
print(f"Citations: {work.cited_by_count}")
print(f"Open Access: {'Yes' if work.open_access.is_oa else 'No'}")
```

## Feature Tour

```python
from openalex import Works, Authors

climate_papers = Works().search("climate change").filter(publication_year=2023).get(per_page=3)
print(f"Found {climate_papers.meta.count} papers on climate change in 2023")
```

```python
from openalex import Authors

climate_researchers = Authors().search("climate change").get(per_page=3)
for author in climate_researchers.results:
    print(f"{author.display_name}: {author.works_count} works")
```

```python
from openalex import Institutions

top_unis = Institutions().filter(type="education").sort(cited_by_count="desc").get(per_page=5)
print("Top universities by citations:")
for uni in top_unis.results:
    print(f"  {uni.display_name}: {uni.cited_by_count:,} citations")
```

```python
from openalex import Topics

ml_topic = Topics()["T10017"]
print(f"Topic: {ml_topic.display_name}")
print(f"Works: {ml_topic.works_count:,}")
print(f"Growing field with {ml_topic.cited_by_count:,} total citations")
```

