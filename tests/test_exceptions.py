import httpx
import pytest

from openalex.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitExceededError,
    ServerError,
    TimeoutError,
    ValidationError,
    raise_for_status,
)


@pytest.mark.parametrize(
    ("status", "exc"),
    [
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitExceededError),
        (500, ServerError),
        (400, ValidationError),
    ],
)
def test_raise_for_status(status: int, exc: type[Exception]) -> None:
    request = httpx.Request("GET", "https://api.openalex.org/test")
    response = httpx.Response(status, json={"message": "err"}, request=request)
    with pytest.raises(exc):
        raise_for_status(response)


def test_validation_and_network_errors() -> None:
    err = ValidationError("bad", field="field", value=123)
    assert err.field == "field"
    assert err.value == 123

    net = NetworkError(original_error=ValueError("x"))
    assert isinstance(net.original_error, ValueError)

    timeout = TimeoutError()
    assert isinstance(timeout, NetworkError)


def test_raise_for_status_non_json() -> None:
    request = httpx.Request("GET", "https://api.openalex.org/test")
    response = httpx.Response(502, text="<!doctype html>", request=request)
    with pytest.raises(ServerError) as exc_info:
        raise_for_status(response)
    assert "Server-side error" in str(exc_info.value) or "server-side" in str(
        exc_info.value
    )
