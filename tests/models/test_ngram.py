from openalex.models.work import Ngram


def test_ngram_model() -> None:
    ngram = Ngram(
        ngram="machine learning",
        ngram_count=42,
        ngram_tokens=2,
        term_frequency=0.05,
    )
    assert ngram.ngram == "machine learning"
    assert ngram.ngram_count == 42
    assert ngram.ngram_tokens == 2
    assert ngram.term_frequency == 0.05
