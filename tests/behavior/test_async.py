"""
Test async functionality behavior with proper mocking.
Tests async operations work correctly, not implementation details.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock


@pytest.mark.asyncio
class TestAsyncBehavior:
    """Test async client behavior matches sync behavior."""

    async def test_async_client_fetches_single_entity(self, mock_work_data):
        """Async client should fetch entities like sync client."""
        from openalex import AsyncWorks

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_work_data)
            )

            works = AsyncWorks()
            work = await works.get("W2741809807")

            assert work.id == "https://openalex.org/W2741809807"
            assert work.title == mock_work_data["title"]

    async def test_async_search_returns_results(self, mock_author_data):
        """Async search should return paginated results."""
        from openalex import AsyncAuthors

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [mock_author_data],
                        "meta": {"count": 1},
                    }
                ),
            )

            authors = AsyncAuthors()
            results = await authors.search("Jason Priem").get()

            assert len(results.results) == 1
            assert results.results[0].display_name == "Jason Priem"

    async def test_async_filter_chains_correctly(self):
        """Async filter chains should build correct parameters."""
        from openalex import AsyncInstitutions

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}}),
            )

            institutions = AsyncInstitutions()
            await (
                institutions.filter(country_code="US")
                .filter_gt(works_count=1000)
                .sort(cited_by_count="desc")
                .get()
            )

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert "country_code:US" in params["filter"]
            assert "works_count:>1000" in params["filter"]
            assert params["sort"] == "cited_by_count:desc"

    async def test_async_pagination_iterates_all_results(
        self, mock_source_data
    ):
        """Async pagination should iterate through all pages."""
        from openalex import AsyncAuthors

        async def mock_response(*args, **kwargs):
            cursor = kwargs["params"].get("cursor")
            if cursor is None:
                page = 1
            elif cursor == "next":
                page = 2
            else:
                page = int(kwargs["params"].get("page", 1))

            if page <= 2:
                return Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "results": [{"id": f"A{page}"}],
                            "meta": {
                                "count": 2,
                                "page": page,
                                "next_cursor": "next" if page < 2 else None,
                            },
                        }
                    ),
                )
            else:
                return Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "results": [],
                            "meta": {
                                "count": 2,
                                "page": page,
                                "next_cursor": None,
                            },
                        }
                    ),
                )

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = mock_response

            authors = AsyncAuthors()
            all_authors = []

            async for author in authors.filter(works_count=">10").all():
                all_authors.append(author)

            assert len(all_authors) == 2
            assert all_authors[0].id == "A1"
            assert all_authors[1].id == "A2"

    async def test_async_concurrent_requests_execute_in_parallel(self):
        """Multiple async requests should execute concurrently."""
        from openalex import AsyncWorks
        import time

        call_times = []

        async def mock_response(*args, **kwargs):
            call_times.append(time.time())
            # Simulate network delay
            await asyncio.sleep(0.1)
            return Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "id": f"W{len(call_times)}",
                        "title": f"Work {len(call_times)}",
                    }
                ),
            )

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = mock_response

            works = AsyncWorks()

            # Launch multiple concurrent requests
            start_time = time.time()
            tasks = [works.get(f"W{i}") for i in range(3)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            # Should complete in ~0.1s (parallel) not ~0.3s (sequential)
            assert total_time < 0.2
            assert len(results) == 3

            # Verify calls were made concurrently (all started within 50ms)
            assert max(call_times) - min(call_times) < 0.05

    async def test_async_random_endpoint(self, mock_concept_data):
        """Async random should return random entity."""
        from openalex import AsyncConcepts

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_concept_data)
            )

            concepts = AsyncConcepts()
            concept = await concepts.random()

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/concepts/random")
            assert concept.display_name == "Medicine"

    async def test_async_autocomplete(self):
        """Async autocomplete should return suggestions."""
        from openalex import AsyncPublishers

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [
                            {
                                "id": "P123",
                                "display_name": "Springer Nature",
                                "entity_type": "publisher",
                                "works_count": 1000000,
                            }
                        ],
                        "meta": {"count": 1},
                    }
                ),
            )

            publishers = AsyncPublishers()
            results = await publishers.autocomplete("springer")

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/autocomplete/publishers")
            assert kwargs["params"]["q"] == "springer"

    async def test_async_first_helper(self):
        """Async first() should return first result or None."""
        from openalex import AsyncFunders

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            # Has results
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [{"id": "F1", "display_name": "NSF"}],
                        "meta": {"count": 5},
                    }
                ),
            )

            funders = AsyncFunders()
            funder = await funders.filter(country_code="US").first()
            assert funder is not None
            assert funder.display_name == "NSF"

            # No results
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}}),
            )

            no_funder = await funders.filter(country_code="XX").first()
            assert no_funder is None

    async def test_async_count_efficient(self):
        """Async count should use minimal page size."""
        from openalex import AsyncTopics

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={"results": [], "meta": {"count": 12345}}
                ),
            )

            topics = AsyncTopics()
            count = await topics.filter(domain={"id": "D123"}).count()

            _, kwargs = mock_request.call_args
            assert kwargs["params"]["per-page"] == "1"
            assert count == 12345

    async def test_async_error_handling(self):
        """Async client should handle errors like sync client."""
        from openalex import AsyncKeywords
        from openalex.exceptions import NotFoundError

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=404,
                json=Mock(
                    return_value={
                        "error": "Not Found",
                        "message": "Keyword not found",
                    }
                ),
                is_success=False,
            )

            keywords = AsyncKeywords()

            with pytest.raises(NotFoundError):
                await keywords.get("nonexistent-keyword")

    async def test_async_cache_behavior(self):
        """Async client should use cache when enabled."""
        from openalex import AsyncWorks, OpenAlexConfig
        import openalex.cache.manager as cache_manager

        cache_manager._cache_manager = None

        config = OpenAlexConfig(cache_enabled=True)

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"id": "W123", "title": "Cached Work"}),
            )

            works = AsyncWorks(config=config)

            # Multiple identical requests
            work1 = await works.get("W123")
            work2 = await works.get("W123")
            work3 = await works.get("W123")

            # All should return same data
            assert work1.title == work2.title == work3.title == "Cached Work"

            # But only one API call
            assert mock_request.call_count == 1

    async def test_async_paginator_gather(self):
        """Async paginator gather should fetch multiple pages concurrently."""
        from openalex import AsyncAuthors

        pages_data = []

        async def mock_response(*args, **kwargs):
            page = int(kwargs["params"].get("page", 1))
            return Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [
                            {"id": f"A{page}", "display_name": f"Author {page}"}
                        ],
                        "meta": {"count": 10, "page": page},
                    }
                ),
            )

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = mock_response

            authors = AsyncAuthors()
            paginator = authors.filter(works_count=">10").paginate(per_page=1)

            # Gather first 3 pages
            results = await paginator.gather(pages=3)

            assert len(results) == 3
            assert results[0].display_name == "Author 1"
            assert results[2].display_name == "Author 3"

    async def test_async_connection_cleanup(self):
        """Async connections should be cleanable."""
        from openalex import AsyncWorks, close_all_async_connections

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}}),
            )

            # Create multiple clients
            works1 = AsyncWorks()
            works2 = AsyncWorks()

            await works1.filter(is_oa=True).count()
            await works2.filter(is_oa=False).count()

            # Clean up all connections
            await close_all_async_connections()

            # Verify cleanup was called (implementation dependent)
            # Main point is it doesn't raise an error

    async def test_all_async_entity_types_work(self):
        """Test that all async entity types can perform basic operations."""
        from openalex import (
            AsyncConcepts,
            AsyncFunders,
            AsyncKeywords,
            AsyncPublishers,
            AsyncTopics,
        )

        test_cases = [
            (AsyncConcepts(), "C2778407487", "artificial intelligence"),
            (AsyncFunders(), "F4320306076", "National Science Foundation"),
            (AsyncKeywords(), "K123", "machine learning"),
            (AsyncPublishers(), "P4310319965", "Elsevier"),
            (AsyncTopics(), "T10001", "Climate change"),
        ]

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            for entity, entity_id, expected_name in test_cases:
                mock_request.return_value = Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "id": f"https://openalex.org/{entity_id}",
                            "display_name": expected_name,
                        }
                    ),
                )

                result = await entity.get(entity_id)

                assert result.display_name == expected_name
                assert entity.endpoint in mock_request.call_args.kwargs["url"]
                assert entity_id in mock_request.call_args.kwargs["url"]

    async def test_async_ngrams_functionality(self):
        """Test async Works.ngrams() method."""
        from openalex import AsyncWorks

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "meta": {"count": 2},
                        "results": [
                            {
                                "ngram": "climate change",
                                "ngram_count": 5,
                                "ngram_tokens": 2,
                            },
                            {
                                "ngram": "global warming",
                                "ngram_count": 3,
                                "ngram_tokens": 2,
                            },
                        ],
                    }
                ),
            )

            works = AsyncWorks()
            ngrams = await works.ngrams("W2741809807")

            assert len(ngrams.results) == 2
            assert ngrams.results[0].ngram == "climate change"

    async def test_async_autocomplete_multiple_entities(self):
        """Test async autocomplete functionality for multiple entity types."""
        from openalex import AsyncWorks, AsyncAuthors

        test_cases = [
            (
                AsyncWorks(),
                "climate ch",
                ["Climate change impacts", "Climate change mitigation"],
            ),
            (
                AsyncAuthors(),
                "einstein a",
                ["Einstein, Albert", "Einstein, Alfred"],
            ),
        ]

        for entity, query, expected_hints in test_cases:
            with patch(
                "httpx.AsyncClient.request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.return_value = Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "results": [
                                {"id": f"hint{i}", "display_name": hint}
                                for i, hint in enumerate(expected_hints)
                            ],
                            "meta": {"count": len(expected_hints)},
                        }
                    ),
                )

                results = await entity.autocomplete(query)
                assert len(results.results) == len(expected_hints)
                assert results.results[0].display_name == expected_hints[0]

    async def test_async_random_entity(self):
        """Test async random entity fetching."""
        from openalex import AsyncInstitutions

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "id": "https://openalex.org/I123",
                        "display_name": "Random University",
                    }
                ),
            )

            institutions = AsyncInstitutions()
            random_inst = await institutions.random()

        assert random_inst.display_name == "Random University"
        assert "/random" in mock_request.call_args.kwargs["url"]


@pytest.mark.asyncio
class TestAsyncAdditionalBehavior:
    """Additional async behavior tests."""

    async def test_async_entity_initialization(self):
        """Test async entities can be initialized with different configs."""
        from openalex import (
            AsyncWorks,
            AsyncAuthors,
            AsyncInstitutions,
            AsyncSources,
            AsyncTopics,
            AsyncPublishers,
            AsyncFunders,
            AsyncKeywords,
            AsyncConcepts,
            OpenAlexConfig,
        )

        base_config = OpenAlexConfig(email="base@example.com", api_key="base-key")

        works = AsyncWorks(config=base_config)
        assert works._config.email == "base@example.com"
        assert works._config.api_key == "base-key"

        authors = AsyncAuthors(
            email="override@example.com",
            api_key="override-key",
            config=base_config,
        )
        assert authors._config.email == "override@example.com"
        assert authors._config.api_key == "override-key"

        entity_classes = [
            AsyncInstitutions,
            AsyncSources,
            AsyncTopics,
            AsyncPublishers,
            AsyncFunders,
            AsyncKeywords,
            AsyncConcepts,
        ]

        for entity_cls in entity_classes:
            entity = entity_cls(email="test@example.com")
            assert entity._config.email == "test@example.com"
            assert hasattr(entity, "endpoint")
            assert entity.endpoint != ""
            assert hasattr(entity, "model_class")
            assert entity.model_class is not None

    async def test_async_get_many_functionality(self):
        """Test async get_many fetches multiple entities efficiently."""
        from openalex import AsyncWorks
        from openalex.entities import AsyncBaseEntity as BaseEntityImpl
        import asyncio

        concurrent_calls = 0
        max_concurrent_observed = 0
        call_times = []

        async def mock_get(self, entity_id):
            nonlocal concurrent_calls, max_concurrent_observed
            concurrent_calls += 1
            max_concurrent_observed = max(max_concurrent_observed, concurrent_calls)
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)
            concurrent_calls -= 1
            if entity_id == "W99999":
                raise RuntimeError("Simulated failure")
            return type(
                "Work",
                (),
                {"id": f"https://openalex.org/{entity_id}", "display_name": f"Work {entity_id}"},
            )()

        works = AsyncWorks()

        with (
            patch.object(BaseEntityImpl, "get", mock_get),
            patch("openalex.entities.logger") as mock_logger,
        ):
            mock_warning = mock_logger.warning
            mock_logger.exception.return_value = None
            results = await works.get_many(
                ["W123", "invalid-id", "W456", "W99999", "W789"],
                max_concurrent=2,
            )

        mock_warning.assert_called()
        warning_args = mock_warning.call_args[0]
        assert "invalid-id" in str(warning_args)

        assert len(results) == 3
        assert all(hasattr(r, "display_name") for r in results)
        assert max_concurrent_observed <= 2
        assert any("W123" in r.id for r in results)
        assert any("W789" in r.id for r in results)
        assert not any("W99999" in r.id for r in results)

