from __future__ import annotations

from openalex.models import Concept


class TestConceptModel:
    """Test Concept model."""

    def test_concept_hierarchy(self) -> None:
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
