from snovault.elasticsearch.searches.mixins import AggsToFacetsMixin


class CartAggsToFacetsMixin(AggsToFacetsMixin):
    '''
    Like AggsToFacetsMixin but builds (fake) facets from cart params instead
    of expanded @ids used by query.
    '''

    def _get_post_filters(self):
        return self.query_builder._get_post_filters_with_carts()
