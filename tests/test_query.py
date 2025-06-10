from openalex.models import ListResult, Meta
from openalex.query import Query, gt_, lt_, not_, or_


class DummyResource:
    def __init__(self) -> None:
        self.calls = []

    def list(self, *, filter=None, **params):
        self.calls.append(("list", filter, params))
        meta = Meta(
            count=1,
            db_response_time_ms=1,
            page=1,
            per_page=params.get("per_page", 25),
        )
        return ListResult(meta=meta, results=[])

    def paginate(self, *, filter=None, per_page=25, max_results=None, **params):
        self.calls.append(("paginate", filter, per_page, max_results, params))
        return f"paginator-{per_page}-{max_results}-{len(params)}"


class MockResource:
    """Mock resource for advanced Query features."""

    def __init__(self) -> None:
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
        meta = {
            "count": 5,
            "db_response_time_ms": 1,
            "page": 1,
            "per_page": 25,
        }
        return ListResult(meta=meta, results=[])


def test_query_builder_and_execution() -> None:
    resource = DummyResource()

    q_filtered = Query(resource).filter(is_oa=True).filter(type="article")
    assert q_filtered.params["filter"] == {"is_oa": True, "type": "article"}
    q_string = Query(resource, {"filter": "raw"}).filter(tag="x")
    assert q_string.params["filter"] == {"tag": "x"}

    q_exec = (
        Query(resource)
        .search("quantum")
        .sort(cited_by_count="desc")
        .group_by("type")
        .select(["id"])
        .sample(5, seed=42)
    )
    assert q_exec.params == {
        "search": "quantum",
        "sort": "cited_by_count:desc",
        "group-by": "type",
        "select": ["id"],
        "sample": 5,
        "seed": 42,
    }

    result = q_exec.list(page=2)
    assert resource.calls[-1][0] == "list"
    assert resource.calls[-1][1] is None
    assert resource.calls[-1][2]["page"] == 2
    assert result.meta.count == 1

    pag = q_exec.paginate(per_page=2, max_results=10, extra="x")
    assert pag == "paginator-2-10-7"
    assert resource.calls[-1][0] == "paginate"
    assert resource.calls[-1][1] is None

    count = q_exec.count()
    assert count == 1
    assert resource.calls[-1][0] == "list"


def test_getitem_single() -> None:
    resource = MockResource()
    query = Query(resource)

    result = query["W123456"]
    assert result["id"] == "W123456"
    assert resource.calls[-1] == ("get", "W123456")


def test_getitem_multiple() -> None:
    resource = MockResource()
    query = Query(resource)

    query[["W123", "W456"]]
    assert resource.calls[-1][0] == "list"
    assert resource.calls[-1][1]["openalex_id"] == ["W123", "W456"]


def test_filter_or() -> None:
    resource = MockResource()
    query = Query(resource).filter_or(type="article", is_oa=True)

    assert isinstance(query.params["filter"], or_)
    assert query.params["filter"]["type"] == "article"
    assert query.params["filter"]["is_oa"] is True


def test_filter_not() -> None:
    resource = MockResource()
    query = Query(resource).filter_not(type="dataset")

    filter_value = query.params["filter"]["type"]
    assert isinstance(filter_value, not_)
    assert filter_value.value == "dataset"


def test_filter_gt_lt() -> None:
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


def test_search_filter() -> None:
    resource = MockResource()
    query = Query(resource).search_filter(title="quantum", abstract="physics")

    assert query.params["filter"]["title.search"] == "quantum"
    assert query.params["filter"]["abstract.search"] == "physics"


def test_count() -> None:
    resource = MockResource()
    query = Query(resource).filter(type="article")

    count = query.count()
    assert count == 42
    assert resource.calls[-1][0] == "list"
    assert resource.calls[-1][2]["per_page"] == 1


def test_random() -> None:
    resource = MockResource()
    query = Query(resource)

    result = query.random()
    assert result["id"] == "random"
    assert resource.calls[-1][0] == "random"


def test_autocomplete() -> None:
    resource = MockResource()
    query = Query(resource)

    result = query.autocomplete("einstein")
    assert result.meta.count == 5
    assert resource.calls[-1] == ("autocomplete", "einstein", {})


def test_query_repr() -> None:
    query = Query(MockResource()).filter(is_oa=True).search("test")
    repr_str = repr(query)
    assert "<Query(MockResource" in repr_str
    assert "filter=" in repr_str
    assert "search='test'" in repr_str
