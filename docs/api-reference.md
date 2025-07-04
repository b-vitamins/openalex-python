# API Reference

This section demonstrates the main features of the OpenAlex client with complete examples.

## Entity Classes

```python

from openalex import Works

work = Works()["W2741809807"]
print(f"Type: {type(work).__name__}")  # Work
print(f"Attributes: {len(work.model_fields)} fields available")
```

```python
from openalex import Authors

author = Authors()["A5023888391"]
print(f"Author: {author.display_name}")
print(f"H-index: {author.summary_stats.h_index}")
```

```python
from openalex import Institutions

mit = Institutions()["I63966007"]
print(f"Institution: {mit.display_name}")
print(f"Location: {mit.geo.city}, {mit.geo.country}")
```

```python
from openalex import Sources

nature = Sources()["S137773608"]
print(f"Journal: {nature.display_name}")
print(f"Impact: {nature.summary_stats.two_year_mean_citedness:.1f}")
```

```python
from openalex import Publishers

elsevier = Publishers()["P4310320990"]
print(f"Publisher: {elsevier.display_name}")
print(f"Works: {elsevier.works_count:,}")
```

```python
from openalex import Funders

nih = Funders()["F4320332161"]
print(f"Funder: {nih.display_name}")
print(f"Grants: {nih.grants_count:,}")
```

```python
from openalex import Topics

ml = Topics()["T10017"]
print(f"Topic: {ml.display_name}")
print(f"Field: {ml.field.display_name}")
```

```python
from openalex import Concepts

cs = Concepts()["C41008148"]
print(f"Concept: {cs.display_name}")
print(f"Level: {cs.level}")
```

## Query Methods

```python

from openalex import Works

results = Works().filter(publication_year=2023).get(per_page=50, page=2)
print(f"Page 2 of results: {len(results.results)} items")
```

```python
from openalex import Works

total = Works().filter(is_oa=True, publication_year=2023).count()
print(f"Total OA works in 2023: {total:,}")
```

```python
from openalex import Authors

all_ml_authors = []
for author in Authors().search("machine learning").paginate(per_page=200):
    all_ml_authors.append(author)
    if len(all_ml_authors) >= 1000:
        break
print(f"Collected {len(all_ml_authors)} ML researchers")
```

```python
from openalex import Institutions

random_uni = Institutions().filter(type="education").random()
print(f"Random university: {random_uni.display_name}")
```

```python
from openalex import Sources

top_oa_journals = (
    Sources()
    .filter(is_oa=True)
    .filter(type="journal")
    .sort(works_count="desc")
    .get(per_page=10)
)
print(f"Top {len(top_oa_journals.results)} OA journals by volume")
```

## Filter Operators

```python

from openalex import Works

recent = Works().filter(publication_year=2023).count()
print(f"Works from 2023: {recent:,}")
```

```python
from openalex import Works

high_cited = Works().filter(cited_by_count=">100").count()
print(f"Works with >100 citations: {high_cited:,}")
```

```python
from openalex import Works

low_cited = Works().filter(cited_by_count="<5").count()
print(f"Works with <5 citations: {low_cited:,}")
```

```python
from openalex import Authors

mid_career = (
    Authors()
    .filter_gte(works_count=50)
    .filter_lte(works_count=200)
    .count()
)
print(f"Authors with 50-200 works: {mid_career:,}")
```

```python
from openalex import Institutions

non_us = Institutions().filter(country_code="!US").count()
print(f"Non-US institutions: {non_us:,}")
```

```python
from openalex import Sources

cs_journals = Sources().filter(topics={"id": "T10017|T11679"}).count()
print(f"ML or AI journals: {cs_journals:,}")
```

```python
from openalex import Authors

no_orcid = Authors().filter(orcid="null").count()
has_orcid = Authors().filter(orcid="!null").count()
print(f"Authors without ORCID: {no_orcid:,}")
print(f"Authors with ORCID: {has_orcid:,}")
```

## Complex Filtering

```python
from openalex import Works

harvard_ai_papers = (
    Works()
    .filter(
        authorships={
            "institutions": {"id": "I136199984"},  # Harvard
        },
        topics={"id": "T10017"}  # Machine Learning
    )
    .filter(publication_year=2023)
    .get(per_page=5)
)

print(f"Harvard AI papers in 2023: {harvard_ai_papers.meta.count}")
```

```python
from openalex import Authors

prolific_recent = (
    Authors()
    .filter(
        works_count=">100",
        last_known_institutions={
            "country_code": "US",
            "type": "education"
        }
    )
    .search("quantum computing")
    .get(per_page=10)
)

for author in prolific_recent.results:
    print(f"{author.display_name}: {author.works_count} works")
```

