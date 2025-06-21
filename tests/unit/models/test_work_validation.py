"""Tests for Work model validation."""

from datetime import date

import pytest
from pydantic import ValidationError

from openalex.models.work import Work, WorkIds


@pytest.mark.unit
class TestWorkValidation:
    """Test Work model validation."""

    def test_doi_validation(self):
        """Test DOI format validation."""
        # Valid DOIs
        valid_dois = [
            "10.1234/example.doi",
            "10.1038/nature12373",
            "https://doi.org/10.1234/test",
            "http://doi.org/10.1234/test",
        ]

        for doi in valid_dois:
            work_data = {
                "id": "https://openalex.org/W123",
                "display_name": "Test",
                "doi": doi,
            }
            work = Work(**work_data)
            assert work.doi == doi

        invalid_dois = [
            "not-a-doi",
            "11.1234/test",
            "10.1234",
        ]

        for doi in invalid_dois:
            work_data = {
                "id": "https://openalex.org/W123",
                "display_name": "Test",
                "doi": doi,
            }
            with pytest.raises(ValidationError, match="Invalid DOI format"):
                Work(**work_data)

    def test_date_validation(self):
        """Test date field validation."""
        valid_dates = [
            ("2023-01-15", date(2023, 1, 15)),
            ("2023/01/15", date(2023, 1, 15)),
            ("15/01/2023", date(2023, 1, 15)),
            (date(2023, 1, 15), date(2023, 1, 15)),
        ]

        for date_str, expected in valid_dates:
            work_data = {
                "id": "https://openalex.org/W123",
                "display_name": "Test",
                "publication_date": date_str,
            }
            work = Work(**work_data)
            assert work.publication_date == expected

        work_data = {
            "id": "https://openalex.org/W123",
            "display_name": "Test",
            "publication_date": "invalid",
        }
        with pytest.raises(ValidationError, match="Unable to parse date"):
            Work(**work_data)

    def test_language_validation(self):
        """Test language code validation."""
        valid_langs = ["en", "es", "fr", "EN", "ES"]

        for lang in valid_langs:
            work_data = {
                "id": "https://openalex.org/W123",
                "display_name": "Test",
                "language": lang,
            }
            work = Work(**work_data)
            assert work.language == lang.lower()

        invalid_langs = ["eng", "english", "e", "123"]

        for lang in invalid_langs:
            work_data = {
                "id": "https://openalex.org/W123",
                "display_name": "Test",
                "language": lang,
            }
            with pytest.raises(ValidationError, match="Invalid language code"):
                Work(**work_data)

    def test_page_range_validation(self):
        """Test page range validation."""
        work_data = {
            "id": "https://openalex.org/W123",
            "display_name": "Test",
            "first_page": "100",
            "last_page": "150",
        }
        work = Work(**work_data)
        assert work.first_page == "100"
        assert work.last_page == "150"

        work_data["first_page"] = "200"
        work_data["last_page"] = "150"
        with pytest.raises(ValidationError, match="Invalid page range"):
            Work(**work_data)

        work_data["first_page"] = "S100"
        work_data["last_page"] = "S150"
        work = Work(**work_data)

    def test_citation_count_validation(self):
        """Test citation count validation."""
        work_data = {
            "id": "https://openalex.org/W123",
            "display_name": "Test",
            "cited_by_count": 100,
            "referenced_works_count": 50,
        }
        work = Work(**work_data)
        assert work.cited_by_count == 100

        work_data["cited_by_count"] = -1
        with pytest.raises(ValidationError, match="cannot be negative"):
            Work(**work_data)

        work_data["cited_by_count"] = 0
        work_data["referenced_works_count"] = -5
        with pytest.raises(ValidationError, match="cannot be negative"):
            Work(**work_data)

    def test_bibliographic_info_cleanup(self):
        """Test bibliographic field cleanup."""
        work_data = {
            "id": "https://openalex.org/W123",
            "display_name": "Test",
            "volume": "  12  ",
            "issue": " ",
            "first_page": "100",
            "last_page": "",
        }

        work = Work(**work_data)
        assert work.volume == "12"
        assert work.issue is None
        assert work.first_page == "100"
        assert work.last_page is None


class TestWorkIdsValidation:
    """Test WorkIds model validation."""

    def test_doi_normalization(self):
        """Test DOI normalization to lowercase."""
        ids = WorkIds(doi="10.1234/EXAMPLE.DOI")
        assert ids.doi == "10.1234/example.doi"

    def test_pubmed_id_validation(self):
        """Test PubMed ID validation."""
        valid_ids = [
            ("12345678", "pmid"),
            ("PMC1234567", "pmcid"),
        ]

        for id_val, field in valid_ids:
            ids = WorkIds(**{field: id_val})
            assert getattr(ids, field) == id_val

        with pytest.raises(ValidationError, match="Invalid PMID format"):
            WorkIds(pmid="ABC123")

        with pytest.raises(ValidationError, match="Invalid PMC ID format"):
            WorkIds(pmcid="123456")

        with pytest.raises(ValidationError, match="Invalid PMC ID format"):
            WorkIds(pmcid="PMCABC")
