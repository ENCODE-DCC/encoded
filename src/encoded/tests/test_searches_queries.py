import pytest


@pytest.fixture
def params_parser(dummy_request):
    from snovault.elasticsearch.searches.parsers import ParamsParser
    from snovault.elasticsearch import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&assay_title=Histone+ChIP-seq&award.project=Roadmap'
        '&assembly=GRCh38&biosample_ontology.classification=primary+cell'
        '&target.label=H3K27me3&biosample_ontology.classification%21=cell+line'
        '&biosample_ontology.term_name%21=naive+thymus-derived+CD4-positive%2C+alpha-beta+T+cell'
        '&limit=10&status=released&searchTerm=chip-seq&sort=date_created&sort=-files.file_size'
        '&field=@id&field=accession&cart=abc123'
    )
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch()
    return ParamsParser(dummy_request)


def test_searches_queries_cart_search_query_factory_with_init(params_parser):
    from encoded.cart_view import CartWithElements
    from encoded.searches.queries import CartQueryMixin
    from encoded.searches.queries import CartSearchQueryFactory
    csqf = CartSearchQueryFactory(
        params_parser,
        cart=CartWithElements(params_parser._request)
    )
    assert isinstance(csqf, CartSearchQueryFactory)
    assert isinstance(csqf, CartQueryMixin)
    assert csqf.params_parser == params_parser
    assert hasattr(csqf, '_get_post_filters_with_carts')


def test_searches_queries_cart_search_query_factory_with_facets_init(params_parser):
    from encoded.cart_view import CartWithElements
    from encoded.searches.queries import CartQueryMixin
    from encoded.searches.queries import CartSearchQueryFactoryWithFacets
    csqf = CartSearchQueryFactoryWithFacets(
        params_parser,
        cart=CartWithElements(params_parser._request)
    )
    assert isinstance(csqf, CartSearchQueryFactoryWithFacets)
    assert isinstance(csqf, CartQueryMixin)
    assert csqf.params_parser == params_parser
    assert hasattr(csqf, '_get_post_filters_with_carts')


def test_searches_queries_cart_matrix_query_factory_with_facets_init(params_parser):
    from encoded.cart_view import CartWithElements
    from encoded.searches.queries import CartQueryMixin
    from encoded.searches.queries import CartMatrixQueryFactoryWithFacets
    cmqf = CartMatrixQueryFactoryWithFacets(
        params_parser,
        cart=CartWithElements(params_parser._request)
    )
    assert isinstance(cmqf, CartMatrixQueryFactoryWithFacets)
    assert isinstance(cmqf, CartQueryMixin)
    assert cmqf.params_parser == params_parser
    assert hasattr(cmqf, '_get_post_filters_with_carts')


def test_searches_queries_cart_report_query_factory_with_facets_init(params_parser):
    from encoded.cart_view import CartWithElements
    from encoded.searches.queries import CartQueryMixin
    from encoded.searches.queries import CartReportQueryFactoryWithFacets
    crqf = CartReportQueryFactoryWithFacets(params_parser)
    assert isinstance(crqf, CartReportQueryFactoryWithFacets)
    assert crqf.params_parser == params_parser
    assert isinstance(crqf, CartReportQueryFactoryWithFacets)
    assert isinstance(crqf, CartQueryMixin)
    assert crqf.params_parser == params_parser
    assert hasattr(crqf, '_get_post_filters_with_carts')
