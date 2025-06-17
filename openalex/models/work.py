"""Query filters and parameters for OpenAlex API."""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from ..utils.text import invert_abstract

__all__ = [
    "Work",
    "WorkIds",
    "WorkType",
    "WorksFilter",
]

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
    BOOK_CHAPTER = "book-chapter"
    DATASET = "dataset"
    DISSERTATION = "dissertation"
    ERRATUM = "erratum"
    LETTER = "letter"
    PARATEXT = "paratext"
    PREPRINT = "preprint"
    REFERENCE_ENTRY = "reference-entry"
    REVIEW = "review"


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
    oa_url: str | None = None
    any_repository_has_fulltext: bool | None = None


class DehydratedAuthor(DehydratedEntity):
    """Minimal author representation."""

    id: str | None = None
    orcid: str | None = None


class DehydratedConcept(DehydratedEntity):
    """Minimal concept representation with optional details."""

    id: str | None = None

    level: int | None = None
    score: float | None = None
    wikidata: str | None = None


class DehydratedInstitution(DehydratedEntity):
    """Minimal institution representation with optional details."""

    id: str | None = None

    ror: str | None = None
    country_code: str | None = None
    type: InstitutionType | None = None
    lineage: list[str] = Field(default_factory=list)


class DehydratedSource(DehydratedEntity):
    """Minimal source representation."""

    id: str | None = None

    type: str | None = None
    issn_l: str | None = None
    is_oa: bool | None = None
    is_in_doaj: bool | None = None


