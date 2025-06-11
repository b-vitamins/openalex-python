"""Custom exceptions for the OpenAlex client."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Final

from .constants import (
    HTTP_NOT_FOUND,
    HTTP_UNAUTHORIZED,
)

__all__ = [
    "APIError",
    "AuthenticationError",
    "NetworkError",
    "NotFoundError",
    "OpenAlexError",
    "RateLimitError",
    "RetryableError",
    "ServerError",
    "RateLimitExceeded",
    "TemporaryError",
    "ConfigurationError",
    "TimeoutError",
    "ValidationError",
    "raise_for_status",
]

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


class RetryableError(OpenAlexError):
    """Base class for errors that can be retried."""
    pass


class ServerError(RetryableError):
    """Server-side errors (5xx status codes)."""
    pass


class RateLimitExceeded(RetryableError):
    """Rate limit exceeded error with retry information."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class TemporaryError(RetryableError):
    """Temporary errors that may succeed on retry."""
    pass


class ConfigurationError(OpenAlexError):
    """Configuration-related errors."""
    pass


def raise_for_status(response: httpx.Response) -> None:
    """Raise an exception for HTTP error responses with detailed messages."""
    if response.is_success:
        return

    status_code = response.status_code

    # Try to extract error message from response
    try:
        error_data = response.json()
        error_message = error_data.get("message", "No error message provided")
        error_details = error_data.get("error", "")
    except Exception:
        error_message = response.text or "No error message provided"
        error_details = ""

    # Construct detailed error message
    base_message = f"HTTP {status_code}: {error_message}"
    if error_details:
        base_message += f" - {error_details}"

    # Add helpful context based on status code
    if status_code == 400:
        raise ValidationError(
            f"{base_message}\n"
            "This usually means there's an issue with your query parameters. "
            "Check the filter syntax and parameter names."
        )
    elif status_code == 401:
        raise AuthenticationError(
            f"{base_message}\n"
            "Your API key may be invalid or expired. "
            "Get a new key at https://openalex.org/api-key"
        )
    elif status_code == 403:
        raise AuthenticationError(
            f"{base_message}\n"
            "You don't have permission to access this resource."
        )
    elif status_code == 404:
        raise NotFoundError(
            f"{base_message}\n"
            "The requested resource does not exist. "
            "Check the entity ID or endpoint."
        )
    elif status_code == 429:
        retry_after = response.headers.get("Retry-After", "unknown")
        raise RateLimitExceeded(
            f"{base_message}\n"
            f"Rate limit exceeded. Retry after {retry_after} seconds. "
            "Consider adding an API key for higher limits.",
            retry_after=int(retry_after) if retry_after.isdigit() else None,
        )
    elif 500 <= status_code < 600:
        raise ServerError(
            f"{base_message}\n"
            "This is a server-side error. The request may succeed if retried."
        )
    else:
        raise APIError(base_message)
