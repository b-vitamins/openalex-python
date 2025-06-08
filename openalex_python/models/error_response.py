"""Details about an API error."""
from __future__ import annotations


class ErrorResponse:
    """Represents an error returned by the API."""

    def __init__(self, *, error: str, message: str) -> None:
        self.error = error
        self.message = message
