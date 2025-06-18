"""Example: Performance monitoring with OpenAlex client."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from openalex import Authors, Works, config
from openalex.logging import configure_logging
from openalex.metrics import get_metrics, reset_metrics


def demo_performance_monitoring() -> None:
    """Demonstrate performance monitoring capabilities."""
    print("OpenAlex Performance Monitoring Demo")
    print("=" * 50)

    configure_logging(level="INFO", format="console")
    reset_metrics()

    config.max_retries = 3
    config.retry_delay = 1.0

    print("\n1. Making various API calls...")

    work = Works()["W2755950973"]
    print(f"   - Fetched work: {work.display_name[:50]}...")

    results = (
        Works()
        .search("climate change")
        .filter(publication_year=2023)
        .filter(is_open_access=True)
        .get(per_page=50)
    )
    print(f"   - Found {results.meta.count:,} works on climate change")

    grouped = (
        Works()
        .filter(institutions={"country_code": "US"})
        .group_by("type")
        .get()
    )
    print(f"   - Grouped {len(grouped.groups)} work types")

    print("\n2. Testing cache performance...")

    start = time.time()
    Authors()["A2150889177"]
    first_time = time.time() - start

    start = time.time()
    Authors()["A2150889177"]
    second_time = time.time() - start

    print(f"   - First call: {first_time*1000:.2f}ms (cache miss)")
    print(f"   - Second call: {second_time*1000:.2f}ms (cache hit)")
    if second_time > 0:
        print(f"   - Speedup: {first_time/second_time:.1f}x")

    print("\n3. Performance Metrics Summary:")
    print("-" * 50)

    metrics = get_metrics()
    report = metrics.to_dict()

    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Success Rate: {report['summary']['success_rate']}")
    print(f"Cache Hit Rate: {report['cache']['hit_rate']}")
    print(f"Avg Response Time: {report['performance']['avg_response_time_ms']}ms")
    print(f"95th Percentile: {report['performance']['p95_response_time_ms']}ms")

    print("\nRequests by Endpoint:")
    for endpoint, count in report["endpoints"].items():
        print(f"  - {endpoint}: {count}")

    if report["errors"]:
        print("\nErrors:")
        for error_type, count in report["errors"].items():
            print(f"  - {error_type}: {count}")


def demo_concurrent_performance() -> None:
    """Demonstrate performance under concurrent load."""
    print("\n\nConcurrent Performance Test")
    print("=" * 50)

    reset_metrics()

    def fetch_work(work_id: str) -> str:
        work = Works()[work_id]
        return work.display_name

    work_ids = [
        "W2755950973",
        "W2126385722",
        "W2170499123",
        "W2755951606",
        "W2736953509",
    ]

    print("Fetching 5 works concurrently...")

    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_work, wid) for wid in work_ids]
        [f.result() for f in futures]
    total_time = time.time() - start

    print(f"\nCompleted in {total_time:.2f}s")
    print(f"Average time per request: {total_time/len(work_ids):.2f}s")

    metrics = get_metrics()
    print(f"\nCache hit rate: {metrics.cache_hit_rate:.1%}")
    print(f"Total retries: {metrics.total_retries}")


async def demo_async_performance() -> None:
    """Demonstrate async performance monitoring."""
    print("\n\nAsync Performance Test")
    print("=" * 50)

    from openalex import AsyncWorks

    reset_metrics()

    async def fetch_works_async() -> list[Any]:
        work_ids = [f"W{2755950973 + i}" for i in range(10)]
        tasks = [AsyncWorks()[wid] for wid in work_ids]
        return await asyncio.gather(*tasks, return_exceptions=True)

    print("Fetching 10 works asynchronously...")
    start = time.time()

    results = await fetch_works_async()

    total_time = time.time() - start
    successful = sum(1 for r in results if not isinstance(r, Exception))

    print(f"\nCompleted in {total_time:.2f}s")
    print(f"Successful: {successful}/10")

    metrics = get_metrics()
    print(f"Average response time: {metrics.avg_response_time:.2f}ms")


if __name__ == "__main__":
    demo_performance_monitoring()
    demo_concurrent_performance()
    asyncio.run(demo_async_performance())

    print("\n\nFinal Performance Summary")
    print("=" * 50)
    final_metrics = get_metrics()
    print(f"Total API calls: {final_metrics.total_requests}")
    print(f"Overall success rate: {final_metrics.success_rate:.1%}")
    print(f"Overall cache hit rate: {final_metrics.cache_hit_rate:.1%}")
    print(f"Session duration: {final_metrics.uptime.total_seconds():.1f}s")
