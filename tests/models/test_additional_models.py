from openalex.models import (
    Funder,
    Institution,
    Keyword,
    Publisher,
    Source,
    SourceType,
    Topic,
)
from openalex.models import work as work_models


def test_funder_metrics_and_government() -> None:
    funder = Funder(
        id="F1",
        display_name="National Science Department",
        grants_count=10,
        works_count=5,
    )
    assert funder.funding_per_work == 2
    assert funder.is_government_funder()


def test_funder_no_works() -> None:
    funder = Funder(
        id="F2", display_name="Private Org", works_count=0, grants_count=1
    )
    assert funder.funding_per_work is None
    assert not funder.is_government_funder()


def test_institution_extras() -> None:
    inst = Institution(
        id="I1", display_name="Solo", lineage=["I1"], repositories=[]
    )
    assert inst.parent_institution is None
    assert inst.root_institution is None
    assert inst.repository_count() == 0
    assert not inst.has_location()

    inst2 = Institution(
        id="I2",
        display_name="Located",
        geo={"latitude": 1.0, "longitude": 2.0},
        repositories=[{"id": "R1", "display_name": "Repo1"}],
    )
    assert inst2.repository_count() == 1
    assert inst2.has_location()


def test_publisher_properties() -> None:
    pub = Publisher(
        id="P1",
        display_name="Pub",
        hierarchy_level=0,
        country_codes=["US"],
        parent_publisher=None,
    )
    assert pub.is_parent_publisher is True
    assert pub.countries == ["US"]
    assert pub.has_parent() is False


def test_source_repository_and_issns() -> None:
    source = Source(
        id="S1",
        display_name="Repo",
        type=SourceType.REPOSITORY,
        issn_l="1234-5678",
        issn=["1111-2222"],
    )
    assert source.is_repository
    assert source.all_issns() == ["1234-5678", "1111-2222"]


def test_topic_levels_and_keywords() -> None:
    topic = Topic(
        id="T1",
        display_name="AI",
        domain={"id": "D", "display_name": "Domain"},
        keywords=["Machine", "Learning"],
    )
    assert topic.level == 0
    assert topic.has_keyword("machine")
    assert not topic.has_keyword("other")

    topic2 = Topic(
        id="T2", display_name="Sub", field={"id": "F", "display_name": "Field"}
    )
    assert topic2.level == 1

    topic3 = Topic(
        id="T3",
        display_name="Deep",
        subfield={"id": "S", "display_name": "Sub"},
    )
    assert topic3.level == 2


def test_keyword_not_popular() -> None:
    kw = Keyword(id="K1", display_name="test")
    assert kw.average_citations_per_work is None
    assert not kw.is_popular(threshold=1)


def test_work_module_filters() -> None:
    filt = (
        work_models.WorksFilter()
        .with_publication_year(2020)
        .with_type("article")
    )
    params = filt.with_open_access().to_params()
    assert "publication_year:2020" in params["filter"]
    assert "type:article" in params["filter"]
    assert "is_oa:true" in params["filter"]
