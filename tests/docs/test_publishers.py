"""Test publishers documentation."""

from pathlib import Path
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestPublishersDocs(BaseDocTest):
    """Test docs/publishers/ documentation."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "publishers"
