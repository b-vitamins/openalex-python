"""Test Phase 4 features."""

from openalex import Authors, Works
from openalex.models.work import Ngram, Work
from openalex.utils.text import invert_abstract


class TestAbstractInversion:
    """Test abstract inversion utility."""

    def test_invert_abstract(self) -> None:
        """Test converting inverted index to text."""
        inverted = {
            "This": [0],
            "is": [1],
            "a": [2],
            "test": [3],
            "abstract": [4],
        }

        result = invert_abstract(inverted)
        assert result == "This is a test abstract"

    def test_invert_abstract_none(self) -> None:
        """Test with None input."""
        assert invert_abstract(None) is None
        assert invert_abstract({}) is None

    def test_work_abstract_property(self) -> None:
        """Test Work.abstract property."""
        work = Work(
            id="W123",
            title="Test",
            display_name="Test",
            abstract_inverted_index={
                "Machine": [0, 5],
                "learning": [1, 6],
                "is": [2],
                "great": [3],
                "for": [4],
            },
        )

        assert work.abstract == "Machine learning is great for Machine learning"


class TestNgrams:
    """Test n-grams functionality."""

    def test_ngram_model(self) -> None:
        """Test Ngram model."""
        ngram = Ngram(
            ngram="machine learning",
            ngram_count=42,
            ngram_tokens=2,
            term_frequency=0.05,
        )

        assert ngram.ngram == "machine learning"
        assert ngram.ngram_count == 42
        assert ngram.ngram_tokens == 2
        assert ngram.term_frequency == 0.05


class TestStringRepresentations:
    """Test __repr__ methods."""

    def test_query_repr(self) -> None:
        """Test Query string representation."""
        from openalex.query import Query

        class MockResource:
            pass

        query = Query(MockResource()).filter(is_oa=True).search("test")
        repr_str = repr(query)

        assert "<Query(MockResource" in repr_str
        assert "filter=" in repr_str
        assert "search='test'" in repr_str

    def test_entity_repr(self) -> None:
        """Test entity string representation."""
        works = Works(email="test@example.com")
        repr_str = repr(works)

        assert "<Works(" in repr_str
        assert "email='test@example.com'" in repr_str

        # Test with API key (should be masked)
        authors = Authors(api_key="secret-key")
        repr_str = repr(authors)

        assert "<Authors(" in repr_str
        assert "api_key='***'" in repr_str
        assert "secret-key" not in repr_str
