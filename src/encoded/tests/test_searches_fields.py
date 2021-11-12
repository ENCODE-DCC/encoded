import pytest


@pytest.fixture()
def dummy_parent_and_dummy_request(dummy_request):
    from pyramid.testing import DummyResource
    from pyramid.security import Allow
    from snosearch.parsers import ParamsParser
    from snosearch.queries import AbstractQueryFactory
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
    return dp, dummy_request


def test_searches_fields_cart_search_response_field_init():
    from encoded.searches.fields import CartSearchResponseField
    crf = CartSearchResponseField()
    assert isinstance(crf, CartSearchResponseField)


def test_searches_fields_cart_search_response_build_query(dummy_parent_and_dummy_request):
    from encoded.cart_view import CartWithElements
    from encoded.searches.fields import CartSearchResponseField
    from elasticsearch_dsl import Search
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    crf = CartSearchResponseField(
        cart=CartWithElements(dummy_request)
    )
    crf.parent = dummy_parent
    crf._build_query()
    assert isinstance(crf.query, Search)


def test_searches_fields_cart_search_response_execute_query(dummy_parent_and_dummy_request, mocker):
    from encoded.cart_view import CartWithElements
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = []
    from encoded.searches.fields import CartSearchResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    crf = CartSearchResponseField(
        cart=CartWithElements(dummy_request)
    )
    crf.parent = dummy_parent
    crf._build_query()
    crf._execute_query()
    assert Search.execute.call_count == 1


def test_searches_fields_cart_search_with_facets_response_field_init():
    from encoded.searches.fields import CartSearchWithFacetsResponseField
    crf = CartSearchWithFacetsResponseField()
    assert isinstance(crf, CartSearchWithFacetsResponseField)


def test_searches_fields_cart_search_with_facets_response_build_query(dummy_parent_and_dummy_request):
    from encoded.cart_view import CartWithElements
    from encoded.searches.fields import CartSearchWithFacetsResponseField
    from elasticsearch_dsl import Search
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    crf = CartSearchWithFacetsResponseField(
        cart=CartWithElements(dummy_request)
    )
    crf.parent = dummy_parent
    crf._build_query()
    assert isinstance(crf.query, Search)


def test_searches_fields_cart_search_with_facets_response_execute_query(dummy_parent_and_dummy_request, mocker):
    from encoded.cart_view import CartWithElements
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    Search.execute.return_value = []
    from encoded.searches.fields import CartSearchWithFacetsResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    crf = CartSearchWithFacetsResponseField(
        cart=CartWithElements(dummy_request)
    )
    crf.parent = dummy_parent
    crf._build_query()
    crf._execute_query()
    assert Search.execute.call_count == 1


def test_searches_fields_cart_report_with_facets_response_build_query(dummy_parent_and_dummy_request):
    from encoded.cart_view import CartWithElements
    from encoded.searches.fields import CartReportWithFacetsResponseField
    from encoded.searches.queries import CartReportQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    crf = CartReportWithFacetsResponseField(
        cart=CartWithElements(dummy_request)
    )
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf'
    )
    crf.parent = dummy_parent
    crf._build_query()
    assert isinstance(crf.query, Search)
    assert isinstance(crf.query_builder, CartReportQueryFactoryWithFacets)


def test_searches_fields_cart_matrix_with_facets_response_field_build_query(dummy_parent_and_dummy_request):
    from encoded.cart_view import CartWithElements
    from encoded.searches.fields import CartMatrixWithFacetsResponseField
    from encoded.searches.queries import CartMatrixQueryFactoryWithFacets
    from elasticsearch_dsl import Search
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&status=released'
    )
    cmwf = CartMatrixWithFacetsResponseField(
        cart=CartWithElements(dummy_request)
    )
    cmwf.parent = dummy_parent
    cmwf._build_query()
    assert isinstance(cmwf.query, Search)
    assert isinstance(cmwf.query_builder, CartMatrixQueryFactoryWithFacets)


def test_searches_fields_cart_matrix_with_facets_response_field_execute_query(dummy_parent_and_dummy_request, mocker):
    from encoded.cart_view import CartWithElements
    from encoded.searches.fields import CartMatrixWithFacetsResponseField
    from elasticsearch_dsl import Search
    mocker.patch.object(Search, 'execute')
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&status=released'
    )
    cmwf = CartMatrixWithFacetsResponseField(
        cart=CartWithElements(dummy_request)
    )
    cmwf.parent = dummy_parent
    cmwf._build_query()
    cmwf._execute_query()
    assert Search.execute.call_count == 1


def test_searches_fields_cart_filters_response_field_get_filters_and_search_terms_from_query_string(dummy_parent_and_dummy_request):
    from encoded.cart_view import CartWithElements
    from encoded.searches.fields import CartFiltersResponseField
    from encoded.searches.queries import CartSearchQueryFactoryWithFacets
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&limit=all&frame=embedded&restricted!=*&searchTerm=ctcf&cart=abc123'
    )
    cfrf = CartFiltersResponseField(
        cart=CartWithElements(dummy_request)
    )
    dummy_parent._meta['query_builder'] = CartSearchQueryFactoryWithFacets(
        dummy_parent._meta['params_parser']
    )
    cfrf.parent = dummy_parent
    expected = [
        ('assay_title', 'Histone ChIP-seq'),
        ('award.project', 'Roadmap'),
        ('restricted!', '*'),
        ('type', 'Experiment'),
        ('searchTerm', 'ctcf'),
        ('cart', 'abc123'),
    ]
    actual = cfrf._get_filters_and_search_terms_from_query_string()
    assert len(actual) == len(expected)
    assert all([e in actual for e in expected])


