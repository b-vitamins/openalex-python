from openalex.models import (
    Author,
    AuthorAffiliation,
    CountsByYear,
    DehydratedConcept,
    DehydratedInstitution,
    SummaryStats,
)


def _make_author() -> Author:
    return Author(
        id="A1",
        display_name="Test Author",
        summary_stats=SummaryStats(h_index=5, i10_index=10),
        counts_by_year=[
            CountsByYear(year=2020, works_count=2, cited_by_count=5),
            CountsByYear(year=2021, works_count=3, cited_by_count=7),
        ],
        affiliations=[
            AuthorAffiliation(
                institution=DehydratedInstitution(
                    id="I1", display_name="Inst A"
                ),
                years=[2020, 2021],
            ),
            AuthorAffiliation(
                institution=DehydratedInstitution(
                    id="I1", display_name="Inst A"
                ),
                years=[2021],
            ),
        ],
        x_concepts=[
            DehydratedConcept(id="C1", display_name="AI"),
            DehydratedConcept(id="C2", display_name=None),
        ],
    )


def test_author_computed_properties() -> None:
    author = _make_author()
    # summary stats
    assert author.h_index == 5
    assert author.i10_index == 10
    # counts and years
    assert author.most_cited_work_count == 7
    assert author.works_in_year(2021) == 3
    assert author.works_in_year(2019) == 0
    assert author.citations_in_year(2020) == 5
    assert author.citations_in_year(2018) == 0
    assert author.active_years() == [2020, 2021]
    # affiliations and concepts
    assert author.institution_names() == ["Inst A"]
    assert author.concept_names() == ["AI"]


def test_most_cited_work_no_counts() -> None:
    author = Author(id="A2", display_name="Empty")
    assert author.most_cited_work_count == 0
