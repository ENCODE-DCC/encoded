from snosearch.interfaces import CART_KEY
from snosearch.queries import BasicSearchQueryFactory
from snosearch.queries import BasicSearchQueryFactoryWithFacets
from snosearch.queries import BasicMatrixQueryFactoryWithFacets
from snosearch.queries import BasicReportQueryFactoryWithFacets


class CartQueryMixin:

    def _get_post_filters_with_carts(self):
        return (
            super()._get_post_filters()
            + self.params_parser.get_cart()
        )
    
    def _get_post_filters(self):
        return (
            super()._get_post_filters()
            + self.kwargs.get(CART_KEY).as_params()
        )


class CartSearchQueryFactory(CartQueryMixin, BasicSearchQueryFactory):
    '''
    Like BasicSearchQueryFactory but expands cart params to @ids and
    adds to post_filters.
    '''
    pass


class CartSearchQueryFactoryWithFacets(CartQueryMixin, BasicSearchQueryFactoryWithFacets):
    '''
    Like BasicSearchQueryFactoryWithFacets but expands cart params to @ids and
    adds to post_filters.
    '''
    pass


class CartMatrixQueryFactoryWithFacets(CartQueryMixin, BasicMatrixQueryFactoryWithFacets):
    '''
    Like BasicMatrixQueryFactoryWithFacets but expands cart params to @ids and
    adds to post_filters.
    '''
    pass


class CartReportQueryFactoryWithFacets(CartQueryMixin, BasicReportQueryFactoryWithFacets):
    '''
    Like BasicReportQueryFactoryWithFacets but expands cart params to @ids and
    adds to post_filters.
    '''
    pass