def test_searches_fields_clear_filter_response_field_with_carts_get_search_term_or_types_from_query_string(dummy_parent_and_dummy_request):
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
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


def test_searches_fields_type_only_clear_filter_response_field_with_carts_get_search_term_or_types_from_query_string(dummy_parent_and_dummy_request):
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
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


def test_searches_fields_remote_response_field(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    rrf = RemoteResponseField(
        how='x',
        where='y',
        then='t',
    )
    assert isinstance(rrf, RemoteResponseField)
    assert rrf.how == 'x'
    assert rrf.where == 'y'
    assert rrf.then == 't'
    assert rrf.use_query_string is True
    rrf = RemoteResponseField(
        how='x',
        where='y',
        use_query_string=False,
    )
    assert isinstance(rrf, RemoteResponseField)
    assert rrf.how == 'x'
    assert rrf.where == 'y'
    assert rrf.then is None
    assert rrf.use_query_string is False


def test_searches_fields_remote_response_field_get_query_string_from_request(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=RNAExpression&assay_title=RNAseq&award.project=Roadmap'
        '&frame=embedded&restricted!=*&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {'result': '123'},
        where='https://rnaget.encodeproject.org/',
        then=lambda x: x,
    )
    rrf.parent = dummy_parent
    assert rrf._get_query_string_from_request() == (
        'type=RNAExpression&assay_title=RNAseq'
        '&award.project=Roadmap&frame=embedded'
        '&restricted%21=%2A&searchTerm=pomc'
    )


def test_searches_fields_remote_response_field_get_key_with_query_string(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=RNAExpression&assay_title=RNAseq&award.project=Roadmap'
        '&frame=embedded&restricted!=*&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': '123',
            'input': x,
        },
        where='https://rnaget.encodeproject.org/',
        then=lambda x: x,
    )
    rrf.parent = dummy_parent
    assert rrf._get_key_with_query_string() == (
        'https://rnaget.encodeproject.org/'
        '?type=RNAExpression&assay_title=RNAseq'
        '&award.project=Roadmap&frame=embedded'
        '&restricted%21=%2A&searchTerm=pomc'
    )


def test_searches_fields_remote_response_field_make_key(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=RNAExpression&assay_title=RNAseq&award.project=Roadmap'
        '&frame=embedded&restricted!=*&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': '123',
            'input': x,
        },
        where='https://rnaget.encodeproject.org/',
        then=lambda x: x,
    )
    rrf.parent = dummy_parent
    assert rrf._make_key() == (
        'https://rnaget.encodeproject.org/'
        '?type=RNAExpression&assay_title=RNAseq'
        '&award.project=Roadmap&frame=embedded'
        '&restricted%21=%2A&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': '123',
            'input': x,
        },
        where='https://rnaget.encodeproject.org/',
        then=lambda x: x,
        use_query_string=False,
    )
    rrf.parent = dummy_parent
    assert rrf._make_key() == (
        'https://rnaget.encodeproject.org/'
    )


def test_searches_fields_remote_response_field_make_remote_calls(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=RNAExpression&assay_title=RNAseq&award.project=Roadmap'
        '&frame=embedded&restricted!=*&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': '123',
            'input': x,
        },
        where='https://rnaget.encodeproject.org/',
        then=lambda x: x,
    )
    rrf.parent = dummy_parent
    assert rrf._make_remote_call() == {
        'result': '123',
        'input': (
            'https://rnaget.encodeproject.org/'
            '?type=RNAExpression&assay_title=RNAseq'
            '&award.project=Roadmap&frame=embedded'
            '&restricted%21=%2A&searchTerm=pomc'
        )
    }
    def remote_call(where, **kwargs):
        return {
            'where': where,
            'kwargs': kwargs
        }
    rrf = RemoteResponseField(
        how=remote_call,
        where='https://rnaget.encodeproject.org/',
        then=lambda x: x,
        use_query_string=False,
        stream=True,
        some_other_thing='abc',
    )
    rrf.parent = dummy_parent
    assert rrf._make_remote_call() == {
        'where': 'https://rnaget.encodeproject.org/',
        'kwargs': {
            'stream': True,
            'some_other_thing': 'abc'
        }
    }


def test_searches_fields_remote_response_field_get_results(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=RNAExpression&assay_title=RNAseq&award.project=Roadmap'
        '&frame=embedded&restricted!=*&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': '123',
            'input': x,
        },
        where='https://rnaget.encodeproject.org/',
    )
    rrf.parent = dummy_parent
    assert rrf._get_results() == {
        'result': '123',
        'input': (
            'https://rnaget.encodeproject.org/'
            '?type=RNAExpression&assay_title=RNAseq'
            '&award.project=Roadmap&frame=embedded'
            '&restricted%21=%2A&searchTerm=pomc'
        )
    }
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': '123',
            'input': x,
        },
        where='https://rnaget.encodeproject.org/',
        then=lambda r, x: x['result']
    )
    rrf.parent = dummy_parent
    assert rrf._get_results() == '123'


def test_searches_fields_remote_response_field_render(dummy_parent_and_dummy_request):
    from encoded.searches.fields import RemoteResponseField
    dummy_parent, dummy_request = dummy_parent_and_dummy_request
    dummy_parent._meta['params_parser']._request.environ['QUERY_STRING'] = (
        'type=RNAExpression&assay_title=RNAseq&award.project=Roadmap'
        '&frame=embedded&restricted!=*&searchTerm=pomc'
    )
    rrf = RemoteResponseField(
        how=lambda x: {
            'result': {'x': 'y'},
        },
        where='https://rnaget.encodeproject.org/',
    )
    assert rrf.render(
        parent=dummy_parent
    ) == {
        'result': {
            'x': 'y'
        }
    }
