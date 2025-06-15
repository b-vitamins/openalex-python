"""Base class for documentation tests."""

import pytest
from pathlib import Path
from pytest_examples import CodeExample, find_examples
from abc import ABC, abstractmethod



class BaseDocTest(ABC):
    """Base class for documentation tests."""

    @abstractmethod
    def get_docs_path(self) -> Path:
        """Return the path to the documentation directory to test."""
        pass

    def get_skip_patterns(self) -> list[str]:
        """Patterns to skip in code examples."""
        return [
            "pip install",
            "export OPENALEX",
            "# Don't do this",
            "# BAD:",
            "# DON'T DO THIS",
            "process(",
        ]

    def should_skip(self, example: CodeExample) -> str | None:
        """Check if example should be skipped, return reason if so."""
        if "python" not in example.prefix.lower() and example.path.suffix != ".py":
            return f"Non-Python code block ({example.prefix or 'unknown'})"

        code = example.source.strip()

        if code.startswith(("$", "pip ", "export ", "# ")):
            return "Shell command or comment"

        for pattern in self.get_skip_patterns():
            if pattern in code:
                return f"Contains skip pattern: {pattern}"

        if "your-api-key" in code and "config.api_key" in code:
            return "API key configuration example"

        return None

    def prepare_code(self, code: str) -> str:
        """Prepare code for execution."""
        return (
            code.replace("your-email@example.com", "test@example.com")
            .replace("your-email@institution.edu", "test@institution.edu")
        )

    @pytest.mark.docs
    def test_examples(self, example: CodeExample, mock_api_responses):
        """Test that each code example runs without errors."""
        skip_reason = self.should_skip(example)
        if skip_reason:
            pytest.skip(skip_reason)

        code = self.prepare_code(example.source)

        try:
            exec(compile(code, str(example.path), "exec"), {})
        except ImportError as e:
            if "pandas" in str(e):
                pytest.skip("Optional dependency not installed: pandas")
            raise
        except Exception as e:
            pytest.fail(
                f"Example failed at {example.path.name}:{example.start_line}\n"
                f"Code:\n{code}\n"
                f"Error: {type(e).__name__}: {e}"
            )


def parametrize_examples(test_class):
    """Decorator to parametrize test methods with examples."""
    instance = test_class()
    docs_path = instance.get_docs_path()

    if docs_path.is_file():
        md_paths = [docs_path]
    else:
        md_paths = list(docs_path.glob("*.md"))

    examples = []
    for path in md_paths:
        examples.extend(find_examples(path))

    orig_method = test_class.__dict__.get("test_examples", BaseDocTest.test_examples)

    def wrapped(self, example, mock_api_responses):
        return orig_method(self, example, mock_api_responses)

    if examples:
        wrapped = pytest.mark.parametrize(
            "example",
            examples,
            ids=lambda e: f"{e.path.name}::line-{e.start_line}",
        )(wrapped)
    else:
        wrapped = pytest.mark.skip(
            f"No examples found in {docs_path}"
        )(wrapped)

    test_class.test_examples = wrapped

    return test_class
