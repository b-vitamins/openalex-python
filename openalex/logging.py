"""Logging configuration with privacy controls."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

import structlog

if TYPE_CHECKING:  # pragma: no cover - typing-only imports
    from structlog.types import EventDict, Processor

__all__ = [
    "RequestLogger",
    "configure_logging",
    "sanitize_sensitive_data",
]


def sanitize_sensitive_data(data: Any) -> Any:
    """Remove or mask sensitive data from logs."""
    if isinstance(data, dict):
        sanitized: dict[str, Any] = {}
        sensitive_keys = {
            "api_key",
            "email",
            "password",
            "token",
            "authorization",
        }

        data_dict: dict[Any, Any] = cast(dict[Any, Any], data)
        for key, value in data_dict.items():
            key_str: str = str(key)
            value_any: Any = value
            if any(
                sensitive in key_str.lower() for sensitive in sensitive_keys
            ):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_sensitive_data(value_any)
        return sanitized

    if isinstance(data, list):
        data_list: list[Any] = cast(list[Any], data)
        return [sanitize_sensitive_data(item) for item in data_list]

    if isinstance(data, str):
        import re

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.sub(email_pattern, "[EMAIL]", data)

    return data


class PrivacyProcessor:
    """Structlog processor that sanitizes sensitive data."""

    def __call__(
        self, _logger: Any, _method_name: str, event_dict: EventDict
    ) -> EventDict:
        """Process log event to remove sensitive data."""
        return cast("EventDict", sanitize_sensitive_data(event_dict))


class RequestLogger:
    """Logger for HTTP requests with privacy controls."""

    def __init__(
        self, *, enabled: bool = True, include_headers: bool = False
    ) -> None:
        """Initialize request logger."""
        self.enabled = enabled
        self.include_headers = include_headers
        self.logger = structlog.get_logger(__name__)

    def log_request(
        self, method: str, url: str, headers: dict[str, str] | None = None
    ) -> None:
        """Log outgoing request."""
        if not self.enabled:
            return

        log_data = {
            "event": "http_request",
            "method": method,
            "url": self._sanitize_url(url),
        }

        if self.include_headers and headers:
            log_data["headers"] = sanitize_sensitive_data(headers)

        self.logger.info(**log_data)

    def log_response(
        self,
        status_code: int,
        response_time: float,
        url: str,
        *,
        cached: bool = False,
    ) -> None:
        """Log response received."""
        if not self.enabled:
            return

        self.logger.info(
            "http_response",
            status_code=status_code,
            response_time_ms=f"{response_time:.2f}",
            url=self._sanitize_url(url),
            cached=cached,
        )

    def log_error(self, error: Exception, url: str) -> None:
        """Log request error."""
        if not self.enabled:
            return

        self.logger.error(
            "http_error",
            error_type=type(error).__name__,
            error_message=str(error),
            url=self._sanitize_url(url),
        )

    def _sanitize_url(self, url: str) -> str:
        """Remove sensitive parameters from URL."""
        import re

        return re.sub(r"api_key=[^&]+", "api_key=[REDACTED]", url)


def configure_logging(
    *,
    level: str = "INFO",
    format: str = "json",
    include_timestamps: bool = True,
    privacy_mode: bool = True,
) -> None:
    """Configure structured logging for the OpenAlex client.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format: Output format ('json' or 'console')
        include_timestamps: Whether to include timestamps
        privacy_mode: Whether to sanitize sensitive data
    """
    logging.basicConfig(level=level)

    processors: list[Processor] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
    ]

    if include_timestamps:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))

    if privacy_mode:
        processors.append(PrivacyProcessor())

    if format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
