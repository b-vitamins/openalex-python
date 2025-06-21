"""
Test entity classes behavior with proper API response mocking.
Focuses on expected behavior, not internal implementation.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.behavior
class TestEntityBehavior:
    """Test entity classes interact correctly with the API."""

    def test_works_entity_fetches_single_work(self, mock_work_data):
        """Works entity should fetch and parse single work correctly."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_work_data)
            )

            work = Works().get("W2741809807")

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/works/W2741809807")

            # Verify parsed correctly
            assert work.id == "https://openalex.org/W2741809807"
            assert (
                work.title
                == "The state of OA: a large-scale analysis of the prevalence and impact of Open Access articles"
            )
            assert work.publication_year == 2018
            assert work.cited_by_count == 962

    def test_authors_entity_searches_correctly(self, mock_author_data):
        """Authors entity should search and return author list."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [mock_author_data],
                        "meta": {"count": 1},
                    }
                ),
            )

            results = Authors().search("Jason Priem").get()

            _, kwargs = mock_request.call_args
            assert kwargs["params"]["search"] == "Jason Priem"

            assert len(results.results) == 1
            author = results.results[0]
            assert author.display_name == "Jason Priem"
            assert author.orcid == "https://orcid.org/0000-0001-6187-6610"

    def test_institutions_entity_filters_by_country(
        self, mock_institution_data
    ):
        """Institutions entity should filter by country code."""
        from openalex import Institutions

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [mock_institution_data],
                        "meta": {"count": 1},
                    }
                ),
            )

            results = Institutions().filter(country_code="US").get()

            _, kwargs = mock_request.call_args
            assert "filter" in kwargs["params"]
            assert "country_code:US" in kwargs["params"]["filter"]

            institution = results.results[0]
            assert institution.country_code == "US"
            assert institution.display_name == "University of Michigan"

    def test_sources_entity_gets_journal_details(self, mock_source_data):
        """Sources entity should fetch source/journal details."""
        from openalex import Sources

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_source_data)
            )

            source = Sources().get("S137773608")

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/sources/S137773608")

            assert source.display_name == "Nature"
            assert source.issn_l == "0028-0836"
            assert source.type == "journal"

    def test_concepts_entity_gets_concept_hierarchy(self, mock_concept_data):
        """Concepts entity should fetch concept with hierarchy info."""
        from openalex import Concepts

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_concept_data)
            )

            concept = Concepts().get("C71924100")

            assert concept.display_name == "Medicine"
            assert concept.level == 0  # Top level
            assert concept.works_count == 65001994

    def test_publishers_entity_filters_by_works_count(
        self, mock_publisher_data
    ):
        """Publishers entity should support filtering by metrics."""
        from openalex import Publishers

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [mock_publisher_data],
                        "meta": {"count": 1},
                    }
                ),
            )

            results = Publishers().filter_gt(works_count=1000000).get()

            _, kwargs = mock_request.call_args
            assert "filter" in kwargs["params"]
            assert "works_count:>1000000" in kwargs["params"]["filter"]

            publisher = results.results[0]
            assert publisher.works_count > 1000000

    def test_funders_entity_autocomplete(self, mock_funder_data):
        """Funders entity should support autocomplete search."""
        from openalex import Funders

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [
                            {
                                "id": mock_funder_data["id"],
                                "display_name": mock_funder_data[
                                    "display_name"
                                ],
                                "entity_type": "funder",
                                "cited_by_count": mock_funder_data[
                                    "cited_by_count"
                                ],
                            }
                        ],
                        "meta": {"count": 1},
                    }
                ),
            )

            results = Funders().autocomplete("National Institutes")

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/autocomplete/funders")
            assert kwargs["params"]["q"] == "National Institutes"

            assert len(results.results) == 1

    def test_topics_entity_groups_by_domain(self, mock_topic_data):
        """Topics entity should support grouping."""
        from openalex import Topics

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "group_by": [
                            {"key": "Health Sciences", "count": 150},
                            {"key": "Life Sciences", "count": 120},
                        ],
                        "meta": {"count": 270},
                    }
                ),
            )

            results = Topics().group_by("domain.display_name").get()

            _, kwargs = mock_request.call_args
            assert kwargs["params"]["group-by"] == "domain.display_name"

            assert len(results.groups) == 2
            assert results.groups[0].key == "Health Sciences"
            assert results.groups[0].count == 150

    def test_entity_pagination_follows_cursor(self, mock_work_data):
        """Entities should follow cursor-based pagination."""
        from openalex import Works

        # First page
        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [mock_work_data],
                        "meta": {
                            "count": 100,
                            "page": 1,
                            "per_page": 1,
                            "next_cursor": "next123",
                        },
                    }
                ),
            )

            paginator = Works().filter(is_oa=True).paginate(per_page=1)
            first_page = next(paginator)

            assert len(first_page.results) == 1
            assert first_page.meta.next_cursor == "next123"

    def test_entity_all_iterates_through_results(self, mock_work_data):
        """Entity.all() should iterate through all pages."""
        from openalex import Works

        call_count = 0

        def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                return Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "results": [mock_work_data],
                            "meta": {
                                "count": 2,
                                "page": 1,
                                "next_cursor": "page2",
                            },
                        }
                    ),
                )
            else:
                return Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "results": [mock_work_data],
                            "meta": {
                                "count": 2,
                                "page": 2,
                                "next_cursor": None,
                            },
                        }
                    ),
                )

        with patch("httpx.Client.request", side_effect=mock_response):
            works = list(Works().filter(is_oa=True).all())

            assert len(works) == 2
            assert call_count == 2

    def test_entity_random_returns_random_item(self, mock_author_data):
        """Entity.random() should return a random item."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_author_data)
            )

            author = Authors().random()

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/authors/random")
            assert author.display_name == "Jason Priem"

    def test_keywords_entity_handles_special_id_format(self):
        """Keywords entity should handle keywords/ prefix in IDs."""
        from openalex import Keywords

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "id": "https://openalex.org/keywords/machine-learning",
                        "display_name": "Machine Learning",
                    }
                ),
            )

            keyword = Keywords().get("machine-learning")

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/keywords/machine-learning")
            assert keyword.display_name == "Machine Learning"

    def test_entity_select_reduces_response_size(self, mock_work_data):
        """Select should only request specified fields."""
        from openalex import Works

        # Simulate reduced response
        reduced_data = {
            "id": mock_work_data["id"],
            "title": mock_work_data["title"],
            "cited_by_count": mock_work_data["cited_by_count"],
        }

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [reduced_data],
                        "meta": {"count": 1},
                    }
                ),
            )

            results = Works().select(["id", "title", "cited_by_count"]).get()

            _, kwargs = mock_request.call_args
            assert kwargs["params"]["select"] == "id,title,cited_by_count"

            work = results.results[0]
            # Should still parse with reduced fields
            assert work.id == mock_work_data["id"]
            assert work.title == mock_work_data["title"]
