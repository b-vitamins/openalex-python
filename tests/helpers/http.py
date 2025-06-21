"""Utilities for constructing HTTPX requests and responses in tests."""

from __future__ import annotations

from typing import Any
import httpx


class MockTransport(httpx.MockTransport):
    """Convenient mock transport for HTTPX-based clients."""

    def __init__(self) -> None:
        super().__init__(self._handler)
        self.routes: dict[str, httpx.Response] = {}

    def register(self, url: str, response: httpx.Response) -> None:
        """Register a response to return for the given URL."""
        self.routes[url] = response

    def _handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path in self.routes:
            return self.routes[request.url.path]
        message = f"Unmocked URL: {request.url}"
        raise RuntimeError(message)


def make_request(method: str, url: str, **kwargs: Any) -> httpx.Request:
    """Create a simple HTTPX request object for tests."""
    return httpx.Request(method=method, url=url, **kwargs)


def make_response(
    data: Any,
    *,
    status_code: int = 200,
    method: str = "GET",
    url: str = "https://api.openalex.org/test",
) -> httpx.Response:
    """Create a JSON response tied to a matching request."""
    request = make_request(method, url)
    return httpx.Response(status_code=status_code, json=data, request=request)
