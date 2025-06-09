import pytest

from openalex.utils import ensure_prefix, strip_id_prefix, normalize_params, empty_list_result


def test_ensure_prefix() -> None:
    assert ensure_prefix("123", "X") == "X123"
    assert ensure_prefix("X123", "X") == "X123"


def test_strip_id_prefix() -> None:
    assert strip_id_prefix("https://openalex.org/W123") == "W123"
    assert strip_id_prefix("W123") == "W123"


def test_normalize_params_select_list() -> None:
    params = normalize_params({"select": ["id", "name"], "per_page": 5})
    assert params["select"] == "id,name"
    assert params["per-page"] == 5


def test_empty_list_result() -> None:
    result = empty_list_result()
    assert result.meta.count == 0
    assert result.results == []
