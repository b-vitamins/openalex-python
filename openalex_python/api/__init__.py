"""Expose API client classes."""

from __future__ import annotations

from .authors_api import AuthorsApi
from .autocomplete_api import AutocompleteApi
from .base import BaseApi
from .concepts_api import ConceptsApi
from .funders_api import FundersApi
from .general_api import GeneralApi
from .institutions_api import InstitutionsApi
from .keywords_api import KeywordsApi
from .publishers_api import PublishersApi
from .sources_api import SourcesApi
from .text_api import TextApi
from .topics_api import TopicsApi
from .works_api import WorksApi

__all__ = [
    "AuthorsApi",
    "AutocompleteApi",
    "BaseApi",
    "ConceptsApi",
    "FundersApi",
    "GeneralApi",
    "InstitutionsApi",
    "KeywordsApi",
    "PublishersApi",
    "SourcesApi",
    "TextApi",
    "TopicsApi",
    "WorksApi",
]
