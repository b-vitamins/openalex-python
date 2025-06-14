"""Test concepts documentation."""

from pathlib import Path
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestConceptsDocs(BaseDocTest):
    """Test docs/concepts/ documentation."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "concepts"
