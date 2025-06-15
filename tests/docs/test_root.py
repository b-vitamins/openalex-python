"""Test root-level documentation files."""

import pytest
from pathlib import Path
from pytest_examples import find_examples
from .base import BaseDocTest, parametrize_examples


@parametrize_examples
class TestIndexDoc(BaseDocTest):
    """Test index.md."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "index.md"


@parametrize_examples
class TestGettingStartedDoc(BaseDocTest):
    """Test getting-started.md."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "getting-started.md"

    @pytest.mark.docs
    def test_progressive_complexity(self):
        """Ensure examples progress from simple to complex."""
        examples = list(find_examples(self.get_docs_path()))
        python_examples = [e for e in examples if e.lang == "python"]

        if len(python_examples) < 2:
            pytest.skip("Not enough examples to test progression")

        first_example_lines = len(python_examples[0].code.strip().split("\n"))
        last_example_lines = len(python_examples[-1].code.strip().split("\n"))

        if first_example_lines > 20 and last_example_lines < 10:
            pytest.fail(
                "Examples should progress from simple to complex. "
                "Consider reordering examples in getting-started.md"
            )


@parametrize_examples
class TestApiReferenceDoc(BaseDocTest):
    """Test api-reference.md."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "api-reference.md"

    @pytest.mark.docs
    def test_all_entities_covered(self):
        """Ensure all entity types are demonstrated."""
        content = self.get_docs_path().read_text()

        entities = [
            "Works",
            "Authors",
            "Institutions",
            "Sources",
            "Publishers",
            "Funders",
            "Topics",
            "Concepts",
        ]

        missing = [e for e in entities if f"from openalex import {e}" not in content]

        if missing:
            pytest.fail(
                "API reference should demonstrate all entities. "
                f"Missing: {', '.join(missing)}"
            )


@parametrize_examples
class TestPerformanceGuideDoc(BaseDocTest):
    """Test performance-guide.md."""

    def get_docs_path(self) -> Path:
        return Path(__file__).parent.parent.parent / "docs" / "performance-guide.md"

    @pytest.mark.docs
    def test_demonstrates_efficient_patterns(self):
        """Ensure performance guide shows efficient patterns."""
        examples = list(find_examples(self.get_docs_path()))

        has_pagination_limit = False
        has_select_fields = False
        has_filter_example = False

        for example in examples:
            if "python" not in example.prefix.lower():
                continue

            code = example.source

            if ".paginate(" in code and ("break" in code or "limit" in code):
                has_pagination_limit = True

            if ".select(" in code:
                has_select_fields = True

            if "Works()" in code and ".filter(" in code:
                has_filter_example = True

        issues = []
        if not has_pagination_limit:
            issues.append("Should show pagination with limits")
        if not has_select_fields:
            issues.append("Should demonstrate select() for performance")
        if not has_filter_example:
            issues.append("Should emphasize filtering Works")

        if issues:
            pytest.fail(
                "Performance guide missing key examples:\n" + "\n".join(f"  - {issue}" for issue in issues)
            )


