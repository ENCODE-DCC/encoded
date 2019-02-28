from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

from collections import OrderedDict

from snovault import COLLECTIONS


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
        if v.properties['submitted_by'] == userid
    ]


def filter_carts_to_visible(request, carts):
    '''Filter cart list to those visible to current user'''
    if 'group.admin' in request.effective_principals:
        return carts
    return [cart for cart in carts if cart['status'] != 'deleted']


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
    user_carts = get_cart_objects_by_user(request, userid)
    visible_user_carts = filter_carts_to_visible(request, user_carts)
    # Calculate the element count in each cart, but remove the elements
    # themselves as this list can be huge.
    for c in visible_user_carts:
        c['element_count'] = len(c['elements'])
        del c['elements']
    result = {
        '@id': '/cart-manager/',
        '@type': ['cart-manager'],
        'title': 'Cart',
        'facets': [],
        '@graph': visible_user_carts,
        'columns': OrderedDict(),
        'notification': '',
        'filters': [],
        'cart_user_max': CART_USER_MAX
    }
    return result
