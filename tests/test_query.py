from openalex.models import ListResult, Meta
from openalex.query import Query


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
