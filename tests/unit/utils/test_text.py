"""
Test text processing utilities.
Tests utility functions for text manipulation like abstract inversion.
"""

import pytest


class TestAbstractInversion:
    """Test abstract inversion from inverted index format."""

    def test_invert_abstract_basic(self):
        """Test basic abstract reconstruction."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "This": [0],
            "is": [1],
            "a": [2],
            "test": [3],
            "abstract": [4],
        }

        result = invert_abstract(inverted_index)
        assert result == "This is a test abstract"

    def test_invert_abstract_repeated_words(self):
        """Test abstract with repeated words."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "The": [0, 4],
            "cat": [1, 5],
            "sat": [2],
            "on": [3],
            "mat": [6],
        }

        result = invert_abstract(inverted_index)
        assert result == "The cat sat on The cat mat"

    def test_invert_abstract_complex(self):
        """Test complex abstract with punctuation."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "Machine": [0],
            "learning": [1, 9],
            "is": [2, 10],
            "a": [3],
            "subset": [4],
            "of": [5],
            "artificial": [6],
            "intelligence.": [7],
            "Deep": [8],
            "powerful.": [11],
        }

        result = invert_abstract(inverted_index)
        expected = "Machine learning is a subset of artificial intelligence. Deep learning is powerful."
        assert result == expected

    def test_invert_abstract_empty(self):
        """Test empty inverted index."""
        from openalex.utils import invert_abstract

        assert invert_abstract({}) == ""
        assert invert_abstract(None) is None

    def test_invert_abstract_single_word(self):
        """Test single word abstract."""
        from openalex.utils import invert_abstract

        inverted_index = {"Hello": [0]}
        assert invert_abstract(inverted_index) == "Hello"

    def test_invert_abstract_out_of_order(self):
        """Test positions not in sequential order in dict."""
        from openalex.utils import invert_abstract

        inverted_index = {"world": [2], "Hello": [0], "beautiful": [1]}

        result = invert_abstract(inverted_index)
        assert result == "Hello beautiful world"

    def test_invert_abstract_unicode(self):
        """Test abstract with unicode characters."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "Schrödinger's": [0],
            "cat": [1],
            "is": [2],
            "alive": [3],
            "and": [4],
            "dead": [5],
            "😺": [6],
        }

        result = invert_abstract(inverted_index)
        assert result == "Schrödinger's cat is alive and dead 😺"

    def test_invert_abstract_with_gaps(self):
        """Test handling gaps in position sequence."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "First": [0],
            "Third": [2],  # Position 1 is missing
            "Fourth": [3],
        }

        # Should handle gaps gracefully
        result = invert_abstract(inverted_index)
        # Behavior depends on implementation - might insert placeholder or skip
        assert "First" in result
        assert "Third" in result
        assert "Fourth" in result

    def test_invert_abstract_large(self):
        """Test performance with large abstract."""
        from openalex.utils import invert_abstract

        # Generate large inverted index
        words = [f"word{i}" for i in range(1000)]
        inverted_index = {word: [i] for i, word in enumerate(words)}

        result = invert_abstract(inverted_index)

        # Should contain all words in order
        assert result.startswith("word0")
        assert result.endswith("word999")
        assert len(result.split()) == 1000

    def test_invert_abstract_special_characters(self):
        """Test handling of special characters and punctuation."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "COVID-19": [0],
            "(SARS-CoV-2)": [1],
            "emerged": [2],
            "in": [3],
            "2019.": [4],
            "[1]": [5],
            "It's": [6],
            "a": [7],
            "pandemic!": [8],
        }

        result = invert_abstract(inverted_index)
        expected = "COVID-19 (SARS-CoV-2) emerged in 2019. [1] It's a pandemic!"
        assert result == expected


