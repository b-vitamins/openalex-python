"""Tests for OpenAlex models."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    Author,
    BaseFilter,
    Concept,
    Institution,
    InstitutionType,
    ListResult,
    Meta,
    OpenAccessStatus,
    Source,
    SourceType,
    Topic,
    Work,
    WorksFilter,
    WorkType,
)


class TestWork:
    """Test Work model."""

    def test_work_creation(self, mock_work_response: dict[str, Any]) -> None:
        """Test creating a work from API response."""
        work = Work(**mock_work_response)

        assert work.id == "https://openalex.org/W2741809807"
        assert work.title == "Generalized Gradient Approximation Made Simple"
        assert work.publication_year == 1996
        assert work.publication_date == date(1996, 10, 28)
        assert work.cited_by_count == 50000
        assert work.type == WorkType.ARTICLE

    def test_work_open_access(self, mock_work_response: dict[str, Any]) -> None:
        """Test work open access information."""
        work = Work(**mock_work_response)

        assert work.open_access is not None
        assert work.open_access.is_oa is True
        assert work.open_access.oa_status == OpenAccessStatus.BRONZE
        assert str(work.open_access.oa_url) == "https://example.com/paper.pdf"

    def test_work_authorships(self, mock_work_response: dict[str, Any]) -> None:
        """Test work authorships."""
        work = Work(**mock_work_response)

        assert len(work.authorships) == 1
        authorship = work.authorships[0]
        assert authorship.author_position == "first"
        assert authorship.author.display_name == "John P. Perdew"
        assert authorship.is_corresponding is True
        assert len(authorship.institutions) == 1
        assert authorship.institutions[0].display_name == "Tulane University"

    def test_work_abstract_reconstruction(self) -> None:
        """Test abstract reconstruction from inverted index."""
        work = Work(
            id="W123",
            display_name="Test Work",
            abstract_inverted_index={
                "This": [0],
                "is": [1, 5],
                "a": [2, 6],
                "test": [3, 7],
                "abstract.": [4],
                "It": [8],
                "test.": [9],
            },
        )

        abstract = work.abstract
        assert abstract == "This is a test abstract. is a test It test."

    def test_work_no_abstract(self) -> None:
        """Test work without abstract."""
        work = Work(
            id="W123",
            display_name="Test Work",
            abstract_inverted_index=None,
        )

        assert work.abstract is None

    def test_work_validation_error(self) -> None:
        """Test work validation errors."""
        with pytest.raises(ValidationError):
            Work()  # Missing required fields


class TestAuthor:
    """Test Author model."""

    def test_author_creation(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        """Test creating an author from API response."""
        author = Author(**mock_author_response)

        assert author.id == "https://openalex.org/A123456"
        assert author.display_name == "John P. Perdew"
        assert str(author.orcid) == "https://orcid.org/0000-0003-4237-824X"
        assert author.works_count == 500
        assert author.cited_by_count == 100000

    def test_author_summary_stats(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        """Test author summary statistics."""
        author = Author(**mock_author_response)

        assert author.h_index == 120
        assert author.i10_index == 450
        assert author.summary_stats.two_year_mean_citedness == 5.2

    def test_author_affiliations(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        """Test author affiliations."""
        author = Author(**mock_author_response)

        assert len(author.affiliations) == 1
        affiliation = author.affiliations[0]
        assert affiliation.institution.display_name == "Tulane University"
        assert affiliation.years == [2020, 2021, 2022, 2023]

    def test_author_helper_methods(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        """Test author helper methods."""
        author = Author(**mock_author_response)

        assert author.works_in_year(2023) == 10
        assert author.citations_in_year(2023) == 5000
        assert author.active_years() == [2022, 2023]
        assert author.institution_names() == ["Tulane University"]


class TestInstitution:
    """Test Institution model."""

    def test_institution_creation(self) -> None:
        """Test creating an institution."""
        institution = Institution(
            id="I123",
            display_name="Test University",
            type=InstitutionType.EDUCATION,
            country_code="US",
            works_count=1000,
            cited_by_count=50000,
        )

        assert institution.display_name == "Test University"
        assert institution.is_education is True
        assert institution.is_company is False

    def test_institution_hierarchy(self) -> None:
        """Test institution hierarchy."""
        institution = Institution(
            id="I123",
            display_name="Department",
            lineage=["I999", "I456", "I123"],
        )

        assert institution.parent_institution == "I456"
        assert institution.root_institution == "I999"


class TestFilters:
    """Test filter models."""

    def test_base_filter(self) -> None:
        """Test base filter functionality."""
        filter = BaseFilter(
            search="machine learning",
            sort="cited_by_count:desc",
            page=2,
            per_page=50,
        )

        params = filter.to_params()
        assert params["search"] == "machine learning"
        assert params["sort"] == "cited_by_count:desc"
        assert params["page"] == 2
        assert params["per-page"] == 50

    def test_filter_with_dict(self) -> None:
        """Test filter with dictionary."""
        filter = BaseFilter(
            filter={
                "is_oa": True,
                "publication_year": [2020, 2021, 2022],
                "type": "article",
            }
        )

        params = filter.to_params()
        assert "is_oa:true" in params["filter"]
        assert "publication_year:2020|2021|2022" in params["filter"]
        assert "type:article" in params["filter"]

    def test_works_filter(self) -> None:
        """Test works-specific filter."""
        filter = WorksFilter()
        filter = filter.with_publication_year([2020, 2021])
        filter = filter.with_type("article")
        filter = filter.with_open_access(True)

        params = filter.to_params()
        filter_str = params["filter"]
        assert "publication_year:2020|2021" in filter_str
        assert "type:article" in filter_str
        assert "is_oa:true" in filter_str

    def test_filter_validation(self) -> None:
        """Test filter validation."""
        # Valid sort for works
        filter = WorksFilter(sort="publication_date:desc")
        assert filter.sort == "publication_date:desc"

        # Invalid sort for works
        with pytest.raises(ValidationError):
            WorksFilter(sort="invalid_field:desc")


class TestListResult:
    """Test ListResult model."""

    def test_list_result_creation(
        self, mock_list_response: dict[str, Any]
    ) -> None:
        """Test creating a list result."""
        result = ListResult[Work](
            meta=Meta(**mock_list_response["meta"]),
            results=[Work(**r) for r in mock_list_response["results"]],
        )

        assert result.meta.count == 100
        assert result.meta.page == 1
        assert len(result.results) == 1
        assert (
            result.results[0].title
            == "Generalized Gradient Approximation Made Simple"
        )


class TestConceptModel:
    """Test Concept model."""

    def test_concept_hierarchy(self) -> None:
        """Test concept hierarchy."""
        concept = Concept(
            id="C123",
            display_name="Machine Learning",
            level=2,
            ancestors=[
                {"id": "C1", "display_name": "Science", "level": 0},
                {"id": "C2", "display_name": "Computer Science", "level": 1},
            ],
        )

        assert concept.is_top_level is False
        assert concept.parent_concept.display_name == "Computer Science"
        assert concept.ancestor_names() == ["Science", "Computer Science"]


class TestTopicModel:
    """Test Topic model."""

    def test_topic_hierarchy(self) -> None:
        """Test topic hierarchy."""
        topic = Topic(
            id="T123",
            display_name="Deep Learning",
            domain={"id": "D1", "display_name": "Physical Sciences"},
            field={"id": "F1", "display_name": "Computer Science"},
            subfield={"id": "S1", "display_name": "Artificial Intelligence"},
            keywords=["neural networks", "machine learning", "AI"],
        )

        expected_path = (
            "Physical Sciences > Computer Science > Artificial Intelligence"
        )
        assert topic.hierarchy_path == expected_path
        assert topic.level == 2
        assert topic.has_keyword("neural networks") is True
        assert topic.has_keyword("blockchain") is False


class TestSourceModel:
    """Test Source model."""

    def test_source_creation(self) -> None:
        """Test creating a source."""
        source = Source(
            id="S123",
            display_name="Nature",
            type=SourceType.JOURNAL,
            issn_l="0028-0836",
            issn=["0028-0836", "1476-4687"],
            is_oa=False,
            apc_usd=3000,
        )

        assert source.is_journal is True
        assert source.is_conference is False
        assert source.has_apc is True
        assert source.all_issns() == ["0028-0836", "1476-4687"]

    def test_source_apc_prices(self) -> None:
        """Test source APC prices."""
        source = Source(
            id="S123",
            display_name="Test Journal",
            apc_prices=[
                {"price": 3000, "currency": "USD"},
                {"price": 2500, "currency": "EUR"},
                {"price": 2200, "currency": "GBP"},
            ],
        )

        assert source.get_apc_in_currency("USD") == 3000
        assert source.get_apc_in_currency("EUR") == 2500
        assert source.get_apc_in_currency("JPY") is None
