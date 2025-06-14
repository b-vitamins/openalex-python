"""Configuration for the OpenAlex client."""

from __future__ import annotations

from typing import Any

__all__ = ["OpenAlexConfig"]

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from . import __version__
from .constants import (
    ACCEPT_ENCODING_GZIP,
    ACCEPT_JSON,
    DEFAULT_BASE_URL,
    DEFAULT_CACHE_TTL,
    DEFAULT_PER_PAGE,
    DEFAULT_TIMEOUT,
    HEADER_ACCEPT,
    HEADER_ACCEPT_ENCODING,
    HEADER_AUTHORIZATION,
    HEADER_USER_AGENT,
)
from .utils.rate_limit import DEFAULT_BUFFER


class OpenAlexConfig(BaseModel):
    """Configuration for OpenAlex API client."""

    base_url: HttpUrl = Field(
        default=DEFAULT_BASE_URL,
        description="Base URL for the OpenAlex API",
    )
    email: str | None = Field(
        default=None,
        description="Email for polite pool access (recommended)",
    )
    api_key: str | None = Field(
        default=None,
        description="Premium API key for higher rate limits",
    )
    timeout: float = Field(
        default=DEFAULT_TIMEOUT,
        gt=0,
        le=300,
        description="Request timeout in seconds",
    )
    per_page: int = Field(
        default=DEFAULT_PER_PAGE,
        ge=1,
        le=200,
        description="Default items per page",
    )
    user_agent: str | None = Field(
        default=None,
        description="Custom user agent string",
    )
    cache_enabled: bool = Field(
        default=False,
        description="Enable request caching",
    )
    cache_maxsize: int = Field(
        default=1000,
        description="Maximum number of cached entries",
        ge=100,
        le=10000,
    )
    cache_ttl: float = Field(
        default=DEFAULT_CACHE_TTL,
        description="Default cache TTL in seconds",
        ge=0.0,
        le=86400.0,
    )
    rate_limit_buffer: float = Field(
        default=DEFAULT_BUFFER,
        ge=0,
        le=1,
        description="Rate limit buffer (0-1)",
    )

    # Retry settings
    retry_enabled: bool = Field(
        default=True,
        description="Enable automatic retry for failed requests",
    )
    retry_max_attempts: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=1,
        le=10,
        alias="max_retries",
    )
    retry_initial_wait: float = Field(
        default=1.0,
        description="Initial wait time between retries in seconds",
        ge=0.1,
        le=60.0,
    )
    retry_max_wait: float = Field(
        default=60.0,
        description="Maximum wait time between retries in seconds",
        ge=1.0,
        le=300.0,
    )
    retry_exponential_base: float = Field(
        default=2.0,
        description="Base for exponential backoff",
        ge=1.1,
        le=4.0,
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure base URL doesn't have trailing slash."""
        return HttpUrl(str(v).rstrip("/"))

    @property
    def headers(self) -> dict[str, str]:
        """Get default headers for requests."""
        headers: dict[str, str] = {
            HEADER_ACCEPT: ACCEPT_JSON,
            HEADER_ACCEPT_ENCODING: ACCEPT_ENCODING_GZIP,
        }

        # Build user agent
        ua_parts = [f"openalex-python/{__version__}"]
        if self.email:
            ua_parts.append(f"(mailto:{self.email})")
        if self.user_agent:
            ua_parts.append(self.user_agent)
        headers[HEADER_USER_AGENT] = " ".join(ua_parts)

        # Add API key if provided
        if self.api_key:
            headers[HEADER_AUTHORIZATION] = f"Bearer {self.api_key}"

        return headers

    @property
    def params(self) -> dict[str, Any]:
        """Get default query parameters."""
        params: dict[str, Any] = {}
        if self.email:
            params["mailto"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    model_config = ConfigDict(frozen=True, populate_by_name=True)
