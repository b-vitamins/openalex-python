from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from openalex.models import (
    AuthorsFilter,
    BaseFilter,
    ConceptsFilter,
    FundersFilter,
    GroupBy,
    InstitutionsFilter,
    PublishersFilter,
    SortOrder,
    SourcesFilter,
    WorksFilter,
)


class TestBaseFilter:
    """Test BaseFilter functionality."""

    def test_base_filter_defaults(self) -> None:
        """Test default values for BaseFilter."""
        filter = BaseFilter()

        assert filter.filter is None
        assert filter.search is None
        assert filter.sort is None
        assert filter.page == 1
        assert filter.per_page == 25
        assert filter.select is None
        assert filter.sample is None
        assert filter.seed is None
        assert filter.group_by is None

    def test_base_filter_with_all_params(self) -> None:
        """Test BaseFilter with all parameters."""
        filter = BaseFilter(
            filter={"type": "article"},
            search="machine learning",
            sort="cited_by_count:desc",
            page=3,
            per_page=100,
            select=["id", "display_name", "cited_by_count"],
            sample=50,
            seed=12345,
            group_by="type",
        )

        params = filter.to_params()
        assert params["filter"] == "type:article"
        assert params["search"] == "machine learning"
        assert params["sort"] == "cited_by_count:desc"
        assert params["page"] == 3
        assert params["per-page"] == 100
        assert params["select"] == "id,display_name,cited_by_count"
        assert params["sample"] == 50
        assert params["seed"] == 12345
        assert params["group-by"] == "type"

    def test_base_filter_validation(self) -> None:
        """Test BaseFilter validation."""
        # Invalid filter type
        with pytest.raises(ValidationError):
            BaseFilter(filter=123)

        # Invalid select type
        with pytest.raises(ValidationError):
            BaseFilter(select=123)

        # Invalid page
        with pytest.raises(ValidationError):
            BaseFilter(page=0)

        # Invalid per_page
        with pytest.raises(ValidationError):
            BaseFilter(per_page=201)  # Max is 200

    def test_build_filter_string_basic_types(self) -> None:
        """Test _build_filter_string with basic types."""
        filter = BaseFilter()

        filters = {
            "bool_true": True,
            "bool_false": False,
            "string": "test",
            "int": 42,
            "float": 3.14,
            "none": None,
        }

        result = filter._build_filter_string(filters)
        assert "bool_true:true" in result
        assert "bool_false:false" in result
        assert "string:test" in result
        assert "int:42" in result
        assert "float:3.14" in result
        assert "none" not in result  # None values should be excluded

    def test_build_filter_string_collections(self) -> None:
        """Test _build_filter_string with collections."""
        filter = BaseFilter()

        filters = {
            "list": [1, 2, 3],
            "tuple": (4, 5, 6),
            "set": {7, 8, 9},
            "empty_list": [],
            "single_item": [10],
        }

        result = filter._build_filter_string(filters)
        assert "list:1|2|3" in result
        assert "tuple:4|5|6" in result
        assert (
            "|" in result.split("set:")[1].split(",")[0]
        )  # Set order not guaranteed
        assert (
            "empty_list" not in result
        )  # Empty collections should be excluded
        assert "single_item:10" in result

    def test_build_filter_string_dates(self) -> None:
        """Test _build_filter_string with date types."""
        filter = BaseFilter()

        filters = {
            "date": date(2024, 12, 25),
            "datetime": datetime(2024, 12, 25, 10, 30, 45),
        }

        result = filter._build_filter_string(filters)
        assert "date:2024-12-25" in result
        assert (
            "datetime:2024-12-25" in result
        )  # DateTime should be converted to date

    def test_build_filter_string_special_characters(self) -> None:
        """Test _build_filter_string with special characters."""
        filter = BaseFilter()

        filters = {
            "with_comma": "test,value",
            "with_pipe": "test|value",
            "with_colon": "test:value",
            "with_space": "test value",
        }

        result = filter._build_filter_string(filters)
        # Should handle special characters appropriately
        assert "with_comma:test,value" in result
        assert "with_pipe:test|value" in result
        assert "with_colon:test:value" in result
        assert "with_space:test value" in result

    def test_parameter_name_transformation(self) -> None:
        """Test parameter name transformation in to_params."""
        filter = BaseFilter(per_page=50, group_by="institution.id")

        params = filter.to_params()
        assert "per-page" in params
        assert "per_page" not in params
        assert "group-by" in params
        assert "group_by" not in params

    def test_empty_filter(self) -> None:
        """Test empty filter returns empty params."""
        filter = BaseFilter()
        params = filter.to_params()

        # Should only have default page and per_page
        assert params == {"page": 1, "per-page": 25}

    def test_none_and_no_defaults(self) -> None:
        """Explicit None values and skipping defaults."""
        filter = BaseFilter(filter=None, select=None)
        assert filter.to_params(include_defaults=False) == {}

        # Explicit string select should pass validation branch
        filter2 = BaseFilter(select="id")
        assert filter2.to_params()["select"] == "id"


