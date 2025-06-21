"""
Test ID handling utilities.
Tests utils functions for OpenAlex ID normalization and validation.
"""

import pytest


class TestIDHandling:
    """Test OpenAlex ID handling utilities."""

    def test_strip_id_prefix(self):
        """Test stripping OpenAlex URL prefix from IDs."""
        from openalex.utils import strip_id_prefix

        # Full URLs
        assert (
            strip_id_prefix("https://openalex.org/W2741809807") == "W2741809807"
        )
        assert (
            strip_id_prefix("https://openalex.org/A5023888391") == "A5023888391"
        )
        assert strip_id_prefix("https://openalex.org/I27837315") == "I27837315"
        assert (
            strip_id_prefix("https://openalex.org/S137773608") == "S137773608"
        )
        assert strip_id_prefix("https://openalex.org/C71924100") == "C71924100"
        assert (
            strip_id_prefix("https://openalex.org/P4310319965") == "P4310319965"
        )
        assert (
            strip_id_prefix("https://openalex.org/F4320332161") == "F4320332161"
        )
        assert strip_id_prefix("https://openalex.org/T10017") == "T10017"

        # Already stripped
        assert strip_id_prefix("W2741809807") == "W2741809807"
        assert strip_id_prefix("A5023888391") == "A5023888391"

        # Special cases
        assert (
            strip_id_prefix("https://openalex.org/keywords/machine-learning")
            == "keywords/machine-learning"
        )
        assert (
            strip_id_prefix("keywords/machine-learning")
            == "keywords/machine-learning"
        )

        # None/empty
        assert strip_id_prefix(None) is None
        assert strip_id_prefix("") == ""

    def test_ensure_prefix(self):
        """Test ensuring IDs have correct prefix."""
        from openalex.utils import ensure_prefix

        # Add prefix when missing
        assert ensure_prefix("2741809807", "W") == "W2741809807"
        assert ensure_prefix("5023888391", "A") == "A5023888391"
        assert ensure_prefix("27837315", "I") == "I27837315"

        # Don't duplicate prefix
        assert ensure_prefix("W2741809807", "W") == "W2741809807"
        assert ensure_prefix("A5023888391", "A") == "A5023888391"

        # Case sensitivity
        assert (
            ensure_prefix("w2741809807", "W") == "w2741809807"
        )  # Preserves case

        # Empty/None handling
        assert ensure_prefix("", "W") == "W"
        assert ensure_prefix(None, "W") is None

    def test_is_openalex_id(self):
        """Test OpenAlex ID format validation."""
        from openalex.utils import is_openalex_id

        # Valid full URLs
        assert is_openalex_id("https://openalex.org/W2741809807")
        assert is_openalex_id("https://openalex.org/A5023888391")
        assert is_openalex_id("https://openalex.org/I27837315")
        assert is_openalex_id("https://openalex.org/S137773608")
        assert is_openalex_id("https://openalex.org/C71924100")
        assert is_openalex_id("https://openalex.org/P4310319965")
        assert is_openalex_id("https://openalex.org/F4320332161")
        assert is_openalex_id("https://openalex.org/T10017")
        assert is_openalex_id("https://openalex.org/keywords/machine-learning")

        # Invalid - short form
        assert not is_openalex_id("W2741809807")
        assert not is_openalex_id("A5023888391")

        # Invalid - wrong domain
        assert not is_openalex_id("https://example.com/W2741809807")
        assert not is_openalex_id(
            "http://openalex.org/W2741809807"
        )  # Wrong protocol

        # Invalid - malformed
        assert not is_openalex_id("not-an-id")
        assert not is_openalex_id("")
        assert not is_openalex_id(None)

    def test_normalize_entity_id(self):
        """Test complete ID normalization process."""
        from openalex.utils import normalize_entity_id

        # Full URL -> short form
        assert (
            normalize_entity_id("https://openalex.org/W123", "work") == "W123"
        )

        # Short form -> short form
        assert normalize_entity_id("W123", "work") == "W123"

        # No prefix -> add prefix
        assert normalize_entity_id("123", "work") == "W123"
        assert normalize_entity_id("456", "author") == "A456"
        assert normalize_entity_id("789", "institution") == "I789"

        # Entity type mapping
        assert normalize_entity_id("123", "source") == "S123"
        assert normalize_entity_id("123", "venue") == "S123"  # Venue -> Source
        assert normalize_entity_id("123", "concept") == "C123"
        assert normalize_entity_id("123", "publisher") == "P123"
        assert normalize_entity_id("123", "funder") == "F123"
        assert normalize_entity_id("123", "topic") == "T123"

        # Special handling for keywords
        assert (
            normalize_entity_id("machine-learning", "keyword")
            == "keywords/machine-learning"
        )
        assert (
            normalize_entity_id("keywords/machine-learning", "keyword")
            == "keywords/machine-learning"
        )
        assert (
            normalize_entity_id(
                "https://openalex.org/keywords/machine-learning", "keyword"
            )
            == "keywords/machine-learning"
        )

        # Case normalization
        assert normalize_entity_id("w123", "work") == "W123"  # Uppercase prefix

    def test_extract_entity_type_from_id(self):
        """Test extracting entity type from ID."""
        from openalex.utils import extract_entity_type

        # From full URLs
        assert extract_entity_type("https://openalex.org/W123") == "work"
        assert extract_entity_type("https://openalex.org/A123") == "author"
        assert extract_entity_type("https://openalex.org/I123") == "institution"
        assert extract_entity_type("https://openalex.org/S123") == "source"
        assert extract_entity_type("https://openalex.org/C123") == "concept"
        assert extract_entity_type("https://openalex.org/P123") == "publisher"
        assert extract_entity_type("https://openalex.org/F123") == "funder"
        assert extract_entity_type("https://openalex.org/T123") == "topic"
        assert (
            extract_entity_type("https://openalex.org/keywords/test")
            == "keyword"
        )

        # From short IDs
        assert extract_entity_type("W123") == "work"
        assert extract_entity_type("A123") == "author"

        # Unknown/invalid
        assert extract_entity_type("X123") is None
        assert extract_entity_type("123") is None
        assert extract_entity_type("") is None
        assert extract_entity_type(None) is None

    def test_validate_id_format(self):
        """Test ID format validation."""
        from openalex.utils import validate_id_format

        # Valid formats
        assert validate_id_format("W123", "work") is True
        assert validate_id_format("W2741809807", "work") is True
        assert validate_id_format("https://openalex.org/W123", "work") is True

        # Wrong prefix for entity type
        assert validate_id_format("A123", "work") is False
        assert validate_id_format("W123", "author") is False

        # Invalid format
        assert validate_id_format("123", "work") is False
        assert validate_id_format("WX123", "work") is False
        assert validate_id_format("W", "work") is False

        # Special cases
        assert validate_id_format("keywords/test", "keyword") is True
        assert validate_id_format("test", "keyword") is False

    def test_parse_mixed_ids(self):
        """Test parsing mixed ID formats from user input."""
        from openalex.utils import parse_entity_ids

        # Mixed formats
        ids = [
            "W123",
            "https://openalex.org/W456",
            "789",  # No prefix
            "w999",  # Lowercase
        ]

        parsed = parse_entity_ids(ids, entity_type="work")

        assert parsed == ["W123", "W456", "W789", "W999"]

        # With validation
        ids_with_invalid = ["W123", "A456", "789"]
        parsed_strict = parse_entity_ids(
            ids_with_invalid, entity_type="work", validate=True
        )

        # Should skip invalid A456
        assert parsed_strict == ["W123", "W789"]

    def test_id_url_construction(self):
        """Test constructing full OpenAlex URLs from IDs."""
        from openalex.utils import id_to_url

        assert id_to_url("W123") == "https://openalex.org/W123"
        assert id_to_url("A456") == "https://openalex.org/A456"
        assert (
            id_to_url("keywords/test") == "https://openalex.org/keywords/test"
        )

        # Already full URL
        assert (
            id_to_url("https://openalex.org/W123")
            == "https://openalex.org/W123"
        )

        # Invalid
        assert id_to_url("123") is None
        assert id_to_url("") is None
        assert id_to_url(None) is None

    def test_batch_id_normalization(self):
        """Test normalizing batches of IDs efficiently."""
        from openalex.utils import normalize_id_batch

        ids = ["W123", "https://openalex.org/W456", "789", None, "", "W999"]

        normalized = normalize_id_batch(ids, entity_type="work")

        assert normalized == ["W123", "W456", "W789", None, "", "W999"]

    def test_id_comparison(self):
        """Test comparing IDs in different formats."""
        from openalex.utils import ids_equal

        # Same ID in different formats
        assert ids_equal("W123", "https://openalex.org/W123")
        assert ids_equal("W123", "w123")  # Case insensitive
        assert ids_equal("https://openalex.org/W123", "W123")

        # Different IDs
        assert not ids_equal("W123", "W456")
        assert not ids_equal("W123", "A123")
        assert not ids_equal("W123", None)

        # Special cases
        assert ids_equal("keywords/test", "https://openalex.org/keywords/test")
