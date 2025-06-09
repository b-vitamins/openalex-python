"""Query filters and parameters for OpenAlex API."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class GroupBy(str, Enum):
    """Common group-by options."""

    PUBLICATION_YEAR = "publication_year"
    TYPE = "type"
    OPEN_ACCESS_STATUS = "open_access.oa_status"
    AUTHORSHIPS_INSTITUTION = "authorships.institutions.id"
    AUTHORSHIPS_INSTITUTIONS_COUNTRY_CODE = (
        "authorships.institutions.country_code"
    )
    INSTITUTIONS_TYPE = "institutions.type"
    CITED_BY_COUNT = "cited_by_count"
    WORKS_COUNT = "works_count"


class BaseFilter(BaseModel):
    """Base class for query filters."""

    search: str | None = Field(None, description="Search query")
    filter: dict[str, Any] | str | None = Field(
        None, description="Filter expression"
    )
    sort: str | None = Field(None, description="Sort field")
    group_by: str | GroupBy | None = Field(None, description="Group by field")
    page: int | None = Field(
        default=None,
        ge=1,
        le=10000,
        description="Page number",
    )
    per_page: int | None = Field(
        default=None,
        ge=1,
        le=200,
        description="Results per page",
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
            elif isinstance(value, list | tuple | set):
                if len(value) == 0:
                    continue
                values = "|".join(str(v) for v in value)
                filter_parts.append(f"{key}:{values}")
            elif isinstance(value, date | datetime):
                filter_parts.append(f"{key}:{value.strftime('%Y-%m-%d')}")
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

    def _add_filter(self, key: str, value: Any) -> WorksFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_doi(self, doi: str) -> WorksFilter:
        """Filter by DOI."""
        return self._add_filter("doi", doi)

    def with_title(self, title: str) -> WorksFilter:
        """Filter by title search."""
        return self._add_filter("title.search", title)

    def with_publication_year(self, year: int | list[int]) -> WorksFilter:
        """Filter by publication year."""
        if isinstance(year, int):
            year = [year]
        return self._add_filter("publication_year", year)

    def with_type(self, work_type: str | list[str]) -> WorksFilter:
        """Filter by work type."""
        if isinstance(work_type, str):
            work_type = [work_type]
        return self._add_filter("type", work_type)

    def with_open_access(self, *, is_oa: bool = True) -> WorksFilter:
        """Filter by open access status."""
        return self._add_filter("is_oa", is_oa)

    def with_oa_status(self, status: str | list[str]) -> WorksFilter:
        """Filter by OA status (gold, green, hybrid, bronze, closed)."""
        if isinstance(status, str):
            status = [status]
        return self._add_filter("oa_status", status)

    def with_publication_date_range(
        self, from_date: date | None = None, to_date: date | None = None
    ) -> WorksFilter:
        """Filter by publication date range."""
        filters = {}
        if from_date:
            filters["from_publication_date"] = from_date
        if to_date:
            filters["to_publication_date"] = to_date

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}
        current_filter.update(filters)
        return self.model_copy(update={"filter": current_filter})

    def with_created_date_range(
        self, from_date: date | None = None, to_date: date | None = None
    ) -> WorksFilter:
        """Filter by created date range."""
        filters = {}
        if from_date:
            filters["from_created_date"] = from_date
        if to_date:
            filters["to_created_date"] = to_date

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}
        current_filter.update(filters)
        return self.model_copy(update={"filter": current_filter})

    def with_author_id(self, author_id: str | list[str]) -> WorksFilter:
        """Filter by author ID."""
        if isinstance(author_id, str):
            author_id = [author_id]
        return self._add_filter("author.id", author_id)

    def with_author_orcid(self, orcid: str) -> WorksFilter:
        """Filter by author ORCID."""
        return self._add_filter("author.orcid", orcid)

    def with_authorships_institutions_id(
        self, institution_id: str | list[str]
    ) -> WorksFilter:
        """Filter by authorship institution ID."""
        if isinstance(institution_id, str):
            institution_id = [institution_id]
        return self._add_filter("authorships.institutions.id", institution_id)

    def with_authorships_institutions_ror(self, ror: str) -> WorksFilter:
        """Filter by authorship institution ROR."""
        return self._add_filter("authorships.institutions.ror", ror)

    def with_authorships_institutions_country_code(
        self, country_code: str | list[str]
    ) -> WorksFilter:
        """Filter by authorship institution country code."""
        if isinstance(country_code, str):
            country_code = [country_code]
        return self._add_filter(
            "authorships.institutions.country_code", country_code
        )

    def with_authorships_institutions_type(
        self, institution_type: str | list[str]
    ) -> WorksFilter:
        """Filter by authorship institution type."""
        if isinstance(institution_type, str):
            institution_type = [institution_type]
        return self._add_filter(
            "authorships.institutions.type", institution_type
        )

    def with_corresponding_author_id(self, author_id: str) -> WorksFilter:
        """Filter by corresponding author ID."""
        return self._add_filter("corresponding_author_ids", author_id)

    def with_corresponding_institution_id(
        self, institution_id: str
    ) -> WorksFilter:
        """Filter by corresponding institution ID."""
        return self._add_filter("corresponding_institution_ids", institution_id)

    def with_institutions_id(
        self, institution_id: str | list[str]
    ) -> WorksFilter:
        """Filter by institution ID."""
        if isinstance(institution_id, str):
            institution_id = [institution_id]
        return self._add_filter("institutions.id", institution_id)

    def with_institutions_ror(self, ror: str) -> WorksFilter:
        """Filter by institution ROR."""
        return self._add_filter("institutions.ror", ror)

    def with_institutions_country_code(
        self, country_code: str | list[str]
    ) -> WorksFilter:
        """Filter by institution country code."""
        if isinstance(country_code, str):
            country_code = [country_code]
        return self._add_filter("institutions.country_code", country_code)

    def with_institutions_type(
        self, institution_type: str | list[str]
    ) -> WorksFilter:
        """Filter by institution type."""
        if isinstance(institution_type, str):
            institution_type = [institution_type]
        return self._add_filter("institutions.type", institution_type)

    def with_primary_location_source(self, source_id: str) -> WorksFilter:
        """Filter by primary location source ID."""
        return self._add_filter("primary_location.source.id", source_id)

    def with_primary_location_issn(self, issn: str) -> WorksFilter:
        """Filter by primary location ISSN."""
        return self._add_filter("primary_location.source.issn", issn)

    def with_primary_location_license(
        self, license: str | list[str]
    ) -> WorksFilter:
        """Filter by primary location license."""
        if isinstance(license, str):
            license = [license]
        return self._add_filter("primary_location.license", license)

    def with_repository(self, repository_id: str) -> WorksFilter:
        """Filter by repository ID."""
        return self._add_filter("repository", repository_id)

    def with_journal(self, journal_id: str) -> WorksFilter:
        """Filter by journal ID."""
        return self._add_filter("journal", journal_id)

    def with_concepts_id(self, concept_id: str | list[str]) -> WorksFilter:
        """Filter by concept ID."""
        if isinstance(concept_id, str):
            concept_id = [concept_id]
        return self._add_filter("concepts.id", concept_id)

    def with_primary_topic_id(self, topic_id: str) -> WorksFilter:
        """Filter by primary topic ID."""
        return self._add_filter("primary_topic.id", topic_id)

    def with_topics_id(self, topic_id: str | list[str]) -> WorksFilter:
        """Filter by topic ID."""
        if isinstance(topic_id, str):
            topic_id = [topic_id]
        return self._add_filter("topics.id", topic_id)

    def with_sustainable_development_goals_id(
        self, sdg_id: str | list[str]
    ) -> WorksFilter:
        """Filter by Sustainable Development Goals ID."""
        if isinstance(sdg_id, str):
            sdg_id = [sdg_id]
        return self._add_filter("sustainable_development_goals.id", sdg_id)

    def with_cited_by_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> WorksFilter:
        """Filter by cited by count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter(
                "cited_by_count", f"{min_count}-{max_count}"
            )
        if min_count is not None:
            return self._add_filter("cited_by_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("cited_by_count", f"<{max_count + 1}")
        return self

    def with_cites(self, work_id: str) -> WorksFilter:
        """Filter by works that cite the given work."""
        return self._add_filter("cites", work_id)

    def with_referenced_works(self, work_id: str) -> WorksFilter:
        """Filter by referenced works."""
        return self._add_filter("referenced_works", work_id)

    def with_related_to(self, work_id: str) -> WorksFilter:
        """Filter by related works."""
        return self._add_filter("related_to", work_id)

    def with_is_retracted(self, *, is_retracted: bool) -> WorksFilter:
        """Filter by retracted status."""
        return self._add_filter("is_retracted", is_retracted)

    def with_is_paratext(self, *, is_paratext: bool) -> WorksFilter:
        """Filter by paratext status."""
        return self._add_filter("is_paratext", is_paratext)

    def with_has_fulltext(self, *, has_fulltext: bool) -> WorksFilter:
        """Filter by fulltext availability."""
        return self._add_filter("has_fulltext", has_fulltext)

    def with_has_abstract(self, *, has_abstract: bool) -> WorksFilter:
        """Filter by abstract availability."""
        return self._add_filter("has_abstract", has_abstract)

    def with_has_doi(self, *, has_doi: bool) -> WorksFilter:
        """Filter by DOI availability."""
        return self._add_filter("has_doi", has_doi)

    def with_grants_funder(self, funder_id: str) -> WorksFilter:
        """Filter by grant funder ID."""
        return self._add_filter("grants.funder", funder_id)

    def with_grants_award_id(self, award_id: str) -> WorksFilter:
        """Filter by grant award ID."""
        return self._add_filter("grants.award_id", award_id)

    def with_apc_paid(self, *, apc_paid: bool) -> WorksFilter:
        """Filter by APC paid status."""
        return self._add_filter("apc_paid", apc_paid)

    def with_language(self, language: str | list[str]) -> WorksFilter:
        """Filter by language."""
        if isinstance(language, str):
            language = [language]
        return self._add_filter("language", language)


class AuthorsFilter(BaseFilter):
    """Filters specific to authors endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        pattern="^(display_name|cited_by_count|works_count|publication_date)(:(asc|desc))?$",
    )

    def _add_filter(self, key: str, value: Any) -> AuthorsFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_orcid(self, orcid: str) -> AuthorsFilter:
        """Filter by ORCID."""
        return self._add_filter("orcid", orcid)

    def with_display_name_search(self, name: str) -> AuthorsFilter:
        """Filter by display name search."""
        return self._add_filter("display_name.search", name)

    def with_works_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> AuthorsFilter:
        """Filter by works count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter("works_count", f"{min_count}-{max_count}")
        if min_count is not None:
            return self._add_filter("works_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("works_count", f"<{max_count + 1}")
        return self

    def with_cited_by_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> AuthorsFilter:
        """Filter by cited by count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter(
                "cited_by_count", f"{min_count}-{max_count}"
            )
        if min_count is not None:
            return self._add_filter("cited_by_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("cited_by_count", f"<{max_count + 1}")
        return self

    def with_last_known_institution_id(
        self, institution_id: str
    ) -> AuthorsFilter:
        """Filter by last known institution ID."""
        return self._add_filter("last_known_institution.id", institution_id)

    def with_last_known_institution_ror(self, ror: str) -> AuthorsFilter:
        """Filter by last known institution ROR."""
        return self._add_filter("last_known_institution.ror", ror)

    def with_last_known_institution_country_code(
        self, country_code: str
    ) -> AuthorsFilter:
        """Filter by last known institution country code."""
        return self._add_filter(
            "last_known_institution.country_code", country_code
        )

    def with_last_known_institution_type(
        self, institution_type: str
    ) -> AuthorsFilter:
        """Filter by last known institution type."""
        return self._add_filter("last_known_institution.type", institution_type)

    def with_x_concepts_id(self, concept_id: str | list[str]) -> AuthorsFilter:
        """Filter by associated concept ID."""
        if isinstance(concept_id, str):
            concept_id = [concept_id]
        return self._add_filter("x_concepts.id", concept_id)


class InstitutionsFilter(BaseFilter):
    """Filters specific to institutions endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        pattern="^(display_name|cited_by_count|works_count)(:(asc|desc))?$",
    )

    def _add_filter(self, key: str, value: Any) -> InstitutionsFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_ror(self, ror: str) -> InstitutionsFilter:
        """Filter by ROR ID."""
        return self._add_filter("ror", ror)

    def with_country_code(
        self, country_code: str | list[str]
    ) -> InstitutionsFilter:
        """Filter by country code."""
        if isinstance(country_code, str):
            country_code = [country_code]
        return self._add_filter("country_code", country_code)

    def with_type(
        self, institution_type: str | list[str]
    ) -> InstitutionsFilter:
        """Filter by institution type."""
        if isinstance(institution_type, str):
            institution_type = [institution_type]
        return self._add_filter("type", institution_type)

    def with_works_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> InstitutionsFilter:
        """Filter by works count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter("works_count", f"{min_count}-{max_count}")
        if min_count is not None:
            return self._add_filter("works_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("works_count", f"<{max_count + 1}")
        return self

    def with_x_concepts_id(self, concept_id: str) -> InstitutionsFilter:
        """Filter by associated concept ID."""
        return self._add_filter("x_concepts.id", concept_id)


class SourcesFilter(BaseFilter):
    """Filters specific to sources endpoint."""

    def _add_filter(self, key: str, value: Any) -> SourcesFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_issn(self, issn: str) -> SourcesFilter:
        """Filter by ISSN."""
        return self._add_filter("issn", issn)

    def with_publisher(self, publisher_id: str) -> SourcesFilter:
        """Filter by publisher ID."""
        return self._add_filter("publisher", publisher_id)

    def with_type(self, source_type: str | list[str]) -> SourcesFilter:
        """Filter by source type."""
        if isinstance(source_type, str):
            source_type = [source_type]
        return self._add_filter("type", source_type)

    def with_is_oa(self, *, is_oa: bool) -> SourcesFilter:
        """Filter by open access status."""
        return self._add_filter("is_oa", is_oa)

    def with_is_in_doaj(self, *, is_in_doaj: bool) -> SourcesFilter:
        """Filter by DOAJ inclusion."""
        return self._add_filter("is_in_doaj", is_in_doaj)

    def with_apc_usd_range(
        self, min_amount: int | None = None, max_amount: int | None = None
    ) -> SourcesFilter:
        """Filter by APC USD range."""
        if min_amount is not None and max_amount is not None:
            return self._add_filter("apc_usd", f"{min_amount}-{max_amount}")
        if min_amount is not None:
            return self._add_filter("apc_usd", f">{min_amount - 1}")
        if max_amount is not None:
            return self._add_filter("apc_usd", f"<{max_amount + 1}")
        return self


class ConceptsFilter(BaseFilter):
    """Filters specific to concepts endpoint."""

    def _add_filter(self, key: str, value: Any) -> ConceptsFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_level(self, level: int | list[int]) -> ConceptsFilter:
        """Filter by concept level."""
        if isinstance(level, int):
            level = [level]
        return self._add_filter("level", level)

    def with_ancestors_id(self, ancestor_id: str) -> ConceptsFilter:
        """Filter by ancestor concept ID."""
        return self._add_filter("ancestors.id", ancestor_id)

    def with_works_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> ConceptsFilter:
        """Filter by works count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter("works_count", f"{min_count}-{max_count}")
        if min_count is not None:
            return self._add_filter("works_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("works_count", f"<{max_count + 1}")
        return self


class PublishersFilter(BaseFilter):
    """Filters specific to publishers endpoint."""

    def _add_filter(self, key: str, value: Any) -> PublishersFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_country_codes(
        self, country_codes: str | list[str]
    ) -> PublishersFilter:
        """Filter by country codes."""
        if isinstance(country_codes, str):
            country_codes = [country_codes]
        return self._add_filter("country_codes", country_codes)

    def with_parent_publisher(self, publisher_id: str) -> PublishersFilter:
        """Filter by parent publisher ID."""
        return self._add_filter("parent_publisher", publisher_id)

    def with_hierarchy_level(self, level: int) -> PublishersFilter:
        """Filter by hierarchy level."""
        return self._add_filter("hierarchy_level", level)


class FundersFilter(BaseFilter):
    """Filters specific to funders endpoint."""

    def _add_filter(self, key: str, value: Any) -> FundersFilter:
        """Helper to add a filter."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter[key] = value
        return self.model_copy(update={"filter": current_filter})

    def with_country_code(self, country_code: str) -> FundersFilter:
        """Filter by country code."""
        return self._add_filter("country_code", country_code)

    def with_grants_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> FundersFilter:
        """Filter by grants count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter("grants_count", f"{min_count}-{max_count}")
        if min_count is not None:
            return self._add_filter("grants_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("grants_count", f"<{max_count + 1}")
        return self

    def with_works_count_range(
        self, min_count: int | None = None, max_count: int | None = None
    ) -> FundersFilter:
        """Filter by works count range."""
        if min_count is not None and max_count is not None:
            return self._add_filter("works_count", f"{min_count}-{max_count}")
        if min_count is not None:
            return self._add_filter("works_count", f">{min_count - 1}")
        if max_count is not None:
            return self._add_filter("works_count", f"<{max_count + 1}")
        return self
