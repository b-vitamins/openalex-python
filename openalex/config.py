"""Configuration for the OpenAlex client."""

from __future__ import annotations

from typing import Any

__all__ = ["OpenAlexConfig"]

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from . import __version__
from .constants import (
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
        default=True,
        description="Enable response caching",
    )
    cache_ttl: int = Field(
        default=DEFAULT_CACHE_TTL,
        ge=0,
        description="Cache TTL in seconds",
    )
    rate_limit_buffer: float = Field(
        default=DEFAULT_BUFFER,
        ge=0,
        le=1,
        description="Rate limit buffer (0-1)",
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
            HEADER_ACCEPT: "application/json",
            HEADER_ACCEPT_ENCODING: "gzip, deflate",
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

    model_config = ConfigDict(frozen=True)
