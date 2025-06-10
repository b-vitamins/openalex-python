from openalex.utils.text import invert_abstract


class TestAbstractInversion:
    """Tests for abstract inversion utility."""

    def test_invert_abstract(self) -> None:
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
        assert invert_abstract(None) is None
        assert invert_abstract({}) is None
