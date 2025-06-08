"""Expose models from the OpenAlex API client."""
from __future__ import annotations

from .all_of_text_concepts_results_concepts_items import (
    AllOfTextConceptsResultsConceptsItems,
)
from .all_of_text_results_concepts_items import AllOfTextResultsConceptsItems
from .all_of_text_results_topics_items import AllOfTextResultsTopicsItems
from .all_of_text_topics_results_topics_items import (
    AllOfTextTopicsResultsTopicsItems,
)
from .apc import APC
from .associated_institution import AssociatedInstitution
from .author import Author
from .author_affiliations import AuthorAffiliations
from .author_ids import AuthorIds
from .authors_list import AuthorsList
from .authorship import Authorship
from .authorship_affiliations import AuthorshipAffiliations
from .autocomplete_result import AutocompleteResult
from .autocomplete_results import AutocompleteResults
from .biblio import Biblio
from .concept import Concept
from .concept_ids import ConceptIds
from .concepts_list import ConceptsList
from .counts_by_year import CountsByYear
from .counts_by_year_inner import CountsByYearInner
from .dehydrated_author import DehydratedAuthor
from .dehydrated_concept import DehydratedConcept
from .dehydrated_funder import DehydratedFunder
from .dehydrated_institution import DehydratedInstitution
from .dehydrated_publisher import DehydratedPublisher
from .dehydrated_source import DehydratedSource
from .dehydrated_topic import DehydratedTopic
from .error_response import ErrorResponse
from .funder import Funder
from .funder_ids import FunderIds
from .funders_list import FundersList
from .geo import Geo
from .grant import Grant
from .group_by_result import GroupByResult
from .group_by_result_inner import GroupByResultInner
from .institution import Institution
from .institution_ids import InstitutionIds
from .institutions_list import InstitutionsList
from .international_names import InternationalNames
from .keyword import Keyword
from .keyword_tag import KeywordTag
from .keywords_list import KeywordsList
from .location import Location
from .mesh_tag import MeshTag
from .meta import Meta
from .open_access import OpenAccess
from .publisher import Publisher
from .publisher_ids import PublisherIds
from .publishers_list import PublishersList
from .repository import Repository
from .role import Role
from .root_response import RootResponse
from .source import Source
from .source_apc_prices import SourceApcPrices
from .source_ids import SourceIds
from .source_societies import SourceSocieties
from .sources_list import SourcesList
from .summary_stats import SummaryStats
from .sustainable_development_goal import SustainableDevelopmentGoal
from .text_body import TextBody
from .text_concepts_results import TextConceptsResults
from .text_concepts_results_meta import TextConceptsResultsMeta
from .text_keyword import TextKeyword
from .text_keywords_results import TextKeywordsResults
from .text_keywords_results_meta import TextKeywordsResultsMeta
from .text_meta import TextMeta
from .text_results import TextResults
from .text_topics_results import TextTopicsResults
from .text_topics_results_meta import TextTopicsResultsMeta
from .topic import Topic
from .topic_ids import TopicIds
from .topic_level import TopicLevel
from .topics_list import TopicsList
from .work import Work
from .work_citation_normalized_percentile import WorkCitationNormalizedPercentile
from .work_ids import WorkIds
from .works_list import WorksList

__all__ = [
    "APC",
    "AllOfTextConceptsResultsConceptsItems",
    "AllOfTextResultsConceptsItems",
    "AllOfTextResultsTopicsItems",
    "AllOfTextTopicsResultsTopicsItems",
    "AssociatedInstitution",
    "Author",
    "AuthorAffiliations",
    "AuthorIds",
    "AuthorsList",
    "Authorship",
    "AuthorshipAffiliations",
    "AutocompleteResult",
    "AutocompleteResults",
    "Biblio",
    "Concept",
    "ConceptIds",
    "ConceptsList",
    "CountsByYear",
    "CountsByYearInner",
    "DehydratedAuthor",
    "DehydratedConcept",
    "DehydratedFunder",
    "DehydratedInstitution",
    "DehydratedPublisher",
    "DehydratedSource",
    "DehydratedTopic",
    "ErrorResponse",
    "Funder",
    "FunderIds",
    "FundersList",
    "Geo",
    "Grant",
    "GroupByResult",
    "GroupByResultInner",
    "Institution",
    "InstitutionIds",
    "InstitutionsList",
    "InternationalNames",
    "Keyword",
    "KeywordTag",
    "KeywordsList",
    "Location",
    "MeshTag",
    "Meta",
    "OpenAccess",
    "Publisher",
    "PublisherIds",
    "PublishersList",
    "Repository",
    "Role",
    "RootResponse",
    "Source",
    "SourceApcPrices",
    "SourceIds",
    "SourceSocieties",
    "SourcesList",
    "SummaryStats",
    "SustainableDevelopmentGoal",
    "TextBody",
    "TextConceptsResults",
    "TextConceptsResultsMeta",
    "TextKeyword",
    "TextKeywordsResults",
    "TextKeywordsResultsMeta",
    "TextMeta",
    "TextResults",
    "TextTopicsResults",
    "TextTopicsResultsMeta",
    "Topic",
    "TopicIds",
    "TopicLevel",
    "TopicsList",
    "Work",
    "WorkCitationNormalizedPercentile",
    "WorkIds",
    "WorksList",
]
