"""Identifier collection for an author."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AuthorIds:
    """Various IDs pointing to author profiles in external systems."""

    openalex: str
    orcid: str | None = None
    scopus: str | None = None
    twitter: str | None = None
    wikipedia: str | None = None

