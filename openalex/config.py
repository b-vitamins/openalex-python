"""Configuration for the OpenAlex client."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class OpenAlexConfig(BaseModel):
    """Configuration for OpenAlex API client."""

    base_url: HttpUrl = Field(
        default=HttpUrl("https://api.openalex.org"),
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
    retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retries for failed requests",
    )
    timeout: float = Field(
        default=30.0,
        gt=0,
        le=300,
        description="Request timeout in seconds",
    )
    per_page: int = Field(
        default=200,
        ge=1,
        le=200,
        description="Default items per page",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries",
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
        default=3600,
        ge=0,
        description="Cache TTL in seconds",
    )
    rate_limit_buffer: float = Field(
        default=0.1,
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
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }

        # Build user agent
        ua_parts = ["openalex-python/0.1.0"]
        if self.email:
            ua_parts.append(f"(mailto:{self.email})")
        if self.user_agent:
            ua_parts.append(self.user_agent)
        headers["User-Agent"] = " ".join(ua_parts)

        # Add API key if provided
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    @property
    def params(self) -> dict[str, Any]:
        """Get default query parameters."""
        params: dict[str, Any] = {}
        if self.email:
            params["mailto"] = self.email
        return params

    model_config = ConfigDict(frozen=True)
