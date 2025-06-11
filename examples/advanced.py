"""Advanced query examples for OpenAlex Python client."""

from datetime import datetime, timedelta

from openalex import Authors, Institutions, OpenAlexConfig, Works

CONFIG = OpenAlexConfig(email="test@example.com")


def performance_optimized_queries():
    """Examples of performance-optimized queries."""

    # Configure for performance
    config = OpenAlexConfig(
        email="test@example.com",
        cache_enabled=True,
        cache_maxsize=5000,
        cache_ttl=7200,  # 2 hours
    )

    works = Works(config=config)

    # 1. Select only needed fields to reduce payload
    print("=== Minimal field selection ===")
    minimal_works = (
        works
        .filter(publication_year=2024)
        .select(["id", "title", "cited_by_count", "doi"])
        .get(per_page=100)
    )
    print(f"Fetched {len(minimal_works.results)} works with minimal data")

    # 2. Use cursor pagination for large datasets
    print("\n=== Efficient pagination ===")
    count = 0
    for _ in works.filter(publication_year=2024, is_oa=True).paginate():
        count += 1
        if count >= 1000:
            break
    print(f"Efficiently processed {count} works")

    # 3. Batch similar queries
    print("\n=== Batch processing ===")
    institution_ids = ["I136199984", "I63966007", "I97018004"]  # Harvard, MIT, Stanford

    # Instead of multiple queries, pass a list of institution IDs
    batch_results = (
        works
        .filter(
            institutions={"id": institution_ids},
            publication_year=2024,
        )
        .get()
    )
    print(f"Batch query returned {batch_results.meta.count} works")


def complex_filtering_examples():
    """Examples of complex filtering patterns."""

    works = Works(config=CONFIG)

    # 1. Date range queries
    print("=== Date range filtering ===")
    last_month = datetime.now() - timedelta(days=30)
    recent_works = (
        works
        .filter(
            from_publication_date=last_month.strftime("%Y-%m-%d"),
            to_publication_date=datetime.now().strftime("%Y-%m-%d")
        )
        .get()
    )
    print(f"Works published in last 30 days: {recent_works.meta.count}")

    # 2. Complex institutional filtering
    print("\n=== Complex institutional queries ===")
    # Find works where Harvard and MIT collaborated
    collaborations = (
        works
        .filter(
            institutions={"id": "I136199984"},
            authorships={"institutions": {"id": "I63966007"}},
        )
        .filter(publication_year=2024)
        .get()
    )
    print(f"Harvard-MIT collaborations in 2024: {collaborations.meta.count}")

    # 3. Citation-based filtering
    print("\n=== Citation analysis ===")
    highly_cited_recent = (
        works
        .filter(publication_year="2020-2024")
        .filter_gt(cited_by_count=100)
        .sort(cited_by_count="desc")
        .get()
    )
    print(f"Recent highly-cited works: {highly_cited_recent.meta.count}")

    # 4. Language and region filtering
    print("\n=== Language and region ===")
    chinese_ml_papers = (
        works
        .filter(language="zh", institutions={"country_code": "CN"})
        .search("machine learning")
        .get()
    )
    print(f"Chinese ML papers: {chinese_ml_papers.meta.count}")


