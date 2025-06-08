from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import OpenAccessStatus, Work, WorkType


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
