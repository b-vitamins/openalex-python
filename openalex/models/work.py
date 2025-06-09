"""Query filters and parameters for OpenAlex API."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

if TYPE_CHECKING:
    from .institution import InstitutionType
    from .topic import TopicHierarchy

from .base import (
    CountsByYear,
    DehydratedEntity,
    OpenAlexBase,
    OpenAlexEntity,
)


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class GroupBy(str, Enum):
    """Common group-by options."""

    PUBLICATION_YEAR = "publication_year"
    TYPE = "type"
    OPEN_ACCESS_STATUS = "oa_status"
    AUTHORSHIPS_INSTITUTIONS_COUNTRY_CODE = (
        "authorships.institutions.country_code"
    )
    INSTITUTIONS_TYPE = "institutions.type"
    CITED_BY_COUNT = "cited_by_count"
    WORKS_COUNT = "works_count"


class WorkType(str, Enum):
    """Types of works."""

    ARTICLE = "article"
    BOOK = "book"
    REPORT = "report"
    OTHER = "other"


class OpenAccessStatus(str, Enum):
    """Open access status values."""

    BRONZE = "bronze"
    GREEN = "green"
    GOLD = "gold"
    HYBRID = "hybrid"
    CLOSED = "closed"


class OpenAccess(BaseModel):
    """Open access information for a work."""

    is_oa: bool = False
    oa_status: OpenAccessStatus | None = None
    oa_url: HttpUrl | None = None
    any_repository_has_fulltext: bool | None = None


class DehydratedAuthor(DehydratedEntity):
    """Minimal author representation."""

    id: str | None = None
    orcid: str | None = None


class DehydratedConcept(DehydratedEntity):
    """Minimal concept representation with optional details."""

    level: int | None = None
    score: float | None = None


class DehydratedInstitution(DehydratedEntity):
    """Minimal institution representation with optional details."""

    ror: HttpUrl | None = None
    country_code: str | None = None
    type: InstitutionType | None = None
    lineage: list[str] = Field(default_factory=list)


class DehydratedSource(DehydratedEntity):
    """Minimal source representation."""

    type: str | None = None


class DehydratedTopic(DehydratedEntity):
    """Minimal topic representation."""

    score: float | None = None
    subfield: TopicHierarchy | None = None
    field: TopicHierarchy | None = None
    domain: TopicHierarchy | None = None


class KeywordTag(OpenAlexBase):
    """Keyword tag for a work."""

    id: str | None = None
    display_name: str | None = None
    score: float | None = None


class MeshTag(OpenAlexBase):
    """MeSH tag for a work."""

    descriptor_ui: str | None = None
    descriptor_name: str | None = None
    qualifier_ui: str | None = None
    qualifier_name: str | None = None
    is_major_topic: bool | None = None


class Location(OpenAlexBase):
    """Location of a hosted version of the work."""

    is_oa: bool = False
    landing_page_url: HttpUrl | None = None
    pdf_url: str | None = None
    source: DehydratedSource | None = None
    license: str | None = None
    license_id: str | None = None
    version: str | None = None
    is_accepted: bool | None = None
    is_published: bool | None = None


class Grant(OpenAlexBase):
    """Grant supporting the work."""

    funder: str | None = None
    funder_display_name: str | None = None
    award_id: str | None = None


class APC(OpenAlexBase):
    """Article processing charge information."""

    value: int | None = None
    currency: str | None = None
    value_usd: int | None = None
    provenance: str | None = None


class Biblio(OpenAlexBase):
    """Bibliographic information for a work."""

    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None

    @property
    def page_range(self) -> str | None:
        """Return formatted page range if available."""
        if self.first_page and self.last_page:
            return f"{self.first_page}-{self.last_page}"
        if self.first_page:
            return self.first_page
        return None


class CitationNormalizedPercentile(OpenAlexBase):
    """Citation percentile information."""

    value: float | None = None
    is_in_top_1_percent: bool | None = None
    is_in_top_10_percent: bool | None = None


class SustainableDevelopmentGoal(OpenAlexBase):
    """UN SDG associated with a work."""

    id: str | None = None
    display_name: str | None = None
    score: float | None = None


class WorkIds(OpenAlexBase):
    """External identifiers for a work."""

    openalex: str | None = None
    doi: HttpUrl | None = None
    pmid: str | None = None


class Authorship(OpenAlexBase):
    """Authorship information."""

    author_position: str | None = None
    author: DehydratedAuthor | None = None
    institutions: list[DehydratedInstitution] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    is_corresponding: bool | None = None
    raw_author_name: str | None = None
    raw_affiliation_strings: list[str] = Field(default_factory=list)


class Work(OpenAlexEntity):
    """Representation of a work."""

    title: str | None = None
    publication_year: int | None = None
    publication_date: date | None = None
    type: WorkType | None = None
    type_crossref: str | None = None
    cited_by_count: int = 0
    is_retracted: bool = False
    is_paratext: bool = False
    fwci: float | None = None
    open_access: OpenAccess | None = None
    is_oa: bool | None = None
    authorships: list[Authorship] = Field(default_factory=list)
    corresponding_author_ids: list[str] = Field(default_factory=list)
    corresponding_institution_ids: list[str] = Field(default_factory=list)
    countries_distinct_count: int | None = None
    concepts: list[DehydratedConcept] = Field(default_factory=list)
    primary_topic: DehydratedTopic | None = None
    topics: list[DehydratedTopic] = Field(default_factory=list)
    mesh: list[MeshTag] = Field(default_factory=list)
    keywords: list[KeywordTag] = Field(default_factory=list)
    language: str | None = None
    primary_location: Location | None = None
    best_oa_location: Location | None = None
    locations_count: int | None = None
    locations: list[Location] = Field(default_factory=list)
    biblio: Biblio | None = None
    apc_list: APC | None = None
    apc_paid: APC | None = None
    grants: list[Grant] = Field(default_factory=list)
    citation_normalized_percentile: CitationNormalizedPercentile | None = None
    counts_by_year: list[CountsByYear] = Field(default_factory=list)
    abstract_inverted_index: dict[str, list[int]] | None = None
    created_date: date | None = None
    ids: WorkIds | None = None
    referenced_works: list[str] = Field(default_factory=list)
    referenced_works_count: int | None = None
    related_works: list[str] = Field(default_factory=list)
    has_fulltext: bool | None = None
    fulltext_origin: str | None = None
    sustainable_development_goals: list[SustainableDevelopmentGoal] = Field(
        default_factory=list
    )
    indexed_in: list[str] = Field(default_factory=list)
    ngrams_url: str | None = None

    @property
    def abstract(self) -> str | None:
        """Reconstruct abstract from inverted index."""
        if not self.abstract_inverted_index:
            return None

        length = (
            max(
                (
                    pos
                    for positions in self.abstract_inverted_index.values()
                    for pos in positions
                ),
                default=-1,
            )
            + 1
        )
        words: list[str] = [""] * length
        for word, positions in self.abstract_inverted_index.items():
            for pos in positions:
                if 0 <= pos < length:
                    words[pos] = word
        abstract = " ".join(words).strip()
        if not abstract.endswith(('.', '!', '?')):
            last_punct = max(abstract.rfind(p) for p in '.!?')
            if last_punct != -1:
                abstract = abstract[: last_punct + 1]
        return abstract

    @model_validator(mode="after")
    def _set_defaults(self) -> "Work":
        """Populate derived fields after initialization."""
        if self.title is None:
            self.title = self.display_name
        if self.is_oa is None and self.open_access is not None:
            self.is_oa = self.open_access.is_oa
        return self

    def citations_in_year(self, year: int) -> int:
        """Return citation count for a given year."""
        for cy in self.counts_by_year:
            if cy.year == year:
                return cy.cited_by_count
        return 0

    def author_names(self) -> list[str]:
        """Return list of author display names."""
        names = []
        for auth in self.authorships:
            if auth.author and auth.author.display_name:
                names.append(auth.author.display_name)
        return names

    def institution_names(self) -> list[str]:
        """Return list of affiliated institution names."""
        names: set[str] = set()
        for auth in self.authorships:
            for inst in auth.institutions:
                if inst.display_name:
                    names.add(inst.display_name)
        return list(names)

    def has_abstract(self) -> bool:
        """Return ``True`` if the work has an abstract."""
        return self.abstract is not None

    def has_references(self) -> bool:
        """Return ``True`` if the work has reference information."""
        if self.referenced_works_count:
            return self.referenced_works_count > 0
        return bool(self.referenced_works)


class BaseFilter(BaseModel):
    """Base class for query filters."""

    search: str | None = Field(None, description="Search query")
    filter: dict[str, Any] | str | None = Field(
        None, description="Filter expression"
    )
    sort: str | None = Field(None, description="Sort field")
    group_by: str | GroupBy | None = Field(None, description="Group by field")
    page: int | None = Field(None, ge=1, le=10000, description="Page number")
    per_page: int | None = Field(
        None, ge=1, le=200, description="Results per page"
    )
    cursor: str | None = Field(None, description="Pagination cursor")
    sample: int | None = Field(None, ge=1, description="Random sample size")
    seed: int | None = Field(None, description="Random seed")
    select: list[str] | str | None = Field(None, description="Fields to select")

    @field_validator("filter", mode="before")
    @classmethod
    def validate_filter(cls, v: Any) -> dict[str, Any] | str | None:
        """Validate and normalize filter parameter."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            return v
        msg = "Filter must be a string or dictionary"
        raise ValueError(msg)

    @field_validator("select", mode="before")
    @classmethod
    def validate_select(cls, v: Any) -> list[str] | str | None:
        """Validate select parameter."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return v
        msg = "Select must be a string or list of strings"
        raise ValueError(msg)

    def to_params(self) -> dict[str, Any]:
        """Convert to API query parameters."""
        params = {}

        for field_name, field_value in self.model_dump(
            exclude_none=True
        ).items():
            if field_name == "filter" and isinstance(field_value, dict):
                # Convert filter dict to API format
                params["filter"] = self._build_filter_string(field_value)
            elif field_name == "select" and isinstance(field_value, list):
                params["select"] = ",".join(field_value)
            elif field_name == "group_by":
                params["group-by"] = field_value
            elif field_name == "per_page":
                params["per-page"] = field_value
            else:
                params[field_name] = field_value

        return params

    def _build_filter_string(self, filters: dict[str, Any]) -> str:
        """Build filter string from dictionary."""
        filter_parts = []

        for key, value in filters.items():
            if value is None:
                continue

            if isinstance(value, bool):
                filter_parts.append(f"{key}:{str(value).lower()}")
            elif isinstance(value, list | tuple):
                values = "|".join(str(v) for v in value)
                filter_parts.append(f"{key}:{values}")
            elif isinstance(value, date | datetime):
                filter_parts.append(f"{key}:{value.isoformat()}")
            else:
                filter_parts.append(f"{key}:{value}")

        return ",".join(filter_parts)


class WorksFilter(BaseFilter):
    """Filters specific to works endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        pattern="^(publication_date|cited_by_count|relevance_score)(:(asc|desc))?$",
    )

    def with_publication_year(self, year: int | list[int]) -> WorksFilter:
        """Filter by publication year."""
        if isinstance(year, int):
            year = [year]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["publication_year"] = year
        return self.model_copy(update={"filter": current_filter})

    def with_type(self, work_type: str | list[str]) -> WorksFilter:
        """Filter by work type."""
        if isinstance(work_type, str):
            work_type = [work_type]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["type"] = work_type
        return self.model_copy(update={"filter": current_filter})

    def with_open_access(self, is_oa: bool = True) -> WorksFilter:  # noqa: FBT001,FBT002
        """Filter by open access status."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["is_oa"] = is_oa
        return self.model_copy(update={"filter": current_filter})


class AuthorsFilter(BaseFilter):
    """Filters specific to authors endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        pattern="^(display_name|cited_by_count|works_count|relevance_score)(:(asc|desc))?$",
    )


