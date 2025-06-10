from openalex.models import ListResult
from openalex.query import Query, gt_, lt_, not_, or_


class MockResource:
    """Mock resource for testing."""

    def __init__(self):
        self.calls = []

    def get(self, id):
        self.calls.append(("get", id))
        return {"id": id, "type": "mock"}

    def list(self, filter=None, **params):
        self.calls.append(("list", filter, params))
        meta = {
            "count": 42,
            "db_response_time_ms": 1,
            "page": 1,
            "per_page": params.get("per_page", 25),
        }
        return ListResult(meta=meta, results=[])

    def random(self, **params):
        self.calls.append(("random", params))
        return {"id": "random", "type": "mock"}

    def autocomplete(self, query, **params):
        self.calls.append(("autocomplete", query, params))
        meta = {"count": 5, "db_response_time_ms": 1, "page": 1, "per_page": 25}
        return ListResult(meta=meta, results=[])


def test_getitem_single():
    resource = MockResource()
    query = Query(resource)

    result = query["W123456"]
    assert result["id"] == "W123456"
    assert resource.calls[-1] == ("get", "W123456")


def test_getitem_multiple():
    resource = MockResource()
    query = Query(resource)

    query[["W123", "W456"]]
    assert resource.calls[-1][0] == "list"
    assert resource.calls[-1][1]["openalex_id"] == ["W123", "W456"]


def test_filter_or():
    resource = MockResource()
    query = Query(resource).filter_or(type="article", is_oa=True)

    assert isinstance(query.params["filter"], or_)
    assert query.params["filter"]["type"] == "article"
    assert query.params["filter"]["is_oa"] is True


def test_filter_not():
    resource = MockResource()
    query = Query(resource).filter_not(type="dataset")

    filter_value = query.params["filter"]["type"]
    assert isinstance(filter_value, not_)
    assert filter_value.value == "dataset"


def test_filter_gt_lt():
    resource = MockResource()
    query = (
        Query(resource)
        .filter_gt(cited_by_count=100)
        .filter_lt(publication_year=2020)
    )

    assert isinstance(query.params["filter"]["cited_by_count"], gt_)
    assert query.params["filter"]["cited_by_count"].value == 100
    assert isinstance(query.params["filter"]["publication_year"], lt_)
    assert query.params["filter"]["publication_year"].value == 2020


def test_search_filter():
    resource = MockResource()
    query = Query(resource).search_filter(title="quantum", abstract="physics")

    assert query.params["filter"]["title.search"] == "quantum"
    assert query.params["filter"]["abstract.search"] == "physics"


def test_count():
    resource = MockResource()
    query = Query(resource).filter(type="article")

    count = query.count()
    assert count == 42
    assert resource.calls[-1][0] == "list"
    assert resource.calls[-1][2]["per_page"] == 1


def test_random():
    resource = MockResource()
    query = Query(resource)

    result = query.random()
    assert result["id"] == "random"
    assert resource.calls[-1][0] == "random"


def test_autocomplete():
    resource = MockResource()
    query = Query(resource)

    result = query.autocomplete("einstein")
    assert result.meta.count == 5
    assert resource.calls[-1] == ("autocomplete", "einstein", {})
