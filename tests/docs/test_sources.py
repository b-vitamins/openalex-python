"""Test sources documentation."""

from pathlib import Path
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestSourcesDocs(BaseDocTest):
    """Test docs/sources/ documentation."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "sources"
