"""Test funders documentation."""

from pathlib import Path
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestFundersDocs(BaseDocTest):
    """Test docs/funders/ documentation."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "funders"
