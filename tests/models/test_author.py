from __future__ import annotations

from typing import Any

from openalex.models import Author


class TestAuthor:
    """Test Author model."""

    def test_author_creation(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        author = Author(**mock_author_response)

        assert author.id == "https://openalex.org/A123456"
        assert author.display_name == "John P. Perdew"
        assert str(author.orcid) == "https://orcid.org/0000-0003-4237-824X"
        assert author.works_count == 500
        assert author.cited_by_count == 100000

    def test_author_summary_stats(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        author = Author(**mock_author_response)

        assert author.h_index == 120
        assert author.i10_index == 450
        assert author.summary_stats.two_year_mean_citedness == 5.2

    def test_author_affiliations(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        author = Author(**mock_author_response)

        assert len(author.affiliations) == 1
        affiliation = author.affiliations[0]
        assert affiliation.institution.display_name == "Tulane University"
        assert affiliation.years == [2020, 2021, 2022, 2023]

    def test_author_helper_methods(
        self, mock_author_response: dict[str, Any]
    ) -> None:
        author = Author(**mock_author_response)

        assert author.works_in_year(2023) == 10
        assert author.citations_in_year(2023) == 5000
        assert author.active_years() == [2022, 2023]
        assert author.institution_names() == ["Tulane University"]