class InstitutionsFilter(BaseFilter):
    """Filters specific to institutions endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        pattern="^(display_name|cited_by_count|works_count|relevance_score)(:(asc|desc))?$",
    )

    def with_country(self, country_code: str | list[str]) -> InstitutionsFilter:
        """Filter by country code."""
        if isinstance(country_code, str):
            country_code = [country_code]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["country_code"] = country_code
        return self.model_copy(update={"filter": current_filter})

    def with_type(
        self, institution_type: str | list[str]
    ) -> InstitutionsFilter:
        """Filter by institution type."""
        if isinstance(institution_type, str):
            institution_type = [institution_type]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["type"] = institution_type
        return self.model_copy(update={"filter": current_filter})


from .institution import InstitutionType  # noqa: E402,TC001
from .topic import TopicHierarchy  # noqa: E402,TC001

DehydratedTopic.model_rebuild()
DehydratedInstitution.model_rebuild()
DehydratedAuthor.model_rebuild()
DehydratedSource.model_rebuild()
KeywordTag.model_rebuild()
MeshTag.model_rebuild()
Location.model_rebuild()
Grant.model_rebuild()
APC.model_rebuild()
Biblio.model_rebuild()
CitationNormalizedPercentile.model_rebuild()
SustainableDevelopmentGoal.model_rebuild()
Work.model_rebuild()
