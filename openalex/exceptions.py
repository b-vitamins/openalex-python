"""Custom exceptions for the OpenAlex client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = [
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "NetworkError",
    "NotFoundError",
    "OpenAlexError",
    "RateLimitError",
    "RateLimitExceededError",
    "RetryableError",
    "ServerError",
    "TemporaryError",
    "TimeoutError",
    "ValidationError",
    "raise_for_status",
]

if TYPE_CHECKING:
    import httpx


class OpenAlexError(Exception):
    """Base exception for OpenAlex client errors."""

    __slots__ = ("extra", "message")

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message)
        self.message = message
        self.extra = kwargs


class APIError(OpenAlexError):
    """Error returned from the OpenAlex API."""

    __slots__ = ("details", "response", "status_code")

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
        self.details = kwargs.get("details")


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    __slots__ = ("retry_after",)

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

    __slots__ = ()

    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=401, **kwargs)


class NotFoundError(APIError):
    """Resource not found error."""

    __slots__ = ("resource_id", "resource_type")

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

    __slots__ = ("field", "value")

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

    __slots__ = ("original_error",)

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

    __slots__ = ()

    def __init__(
        self,
        message: str = "Request timed out",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class RetryableError(OpenAlexError):
    """Base class for errors that can be retried."""

    __slots__ = ()


class ServerError(APIError, RetryableError):
    """Server-side errors (5xx status codes)."""

    __slots__ = ()


class RateLimitExceededError(RetryableError):
    """Rate limit exceeded error with retry information."""

    __slots__ = ("retry_after",)

    def __init__(self, retry_after: int | None = None) -> None:
        message = (
            f"Rate limit exceeded. Retry after {retry_after} seconds"
            if retry_after is not None
            else "Rate limit exceeded"
        )
        super().__init__(message)
        self.retry_after = retry_after


class TemporaryError(APIError, RetryableError):
    """Temporary errors that may succeed on retry."""

    __slots__ = ("retry_after",)

    def __init__(self, message: str, *, status_code: int | None = None, retry_after: int | None = None) -> None:
        super().__init__(message, status_code=status_code)
        self.retry_after = retry_after


class ConfigurationError(OpenAlexError):
    """Configuration-related errors."""

    __slots__ = ()


def raise_for_status(response: httpx.Response) -> None:
    """Raise an exception for HTTP error responses with detailed messages."""
    status_code = response.status_code
    if 200 <= status_code < 300:
        return

    # Try to extract error message from response
    try:
        error_data = response.json()
        error_message = error_data.get("message", "No error message provided")
        error_details = error_data.get("error", "")
        error_extra = error_data.get("details")
    except Exception:
        error_message = response.text or "No error message provided"
        error_details = ""
        error_extra = None

    # Construct detailed error message
    base_message = f"HTTP {status_code}: {error_message}"
    if error_details:
        base_message += f" - {error_details}"

    # Add helpful context based on status code
    if status_code == 400:
        msg = (
            f"{base_message}\n"
            "This usually means there's an issue with your query parameters. "
            "Check the filter syntax and parameter names."
        )
        if "filter" in error_message.lower() or "filter" in error_details.lower():
            raise ValidationError(msg)
        raise APIError(error_message, status_code=status_code, response=response, details=error_extra)
    if status_code == 401:
        msg = (
            f"{base_message}\n"
            "Your API key may be invalid or expired. "
            "Get a new key at https://openalex.org/api-key"
        )
        raise AuthenticationError(msg)
    if status_code == 403:
        msg = (
            f"{base_message}\n"
            "You don't have permission to access this resource."
        )
        raise AuthenticationError(msg)
    if status_code == 404:
        msg = (
            f"{base_message}\n"
            "The requested resource does not exist. "
            "Check the entity ID or endpoint."
        )
        raise NotFoundError(msg)
    if status_code == 429:
        retry_after_raw = response.headers.get("Retry-After")
        retry_after: int | None = None
        if retry_after_raw:
            if retry_after_raw.isdigit():
                retry_after = int(retry_after_raw)
            else:
                from datetime import UTC, datetime
                from email.utils import parsedate_to_datetime

                try:
                    retry_dt = parsedate_to_datetime(retry_after_raw)
                    retry_after = int((retry_dt - datetime.now(UTC)).total_seconds())
                except Exception:
                    retry_after = None
        raise RateLimitError(
            base_message,
            response=response,
            retry_after=retry_after,
            details=error_extra,
        )
    if 500 <= status_code < 600:
        msg = (
            f"{base_message}\n"
            "This is a server-side error. The request may succeed if retried."
        )
        if status_code == 503:
            retry_header = (
                response.headers.get("Retry-After") if hasattr(response, "headers") else None
            )
            if isinstance(retry_header, str) and retry_header:
                try:
                    header_str = retry_header
                    retry_after_val = int(header_str) if header_str.isdigit() else 0
                except Exception:
                    retry_after_val = 0
                raise TemporaryError(
                    msg,
                    status_code=status_code,
                    retry_after=retry_after_val,
                )
            raise ServerError(
                msg,
                status_code=status_code,
                response=response,
                details=error_extra,
            )
        raise ServerError(
            msg,
            status_code=status_code,
            response=response,
            details=error_extra,
        )
    raise APIError(error_message, status_code=status_code, response=response, details=error_extra)
