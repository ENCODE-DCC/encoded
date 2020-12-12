from snovault.elasticsearch.searches.interfaces import CART_KEY
from snovault.elasticsearch.searches.queries import BasicSearchQueryFactoryWithFacets
from snovault.elasticsearch.searches.queries import BasicMatrixQueryFactoryWithFacets
from snovault.elasticsearch.searches.queries import BasicReportQueryFactoryWithFacets


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