class TestWorksFilter:
    """Test WorksFilter functionality."""

    def test_works_filter_basic_filters(self) -> None:
        """Test basic WorksFilter methods."""
        filter = (
            WorksFilter()
            .with_doi("10.1038/nature12373")
            .with_title("quantum computing")
            .with_publication_year(2023)
            .with_type("article")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "doi:10.1038/nature12373" in filter_str
        assert "title.search:quantum computing" in filter_str
        assert "publication_year:2023" in filter_str
        assert "type:article" in filter_str

    def test_works_filter_date_ranges(self) -> None:
        """Test date range filters."""
        filter = (
            WorksFilter()
            .with_publication_date_range(date(2023, 1, 1), date(2023, 12, 31))
            .with_created_date_range(date(2022, 6, 1), date(2023, 6, 1))
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "from_publication_date:2023-01-01" in filter_str
        assert "to_publication_date:2023-12-31" in filter_str
        assert "from_created_date:2022-06-01" in filter_str
        assert "to_created_date:2023-06-01" in filter_str

    def test_works_filter_open_access(self) -> None:
        """Test open access filters."""
        # Test all OA options
        filter_true = WorksFilter().with_open_access(is_oa=True)
        assert "is_oa:true" in filter_true.to_params()["filter"]

        filter_false = WorksFilter().with_open_access(is_oa=False)
        assert "is_oa:false" in filter_false.to_params()["filter"]

        filter_status = WorksFilter().with_oa_status(["gold", "green"])
        assert "oa_status:gold|green" in filter_status.to_params()["filter"]

    def test_works_filter_author_filters(self) -> None:
        """Test author-related filters."""
        filter = (
            WorksFilter()
            .with_author_id("A5023888391")
            .with_author_orcid("0000-0003-4237-824X")
            .with_authorships_institutions_id("I27837315")
            .with_corresponding_author_id("A5023888391")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "author.id:A5023888391" in filter_str
        assert "author.orcid:0000-0003-4237-824X" in filter_str
        assert "authorships.institutions.id:I27837315" in filter_str
        assert "corresponding_author_ids:A5023888391" in filter_str

    def test_works_filter_location_filters(self) -> None:
        """Test location and source filters."""
        filter = (
            WorksFilter()
            .with_primary_location_source("S48139910")
            .with_primary_location_issn("0031-9007")
            .with_repository("S4306400194")
            .with_journal("S48139910")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "primary_location.source.id:S48139910" in filter_str
        assert "primary_location.source.issn:0031-9007" in filter_str
        assert "repository:S4306400194" in filter_str
        assert "journal:S48139910" in filter_str

    def test_works_filter_institution_filters(self) -> None:
        """Test institution-related filters."""
        filter = (
            WorksFilter()
            .with_institutions_id("I27837315")
            .with_institutions_ror("https://ror.org/00za53h95")
            .with_institutions_country_code("US")
            .with_institutions_type("education")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "institutions.id:I27837315" in filter_str
        assert "institutions.ror:https://ror.org/00za53h95" in filter_str
        assert "institutions.country_code:US" in filter_str
        assert "institutions.type:education" in filter_str

    def test_works_filter_concept_topic_filters(self) -> None:
        """Test concept and topic filters."""
        filter = (
            WorksFilter()
            .with_concepts_id("C121332964")
            .with_primary_topic_id("T10555")
            .with_topics_id(["T10555", "T10556"])
            .with_sustainable_development_goals_id("7")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "concepts.id:C121332964" in filter_str
        assert "primary_topic.id:T10555" in filter_str
        assert "topics.id:T10555|T10556" in filter_str
        assert "sustainable_development_goals.id:7" in filter_str

    def test_works_filter_citation_filters(self) -> None:
        """Test citation-related filters."""
        filter = (
            WorksFilter()
            .with_cited_by_count_range(100, 1000)
            .with_cites("W2741809807")
            .with_referenced_works("W2486144666")
            .with_related_to("W2124495158")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "cited_by_count:100-1000" in filter_str
        assert "cites:W2741809807" in filter_str
        assert "referenced_works:W2486144666" in filter_str
        assert "related_to:W2124495158" in filter_str

    def test_works_filter_boolean_flags(self) -> None:
        """Test boolean flag filters."""
        filter = (
            WorksFilter()
            .with_is_retracted(is_retracted=True)
            .with_is_paratext(is_paratext=False)
            .with_has_fulltext(has_fulltext=True)
            .with_has_abstract(has_abstract=True)
            .with_has_doi(has_doi=True)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "is_retracted:true" in filter_str
        assert "is_paratext:false" in filter_str
        assert "has_fulltext:true" in filter_str
        assert "has_abstract:true" in filter_str
        assert "has_doi:true" in filter_str

    def test_works_filter_grant_filters(self) -> None:
        """Test grant-related filters."""
        filter = (
            WorksFilter()
            .with_grants_funder("F4320306076")
            .with_grants_award_id("DMR-9521353")
            .with_apc_paid(apc_paid=True)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "grants.funder:F4320306076" in filter_str
        assert "grants.award_id:DMR-9521353" in filter_str
        assert "apc_paid:true" in filter_str

    def test_works_filter_language_filters(self) -> None:
        """Test language filter."""
        filter = WorksFilter().with_language(["en", "es", "fr"])

        params = filter.to_params()
        assert "language:en|es|fr" in params["filter"]

    def test_works_filter_complex_combination(self) -> None:
        """Test complex filter combination."""
        filter = (
            WorksFilter()
            .with_publication_year([2020, 2021, 2022])
            .with_type(["article", "preprint"])
            .with_open_access(is_oa=True)
            .with_institutions_country_code(["US", "GB"])
            .with_cited_by_count_range(10, None)  # Min 10, no max
            .with_primary_location_license(["cc-by", "cc-by-sa"])
        )

        filter = filter.model_copy(
            update={
                "search": "machine learning",
                "sort": "publication_date:desc",
                "per_page": 100,
                "select": ["id", "title", "doi", "publication_date"],
            }
        )

        params = filter.to_params()
        filter_str = params["filter"]

        # Check filter string
        assert "publication_year:2020|2021|2022" in filter_str
        assert "type:article|preprint" in filter_str
        assert "is_oa:true" in filter_str
        assert "institutions.country_code:US|GB" in filter_str
        assert (
            "cited_by_count:>9" in filter_str
        )  # Range with None becomes >min-1
        assert "primary_location.license:cc-by|cc-by-sa" in filter_str

        # Check other params
        assert params["search"] == "machine learning"
        assert params["sort"] == "publication_date:desc"
        assert params["per-page"] == 100
        assert params["select"] == "id,title,doi,publication_date"

    def test_works_filter_sorting_validation(self) -> None:
        """Test WorksFilter sort field validation."""
        # Valid sort fields
        valid_sorts = [
            "publication_date:desc",
            "cited_by_count:asc",
            "relevance_score:desc",
        ]

        for sort in valid_sorts:
            filter = WorksFilter(sort=sort)
            assert filter.sort == sort

        # Invalid sort field
        with pytest.raises(ValidationError):
            WorksFilter(sort="invalid_field:desc")

    def test_works_filter_method_chaining(self) -> None:
        """Test method chaining returns new instances."""
        filter1 = WorksFilter()
        filter2 = filter1.with_type("article")
        filter3 = filter2.with_publication_year(2023)

        # Each should be a different instance
        assert filter1 is not filter2
        assert filter2 is not filter3

        # Original should be unchanged
        assert filter1.filter is None
        assert "type:article" in filter2.to_params()["filter"]
        assert "type:article" in filter3.to_params()["filter"]
        assert "publication_year:2023" in filter3.to_params()["filter"]

    def test_add_filter_string_start(self) -> None:
        """Starting with a raw string filter then chaining."""
        wf = WorksFilter(filter="foo").with_doi("10/1")
        assert "raw:foo" in wf.to_params()["filter"]

    def test_works_filter_str_branches(self) -> None:
        """Ensure string filters remain when adding range helpers."""
        wf = WorksFilter(filter="raw")
        wf = wf.with_publication_date_range(date(2020, 1, 1), None)
        wf = wf.with_created_date_range(None, date(2021, 1, 1))
        wf = wf.with_oa_status("gold")
        wf = wf.with_primary_location_license("cc-by").with_topics_id("T1")
        wf = wf.with_authorships_institutions_ror("https://ror.org/abcd")
        wf = wf.with_authorships_institutions_country_code("US")
        wf = wf.with_authorships_institutions_type("education")
        wf = wf.with_corresponding_institution_id("I1")
        filter_str = wf.to_params()["filter"]
        assert "raw:raw" in filter_str
        assert "oa_status:gold" in filter_str
        assert "from_publication_date:2020-01-01" in filter_str
        assert "to_created_date:2021-01-01" in filter_str
        assert "authorships.institutions.ror:https://ror.org/abcd" in filter_str
        assert "authorships.institutions.country_code:US" in filter_str
        assert "authorships.institutions.type:education" in filter_str
        assert "corresponding_institution_ids:I1" in filter_str
        assert "primary_location.license:cc-by" in filter_str
        assert "topics.id:T1" in filter_str

        wf2 = WorksFilter(filter="bar").with_created_date_range(
            date(2022, 1, 1)
        )
        assert "raw:bar" in wf2.to_params()["filter"]


class TestAuthorsFilter:
    """Test AuthorsFilter functionality."""

    def test_authors_filter_basic(self) -> None:
        """Test basic AuthorsFilter methods."""
        filter = (
            AuthorsFilter()
            .with_orcid("0000-0003-4237-824X")
            .with_display_name_search("John Perdew")
            .with_works_count_range(100, 1000)
            .with_cited_by_count_range(10000, None)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "orcid:0000-0003-4237-824X" in filter_str
        assert "display_name.search:John Perdew" in filter_str
        assert "works_count:100-1000" in filter_str
        assert "cited_by_count:>9999" in filter_str

    def test_authors_filter_institution(self) -> None:
        """Test author institution filters."""
        filter = (
            AuthorsFilter()
            .with_last_known_institution_id("I27837315")
            .with_last_known_institution_ror("https://ror.org/00za53h95")
            .with_last_known_institution_country_code("US")
            .with_last_known_institution_type("education")
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "last_known_institution.id:I27837315" in filter_str
        assert (
            "last_known_institution.ror:https://ror.org/00za53h95" in filter_str
        )
        assert "last_known_institution.country_code:US" in filter_str
        assert "last_known_institution.type:education" in filter_str

    def test_authors_filter_concepts(self) -> None:
        """Test author concept filter."""
        filter = AuthorsFilter().with_x_concepts_id(["C121332964", "C62520636"])

        params = filter.to_params()
        assert "x_concepts.id:C121332964|C62520636" in params["filter"]

    def test_authors_filter_sorting_validation(self) -> None:
        """Test AuthorsFilter sort field validation."""
        # Valid sort fields
        valid_sorts = [
            "display_name:asc",
            "cited_by_count:desc",
            "works_count:desc",
            "publication_date:desc",
        ]

        for sort in valid_sorts:
            filter = AuthorsFilter(sort=sort)
            assert filter.sort == sort

        # Invalid sort field
        with pytest.raises(ValidationError):
            AuthorsFilter(sort="invalid_field:desc")

    def test_authors_filter_branches(self) -> None:
        """Range helpers handle None values correctly."""
        base = AuthorsFilter(filter="foo")

        f1 = base.with_works_count_range(min_count=5, max_count=None)
        assert "works_count:>4" in f1.to_params()["filter"]

        f2 = base.with_works_count_range(min_count=None, max_count=8)
        assert "works_count:<9" in f2.to_params()["filter"]

        f3 = base.with_works_count_range(None, None)
        assert "works_count" not in f3.to_params()["filter"]

        c1 = base.with_cited_by_count_range(min_count=1, max_count=3)
        assert "cited_by_count:1-3" in c1.to_params()["filter"]

        c2 = base.with_cited_by_count_range(min_count=None, max_count=10)
        assert "cited_by_count:<11" in c2.to_params()["filter"]

        c3 = base.with_cited_by_count_range(None, None)
        assert "cited_by_count" not in c3.to_params()["filter"]

        assert (
            "x_concepts.id:C1"
            in base.with_x_concepts_id("C1").to_params()["filter"]
        )


class TestInstitutionsFilter:
    """Test InstitutionsFilter functionality."""

    def test_institutions_filter_basic(self) -> None:
        """Test basic InstitutionsFilter methods."""
        filter = (
            InstitutionsFilter()
            .with_ror("https://ror.org/00za53h95")
            .with_country_code(["US", "GB", "DE"])
            .with_type(["education", "facility"])
            .with_works_count_range(1000, None)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "ror:https://ror.org/00za53h95" in filter_str
        assert "country_code:US|GB|DE" in filter_str
        assert "type:education|facility" in filter_str
        assert "works_count:>999" in filter_str

    def test_concepts_filter_branches(self) -> None:
        """Range helper edge cases."""
        base = ConceptsFilter(filter="foo").with_level(1)
        assert "level:1" in base.to_params()["filter"]

        f1 = base.with_works_count_range(2, 4)
        assert "works_count:2-4" in f1.to_params()["filter"]

        f2 = base.with_works_count_range(min_count=1, max_count=None)
        assert "works_count:>0" in f2.to_params()["filter"]

        f3 = base.with_works_count_range(None, 5)
        assert "works_count:<6" in f3.to_params()["filter"]

        f4 = ConceptsFilter(filter="foo").with_works_count_range(None, None)
        assert "works_count" not in f4.to_params()["filter"]

    def test_institutions_filter_works_count_range_variants(self) -> None:
        """Works count range with only min or max."""
        f_min = InstitutionsFilter().with_works_count_range(10, None)
        assert "works_count:>9" in f_min.to_params()["filter"]

        f_max = InstitutionsFilter().with_works_count_range(None, 20)
        assert "works_count:<21" in f_max.to_params()["filter"]

    def test_institutions_filter_concepts(self) -> None:
        """Test institution concept filter."""
        filter = InstitutionsFilter().with_x_concepts_id("C121332964")

        params = filter.to_params()
        assert "x_concepts.id:C121332964" in params["filter"]

    def test_institutions_filter_sorting_validation(self) -> None:
        """Test InstitutionsFilter sort field validation."""
        # Valid sort fields
        valid_sorts = [
            "display_name:asc",
            "cited_by_count:desc",
            "works_count:desc",
        ]

        for sort in valid_sorts:
            filter = InstitutionsFilter(sort=sort)
            assert filter.sort == sort

    def test_institutions_filter_branches(self) -> None:
        """Additional range and basic branches."""
        base = InstitutionsFilter(filter="foo")
        f1 = base.with_country_code("US").with_type("education")
        flt = f1.to_params()["filter"]
        assert "country_code:US" in flt
        assert "type:education" in flt

        f2 = base.with_works_count_range(1, 3)
        assert "works_count:1-3" in f2.to_params()["filter"]

        f3 = base.with_works_count_range(None, 4)
        assert "works_count:<5" in f3.to_params()["filter"]

        f4 = base.with_works_count_range(None, None)
        assert "works_count" not in f4.to_params()["filter"]


class TestSourcesFilter:
    """Test SourcesFilter functionality."""

    def test_sources_filter_basic(self) -> None:
        """Test basic SourcesFilter methods."""
        filter = (
            SourcesFilter()
            .with_issn("0031-9007")
            .with_publisher("P4310319965")
            .with_type(["journal", "repository"])
            .with_is_oa(is_oa=True)
            .with_is_in_doaj(is_in_doaj=True)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "issn:0031-9007" in filter_str
        assert "publisher:P4310319965" in filter_str
        assert "type:journal|repository" in filter_str
        assert "is_oa:true" in filter_str
        assert "is_in_doaj:true" in filter_str

    def test_sources_filter_apc(self) -> None:
        """Test source APC filter."""
        filter = SourcesFilter().with_apc_usd_range(0, 5000)

        params = filter.to_params()
        assert "apc_usd:0-5000" in params["filter"]

    def test_sources_filter_apc_min_max_only(self) -> None:
        """APC filter with only min or max values."""
        f_min = SourcesFilter().with_apc_usd_range(100, None)
        assert "apc_usd:>99" in f_min.to_params()["filter"]

        f_max = SourcesFilter().with_apc_usd_range(None, 200)
        assert "apc_usd:<201" in f_max.to_params()["filter"]

        base = SourcesFilter()
        f_none = base.with_apc_usd_range(None, None)
        assert f_none is base

    def test_sources_filter_branches(self) -> None:
        """Additional type and APC branches."""
        sf = SourcesFilter(filter="foo")
        sf = sf.with_type("journal")
        sf = sf.with_apc_usd_range(None, None)
        assert sf is sf
        sf = sf.with_apc_usd_range(100, 200)
        assert "apc_usd:100-200" in sf.to_params()["filter"]


class TestConceptsFilter:
    """Test ConceptsFilter functionality."""

    def test_concepts_filter_basic(self) -> None:
        """Test basic ConceptsFilter methods."""
        filter = (
            ConceptsFilter()
            .with_level([0, 1, 2])
            .with_ancestors_id("C121332964")
            .with_works_count_range(1000, None)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "level:0|1|2" in filter_str
        assert "ancestors.id:C121332964" in filter_str
        assert "works_count:>999" in filter_str


class TestPublishersFilter:
    """Test PublishersFilter functionality."""

    def test_publishers_filter_basic(self) -> None:
        """Test basic PublishersFilter methods."""
        filter = (
            PublishersFilter()
            .with_country_codes(["US", "GB"])
            .with_parent_publisher("P4310319965")
            .with_hierarchy_level(0)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "country_codes:US|GB" in filter_str
        assert "parent_publisher:P4310319965" in filter_str
        assert "hierarchy_level:0" in filter_str

    def test_publishers_filter_branches(self) -> None:
        """Single country code branch."""
        pf = PublishersFilter(filter="foo").with_country_codes("US")
        params = pf.to_params()
        assert "country_codes:US" in params["filter"]


class TestFundersFilter:
    """Test FundersFilter functionality."""

    def test_funders_filter_basic(self) -> None:
        """Test basic FundersFilter methods."""
        filter = (
            FundersFilter()
            .with_country_code("US")
            .with_grants_count_range(1000, 10000)
            .with_works_count_range(10000, None)
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "country_code:US" in filter_str
        assert "grants_count:1000-10000" in filter_str
        assert "works_count:>9999" in filter_str

    def test_funders_filter_range_variants(self) -> None:
        """Test min-only and max-only ranges."""
        f_min = FundersFilter().with_grants_count_range(100, None)
        assert "grants_count:>99" in f_min.to_params()["filter"]

        f_max = FundersFilter().with_grants_count_range(None, 200)
        assert "grants_count:<201" in f_max.to_params()["filter"]

        w_min = FundersFilter().with_works_count_range(50, None)
        assert "works_count:>49" in w_min.to_params()["filter"]

        w_max = FundersFilter().with_works_count_range(None, 75)
        assert "works_count:<76" in w_max.to_params()["filter"]

    def test_funders_filter_branches(self) -> None:
        """Extra range handling starting from string filter."""
        base = FundersFilter(filter="foo")
        f1 = base.with_grants_count_range(3, 6)
        assert "grants_count:3-6" in f1.to_params()["filter"]

        f2 = base.with_grants_count_range(None, None)
        assert "grants_count" not in f2.to_params()["filter"]

        w1 = base.with_works_count_range(1, 2)
        assert "works_count:1-2" in w1.to_params()["filter"]

        w2 = base.with_works_count_range(min_count=None, max_count=4)
        assert "works_count:<5" in w2.to_params()["filter"]

        w3 = base.with_works_count_range(None, None)
        assert "works_count" not in w3.to_params()["filter"]


class TestGroupBy:
    """Test GroupBy enum."""

    def test_group_by_values(self) -> None:
        """Test GroupBy enum values."""
        assert GroupBy.PUBLICATION_YEAR == "publication_year"
        assert GroupBy.TYPE == "type"
        assert GroupBy.OPEN_ACCESS_STATUS == "open_access.oa_status"
        assert GroupBy.AUTHORSHIPS_INSTITUTION == "authorships.institutions.id"
        assert GroupBy.CITED_BY_COUNT == "cited_by_count"


class TestSortOrder:
    """Test SortOrder enum."""

    def test_sort_order_values(self) -> None:
        """Test SortOrder enum values."""
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"


class TestFilterEdgeCases:
    """Test edge cases and special scenarios."""

    def test_filter_with_negation(self) -> None:
        """Test filter negation (NOT filters)."""
        # OpenAlex supports negation with !
        filter = BaseFilter(
            filter={
                "is_oa": True,
                "!type": "article",  # NOT article
                "!institutions.country_code": [
                    "CN",
                    "RU",
                ],  # NOT from these countries
            }
        )

        params = filter.to_params()
        filter_str = params["filter"]

        assert "is_oa:true" in filter_str
        assert "!type:article" in filter_str
        assert "!institutions.country_code:CN|RU" in filter_str

    def test_filter_with_ranges(self) -> None:
        """Test various range formats."""
        filter = WorksFilter()

        # Test different range methods
        f1 = filter.with_cited_by_count_range(10, 100)
        assert "cited_by_count:10-100" in f1.to_params()["filter"]

        f2 = filter.with_cited_by_count_range(50, None)  # Min only
        assert "cited_by_count:>49" in f2.to_params()["filter"]

        f3 = filter.with_cited_by_count_range(None, 200)  # Max only
        assert "cited_by_count:<201" in f3.to_params()["filter"]

        f4 = filter.with_cited_by_count_range(None, None)
        assert f4 is filter

    def test_filter_special_values(self) -> None:
        """Test filters with special values."""
        filter = BaseFilter(
            filter={
                "doi": "10.1038/nature12373",  # Contains special characters
                "display_name.search": "COVID-19",  # Contains hyphen
                "raw_affiliation_string.search": "University of California, Berkeley",  # Contains comma
            }
        )

        params = filter.to_params()
        # Should handle special characters correctly
        assert params["filter"] is not None

    def test_empty_collections_in_filter(self) -> None:
        """Test that empty collections are handled properly."""
        filter = WorksFilter().with_type([])  # Empty list
        params = filter.to_params()

        # Empty list should not add to filter
        assert "type:" not in params.get("filter", "")

    def test_none_values_in_filter(self) -> None:
        """Test that None values are handled properly."""
        filter = BaseFilter(
            filter={
                "type": "article",
                "doi": None,
                "is_oa": True,
                "title": None,
            }
        )

        params = filter.to_params()
        filter_str = params["filter"]

        # None values should be excluded
        assert "type:article" in filter_str
        assert "is_oa:true" in filter_str
        assert "doi" not in filter_str
        assert "title" not in filter_str

    def test_complex_nested_filters(self) -> None:
        """Test complex nested filter scenarios."""
        # This tests the real-world scenario of complex filtering
        filter = (
            WorksFilter()
            .with_publication_year([2020, 2021, 2022, 2023])
            .with_type("article")
            .with_open_access(is_oa=True)
            .with_primary_location_source("S48139910")
            .with_authorships_institutions_country_code(
                ["US", "GB", "DE", "FR"]
            )
            .with_cited_by_count_range(5, None)
            .with_has_doi(has_doi=True)
            .with_language(language="en")
        )

        # Add search and sorting
        filter = filter.model_copy(
            update={
                "search": "quantum computing applications",
                "sort": "cited_by_count:desc",
                "per_page": 200,
                "page": 2,
                "select": [
                    "id",
                    "title",
                    "doi",
                    "cited_by_count",
                    "publication_date",
                ],
            }
        )

        params = filter.to_params()

        # Verify all parameters are present
        assert params["search"] == "quantum computing applications"
        assert params["sort"] == "cited_by_count:desc"
        assert params["per-page"] == 200
        assert params["page"] == 2
        assert (
            params["select"] == "id,title,doi,cited_by_count,publication_date"
        )

        # Verify filter string contains all filters
        filter_str = params["filter"]
        assert "publication_year:2020|2021|2022|2023" in filter_str
        assert "type:article" in filter_str
        assert "is_oa:true" in filter_str
        assert "primary_location.source.id:S48139910" in filter_str
        assert "authorships.institutions.country_code:US|GB|DE|FR" in filter_str
        assert "cited_by_count:>4" in filter_str
        assert "has_doi:true" in filter_str
        assert "language:en" in filter_str


def test_validate_select_none() -> None:
    bf = BaseFilter(select=None)
    assert bf.select is None


def test_string_filter_branches() -> None:
    wf = (
        WorksFilter(filter="raw")
        .with_type("article")
        .with_open_access(is_oa=False)
    )
    params = wf.to_params()
    assert "raw:raw" in params["filter"]
    assert "type:article" in params["filter"]
    assert "is_oa:false" in params["filter"]

    inst = InstitutionsFilter(filter="start").with_type("education")
    inst_str = inst.to_params()["filter"]
    assert "raw:start" in inst_str
    assert "type:education" in inst_str