def author_career_analysis():
    """Analyze an author's career trajectory."""

    authors = Authors(config=CONFIG)

    # Find a specific author
    author_results = authors.search("Yoshua Bengio", per_page=1)
    if not author_results.results:
        print("Author not found")
        return

    author = author_results.results[0]
    print(f"\n=== Analyzing {author.display_name} ===")
    print(f"Total works: {author.works_count}")
    print(f"Total citations: {author.cited_by_count}")
    if author.summary_stats:
        h_index = (
            author.summary_stats.h_index
            if hasattr(author.summary_stats, "h_index")
            else author.summary_stats.get("h_index")
        )
        if h_index is not None:
            print(f"H-index: {h_index}")

    # Get their works over time
    works = Works(config=CONFIG)

    # Publications by year
    yearly_stats = (
        works
        .filter(author={"id": author.id})
        .group_by("publication_year")
        .get()
    )

    print("\nPublications by year:")
    groups = yearly_stats.group_by or []
    for group in sorted(groups, key=lambda x: x.key, reverse=True)[:5]:
        print(f"  {group.key}: {group.count} works")

    # Top collaborators
    print("\nFinding top collaborators...")
    author_works = works.filter(author={"id": author.id}).get(per_page=50)

    collaborators: dict[str, int] = {}
    for work in author_works.results:
        for authorship in work.authorships:
            auth = getattr(authorship, "author", None)
            auth_id = getattr(auth, "id", None) if auth else None
            if auth and auth_id != author.id:
                name = getattr(auth, "display_name", "")
                collaborators[name] = collaborators.get(name, 0) + 1

    print("Top collaborators:")
    for name, count in sorted(collaborators.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {name}: {count} papers")


def institutional_rankings():
    """Create custom institutional rankings."""

    institutions = Institutions(config=CONFIG)

    # Top institutions by recent paper count
    print("=== Top institutions by output ===")
    top_institutions = (
        institutions
        .filter_gt(works_count=1000)  # Minimum threshold
        .sort(works_count="desc")
        .get(per_page=10)
    )

    # Now get their 2024 metrics
    works = Works(config=CONFIG)
    for inst in top_institutions.results[:5]:
        recent_works = works.filter(
            institutions={"id": inst.id},
            publication_year=2024
        ).get(per_page=1)

        print(f"{inst.display_name}: {recent_works.meta.count} papers in 2024")


def research_trend_analysis():
    """Analyze research trends over time."""

    works = Works(config=CONFIG)

    # Compare AI subfields growth
    subfields = [
        "deep learning",
        "reinforcement learning",
        "natural language processing",
        "computer vision",
        "generative AI"
    ]

    print("=== AI Research Trends (2020-2024) ===")

    for subfield in subfields:
        # Get counts by year
        yearly_counts: dict[int, int] = {}

        for year in range(2020, 2025):
            result = works.search(
                subfield,
                filter={"publication_year": year},
                per_page=1,
            )
            yearly_counts[year] = result.meta.count

        # Calculate growth
        if yearly_counts[2020] > 0:
            growth = ((yearly_counts[2024] - yearly_counts[2020]) / yearly_counts[2020]) * 100
        else:
            growth = 0

        print(f"\n{subfield.title()}:")
        print(f"  2020: {yearly_counts[2020]:,} papers")
        print(f"  2024: {yearly_counts[2024]:,} papers")
        print(f"  Growth: {growth:.1f}%")


def open_access_analysis():
    """Analyze open access trends."""

    works = Works(config=CONFIG)

    print("=== Open Access Analysis ===")

    # OA percentage by year
    for year in range(2020, 2025):
        try:
            stats = (
                works
                .filter(publication_year=year)
                .group_by("is_oa")
                .get()
            )
        except Exception as exc:  # pragma: no cover - example
            print(f"Failed to fetch OA stats for {year}: {exc}")
            return

        groups = stats.group_by or []
        total = sum(g.count for g in groups)
        oa_count = next((g.count for g in groups if g.key == "true"), 0)
        oa_percentage = (oa_count / total * 100) if total > 0 else 0

        print(f"{year}: {oa_percentage:.1f}% OA ({oa_count:,}/{total:,})")



def cache_performance_demo():
    """Demonstrate cache performance benefits."""

    import time

    # Without cache
    config_no_cache = OpenAlexConfig(email="test@example.com", cache_enabled=False)
    works_no_cache = Works(config=config_no_cache)

    # With cache
    config_cache = OpenAlexConfig(email="test@example.com", cache_enabled=True)
    works_cache = Works(config=config_cache)

    work_id = "W2741809807"

    print("=== Cache Performance Demo ===")

    # First fetch - no cache
    start = time.time()
    works_no_cache.get(work_id)
    time1 = time.time() - start
    print(f"First fetch (no cache): {time1:.3f}s")

    # Second fetch - no cache
    start = time.time()
    works_no_cache.get(work_id)
    time2 = time.time() - start
    print(f"Second fetch (no cache): {time2:.3f}s")

    # First fetch - with cache
    start = time.time()
    works_cache.get(work_id)
    time3 = time.time() - start
    print(f"First fetch (with cache): {time3:.3f}s")

    # Second fetch - from cache
    start = time.time()
    works_cache.get(work_id)
    time4 = time.time() - start
    print(f"Second fetch (from cache): {time4:.3f}s")

    print(f"\nCache speedup: {time2/time4:.0f}x faster!")

    # Show cache stats
    stats = works_cache.cache_stats()
    print(f"\nCache stats: {stats}")


if __name__ == "__main__":
    print("OpenAlex Python Client - Advanced Examples\n")

    examples = [
        performance_optimized_queries,
        complex_filtering_examples,
        author_career_analysis,
        institutional_rankings,
        research_trend_analysis,
        open_access_analysis,
        cache_performance_demo,
    ]

    for example in examples:
        try:
            example()
        except Exception as exc:  # pragma: no cover - example
            print(f"Example {example.__name__} failed: {exc}")
        print("\n" + "=" * 50 + "\n")

