"""OpenAlex data models."""

from .author import Author, AuthorAffiliation, AuthorIds
from .base import (
    AutocompleteResult,
    CountsByYear,
    DehydratedEntity,
    EntityType,
    Geo,
    GroupByResult,
    InternationalNames,
    ListResult,
    Meta,
    OpenAlexBase,
    OpenAlexEntity,
    Role,
    SummaryStats,
)
from .concept import Concept, ConceptAncestor, ConceptIds, RelatedConcept
from .filters import (
    AuthorsFilter,
    BaseFilter,
    GroupBy,
    InstitutionsFilter,
    SortOrder,
    WorksFilter,
)
from .funder import Funder, FunderIds
from .institution import (
    AssociatedInstitution,
    Institution,
    InstitutionIds,
    InstitutionType,
    Repository,
)
from .keyword import Keyword
from .publisher import Publisher, PublisherIds
from .source import APCPrice, Society, Source, SourceIds, SourceType
from .topic import Topic, TopicHierarchy, TopicIds, TopicLevel
from .work import (
    APC,
    Authorship,
    Biblio,
    CitationNormalizedPercentile,
    DehydratedAuthor,
    DehydratedConcept,
    DehydratedInstitution,
    DehydratedSource,
    DehydratedTopic,
    Grant,
    KeywordTag,
    Location,
    MeshTag,
    OpenAccess,
    OpenAccessStatus,
    SustainableDevelopmentGoal,
    Work,
    WorkIds,
    WorkType,
)

__all__ = [
    "APC",
    "APCPrice",
    "AssociatedInstitution",
    # Author models
    "Author",
    "AuthorAffiliation",
    "AuthorIds",
    "AuthorsFilter",
    "Authorship",
    "AutocompleteResult",
    # Filters
    "BaseFilter",
    "Biblio",
    "CitationNormalizedPercentile",
    # Concept models
    "Concept",
    "ConceptAncestor",
    "ConceptIds",
    "CountsByYear",
    "DehydratedAuthor",
    "DehydratedConcept",
    "DehydratedEntity",
    "DehydratedInstitution",
    "DehydratedSource",
    "DehydratedTopic",
    "EntityType",
    # Funder models
    "Funder",
    "FunderIds",
    "Geo",
    "Grant",
    "GroupBy",
    "GroupByResult",
    # Institution models
    "Institution",
    "InstitutionIds",
    "InstitutionType",
    "InstitutionsFilter",
    "InternationalNames",
    # Keyword models
    "Keyword",
    "KeywordTag",
    "ListResult",
    "Location",
    "MeshTag",
    "Meta",
    "OpenAccess",
    "OpenAccessStatus",
    # Base models
    "OpenAlexBase",
    "OpenAlexEntity",
    # Publisher models
    "Publisher",
    "PublisherIds",
    "RelatedConcept",
    "Repository",
    "Role",
    "Society",
    "SortOrder",
    # Source models
    "Source",
    "SourceIds",
    "SourceType",
    "SummaryStats",
    "SustainableDevelopmentGoal",
    # Topic models
    "Topic",
    "TopicHierarchy",
    "TopicIds",
    "TopicLevel",
    # Work models
    "Work",
    "WorkIds",
    "WorkType",
    "WorksFilter",
]
