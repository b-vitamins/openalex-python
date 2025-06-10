"""Examples of PyAlex-style usage patterns."""

from openalex import Institutions, Works
from openalex.query import gt_


# Direct entity access
def example_direct_access():
    """Get entities directly by ID."""
    # Single work
    work = Works()["W2741809807"]
    print(f"Title: {work.title}")
    print(f"Abstract: {work.abstract}")  # Auto-converted from inverted index

    # Multiple works
    works = Works()[["W2741809807", "W2038229424"]]
    for w in works.results:
        print(f"{w.title} ({w.publication_year})")


# Complex filtering
def example_complex_filters():
    """Demonstrate complex filter combinations."""
    # Recent, highly-cited, open access articles
    results = (
        Works()
        .filter_gt(cited_by_count=100)
        .filter(publication_year=[2022, 2023, 2024])
        .filter(is_oa=True)
        .filter_not(type="retracted")
        .sort(cited_by_count="desc")
        .select(["id", "title", "cited_by_count", "doi"])
        .get(per_page=10)
    )

    for work in results.results:
        print(f"{work.title}: {work.cited_by_count} citations")


# Search with filters
def example_search():
    """Search with field-specific filters."""
    # Search in title and abstract
    results = (
        Works()
        .search_filter(title="quantum computing", abstract="algorithm")
        .filter(publication_year=2023)
        .get()
    )

    print(f"Found {results.meta.count} papers on quantum computing algorithms")


# Author collaboration network
def example_author_network():
    """Find co-authors of a specific author."""
    author_id = "A2208157607"  # Geoffrey Hinton

    # Get all works by this author
    works = Works().filter(authorships={"author": {"id": author_id}}).paginate()

    # Extract unique co-authors
    coauthors = set()
    for work in works:
        for authorship in work.authorships:
            if authorship.author.id != author_id:
                coauthors.add(authorship.author.id)

    print(f"Found {len(coauthors)} unique co-authors")


# Institution comparison
def example_institution_comparison():
    """Compare research output of institutions."""
    institutions = ["I134386786", "I62916508"]  # MIT and Stanford

    for inst_id in institutions:
        # Get institution details
        inst = Institutions()[inst_id]

        # Count recent works
        recent_works = (
            Works()
            .filter(
                authorships={"institutions": {"id": inst_id}},
                publication_year=gt_(2020),
            )
            .count()
        )

        print(f"{inst.display_name}: {recent_works} works since 2020")


# N-grams analysis
def example_ngrams():
    """Analyze n-grams from a work."""
    work_id = "W2741809807"

    # Get the work
    work = Works()[work_id]
    print(f"Analyzing: {work.title}")

    # Get n-grams
    ngrams = Works()._resource.ngrams(work_id)  # noqa: SLF001

    # Most frequent n-grams
    top_ngrams = sorted(
        ngrams.results, key=lambda x: x.ngram_count, reverse=True
    )[:10]

    print("\nTop 10 n-grams:")
    for ng in top_ngrams:
        print(f"  '{ng.ngram}': {ng.ngram_count} occurrences")


if __name__ == "__main__":
    # Run examples
    example_direct_access()
    example_complex_filters()
    example_search()
    example_ngrams()
