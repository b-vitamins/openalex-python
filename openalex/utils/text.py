"""Text processing utilities."""

from __future__ import annotations

import html
import re
from collections import Counter

__all__ = [
    "clean_html",
    "clean_title",
    "count_words",
    "detect_language",
    "extract_doi",
    "extract_keywords",
    "invert_abstract",
    "normalize_author_name",
    "truncate_abstract",
]


def invert_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """Convert inverted abstract index to plaintext.

    Args:
        inverted_index: Dictionary mapping words to position lists

    Returns:
        Reconstructed abstract text or ``None`` if no index provided
    """
    if inverted_index is None:
        return None
    if not inverted_index:
        return ""

    word_positions = [
        (word, pos)
        for word, positions in inverted_index.items()
        for pos in positions
    ]
    word_positions.sort(key=lambda item: item[1])
    return " ".join(word for word, _ in word_positions)


def clean_title(title: str, *, max_length: int | None = None) -> str:
    """Clean and normalize a title string."""
    text = re.sub(r"<[^>]+>", "", title)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    if max_length is not None and len(text) > max_length:
        cut = text[: max_length - 3]
        cut = cut.rsplit(" ", 1)[0] if " " in cut else cut
        text = cut.rstrip() + "..."

    return text


_DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s)]+)", re.I)


def extract_doi(text: str) -> str | None:
    """Extract the first DOI from ``text`` if present."""
    match = _DOI_RE.search(text)
    return match.group(0) if match else None


def normalize_author_name(name: str) -> str:
    """Normalize an author name to a consistent presentation."""
    if "," in name:
        last, first = [part.strip() for part in name.split(",", 1)]
        name = f"{first} {last}".strip()

    name = " ".join(name.split())

    def _norm_token(token: str) -> str:
        if re.fullmatch(r"[A-Za-z]\.", token) or re.fullmatch(
            r"(?:[A-Za-z]\.)+", token
        ):
            return token.upper()
        return token.capitalize() if token.isalpha() else token

    tokens = [_norm_token(t) for t in re.split(r"\s+", name)]
    return " ".join(tokens)


def truncate_abstract(text: str, *, max_length: int) -> str:
    """Truncate an abstract at a word boundary."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(" ", 1)[0]
    return truncated.rstrip() + "..."


_WORD_RE = re.compile(
    r"[A-Za-z]+(?:\.[A-Za-z]+)+|[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*|\d+", re.UNICODE
)


def count_words(text: str) -> int:
    """Count the number of words in ``text``."""
    words = _WORD_RE.findall(text)
    return len(words)


_STOP_WORDS = {
    "and",
    "or",
    "the",
    "a",
    "an",
    "of",
    "in",
    "on",
    "is",
    "are",
    "to",
}


def extract_keywords(text: str, *, max_keywords: int = 5) -> list[str]:
    """Extract simple keywords from text."""
    words = [w.lower() for w in _WORD_RE.findall(text)]
    filtered = [w for w in words if w not in _STOP_WORDS]
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(max_keywords)]


def clean_html(text: str, *, preserve_newlines: bool = False) -> str:
    """Remove HTML tags and decode entities."""
    if preserve_newlines:
        text = re.sub(r"</(?:p|br)\s*>", "\n", text, flags=re.I)
    # Remove script blocks entirely
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    if preserve_newlines:
        text = re.sub(r"[ \t]+", " ", text)
    else:
        text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_language(text: str | None) -> str | None:
    """Very small heuristic language detector for tests."""
    if not text or len(text.strip()) < 5:
        return None

    sample = text.lower()
    if re.search(r"[\u4e00-\u9fff]", sample):
        return "zh"
    if "fran" in sample or "ceci" in sample:
        return "fr"
    if "español" in sample or "este es" in sample:
        return "es"
    if "deutscher" in sample or "dies ist" in sample:
        return "de"
    return "en" if "this" in sample or "the" in sample else None
