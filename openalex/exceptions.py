"""Custom exceptions for the OpenAlex client."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


class OpenAlexError(Exception):
    """Base exception for OpenAlex client errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message)
        self.message = message
        self.extra = kwargs


class APIError(OpenAlexError):
    """Error from the OpenAlex API."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response = response


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=401, **kwargs)


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        resource_id: str | None = None,
        resource_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=404, **kwargs)
        self.resource_id = resource_id
        self.resource_type = resource_type


class ValidationError(OpenAlexError):
    """Validation error for input data."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value


class NetworkError(OpenAlexError):
    """Network-related error."""

    def __init__(
        self,
        message: str = "Network error occurred",
        *,
        original_error: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.original_error = original_error


class TimeoutError(NetworkError):
    """Request timeout error."""

    def __init__(
        self,
        message: str = "Request timed out",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


def raise_for_status(response: httpx.Response) -> None:
    """Raise appropriate exception for HTTP error status codes."""
    if response.is_success:
        return

    try:
        error_data = response.json()
        message = error_data.get("message", response.reason_phrase)
    except (ValueError, json.JSONDecodeError):
        message = response.reason_phrase or f"HTTP {response.status_code}"

    if response.status_code == 401:
        raise AuthenticationError(message, response=response)
    if response.status_code == 404:
        raise NotFoundError(message, response=response)
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        raise RateLimitError(
            message,
            retry_after=int(retry_after) if retry_after else None,
            response=response,
        )
    if response.status_code >= 500:
        msg = f"Server error: {message}"
        raise APIError(
            msg,
            status_code=response.status_code,
            response=response,
        )
    raise APIError(
        message,
        status_code=response.status_code,
        response=response,
    )
