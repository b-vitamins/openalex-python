"""Test works documentation."""

import pytest
from pathlib import Path
from pytest_examples import find_examples
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestWorksDocs(BaseDocTest):
    """Test docs/works/ documentation."""

    def get_docs_path(self) -> Path:
        """Return path to works docs."""
        return Path(__file__).parent.parent.parent / "docs" / "works"

    @pytest.mark.docs
    def test_works_always_filtered(self):
        """Ensure Works() queries always have filters in examples."""
        docs_path = self.get_docs_path()

        for example in find_examples(*docs_path.glob("*.md")):
            if "python" not in example.prefix.lower() or self.should_skip(
                example
            ):
                continue

            code = example.source

            if (
                "Works().get()" in code.replace(" ", "")
                and "# BAD" not in code
                and "Don't do this" not in code
            ):
                pytest.fail(
                    f"Unfiltered Works query at {example.path.name}:{example.start_line}\n"
                    "Works queries should always include filters due to dataset size (250M+ records)\n"
                    f"Code:\n{code}"
                )

            import re

            pattern = r"Works\(\)\s*\.get\(\)"
            if re.search(pattern, code) and "# BAD" not in code:
                pytest.fail(
                    f"Unfiltered Works query at {example.path.name}:{example.start_line}\n"
                    "Avoid calling Works().get() without filters"
                )

    @pytest.mark.docs
    def test_large_paginate_has_limits(self):
        """Ensure paginate() examples have reasonable limits."""
        docs_path = self.get_docs_path()

        for example in find_examples(*docs_path.glob("*.md")):
            if "python" not in example.prefix.lower() or self.should_skip(
                example
            ):
                continue

            code = example.source

            if ".paginate(" in code and "Works()" in code:
                has_limit = any(
                    [
                        "break" in code,
                        "[:1000]" in code,
                        "max_results" in code,
                        "limit" in code.lower(),
                        "first 100" in code.lower(),
                        "# Stop after" in code,
                    ]
                )

                if not has_limit:
                    pytest.fail(
                        f"Pagination without limit at {example.path.name}:{example.start_line}\n"
                        "Add a break condition or limit to avoid fetching millions of records\n"
                        f"Code:\n{code}"
                    )
