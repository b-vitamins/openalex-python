"""OpenAlex API resources."""

from .authors import AsyncAuthorsResource, AuthorsResource
from .base import AsyncBaseResource, BaseResource
from .concepts import AsyncConceptsResource, ConceptsResource
from .funders import AsyncFundersResource, FundersResource
from .institutions import AsyncInstitutionsResource, InstitutionsResource
from .keywords import AsyncKeywordsResource, KeywordsResource
from .publishers import AsyncPublishersResource, PublishersResource
from .sources import AsyncSourcesResource, SourcesResource
from .topics import AsyncTopicsResource, TopicsResource
from .works import AsyncWorksResource, WorksResource

__all__ = [
    # Async resources
    "AsyncAuthorsResource",
    "AsyncBaseResource",
    "AsyncConceptsResource",
    "AsyncFundersResource",
    "AsyncInstitutionsResource",
    "AsyncKeywordsResource",
    "AsyncPublishersResource",
    "AsyncSourcesResource",
    "AsyncTopicsResource",
    "AsyncWorksResource",
    # Sync resources
    "AuthorsResource",
    # Base classes
    "BaseResource",
    "ConceptsResource",
    "FundersResource",
    "InstitutionsResource",
    "KeywordsResource",
    "PublishersResource",
    "SourcesResource",
    "TopicsResource",
    "WorksResource",
]
