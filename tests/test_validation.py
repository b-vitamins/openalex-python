import pytest
from openalex.utils.validation import validate_entity_id


class TestValidation:
    def test_valid_entity_ids_pass(self):
        """Test valid IDs pass validation."""
        assert validate_entity_id("W1234567890", "work") == "W1234567890"

    def test_invalid_ids_raise_error(self):
        """Test invalid IDs raise ValueError."""
        with pytest.raises(ValueError):
            validate_entity_id("invalid-id", "work")

    def test_sql_injection_blocked(self):
        """Test SQL injection attempts are blocked."""
        with pytest.raises(ValueError):
            validate_entity_id("W123'; DROP TABLE works;--", "work")

    def test_url_parsing_works(self):
        """Test URL parsing extracts ID correctly."""
        result = validate_entity_id("https://openalex.org/W1234567890", "work")
        assert result == "W1234567890"
