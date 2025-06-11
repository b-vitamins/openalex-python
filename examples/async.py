"""Example of using async OpenAlex API."""

import asyncio

from openalex import (
    AsyncAuthors,
    AsyncWorks,
    OpenAlexConfig,
    close_all_async_connections,
)

CONFIG = OpenAlexConfig(email="test@example.com")


async def search_recent_ml_papers():
    """Search for recent machine learning papers."""
    works = AsyncWorks(config=CONFIG)

    try:
        results = await (
            works.search("machine learning")
            .filter(publication_year=2024)
            .filter(is_oa=True)
            .sort("cited_by_count", "desc")
            .get(per_page=10)
        )
    except Exception as e:
        print(f"Error fetching ML papers: {e}")
        return

    print(f"Found {results.meta.count} ML papers from 2024")

    for work in results.results:
        print(f"\n{work.title}")
        print(f"  Citations: {work.cited_by_count}")
        print(f"  DOI: {work.doi}")


async def parallel_searches():
    """Demonstrate parallel searches."""
    works = AsyncWorks(config=CONFIG)
    authors = AsyncAuthors(config=CONFIG)

    tasks = [
        works.search("quantum computing").get(per_page=5),
        works.search("climate change").get(per_page=5),
        authors.search("Einstein").get(per_page=5),
    ]

    try:
        results = await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error in parallel searches: {e}")
        return

    quantum_results, climate_results, einstein_results = results

    print(f"Quantum computing papers: {quantum_results.meta.count}")
    print(f"Climate change papers: {climate_results.meta.count}")
    print(f"Authors named Einstein: {einstein_results.meta.count}")


async def stream_all_results():
    """Stream all results using async iteration."""
    works = AsyncWorks(config=CONFIG)

    count = 0
    try:
        async for _work in works.filter(publication_year=2024, is_oa=True).all():
            count += 1
            if count % 100 == 0:
                print(f"Processed {count} papers...")

            if count >= 1000:
                break
    except Exception as e:
        print(f"Error streaming results: {e}")
        return

    print(f"Total processed: {count}")


async def main():
    """Run all examples."""
    print("=== Recent ML Papers ===")
    await search_recent_ml_papers()

    print("\n=== Parallel Searches ===")
    await parallel_searches()

    print("\n=== Streaming Results ===")
    await stream_all_results()

    await close_all_async_connections()


if __name__ == "__main__":
    asyncio.run(main())
