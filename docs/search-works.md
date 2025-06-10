# Search works

Use `works.search()` to query titles, abstracts, and full text.

```python
from openalex import Works

works = Works()
results = works.search("dna")
print(results.results[0].display_name)
```

Full text search only applies to works where `has_fulltext` is true.

See the [OpenAlex documentation](https://docs.openalex.org/api-entities/works/search-works) for details on how search ranking works and more advanced options.

## Search a specific field

Append `.search` to a filter key to limit searching to that field:

```python
works = works.list(filter={"title.search": "cubist"})
```

Fields that accept `.search` include `abstract`, `display_name` (alias `title`), `fulltext`, `raw_affiliation_strings`, and `title_and_abstract`. You can also use `default.search`, which behaves the same as the `search` parameter.

| Search filter | Field that is searched |
| --- | --- |
| `abstract.search` | `abstract_inverted_index` |
| `display_name.search` | `display_name` |
| `fulltext.search` | fulltext via n-grams |
| `raw_affiliation_strings.search` | `authorships.raw_affiliation_strings` |
| `title.search` | `display_name` |
| `title_and_abstract.search` | `display_name` and `abstract_inverted_index` |

These searches apply stemming and stop-word removal. See the API docs if you need to disable this behaviour.

### Searching by related entity names

To search works by a related entity like an author or institution, first lookup that entity and then filter works by its ID:

```python
from openalex import Institutions

nyu = Institutions().search("nyu").results[0]
works = works.list(filter={"institutions.id": nyu.id})
```

## Autocomplete works

`works.autocomplete()` provides typeahead suggestions:

```python
suggestions = works.autocomplete("tigers")
```

Each suggestion includes the title and a hint containing the authors.