class TestTextCleaning:
    """Test text cleaning utilities."""

    def test_clean_title(self):
        """Test title cleaning and normalization."""
        from openalex.utils import clean_title

        # Remove HTML tags
        assert (
            clean_title("The <i>Nature</i> of Science")
            == "The Nature of Science"
        )

        # Normalize whitespace
        assert clean_title("Too    many     spaces") == "Too many spaces"
        assert clean_title("\n\tWhitespace\r\n") == "Whitespace"

        # Trim length
        long_title = "A" * 1000
        cleaned = clean_title(long_title, max_length=100)
        assert len(cleaned) <= 100
        assert cleaned.endswith("...")

    def test_extract_doi_from_text(self):
        """Test DOI extraction from text."""
        from openalex.utils import extract_doi

        # Standard DOI formats
        assert extract_doi("doi: 10.1038/nature12373") == "10.1038/nature12373"
        assert extract_doi("DOI:10.1038/nature12373") == "10.1038/nature12373"
        assert (
            extract_doi("https://doi.org/10.1038/nature12373")
            == "10.1038/nature12373"
        )

        # In sentence
        text = "This paper (doi: 10.1038/nature12373) shows that..."
        assert extract_doi(text) == "10.1038/nature12373"

        # Multiple DOIs (return first)
        text = "See doi:10.1038/nature12373 and doi:10.1038/nature12374"
        assert extract_doi(text) == "10.1038/nature12373"

        # No DOI
        assert extract_doi("This text has no DOI") is None

    def test_normalize_author_name(self):
        """Test author name normalization."""
        from openalex.utils import normalize_author_name

        # Basic normalization
        assert normalize_author_name("John Smith") == "John Smith"
        assert normalize_author_name("JOHN SMITH") == "John Smith"
        assert normalize_author_name("john smith") == "John Smith"

        # Handle initials
        assert normalize_author_name("J. Smith") == "J. Smith"
        assert normalize_author_name("J.A. Smith") == "J.A. Smith"
        assert normalize_author_name("Smith, J.A.") == "J.A. Smith"

        # Unicode names
        assert normalize_author_name("José García") == "José García"
        assert normalize_author_name("李明") == "李明"

        # Remove extra spaces
        assert normalize_author_name("John   Smith") == "John Smith"

    def test_truncate_abstract(self):
        """Test abstract truncation with word boundaries."""
        from openalex.utils import truncate_abstract

        abstract = "This is a very long abstract that needs to be truncated at a reasonable word boundary to avoid cutting words in half."

        # Truncate at word boundary
        truncated = truncate_abstract(abstract, max_length=50)
        assert len(truncated) <= 50
        assert not truncated.endswith(" ")
        assert truncated.endswith("...")

        # Short abstract unchanged
        short = "Short abstract"
        assert truncate_abstract(short, max_length=50) == short

    def test_count_words(self):
        """Test word counting utility."""
        from openalex.utils import count_words

        assert count_words("Hello world") == 2
        assert count_words("Hello  world") == 2  # Multiple spaces
        assert count_words("Hello\nworld") == 2  # Newline
        assert count_words("") == 0
        assert count_words("   ") == 0
        assert count_words("COVID-19 pandemic") == 2  # Hyphenated counts as one
        assert count_words("The U.S.A. is...") == 3  # Abbreviations

    def test_extract_keywords(self):
        """Test keyword extraction from text."""
        from openalex.utils import extract_keywords

        text = "Machine learning and artificial intelligence are transforming healthcare"

        keywords = extract_keywords(text, max_keywords=3)

        # Should extract meaningful terms
        assert len(keywords) <= 3
        assert all(isinstance(k, str) for k in keywords)

        # Should ignore stop words
        assert "and" not in keywords
        assert "are" not in keywords

    def test_clean_html(self):
        """Test HTML cleaning from text."""
        from openalex.utils import clean_html

        # Remove tags
        assert clean_html("<p>Hello <b>world</b></p>") == "Hello world"
        assert clean_html("<script>alert('xss')</script>Text") == "Text"

        # Decode entities
        assert clean_html("A &amp; B") == "A & B"
        assert clean_html("&quot;quoted&quot;") == '"quoted"'
        assert clean_html("&lt;tag&gt;") == "<tag>"

        # Preserve newlines from block elements
        html = "<p>Paragraph 1</p><p>Paragraph 2</p>"
        cleaned = clean_html(html, preserve_newlines=True)
        assert "Paragraph 1\n" in cleaned
        assert "Paragraph 2" in cleaned

    def test_language_detection(self):
        """Test language detection utility."""
        from openalex.utils import detect_language

        # Common languages
        assert detect_language("This is an English text") == "en"
        assert detect_language("Ceci est un texte français") == "fr"
        assert detect_language("Este es un texto español") == "es"
        assert detect_language("Dies ist ein deutscher Text") == "de"
        assert detect_language("这是中文文本") == "zh"

        # Too short to detect
        assert detect_language("Hello") is None
        assert detect_language("") is None
