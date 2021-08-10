from encoded.searches.responses import CartQueryResponseWithFacets
from encoded.searches.responses import CartMatrixResponseWithFacets
from encoded.searches.queries import CartSearchQueryFactory
from encoded.searches.queries import CartSearchQueryFactoryWithFacets
from encoded.searches.queries import CartMatrixQueryFactoryWithFacets
from encoded.searches.queries import CartReportQueryFactoryWithFacets
from snosearch.fields import BasicSearchResponseField
from snosearch.fields import BasicSearchWithFacetsResponseField
from snosearch.fields import BasicMatrixWithFacetsResponseField
from snosearch.fields import ClearFiltersResponseField
from snosearch.fields import TypeOnlyClearFiltersResponseField
from snosearch.fields import FiltersResponseField


class CartSearchResponseField(BasicSearchResponseField):
    '''
    Like BasicSearchResponseField but uses CartSearchQueryFactory
    as query builder and CartQueryResponseWithFacets as response.
    '''

    def _build_query(self):
        self.query_builder = CartSearchQueryFactory(
            params_parser=self.get_params_parser(),
            **self.kwargs
        )
        self.query = self.query_builder.build_query()

    def _execute_query(self):
        self.results = CartQueryResponseWithFacets(
            results=self.query.execute(),
            query_builder=self.query_builder
        )


class CartSearchWithFacetsResponseField(BasicSearchWithFacetsResponseField):
    '''
    Like BasicSearchWithFacetsResponseField but uses CartSearchQueryFactoryWithFacets
    as query builder and CartQueryResponseWithFacets as response.
    '''

    def _build_query(self):
        self.query_builder = CartSearchQueryFactoryWithFacets(
            params_parser=self.get_params_parser(),
            **self.kwargs
        )
        self.query = self.query_builder.build_query()

    def _execute_query(self):
        self.results = CartQueryResponseWithFacets(
            results=self.query.execute(),
            query_builder=self.query_builder
        )


class CartReportWithFacetsResponseField(CartSearchWithFacetsResponseField):

    def _build_query(self):
        self.query_builder = CartReportQueryFactoryWithFacets(
            params_parser=self.get_params_parser(),
            **self.kwargs
        )
        self.query = self.query_builder.build_query()


class CartMatrixWithFacetsResponseField(BasicMatrixWithFacetsResponseField):

    def _build_query(self):
        self.query_builder = CartMatrixQueryFactoryWithFacets(
            params_parser=self.get_params_parser(),
            **self.kwargs
        )
        self.query = self.query_builder.build_query()

    def _execute_query(self):
        self.results = CartMatrixResponseWithFacets(
            results=self.query.execute(),
            query_builder=self.query_builder
        )


class CartFiltersResponseField(FiltersResponseField):
    '''
    Like FiltersResponseField but includes cart params as filters.
    '''

    def _get_filters_and_search_terms_from_query_string(self):
        return (
            self.get_query_builder()._get_post_filters_with_carts()
            + self.get_params_parser().get_search_term_filters()
            + self.get_params_parser().get_advanced_query_filters()
        )


class ClearFiltersResponseFieldWithCarts(ClearFiltersResponseField):
    '''
    Like ClearFiltersResponseField but keeps cart params.
    '''

    def _get_search_term_or_types_from_query_string(self):
        return (
            super()._get_search_term_or_types_from_query_string()
            + self.get_params_parser().get_cart()
        )


class TypeOnlyClearFiltersResponseFieldWithCarts(TypeOnlyClearFiltersResponseField):

    def _get_search_term_or_types_from_query_string(self):
        return (
            super()._get_search_term_or_types_from_query_string()
            + self.get_params_parser().get_cart()
        )
