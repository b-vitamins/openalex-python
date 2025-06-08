from __future__ import annotations

from openalex.models import Topic


class TestTopicModel:
    """Test Topic model."""

    def test_topic_hierarchy(self) -> None:
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
