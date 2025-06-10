"""Example usage patterns for entity classes."""

from openalex import Authors, Institutions, Works


def test_pyalex_style_usage():
    """Demonstrate PyAlex-style usage patterns."""
    Works()["W2741809807"]
    Works().filter(publication_year=2020, is_oa=True).get()
    (
        Works()
        .filter_gt(cited_by_count=100)
        .filter_lt(publication_year=2020)
        .search("machine learning")
        .sort(cited_by_count="desc")
        .get()
    )
    Authors().random()
    Institutions().count()
    Authors().autocomplete("einstein")
    Works().filter(publication_year=2024).get()
    Works().filter_gt(cited_by_count=1000).get()
    Works().filter_or(topics={"id": "T10017"}, topics2={"id": "T10018"})
