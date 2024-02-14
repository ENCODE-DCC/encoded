from encoded.searches.mixins import CartAggsToFacetsMixin
from snosearch.responses import BasicQueryResponseWithFacets
from snosearch.responses import BasicMatrixResponseWithFacets


class CartQueryResponseWithFacets(CartAggsToFacetsMixin, BasicQueryResponseWithFacets):
    '''
    Like BasicQueryResponseWithFacets but uses CartAggsToFacetsMixin instead of AggsToFacetsMixin.
    '''

    def __init__(self, results, query_builder, *args, **kwargs):
        super().__init__(results, query_builder, *args, **kwargs)


class CartMatrixResponseWithFacets(CartAggsToFacetsMixin, BasicMatrixResponseWithFacets):
    '''
    Like BasicMatrixResponseWithFacets but uses CartAggsToFacetsMixin instead of AggsToFacetsMixin.
    '''

    def __init__(self, results, query_builder, *args, **kwargs):
        super().__init__(results, query_builder, *args, **kwargs)
