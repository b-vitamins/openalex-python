"""Synchronous OpenAlex API client used for behavior tests."""

from __future__ import annotations

import contextlib
import time
from typing import Any, cast

import httpx

from .cache.manager import CacheManager
from .config import OpenAlexConfig
from .exceptions import (
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    raise_for_status,
)
from .utils.common import normalize_entity_id


class OpenAlexClient:
    """Minimal synchronous client for the OpenAlex API."""

    def __init__(self, config: OpenAlexConfig | None = None) -> None:
        self.config = config or OpenAlexConfig()
        self._client = httpx.Client(
            headers=self.config.headers,
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=True,
        )
        self._cache_manager = CacheManager(self.config)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _build_url(self, path: str) -> str:
        base = str(self.config.base_url).rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    def _default_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        merged = self.config.headers.copy()
        if headers:
            merged.update(headers)
        return merged

    def _default_params(self, params: dict[str, Any] | None) -> dict[str, Any]:
        merged = self.config.params.copy()
        if params:
            merged.update(params)
        return merged

    def _normalize_path(self, path: str) -> tuple[str, str, str | None]:
        path = path.strip()
        parts = path.lstrip("/").split("/", 1)
        endpoint = parts[0]
        entity_id: str | None = None
        if len(parts) > 1 and parts[1]:
            entity_id = normalize_entity_id(parts[1].strip(), endpoint.rstrip("s"))
            path = f"/{endpoint}/{entity_id}"
        else:
            path = f"/{endpoint}"
        return path, endpoint, entity_id

    # ------------------------------------------------------------------
    # request handling
    # ------------------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = self._build_url(path)
        req_headers = self._default_headers(headers)
        req_params = self._default_params(params)

        attempt = 0
        # ``retry_max_attempts`` already represents the total number of attempts
        # allowed (including the first request).  Do not add 1 here to avoid
        # exceeding the configured retry limit.
        max_attempts = (
            self.config.retry_max_attempts if self.config.retry_enabled else 1
        )
        wait = self.config.retry_initial_wait

        while True:
            try:
                response = self._client.request(
                    method,
                    url,
                    headers=req_headers,
                    params=req_params,
                )
            except httpx.TimeoutException as exc:  # pragma: no cover - network
                attempt += 1
                if attempt >= max_attempts:
                    raise TimeoutError(str(exc)) from exc
                time.sleep(min(wait, self.config.retry_max_wait))
                wait = min(
                    wait * self.config.retry_exponential_base,
                    self.config.retry_max_wait,
                )
                continue
            except httpx.NetworkError as exc:  # pragma: no cover - network
                attempt += 1
                if attempt >= max_attempts:
                    raise NetworkError(str(exc)) from exc
                time.sleep(min(wait, self.config.retry_max_wait))
                wait = min(
                    wait * self.config.retry_exponential_base,
                    self.config.retry_max_wait,
                )
                continue

            status = response.status_code
            if status == 429:
                retry_after_raw = response.headers.get("Retry-After")
                retry_after = int(retry_after_raw) if retry_after_raw else None
                attempt += 1
                if attempt >= max_attempts:
                    raise RateLimitError(retry_after=retry_after)
                sleep_for = retry_after or wait
                time.sleep(min(sleep_for, self.config.retry_max_wait))
                wait = min(
                    wait * self.config.retry_exponential_base,
                    self.config.retry_max_wait,
                )
                continue
            if status in (502, 503, 504):
                attempt += 1
                if attempt >= max_attempts:
                    msg = f"Server error {status}"
                    raise ServerError(msg)
                time.sleep(min(wait, self.config.retry_max_wait))
                wait = min(
                    wait * self.config.retry_exponential_base,
                    self.config.retry_max_wait,
                )
                continue
            if 500 <= status < 600:
                attempt += 1
                if attempt >= max_attempts:
                    msg = f"Server error {status}"
                    raise ServerError(msg)
                time.sleep(min(wait, self.config.retry_max_wait))
                wait = min(
                    wait * self.config.retry_exponential_base,
                    self.config.retry_max_wait,
                )
                continue
            if status == 404:
                with contextlib.suppress(Exception):
                    data = response.json()
                message = locals().get("data", {}).get("error", "Resource not found")
                raise NotFoundError(message)

            raise_for_status(response)
            return cast("dict[str, Any]", response.json())

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        norm_path, endpoint, entity_id = self._normalize_path(path)

        def fetch() -> dict[str, Any]:
            return self._request("GET", norm_path, params=params)

        if self._cache_manager.enabled:
            return self._cache_manager.get_or_fetch(
                endpoint,
                fetch,
                entity_id=entity_id,
                params=params,
            )
        return fetch()

    def close(self) -> None:
        self._client.close()
