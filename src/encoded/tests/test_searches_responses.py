import pytest


def test_searches_responses_cart_query_response_with_facets_init():
    from encoded.searches.mixins import CartAggsToFacetsMixin
    from encoded.searches.responses import CartQueryResponseWithFacets
    cqr = CartQueryResponseWithFacets([], [])
    assert isinstance(cqr, CartQueryResponseWithFacets)
    assert isinstance(cqr, CartAggsToFacetsMixin)


def test_searches_responses_cart_matrix_response_with_facets_init():
    from encoded.searches.mixins import CartAggsToFacetsMixin
    from encoded.searches.responses import CartMatrixResponseWithFacets
    cmr = CartMatrixResponseWithFacets([], [])   
    assert isinstance(cmr, CartMatrixResponseWithFacets)
    assert isinstance(cmr, CartAggsToFacetsMixin)
