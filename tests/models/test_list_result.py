from __future__ import annotations

from typing import Any

from openalex.models import ListResult, Meta, Work


class TestListResult:
    """Test ListResult model."""

    def test_list_result_creation(self, mock_list_response: dict[str, Any]) -> None:
        result = ListResult[Work](
            meta=Meta(**mock_list_response["meta"]),
            results=[Work(**r) for r in mock_list_response["results"]],
        )

        assert result.meta.count == 100
        assert result.meta.page == 1
        assert len(result.results) == 1
        assert (
            result.results[0].title
            == "Generalized Gradient Approximation Made Simple"
        )
