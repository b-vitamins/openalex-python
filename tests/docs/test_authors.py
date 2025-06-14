"""Test authors documentation."""

import pytest
from pathlib import Path
from pytest_examples import find_examples
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestAuthorsDocs(BaseDocTest):
    """Test docs/authors/ documentation."""

    def get_docs_path(self) -> Path:
        """Return path to authors docs."""
        return Path(__file__).parent.parent.parent / "docs" / "authors"

    @pytest.mark.docs
    def test_orcid_format(self):
        """Ensure ORCID examples use correct format."""
        docs_path = self.get_docs_path()

        for example in find_examples(docs_path, pattern="*.md"):
            if example.lang != "python" or self.should_skip(example):
                continue

            code = example.code

            if "orcid" in code.lower():
                import re
                bad_orcid_pattern = r'orcid["\']?\s*[:=]\s*["\']?\d{15,16}["\']?'
                if re.search(bad_orcid_pattern, code, re.IGNORECASE):
                    pytest.fail(
                        f"ORCID should use XXXX-XXXX-XXXX-XXXX format at {example.path.name}:{example.start_line}\n"
                        f"Code:\n{code}"
                    )

    @pytest.mark.docs
    def test_author_id_format(self):
        """Ensure author IDs use correct format."""
        docs_path = self.get_docs_path()

        for example in find_examples(docs_path, pattern="*.md"):
            if example.lang != "python" or self.should_skip(example):
                continue

            code = example.code

            if "Authors()[" in code or 'author": {"id":' in code:
                import re
                bad_id_pattern = r'Authors\(\)\[["\'](?!A)[^"\']*["\']'
                if re.search(bad_id_pattern, code):
                    pytest.fail(
                        f"Author IDs should start with 'A' at {example.path.name}:{example.start_line}\n"
                        f"Code:\n{code}"
                    )
