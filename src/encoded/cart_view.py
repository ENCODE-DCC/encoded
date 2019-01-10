from pyramid.view import view_config
from collections import OrderedDict
from snovault import COLLECTIONS
from pyramid.httpexceptions import HTTPBadRequest

CART_USER_MAX = 30  # Maximum number of non-deleted carts allowed per user

def includeme(config):
    # config.scan()
    config.add_route('cart-view', '/cart-view{slash:/?}')
    config.add_route('cart-manager', '/cart-manager{slash:/?}')
    config.scan(__name__)


def get_cart_objects_by_user(request, userid):
    request.datastore = 'database'
    return [
        request.embed(request.resource_path(v), '@@object')
        for k, v in request.registry[COLLECTIONS]['cart'].items()
        if v.properties['submitted_by'] == userid and (v.properties['status'] != 'deleted' or 'group.admin' in request.effective_principals)
    ]


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


@view_config(route_name='cart-manager', request_method='GET', permission='search')
def cart_manager(context, request):
    '''Cart manager page context object generation'''
    userid = [
        p.replace('userid.', '')
        for p in request.effective_principals
        if p.startswith('userid.')
    ]
    if not userid:
        raise HTTPBadRequest()
    else:
        userid = userid[0]
    carts = get_cart_objects_by_user(request, userid)
    # Calculate the element count in each cart, but remove the elements
    # themselves as this list can be huge.
    for c in carts:
        c['element_count'] = len(c['elements'])
        del c['elements']
    result = {
        '@id': '/cart-manager/',
        '@type': ['cart-manager'],
        'title': 'Cart',
        'facets': [],
        '@graph': carts,
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'cart_user_max': CART_USER_MAX
    }
    return result
