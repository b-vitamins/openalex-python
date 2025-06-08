import httpx
import pytest

from openalex.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    raise_for_status,
)


@pytest.mark.parametrize(
    ("status", "exc"),
    [
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, APIError),
        (400, APIError),
    ],
)
def test_raise_for_status(status: int, exc: type[Exception]) -> None:
    request = httpx.Request("GET", "https://api.openalex.org/test")
    response = httpx.Response(status, json={"message": "err"}, request=request)
    with pytest.raises(exc):
        raise_for_status(response)

