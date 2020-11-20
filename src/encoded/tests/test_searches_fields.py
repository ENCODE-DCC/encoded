import pytest


@pytest.fixture()
def dummy_parent(dummy_request):
    from pyramid.testing import DummyResource
    from pyramid.security import Allow
    from snovault.elasticsearch.searches.parsers import ParamsParser
    from snovault.elasticsearch.searches.queries import AbstractQueryFactory
    from snovault.elasticsearch.interfaces import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch()
    dummy_request.context = DummyResource()
    dummy_request.context.__acl__ = lambda: [(Allow, 'group.submitter', 'search_audit')]
    class DummyParent():
        def __init__(self):
            self._meta = {}
            self.response = {}
    dp = DummyParent()
    pp = ParamsParser(dummy_request)
    dp._meta = {
        'params_parser': pp,
        'query_builder': AbstractQueryFactory(pp)
    }
    return dp


def test_searches_fields_clear_filter_response_field_with_carts_get_search_term_or_types_from_query_string(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from encoded.searches.fields import ClearFiltersResponseFieldWithCarts
    cfr = ClearFiltersResponseFieldWithCarts()
    cfr.parent = dummy_parent
    search_term_or_types = cfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('searchTerm', 'ctcf')]
    cfr.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*'
    )
    search_term_or_types = cfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('type', 'Experiment')]
    cfr.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&cart=/carts/1234abc/&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*'
    )
    search_term_or_types = cfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [
        ('type', 'Experiment'),
        ('cart', '/carts/1234abc/')
    ]


def test_searches_fields_type_only_clear_filter_response_field_with_carts_get_search_term_or_types_from_query_string(dummy_parent):
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    from encoded.searches.fields import TypeOnlyClearFiltersResponseFieldWithCarts
    tcfr = TypeOnlyClearFiltersResponseFieldWithCarts()
    tcfr.parent = dummy_parent
    search_term_or_types = tcfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('type', 'Experiment')]
    tcfr.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*'
    )
    search_term_or_types = tcfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [('type', 'Experiment')]
    tcfr.parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&cart=abc&cart=/carts/1234/'
    )
    search_term_or_types = tcfr._get_search_term_or_types_from_query_string()
    assert search_term_or_types == [
        ('type', 'Experiment'),
        ('cart', 'abc'),
        ('cart', '/carts/1234/')
    ]
