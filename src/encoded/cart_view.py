from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from urllib.parse import (
    parse_qs,
    urlencode,
)

from collections import OrderedDict

from snovault import COLLECTIONS
from snovault.elasticsearch.searches.decorators import assert_something_returned
from snovault.elasticsearch.searches.parsers import QueryString


CART_USER_MAX = 30  # Maximum number of non-deleted carts allowed per non-admin user
CART_ADMIN_MAX = 200  # Maximum per admin user
MAX_CART_ELEMENTS = 8000 # Max total elements from multiple carts


def includeme(config):
    # config.scan()
    config.add_route('cart-view', '/cart-view{slash:/?}')
    config.add_route('cart-manager', '/cart-manager{slash:/?}')
    config.add_route('search_elements', '/search_elements/{search_params}')
    config.scan(__name__)


def get_userid(request):
    userid = [
        p.replace('userid.', '')
        for p in request.effective_principals
        if p.startswith('userid.')
    ]
    if not userid:
        raise HTTPBadRequest()
    return userid[0]


def get_cart_objects_by_user(request, userid, blocked_statuses=[]):
    request.datastore = 'database'
    return [
        dict(v.properties, **{'@id': request.resource_path(v)})
        for k, v in request.registry[COLLECTIONS]['cart'].items()
        if v.properties['submitted_by'] == userid and v.properties['status'] not in blocked_statuses
    ]


@view_config(route_name='cart-view', request_method='GET', permission='search')
def cart_view(context, request):
    # 400 error if not logged in.
    get_userid(request)
    result = {
        '@id': '/cart-view/',
        '@type': ['cart-view'],
        'title': 'Cart',
        'facets': [],
        '@graph': [],
        'columns': OrderedDict(),
        'notification': '',
        'filters': []
    }
    return result


@view_config(route_name='cart-manager', request_method='GET', permission='search')
def cart_manager(context, request):
    '''Cart manager page context object generation'''
    userid = get_userid(request)
    is_admin = 'group.admin' in request.effective_principals
    blocked_statuses = ['deleted'] if not is_admin else []
    user_carts = get_cart_objects_by_user(request, userid, blocked_statuses)
    # Calculate the element count in each cart, but remove the elements
    # themselves as this list can be huge.
    for c in user_carts:
        c['element_count'] = len(c['elements'])
        del c['elements']
    result = {
        '@id': '/cart-manager/',
        '@type': ['cart-manager'],
        'title': 'Cart',
        'facets': [],
        '@graph': user_carts,
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'cart_user_max': CART_ADMIN_MAX if is_admin else CART_USER_MAX
    }
    return result


@view_config(route_name='search_elements', request_method='POST')
def search_elements(context, request):
    '''Same as search but takes JSON payload of search filters'''
    param_list = parse_qs(request.matchdict['search_params'])
    param_list.update(request.json_body)
    path = '/search/?%s' % urlencode(param_list, True)
    results = request.embed(path, as_user=True)
    return results


class Cart:
    '''
    Pass either a request with a query string with `?cart=foo&cart=bar` params
    or a list of uuids (@ids also work):
    * `cart = Cart(request)` or `cart = Cart(request, uuids=['xyz'])`
    * `cart.elements` return all elements in the cart(s)
    * `cart.as_params()` return [('@id', '/elements/xyz')] tuples for use in filters
    Can use max_cart_elements to limit total number of elements allowed in carts.
    Default is no limit.
    '''

    def __init__(self, request, uuids=None, max_cart_elements=None):
        self.request = request
        self.query_string = QueryString(request)
        self.uuids = uuids or []
        self.max_cart_elements = max_cart_elements
        self._elements = []

    def _get_carts_from_params(self):
        return self.query_string.param_values_to_list(
            params=self.query_string.get_cart()
        )

    def _get_cart_object_or_error(self, uuid):
        return self.request.embed(uuid, '@@object')

    def _try_to_get_cart_object(self, uuid):
        try:
            cart = self._get_cart_object_or_error(uuid)
        except KeyError:
            cart = {}
        return cart

    def _try_to_get_elements_from_cart(self, uuid):
        cart = self._try_to_get_cart_object(uuid)
        return cart.get('elements', [])

    def _get_elements_from_carts(self):
        carts = self.uuids or self._get_carts_from_params()
        for cart in carts:
            yield from self._try_to_get_elements_from_cart(cart)

    def _validate_cart_size(self):
        if self.max_cart_elements is not None and len(self._elements) > self.max_cart_elements:
            raise HTTPBadRequest(
                explanation=(
                    f'Too many elements in cart '
                    f'(total {len(self._elements)} > max {self.max_cart_elements})'
                )
            )

    @property
    def elements(self):
        if not self._elements:
            self._elements = sorted(set(self._get_elements_from_carts()))
        self._validate_cart_size()
        yield from self._elements

    def as_params(self):
        return [
            ('@id', at_id)
            for at_id in self.elements
        ]


class CartWithElements(Cart):
    '''
    Like Cart but raises error if empty or doesn't exist.
    cart elements to prevent triggering of max ES clauses.
    We set default MAX_CART_ELEMENTS to avoid exceeding
    `indices.query.bool.max_clause_count`.
    '''

    def __init__(self, *args, max_cart_elements=MAX_CART_ELEMENTS, **kwargs):
        super().__init__(*args, **kwargs, max_cart_elements=max_cart_elements)

    def _try_to_get_cart_object(self, uuid):
        try:
            return self._get_cart_object_or_error(uuid)
        except KeyError:
            raise HTTPBadRequest(explanation=f'Specified cart {uuid} not found')

    @assert_something_returned('Empty cart')
    def _try_to_get_elements_from_cart(self, uuid):
        return super()._try_to_get_elements_from_cart(uuid)
