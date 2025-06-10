"""Text processing utilities."""

from __future__ import annotations

__all__ = ["invert_abstract"]


def invert_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """Convert inverted abstract index to plaintext.

    Args:
        inverted_index: Dictionary mapping words to position lists

    Returns:
        Reconstructed abstract text or ``None`` if no index provided
    """
    if not inverted_index:
        return None

    word_positions = [
        (word, pos)
        for word, positions in inverted_index.items()
        for pos in positions
    ]
    word_positions.sort(key=lambda item: item[1])
    return " ".join(word for word, _ in word_positions)
