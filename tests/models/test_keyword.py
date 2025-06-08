from openalex.models import Keyword


def test_keyword_metrics() -> None:
    kw = Keyword(
        id="K1", display_name="AI", works_count=100, cited_by_count=250
    )
    assert kw.average_citations_per_work == 2.5
    assert kw.is_popular(threshold=50)
