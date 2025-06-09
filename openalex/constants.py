"""Common string and numeric constants for OpenAlex."""

from __future__ import annotations

from enum import Enum
from http import HTTPStatus

from pydantic import HttpUrl

OPENALEX_ID_PREFIX = "https://openalex.org/"
ORCID_URL_PREFIX = "https://orcid.org/"
DOI_URL_PREFIX = "https://doi.org/"
PMID_PREFIX = "pmid:"
MAG_PREFIX = "mag:"
ROR_URL_PREFIX = "https://ror.org/"

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
MAX_SECONDS_IN_MINUTE = SECONDS_PER_MINUTE - 1

DEFAULT_RATE_LIMIT = 10.0
DEFAULT_TIMEOUT = 30.0
DEFAULT_PER_PAGE = 200
DEFAULT_CACHE_TTL = 3600
DEFAULT_CONCURRENCY = 5
FIRST_PAGE = 1
SINGLE_PER_PAGE = 1
FILTER_DEFAULT_PER_PAGE = 25
REQUEST_FAILED_MSG = "Request failed after all retries"
DEFAULT_BASE_URL = HttpUrl("https://api.openalex.org")
HTTP_METHOD_GET = "GET"
HEADER_ACCEPT = "Accept"
HEADER_ACCEPT_ENCODING = "Accept-Encoding"
HEADER_AUTHORIZATION = "Authorization"
HEADER_USER_AGENT = "User-Agent"
ACCEPT_JSON = "application/json"
ACCEPT_ENCODING_GZIP = "gzip, deflate"
PARAM_Q = "q"
PARAM_CURSOR = "cursor"
PARAM_PAGE = "page"
PARAM_PER_PAGE = "per-page"
AUTOCOMPLETE_PATH = "autocomplete"
RANDOM_PATH = "random"
TEXT_PATH = "text"
UNREACHABLE_MSG = "Unreachable"


class Resource(str, Enum):
    """Enumeration of OpenAlex resource endpoints."""

    WORKS = "works"
    AUTHORS = "authors"
    INSTITUTIONS = "institutions"
    SOURCES = "sources"
    CONCEPTS = "concepts"
    TOPICS = "topics"
    PUBLISHERS = "publishers"
    FUNDERS = "funders"
    KEYWORDS = "keywords"


GOVERNMENT_KEYWORDS = [
    "national",
    "federal",
    "ministry",
    "department",
    "agency",
]

HTTP_TOO_MANY_REQUESTS = HTTPStatus.TOO_MANY_REQUESTS
HTTP_UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_SERVER_ERROR_BOUNDARY = HTTPStatus.INTERNAL_SERVER_ERROR

__all__ = [
    "ACCEPT_ENCODING_GZIP",
    "ACCEPT_JSON",
    "AUTOCOMPLETE_PATH",
    "DEFAULT_BASE_URL",
    "DEFAULT_CACHE_TTL",
    "DEFAULT_CONCURRENCY",
    "DEFAULT_PER_PAGE",
    "DEFAULT_RATE_LIMIT",
    "DEFAULT_TIMEOUT",
    "DOI_URL_PREFIX",
    "FILTER_DEFAULT_PER_PAGE",
    "FIRST_PAGE",
    "GOVERNMENT_KEYWORDS",
    "HEADER_ACCEPT",
    "HEADER_ACCEPT_ENCODING",
    "HEADER_AUTHORIZATION",
    "HEADER_USER_AGENT",
    "HTTP_METHOD_GET",
    "HTTP_NOT_FOUND",
    "HTTP_SERVER_ERROR_BOUNDARY",
    "HTTP_TOO_MANY_REQUESTS",
    "HTTP_UNAUTHORIZED",
    "MAG_PREFIX",
    "MAX_SECONDS_IN_MINUTE",
    "MINUTES_PER_HOUR",
    "OPENALEX_ID_PREFIX",
    "ORCID_URL_PREFIX",
    "PARAM_CURSOR",
    "PARAM_PAGE",
    "PARAM_PER_PAGE",
    "PARAM_Q",
    "PMID_PREFIX",
    "RANDOM_PATH",
    "REQUEST_FAILED_MSG",
    "ROR_URL_PREFIX",
    "SECONDS_PER_MINUTE",
    "SINGLE_PER_PAGE",
    "TEXT_PATH",
    "UNREACHABLE_MSG",
    "Resource",
]
