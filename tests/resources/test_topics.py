"""Tests for Topics resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from openalex.models import Topic, TopicLevel

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import AsyncTopicsResource, TopicsResource


class TestTopicsResource(BaseResourceTest[Topic]):
    """Test Topics resource functionality."""

    resource_name: ClassVar[str] = "topics"
    entity_class: ClassVar[type[Topic]] = Topic
    sample_id: ClassVar[str] = "T10001"
    sample_ids: ClassVar[list[str]] = ["T10001", "T10002", "T10003"]

    def get_resource(self, client: OpenAlex) -> TopicsResource:
        """Get topics resource."""
        return client.topics

    def get_async_resource(self, client: AsyncOpenAlex) -> AsyncTopicsResource:
        """Get async topics resource."""
        return client.topics

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample topic data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "display_name": "Machine Learning",
            "works_count": 500000,
            "cited_by_count": 10000000,
            "summary_stats": {
                "2yr_mean_citedness": 5.5,
                "h_index": 350,
                "i10_index": 100000,
            },
            "description": "Machine learning is a field of artificial intelligence...",
            "keywords": [
                "neural networks",
                "deep learning",
                "artificial intelligence",
                "supervised learning",
                "unsupervised learning",
            ],
            "domain": {
                "id": "https://openalex.org/D1",
                "display_name": "Physical Sciences",
            },
            "field": {
                "id": "https://openalex.org/F1",
                "display_name": "Computer Science",
            },
            "subfield": {
                "id": "https://openalex.org/S1",
                "display_name": "Artificial Intelligence",
            },
            "sisters": [
                {
                    "id": "https://openalex.org/T10002",
                    "display_name": "Computer Vision",
                },
                {
                    "id": "https://openalex.org/T10003",
                    "display_name": "Natural Language Processing",
                },
            ],
            "works_api_url": f"https://api.openalex.org/works?filter=topics.id:{self.sample_id}",
            "updated_date": "2024-01-01",
            "created_date": "2023-01-01",
        }

    # Topic-specific tests
    def test_topic_hierarchy(self) -> None:
        """Test topic hierarchy levels."""
        topic_data = self.get_sample_entity()
        topic = Topic(**topic_data)

        assert topic.level == TopicLevel.SUBFIELD
        expected_path = (
            "Physical Sciences > Computer Science > Artificial Intelligence"
        )
        assert topic.hierarchy_path == expected_path

    def test_filter_by_domain(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering topics by domain."""
        domain_response = self.get_list_response(count=100)

        httpx_mock.add_response(
            url="https://api.openalex.org/topics?filter=domain.id%3AD1&mailto=test%40example.com",
            json=domain_response,
        )

        physical_sciences_topics = client.topics.list(
            filter={"domain.id": "D1"}
        )
        assert physical_sciences_topics.meta.count == 100

    def test_filter_by_field(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering topics by field."""
        field_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url="https://api.openalex.org/topics?filter=field.id%3AF1&mailto=test%40example.com",
            json=field_response,
        )

        cs_topics = client.topics.list(filter={"field.id": "F1"})
        assert cs_topics.meta.count == 50

    def test_filter_by_subfield(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering topics by subfield."""
        subfield_response = self.get_list_response(count=20)

        httpx_mock.add_response(
            url="https://api.openalex.org/topics?filter=subfield.id%3AS1&mailto=test%40example.com",
            json=subfield_response,
        )

        ai_topics = client.topics.list(filter={"subfield.id": "S1"})
        assert ai_topics.meta.count == 20

    def test_topic_keywords(self) -> None:
        """Test topic keyword functionality."""
        topic_data = self.get_sample_entity()
        topic = Topic(**topic_data)

        assert topic.has_keyword("neural networks") is True
        assert topic.has_keyword("deep learning") is True
        assert topic.has_keyword("blockchain") is False
        assert len(topic.keywords) == 5

    def test_sister_topics(self) -> None:
        """Test sister topic relationships."""
        topic_data = self.get_sample_entity()
        topic = Topic(**topic_data)

        assert len(topic.sisters) == 2
        sister_names = [s.display_name for s in topic.sisters]
        assert "Computer Vision" in sister_names
        assert "Natural Language Processing" in sister_names

    def test_search_topics_by_keyword(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test searching topics by keyword."""
        keyword_response = self.get_list_response(count=10)

        httpx_mock.add_response(
            url="https://api.openalex.org/topics?filter=keywords.keyword%3Aneural+networks&mailto=test%40example.com",
            json=keyword_response,
        )

        neural_topics = client.topics.list(
            filter={"keywords.keyword": "neural networks"}
        )
        assert neural_topics.meta.count == 10

    def test_topic_works_count_filter(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering topics by works count."""
        popular_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url="https://api.openalex.org/topics?filter=works_count%3A%3E100000&mailto=test%40example.com",
            json=popular_response,
        )

        popular_topics = client.topics.list(filter={"works_count": ">100000"})
        assert popular_topics.meta.count == 50

    def test_domain_level_topics(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting domain-level topics."""
        domain_data = self.get_sample_entity()
        domain_data.update(
            {
                "display_name": "Physical Sciences",
                "field": None,
                "subfield": None,
            }
        )

        domain_topic = Topic(**domain_data)
        assert domain_topic.level == TopicLevel.DOMAIN
        assert domain_topic.hierarchy_path == "Physical Sciences"

    def test_field_level_topics(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting field-level topics."""
        field_data = self.get_sample_entity()
        field_data.update(
            {
                "display_name": "Computer Science",
                "subfield": None,
            }
        )

        field_topic = Topic(**field_data)
        assert field_topic.level == TopicLevel.FIELD
        assert (
            field_topic.hierarchy_path == "Physical Sciences > Computer Science"
        )
