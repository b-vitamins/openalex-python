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

    def should_skip(self, example: CodeExample) -> str | None:
        """No skipping of documentation examples."""
        return None

    def prepare_code(self, code: str) -> str:
        """Return code unchanged."""
        return code

    @pytest.mark.docs
    def test_examples(self, example: CodeExample):
        """Test that each code example runs without errors."""
        code = self.prepare_code(example.source)
        exec(compile(code, str(example.path), "exec"), {})


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

    orig_method = test_class.__dict__.get(
        "test_examples", BaseDocTest.test_examples
    )

    def wrapped(self, example):
        return orig_method(self, example)

    if examples:
        wrapped = pytest.mark.parametrize(
            "example",
            examples,
            ids=lambda e: f"{e.path.name}::line-{e.start_line}",
        )(wrapped)
    else:
        wrapped = pytest.mark.skip(f"No examples found in {docs_path}")(wrapped)

    test_class.test_examples = wrapped

    return test_class