class DehydratedTopic(DehydratedEntity):
    """Minimal topic representation."""

    id: str | None = None

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
    landing_page_url: str | None = None
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
        return self.first_page


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
    doi: str | None = None
    pmid: str | None = None
    pmcid: str | None = None
    mag: str | None = None

    @field_validator("doi")
    @classmethod
    def normalize_doi(cls, v: str | None) -> str | None:
        """Normalize DOI to lowercase."""
        return v.lower() if v else None

    @field_validator("pmid")
    @classmethod
    def validate_pmid(cls, v: str | None) -> str | None:
        """Validate PMID allowing numeric ID or full URL."""
        if v is None:
            return None

        if v.isdigit():
            return v

        try:
            parsed = urlparse(v)
        except Exception:
            parsed = None

        if parsed and parsed.scheme in {"http", "https"} and parsed.netloc:
            last_part = parsed.path.rstrip("/").split("/")[-1]
            if last_part.isdigit():
                return v

        msg = f"Invalid PMID format: {v}"
        raise ValueError(msg)

    @field_validator("pmcid")
    @classmethod
    def validate_pmcid(cls, v: str | None) -> str | None:
        """Validate PMCID allowing prefix or URL."""
        if v is None:
            return None

        if re.match(r"^PMC\d+$", v):
            return v

        try:
            parsed = urlparse(v)
        except Exception:
            parsed = None

        if parsed and parsed.scheme in {"http", "https"} and parsed.netloc:
            last_part = parsed.path.rstrip("/").split("/")[-1]
            if last_part.lower().startswith("pmc"):
                digits = last_part[3:]
            else:
                digits = last_part
            if digits.isdigit():
                return v

        msg = f"Invalid PMC ID format: {v}"
        raise ValueError(msg)


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

    doi: str | None = None
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
    institutions_distinct_count: int | None = None
    institution_assertions: list[str] = Field(default_factory=list)
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
    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None
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
    relevance_score: float | None = None

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, v: str | None) -> str | None:
        """Validate DOI format."""
        if v is None:
            return None

        normalized = v
        if v.startswith("https://doi.org/"):
            normalized = v[16:]
        elif v.startswith("http://doi.org/"):
            normalized = v[15:]

        doi_pattern = r"^10\.\d{4,9}/[-._;()/:\w]+$"
        if not re.match(doi_pattern, normalized):
            msg = f"Invalid DOI format: {v}"
            raise ValueError(msg)

        return v

    @field_validator("publication_date", "created_date", mode="before")
    @classmethod
    def validate_dates(cls, v: str | date | None) -> date | None:
        """Validate and parse date fields."""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00")).date()
        except ValueError:
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            msg = f"Unable to parse date: {v}"
            raise ValueError(msg) from None

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        """Validate language code is ISO 639-1."""
        if v is None:
            return None
        if not re.match(r"^[a-z]{2}$", v.lower()):
            msg = f"Invalid language code: {v}. Expected ISO 639-1 format (e.g., 'en', 'es')"
            raise ValueError(msg)
        return v.lower()

    @field_validator("volume", "issue", "first_page", "last_page")
    @classmethod
    def validate_bibliographic_info(cls, v: str | None) -> str | None:
        """Validate bibliographic information fields."""
        if v is None:
            return None
        v = v.strip()
        if v == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_page_range(self) -> Work:
        """Validate that page range is logical."""
        if self.first_page and self.last_page:
            try:
                first = int(re.sub(r"[^\d]", "", self.first_page))
                last = int(re.sub(r"[^\d]", "", self.last_page))
            except ValueError:
                pass
            else:
                if first > last:
                    msg = f"Invalid page range: {self.first_page}-{self.last_page}"
                    raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_citation_count(self) -> Work:
        """Ensure citation counts are non-negative."""
        if self.cited_by_count is not None and self.cited_by_count < 0:
            msg = "cited_by_count cannot be negative"
            raise ValueError(msg)
        if (
            self.referenced_works_count is not None
            and self.referenced_works_count < 0
        ):
            msg = "referenced_works_count cannot be negative"
            raise ValueError(msg)
        return self

    @property
    def abstract(self) -> str | None:
        """Get abstract as plaintext."""
        return invert_abstract(self.abstract_inverted_index)

    @model_validator(mode="after")
    def _set_defaults(self) -> Work:
        """Populate derived fields after initialization."""
        if self.title is None:
            self.title = self.display_name
        if self.is_oa is None and self.open_access is not None:
            self.is_oa = self.open_access.is_oa
        if self.doi is None and self.ids and self.ids.doi is not None:
            self.doi = self.ids.doi
        if self.ids is None and self.doi is not None:
            self.ids = WorkIds(doi=self.doi, openalex=self.id)
        if self.biblio is None and any(
            [self.volume, self.issue, self.first_page, self.last_page]
        ):
            object.__setattr__(
                self,
                "biblio",
                Biblio(
                    volume=self.volume,
                    issue=self.issue,
                    first_page=self.first_page,
                    last_page=self.last_page,
                ),
            )
        elif self.biblio is not None:
            if self.volume is None:
                object.__setattr__(self, "volume", self.biblio.volume)
            if self.issue is None:
                object.__setattr__(self, "issue", self.biblio.issue)
            if self.first_page is None:
                object.__setattr__(self, "first_page", self.biblio.first_page)
            if self.last_page is None:
                object.__setattr__(self, "last_page", self.biblio.last_page)
        return self

    def citations_in_year(self, year: int) -> int:
        """Return citation count for a given year."""
        return next(
            (
                cy.cited_by_count
                for cy in self.counts_by_year
                if cy.year == year
            ),
            0,
        )

    def author_names(self) -> list[str]:
        """Return list of author display names."""
        return [
            auth.author.display_name
            for auth in self.authorships
            if auth.author and auth.author.display_name
        ]

    def institution_names(self) -> list[str]:
        """Return list of affiliated institution names."""
        return list(
            {
                inst.display_name
                for auth in self.authorships
                for inst in auth.institutions
                if inst.display_name
            }
        )

    def has_abstract(self) -> bool:
        """Return ``True`` if the work has an abstract."""
        return self.abstract is not None

    def has_references(self) -> bool:
        """Return ``True`` if the work has reference information."""
        return bool(self.referenced_works_count or self.referenced_works)


class Ngram(OpenAlexBase):
    """N-gram from a work."""

    ngram: str
    ngram_count: int
    ngram_tokens: int
    term_frequency: float | None = None


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
Ngram.model_rebuild()
