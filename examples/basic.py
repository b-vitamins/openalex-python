"""Basic usage examples for the OpenAlex Python client."""

from openalex import Authors, OpenAlexConfig, Works

config = OpenAlexConfig(email="test@example.com")


def list_ai_papers() -> None:
    """Print titles of recent AI papers."""
    results = Works(config=config).search("artificial intelligence", per_page=5)
    for work in results.results:
        print(work.title)


def get_author_info() -> None:
    """Print information about a specific author."""
    author = Authors(config=config).get("A5086198262")
    print(f"{author.display_name} has {author.works_count} works")


if __name__ == "__main__":
    list_ai_papers()
    get_author_info()
