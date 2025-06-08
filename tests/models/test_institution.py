from __future__ import annotations

from openalex.models import Institution, InstitutionType


class TestInstitution:
    """Test Institution model."""

    def test_institution_creation(self) -> None:
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
        institution = Institution(
            id="I123",
            display_name="Department",
            lineage=["I999", "I456", "I123"],
        )

        assert institution.parent_institution == "I456"
        assert institution.root_institution == "I999"
