from pyramid.view import view_config
from collections import OrderedDict


def includeme(config):
    # config.scan()
    # config.add_route('carts', '/carts{slash:/?}')
    config.add_route('cart-view', '/cart-view{slash:/?}')
    config.scan(__name__)


@view_config(route_name='cart-view', request_method='GET', permission='search')
def cart_view(context, request):
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
