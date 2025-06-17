from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


class RequestInterceptor(ABC):
    @abstractmethod
    def process_request(self, request: httpx.Request) -> httpx.Request:
        """Modify request before sending."""
        raise NotImplementedError


class ResponseInterceptor(ABC):
    @abstractmethod
    def process_response(self, response: httpx.Response) -> httpx.Response:
        """Process response after receiving."""
        raise NotImplementedError


class Middleware:
    def __init__(self) -> None:
        self.request_interceptors: list[RequestInterceptor] = []
        self.response_interceptors: list[ResponseInterceptor] = []
